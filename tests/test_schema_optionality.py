"""P0-B Slice C: structural validity without invented semantic claims."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import jsonschema
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "knowledge" / "schema"
MERAVIGLIA_DIR = REPO_ROOT / "knowledge" / "ships" / "msc-meraviglia"

# Classification used by the focused schema inventory assertions below.
# Structural identity and evidence closure stay required; semantic enrichment does not.
MINIMAL_DOCUMENTS = {
    "bar.schema.json": ("bars", {"id": "BAR-1", "source": "held-source", "provenance": "page:1"}),
    "cabin.schema.json": ("cabin_categories", {"id": "CABIN-1", "source": "held-source", "provenance": "page:1"}),
    "deck.schema.json": ("decks", {"id": "DECK-1", "deck_number": 1, "source": "held-source", "provenance": "page:1"}),
    "entertainment.schema.json": ("entertainment_venues", {"id": "ENT-1", "source": "held-source", "provenance": "page:1"}),
    "lounge.schema.json": ("lounges", {"id": "LOUNGE-1", "source": "held-source", "provenance": "page:1"}),
    "pool.schema.json": ("pools_and_water_areas", {"id": "POOL-1", "source": "held-source", "provenance": "page:1"}),
    "restaurant.schema.json": ("restaurants", {"id": "REST-1", "source": "held-source", "provenance": "page:1"}),
    "sport.schema.json": ("sports_and_recreation", {"id": "SPORT-1", "source": "held-source", "provenance": "page:1"}),
    "venue.schema.json": ("public_areas", {"id": "VENUE-1", "source": "held-source", "provenance": "page:1"}),
}


def load_schema(name):
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def validate(name, document):
    schema = load_schema(name)
    jsonschema.validators.validator_for(schema)(schema).validate(document)


def document_for(schema_name, **claims):
    container, template = MINIMAL_DOCUMENTS[schema_name]
    item = deepcopy(template)
    item.update(claims)
    return {
        "vessel_id": "test-vessel",
        "provenance": {"source_artifact": "held-source"},
        container: [item],
    }


@pytest.mark.parametrize("schema_name,container_and_item", MINIMAL_DOCUMENTS.items())
def test_minimal_structural_object_without_optional_semantics_is_valid(
    schema_name, container_and_item
):
    container, item = container_and_item
    validate(
        schema_name,
        {
            "vessel_id": "test-vessel",
            "provenance": {"source_artifact": "held-source"},
            container: [item],
        },
    )


def test_minimal_spa_and_muster_documents_are_valid_without_semantic_placeholders():
    validate(
        "spa.schema.json",
        {
            "vessel_id": "test-vessel",
            "provenance": {"source_artifact": "held-source"},
            "spa_and_wellness": {
                "id": "SPA-1",
                "source": "held-source",
                "provenance": "page:1",
            },
        },
    )
    validate(
        "muster.schema.json",
        {
            "vessel_id": "test-vessel",
            "provenance": {"source_artifact": "held-source"},
            "emergency_and_muster_protocol": {},
        },
    )


def minimal_cabin(**claims):
    item = {"id": "CABIN-1", "source": "held-source", "provenance": "page:1"}
    item.update(claims)
    return {
        "vessel_id": "test-vessel",
        "provenance": {"source_artifact": "held-source"},
        "cabin_categories": [item],
    }


@pytest.mark.parametrize(
    "claims",
    [
        {"category": 3},
        {"description": ""},
        {"category": None},
    ],
)
def test_optional_cabin_claim_present_but_malformed_is_rejected(claims):
    with pytest.raises(jsonschema.ValidationError):
        validate("cabin.schema.json", minimal_cabin(**claims))


@pytest.mark.parametrize(
    "field",
    ["features", "perks", "design_partners", "tags"],
)
def test_confirmed_empty_cabin_arrays_are_valid(field):
    validate("cabin.schema.json", minimal_cabin(**{field: []}))


def test_confirmed_empty_standard_amenities_are_valid():
    document = minimal_cabin()
    document["summary"] = {"standard_amenities": []}
    validate("cabin.schema.json", document)


@pytest.mark.parametrize(
    "schema_name",
    [
        "bar.schema.json",
        "cabin.schema.json",
        "deck.schema.json",
        "restaurant.schema.json",
    ],
)
@pytest.mark.parametrize("field", ["id", "source", "provenance"])
@pytest.mark.parametrize("empty_value", ["", "   "])
def test_empty_or_whitespace_identity_and_evidence_are_rejected(
    schema_name, field, empty_value
):
    document = document_for(schema_name)
    container, _ = MINIMAL_DOCUMENTS[schema_name]
    document[container][0][field] = empty_value
    with pytest.raises(jsonschema.ValidationError):
        validate(schema_name, document)


@pytest.mark.parametrize(
    "schema_name,document,item_path",
    [
        (
            "spa.schema.json",
            {
                "vessel_id": "test-vessel",
                "provenance": {"source_artifact": "held-source"},
                "spa_and_wellness": {
                    "id": "SPA-1",
                    "source": "held-source",
                    "provenance": "page:1",
                    "sub_venues": [
                        {"id": "", "source": "held-source", "provenance": "page:2"}
                    ],
                },
            },
            "sub_venues",
        ),
        (
            "sport.schema.json",
            document_for(
                "sport.schema.json",
                sub_attractions=[
                    {"id": "", "source": "held-source", "provenance": "page:2"}
                ],
            ),
            "sub_attractions",
        ),
        (
            "muster.schema.json",
            {
                "vessel_id": "test-vessel",
                "provenance": {"source_artifact": "held-source"},
                "emergency_and_muster_protocol": {
                    "physical_muster_stations": [
                        {"id": "", "source": "held-source", "provenance": "page:2"}
                    ]
                },
            },
            "physical_muster_stations",
        ),
    ],
)
def test_nested_item_empty_identity_is_rejected(schema_name, document, item_path):
    del item_path  # The parameter documents which nested collection is under test.
    with pytest.raises(jsonschema.ValidationError):
        validate(schema_name, document)


@pytest.mark.parametrize(
    "schema_name,claim",
    [
        ("bar.schema.json", {"name": ""}),
        ("restaurant.schema.json", {"description": "   "}),
        ("lounge.schema.json", {"category": ""}),
        ("entertainment.schema.json", {"position": "   "}),
        ("pool.schema.json", {"access": ""}),
        ("venue.schema.json", {"description": ""}),
    ],
)
def test_present_empty_optional_semantic_string_is_rejected(schema_name, claim):
    with pytest.raises(jsonschema.ValidationError):
        validate(schema_name, document_for(schema_name, **claim))


@pytest.mark.parametrize(
    "schema_name",
    [
        "bar.schema.json",
        "cabin.schema.json",
        "deck.schema.json",
        "entertainment.schema.json",
        "lounge.schema.json",
        "pool.schema.json",
        "restaurant.schema.json",
        "sport.schema.json",
        "venue.schema.json",
    ],
)
def test_confirmed_empty_tags_are_valid(schema_name):
    validate(schema_name, document_for(schema_name, tags=[]))


def test_confirmed_empty_features_are_valid_across_domains():
    validate("cabin.schema.json", minimal_cabin(features=[]))
    validate("entertainment.schema.json", document_for("entertainment.schema.json", features=[]))
    validate("pool.schema.json", document_for("pool.schema.json", features=[]))


def test_array_with_empty_string_element_is_rejected():
    with pytest.raises(jsonschema.ValidationError):
        validate("cabin.schema.json", minimal_cabin(features=[""]))
    with pytest.raises(jsonschema.ValidationError):
        validate("entertainment.schema.json", document_for("entertainment.schema.json", features=["   "]))


@pytest.mark.parametrize("schema_name", ["bar.schema.json", "cabin.schema.json", "venue.schema.json"])
def test_asserted_deck_association_array_must_not_be_empty(schema_name):
    with pytest.raises(jsonschema.ValidationError):
        validate(schema_name, document_for(schema_name, deck=[]))


def test_asserted_muster_procedure_must_contain_a_step():
    document = {
        "vessel_id": "test-vessel",
        "provenance": {"source_artifact": "held-source"},
        "emergency_and_muster_protocol": {"procedure": []},
    }
    with pytest.raises(jsonschema.ValidationError):
        validate("muster.schema.json", document)


def test_optional_cabin_summary_is_omitted_instead_of_defaulted():
    document = minimal_cabin()
    assert "summary" not in document
    validate("cabin.schema.json", document)


def test_claim_evidence_closure_remains_required():
    document = minimal_cabin(description="Evidence-backed cabin description")
    del document["cabin_categories"][0]["source"]
    with pytest.raises(jsonschema.ValidationError):
        validate("cabin.schema.json", document)


def test_modified_schemas_keep_only_structural_item_requirements():
    for schema_name, (container, item) in MINIMAL_DOCUMENTS.items():
        required = load_schema(schema_name)["properties"][container]["items"]["required"]
        assert required == list(item)

    spa_required = load_schema("spa.schema.json")["properties"]["spa_and_wellness"]["required"]
    assert spa_required == ["id", "source", "provenance"]


def test_schema_validation_does_not_mutate_meraviglia_data():
    paths = sorted(MERAVIGLIA_DIR.glob("*.json"))
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    for path in paths:
        json.loads(path.read_text(encoding="utf-8"))
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    assert after == before


def test_existing_meraviglia_knowledge_documents_remain_schema_valid():
    mapping = {
        "technical.json": "ship.schema.json",
        "decks.json": "deck.schema.json",
        "public_areas.json": "venue.schema.json",
        "restaurants.json": "restaurant.schema.json",
        "bars.json": "bar.schema.json",
        "lounges.json": "lounge.schema.json",
        "pools.json": "pool.schema.json",
        "spa.json": "spa.schema.json",
        "sports.json": "sport.schema.json",
        "entertainment.json": "entertainment.schema.json",
        "muster.json": "muster.schema.json",
        "cabins.json": "cabin.schema.json",
    }
    for document_name, schema_name in mapping.items():
        path = MERAVIGLIA_DIR / document_name
        if path.exists():
            validate(schema_name, json.loads(path.read_text(encoding="utf-8")))


def test_modified_item_schemas_share_nonempty_identity_and_evidence_constraints():
    scopes = []
    for schema_name, (container, _) in MINIMAL_DOCUMENTS.items():
        scopes.append(load_schema(schema_name)["properties"][container]["items"])

    spa = load_schema("spa.schema.json")["properties"]["spa_and_wellness"]
    scopes.extend([spa, spa["properties"]["sub_venues"]["items"]])
    sport = load_schema("sport.schema.json")["properties"]["sports_and_recreation"]["items"]
    scopes.append(sport["properties"]["sub_attractions"]["items"])
    muster = load_schema("muster.schema.json")["properties"]["emergency_and_muster_protocol"]
    scopes.append(muster["properties"]["physical_muster_stations"]["items"])

    for scope in scopes:
        for field in ("id", "source", "provenance"):
            constraint = scope["properties"][field]
            assert constraint["minLength"] == 1
            assert constraint["pattern"] == r"\S"


def test_no_confidence_or_new_trust_field_is_introduced():
    forbidden = {"trust", "trust_level", "verified", "confidence"}
    for schema_name in MINIMAL_DOCUMENTS:
        schema = load_schema(schema_name)
        required_text = json.dumps(schema.get("required", []))
        assert not forbidden.intersection(json.loads(required_text))

        document = document_for(schema_name, confidence=1.0)
        with pytest.raises(jsonschema.ValidationError):
            validate(schema_name, document)
