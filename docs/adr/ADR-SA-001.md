---
id: ADR-SA-001
title: WARC 1.1 Preservation Envelope
status: FROZEN
date: 2026-08-20
layer: Source Acquisition / Preservation
evidence: spikes/warc-envelope-v2/REPORT.md
applies_to: future HTTP acquisition, preservation registry, integrity validation, and envelope storage
---

# ADR-SA-001 — WARC 1.1 Preservation Envelope

## Status

**FROZEN.** This decision is binding for future HTTP acquisition and preservation work. It does not authorize or implement a Source Acquisition Service, and it does not modify Timonelo's Evidence, Statement, Gatekeeper, authority, or knowledge semantics.

Normative terms such as **MUST**, **MUST NOT**, **SHALL**, **SHALL NOT**, **SHOULD**, and **MAY** are to be interpreted as requirements of this architecture decision.

## Context

Timonelo must preserve what an HTTP acquisition observed while keeping preservation mechanics separate from epistemic authority. The [WARC Envelope Spike v2](../../spikes/warc-envelope-v2/REPORT.md) measured WARC 1.1 behavior for transfer and content encoding, raw headers, redirects, binary content, corruption, HTTP/2, streaming, repacking, request secrets, and container compression.

The spike established that WARC is suitable as a durable preservation envelope only when Timonelo independently owns identity, byte-state derivation, validation, linkage, and integrity decisions.

> **WARC preserves recorded bytes.**
> **It does not certify truth, admissibility, authority or semantic correctness.**

## Decision

Timonelo SHALL adopt **WARC 1.1 plus an independent Timonelo Registry / Integrity Layer** as the preservation architecture for HTTP acquisition observations.

> **WARC + Registry is the architecture.**
> **WARC alone is insufficient.**
> **Registry alone is insufficient.**

WARC SHALL carry replay-oriented records, opaque wire evidence where available, and self-contained metadata copies. The Registry SHALL own canonical identities, queryable Observation metadata, Envelope coordinates, independently computed hashes, validation findings, and lifecycle state.

This decision freezes architecture only. Production acquisition, storage, transactionality, retention, and access-control implementation remain separate work.

## Artifact / Observation / Envelope Model

### Artifact

An Artifact is content-addressed. Its canonical identity SHALL be:

```text
content_sha256 = SHA-256(S4)
```

S4 is transfer-decoded and content-decoded bytes with no charset decoding, semantic normalization, or rendering.

Artifact identity MUST NOT depend on:

- transfer framing or compression representation;
- charset interpretation;
- HTTP headers;
- browser or semantic rendering;
- WARC Record ID;
- WARC container path, location, or hash;
- egress region or transport metadata.

One Artifact MAY be referenced by many Observations.

### Observation

An Observation is event-addressed and represents exactly one acquisition occurrence. A redirect chain SHALL be modeled as one Observation containing multiple ordered HTTP hops.

An Observation SHALL own, as available:

- requested URI and final URI;
- capture timestamp;
- egress region and egress IP;
- DNS answers and resolved IP;
- TLS version and cipher suite;
- HTTP version and ALPN;
- User-Agent;
- capture fidelity;
- redirect chain;
- Artifact reference;
- Envelope references.

Observation identity MUST NOT be derived from Artifact identity, WARC Record ID, container location, or container seal.

### Envelope

An Envelope is storage-addressed and identifies WARC record and container coordinates only. It SHALL include the relevant WARC location plus independently computed record and container integrity values.

Envelope identifiers MAY change during repacking. Envelope identity MUST NOT become Artifact identity or Observation identity.

## Byte-State Model

The following byte states are canonical vocabulary:

| State | Definition |
|---|---|
| **S0** | Exact observable transport representation or TLS plaintext where available. |
| **S1** | Exact HTTP response status line, ordered raw headers, and terminating CRLF. |
| **S2** | Exact framed HTTP body as transmitted, including chunk framing and trailers where applicable. |
| **S3** | Transfer-decoded body; chunk framing removed while Content-Encoding remains applied. |
| **S4** | Content-decoded bytes; canonical Artifact byte state. |
| **S5** | Charset-decoded text; derived only. |
| **S6** | Parsed or rendered semantics; derived only. |

No component SHALL use S5 or S6 as Artifact identity. A component MUST NOT label bytes as S4 until all declared transfer and content decoding required to reach S4 has succeeded.

## Hash Namespace

The following names and byte-state semantics are frozen:

### Artifact level

