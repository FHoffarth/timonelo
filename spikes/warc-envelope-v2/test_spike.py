"""Executable evidence matrix for the isolated WARC envelope spike."""

from __future__ import annotations

import gzip
import io
import os

import brotli
import pytest
import zstandard

from spike import (
    Artifact,
    Envelope,
    Observation,
    build_redirect_chain,
    chunk,
    content_stream_bytes,
    derive_states,
    hashes_for,
    measure_streaming,
    measure_warc_streaming,
    read_warc,
    request,
    response,
    sanitize_request,
    sha256,
    validate_container,
    warc_date,
    write_warc,
)


URL = "http://fixture.test/resource"


def round_trip(raw: bytes, record_type: str = "response") -> tuple[bytes, dict[str, object]]:
    container = write_warc([(URL, record_type, raw, {})])
    return container, read_warc(container)[0]


def test_case_1_simple_http_200_round_trip():
    body = b"known text without charset decoding\n"
    raw_request = request(b"GET", b"/resource", [(b"Host", b" fixture.test")])
    raw_response = response(b"200 OK", [(b"X-First", b" one"), (b"X-Second", b" two")], body)
    container = write_warc([
        (URL, "request", raw_request, {}),
        (URL, "response", raw_response, {}),
    ])
    records = read_warc(container)
    assert records[0]["raw_http"] == raw_request
    assert records[1]["raw_http"] == raw_response
    assert records[1]["uri"] == URL
    assert derive_states(records[1]["raw_http"]).s4 == body
    assert hashes_for(derive_states(raw_response)).content_sha256 == hashes_for(
        derive_states(records[1]["raw_http"])
    ).content_sha256


def test_case_2_gzip_only_hashes_s3_and_s4_separately():
    body = "Grüße remain UTF-8 bytes".encode()
    compressed = gzip.compress(body, mtime=0)
    raw = response(b"200 OK", [(b"Content-Encoding", b" gzip")], compressed)
    states = derive_states(raw)
    assert states.s3 == compressed
    assert states.s4 == body
    assert sha256(states.s3) != sha256(states.s4)
    container, record = round_trip(raw)
    assert derive_states(record["raw_http"]).s4 == body
    assert content_stream_bytes(container) == body


def test_case_3_chunked_only_preserves_s2_and_dechunks_content_stream():
    body = b"Wikipedia in deterministic chunks"
    framed = chunk(body, trailers=b"X-Trailer: yes\r\n")
    raw = response(b"200 OK", [(b"Transfer-Encoding", b" chunked")], framed)
    states = derive_states(raw)
    container, record = round_trip(raw)
    recovered = derive_states(record["raw_http"])
    assert states.s2 == framed
    assert states.s3 == body == states.s4
    assert recovered.s2 == framed
    assert b"Transfer-Encoding: chunked" in record["raw_http"]
    # warcio removes chunk framing but incorrectly exposes trailers as payload.
    assert content_stream_bytes(container) == body + b"0\r\nTrailer: yes\r\n\r\n"


def test_case_4_gzip_plus_chunked_all_states_and_warcio_streams():
    body = b"highest priority combined state" * 4
    compressed = gzip.compress(body, mtime=0)
    framed = chunk(compressed)
    raw = response(
        b"200 OK",
        [(b"Transfer-Encoding", b" chunked"), (b"Content-Encoding", b" gzip")],
        framed,
    )
    states = derive_states(raw)
    container, record = round_trip(raw)
    assert states.s1.endswith(b"\r\n\r\n")
    assert states.s2 == framed
    assert states.s3 == compressed
    assert states.s4 == body
    assert derive_states(record["raw_http"]) == states
    assert content_stream_bytes(container) == body
    assert len({sha256(states.s1), sha256(states.s2), sha256(states.s3), sha256(states.s4)}) == 4


def test_case_5_redirect_chain_is_external_and_loop_aware():
    chain = build_redirect_chain(
        "http://a.test/start",
        [(302, "/middle"), (307, "http://b.test/final")],
        initial_method="POST",
    )
    assert chain.final_uri == "http://b.test/final"
    assert chain.hop_count == 2
    assert chain.hops[0].method_after == "GET"
    assert chain.hops[1].host_change
    loop = build_redirect_chain("http://a.test/a", [(302, "/b"), (302, "/a")])
    assert loop.loop_detected


def test_case_6_duplicate_and_weird_headers_are_ordered_bytes():
    headers = [
        (b"Set-Cookie", b" a=1"),
        (b"set-cookie", b" b=2"),
        (b"Content-Length", b" 3"),
        (b"Content-Length", b" 4"),
        (b"Transfer-Encoding", b" chunked"),
        (b"Content-Encoding", b" identity"),
        (b"Content-Encoding", b" identity"),
        (b"Location", b" /one"),
        (b"location", b" /two"),
        (b"Content-Type", b" text/plain ; charset=utf-8"),
        (b"CONTENT-TYPE", b" application/octet-stream"),
        (b"X-Weird", b"\t spaced \t"),
        (b"X-Obs-Text", " café".encode()),
    ]
    raw = response(b"200 OK", headers, chunk(b"abc"))
    container, record = round_trip(raw)
    # create_warc_record parses and rewrites even an application/http payload:
    # whitespace is stripped and non-ASCII header bytes are percent-encoded.
    assert raw not in container
    assert record["raw_http"] != raw
    observed = derive_states(record["raw_http"]).headers
    assert [(h.index, h.name_bytes) for h in observed] == [
        (i, name) for i, (name, _) in enumerate(headers)
    ]
    assert observed[0].value_bytes == b" a=1"
    assert observed[1].value_bytes == b" b=2"
    assert observed[11].value_bytes != headers[11][1]
    assert observed[12].value_bytes == b" caf%C3%A9"


