"""Evidence guards for the MSC Meraviglia semantic cleanup."""

import hashlib
import json
from pathlib import Path

import jsonschema

from scripts.reingest_msc_meraviglia_official_deckplan import run_ingestion


REPO_ROOT = Path(__file__).resolve().parents[1]
SHIP_DIR = REPO_ROOT / "knowledge" / "ships" / "msc-meraviglia"
SCHEMA_DIR = REPO_ROOT / "knowledge" / "schema"
INVENTORY_PATH = SHIP_DIR / "semantic_cleanup_inventory.jsonl"
ARTIFACT_SHA256 = "77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9"

CANONICAL_FILES = {
    "bars.json": ("bar.schema.json", "bars"),
    "cabins.json": ("cabin.schema.json", "cabin_categories"),
    "decks.json": ("deck.schema.json", "decks"),
    "entertainment.json": ("entertainment.schema.json", "entertainment_venues"),
    "lounges.json": ("lounge.schema.json", "lounges"),
    "pools.json": ("pool.schema.json", "pools_and_water_areas"),
    "public_areas.json": ("venue.schema.json", "public_areas"),
    "restaurants.json": ("restaurant.schema.json", "restaurants"),
    "sports.json": ("sport.schema.json", "sports_and_recreation"),
}

REGENERATED_FILES = (*CANONICAL_FILES, "spa.json", "technical.json")

EXPECTED_DECK_NAMES = {
    4: "Deck 4 (Kos)",
    5: "Deck 5 (Colosseo)",
    6: "Deck 6 (Petra)",
    7: "Deck 7 (Taj Mahal)",
    8: "Deck 8 (Machu Picchu)",
    9: "Deck 9 (Alhambra)",
    10: "Deck 10 (Hagia Sophia)",
    11: "Deck 11 (Acropolis)",
    12: "Deck 12 (Grand Canyon)",
    13: "Deck 13 (Kilimangiaro)",
    14: "Deck 14 (Angkor Wat)",
    15: "Deck 15 (Tour Eiffel)",
    16: "Deck 16 (Iguazu)",
    18: "Deck 18 (Pyramids)",
    19: "Deck 19 (Babylon)",
}

EXPECTED_CABIN_CODES = {
    "YC3", "YJD", "YC1", "YIN", "SXJ", "SLJ", "BA", "BL3", "BL2",
    "BL1", "BR3", "BR2", "BR1", "BP", "BS", "OL2", "OR1", "OM2",
    "OO", "IR2", "IR1", "IS",
}


def load_json(name):
    return json.loads((SHIP_DIR / name).read_text(encoding="utf-8"))


def load_inventory():
    return [json.loads(line) for line in INVENTORY_PATH.read_text(encoding="utf-8").splitlines()]


def canonical_items():
    for filename, (_, container) in CANONICAL_FILES.items():
        for item in load_json(filename)[container]:
            yield filename, item
    yield "spa.json", load_json("spa.json")["spa_and_wellness"]