```text
content_sha256 = SHA-256(S4)
```

### Observation level

```text
wire_head_sha256 = SHA-256(S1)  # only when WIRE fidelity exists
wire_body_sha256 = SHA-256(S2)  # only when WIRE fidelity exists
payload_sha256   = SHA-256(S3)
```

### Envelope level

```text
warc_record_sha256    = Timonelo-computed SHA-256 of the complete WARC record
container_seal_sha256 = SHA-256 of the finalized, sealed WARC container
```

No generic canonical field named `sha256` SHALL be introduced on the Source Acquisition or Evidence path. Every hash name MUST identify its byte-state or envelope semantics.

`WARC-Block-Digest` and `WARC-Payload-Digest` are Envelope evidence. Timonelo MUST verify them independently. Neither SHALL be treated as Artifact identity, and neither SHALL replace an independently computed Timonelo hash.

## WARC Version

Production preservation SHALL write **WARC 1.1** explicitly and MUST NOT silently fall back to WARC 1.0.

WARC 1.1 is selected for sub-second `WARC-Date` precision, explicit request/response linkage, and compatibility with future revisit or reference semantics.

`WARC-Date` records recorder time. It MUST NOT be presented as authoritative third-party publication, observation, or event time.

## Capture Path

The production acquisition path SHALL use an explicitly owned `WARCWriter` flow.

`capture_http` MAY be used in isolated tests and differential experiments. It MUST NOT be used in the production acquisition path because it monkey-patches `http.client`, introduces global and hidden transformation boundaries, does not intercept httpx, is unsuitable for a transparent async evidence path, and weakens capture ownership.

## Wire Fidelity

warcio may normalize portions of an `application/http` representation. A replay-oriented request or response record alone is therefore insufficient proof of exact S1 and S2.

If an Observation declares:

```text
capture_fidelity = WIRE
```

Timonelo MUST additionally preserve exact S1+S2 as opaque raw-wire evidence, equivalent to an `application/octet-stream` WARC resource record. The ordinary request and response records SHALL remain the replay-oriented representation.

WIRE fidelity MUST NOT be claimed when exact bytes were not observed and retained.

## HTTP/2 Policy

The V1 policy is:

```text
ALLOW_HTTP_2_WITH_DECODED_FIDELITY
```

When an HTTP/2 client exposes decoded response semantics but not exact HPACK or frame bytes, the Observation SHALL declare:

```text
capture_fidelity = DECODED
```

Unavailable `wire_head_sha256` and `wire_body_sha256` values SHALL remain unset. They MUST NOT be synthesized from decoded headers or body APIs.

A future acquisition policy MAY explicitly retry HTTP/1.1 when WIRE fidelity is required.

## Redirect & Header Model

### Redirects

Redirect chains SHALL be explicit Observation data and MUST NOT be inferred solely from WARC record order, timestamps, or later Location parsing.

Each ordered hop SHALL contain at least:

- `hop_index`;
- request WARC record ID;
- response WARC record ID;
- status code;
- raw Location value;
- derived resolved Location;
- method before and after;
- scheme-change and host-change flags.

The Observation SHALL also contain `requested_uri`, `final_uri`, `hop_count`, and `loop_detected`.

### Headers

Raw evidence headers MUST NOT be modeled as a dictionary. The canonical raw representation SHALL be equivalent to:

```text
(index, name_bytes, value_bytes)
```

It SHALL preserve, where observed, order, duplicates, capitalization, whitespace, non-ASCII bytes, and trailers. Parsed or normalized headers MAY exist only as derived views.

Duplicate or conflicting framing headers MUST produce typed validation findings. They MUST NOT be silently collapsed or normalized in raw evidence.

## Content Decoding

`content_sha256` SHALL be computed only after all declared content decoding succeeds. V1 measured support includes `gzip`, `br`, and `zstd`.

Unknown, unsupported, malformed, or truncated content encodings MUST produce a typed validation or quarantine outcome. Still-compressed bytes MUST NOT be silently hashed as `content_sha256`.

Timonelo SHALL own independent transfer decoding where required. Chunk framing and trailers MUST NOT rely solely on warcio `content_stream()` behavior.

## Validation / Corruption Handling

WARC parsing alone is insufficient. Timonelo SHALL independently validate at least:

- WARC and container truncation;
- record Content-Length;
- malformed HTTP blocks;
- duplicate WARC Record IDs;
- request/response pairing;
- linkage and orphan records;
- WARC and Timonelo digest mismatches;
- compressed-member integrity;
- unsupported or broken encoding;
- finalized container seal.

