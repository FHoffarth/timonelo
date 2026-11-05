"""Read-only checks for the closure files.

Run from the repo root: PYTHONPATH=src python -B reports/fleet-evidence-expansion/closure/validate_closure.py
"""
import hashlib
import json
from pathlib import Path
import subprocess

import fitz

from timonelo.factory.evidence_batch import _document_reading

ROOT = Path(".").resolve()
HERE = ROOT / "reports/fleet-evidence-expansion/closure"
pilot = json.loads((ROOT / "reports/evidence-factory-automation/pilot-batch.json").read_text(encoding="utf8"))
batch = json.loads((HERE / "meraviglia-review-batch.json").read_text(encoding="utf8"))
closure = json.loads((HERE / "identity-closure.json").read_text(encoding="utf8"))
results = []


def check(label, ok):
    results.append(bool(ok))
    print("PASS" if ok else "FAIL", label)


claims = batch["claims"]
sha = claims[0]["artifact_sha256"]
path = ROOT / "evidence/raw/sha256" / sha[:2] / f"{sha}.pdf"
check("held plan bytes match the batch digest", hashlib.sha256(path.read_bytes()).hexdigest() == sha)
check("plan is still unregistered", sha not in (ROOT / "evidence/artifacts/index.json").read_text(encoding="utf8"))
check("batch has 1 to 8 claims with unique IDs", 1 <= len(claims) <= 8 and len({c["id"] for c in claims}) == len(claims))
check("claims use the exact v1 claim keys", all(set(c) == set(pilot["claims"][0]) for c in claims))
check("no artifact ID is set", all(c["artifact_id"] is None for c in claims))
check("every decision field is unset", all(v is None for d in batch["decisions"] for k, v in d.items() if k != "claim_id"))
check("decisions cover exactly the claims", [d["claim_id"] for d in batch["decisions"]] == [c["id"] for c in claims])
check("batch is declared review-only", batch["state"] == "REVIEW_ONLY_NOT_REGISTERED_NOT_ADMITTED")

for c in claims:
    try:
        _document_reading(path, c)
        read = True
    except Exception as exc:
        print("   ", c["id"], exc)
        read = False
    check(f"{c['id']} {c['name']}: factory box routine reproduces the observed text", read)

with fitz.open(path) as doc:
    for c in claims:
        words = doc[c["page"] - 1].get_text("words")
        heads = {int(words[i + 1][4]): (w[0] + words[i + 1][2]) / 2 for i, w in enumerate(words[:-1])
                 if w[4] == "DECK" and words[i + 1][4].isdigit() and w[1] > 750}
        placed = [min(heads, key=lambda d: abs(heads[d] - (b[0] + b[2]) / 2)) for b in c["source_boxes"]]
        check(f"{c['id']}: boxes sit under deck headings {sorted(set(placed))}", sorted(set(placed)) == c["value"])

ships = closure["ships"]
check("eight ships in the identity closure", len(ships) == 8)
check("ITU and USCG agree on all eight IMO numbers", all(s["itu_mars_row"]["vessel_id_number"] == s["uscg_psix_row"]["vin"] for s in ships.values()))
check("the three contradicted IMOs are exactly the repo mismatches",
      sorted(k for k, s in ships.items() if not s["repo_imo_matches"]) == ["msc-meraviglia", "msc-seascape", "msc-seashore"])
tracked = subprocess.run(["git", "diff", "--name-only", "cff78ebf52fd190b81adeaca9655157c0b447f3a"], capture_output=True, text=True).stdout.split()
check("nothing committed at cff78eb has changed", tracked == [])
print(f"{sum(results)}/{len(results)} checks passed")
raise SystemExit(0 if all(results) else 1)
