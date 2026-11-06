"""Read-only checks for the ship-map research package.

Run from the repo root: PYTHONPATH=src python -B reports/fleet-evidence-expansion/ship-maps/validate_ship_maps.py <maps folder>
The maps folder holds the acquired PDFs, which are not committed. Probe batches exist only in memory.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).parent))
from extract_ship_maps import expand, read_map
from timonelo.factory.evidence_batch import _document_reading, inspect_batch

ROOT = Path(".").resolve()
HERE = ROOT / "reports/fleet-evidence-expansion/ship-maps"
MAPS = Path(sys.argv[1])
BASELINE = "ffce96b62c803506114235305d610628d73f27c6"
pilot = json.loads((ROOT / "reports/evidence-factory-automation/pilot-batch.json").read_text(encoding="utf8"))
register = json.loads((HERE / "source-register.json").read_text(encoding="utf8"))["documents"]
results = []


def check(label, ok):
    results.append(bool(ok))
    print("PASS" if ok else "FAIL", label)


art2 = ROOT / "evidence/raw/sha256/4f/4f7f1aba2fe1adfe4a2539362cfc39ad51f9f606c9765245245c7a0eece0c603.pdf"
known = sorted(sorted(s["value"]) for s in json.loads((ROOT / "evidence/statements/statements.json").read_text(encoding="utf8")).values()
               if s.get("artifact_id") == "ART-0002")
bellissima = read_map(art2)
check("regression: extractor reads 115 rows and 87 labels from the audited Bellissima map",
      (len(bellissima["rows"]), len(bellissima["venues"])) == (115, 87))
check("regression: deck values equal the 87 audited ART-0002 statements", sorted(sorted(set(expand(v["tokens"][0]))) for v in bellissima["venues"]) == known)

check("seven documents registered", len(register) == 7)
for entry in register:
    slug = entry["slug"]
    code = entry["url"].rsplit("/", 1)[1][:2]
    path = MAPS / code / f"{code}_en-gb.pdf"
    package = json.loads((HERE / "observations" / f"{slug}.json").read_text(encoding="utf8"))
    claims, observations = package["first_review_batch"], package["observations"]
    check(f"{slug}: bytes match the recorded digest", hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"] and path.stat().st_size == entry["bytes"])
    check(f"{slug}: official MSC host and exact cover title", entry["url"].startswith("https://service.msccruises.com/") and entry["cover_title"] == f"{entry['vessel']} SHIP MAP")
    check(f"{slug}: version stays unknown, not invented", entry["version"] is None and all(c["source_version"] is None for c in claims))
    check(f"{slug}: 1 to 8 first-batch claims with v1 keys", 1 <= len(claims) <= 8 and all(set(c) == set(pilot["claims"][0]) for c in claims))
    check(f"{slug}: no artifact ID and no decision", all(c["artifact_id"] is None for c in claims) and
          all(v is None for d in package["decisions"] for k, v in d.items() if k != "claim_id"))
    readable = True
    for claim in claims:
        try:
            _document_reading(path, claim)
        except Exception as exc:
            print("   ", claim["id"], exc)
            readable = False
    check(f"{slug}: factory box routine reproduces every first-batch reading", readable)
    fresh = {v["key"]: v for v in read_map(path)["venues"]}
    tokens_ok = True
    for claim in claims:
        low, high = expand(claim["observed_text"].split()[-1])
        tokens_ok &= claim["value"][0] == low and claim["value"][-1] == high
    check(f"{slug}: structured values equal the printed tokens", tokens_ok)
    check(f"{slug}: rejected readings carry no value", all(o["structured_deck_value"] is None for o in observations if o["status"] == "CONFLICT"))
    check(f"{slug}: first batch uses agreed readings only", {c["entity_id"] for c in claims} <=
          {o["entity_id"] for o in observations if o["status"] == "AGREED"})
    check(f"{slug}: observation count equals labels read", len(observations) == len(fresh) == entry["distinct_labels"])
    blocked = package["vessel"]["identity_state"].startswith("BLOCKED")
    check(f"{slug}: classification follows identity state", (entry["eligibility"]["classification"] == "NEEDS REVIEW") == blocked)

blob = "".join(p.read_text(encoding="utf8") for p in (HERE / "observations").glob("*.json"))
check("no artifact ID value appears in observations", '"artifact_id": null' in blob and "ART-" not in blob)
comparison = json.loads((HERE / "meraviglia-source-comparison.json").read_text(encoding="utf8"))
check("Meraviglia map is comparison only", comparison["ship_map"]["state"] == "NOT_A_SOURCE_FOR_MER_DK_CLAIMS" and len(comparison["comparison"]) == 8)
check("Meraviglia plan is still unregistered", comparison["held_plan"]["sha256"] not in (ROOT / "evidence/artifacts/index.json").read_text(encoding="utf8"))

claim = dict(copy.deepcopy(pilot["claims"][1]), id="PROBE-MAP", artifact_id="ART-0002",
             artifact_sha256=art2.stem, source_version=None, entity_id="venue:MSC-BELLISSIMA:probe")
reasons = inspect_batch(ROOT, dict(copy.deepcopy(pilot), claims=[claim]), {"decisions": []})["claims"][0]["reasons"]
print("INFO a ship map with no version in the current factory:", reasons)
check("current factory refuses an unversioned map claim", "SOURCE_VERSION_MISMATCH" in reasons)

changed = subprocess.run(["git", "diff", "--name-only", BASELINE], capture_output=True, text=True).stdout.split()
check("no file from the baseline commit has changed", [p for p in changed if "/ship-maps/" not in p] == [])
print(f"{sum(results)}/{len(results)} checks passed")
raise SystemExit(0 if all(results) else 1)
