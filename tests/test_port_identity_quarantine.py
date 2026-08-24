"""Corpus-wide invariants for the port identity layer (ADR-0006).

These guard against one specific failure, already realised once on `develop`:
a bulk generator wrote template constants into every `knowledge/ports/*/
identity.json` and attested them with a single blanket source record
(`field: "all"`, `source_id: "src:official-port-authority"`,
`trust_level: "OFFICIAL"`). Nothing in the repository objected, because every
file was individually well-formed and individually plausible. The defect was
only visible in the DISTRIBUTION across the corpus.

So these tests are deliberately distribution-based rather than per-file. A
per-file assertion cannot distinguish "10 minutes is the researched walking
time for this port" from "10 minutes is what the template emits"; a
corpus-wide cardinality check can. The rule enforced is: a passenger-facing
numeric may not take one identical value across the entire corpus unless a
field-scoped source attests it.

`None` is the fail-closed state and is always permitted. The point of the
quarantine is that UNKNOWN is publishable and synthetic precision is not.
"""

from __future__ import annotations

import collections
import json
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PORTS_DIR = REPO_ROOT / "knowledge" / "ports"

#: Blanket attestation emitted by the bulk generators. `field: "all"` cannot
#: establish provenance for unrelated facts, and this source_id names a
#: category of authority rather than any retrievable document.
BANNED_SOURCE_ID = "src:official-port-authority"

#: Passenger-facing numerics that were template constants. Each may be None,
#: or may carry a real value attested by a source scoped to that field.
GUARDED_TERMINAL_FIELDS = (
    "walking_time_min",
    "distance_to_city_center_m",
    "gangway_deck_default",
)
GUARDED_LOGISTICS_FIELDS = (
    "card_acceptance_pct",
    "currency",
    "emergency_phone",
)

#: Below this many ports the "one distinct value" signal is meaningless.
MIN_CORPUS_FOR_DISTRIBUTION_CHECK = 20


def _identity_files() -> list[pathlib.Path]:
    return sorted(PORTS_DIR.glob("*/identity.json"))


def _load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def corpus() -> list[tuple[str, dict]]:
    files = _identity_files()
    assert files, "no port identity files found; check PORTS_DIR"
    return [(p.parent.name, _load(p)) for p in files]


def _sourced_fields(doc: dict) -> set[str]:
    """Field names carrying a field-scoped source record.

    `field: "all"` deliberately contributes nothing: a source covering
    everything attests nothing in particular.
    """
    out: set[str] = set()
    for src in doc.get("sources", []):
        field = src.get("field")
        if isinstance(field, str) and field != "all":
            out.add(field)
        elif isinstance(field, list):
            out.update(f for f in field if f != "all")
    return out


def test_json_is_wellformed_and_parses(corpus):
    for slug, doc in corpus:
        assert isinstance(doc, dict), f"{slug}: identity.json is not an object"
        assert doc.get("slug"), f"{slug}: missing slug"


def test_no_blanket_official_attestation(corpus):
    """`field: "all"` + generic authority id may not attest anything."""
    offenders = [
        slug
        for slug, doc in corpus
        for src in doc.get("sources", [])
        if src.get("field") == "all" and src.get("source_id") == BANNED_SOURCE_ID
    ]
    assert not offenders, (
        f"{len(offenders)} port(s) re-introduced the blanket attestation "
        f"(field='all', source_id='{BANNED_SOURCE_ID}'): {offenders[:10]}. "
        "A source covering every field attests none of them; see ADR-0006."
    )


def test_no_source_claims_field_all(corpus):
    """Any `field: "all"` record is rejected, whatever its source_id.

    Renaming the source_id would otherwise slip the same laundering pattern
    past the previous test.
    """
    offenders = [
        (slug, src.get("source_id"))
        for slug, doc in corpus
        for src in doc.get("sources", [])
        if src.get("field") == "all"
    ]
    assert not offenders, (
        f"field='all' provenance found on {len(offenders)} record(s): "
        f"{offenders[:10]}. Passenger-facing facts require field-scoped "
        "provenance; add an explicit schema exception if one is ever justified."
    )