def test_raw_wire_block_can_be_preserved_as_opaque_resource_record():
    raw = response(
        b"200 OK",
        [(b"X-Weird", b"\t exact \t"), (b"X-Obs-Text", " café".encode())],
        b"payload",
    )
    container = write_warc([(URL, "resource", raw, {})])
    record = read_warc(container)[0]
    assert record["raw_http"] == raw
    assert raw in container


def test_case_7_binary_pdf_round_trip_without_text_decode():
    pdf = b"%PDF-1.4\n1 0 obj\n<< /Length 8 >>\nstream\n\x00\xffA\x80B\nendstream\nendobj\n%%EOF\n"
    raw = response(b"200 OK", [(b"Content-Type", b" application/pdf")], pdf)
    _, record = round_trip(raw)
    assert derive_states(record["raw_http"]).s4 == pdf
    assert sha256(derive_states(record["raw_http"]).s4) == sha256(pdf)


def test_case_8_corruption_matrix_has_typed_findings():
    raw = response(b"200 OK", [], b"payload")
    container = write_warc([(URL, "response", raw, {"WARC-Record-ID": "<urn:uuid:fixed>"})])
    variants = {
        "truncated_warc_header": container[:20],
        "truncated_record_body": container[:-9],
        "bad_content_length": container.replace(b"Content-Length: ", b"Content-Length: 999", 1),
        "malformed_status": container.replace(b"HTTP/1.1 200 OK", b"NOT-HTTP STATUS!", 1),
        "malformed_terminator": container.replace(b"HTTP/1.1 200 OK\r\n\r\n", b"HTTP/1.1 200 OK\r\nX", 1),
        "broken_payload_digest": container.replace(b"WARC-Payload-Digest: sha1:", b"WARC-Payload-Digest: sha1:X", 1),
        "broken_block_digest": container.replace(b"WARC-Block-Digest: sha1:", b"WARC-Block-Digest: sha1:X", 1),
        "duplicate_record_id": container + container,
        "missing_pair": container,
        "container_truncation": container[: len(container) // 2],
        "invalid_linkage": write_warc([(
            URL,
            "response",
            raw,
            {"WARC-Concurrent-To": "<urn:uuid:not-present>"},
        )]),
    }
    results = {
        name: validate_container(
            data,
            expected_record_ids={"<urn:uuid:fixed>", "<urn:uuid:missing>"}
            if name == "missing_pair" else None,
        )
        for name, data in variants.items()
    }
    assert all(name in results for name in variants)
    assert any(f.code == "DUPLICATE_WARC_RECORD_ID" for f in results["duplicate_record_id"])
    assert any(f.code == "MISSING_REQUEST_RESPONSE_PAIR" for f in results["missing_pair"])
    assert any(f.code == "INVALID_LINKAGE" for f in results["invalid_linkage"])
    truncated_gzip = gzip.compress(b"gzip payload")[:-4]
    with pytest.raises(Exception):
        derive_states(response(b"200 OK", [(b"Content-Encoding", b" gzip")], truncated_gzip))
    with pytest.raises(ValueError):
        derive_states(response(b"200 OK", [(b"Transfer-Encoding", b" chunked")], b"Z\r\n"))


def test_case_9_same_url_can_create_two_observations_and_artifacts():
    first = b"timestamp=1&nonce=A"
    second = b"timestamp=2&nonce=B"
    artifact_a, artifact_b = Artifact(sha256(first)), Artifact(sha256(second))
    obs_a = Observation("OBS-A", URL, "WIRE", artifact_a.content_sha256)
    obs_b = Observation("OBS-B", URL, "WIRE", artifact_b.content_sha256)
    assert obs_a.requested_uri == obs_b.requested_uri
    assert obs_a.observation_id != obs_b.observation_id
    assert obs_a.artifact_content_sha256 != obs_b.artifact_content_sha256


@pytest.mark.parametrize(
    ("encoding", "encoded"),
    [
        (b"br", brotli.compress(b"brotli content")),
        (b"zstd", zstandard.ZstdCompressor().compress(b"zstd content")),
    ],
)
def test_case_11_brotli_and_zstd_decode_or_fail_explicitly(encoding, encoded):
    expected = b"brotli content" if encoding == b"br" else b"zstd content"
    raw = response(b"200 OK", [(b"Content-Encoding", b" " + encoding)], encoded)
    assert derive_states(raw).s4 == expected
    with pytest.raises(ValueError, match="CONTENT_ENCODING_UNSUPPORTED"):
        derive_states(response(b"200 OK", [(b"Content-Encoding", b" mystery")], b"x"))


def test_case_12_large_fixture_hashing_is_bounded():
    block = bytes(range(256)) * 4096
    payload = block * 32  # 32 MiB deterministic fixture
    measurement = measure_streaming(payload)
    assert measurement["bytes"] == 32 * 1024 * 1024
    assert measurement["content_sha256"] == sha256(payload)
    assert measurement["peak_traced_bytes"] < 4 * 1024 * 1024
    warc_measurement = measure_warc_streaming(32 * 1024 * 1024)
    assert warc_measurement["content_sha256"] == warc_measurement["replay_sha256"]
    assert warc_measurement["replay_bytes"] == warc_measurement["bytes"]
    assert warc_measurement["peak_traced_bytes"] < 20 * 1024 * 1024


@pytest.mark.parametrize(
    ("status", "headers", "body"),
    [
        (b"204 No Content", [], b""),
        (b"304 Not Modified", [], b""),
        (b"206 Partial Content", [(b"Content-Range", b" bytes 0-2/10")], b"abc"),
        (b"200 OK", [(b"Content-Length", b" 0")], b""),
    ],
)
def test_case_13_empty_and_partial_bodies_remain_distinct(status, headers, body):
    raw = response(status, headers, body)
    _, record = round_trip(raw)
    assert record["raw_http"] == raw


def test_secret_hygiene_is_explicit_and_dual_representation_is_possible():
    raw = request(
        b"GET",
        b"/private",
        [
            (b"Host", b" fixture.test"),
            (b"Authorization", b" Bearer SYNTHETIC"),
            (b"Cookie", b" session=SYNTHETIC"),
            (b"X-API-Key", b" SYNTHETIC"),
        ],
    )
    sanitized, redacted = sanitize_request(raw)
    assert b"SYNTHETIC" in raw
    assert b"SYNTHETIC" not in sanitized
    assert redacted == ["Authorization", "Cookie", "X-API-Key"]
    assert sanitized.count(b"[REDACTED]") == 3


def test_warc_1_1_subsecond_dates_linkage_and_unique_ids():
    req_id = "<urn:uuid:req>"
    res_id = "<urn:uuid:res>"
    date_a, date_b = warc_date(), warc_date()
    container = write_warc([
        (URL, "request", request(b"GET", b"/", []), {
            "WARC-Date": date_a, "WARC-Record-ID": req_id,
        }),
        (URL, "response", response(b"200 OK", [], b"ok"), {
            "WARC-Date": date_b, "WARC-Record-ID": res_id,
            "WARC-Concurrent-To": req_id,
        }),
    ])
    records = read_warc(container)
    assert all(r["version"] == "WARC/1.1" for r in records)
    assert all("." in r["date"] for r in records)
    assert {r["record_id"] for r in records} == {req_id, res_id}


def test_observation_metadata_can_be_copied_into_warc_without_becoming_identity():
    metadata = (
        b'{"capture_fidelity":"WIRE","egress_region":"fixture",'
        b'"observation_id":"OBS-META","resolved_ip":"127.0.0.1"}'
    )
    container = write_warc([("urn:timonelo:observation:OBS-META", "metadata", metadata, {})])
    record = read_warc(container)[0]
    assert record["type"] == "metadata"
    assert record["raw_http"] == metadata
    assert sha256(metadata) != sha256(b"artifact content")


def test_repack_changes_envelope_not_artifact_or_observation():
    raw = response(b"200 OK", [], b"stable payload")
    artifact = Artifact(sha256(derive_states(raw).s4))
    observation = Observation("OBS-STABLE", URL, "WIRE", artifact.content_sha256)
    first = write_warc([(URL, "response", raw, {"WARC-Record-ID": "<urn:uuid:first>"})])
    second = write_warc([(URL, "response", raw, {"WARC-Record-ID": "<urn:uuid:second>"})])
    env_a = Envelope("ENV-A", observation.observation_id, sha256(first), sha256(first))
    env_b = Envelope("ENV-B", observation.observation_id, sha256(second), sha256(second))
    assert derive_states(read_warc(first)[0]["raw_http"]).s4 == derive_states(
        read_warc(second)[0]["raw_http"]
    ).s4
    assert env_a.observation_id == env_b.observation_id
    assert env_a.container_seal_sha256 != env_b.container_seal_sha256


def test_forged_warc_digest_is_not_artifact_authority():
    raw = response(b"200 OK", [], b"actual content")
    container = write_warc([(URL, "response", raw, {})])
    forged = container.replace(b"WARC-Payload-Digest: sha1:", b"WARC-Payload-Digest: sha1:X", 1)
    with pytest.raises(Exception):
        list(__import__("warcio.archiveiterator", fromlist=["ArchiveIterator"]).ArchiveIterator(
            io.BytesIO(forged), check_digests=True
        ))
    assert derive_states(read_warc(container)[0]["raw_http"]).s4 == b"actual content"