Validation failures SHALL produce typed integrity findings. Corrupt evidence SHALL be retained immutably and SHALL NOT be deleted merely because validation failed. Its admissibility and downstream use MUST fail closed according to later lifecycle policy.

## Secret Hygiene

V1 SHALL use a dual request representation:

1. restricted raw request evidence;
2. sanitized general-access WARC request record.

Secret-bearing request bytes MUST NOT be silently persisted into broadly accessible archives. Sanitization MUST be explicit and SHALL record:

- redaction policy version;
- affected header names;
- restricted raw-envelope reference;
- sanitized capture fidelity or state.

Redaction metadata MUST NOT contain the removed secret values. Redaction MUST NOT be invisible.

## Transport Metadata

Observation is the authoritative and queryable owner of transport and egress metadata. WARC metadata or warcinfo records SHALL carry a self-contained copy where available.

This metadata includes egress region, egress IP, DNS answers, resolved IP, TLS version, cipher, HTTP version, ALPN, User-Agent, and capture fidelity.

Transport and egress metadata MUST NOT affect Artifact identity.

## Container Strategy

V1 SHALL use:

```text
one sealed WARC per Observation
one gzip member per WARC record
write -> validate -> seal -> immutable storage
```

Rolling append-only WARC containers SHALL NOT be used in V1 because they have unstable seals, broader corruption blast radius, and harder audit and recovery boundaries.

A later migration from per-Observation to per-session containers MAY occur without changing Artifact or Observation identity. Such migration is repacking and SHALL obey the repacking invariant below.

## Repacking Invariant

Repacking MAY change:

- WARC Record IDs;
- record and container locations;
- record or container hashes;
- storage coordinates.

Repacking MUST NOT change:

- Artifact `content_sha256`;
- Observation identity;
- semantic provenance references.

Canonical Registry references MUST NOT depend on container hashes or storage coordinates as Artifact or Observation identity.

## Guardrails

1. Artifact, Observation, and Envelope SHALL remain separate schema concepts.
2. Timonelo SHALL independently compute every canonical hash.
3. A successful WARC write MUST NOT imply truth, authority, admissibility, or semantic correctness.
4. Exact WIRE claims require retained opaque S1+S2 evidence.
5. Missing wire fidelity or wire hashes SHALL remain explicit and unset.
6. Redirect chains SHALL remain external to record ordering.
7. Corruption SHALL be retained with typed findings and fail-closed downstream handling.
8. Production capture SHALL use explicit WARCWriter ownership.
9. Request sanitization SHALL be disclosed and linked to restricted raw evidence.
10. Envelope storage identity SHALL never leak upward.

## Known Limitations

The supporting spike does not prove:

- streaming behavior beyond the measured 32 MiB fixture;
- multi-gigabyte acquisition and replay behavior;
- multipart object-storage recovery;
- interrupted upload recovery;
- full long-term pywb or cross-tool interoperability;
- Registry transactionality;
- retention and access-control implementation.

These limitations require future validation. They do not block adopting WARC 1.1 with the frozen independent Registry and integrity guardrails.

## Consequences

### Positive

- Captured HTTP evidence gains a standard replay and preservation envelope.
- Artifact identity remains stable across compression changes, redirects, repacking, and storage migration.
- Observation context remains queryable without overloading content identity.
- Corruption and unsupported decoding become explicit rather than silent.
- Future container strategies can evolve without breaking upper-layer identity.

### Costs and constraints

- WIRE fidelity requires additional opaque records and storage.
- Independent transfer/content decoding and validation are mandatory.
- Per-Observation containers increase object count.
- Restricted raw request evidence requires access-control and retention policy.
- HTTP/2 acquisitions cannot claim WIRE fidelity without a future frame-aware capture mechanism.

## Follow-Ups

The following work remains separately authorized and SHALL NOT be inferred from this ADR:

1. Define Artifact, Observation, Envelope, redirect-hop, header, metadata, finding, and redaction schemas.
2. Specify Observation identity generation and Registry transaction boundaries.
3. Design seal-on-close, interrupted-write recovery, and object-storage publication.
4. Validate multi-gigabyte streaming, multipart storage, and replay.
5. Perform pywb and additional long-term interoperability testing.
6. Define restricted-envelope access control, retention, and secret destruction policy.
7. Define quarantine and admissibility lifecycle integration without changing Evidence semantics.

No follow-up is implemented by this ADR.
