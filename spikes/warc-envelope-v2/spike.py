"""Isolated WARC envelope spike; deliberately not imported by Timonelo."""

from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import re
import tempfile
import tracemalloc
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import BinaryIO, Iterable, Optional
from urllib.parse import urljoin, urlparse

import brotli
import zstandard
from warcio.archiveiterator import ArchiveIterator
from warcio.warcwriter import WARCWriter


CRLF = b"\r\n"
HEADER_END = b"\r\n\r\n"
SECRET_HEADERS = {b"authorization", b"cookie", b"x-api-key"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class RawHeader:
    index: int
    name_bytes: bytes
    value_bytes: bytes


@dataclass(frozen=True)
class ByteStates:
    s1: bytes
    s2: bytes
    s3: bytes
    s4: bytes
    headers: tuple[RawHeader, ...]


@dataclass(frozen=True)
class HashNamespace:
    content_sha256: str
    wire_head_sha256: str
    wire_body_sha256: str
    payload_sha256: str
    warc_record_sha256: Optional[str] = None
    container_seal_sha256: Optional[str] = None


@dataclass(frozen=True)
class Artifact:
    content_sha256: str


@dataclass(frozen=True)
class Observation:
    observation_id: str
    requested_uri: str
    capture_fidelity: str
    artifact_content_sha256: str


@dataclass(frozen=True)
class Envelope:
    envelope_id: str
    observation_id: str
    warc_record_sha256: str
    container_seal_sha256: str


@dataclass(frozen=True)
class RedirectHop:
    hop_index: int
    request_record_id: str
    response_record_id: str
    status_code: int
    location_header_raw: str
    location_resolved: str
    method_before: str
    method_after: str
    scheme_change: bool
    host_change: bool


@dataclass(frozen=True)
class RedirectChain:
    requested_uri: str
    final_uri: str
    hop_count: int
    loop_detected: bool
    hops: tuple[RedirectHop, ...]


@dataclass(frozen=True)
class IntegrityFinding:
    code: str
    detected_by_warcio: bool
    must_be_detected_by_timonelo: bool
    detail: str


def parse_headers(s1: bytes) -> tuple[bytes, tuple[RawHeader, ...]]:
    if not s1.endswith(HEADER_END):
        raise ValueError("HTTP_HEADER_TERMINATOR_INVALID")
    lines = s1[:-4].split(CRLF)
    if not re.match(br"^HTTP/\d(?:\.\d)? \d{3}(?: |$)", lines[0]):
        raise ValueError("HTTP_STATUS_LINE_INVALID")
    headers = []
    for index, line in enumerate(lines[1:]):
        if b":" not in line:
            raise ValueError("HTTP_HEADER_INVALID")
        name, value = line.split(b":", 1)
        headers.append(RawHeader(index, name, value))
    return lines[0], tuple(headers)


def header_values(headers: Iterable[RawHeader], name: bytes) -> list[bytes]:
    target = name.lower()
    return [h.value_bytes.strip() for h in headers if h.name_bytes.lower() == target]


def dechunk(body: bytes) -> tuple[bytes, bytes]:
    output = bytearray()
    cursor = 0
    trailers = b""
    while True:
        line_end = body.find(CRLF, cursor)
        if line_end < 0:
            raise ValueError("CHUNK_SIZE_TERMINATOR_MISSING")
        token = body[cursor:line_end].split(b";", 1)[0]
        try:
            size = int(token, 16)
        except ValueError as exc:
            raise ValueError("CHUNK_SIZE_INVALID") from exc
        cursor = line_end + 2
        if size == 0:
            terminal = body.find(HEADER_END, cursor)
            if terminal >= 0:
                trailers = body[cursor:terminal]
                cursor = terminal + 4
            elif body[cursor:cursor + 2] == CRLF:
                cursor += 2
            else:
                raise ValueError("CHUNK_TERMINATOR_INVALID")
            if cursor != len(body):
                raise ValueError("CHUNK_TRAILING_BYTES")
            return bytes(output), trailers
        end = cursor + size
        if body[end:end + 2] != CRLF:
            raise ValueError("CHUNK_DATA_TERMINATOR_INVALID")
        output.extend(body[cursor:end])
        cursor = end + 2


def content_decode(payload: bytes, encodings: Iterable[bytes]) -> bytes:
    result = payload
    for raw_encoding in reversed(list(encodings)):
        encoding = raw_encoding.strip().lower()
        if encoding in (b"", b"identity"):
            continue
        if encoding == b"gzip":
            result = gzip.decompress(result)
        elif encoding == b"br":
            result = brotli.decompress(result)
        elif encoding in (b"zstd", b"zstandard"):
            result = zstandard.ZstdDecompressor().decompress(result)
        else:
            raise ValueError(f"CONTENT_ENCODING_UNSUPPORTED:{encoding.decode('ascii', 'replace')}")
    return result


def derive_states(raw_http_response: bytes) -> ByteStates:
    split = raw_http_response.find(HEADER_END)
    if split < 0:
        raise ValueError("HTTP_HEADER_TERMINATOR_INVALID")
    s1 = raw_http_response[:split + 4]
    s2 = raw_http_response[split + 4:]
    _, headers = parse_headers(s1)
    transfer = b",".join(header_values(headers, b"transfer-encoding")).lower()
    s3 = dechunk(s2)[0] if b"chunked" in transfer else s2
    encodings = []
    for value in header_values(headers, b"content-encoding"):
        encodings.extend(part.strip() for part in value.split(b","))
    s4 = content_decode(s3, encodings)
    return ByteStates(s1, s2, s3, s4, headers)


def hashes_for(states: ByteStates, record: bytes | None = None,
               container: bytes | None = None) -> HashNamespace:
    return HashNamespace(
        content_sha256=sha256(states.s4),
        wire_head_sha256=sha256(states.s1),
        wire_body_sha256=sha256(states.s2),
        payload_sha256=sha256(states.s3),
        warc_record_sha256=sha256(record) if record is not None else None,
        container_seal_sha256=sha256(container) if container is not None else None,
    )


def chunk(payload: bytes, sizes: tuple[int, ...] = (5, 7, 11),
          trailers: bytes = b"") -> bytes:
    chunks = []
    cursor = 0
    i = 0
    while cursor < len(payload):
        size = min(sizes[i % len(sizes)], len(payload) - cursor)
        part = payload[cursor:cursor + size]
        chunks.append(f"{size:x}".encode() + CRLF + part + CRLF)
        cursor += size
        i += 1
    chunks.append(b"0\r\n" + trailers + CRLF)
    return b"".join(chunks)


def response(status: bytes, headers: list[tuple[bytes, bytes]], body: bytes) -> bytes:
    head = b"HTTP/1.1 " + status + CRLF
    head += b"".join(name + b":" + value + CRLF for name, value in headers)
    return head + CRLF + body


def request(method: bytes, target: bytes, headers: list[tuple[bytes, bytes]],
            body: bytes = b"") -> bytes:
    head = method + b" " + target + b" HTTP/1.1\r\n"
    head += b"".join(name + b":" + value + CRLF for name, value in headers)
    return head + CRLF + body


def warc_date() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def write_warc(records: list[tuple[str, str, bytes, dict[str, str]]],
               gzip_records: bool = False) -> bytes:
    output = io.BytesIO()
    writer = WARCWriter(output, gzip=gzip_records, warc_version="WARC/1.1")
    for uri, record_type, raw_http, extra in records:
        headers = {
            "WARC-Date": extra.get("WARC-Date", warc_date()),
            "WARC-Record-ID": extra.get("WARC-Record-ID", f"<urn:uuid:{uuid.uuid4()}>")
        }
        headers.update({k: v for k, v in extra.items() if k not in headers})
        record = writer.create_warc_record(
            uri,
            record_type,
            payload=io.BytesIO(raw_http),
            warc_content_type=(
                f"application/http; msgtype={record_type}"
                if record_type in ("request", "response")
                else "application/octet-stream"
            ),
            warc_headers_dict=headers,
        )
        writer.write_record(record)
    return output.getvalue()


def read_warc(container: bytes) -> list[dict[str, object]]:
    result = []
    for record in ArchiveIterator(io.BytesIO(container), check_digests=True):
        raw = record.raw_stream.read()
        http = record.http_headers.to_bytes() + raw if record.http_headers else raw
        result.append({
            "record_id": record.rec_headers.get_header("WARC-Record-ID"),
            "type": record.rec_type,
            "uri": record.rec_headers.get_header("WARC-Target-URI"),
            "version": record.rec_headers.protocol,
            "date": record.rec_headers.get_header("WARC-Date"),
            "block_digest": record.rec_headers.get_header("WARC-Block-Digest"),
            "payload_digest": record.rec_headers.get_header("WARC-Payload-Digest"),
            "digest_ok": record.rec_headers.get_header("WARC-Block-Digest") is not None,
            "raw_http": http,
        })
    return result


def content_stream_bytes(container: bytes) -> bytes:
    record = next(ArchiveIterator(io.BytesIO(container)))
    return record.content_stream().read()


def build_redirect_chain(requested_uri: str, transitions: list[tuple[int, str]],
                         initial_method: str = "POST") -> RedirectChain:
    current = requested_uri
    method = initial_method
    seen = {current}
    hops = []
    loop = False
    for index, (status, location) in enumerate(transitions):
        resolved = urljoin(current, location)
        new_method = "GET" if status in (301, 302, 303) and method != "HEAD" else method
        before_parts, after_parts = urlparse(current), urlparse(resolved)
        hops.append(RedirectHop(
            index,
            f"<urn:uuid:req-{index}>",
            f"<urn:uuid:res-{index}>",
            status,
            location,
            resolved,
            method,
            new_method,
            before_parts.scheme != after_parts.scheme,
            before_parts.netloc != after_parts.netloc,
        ))
        current, method = resolved, new_method
        if current in seen:
            loop = True
            break
        seen.add(current)
    return RedirectChain(requested_uri, current, len(hops), loop, tuple(hops))


def sanitize_request(raw_request: bytes) -> tuple[bytes, list[str]]:
    split = raw_request.find(HEADER_END)
    if split < 0:
        raise ValueError("HTTP_HEADER_TERMINATOR_INVALID")
    lines = raw_request[:split].split(CRLF)
    redacted = [lines[0]]
    names = []
    for line in lines[1:]:
        name, value = line.split(b":", 1)
        if name.lower() in SECRET_HEADERS:
            redacted.append(name + b": [REDACTED]")
            names.append(name.decode("ascii", "replace"))
        else:
            redacted.append(line)
    return CRLF.join(redacted) + HEADER_END + raw_request[split + 4:], names


def stream_hash(stream: BinaryIO, chunk_size: int = 1024 * 1024) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    while True:
        block = stream.read(chunk_size)
        if not block:
            break
        digest.update(block)
        total += len(block)
    return digest.hexdigest(), total


def measure_streaming(payload: bytes) -> dict[str, int | str]:
    tracemalloc.start()
    digest, total = stream_hash(io.BytesIO(payload))
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"bytes": total, "peak_traced_bytes": peak, "content_sha256": digest}