def test_timezone_is_not_uniformly_hardcoded(corpus):
    """A single timezone across a global corpus is a generator artefact.

    All-aboard time is computed from this field, so a wrong value strands
    passengers. UTC for 119 ports spanning Reykjavik to Sydney is not data.
    """
    if len(corpus) < MIN_CORPUS_FOR_DISTRIBUTION_CHECK:
        pytest.skip("corpus too small for a distribution check")
    values = collections.Counter(
        doc.get("timezone") for _, doc in corpus if doc.get("timezone") is not None
    )
    assert len(values) != 1, (
        f"every port with a timezone declares {list(values)[0]!r}. "
        "This is template output, not observation. Null it or source it "
        "per port (ADR-0006)."
    )


@pytest.mark.parametrize("field", GUARDED_TERMINAL_FIELDS)
def test_terminal_numeric_is_not_a_corpus_wide_constant(corpus, field):
    if len(corpus) < MIN_CORPUS_FOR_DISTRIBUTION_CHECK:
        pytest.skip("corpus too small for a distribution check")
    values = collections.Counter()
    for slug, doc in corpus:
        if field in _sourced_fields(doc):
            continue  # individually attested; exempt from the constant check
        for term in doc.get("terminals", []):
            if term.get(field) is not None:
                values[term[field]] += 1
    assert len(values) != 1, (
        f"unsourced {field!r} takes the single value {list(values)[0]!r} across "
        f"{sum(values.values())} terminals. Synthetic precision must be null "
        "until field-scoped evidence exists (ADR-0006)."
    )


@pytest.mark.parametrize("field", GUARDED_LOGISTICS_FIELDS)
def test_logistics_value_is_not_a_corpus_wide_constant(corpus, field):
    if len(corpus) < MIN_CORPUS_FOR_DISTRIBUTION_CHECK:
        pytest.skip("corpus too small for a distribution check")
    values = collections.Counter(
        doc["logistics"][field]
        for slug, doc in corpus
        if field not in _sourced_fields(doc)
        and doc.get("logistics", {}).get(field) is not None
    )
    assert len(values) != 1, (
        f"unsourced logistics.{field} takes the single value "
        f"{list(values)[0]!r} across {sum(values.values())} ports (ADR-0006)."
    )


def test_negative_intelligence_is_not_template_derived(corpus):
    """Guidance repeated verbatim across ports is boilerplate, not intelligence.

    Compared on the invariant portion of the string, since the generators
    interpolated the port name into an otherwise fixed sentence.
    """
    if len(corpus) < MIN_CORPUS_FOR_DISTRIBUTION_CHECK:
        pytest.skip("corpus too small for a distribution check")
    counts = collections.Counter(
        entry.split(" in ")[0].strip().rstrip(".")
        for _, doc in corpus
        for entry in doc.get("negative_intelligence", [])
        if isinstance(entry, str)
    )
    repeated = {k: v for k, v in counts.items() if v > 5}
    assert not repeated, (
        f"negative_intelligence entries repeat across many ports: {repeated}. "
        "Port-specific guidance cannot be identical corpus-wide (ADR-0006)."
    )


def test_unsourced_identity_publishes_no_facts(corpus):
    """Fail-closed: no sources means no passenger-facing values.

    Identity data absent evidence may still carry the entity's name and
    place. It may not carry claims a traveller could act on.
    """
    offenders = []
    for slug, doc in corpus:
        if _sourced_fields(doc):
            continue
        asserted = [
            f for f in GUARDED_LOGISTICS_FIELDS
            if doc.get("logistics", {}).get(f) is not None
        ] + [
            f for f in GUARDED_TERMINAL_FIELDS
            for term in doc.get("terminals", [])
            if term.get(f) is not None
        ]
        if asserted:
            offenders.append((slug, sorted(set(asserted))))
    assert not offenders, (
        f"{len(offenders)} port(s) publish passenger-facing values with no "
        f"field-scoped source: {offenders[:10]} (ADR-0006)."
    )


def test_compiler_tolerates_unknown_values():
    """The compiler must load a fully-quarantined corpus without raising.

    Restoring a synthetic value to satisfy a consumer is the failure this
    guards against; the consumer handles UNKNOWN instead.
    """
    from timonelo.database.compiler import KnowledgeDBCompiler

    compiler = KnowledgeDBCompiler(root_dir=str(REPO_ROOT))
    compiler.compile()
    assert compiler.ports, "compiler produced no ports"
    for slug, port in compiler.ports.items():
        assert "slug" in port, f"{slug}: compiled port lost its slug"
