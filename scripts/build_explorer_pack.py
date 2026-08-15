#!/usr/bin/env python3
"""Migrate MSC Meraviglia engine output into a canonical Knowledge Pack.

This migrates the *data* into the canonical `knowledge-pack.json` schema defined
by `src/timonelo/knowledge_pack/` (the MSC Bellissima reference architecture) —
it does not invent a bespoke format. The Spatial Evidence Engine geometry model
(ship-graph / motion / noise) is kept under data/ships/<ship>/engine as the
development reference; this script is the deterministic bridge from that
reference into the canonical schema the Explorer renders.

Output:
  data/ships/msc-meraviglia/knowledge-pack.json      (canonical source of truth)
  frontend/public/packs/msc-meraviglia.pack.json     (asset the Explorer fetches)

Honesty notes (the source is a single third-party deck plan, trust ~T3):
  * Cabin category, view, balcony and dimensions are not in a deck plan and are
    left as pack-level limitations rather than fabricated.
  * Public-area `kind` is required by the schema but not stated by the source, so
    it is classified from the venue label by a transparent rule and every area
    carries a limitation saying so; ambiguous labels are flagged.
  * Motion and noise are deterministic derivations, carried as claims with their
    rule and a limitation that they are geometric exposure, not experience.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHIP = "msc-meraviglia"
ENGINE = ROOT / "data" / "ships" / SHIP / "engine"
CANONICAL_OUT = ROOT / "data" / "ships" / SHIP / "knowledge-pack.json"
ASSET_OUT = ROOT / "frontend" / "public" / "packs" / f"{SHIP}.pack.json"

SHIP_SLUG = "msc-meraviglia"
SOURCE_ID = "source:rejsy:msc-meraviglia-deckplan-19"
ACCESSED_AT = "2026-08-15"

# Transparent, deterministic venue-kind classifier. Every classified area also
# carries a limitation stating the kind is label-derived, not officially sourced.
KIND_RULES: list[tuple[str, str]] = [
    ("restaurant", "dining"),
    ("buffet", "dining"),
    ("ice cream", "dining"),
    ("marketplace", "dining"),
    ("theatre", "entertainment"),
    ("cinema", "entertainment"),
    ("amphitheatre", "entertainment"),
    ("broadway", "entertainment"),
    ("dancing", "entertainment"),
    ("tv games", "entertainment"),
    ("gym", "wellness"),
    ("technogym", "wellness"),
    ("solarium", "wellness"),
    ("spa", "wellness"),
    ("pool", "recreation"),
    ("sport", "recreation"),
    ("bowling", "recreation"),
    ("walking", "recreation"),
    ("arcade", "recreation"),
    ("games", "recreation"),
    ("simulator", "recreation"),
    ("xd", "recreation"),
    ("virtual", "recreation"),
    ("club", "recreation"),
    ("teen", "recreation"),
    ("junior", "recreation"),
    ("young", "recreation"),
    ("lego", "recreation"),
    ("sun deck", "promenade"),
    ("pool deck", "promenade"),
    ("promenade", "promenade"),
    ("bar", "lounge"),
    ("lounge", "lounge"),
    ("atrium", "lounge"),
    ("atmosphere", "lounge"),
    ("reception", "guest_service"),
    ("concierge", "guest_service"),
    ("excursion", "guest_service"),
    ("business", "guest_service"),
    ("yacht club", "guest_service"),
    ("shop", "retail"),
    ("market", "retail"),
]
FALLBACK_KIND = "guest_service"

KIND_LIMITATION = "Venue kind is classified from the deck-plan label, not an official venue directory."
AMBIGUOUS_LIMITATION = "The deck-plan label is ambiguous; the kind is a best-effort classification."


def load(name: str) -> object:
    return json.loads((ENGINE / name).read_text(encoding="utf-8"))


def deck_entity_id(number: int) -> str:
    return f"deck:{SHIP_SLUG}:{number:02d}"


def classify_kind(name: str) -> tuple[str, bool]:
    low = name.lower()
    for needle, kind in KIND_RULES:
        if needle in low:
            return kind, False
    return FALLBACK_KIND, True


def sentence(value: object) -> str:
    return str(value).replace("_", " ")


def main() -> None:
    graph = load("ship-graph.json")
    motion = {m["cabin"]: m for m in load("motion-layer.json")}
    noise = {n["cabin"]: n for n in load("noise-layer.json")}
    manifest = load("engine-manifest.json")
    src = graph["source"]
    val = manifest.get("validation", {}).get("ship_graph", {})

    ship_id = f"ship:{SHIP_SLUG}"

    sources = [
        {
            "source_id": SOURCE_ID,
            "title": "MSC Meraviglia deck plan (edition 19)",
            "publisher": "rejsy.pl",
            "url": src["url"],
            "accessed_at": ACCESSED_AT,
            "source_type": "third_party_deck_plan",
            "published_at": None,
            "limitations": [
                f"Retained deck-plan PDF, SHA-256 {src['sha256']}.",
                "A third-party aggregator plan, not an official MSC document; it can structure the ship but not verify it.",
            ],
        }
    ]

    ship = {
        "entity_id": ship_id,
        "name": "MSC Meraviglia",
        "operator_name": "MSC Cruises",
        "source_ids": [SOURCE_ID],
        "source_locator": "Deck plan, ship title block",
        "cabin_count": val.get("cabins"),
        "guest_capacity": None,
    }

    # Decks ordered bottom -> top for stable, unique ordinals.
    graph_decks = sorted(graph["decks"], key=lambda d: d["deck"])
    decks = []
    for ordinal, d in enumerate(graph_decks, start=1):
        decks.append(
            {
                "entity_id": deck_entity_id(d["deck"]),
                "ship_id": ship_id,
                "number": d["deck"],
                "name": d.get("name") or f"Deck {d['deck']}",
                "ordinal": ordinal,
                "source_ids": [SOURCE_ID],
                "source_locator": f"Deck plan, Deck {d['deck']}",
            }
        )

    # Cabins (no category: not stated by a deck plan -> category_id stays None).
    cabins = []
    for d in graph["decks"]:
        for cab in d.get("cabins", []):
            cabins.append(
                {
                    "entity_id": f"cabin:{SHIP_SLUG}:{cab['number']}",
                    "ship_id": ship_id,
                    "deck_id": deck_entity_id(d["deck"]),
                    "number": cab["number"],
                    "category_id": None,
                    "feature_codes": [],
                    "source_ids": [SOURCE_ID],
                    "source_locator": f"Deck plan, Deck {d['deck']}, cabin {cab['number']}",
                    "limitations": [],
                }
            )

    # Public areas: classify kind transparently; disclose it via limitations.
    public_areas = []
    ambiguous = 0
    for d in graph["decks"]:
        for area in d.get("public_areas", []):
            kind, is_ambiguous = classify_kind(area["name"])
            limitations = [KIND_LIMITATION]
            if is_ambiguous:
                limitations.append(AMBIGUOUS_LIMITATION)
                ambiguous += 1
            public_areas.append(
                {
                    "entity_id": f"public-area:{SHIP_SLUG}:{area['id']}",
                    "ship_id": ship_id,
                    "name": area["name"],
                    "kind": kind,
                    "deck_ids": [deck_entity_id(d["deck"])],
                    "source_ids": [SOURCE_ID],
                    "source_locator": f"Deck plan, Deck {d['deck']}, {area['name']}",
                    "limitations": limitations,
                }
            )

    # Relationships: authoritative deck-level above/below (deterministic derivation).
    relationships = []
    for a, b in graph["spatial_reference"]["adjacent_deck_pairs"]:
        lo, hi = (a, b) if a < b else (b, a)
        relationships.append(
            {
                "relationship_id": f"relationship:{SHIP_SLUG}:deck-{lo:02d}-below-deck-{hi:02d}",
                "source_entity_id": deck_entity_id(lo),
                "target_entity_id": deck_entity_id(hi),
                "kind": "below",
                "evidence_kind": "deterministic_derivation",
                "source_ids": [SOURCE_ID],
                "source_locator": "Deck plan, consecutive deck ordering",
                "derivation_rule": "deck-adjacent-pairs-v1",
                "limitation": "Structural ordering only; no passenger impact is implied.",
            }
        )
        relationships.append(
            {
                "relationship_id": f"relationship:{SHIP_SLUG}:deck-{hi:02d}-above-deck-{lo:02d}",
                "source_entity_id": deck_entity_id(hi),
                "target_entity_id": deck_entity_id(lo),
                "kind": "above",
                "evidence_kind": "deterministic_derivation",
                "source_ids": [SOURCE_ID],
                "source_locator": "Deck plan, consecutive deck ordering",
                "derivation_rule": "deck-adjacent-pairs-v1",
                "limitation": "Structural ordering only; no passenger impact is implied.",
            }
        )

    # Claims: ship-level counts + per-cabin motion and noise (deterministic).
    claims = []

    def ship_claim(pred: str, value, unit, statement, rule):
        claims.append(
            {
                "claim_id": f"claim:{SHIP_SLUG}:ship-{pred.replace('_', '-')}",
                "subject_entity_id": ship_id,
                "predicate": pred,
                "statement": statement,
                "value": value,
                "unit": unit,
                "evidence_kind": "deterministic_derivation",
                "source_ids": [SOURCE_ID],
                "source_locator": "Ship graph extraction",
                "derivation_rule": "ship-graph/vector-text-geometry-v2",
                "limitation": None,
            }
        )

    ship_claim("deck_count", val.get("decks"), "decks", f"{val.get('decks')} decks were extracted from the plan.", None)
    ship_claim("cabin_count", val.get("cabins"), "cabins", f"{val.get('cabins')} cabins were located on the plan.", None)
    ship_claim("public_area_count", val.get("public_areas"), "areas", f"{val.get('public_areas')} public areas were located.", None)
    ship_claim("elevator_count", val.get("elevators"), "elevators", f"{val.get('elevators')} elevators were located.", None)

    motion_rule = "motion/normalized-geometry-v1"
    noise_rule = "noise/structural-proximity-v2"
    motion_limitation = "Geometric exposure relative to the ship's centre; not a forecast of sea conditions or comfort."

    for cab in cabins:
        num = cab["number"]
        m = motion.get(num)
        if m:
            mc = m["motion"]
            ev = m.get("evidence", {})
            value = {
                "overall": mc.get("motion_exposure"),
                "pitch": mc.get("pitch_exposure"),
                "roll": mc.get("roll_exposure"),
                "longitudinal_position": mc.get("longitudinal_position"),
                "vertical_zone": mc.get("vertical_zone"),
                "distance_from_midship_m": round(ev["distance_from_midship_m"], 1)
                if ev.get("distance_from_midship_m") is not None
                else None,
            }
            claims.append(
                {
                    "claim_id": f"claim:{SHIP_SLUG}:{num}-motion-profile",
                    "subject_entity_id": cab["entity_id"],
                    "predicate": "motion_profile",
                    "statement": (
                        f"Cabin {num} sits {sentence(mc.get('longitudinal_position'))} and "
                        f"{sentence(mc.get('vertical_zone'))}, giving {sentence(mc.get('motion_exposure'))} "
                        f"overall motion exposure."
                    ),
                    "value": value,
                    "unit": None,
                    "evidence_kind": "deterministic_derivation",
                    "source_ids": [SOURCE_ID],
                    "source_locator": f"Motion layer, cabin {num}",
                    "derivation_rule": motion_rule,
                    "limitation": motion_limitation,
                }
            )
        n = noise.get(num)
        if n and n.get("noise_sources"):
            claims.append(
                {
                    "claim_id": f"claim:{SHIP_SLUG}:{num}-noise-exposure",
                    "subject_entity_id": cab["entity_id"],
                    "predicate": "noise_exposure",
                    "statement": (
                        f"Cabin {num} is structurally adjacent to "
                        f"{', '.join(sentence(s) for s in n['noise_sources'])}."
                    ),
                    "value": {"sources": n["noise_sources"], "confidence": n.get("confidence")},
                    "unit": None,
                    "evidence_kind": "deterministic_derivation",
                    "source_ids": [SOURCE_ID],
                    "source_locator": f"Noise layer, cabin {num}",
                    "derivation_rule": noise_rule,
                    "limitation": "Structural proximity only; describes exposure, not perceived loudness.",
                }
            )

    pack = {
        "schema_version": "1.0",
        "pack_id": f"knowledge-pack:{SHIP_SLUG}",
        "version": "0.1.0",
        "effective_date": ACCESSED_AT,
        "status": "structured",
        "limitations": [
            "Maturity is Structured: a single third-party deck-plan source, machine-extracted, not corroborated against an official MSC plan.",
            "Cabin category, view, balcony and dimensions are not present in a deck plan and remain unknown.",
            f"Public-area kinds are classified from deck-plan labels; {ambiguous} ambiguous labels are flagged on the affected areas.",
        ],
        "sources": sources,
        "ship": ship,
        "decks": decks,
        "cabin_categories": [],
        "cabins": cabins,
        "public_areas": public_areas,
        "relationships": relationships,
        "claims": claims,
    }

    validate(pack)

    CANONICAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    ASSET_OUT.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(pack, ensure_ascii=False, separators=(",", ":"))
    CANONICAL_OUT.write_text(blob, encoding="utf-8")
    ASSET_OUT.write_text(blob, encoding="utf-8")
    kb = ASSET_OUT.stat().st_size / 1024
    print(f"Migrated MSC Meraviglia -> canonical knowledge pack")
    print(f"  decks={len(decks)} cabins={len(cabins)} public_areas={len(public_areas)} "
          f"relationships={len(relationships)} claims={len(claims)}")
    print(f"  ambiguous public-area kinds flagged: {ambiguous}")
    print(f"  wrote {CANONICAL_OUT.relative_to(ROOT)} and {ASSET_OUT.relative_to(ROOT)} ({kb:.0f} KB)")


# --- lightweight conformance check mirroring the canonical validator ---
ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*(?::[a-z0-9]+(?:-[a-z0-9]+)*)+")
VERSION_RE = re.compile(r"\d+\.\d+\.\d+")


def validate(pack: dict) -> None:
    errors: list[str] = []
    assert pack["schema_version"] == "1.0"
    if not VERSION_RE.fullmatch(pack["version"]):
        errors.append("version must be MAJOR.MINOR.PATCH")

    ids = [pack["pack_id"], *(s["source_id"] for s in pack["sources"])]
    entities = {pack["ship"]["entity_id"]}
    for group in ("decks", "cabin_categories", "cabins", "public_areas"):
        for e in pack[group]:
            entities.add(e["entity_id"])
            ids.append(e["entity_id"])
    ids += [r["relationship_id"] for r in pack["relationships"]]
    ids += [c["claim_id"] for c in pack["claims"]]
    for i in ids:
        if not ID_RE.fullmatch(i):
            errors.append(f"bad identifier: {i}")
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        errors.append(f"duplicate ids: {sorted(dupes)[:5]}")

    deck_ids = {d["entity_id"] for d in pack["decks"]}
    deck_numbers = {d["number"] for d in pack["decks"]}
    if len({d["ordinal"] for d in pack["decks"]}) != len(pack["decks"]):
        errors.append("deck ordinals not unique")
    for cab in pack["cabins"]:
        if cab["deck_id"] not in deck_ids:
            errors.append(f"cabin {cab['number']} references missing deck")
        deck_num = next(d["number"] for d in pack["decks"] if d["entity_id"] == cab["deck_id"])
        if not cab["number"].startswith(str(deck_num)):
            errors.append(f"cabin {cab['number']} inconsistent with deck {deck_num}")
    for area in pack["public_areas"]:
        for did in area["deck_ids"]:
            if did not in deck_ids:
                errors.append(f"area {area['name']} references missing deck")
    for rel in pack["relationships"]:
        if rel["source_entity_id"] not in entities or rel["target_entity_id"] not in entities:
            errors.append(f"relationship {rel['relationship_id']} references missing entity")
        if rel["evidence_kind"] == "deterministic_derivation" and not rel.get("derivation_rule"):
            errors.append(f"relationship {rel['relationship_id']} missing derivation_rule")
    for claim in pack["claims"]:
        if claim["subject_entity_id"] not in entities:
            errors.append(f"claim {claim['claim_id']} references missing subject")
        if claim["evidence_kind"] == "deterministic_derivation" and not claim.get("derivation_rule"):
            errors.append(f"claim {claim['claim_id']} missing derivation_rule")
    _ = (deck_numbers,)
    if errors:
        raise SystemExit("CANONICAL VALIDATION FAILED:\n  " + "\n  ".join(errors[:20]))


if __name__ == "__main__":
    main()
