"""Trust-boundary invariants for the frontend bridge (audit U-1).

The bridge exists to carry canonical knowledge to the passenger surface. The
failure it exhibited was not carrying anything: for every field the knowledge
layer could not supply, it substituted a plausible literal and shipped that
instead -- `walkingTimeMin: 10`, `cardAcceptancePct: 98`, a `stepFreeAccess`
assertion for all 119 ports, and an `officialSource` naming Timonelo's own
domain as the port authority under `trustLevel: "OFFICIAL"`.

That is worse than a gap. A missing value invites checking; a confident wrong
value suppresses it. And because the substitution happened downstream of the
knowledge layer, no amount of governance applied to `knowledge/ports/` could
reach it -- quarantining the identity layer left the passenger surface
unchanged.

The rule these tests enforce: **the bridge may propagate provenance, never
originate it.** Checks run against both the generator source and the emitted
artifact, because a leak can be reintroduced in either.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
BRIDGE = REPO_ROOT / "tools" / "generate_frontend_bridge.py"
PORTS_TS = REPO_ROOT / "frontend" / "src" / "generated" / "ports.ts"

#: Timonelo is not a port authority. Emitting its own domain as the source URL
#: for a port fact is self-attestation with the shape of evidence.
SELF_ATTESTATION_HOSTS = ("timonelo.com", "www.timonelo.com")

#: Genoa's code, previously the `.get("un_locode", ...)` fallback. Any port
#: without a code silently became Genoa.
LOCODE_FALLBACK = "ITGOA"


def _bridge_code() -> str:
    """Generator source with comments stripped.

    The comments document the removed literals by name, so matching against
    the raw file would flag the explanation as the offence.
    """
    return "\n".join(
        line
        for line in BRIDGE.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("#")
    )


@pytest.fixture(scope="module")
def emitted_ports() -> list[dict]:
    """The `PORTS_REGISTRY` array parsed out of the generated TypeScript."""
    text = PORTS_TS.read_text(encoding="utf-8")
    marker = "PORTS_REGISTRY: PortData[] = "
    start = text.index(marker) + len(marker)
    end = text.rindex("];") + 1
    records = json.loads(text[start:end])
    assert records, "generated ports.ts contains no port records"
    return records


# --------------------------------------------------------------------------
# Generator source
# --------------------------------------------------------------------------

def test_bridge_does_not_self_attest_as_authority():
    code = _bridge_code()
    for host in SELF_ATTESTATION_HOSTS:
        assert host not in code, (
            f"bridge emits {host!r} as a source URL. Timonelo is not a port "
            "authority; provenance is propagated from the knowledge layer or "
            "omitted (audit U-1)."
        )


def test_bridge_does_not_originate_trust_levels():
    """`OFFICIAL` may be read from upstream, never written as a literal."""
    code = _bridge_code()
    offenders = [
        line.strip()
        for line in code.splitlines()
        if re.search(r"""['"]OFFICIAL['"]""", line)
        and "trust_level" not in line  # reading the upstream key is fine
    ]
    assert not offenders, (
        f"bridge writes a literal trust level: {offenders[:3]}. Trust is a "
        "property of evidence, not a presentation default (audit U-1)."
    )


def test_bridge_has_no_locode_fallback():
    code = _bridge_code()
    assert LOCODE_FALLBACK not in code, (
        f"bridge still references {LOCODE_FALLBACK!r}. A missing UN/LOCODE "
        "must stay missing rather than relabelling the port as Genoa."
    )


@pytest.mark.parametrize(
    "literal",
    ['"walkingTimeMin": 10', '"cardAcceptancePct": 98',
     '"distanceToCenterM": 500', '"gangwayDeckDefault": 5',
     '"stepFreeAccess": True', '"berths": ["Berth 1"'],
)
def test_bridge_emits_no_hardcoded_passenger_values(literal):
    assert literal not in _bridge_code(), (
        f"bridge hardcodes {literal!r}. Passenger-facing values come from the "
        "knowledge layer or are null (audit U-1)."
    )


