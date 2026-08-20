# Timonelo WARC Envelope Spike v2

## Environment

- Python: 3.12.13
- warcio: 1.8.1
- requests: 2.34.2
- urllib3: 2.7.0
- httpx: 0.28.1
- httpcore: 1.0.9
- Brotli: 1.2.0
- zstandard: 0.25.0
- Platform: Windows 11
- Written format: WARC 1.1, explicitly selected
- Test environment: external temporary virtual environment; no production dependency changed

The deterministic measurements are recorded in `measurements.json`. No Timonelo production module is imported by this spike.

## Architecture Under Test

The three identities remain separate:

1. **Artifact** — content-addressed by `content_sha256 = SHA-256(S4)`.
2. **Observation** — event-addressed and records one acquisition occurrence, URI, redirect chain, transport metadata, fidelity and Artifact reference.
3. **Envelope** — storage-addressed by WARC record location, `warc_record_sha256`, and sealed-container `container_seal_sha256`.

WARC is an evidence envelope. Its identifiers and built-in digests are not Artifact authority. Repacking may change every Envelope coordinate without changing Artifact or Observation identity.

## Byte-State Findings

| State | Meaning | Combined-case bytes | Availability |
|---|---|---:|---|
| S0 | TLS plaintext / exact observable wire representation | not exposed for HTTP/2 | conditional |
| S1 | status line, ordered raw headers, terminal CRLF | 71 | captured for HTTP/1.1 |
| S2 | exact chunk-framed transmitted body | 109 | captured for HTTP/1.1 |
| S3 | transfer-decoded, still gzip encoded | 59 | independently derived |
| S4 | content-decoded bytes, no charset decode | 288 | independently derived |
| S5 | charset-decoded text | n/a | derived only |
| S6 | parsed/rendered semantics | n/a | derived only |

For the gzip+chunked case, `ArchiveIterator.raw_stream` exposes S2. `content_stream()` exposes S4 when no trailers are present. With chunk trailers, `content_stream()` produced an incorrect payload suffix (`0\r\nTrailer: ...`); therefore Timonelo must independently dechunk and parse trailers.

## Hash Findings

Measured combined-case hashes:

| Namespace | SHA-256 |
|---|---|
| `wire_head_sha256` | `20b197be648c3c79e3610c7d8ff3132cd98a72ee3c2b86beeea7990ba20de1e4` |
| `wire_body_sha256` | `125505933507bfc20a36a48094b685d74134ae2b58796695af22ab065c792368` |
| `payload_sha256` | `01f3588a2d68c120b1667eb8bf47c263c26540046397e48cdee22305f058764d` |
| `content_sha256` | `d47c712a9424a0856ff8daeff9fe03fc96ae2c8abe2b54449ea0c733b9027ede` |

`WARC-Payload-Digest` exactly matched SHA-1(S2), not S3 or S4. `WARC-Block-Digest` matched SHA-1(S1+S2). Both are independently verifiable Envelope data; neither is Artifact identity.

In a one-record, uncompressed container, `warc_record_sha256` and `container_seal_sha256` may have the same value. The namespaces remain distinct because they diverge for multi-record or repacked containers.

## Simple Response

**PASS.** Request, response, URI, status, normal ordered headers, and body survived WARC 1.1 round-trip. S1–S4 were derivable and `content_sha256` remained stable.

## Gzip

**PASS.** S3 was the deterministic gzip stream and S4 the inflated bytes. Their hashes differed. UTF-8 text was never charset-decoded for Artifact hashing.

## Chunked

**PASS WITH GUARDRAIL.** The WARC response stored S2 with the `Transfer-Encoding: chunked` header, so the stored block remained truthful. Independent dechunking produced S3/S4 exactly. warcio trailer handling was not reliable and must not define S3.

## Gzip + Chunked

**PASS.** S1, S2, S3 and S4 were independently measured and all four relevant hashes differed. The response block stored S2, `raw_stream` exposed S2, and `content_stream()` exposed S4 for the trailer-free fixture. Artifact round-trip identity was exact.

## Redirect Chain

**PASS.** The external model records hop index, request/response IDs, raw and resolved Location, status, method transition, and scheme/host changes. A 302 relative hop changed POST to GET; a 307 cross-host hop retained GET. Loop detection used visited resolved URIs. Reconstruction does not use WARC record order; capture_http itself emitted response before request in the measured file.

## Header Fidelity

**PARTIAL.** Duplicate headers, capitalization, order and most values survived. However, manual `create_warc_record()` parsed and rewrote an application/http response: leading horizontal whitespace was normalized and a non-ASCII value was percent-encoded. Dictionary comparison is therefore forbidden.

Required representation is `(index, name_bytes, value_bytes)`. For `capture_fidelity=WIRE`, Timonelo must store an additional opaque `application/octet-stream` WARC resource record containing exact S1+S2. The ordinary response record remains the replay-oriented representation.

Conflicting Content-Length, Content-Length plus Transfer-Encoding, duplicate Content-Encoding, duplicate Location and duplicate Content-Type were preserved as evidence by the manual fixture; no client was asked to interpret these unsafe combinations.

