# Port Identity Corpus Audit — 2026-08-24

**Branch audited**: `develop`
**HEAD**: `868325a` (*Merge pull request #55 from FHoffarth/feature/public-deck-geometry-review-workspace-v1*)
**Scope**: `knowledge/ports/` and every consumer that reads it
**Method**: corpus-wide distinct-value analysis, followed by generator-source confirmation
**Status**: findings confirmed against generator source; remediation proposed in ADR-0006

---

## 0. Why this audit replaced the planned sprint

The commissioned work was a port-by-port reconciliation sprint: audit a sample
of ports, downgrade unsupported precision, reconcile external research.

That plan could not have found the defect described here. Every
`identity.json` file in the repository is individually well-formed and
individually plausible. Barcelona reads like researched data. So does Hamburg.
So does Singapore. The defect is invisible at file scope and only appears in
the **distribution across the corpus** — which is why a sampling audit of eight
ports would have returned a clean bill of health for a corpus in which every
trust-bearing field is a constant.

**Generalisable lesson:** a machine-readable corpus should be audited by
scanning it, not by reading a sample of it. Sampling answers "is this file
plausible?" Scanning answers "is this corpus data?" Only the second question
detects generator output.

---

## 1. Corpus inventory

| Measure | Value |
|---|---|
| Port directories under `knowledge/ports/` | 119 |
| `identity.json` files | 119 |
| Total JSON files in tree | 161 |
| Directories with `identity.json` only | 113 |
| Directories with the 8-file rich layout | 6 |
| Distinct file layouts | 2 |

The six rich-layout ports are **Barcelona, Genoa, Marseille, Messina, Naples,
Valletta**, each carrying `emergency.json`, `identity.json`, `medical.json`,
`port.json`, `sustainability.json`, `terminals.json`, `transport.json`,
`weather.json`.

---

## 2. Principal finding — the identity layer is template output

Across all 119 ports, every trust-bearing field resolves to a single constant
or to a two-valued split:

| Field | Distinct values across 119 ports |
|---|---|
| `timezone` | `"UTC"` — 119/119 |
| `sources[].field` | `"all"` — 119/119 |
| `sources[].source_id` | `"src:official-port-authority"` — 119/119 |
| `sources[].trust_level` | `"OFFICIAL"` — 119/119 |
| `sources[].retrieved_at` | `2026-08-16T12:00:00Z` — 119/119 |
| `terminals[].walking_time_min` | `10` — 119/119 |
| `terminals[].step_free_access` | `true` — 119/119 |
| `logistics.card_acceptance_pct` | `98` — 119/119 |
| terminals per port | `1` — 119/119 |
| `terminals[].distance_to_city_center_m` | `500` (101) / `800` (18) |
| `terminals[].gangway_deck_default` | `5` (108) / `2` (11) |
| `terminals[].berths` | 2 synthetic entries (101) / 1 (18) |
| `negative_intelligence` | two templates, 101/18 split |

There is no third value anywhere in the corpus for any of these fields.

### 2.1 The 101/18 split explained

The split is not a data property. It is **two generators**, each with its own
hardcoded template:

| Generator | Ports | Fingerprint |
|---|---|---|
| `tools/mass_populate_knowledge.py` (~L170–205) | 101 | `distance_to_city_center_m: 500`; `berths: ["{Slug} Berth 1", "{Slug} Berth 2"]`; `gangway_deck_default: 5 if "River" not in region else 2`; `negative_intelligence[0] = f"Check terminal berth assignment upon morning arrival in {name}."` |
| `tools/populate_classes_and_ports.py` (~L52–86) | 18 | `distance_to_city_center_m: 800`; `berths: ["{Slug} Pier 1"]`; `gangway_deck_default: 5`; `negative_intelligence[0] = f"Verify pier location in {name}."` |

The `gangway_deck_default` 108/11 split is a nested conditional inside
generator A: eleven river ports carry `2`, everything else `5`.

Both generators emit the identical blanket source record:

```python
"sources": [
    {"field": "all", "source_id": "src:official-port-authority",
     "trust_level": "OFFICIAL", "retrieved_at": "2026-08-16T12:00:00Z"}
]
```

**These values are synthetic/template-derived and carry no field-level
evidence.** This is not inferred from the distribution — the generator source
is in the repository and is quoted above. The distribution raised the
question; the generator source answered it.

---

## 3. Provenance laundering

The blanket source record is the mechanism by which unsourced generator output
acquired an authoritative appearance. Three independent defects compound:

1. **`field: "all"`** — a source covering every field attests no field in
   particular. It cannot establish provenance for `card_acceptance_pct` or for
   anything else.
2. **`source_id: "src:official-port-authority"`** — this names a *category of
   authority*, not a retrievable document. No artifact, no URL, no content
   address. There is nothing behind it to fetch or verify.
3. **`trust_level: "OFFICIAL"`** — the corpus's highest trust label, applied
   uniformly by a generator to values the generator itself invented.

`retrieved_at` is identical to the second across all 119 ports, which is not a
possible outcome of 119 retrievals.

This is the P0-A/P0-B anti-pattern in its purest observed form: unsourced
values inheriting an authoritative provenance stamp. It is more severe than
the earlier instances, because here the values never had a source at any point
— the stamp was applied by a generator to content it fabricated in the same
statement.

---

## 4. Passenger-facing risk

Ranked by consequence to a traveller.

### 4.1 `timezone: "UTC"` on all 119 ports — SEVERE

All-aboard time is computed from this field. The corpus spans Reykjavík to
Sydney; not one port is correctly UTC in practice for local operations
(Barcelona is `Europe/Madrid`). A passenger acting on a UTC-derived all-aboard
time in Barcelona in summer is wrong by two hours in the direction that misses
the ship.

### 4.2 `logistics.emergency_phone` — SEVERE

Not in the original quarantine scope; discovered during consumer analysis and
added. The generators derive this from a country allow-list with an
else-branch fallback:

```python
"emergency_phone": "112" if p["country"] not in ["United States", "Puerto Rico"] else "911"
```

Distribution: `112` (91 ports), `911` (23), `999` (5). The else-branch
misroutes every country outside the allow-list. Confirmed incorrect values
include:

| Port | Country | Stored | Actual |
|---|---|---|---|
| `costa-maya`, `cozumel` | Mexico | `112` | `911` |
| `bridgetown` | Barbados | `112` | `511` / `911` |
| `grand-cayman` | Cayman Islands | `112` | `911` |
| `haifa` | Israel | `112` | `100` / `101` / `102` |

A wrong emergency number published under `trust_level: OFFICIAL` is the most
directly harmful fact in the corpus. Phase 2F (fail-closed on passenger-facing
claims) applies without qualification.

### 4.3 `logistics.currency` — MODERATE

31 of 119 ports carry the literal string `"Local"`, the generator's
else-branch. This is a non-value occupying a field a passenger would read.

### 4.4 Synthetic precision — MODERATE

`walking_time_min: 10`, `distance_to_city_center_m: 500/800`,
`card_acceptance_pct: 98`, `step_free_access: true`. Each is actionable and
each is invented. `step_free_access: true` corpus-wide is an accessibility
claim asserted for 119 ports without a single observation, and is the one most
likely to strand a wheelchair user.

---

## 5. Duplicate UN/LOCODE entity pairs

Two LOCODEs appear twice, indicating either duplicate directories for one port
or a genuine entity-identity question:

| LOCODE | Directories |
|---|---|
| `USPEF` | `fort-lauderdale`, `port-everglades` |
| `ITTRS` | `trieste`, `venice-trieste` |

Both pairs are plausibly the same physical port under two slugs — the same
class of question as New York vs. Bayonne, but already live in the repository.
All 119 LOCODEs are syntactically well-formed (5 chars, uppercase
alphanumeric); none has been validated against the UNECE list.

**Not resolved in this audit.** Entity identity is an ontology decision
requiring its own ADR, not a cleanup edit.

---

## 6. The six rich-layout ports

These carry a **second, incompatible provenance model**:

```json
"provenance": { "source_artifact": "CRUISE_PORT_INTELLIGENCE_PROFILE_WEST_MED_2026" }
```

plus per-item `"source"` (a prose authority name) and `"provenance"` (an opaque
string such as `"BCN-PA-TERM-A"`). Neither resolves to a content-addressed
artifact. `CRUISE_PORT_INTELLIGENCE_PROFILE_WEST_MED_2026` is a name, not an
address.

**However**: this content does not exhibit template fingerprints. Values vary
per port, are specific and checkable (named hospitals with addresses and phone
numbers, named metro lines, named terminal operators), and read as
hand-researched. Its provenance model is inadequate; its *content* is not
demonstrated to be synthetic and **must not be assumed invalid merely because
`identity.json` in the same directory is**.

### 6.1 `identity.json` vs `port.json` contradictions

| Port | terminals in `identity.json` | in `port.json` | in `terminals.json` | `un_locode` | `unlocode` |
|---|---|---|---|---|---|
| barcelona | 1 | 8 | 8 | `ESBCN` | `ES-BCN` |
| genoa | 1 | 3 | 3 | `ITGOA` | `IT-GOA` |
| marseille | 1 | 2 | 2 | `FRMRS` | `FR-MRS` |
| messina | 1 | 1 | 1 | `ITMSN` | `IT-MSN` |
| naples | 1 | 3 | 3 | `ITNAP` | `IT-NAP` |
| valletta | 1 | 2 | 2 | `MTMLA` | `MT-MLA` |

Two divergences: the single-terminal count is generator output contradicting
researched data, and the LOCODE is stored under two field names in two formats
in the same directory.

---

## 7. Unexpected findings

### U-1 — The frontend bridge is an independent second source of synthetic values

`tools/generate_frontend_bridge.py` (~L130–170) does **not** read these values
from the knowledge layer. It hardcodes them inline at generation time:

```python
"berths": ["Berth 1", "Berth 2"],
"gangwayDeckDefault": 5,
"distanceToCenterM": 500,
"walkingTimeMin": 10,
"cardAcceptancePct": 98,
"officialSource": {
    "authority": f"{name} Port Authority",
    "url": "https://www.timonelo.com",
    "trustLevel": "OFFICIAL",
},
```

Three consequences:

1. **Quarantining `identity.json` does not stop the frontend publishing these
   values.** `frontend/src/generated/ports.ts` will continue to carry
   `walkingTimeMin: 10` for all 119 ports regardless of the knowledge layer.
2. `officialSource.url` is **Timonelo's own domain**, presented as the port
   authority's official source under `trustLevel: "OFFICIAL"`. The authority
   name is manufactured by string interpolation.
3. `locode = p.get("un_locode", "ITGOA")` — any port missing a LOCODE
   **silently becomes Genoa**. Same pattern for `country` → `"Italy"` and
   `region` → `"Mediterranean"`.

This is the `fleet.ts` failure mode again: a generated frontend artifact
carrying values the knowledge layer does not support. It is arguably the more
serious of the two, because it bypasses the knowledge layer entirely and
therefore cannot be fixed by any amount of knowledge-layer governance.

**Not fixed in this patch.** The `PortData` TypeScript interface declares these
fields non-optional, so removing them is a frontend contract change requiring
a design decision about how the UI renders UNKNOWN. That is not a mechanical
edit.

### U-2 — Committed generated artifacts are already stale on `develop`

`data/cruise_intelligence_db.json` and `data/cruise_knowledge_graph.json` do
not match what `develop`'s own knowledge layer compiles to. Verified on a
pristine `HEAD` checkout with no modifications: regeneration produces a
~20,000-line diff, concentrated in `ship:msc-bellissima` and
`ship:msc-meraviglia` cabin attributes.

Regeneration is **deterministic** (byte-identical across repeated runs), so
this is genuine drift, not nondeterminism.

**Consequence for this patch:** `data/` is deliberately excluded. Regenerating
would mix ~20k lines of pre-existing unrelated drift into a port quarantine
diff, making both unreviewable. Regeneration must be a separate, deliberate
change once the drift is understood.

---

## 8. Remediation applied

See ADR-0006. Summary: `knowledge/ports/*/identity.json` × 119, synthetic
fields nulled or emptied, blanket source records removed. Entity identity
fields (`slug`, `name`, `un_locode`, `country`, `region`, `coordinates`,
`terminals[].name`) preserved unchanged and **not promoted** to trusted facts.

Enforcement: `tests/test_port_identity_quarantine.py`, 13 corpus-wide
invariants. These are distribution-based rather than per-file, because a
per-file assertion cannot distinguish researched data from template output.

---

## 9. Explicit UNKNOWNs and unresolved items

| # | Item | Status |
|---|---|---|
| K1 | Correct IANA timezone for all 119 ports | UNKNOWN — nulled, needs sourced per-port value |
| K2 | Correct emergency number for all 119 ports | UNKNOWN — nulled; **passenger-safety priority** |
| K3 | Walking time / centre distance / step-free access | UNKNOWN — no evidence exists for any port |
| K4 | Card acceptance rate | UNKNOWN — questionable as a knowledge-layer field at all |
| K5 | Real terminal and berth inventories | UNKNOWN for 113 ports; 6 rich ports have candidate data |
| K6 | Validity of all 119 UN/LOCODEs | UNVALIDATED — syntactically well-formed, never checked against UNECE |
| K7 | `USPEF` and `ITTRS` duplicate pairs | UNRESOLVED — ontology decision, needs its own ADR |
| K8 | Provenance model for the 6 rich ports | UNRESOLVED — separate audit required |
| K9 | Frontend bridge hardcoded values (U-1) | UNRESOLVED — frontend contract decision required |
| K10 | `data/` drift (U-2) | UNRESOLVED — cause not investigated |
| K11 | Generators still present and will re-emit templates if run | MITIGATED by tests, not removed |

---

## Appendix A — Machine-readable finding summary

```json
{
  "audit_date": "2026-08-24",
  "branch": "develop",
  "head_sha": "868325a",
  "corpus": {
    "port_directories": 119,
    "identity_files": 119,
    "rich_layout_ports": ["barcelona", "genoa", "marseille", "messina", "naples", "valletta"]
  },
  "template_constants": {
    "timezone": {"UTC": 119},
    "walking_time_min": {"10": 119},
    "card_acceptance_pct": {"98": 119},
    "step_free_access": {"true": 119},
    "terminals_per_port": {"1": 119},
    "distance_to_city_center_m": {"500": 101, "800": 18},
    "gangway_deck_default": {"5": 108, "2": 11},
    "sources_field": {"all": 119},
    "sources_source_id": {"src:official-port-authority": 119},
    "sources_trust_level": {"OFFICIAL": 119},
    "sources_retrieved_at": {"2026-08-16T12:00:00Z": 119}
  },
  "generators": [
    {"path": "tools/mass_populate_knowledge.py", "ports": 101, "distance_m": 500},
    {"path": "tools/populate_classes_and_ports.py", "ports": 18, "distance_m": 800}
  ],
  "duplicate_locodes": {
    "USPEF": ["fort-lauderdale", "port-everglades"],
    "ITTRS": ["trieste", "venice-trieste"]
  },
  "emergency_phone_distribution": {"112": 91, "911": 23, "999": 5},
  "currency_distribution": {
    "EUR": 55, "Local": 31, "USD": 17, "NOK": 8, "MXN": 4, "GBP": 2, "SGD": 1, "AUD": 1
  },
  "unexpected_findings": ["U-1 frontend bridge hardcodes values", "U-2 data/ drift on develop"]
}
```