# --------------------------------------------------------------------------
# Emitted artifact
# --------------------------------------------------------------------------

def test_emitted_ports_contain_no_self_attestation(emitted_ports):
    offenders = [
        rec["slug"]
        for rec in emitted_ports
        if (rec.get("officialSource") or {}).get("url")
        and any(h in rec["officialSource"]["url"] for h in SELF_ATTESTATION_HOSTS)
    ]
    assert not offenders, (
        f"{len(offenders)} emitted port(s) cite Timonelo as the official "
        f"source: {offenders[:5]} (audit U-1)."
    )


def test_emitted_provenance_is_field_scoped(emitted_ports):
    """Any surviving source record must name a field and a source id.

    `field: "all"` was the blanket attestation quarantined by ADR-0006 D2. It
    must not reappear by way of the bridge.
    """
    offenders = []
    for rec in emitted_ports:
        src = rec.get("officialSource")
        if src is None:
            continue
        if not src.get("sourceId") or src.get("field") in (None, "", "all"):
            offenders.append((rec["slug"], src))
    assert not offenders, (
        f"{len(offenders)} emitted source record(s) lack field-scoped "
        f"provenance: {offenders[:3]} (ADR-0006 D2)."
    )


def test_emitted_locode_is_never_a_shared_fallback(emitted_ports):
    """No two ports may share a UN/LOCODE via a default.

    Genoa legitimately holds ITGOA. The defect was every codeless port also
    holding it, so the check is on duplication rather than on the value.
    """
    seen: dict[str, list[str]] = {}
    for rec in emitted_ports:
        code = rec.get("unLocode")
        if code:
            seen.setdefault(code, []).append(rec["slug"])
    shared = {
        code: slugs
        for code, slugs in seen.items()
        if len(slugs) > 1 and code == LOCODE_FALLBACK
    }
    assert not shared, (
        f"the fallback LOCODE is shared across ports: {shared}. A port "
        "without a code must emit null (audit U-1)."
    )


@pytest.mark.parametrize(
    "field", ["walkingTimeMin", "cardAcceptancePct", "distanceToCenterM",
              "gangwayDeckDefault", "stepFreeAccess"],
)
def test_emitted_passenger_values_are_not_uniform_constants(emitted_ports, field):
    """A single non-null value across every port is a substituted default.

    Stated as uniformity rather than as a banned value, so a genuinely sourced
    future value is unaffected: the corpus only fails when every port agrees
    and nothing sourced it.
    """
    if len(emitted_ports) < 20:
        pytest.skip("too few ports for a distribution check")
    values = {
        rec[field] for rec in emitted_ports if rec.get(field) is not None
    }
    assert len(values) != 1, (
        f"every emitted port carries {field}={values.pop()!r}. The bridge is "
        "substituting a default for a value the knowledge layer does not have "
        "(audit U-1)."
    )


def test_null_survives_generation(emitted_ports):
    """Quarantined fields reach the frontend as null, not as a stand-in.

    The point of the quarantine was that UNKNOWN is publishable. If the bridge
    converted null into anything renderable, the quarantine bought nothing.
    """
    quarantined = ["walkingTimeMin", "cardAcceptancePct", "gangwayDeckDefault",
                   "stepFreeAccess", "emergencyPhone", "currency"]
    for field in quarantined:
        assert all(field in rec for rec in emitted_ports), (
            f"{field} missing from some emitted records; the key must persist "
            "so the frontend can distinguish unknown from unmodelled"
        )
    nulls = {
        field: sum(1 for rec in emitted_ports if rec.get(field) is None)
        for field in quarantined
    }
    assert all(count > 0 for count in nulls.values()), (
        f"no nulls survived generation for some quarantined field: {nulls}. "
        "The bridge is filling gaps it should propagate (audit U-1)."
    )


def test_emitted_artifact_is_valid_and_complete(emitted_ports):
    assert len(emitted_ports) >= 100, (
        f"only {len(emitted_ports)} ports emitted; expected the full corpus"
    )
    for rec in emitted_ports:
        assert rec.get("slug"), f"emitted record without a slug: {rec}"
