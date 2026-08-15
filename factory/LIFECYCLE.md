# Knowledge Pack Lifecycle State Machine
### The Canonical Progression from Raw Blueprint to Immutable Production Release

---

## 1. Lifecycle State Machine Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE PACK LIFECYCLE TOPOLOGY                        │
│                                                                             │
│   [ DRAFT ] ──────────► [ REVIEWED ] ──────────► [ VERIFIED ]               │
│       │                      │                         │                    │
│       │ (Rejection)          │ (Audit Failure)         │ (Audit Pass)       │
│       ▼                      ▼                         ▼                    │
│   [ REJECTED ]          [ DRAFT ]              [ EXPERIENCE READY ]         │
│                                                        │                    │
│                                                        │ (Sign & Seal)      │
│                                                        ▼                    │
│   [ ARCHIVED ] ◄────────── Drydock Refit ──────── [ PUBLISHED ]             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. State Definitions & Exit Criteria

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STATE               │ CORE DEFINITION                          │ MANDATORY EXIT CRITERIA                │
├─────────────────────┼──────────────────────────────────────────┼────────────────────────────────────────┤
│ 1. DRAFT            │ Working compilation artifact generated   │ Passes schema self-validation and basic│
│                     │ by Stage 05 (Pack Generation).           │ referential integrity audits.          │
├─────────────────────┼──────────────────────────────────────────┼────────────────────────────────────────┤
│ 2. REVIEWED         │ Succeeded Stage 06 Spatial Validation.   │ Zero polygon overlaps; 100% door-to-   │
│                     │ CAD vectors and corridor graphs verified.│ corridor snapping verified.            │
├─────────────────────┼──────────────────────────────────────────┼────────────────────────────────────────┤
│ 3. VERIFIED         │ Succeeded Stage 07 Experience Validation.│ Two-source rule verified for claims;   │
│                     │ Multi-source evidence corroborated.      │ 100% overhead sandwiches mapped.       │
├─────────────────────┼──────────────────────────────────────────┼────────────────────────────────────────┤
│ 4. EXPERIENCE READY │ Highest pre-publication audit state.     │ Experience Ready Score $\ge 90.0\%$;   │
│                     │ Complete vessel meets public standard.   │ approved for production deployment.    │
├─────────────────────┼──────────────────────────────────────────┼────────────────────────────────────────┤
│ 5. PUBLISHED        │ Digitally signed, sealed immutable pack  │ Active on production edge nodes and    │
│                     │ serving live passenger orientation.      │ local offline client runtimes.         │
├─────────────────────┼──────────────────────────────────────────┼────────────────────────────────────────┤
│ 6. ARCHIVED         │ Historical pack superseded by a drydock  │ Read-only historical access for past   │
│                     │ refit or major layout mutation.          │ voyage logs; never mutated in place.   │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. State Transition Matrix & Permissions

| Current State | Target State | Triggering Action | Validation & Authority Required |
| :--- | :--- | :--- | :--- |
| **None** | `DRAFT` | Pipeline compilation (Stage 05) | Automated compiler pass |
| `DRAFT` | `REVIEWED` | Spatial validation (Stage 06) | Spatial validator algorithm pass |
| `REVIEWED` | `DRAFT` | Spatial linting failure | Automatic rollback with error log |
| `REVIEWED` | `VERIFIED` | Experience validation (Stage 07)| Multi-source evidence audit pass |
| `VERIFIED` | `EXPERIENCE READY` | Final quality gate review | Quality score $\ge 90.0\%$ |
| `EXPERIENCE READY`| `PUBLISHED` | Stage 08 Publication | Cryptographic signature & maintainer release |
| `PUBLISHED` | `ARCHIVED` | Drydock refit compilation | Superseded by newly minted version pack |

---

## 4. Immutability & Sealing Rules

1. **Write-Once After Sealing**: The moment a Knowledge Pack enters `PUBLISHED` status, its SHA-256 hash is locked. No direct edits, patches, or database updates are ever made to a published pack.
2. **Corrections Require New Semantic Versions**: Any correction (e.g., fixing a mislabeled socket or updating a venue name) produces a new `PATCH` release (e.g., `v2.1.0` $\rightarrow$ `v2.1.1`).
3. **Refits Create Major Revisions**: When a vessel completes a shipyard drydock altering deck structures, a new `MAJOR` version pack is compiled (e.g., `v2.x` $\rightarrow$ `v3.0.0`), and the prior pack is transitioned to `ARCHIVED`.

---

## 5. Audit Logging & Provenance Ledger

Every state transition records an immutable audit log entry:

```json
{
  "event": "STATE_TRANSITION",
  "pack_id": "KP-IMO9766205-V2.1.0",
  "from_state": "VERIFIED",
  "to_state": "EXPERIENCE_READY",
  "timestamp_utc": "2026-08-15T22:30:00Z",
  "experience_ready_score": 94.5,
  "validation_report_hash": "sha256:4b9a8f2e...",
  "triggered_by": "factory.stages.experience_validator"
}
```
