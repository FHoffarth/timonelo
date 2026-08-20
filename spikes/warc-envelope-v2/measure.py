"""Produce reproducible measurements for the WARC envelope spike."""

from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.metadata
import io
import json
import platform
import re
import socket
import socketserver
import sys
import threading
from pathlib import Path

import httpx
from warcio.archiveiterator import ArchiveIterator
from warcio.capture_http import capture_http
import requests

from spike import (
    chunk,
    content_stream_bytes,
    derive_states,
    hashes_for,
    measure_warc_streaming,
    read_warc,
    response,
    sha256,
    validate_container,
    write_warc,
)


ROOT = Path(__file__).parent


def sha1_b32(data: bytes) -> str:
    return "sha1:" + base64.b32encode(hashlib.sha1(data).digest()).decode("ascii")


class FixtureHandler(socketserver.BaseRequestHandler):
    raw_response = b""

    def handle(self) -> None:
        request_bytes = b""
        while b"\r\n\r\n" not in request_bytes:
            request_bytes += self.request.recv(65536)
        self.server.last_request = request_bytes
        self.request.sendall(self.raw_response)


class FixtureServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def capture_http_measurement(raw_response: bytes) -> dict[str, object]:
    FixtureHandler.raw_response = raw_response
    server = FixtureServer(("127.0.0.1", 0), FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_address[1]}/fixture"
    try:
        with capture_http(gzip=False, warc_version="WARC/1.1", record_ip=False) as writer:
            result = requests.get(url, timeout=5)
            result.raise_for_status()
            client_body = result.content
        container = writer.get_contents()
        records = read_warc(container)
        with capture_http(gzip=False, warc_version="WARC/1.1", record_ip=False) as httpx_writer:
            httpx_result = httpx.get(url, timeout=5)
            httpx_result.raise_for_status()
        httpx_record_count = len(read_warc(httpx_writer.get_contents()))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    response_record = next(record for record in records if record["type"] == "response")
    stored = derive_states(response_record["raw_http"])
    return {
        "records": [record["type"] for record in records],
        "client_body_sha256": sha256(client_body),
        "stored_s2_sha256": sha256(stored.s2),
        "stored_s3_sha256": sha256(stored.s3),
        "stored_s4_sha256": sha256(stored.s4),
        "stored_equals_input": response_record["raw_http"] == raw_response,
        "warc_version": response_record["version"],
        "global_http_client_monkey_patch": True,
        "requests_compatible": True,
        "httpx_intercepted": httpx_record_count > 0,
        "httpx_record_count": httpx_record_count,
        "async_safe": False,
    }


def http2_measurement() -> dict[str, object]:
    url = "https://nghttp2.org/httpbin/get"
    host = "nghttp2.org"
    result: dict[str, object] = {
        "endpoint": url,
        "capture_fidelity": "DECODED",
        "wire_http2_frames_observable": False,
        "recommendation": "ALLOW_HTTP_2_WITH_DECODED_FIDELITY",
    }
    try:
        result["dns_answers"] = sorted({
            item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        })
        with httpx.Client(http2=True, timeout=15, follow_redirects=True) as client:
            response_obj = client.get(url)
            result["status_code"] = response_obj.status_code
            result["http_version"] = response_obj.http_version
            result["final_uri"] = str(response_obj.url)
            result["header_representation"] = "decoded ordered name/value API, not HPACK/frame bytes"
            stream = response_obj.extensions.get("network_stream")
            if stream:
                ssl_object = stream.get_extra_info("ssl_object")
                if ssl_object:
                    result["tls_version"] = ssl_object.version()
                    result["cipher_suite"] = ssl_object.cipher()[0]
                    result["alpn"] = ssl_object.selected_alpn_protocol()
                sock = stream.get_extra_info("socket")
                if sock:
                    result["resolved_ip"] = sock.getpeername()[0]
        with httpx.Client(timeout=10) as client:
            egress = client.get("https://www.cloudflare.com/cdn-cgi/trace")
            trace = dict(
                line.split("=", 1) for line in egress.text.splitlines() if "=" in line
            )
            result["egress_ip"] = trace.get("ip")
            result["egress_region"] = trace.get("colo")
    except Exception as exc:
        result["error"] = type(exc).__name__ + ": " + str(exc)
        result["recommendation"] = "ALLOW_HTTP_2_WITH_DECODED_FIDELITY"
    return result