## Binary / PDF

**PASS.** A deterministic PDF-like binary payload containing NUL, `0xff`, and `0x80` round-tripped byte-exactly. No text conversion occurred and `content_sha256` matched.

## Corruption Matrix

| Case | warcio | Independent Timonelo finding |
|---|---|---|
| A truncated WARC header | accepted/no finding | `TRUNCATED_WARC_HEADER` |
| B truncated record body | accepted/no finding | `TRUNCATED_WARC_RECORD_BODY` |
| C bad WARC Content-Length | accepted/no finding | `TRUNCATED_WARC_RECORD_BODY` |
| D malformed HTTP status | accepted | `PAYLOAD_DECODE_FAILURE` |
| E malformed HTTP terminator | rejected | `WARC_RECORD_TERMINATOR_INVALID`, parse failure |
| F forged Payload-Digest | rejected with digest checking | `WARC_DIGEST_VALIDATION_FAILURE` |
| G forged Block-Digest | rejected with digest checking | `WARC_DIGEST_VALIDATION_FAILURE` |
| H duplicate Record-ID | accepted | `DUPLICATE_WARC_RECORD_ID` |
| I missing request/response pair | accepted | `MISSING_REQUEST_RESPONSE_PAIR` |
| J container truncation | accepted/no record | `TRUNCATED_WARC_HEADER`, `NO_WARC_RECORDS` |
| K truncated gzip member | accepted | `PAYLOAD_DECODE_FAILURE` |
| L invalid linkage | accepted | `INVALID_LINKAGE` |

**PASS.** All corrupt bytes were retained verbatim with their size and container hash in `corruption_corpus.json`; the harness returned typed findings. warcio alone is insufficient for structural, linkage and content-decoding validation.

## Non-Deterministic Content

**PASS.** Two bodies from the same Source URL produced two Observation IDs, two Artifacts and two distinct `content_sha256` values. Source URL did not become identity.

## HTTP/2

**PASS WITH POLICY.** A live request negotiated HTTP/2 through ALPN `h2`, TLS 1.3, and `TLS_AES_256_GCM_SHA384`. httpx exposed decoded headers/body and protocol metadata, not HPACK blocks or exact HTTP/2 frames. S0/S1/S2 wire fidelity cannot be claimed.

Recommendation: **ALLOW_HTTP_2_WITH_DECODED_FIDELITY**. Such Observations must set `capture_fidelity=DECODED`, leave unavailable wire hashes unset, and never synthesize them. A policy requiring wire fidelity may retry explicitly over HTTP/1.1.

## Brotli / Zstd

**PASS.** Brotli 1.2.0 and zstandard 0.25.0 decoded deterministic fixtures to exact S4. An unknown encoding raised `CONTENT_ENCODING_UNSUPPORTED`; compressed bytes were never silently treated as `content_sha256` input.

## Large Artifact Streaming

**PASS WITH LIMIT.** A deterministic 32 MiB payload was written as a disk-backed, per-record-gzipped WARC and replay-hashed without materializing the payload in memory. Replay returned 33,554,432 bytes with the same hash. Peak Python-traced allocation was approximately 16.2 MiB and the compressed container approximately 130.8 KiB; exact run values are in `measurements.json`. The spike proves bounded behavior at 32 MiB, not at multi-gigabyte scale.

## Empty / Partial Bodies

**PASS.** 204, 304, 206 with Content-Range, and 200 with an explicit zero-length body remained distinct Observations. Empty S4 bytes may legitimately share one Artifact identity; status and range semantics remain on Observation and are not collapsed.

## TLS / DNS / Egress

The live Observation measured:

- resolved/DNS IP: `139.162.123.134`
- egress IP: `93.195.232.11`
- egress edge/region indicator: `FRA`
- TLS: 1.3
- cipher: `TLS_AES_256_GCM_SHA384`
- HTTP/ALPN: HTTP/2 / `h2`

Observation is authoritative/queryable for egress region/IP, DNS answers, resolved IP, TLS, cipher, HTTP version, User-Agent and fidelity. A WARC metadata or warcinfo record carries a self-contained copy. None affects Artifact identity.

## Secret Hygiene

Synthetic Authorization, Cookie and X-API-Key headers were tested.

- Option A preserves evidence but creates unacceptable broad secret persistence.
- Option B is safe for general WARC access but is not faithful raw request evidence.
- Option C is recommended: access-controlled raw request evidence plus a sanitized WARC request record.

Redaction must record policy version, affected header names, raw restricted-envelope reference, and `capture_fidelity=SANITIZED_REQUEST`. It must never occur silently. Response Artifact identity is unaffected.

## capture_http vs WARCWriter

| Property | `capture_http` | explicit WARCWriter |
|---|---|---|
| requests | works | client-independent |
| httpx | zero records measured | works with supplied bytes |
| async | unsafe/unproven | caller-controlled |
| global effects | replaces `http.client.HTTPConnection` at import | none |
| thread isolation | thread-local recorder over global class patch | normal ownership |
| standard gzip+chunked block | exact in local measurement | exact in local measurement |
| weird header normalization | writer/parser limitations remain | writer/parser limitations measured |
| production recommendation | no | yes |

