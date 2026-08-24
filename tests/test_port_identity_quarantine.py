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


def test_accessibility_claims_are_not_a_corpus_wide_constant(corpus):
    """`step_free_access` may not be uniformly asserted without evidence.

    Separated from the numeric checks because the harm differs in kind. A wrong
    walking time costs a passenger ten minutes; a wrong step-free claim sends a
    wheelchair user to a gangway they cannot board. The generators asserted
    `true` for all 119 ports without a single observation.

    Diversity is not the standard here — a corpus where every *sourced* port
    happens to be step-free is legitimate. The standard is that an unsourced
    uniform assertion is template output.
    """
    if len(corpus) < MIN_CORPUS_FOR_DISTRIBUTION_CHECK:
        pytest.skip("corpus too small for a distribution check")
    values = collections.Counter()
    for slug, doc in corpus:
        if "step_free_access" in _sourced_fields(doc):
            continue
        for term in doc.get("terminals", []):
            if term.get("step_free_access") is not None:
                values[term["step_free_access"]] += 1
    assert len(values) != 1, (
        f"unsourced step_free_access is uniformly {list(values)[0]!r} across "
        f"{sum(values.values())} terminals. Accessibility claims fail closed: "
        "null until observed per terminal (ADR-0006 D5)."
    )


def test_accessibility_never_claimed_without_evidence(corpus):
    """A positive step-free claim requires field-scoped provenance.

    Stricter than the distribution check and deliberately so. `false` and
    `null` need no source — neither sends anyone to an unusable gangway — but
    `true` is the claim a passenger acts on, so it carries the burden.
    """
    offenders = [
        slug
        for slug, doc in corpus
        if "step_free_access" not in _sourced_fields(doc)
        for term in doc.get("terminals", [])
        if term.get("step_free_access") is True
    ]
    assert not offenders, (
        f"{len(offenders)} terminal(s) claim step_free_access=true with no "
        f"field-scoped source: {offenders[:10]} (ADR-0006 D5)."
    )


def test_berth_lists_are_not_template_derived(corpus):
    """Berth names may not be derived from the port slug.

    Both generators built berths by interpolation — `f"{slug.title()} Berth 1"`
    and `f"{slug.title()} Pier 1"`. The tell is that the berth name contains
    the slug, which a real berth designation ("Ponte dei Mille", "Berths
    91-93") generally does not. Checked structurally rather than against the
    two known templates, so renaming the suffix does not evade it.
    """
    offenders = []
    for slug, doc in corpus:
        if "berths" in _sourced_fields(doc):
            continue
        slug_words = slug.replace("-", " ").lower()
        for term in doc.get("terminals", []):
            for berth in term.get("berths") or []:
                if isinstance(berth, str) and slug_words in berth.lower():
                    offenders.append((slug, berth))
    assert not offenders, (
        f"{len(offenders)} berth name(s) are interpolated from the port slug: "
        f"{offenders[:8]}. Berth designations come from the port authority, "
        "not from string formatting (ADR-0006)."
    )


def test_berth_counts_are_not_a_corpus_wide_constant(corpus):
    """Unsourced ports may not all declare the same number of berths.

    Guards the shape as well as the names: a generator emitting
    `["Berth 1", "Berth 2"]` for every port defeats the name check above while
    reproducing the same false uniformity.
    """
    if len(corpus) < MIN_CORPUS_FOR_DISTRIBUTION_CHECK:
        pytest.skip("corpus too small for a distribution check")
    counts = collections.Counter(
        len(term.get("berths") or [])
        for slug, doc in corpus
        if "berths" not in _sourced_fields(doc)
        for term in doc.get("terminals", [])
        if term.get("berths")
    )
    assert len(counts) != 1, (
        f"every unsourced terminal declares exactly {list(counts)[0]} berth(s) "
        f"across {sum(counts.values())} terminals. Real ports differ "
        "(ADR-0006)."
    )