def walk(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def test_cleanup_inventory_accounts_for_every_removed_claim():
    records = load_inventory()
    metadata, removed = records[0], records[1:]
    assert metadata["record_type"] == "metadata"
    assert metadata["accepted_artifact_sha256"] == ARTIFACT_SHA256
    assert metadata["removed_claims_count"] == 318 == len(removed)
    assert all(record["record_type"] == "removed_claim" for record in removed)
    assert {record["classification"] for record in removed} == {
        "UNSUPPORTED", "PLACEHOLDER-LIKE"
    }
    assert all(record["previous_value"] is not None for record in removed)
    assert all(record["evidence_reason"] for record in removed)


def test_unsupported_placeholder_fields_are_absent_from_canonical_items():
    generally_removed = {"category", "description", "tags"}
    for filename, item in canonical_items():
        assert generally_removed.isdisjoint(item), (filename, item["id"])
        assert "passenger_accessible" not in item
        assert "dining_model" not in item


def test_no_legacy_summary_placeholders_or_generic_amenities_remain():
    cabins = load_json("cabins.json")
    summary = cabins["summary"]
    assert summary == {"total_staterooms": 2214, "distinct_categories_count": 22}
    assert "balcony_percentage" not in summary
    assert "standard_amenities" not in summary

    technical = load_json("technical.json")
    serialized = json.dumps(technical)
    assert "passenger_accessible_decks" not in serialized
    assert "75.0" not in serialized


def test_connecting_cabin_absence_is_not_encoded_as_false():
    cabins = load_json("cabins.json")
    for value in walk(cabins):
        if isinstance(value, dict):
            assert not any("connect" in key.lower() for key in value)
        elif isinstance(value, str):
            assert "connecting cabin" not in value.lower()


def test_unknown_semantic_arrays_are_omitted_not_encoded_as_empty():
    for filename, item in canonical_items():
        for field, value in item.items():
            if isinstance(value, list):
                assert value, (filename, item["id"], field)


def test_retained_items_keep_identity_and_evidence_closure():
    for filename, item in canonical_items():
        assert item["id"].strip(), filename
        assert item["source"].strip(), (filename, item["id"])
        assert item["provenance"].strip(), (filename, item["id"])
        assert ARTIFACT_SHA256 == load_json(filename)["provenance"]["sha256"]


def test_supported_deck_names_and_deck_17_absence_remain_unchanged():
    decks = load_json("decks.json")
    actual = {deck["deck_number"]: deck["name"] for deck in decks["decks"]}
    assert actual == EXPECTED_DECK_NAMES
    assert 17 not in actual
    assert "reason" not in decks["notes"].lower()


def test_supported_cabin_codes_and_scoped_decks_remain():
    cabins = load_json("cabins.json")["cabin_categories"]
    assert {item["id"].removeprefix("CAT-") for item in cabins} == EXPECTED_CABIN_CODES
    assert all(item["name"].endswith(f"({item['id'].removeprefix('CAT-')})") for item in cabins)
    assert all(item["deck"] for item in cabins)


def test_historical_ocean_cay_and_top_sail_corrections_remain():
    restaurants = {item["id"]: item for item in load_json("restaurants.json")["restaurants"]}
    lounges = {item["id"]: item for item in load_json("lounges.json")["lounges"]}
    assert restaurants["REST-OCEAN-CAY"]["deck"] == 6
    assert lounges["LOUNGE-TOP-SAIL"]["deck"] == 16


def test_cleaned_documents_validate_against_current_schemas():
    for filename, (schema_name, _) in CANONICAL_FILES.items():
        document = load_json(filename)
        schema = json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
        jsonschema.validators.validator_for(schema)(schema).validate(document)

    spa = load_json("spa.json")
    schema = json.loads((SCHEMA_DIR / "spa.schema.json").read_text(encoding="utf-8"))
    jsonschema.validators.validator_for(schema)(schema).validate(spa)

    technical = load_json("technical.json")
    schema = json.loads((SCHEMA_DIR / "ship.schema.json").read_text(encoding="utf-8"))
    jsonschema.validators.validator_for(schema)(schema).validate(technical)


def test_cleanup_is_subtractive_at_item_level():
    expected_keys = {
        "decks.json": {"id", "name", "deck_number", "source", "provenance"},
        "cabins.json": {"id", "name", "deck", "source", "provenance"},
    }
    venue_keys = {"id", "name", "deck", "source", "provenance"}
    for filename, item in canonical_items():
        assert set(item) == expected_keys.get(filename, venue_keys), (filename, item["id"])


def test_cleanup_validation_does_not_modify_any_ship_data():
    ship_root = REPO_ROOT / "knowledge" / "ships"
    paths = sorted(ship_root.glob("**/*.json"))
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    for path in paths:
        json.loads(path.read_text(encoding="utf-8"))
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    assert after == before


def test_reingestion_source_definitions_do_not_model_removed_defaults():
    script = (
        REPO_ROOT / "scripts" / "reingest_msc_meraviglia_official_deckplan.py"
    ).read_text(encoding="utf-8")
    for key in (
        "category",
        "cat",
        "desc",
        "description",
        "tags",
        "dining_model",
        "passenger_accessible",
    ):
        assert f'"{key}":' not in script
    assert "d_cat" not in script
    assert "d_desc" not in script


def test_isolated_reingestion_reproduces_cleaned_canonical_payloads(tmp_path):
    output_dir = tmp_path / "knowledge" / "ships" / "msc-meraviglia"
    reports_dir = tmp_path / "knowledge" / "reports"
    tracked_paths = sorted((REPO_ROOT / "knowledge").glob("**/*"))
    tracked_files = [path for path in tracked_paths if path.is_file()]
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in tracked_files}

    result = run_ingestion(str(output_dir), str(reports_dir))

    first_generation = {}
    for filename in REGENERATED_FILES:
        expected = load_json(filename)
        actual = json.loads((output_dir / filename).read_text(encoding="utf-8"))
        assert actual == expected, filename
        first_generation[filename] = actual

    manifest = json.loads(
        (output_dir / "extraction_manifest.json").read_text(encoding="utf-8")
    )
    corrections = manifest["historical_corrections"]
    assert result["historical_corrections_count"] == len(corrections) == 6
    assert all(
        correction["reference_integrity"] == "VALIDATED" for correction in corrections
    )
    # Keyed by entity: both venue-deck corrections answer the same registered
    # question Q-0016, so question_id alone is no longer unique.
    corrections_by_entity = {
        correction["entity_id"]: correction for correction in corrections
    }
    assert corrections_by_entity["msc-meraviglia:venue:REST-OCEAN-CAY"][
        "evidence_event_ids"
    ] == ["EVT-MER-REST-OCEAN-CAY-DECK"]
    assert corrections_by_entity["msc-meraviglia:venue:LOUNGE-TOP-SAIL"][
        "evidence_event_ids"
    ] == ["EVT-MER-LOUNGE-TOP-SAIL-DECK"]
    assert result["conflict_detection_executed"] is True

    run_ingestion(str(output_dir), str(reports_dir))
    second_generation = {
        filename: json.loads((output_dir / filename).read_text(encoding="utf-8"))
        for filename in REGENERATED_FILES
    }
    assert second_generation == first_generation

    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in tracked_files}
    assert after == before


def test_isolated_regenerated_payloads_validate_against_current_schemas(tmp_path):
    output_dir = tmp_path / "knowledge" / "ships" / "msc-meraviglia"
    run_ingestion(str(output_dir), str(tmp_path / "reports"))

    for filename, (schema_name, _) in CANONICAL_FILES.items():
        document = json.loads((output_dir / filename).read_text(encoding="utf-8"))
        schema = json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
        jsonschema.validators.validator_for(schema)(schema).validate(document)

    for filename, schema_name in (
        ("spa.json", "spa.schema.json"),
        ("technical.json", "ship.schema.json"),
    ):
        document = json.loads((output_dir / filename).read_text(encoding="utf-8"))
        schema = json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
        jsonschema.validators.validator_for(schema)(schema).validate(document)