`capture_http` is retained only as a differential oracle. Production should explicitly acquire bytes, compute Timonelo hashes, and write records with WARCWriter.

## WARC 1.1

**PASS.** Every record used `WARC/1.1`. Explicit microsecond WARC-Date values survived, including multiple records created within one second. Unique request/response record IDs and `WARC-Concurrent-To` linkage survived. Metadata records replayed. No WARC 1.0 fallback occurred.

## Container Strategy

| Option | Assessment |
|---|---|
| one WARC per Observation | smallest corruption blast radius, simple immutable seal and deletion policy; higher object count |
| one per acquisition session | fewer objects but broader corruption/replay and access-control blast radius |
| rolling append-only | unstable seal until roll, complex recovery and migration; reject for V1 |

Per-record gzip produced two independently replayable gzip members. Whole-file gzip was smaller in the tiny fixture but warcio rejected it as non-seekable/non-multimember. Recommended V1: **one sealed WARC per Observation, one gzip member per record, seal-on-close**.

Artifact deduplication occurs above the Envelope using `content_sha256`; WARC containers are not deduplicated identities.

## Repack Test

**PASS.** Rewriting identical HTTP content with new WARC record IDs changed the record/container hashes and Envelope IDs. S4, `content_sha256`, and the externally assigned Observation ID remained unchanged. No Artifact or Observation reference depended on container coordinates.

## Digest Forgery Test

**PASS.** Deliberately altering `WARC-Payload-Digest` while preserving content caused digest-checked parsing to fail. Timonelo still derives Artifact identity from independently decoded S4. The WARC digest is evidence to verify, never authority.

## Freeze Criteria Matrix

| Criterion | Result | Evidence |
|---|---|---|
| F1 gzip+chunked model | PASS | four independently measured states |
| F2 stored byte state | PASS | response stores S2; opaque record preserves exact block |
| F3 hash namespace | PASS | six explicit names, no generic `sha256` field |
| F4 independent recomputation | PASS | SHA-256 and WARC SHA-1 coverage compared |
| F5 forged digest | PASS | mismatch rejected/quarantined |
| F6 binary identity | PASS | PDF fixture exact |
| F7 corruption matrix | PASS | twelve typed cases |
| F8 Artifact/Observation split | PASS | same URL, two observations/artifacts |
| F9 HTTP/2 policy | PASS | decoded-fidelity policy selected |
| F10 redirects external | PASS | explicit chain independent of WARC order |
| F11 capture path | PASS | WARCWriter selected; capture_http oracle only |
| F12 container strategy | PASS | one Observation, per-record gzip, sealed |
| F13 repacking | PASS | upper identities stable |
| F14 secret policy | PASS | dual restricted/sanitized representation |
| F15 conclusion consistency | PASS | harness, schema recommendation and guardrails align |

## Required Timonelo Guardrails

1. Keep Artifact, Observation and Envelope schemas separate.
2. Compute every Timonelo hash independently; never trust WARC digest headers.
3. Never expose a generic `sha256` field.
4. Persist exact HTTP/1.1 S1+S2 as an opaque raw-wire record when claiming WIRE fidelity.
5. Store a replay-oriented WARC request/response record separately from opaque wire evidence.
6. Reject or quarantine unsupported content encodings and truncated compressed members.
7. Validate WARC framing, declared lengths, IDs, linkage, pairing, seals and decoded content independently.
8. Model redirect chains externally and never infer them from record order.
9. Declare HTTP/2 captures as DECODED unless a frame-aware capture mechanism exists.
10. Use explicit WARCWriter ownership; prohibit capture_http in production.
11. Use one sealed WARC per Observation with per-record gzip members.
12. Use dual restricted/sanitized request evidence with disclosed redaction.
13. Keep TLS/DNS/egress metadata on Observation and copy it into WARC metadata.
14. Preserve corrupt envelopes immutably and attach typed integrity findings.

## Open Risks

- warcio's response parser normalizes some header bytes; opaque raw-wire storage is mandatory for byte fidelity.
- Trailer behavior in `content_stream()` is unsuitable as Timonelo's transfer decoder.
- HTTP/2 frame fidelity is not available through httpx.
- Large streaming was measured only to 32 MiB on this environment.
- Multi-gigabyte replay, interrupted upload recovery, object-store multipart behavior and long-term WARC tooling interoperability remain future validation work.
- Observation ID generation, registry transactionality, retention and access-control implementation are intentionally outside this spike.

## Final Architecture Recommendation

Adopt **WARC 1.1 plus an independent Timonelo registry/integrity layer**, subject to all guardrails above.

The production capture architecture should use explicit WARCWriter, one sealed per-Observation container, per-record gzip, independent S-state hashing, an opaque raw-wire record when WIRE fidelity is claimed, and external Observation metadata/linkage. `capture_http` must remain test-only.

WARC preserves recorded bytes. It does not certify truth, admissibility, authority or semantic correctness.

WARC ENVELOPE SPIKE v2 — ADOPT WITH GUARDRAILS
