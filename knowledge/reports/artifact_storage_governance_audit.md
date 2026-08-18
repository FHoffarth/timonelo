# Artifact Storage Governance Audit

**Date**: 2026-08-18  
**Audit Target**: Physical binary artifact storage and deduplication across Timonelo repository.

---

## 1. Inventory of Observed Artifact Duplicates

| File Path | File Size | SHA-256 Digest | Original Role | Audit Decision |
| :--- | :--- | :--- | :--- | :--- |
| `evidence/raw/sha256/77/77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9.pdf` | 1,969,779 bytes | `77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9` | Content-addressed Evidence Vault storage | **KEEP (CANONICAL)** |
| `knowledge/ships/msc-meraviglia/artifacts/MSC_MERAVIGLIA_DECKPLAN_GER.pdf` | 1,969,779 bytes | `77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9` | Local ship folder copy | **REMOVE (REDUNDANT)** — Knowledge records reference artifact metadata and SHA-256; they do not store redundant binaries. |
| `tests/fixtures/MSC_MERAVIGLIA_DECKPLAN_GER.pdf` | 1,969,779 bytes | `77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9` | Harvester test fixture | **REMOVE (REDUNDANT)** — Tests reference canonical Evidence Vault. |

---

## 2. Canonical Governance Policy

1. **One Authoritative Byte Identity**: Every immutable physical document possessed by Timonelo resides under `evidence/raw/sha256/<prefix>/<sha256>.<ext>`.
2. **Zero In-Tree Binary Duplication**: Knowledge directories (`knowledge/ships/<slug>/`) and test suites (`tests/`) MUST NOT store redundant multi-megabyte copies of production PDFs.
3. **Reference Integrity**: All JSON models and test fixtures refer to the artifact by its content-addressed SHA-256 identifier and locator.

---

## 3. Final Canonical Artifact Path

- **Artifact Name**: `MSC Meraviglia Deckpläne (11.2025 DEU)`
- **Canonical Vault Path**: `evidence/raw/sha256/77/77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9.pdf`
- **SHA-256**: `77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9`
- **Byte Count**: `1,969,779 bytes`
- **Verification Status**: `VERIFIED`
