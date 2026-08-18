# 03_TRUTH_ENGINE — Epistemic Calculus & Grounding

## 1. Core Mandate

> **"Never present certainty where only inference exists."**

Every statement in the Timonelo knowledge graph is an assertion accompanied by **epistemic metadata**: who asserted it, from which physical artifact it was extracted, what algorithm derived it, and what confidence level applies.

---

## 2. Epistemic Classification States

```
                                  [ STATEMENT ]
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
            [ DIRECT EVIDENCE ]                    [ INFERRED / DERIVED ]
           (SHA-256 Pinned GA)                   (Topological Heuristics)
                    │                                       │
            ┌───────┴───────┐                       ┌───────┴───────┐
            ▼               ▼                       ▼               ▼
      [ VERIFIED ]       [ KNOWN ]              [ DERIVED ]      [ LIKELY ]
     (Peer-Reviewed)   (Direct Fact)          (Calculus Rule)  (Statistical)
```

| Epistemic State | Badge Tag | Meaning & Evidentiary Standard | Confidence |
| :--- | :--- | :--- | :--- |
| **VERIFIED** | `[VERIFIED]` | Grounded in official builder GA plans, verified by human review or multi-artifact agreement. | $c \ge 0.98$ |
| **KNOWN** | `[KNOWN]` | Directly stated in primary authoritative documentation (e.g. published deck plan or tariff). | $c \ge 0.90$ |
| **DERIVED** | `[DERIVED]` | Calculated via topological adjacency rules, parity sequencing, or structural symmetry. | $0.70 \le c < 0.90$ |
| **LIKELY** | `[LIKELY]` | Statistical estimate or seasonal itinerary profile based on historical patterns. | $0.50 \le c < 0.70$ |
| **UNKNOWN** | `[UNKNOWN]` | Insufficient or missing evidence; marked explicitly rather than fabricated. | $c = 0.00$ |
| **CONFLICT** | `[CONFLICT]` | Multiple authoritative sources make contradictory statements (e.g. 2 vs 4 berth capacity). | Requires Review |

---

## 3. Provenance & W3C PROV-O Pinning

Every stateroom or venue entity includes a `prov:wasDerivedFrom` record containing:
- `artifact_id`: e.g. `MSC-BEL-GA-2019-REV4-P14`
- `sha256`: Cryptographic hash of the source document
- `statement_id`: e.g. `STM-BEL-14122-PRM`
- `extractor_activity`: Algorithm or pipeline step that generated the claim
- `attribution`: Reviewer ID or verification agent