def test_terminal_structure_is_not_a_corpus_wide_constant(corpus):
    """Unsourced ports may not all declare an identical terminal shape.

    The original corpus gave all 119 ports exactly one terminal — including
    Barcelona, whose own `port.json` lists eight — so the terminal *array* is
    generator output, not merely the fields inside it.

    KNOWN RESIDUE: quarantine did not remove that. Every port still declares
    one name-only terminal, because emptying the array would drop 119
    `Terminal` nodes and their `LOCATED_ON` edges from the knowledge graph.
    Terminal cardinality is logged as an open item (audit K5) and needs a
    referential-integrity decision, not a bulk edit.

    So this test guards the forward direction, which is what it is for: a
    future generator must not re-populate terminals with uniform *content*.
    The name-only shape is the accepted quarantined baseline; any additional
    key appearing uniformly across the unsourced corpus is re-population.
    """
    if len(corpus) < MIN_CORPUS_FOR_DISTRIBUTION_CHECK:
        pytest.skip("corpus too small for a distribution check")
    unsourced = [
        (slug, doc) for slug, doc in corpus if not _sourced_fields(doc)
    ]
    if len(unsourced) < MIN_CORPUS_FOR_DISTRIBUTION_CHECK:
        pytest.skip("too few unsourced ports to judge uniformity")

    #: Entity identity, retained by ADR-0006 and not a passenger-facing claim.
    BASELINE_KEYS = {"name"}

    shapes = collections.Counter(
        (
            len(doc.get("terminals", [])),
            tuple(
                sorted(
                    k
                    for term in doc.get("terminals", [])
                    for k, v in term.items()
                    if v is not None and v != [] and k not in BASELINE_KEYS
                )
            ),
        )
        for _, doc in unsourced
    )
    populated = {shape: n for shape, n in shapes.items() if shape[1]}
    assert len(populated) != 1, (
        f"all {sum(populated.values())} unsourced ports share one populated "
        f"terminal shape {list(populated)[0]!r}. A uniform terminal structure "
        "across a global corpus is generator output (ADR-0006)."
    )


def test_synthetic_generators_cannot_repopulate_ports():
    """The two proven generators must fail closed on the port path.

    Asserts behaviour, not text: the module is imported and its refusal
    invoked. A generator that silently succeeded would restore every
    quarantined value, so the guard is load-bearing and is tested as such.
    """
    import importlib

    for module_name in ("tools.mass_populate_knowledge",
                        "tools.populate_classes_and_ports"):
        module = importlib.import_module(module_name)
        assert hasattr(module, "refuse_port_population"), (
            f"{module_name} lost its fail-closed port guard"
        )
        with pytest.raises(RuntimeError, match="Refusing to populate"):
            module.refuse_port_population(1)


@pytest.mark.parametrize(
    "literal",
    ["walking_time_min", "card_acceptance_pct", "distance_to_city_center_m",
     "gangway_deck_default", "step_free_access", "negative_intelligence",
     BANNED_SOURCE_ID],
)
def test_generator_source_contains_no_port_templates(literal):
    """Belt and braces: the templates are gone, not merely unreachable.

    The runtime guard above could be deleted by someone who reads it as
    obstruction. Removing the literals means that even then, the generators
    cannot reproduce the quarantined fields — the code to do it no longer
    exists. Comments are stripped before matching so the explanatory notes
    naming these fields do not trip the check.
    """
    for name in ("mass_populate_knowledge.py", "populate_classes_and_ports.py"):
        path = REPO_ROOT / "tools" / name
        code = "\n".join(
            line for line in path.read_text(encoding="utf-8").splitlines()
            if not line.lstrip().startswith("#")
        )
        assert literal not in code, (
            f"{name} still contains the port template literal {literal!r} "
            "outside a comment (ADR-0006)."
        )


def test_compiler_tolerates_unknown_values(tmp_path):
    """The compiler must load a fully-quarantined corpus without raising.

    Restoring a synthetic value to satisfy a consumer is the failure this
    guards against; the consumer handles UNKNOWN instead.

    `compile()` writes `cruise_intelligence_db.json` and
    `cruise_knowledge_graph.json` into `<root_dir>/data` unconditionally, and
    the compiler exposes no output-path option. So the test runs against a
    temporary root whose `knowledge` is a symlink to the real corpus: the real
    data is exercised, and the writes land in `tmp_path`. A test that mutated
    tracked files and then restored them would still be a test that rewrites
    the working tree, and would mask genuine drift.
    """
    from timonelo.database.compiler import KnowledgeDBCompiler

    real_data = REPO_ROOT / "data"
    before = {
        p.name: p.read_bytes() for p in sorted(real_data.glob("*.json"))
    }

    (tmp_path / "knowledge").symlink_to(REPO_ROOT / "knowledge")
    compiler = KnowledgeDBCompiler(root_dir=str(tmp_path))
    compiler.compile()

    assert compiler.ports, "compiler produced no ports"
    for slug, port in compiler.ports.items():
        assert "slug" in port, f"{slug}: compiled port lost its slug"

    # The writes must have gone to the temporary root, not the repository.
    assert (tmp_path / "data" / "cruise_intelligence_db.json").exists(), (
        "compile() did not write to the temporary root; the redirection "
        "assumption in this test no longer holds"
    )
    after = {p.name: p.read_bytes() for p in sorted(real_data.glob("*.json"))}
    assert before == after, (
        "compile() mutated tracked files under data/ despite the temporary "
        f"root: {sorted(k for k in before if before[k] != after.get(k))}"
    )
