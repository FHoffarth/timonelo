"""Read-only checks for the Track B packages against the current Evidence Factory contract.

Run from the repo root: PYTHONPATH=src python -B reports/fleet-evidence-expansion/validate_packages.py
Probe batches below exist only in memory. inspect_batch works on its own temporary copy.
"""
import copy
import json
from pathlib import Path

from timonelo.factory.evidence_batch import BatchError, READER, SCOPE, inspect_batch

ROOT = Path(".").resolve()
HERE = ROOT / "reports/fleet-evidence-expansion"
SHIPS = ("msc-grandiosa", "msc-virtuosa", "msc-euribia", "msc-world-europa",
         "msc-world-america", "msc-meraviglia", "msc-seascape", "msc-seashore")
pilot = json.loads((ROOT / "reports/evidence-factory-automation/pilot-batch.json").read_text(encoding="utf8"))
CLAIM_KEYS = {"id", "name", "exact_claim", "value", "artifact_id", "artifact_sha256", "target_vessel", "page", "locator",
              "observed_text", "entity_id", "question_id", "statement_type", "source_version", "source_boxes", "scope"}
results = []


def check(label, ok):
    results.append(bool(ok))
    print("PASS" if ok else "FAIL", label)


def probe(slug, imo, artifact=None):
    claim = dict(copy.deepcopy(pilot["claims"][1]), id="PROBE-1", target_vessel=imo,
                 entity_id=f"venue:{slug.upper()}:probe", artifact_id=artifact or "UNREGISTERED-PROBE")
    batch = dict(copy.deepcopy(pilot), vessel_slug=slug, vessel_imo=imo, claims=[claim])
    try:
        return inspect_batch(ROOT, batch, {"decisions": []})["claims"][0]["reasons"]
    except BatchError as exc:
        return [str(exc)]


check("pilot claim keys equal the v1 claim shape", all(set(c) == CLAIM_KEYS for c in pilot["claims"]))
check(f"scope and reader constants unchanged ({SCOPE}; {READER})", SCOPE == "SOURCE_EDITION_VENUE_DECK_ONLY" and READER.startswith("Codex"))
packages = {s: json.loads((HERE / "review-packages" / f"{s}.json").read_text(encoding="utf8")) for s in SHIPS}
claims = [c for p in packages.values() for c in p["identity_candidates"]]
check("eight packages, three identity candidates each", len(claims) == 24)
check("every human decision field is unset", all(c[k] is None for c in claims for k in ("decision", "reviewer", "review_date", "decision_reason")))
check("no package records a human decision", all(p["human_decisions_recorded"] == 0 for p in packages.values()))
check("no deck-location candidate exists without primary bytes", all(p["deck_location_candidates"] == [] for p in packages.values()))
check("nothing is marked admission-ready", all(p["admission_state"] == "NOT_ADMISSION_READY" for p in packages.values()))
blob = "".join((HERE / "review-packages" / f"{s}.json").read_text(encoding="utf8") for s in SHIPS)
blob += (HERE / "source-inventory.json").read_text(encoding="utf8")
check("no artifact ID appears in packages or inventory", "ART-" not in blob)
locators = json.loads((HERE / "meraviglia-page-locators.json").read_text(encoding="utf8"))
check("locator map is declared not a batch and carries no artifact ID",
      locators["record_type"] == "PAGE_LOCATOR_MAP_NOT_A_BATCH" and locators["artifact_id"] is None)
index = json.loads((ROOT / "evidence/artifacts/index.json").read_text(encoding="utf8"))
check("held Meraviglia plan is still unregistered", locators["sha256"] not in json.dumps(index))

try:
    inspect_batch(ROOT, dict(copy.deepcopy(pilot), claims=[]), {"decisions": []})
    check("empty batch is refused", False)
except BatchError as exc:
    check(f"empty batch is refused ({exc}), so source-blocked ships get no batch file", "INVALID_BOUNDED_BATCH" in str(exc))
r = probe("msc-meraviglia", "IMO9760512")
check(f"Meraviglia with the candidate IMO is refused today: {r}", r == ["CANONICAL_VESSEL_IDENTITY_MISMATCH"])
r = probe("msc-meraviglia", "IMO9660463")
print("INFO Meraviglia with the seed IMO passes the identity gate and stops at:", r)
check("the seed-IMO route stops at the registry, not at identity", r and "IDENTITY" not in r[0])
for slug, imo in (("msc-grandiosa", "IMO9803613"), ("msc-world-europa", "IMO9837420")):
    r = probe(slug, imo)
    check(f"{slug} passes the identity gate and stops at the unregistered artifact: {r}", r and "IDENTITY" not in r[0])
print(f"{sum(results)}/{len(results)} checks passed")
raise SystemExit(0 if all(results) else 1)