def measure_warc_streaming(size: int, block: bytes = bytes(range(256)) * 4096) -> dict[str, int | str]:
    """Measure a resource-record write/replay using disk-backed streams."""
    tracemalloc.start()
    expected = hashlib.sha256()
    with tempfile.TemporaryFile() as payload, tempfile.TemporaryFile() as container:
        remaining = size
        while remaining:
            part = block[: min(len(block), remaining)]
            payload.write(part)
            expected.update(part)
            remaining -= len(part)
        payload.seek(0)
        writer = WARCWriter(container, gzip=True, warc_version="WARC/1.1")
        record = writer.create_warc_record(
            "urn:timonelo:large-fixture",
            "resource",
            payload=payload,
            length=size,
            warc_content_type="application/octet-stream",
            warc_headers_dict={"WARC-Date": warc_date()},
        )
        writer.write_record(record)
        container_size = container.tell()
        container.seek(0)
        replay = next(ArchiveIterator(container)).raw_stream
        replay_digest, replay_size = stream_hash(replay)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "bytes": size,
        "container_bytes": container_size,
        "peak_traced_bytes": peak,
        "content_sha256": expected.hexdigest(),
        "replay_sha256": replay_digest,
        "replay_bytes": replay_size,
        "temp_file_behavior": "disk-backed payload and container",
    }