def corruption_measurement() -> dict[str, object]:
    raw = response(b"200 OK", [], b"payload")
    rid = "<urn:uuid:corruption-base>"
    base = write_warc([("http://fixture.test/corrupt", "response", raw, {
        "WARC-Record-ID": rid,
    })])
    gzip_raw = response(
        b"200 OK",
        [(b"Content-Encoding", b" gzip")],
        gzip.compress(b"gzip-body", mtime=0)[:-4],
    )
    variants = {
        "A_truncated_warc_header": base[:20],
        "B_truncated_record_body": base[:-9],
        "C_bad_warc_content_length": re.sub(
            br"Content-Length: \d+", b"Content-Length: 999999", base, count=1
        ),
        "D_malformed_http_status": base.replace(b"HTTP/1.1 200 OK", b"HTTP/1.1 BAD OK", 1),
        "E_malformed_http_header_terminator": base.replace(
            b"HTTP/1.1 200 OK\r\n\r\n", b"HTTP/1.1 200 OK\r\nX: broken\r\nX", 1
        ),
        "F_broken_warc_payload_digest": base.replace(
            b"WARC-Payload-Digest: sha1:", b"WARC-Payload-Digest: sha1:X", 1
        ),
        "G_broken_warc_block_digest": base.replace(
            b"WARC-Block-Digest: sha1:", b"WARC-Block-Digest: sha1:X", 1
        ),
        "H_duplicate_warc_record_id": base + base,
        "I_missing_request_response_pair": base,
        "J_container_truncation": base[: len(base) // 2],
        "K_truncated_gzip_member": write_warc([
            ("http://fixture.test/gzip", "response", gzip_raw, {})
        ]),
        "L_invalid_linkage": write_warc([(
            "http://fixture.test/link",
            "response",
            raw,
            {"WARC-Concurrent-To": "<urn:uuid:not-present>"},
        )]),
    }
    (ROOT / "corruption_corpus.json").write_text(
        json.dumps(
            {
                name: {
                    "base64": base64.b64encode(data).decode("ascii"),
                    "bytes": len(data),
                    "container_sha256": sha256(data),
                }
                for name, data in variants.items()
            },
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )
    result = {}
    for name, data in variants.items():
        expected_ids = {rid, "<urn:uuid:missing>"} if name.startswith("I_") else None
        findings = validate_container(data, expected_record_ids=expected_ids)
        result[name] = {
            "finding_codes": [finding.code for finding in findings],
            "warcio_detected": any(finding.detected_by_warcio for finding in findings),
            "timonelo_guard_required": any(
                finding.must_be_detected_by_timonelo for finding in findings
            ),
            "accepted_without_finding": not findings,
        }
    return result


def main() -> int:
    body = b"gzip and chunked measurement payload" * 8
    compressed = gzip.compress(body, mtime=0)
    framed = chunk(compressed)
    raw = response(
        b"200 OK",
        [(b"Transfer-Encoding", b" chunked"), (b"Content-Encoding", b" gzip")],
        framed,
    )
    states = derive_states(raw)
    container = write_warc([("http://fixture.test/combined", "response", raw, {})])
    record = read_warc(container)[0]
    digest_coverage = {
        "warc_block_digest": record["block_digest"],
        "warc_payload_digest": record["payload_digest"],
        "sha1_s1": sha1_b32(states.s1),
        "sha1_s2": sha1_b32(states.s2),
        "sha1_s3": sha1_b32(states.s3),
        "sha1_s4": sha1_b32(states.s4),
        "sha1_block_s1_plus_s2": sha1_b32(states.s1 + states.s2),
        "payload_digest_covers": "S2",
        "block_digest_covers": "S1+S2",
        "raw_stream_exposes": "S2",
        "content_stream_exposes": "S4",
    }
    uncompressed_session = write_warc([
        ("http://fixture.test/a", "response", response(b"200 OK", [], b"A" * 4096), {}),
        ("http://fixture.test/b", "response", response(b"200 OK", [], b"B" * 4096), {}),
    ])
    per_record_gzip = write_warc([
        ("http://fixture.test/a", "response", response(b"200 OK", [], b"A" * 4096), {}),
        ("http://fixture.test/b", "response", response(b"200 OK", [], b"B" * 4096), {}),
    ], gzip_records=True)
    whole_file_gzip = gzip.compress(uncompressed_session, mtime=0)
    try:
        whole_file_replay_records = len(list(ArchiveIterator(io.BytesIO(whole_file_gzip))))
        whole_file_replay_error = None
    except Exception as exc:
        whole_file_replay_records = 0
        whole_file_replay_error = type(exc).__name__ + ": " + str(exc).strip()
    results = {
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "warcio": importlib.metadata.version("warcio"),
            "requests": importlib.metadata.version("requests"),
            "urllib3": importlib.metadata.version("urllib3"),
            "httpx": importlib.metadata.version("httpx"),
            "httpcore": importlib.metadata.version("httpcore"),
            "brotli": importlib.metadata.version("brotli"),
            "zstandard": importlib.metadata.version("zstandard"),
            "warc_version": "WARC/1.1",
        },
        "combined": {
            "sizes": {"s1": len(states.s1), "s2": len(states.s2), "s3": len(states.s3), "s4": len(states.s4)},
            "hashes": hashes_for(states, container, container).__dict__,
            "round_trip_s4_equal": derive_states(record["raw_http"]).s4 == body,
            "content_stream_s4_equal": content_stream_bytes(container) == body,
            "digest_coverage": digest_coverage,
        },
        "capture_http": capture_http_measurement(raw),
        "http2": http2_measurement(),
        "corruption": corruption_measurement(),
        "large_streaming": measure_warc_streaming(32 * 1024 * 1024),
        "container": {
            "uncompressed_bytes": len(uncompressed_session),
            "per_record_gzip_bytes": len(per_record_gzip),
            "whole_file_gzip_bytes": len(whole_file_gzip),
            "per_record_members": per_record_gzip.count(b"\x1f\x8b"),
            "per_record_replay_records": len(list(ArchiveIterator(io.BytesIO(per_record_gzip)))),
            "whole_file_replay_records": whole_file_replay_records,
            "whole_file_replay_error": whole_file_replay_error,
            "uncompressed_seal_sha256": sha256(uncompressed_session),
            "per_record_gzip_seal_sha256": sha256(per_record_gzip),
            "whole_file_gzip_seal_sha256": sha256(whole_file_gzip),
        },
    }
    output = ROOT / "measurements.json"
    output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
