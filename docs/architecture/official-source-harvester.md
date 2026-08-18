# Architecture Specification: Official Source Harvester v0.1

**Document ID**: `TIM-ARCH-HARV-001`  
**Status**: `CANONICAL`  
**Version**: `0.1.0`  
**Date**: `2026-08-18`  
**Scope**: `MSC Cruises (Deck Plans)`  

---

## 1. Executive Summary & Purpose

The **Official Source Harvester v0.1** is Timonelo's automated source supply infrastructure. Its sole responsibility is to discover, download, verify, fingerprint, version, and register immutable primary source artifacts.

### Core Architectural Axioms
1. **Discovery is not verification**: Finding a URL on the internet does not make the content authentic.
2. **A URL is not evidence**: Only the retrieved, verified, and content-addressed immutable artifact file constitutes evidence.
3. **Strict Separation of Concerns**: The Harvester supplies verified sources; the Knowledge Factory extracts knowledge facts. The Harvester never generates cabin counts, dimensions, venues, or deck names.

---

## 2. Ingestion Pipeline & Architecture Flow

```text
Official Domains (Tier A/B)
         ↓
Discovery Engine (Sitemap, Patterns, Link Crawler, Local Fixtures)
         ↓
Artifact Fetcher (Robots.txt check, Rate Limiter, Polite User-Agent)
         ↓
Byte-Level Verifier (Magic Bytes %PDF-, Parseability via pypdf, Page Count, File Size)
         ↓
Cryptographic Fingerprinter (SHA-256 Byte Digest)
         ↓
Document Classifier (DECK_PLAN vs. UNKNOWN, Language & Edition Detection)
         ↓
Vessel Resolver (Deterministic Fleet Matching)
         ↓
Immutable Evidence Vault (evidence/raw/sha256/ab/abcdef....pdf)
         ↓
Source Registry (data/sources_registry.json & Version Tracking)
```

---

## 3. Trust Tiers

| Tier | Classification | Verification Status | Rules & Constraints |
| :--- | :--- | :--- | :--- |
| **TIER A** | Direct Official MSC Domain (e.g. `msccruises.de`, `msccruises.com`) | `VERIFIED_OFFICIAL_SOURCE` | Primary canonical source domain. |
| **TIER B** | Official MSC CDN / Asset Host (e.g. `msc-media.azureedge.net`, `assets.msccruises.com`) | `VERIFIED_OFFICIAL_SOURCE` | Asset origin verified via official linkage. |
| **TIER C** | Third-party Portals / Mirrors / Blogs | `UNVERIFIED_THIRD_PARTY` | Allowed solely as discovery hints; never certified as official primary source. |

---

## 4. Lifecycle States

```text
Positive Lifecycle:
  DISCOVERED → FETCHED → FILE_VALID → OFFICIAL_DOMAIN_VERIFIED → FINGERPRINTED → CLASSIFIED → VESSEL_MATCHED → REGISTERED

Alternative / Duplicate / Error States:
  DUPLICATE (Same SHA-256 already registered in Vault)
  ROBOTS_BLOCKED (Forbidden by robots.txt)
  HTTP_FAILED (Network error or non-200 HTTP status)
  NOT_A_PDF (Invalid header or HTML masquerade)
  CORRUPT_FILE (Parser error when reading pages)
  VESSEL_UNRESOLVED (Ship name not deterministically identifiable)
  MANUAL_REVIEW_REQUIRED (Ambiguous multiple ship names found)
  VERSION_CANDIDATE (New SHA-256 for existing vessel deck plan)
```

---

## 5. Content-Addressable Evidence Vault

Artifacts are stored in the immutable filesystem vault keyed by their SHA-256 hash:

```text
evidence/
  raw/
    sha256/
      77/
        77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9.pdf
```

### Idempotency Guarantee
- If an artifact with the exact same SHA-256 is fetched again, the vault ignores the write and returns `is_duplicate = True`.
- The registry updates the record's `retrieval_history` timestamp list without creating duplicate entries.

---

## 6. Source Registry Schema (`data/sources_registry.json`)

```json
{
  "source_id": "SRC-MSC-MERAVIGLIA-77F5A51B",
  "cruise_line_id": "msc",
  "vessel_id": "msc-meraviglia",
  "document_type": "DECK_PLAN",
  "title": "MSC Meraviglia Deckpläne",
  "publisher": "MSC Cruises",
  "language": "de",
  "edition": "11.2025",
  "source_url": "https://www.msccruises.de/deckplans/msc-meraviglia.pdf",
  "final_url": "https://www.msccruises.de/deckplans/msc-meraviglia.pdf",
  "retrieved_at": "2026-08-18T21:56:33.400Z",
  "sha256": "77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9",
  "file_size_bytes": 1969779,
  "page_count": 6,
  "mime_type": "application/pdf",
  "source_tier": "TIER_A",
  "verification_status": "VERIFIED_OFFICIAL_SOURCE",
  "vault_path": "evidence/raw/sha256/77/77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9.pdf",
  "retrieval_history": [
    "2026-08-18T21:56:33.400Z"
  ]
}
```

---

## 7. Version Candidate Model

When a new artifact is discovered for a known vessel with a different SHA-256 digest:
1. It is stored as a distinct immutable artifact in the vault.
2. It is added to `versions` with status `CURRENT_CANDIDATE`.
3. The Knowledge Factory is notified of a potential new edition candidate for diffing and conflict resolution.

---

## 8. Guardrails & Compliance

1. **Robots.txt & Rate Limiting**: Checked before every HTTP request. Mandatory delay of $\ge 1.0\text{ s}$ between requests to official servers.
2. **No Scraping behind Login / Paywalls**: Only publicly accessible resources are harvested.
3. **No Knowledge Generation**: The harvester does not populate `cabins.json` or `decks.json`.