def validate_container(container: bytes, expected_record_ids: Optional[set[str]] = None,
                       expected_digests: Optional[dict[str, str]] = None) -> list[IntegrityFinding]:
    findings: list[IntegrityFinding] = []
    if not container.startswith(b"\x1f\x8b"):
        cursor = 0
        while cursor < len(container):
            while container[cursor:cursor + 2] == CRLF:
                cursor += 2
            if cursor >= len(container):
                break
            header_end = container.find(HEADER_END, cursor)
            if header_end < 0:
                findings.append(IntegrityFinding(
                    "TRUNCATED_WARC_HEADER", False, True, f"offset={cursor}"
                ))
                break
            header = container[cursor:header_end]
            length_match = re.search(br"(?:^|\r\n)Content-Length: (\d+)(?:\r\n|$)", header)
            if not length_match:
                findings.append(IntegrityFinding(
                    "WARC_CONTENT_LENGTH_MISSING_OR_INVALID", False, True, f"offset={cursor}"
                ))
                break
            block_start = header_end + 4
            block_end = block_start + int(length_match.group(1))
            if block_end > len(container):
                findings.append(IntegrityFinding(
                    "TRUNCATED_WARC_RECORD_BODY", False, True,
                    f"declared_end={block_end},container_end={len(container)}",
                ))
                break
            if container[block_end:block_end + 4] != HEADER_END:
                findings.append(IntegrityFinding(
                    "WARC_RECORD_TERMINATOR_INVALID", False, True, f"offset={block_end}"
                ))
                break
            cursor = block_end + 4
    records: list[tuple[str | None, str | None]] = []
    try:
        for record in ArchiveIterator(io.BytesIO(container), check_digests=True):
            rid = record.rec_headers.get_header("WARC-Record-ID")
            linked = record.rec_headers.get_header("WARC-Concurrent-To")
            records.append((rid, linked))
            try:
                raw_body = record.raw_stream.read()
            except Exception as exc:
                findings.append(IntegrityFinding(
                    "WARC_DIGEST_VALIDATION_FAILURE", True, True,
                    (rid or "") + ":" + str(exc),
                ))
                continue
            try:
                if record.http_headers:
                    raw_http = record.http_headers.to_bytes() + raw_body
                    body = derive_states(raw_http).s4
                else:
                    body = raw_body
            except Exception as exc:
                findings.append(IntegrityFinding(
                    "PAYLOAD_DECODE_FAILURE", False, True,
                    (rid or "") + ":" + str(exc),
                ))
                continue
            if expected_digests and rid in expected_digests and sha256(body) != expected_digests[rid]:
                findings.append(IntegrityFinding(
                    "TIMONELO_CONTENT_DIGEST_MISMATCH", False, True, rid or ""
                ))
    except Exception as exc:
        findings.append(IntegrityFinding(
            "WARC_PARSE_FAILURE", True, True, type(exc).__name__ + ": " + str(exc)
        ))
    if container and not records:
        findings.append(IntegrityFinding(
            "NO_WARC_RECORDS", False, True, "non-empty container yielded zero records"
        ))
    ids = [rid for rid, _ in records]
    duplicates = sorted({rid for rid in ids if rid and ids.count(rid) > 1})
    if duplicates:
        findings.append(IntegrityFinding(
            "DUPLICATE_WARC_RECORD_ID", False, True, ",".join(duplicates)
        ))
    if expected_record_ids is not None:
        missing = sorted(expected_record_ids - set(ids))
        if missing:
            findings.append(IntegrityFinding(
                "MISSING_REQUEST_RESPONSE_PAIR", False, True, ",".join(missing)
            ))
    id_set = set(ids)
    for _, linked in records:
        if linked and linked not in id_set:
            findings.append(IntegrityFinding(
                "INVALID_LINKAGE", False, True, linked
            ))
    return findings


def encoded_json(value: object) -> object:
    if isinstance(value, bytes):
        return {"base64": base64.b64encode(value).decode("ascii")}
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    raise TypeError(type(value).__name__)


def dump_json(value: object) -> str:
    return json.dumps(value, default=encoded_json, indent=2, sort_keys=True)
