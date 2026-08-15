# Timonelo Knowledge Factory (v1.0 Architecture)
### Automated Industrial Pipeline for Cruise Knowledge Pack Production

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               TIMONELO KNOWLEDGE FACTORY PIPELINE                                │
│                                                                                                  │
│   [ STAGE 01 ] ──► [ STAGE 02 ] ──► [ STAGE 03 ] ──► [ STAGE 04 ]                                │
│   Evidence Intake   Normalization   Archetype Match   Ship Delta Detection                       │
│                                                              │                                   │
│                                                              ▼                                   │
│   [ STAGE 08 ] ◄── [ STAGE 07 ] ◄── [ STAGE 06 ] ◄── [ STAGE 05 ]                                │
│   Publication       Experience Val. Spatial Valid.    Knowledge Pack Gen                         │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Executive Overview

The **Knowledge Factory** is the core backend compilation engine of Timonelo. It transforms raw maritime evidence (shipyard CAD drawings, General Arrangement PDFs, on-site survey photographs, and cabin manifest tables) into **sealed, immutable, self-validating Canonical Knowledge Packs**.

The Factory is designed around three architectural pillars:
1. **Deterministic Compilation**: Given the same inputs and rule version, the factory produces bit-for-bit identical Knowledge Packs across any execution runtime.
2. **Archetypal Leverage**: Instead of hand-authoring 100% of a ship's geometry, sister ships inherit $\ge 80\%$ of baseline structures from Master Archetypes, focusing human and automated auditing solely on structural deltas.
3. **Multi-Gate Quality Enforcement**: A Knowledge Pack cannot advance to publication without passing independent geometric, topological, acoustic, and experience validation gates.

---

## 2. Directory Structure

```text
factory/
├── README.md             # Master architecture overview, pipeline topology & quickstart
├── PIPELINE_STAGES.md    # Detailed specifications for Stages 01 through 08
├── LIFECYCLE.md          # Knowledge Pack state machine (Draft → Published → Archived)
├── CONTRACTS.md          # Strict JSON data contracts for stage inputs and outputs
└── INTERFACES.md         # Python Protocols & structural typing definitions
```

---

## 3. The 8-Stage Production Sequence

```
┌─────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ STAGE                   │ CORE RESPONSIBILITY                                                    │
├─────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 01. Evidence Intake     │ Ingests raw source assets (GA PDFs, manifests, survey photos).         │
│ 02. Normalization       │ Converts raw sources into normalized Cartesian $[X,Y,Z]$ coordinate space.│
│ 03. Archetype Matching  │ Identifies class sister ship base and binds master geometry layers.    │
│ 04. Delta Detection     │ Isolates physical refits, cabin additions, and venue modifications.    │
│ 05. Pack Generation     │ Compiles normalized entities, claims, and limits into canonical JSON.  │
│ 06. Spatial Validation  │ Audits polygon non-intersection, door-to-corridor graph connectivity.  │
│ 07. Experience Valid.   │ Verifies overhead noise sandwiches, balcony sightlines, socket counts. │
│ 08. Publication         │ Digitally signs, hashes, and deploys sealed packs to edge CDN & cache. │
└─────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Operational Invariants

- **No Business Logic in Client**: The client Explorer runtime is a pure renderer; all graph derivations, distance calculations, and obstruction flags are compiled ahead of time by the Factory.
- **Fail-Closed Pipelines**: Any validation failure immediately halts pipeline execution and emits an explicit error manifest detailing the exact coordinate, cabin number, and rule violation.
- **Permanent Evidence Lineage**: Every claim in the generated Knowledge Pack references the exact `evidence_id` and source locator from Stage 01.

---

## 5. Architectural Cross-References

- Technical Architecture: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- Epistemic Canon: [docs/CANON.md](../docs/CANON.md)
- Engineering Principles: [docs/ENGINEERING_PRINCIPLES.md](../docs/ENGINEERING_PRINCIPLES.md)
- Trust Framework: [docs/TRUST_FRAMEWORK.md](../docs/TRUST_FRAMEWORK.md)
