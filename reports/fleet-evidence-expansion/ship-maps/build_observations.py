"""Build the source register and per-ship observations from held ship-map bytes.

argv[1] = folder holding <code>/<code>_en-gb.pdf and <code>/headers.txt. Run from the repo root.
Writes only into this report folder. No artifact ID or decision is ever produced.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

import fitz

sys.path.insert(0, str(Path(__file__).parent))
from extract_ship_maps import expand, read_map

HERE = Path(__file__).parent
MAPS = Path(sys.argv[1])
ROOT = Path(".").resolve()
RETRIEVED = "2026-11-05"
BASE = "https://service.msccruises.com/images/shipmap/pdfs/"
LIMITS = ["No edition or version is printed; PDF metadata dates are production data, not an edition.",
          "The map prints no IMO; vessel attribution comes from its title.",
          "Deck assignment only; no position, distance, adjacency or current-operations claim.",
          "Cite-only; source artwork is not redistributable."]
SHIPS = {
    "gr": ("msc-grandiosa", "MSC GRANDIOSA", "9803613"), "vi": ("msc-virtuosa", "MSC VIRTUOSA", "9803625"),
    "er": ("msc-euribia", "MSC EURIBIA", "9901544"), "eu": ("msc-world-europa", "MSC WORLD EUROPA", "9837420"),
    "am": ("msc-world-america", "MSC WORLD AMERICA", "9837432"), "sc": ("msc-seascape", "MSC SEASCAPE", "9843807"),
    "sh": ("msc-seashore", "MSC SEASHORE", "9843792"),
}


# Possible language variants of a neighbouring label: kept as observations, held out of first batches.
HELD_OUT = {"AURORA BOREALE", "ESAGONO RESTAURANT"}


def slugify(label):
    text = re.sub(r"\s*\(.*?\)\*?", "", label).replace("&", " and ").replace("’", "").replace("'", "")
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def header(lines, name):
    return next((l.split(":", 1)[1].strip() for l in lines if l.lower().startswith(name + ":")), None)


def row_reading(page, row):
    box = [row["box"][0], row["box"][1] + 2.6, row["box"][2], row["box"][3] - 2.6]
    return [round(v, 2) for v in box], page.get_textbox(fitz.Rect(box) + (-2, -2, 2, 2)).strip()


def rank(venue):
    label = venue["key"]
    section = venue["rows"][0]["section"].lower()
    if "THEAT" in label:
        return 0
    if "BUFFET" in label:
        return 1
    if "CASINO" in label:
        return 2
    return 3 if "restaurant" in section else 4


def status_of(venue):
    if not venue["issues"]:
        return "AGREED"
    if venue["issues"] == ["NOT_IN_DECK_INDEX"]:
        return "TABLE_ONLY"
    return "CONFLICT"


def decks_of(venue):
    if venue["value"]:
        return venue["value"]
    if status_of(venue) == "TABLE_ONLY" and len(venue["tokens"]) == 1:
        low, high = expand(venue["tokens"][0])
        return [low] if low == high else None
    return None


def build(code):
    slug, title, verified = SHIPS[code]
    path = MAPS / code / f"{code}_en-gb.pdf"
    url, raw = BASE + path.name, path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    head = (MAPS / code / "headers.txt").read_text(encoding="utf8").splitlines()
    data = read_map(path)
    stored = json.loads((ROOT / f"knowledge/ships/{slug}/identity.json").read_text(encoding="utf8"))["imo_number"]["value"]
    identity_ok = stored == verified
    state = "CANONICAL_MATCHES_VERIFIED" if identity_ok else f"BLOCKED_STORED_IMO_{stored}_AWAITS_OWNER_DECISION"
    ship = {"slug": slug, "name": title, "verified_imo": "IMO" + verified, "stored_imo": "IMO" + stored, "identity_state": state}
    source = {"sha256": sha, "url": url, "retrieved_on": RETRIEVED, "title": data["cover"], "version": None, "version_status": "UNKNOWN_NOT_PRINTED"}
    counts = {"AGREED": 0, "TABLE_ONLY": 0, "CONFLICT": 0}
    observations = []
    with fitz.open(path) as doc:
        for venue in data["venues"]:
            status = status_of(venue)
            counts[status] += 1
            row = venue["rows"][0]
            box, observed = row_reading(doc[row["page"] - 1], row)
            decks = decks_of(venue)
            label = row["label"]
            where = f"Page {row['page']}, table {row['section']!r}, row {label!r}, printed deck {row['token']!r}"
            observations.append({
                "vessel": ship, "source": source, "exact_label": label, "other_printed_labels": [l for l in venue["labels"] if l != label],
                "structured_deck_value": decks, "printed_tokens": venue["tokens"], "status": status,
                "generated_claim": (f"The official MSC ship map for {title} (SHA-256 {sha[:12]}, version unknown) prints {label} on deck(s) "
                                    f"{', '.join(map(str, decks))}.") if decks else None,
                "locator": {"page": row["page"], "table": row["section"], "row_box": box, "text": where, "observed_text": observed},
                "all_table_rows": [{"page": r["page"], "table": r["section"], "token": r["token"]} for r in venue["rows"]],
                "deck_index": {"page": data["index_pages"][0], "decks_listed": venue["index_decks"]},
                "source_version_status": "UNKNOWN_NOT_PRINTED", "provenance_limitations": LIMITS, "unresolved_conflicts": venue["issues"],
                "entity_id": f"venue:{slug.upper()}:{slugify(label)}", "_rank": rank(venue),
            })
    ready = sorted((o for o in observations if o["status"] == "AGREED" and "WHIRLPOOL" not in o["exact_label"].upper() and o["exact_label"] not in HELD_OUT), key=lambda o: (o["_rank"], o["exact_label"]))[:8]
    claims = [{"id": f"{code.upper()}-MAP-{i:02d}", "name": o["exact_label"], "exact_claim": o["generated_claim"], "value": o["structured_deck_value"], "artifact_id": None,
               "artifact_sha256": sha, "target_vessel": "IMO" + verified, "page": o["locator"]["page"], "locator": o["locator"]["text"], "observed_text": o["locator"]["observed_text"],
               "entity_id": o["entity_id"], "question_id": "Q-0016", "statement_type": "deck.venue_present", "source_version": None, "source_boxes": [o["locator"]["row_box"]],
               "scope": "SOURCE_EDITION_VENUE_DECK_ONLY"} for i, o in enumerate(ready, 1)]
    for o in observations:
        del o["_rank"]
    text = data["text"].upper()
    foreign = [n for n in ("SEASCAPE", "SEASHORE", "SEASIDE", "SEAVIEW", "BELLISSIMA", "MERAVIGLIA", "GRANDIOSA", "VIRTUOSA", "EURIBIA") if n not in title and re.search(r"\b" + n + r"\b", text)]
    identity_gap = None if identity_ok else f"Stored IMO {stored} differs from verified {verified}; owner decision pending."
    if not identity_ok:
        verdict, why = "NEEDS REVIEW", identity_gap
    elif len(claims) < 8:
        verdict, why = "NEEDS REVIEW", "Fewer than eight internally agreed observations."
    else:
        verdict, why = "ELIGIBLE CANDIDATE", "Official domain, inspected content, exact title match, canonical IMO verified, version recorded as unknown."
    register = {
        "slug": slug, "vessel": title, "url": url, "retrieved_on": RETRIEVED, "http_status": 200, "bytes": len(raw), "sha256": sha,
        "content_type": header(head, "content-type"), "server_last_modified": header(head, "last-modified"), "etag": header(head, "etag"),
        "document_type": "official_ship_map", "cover_title": data["cover"], "pages": data["pages"], "language_from_filename": "en-GB",
        "version": None, "version_status": "UNKNOWN_NOT_PRINTED", "pdf_metadata": data["metadata"], "foreign_ship_names_in_text": foreign,
        "deck_index_page": data["index_pages"], "decks_with_index_headings": sorted({e[0] for e in data["index_entries"]}),
        "table_rows_read": len(data["rows"]), "distinct_labels": len(data["venues"]), "counts": counts, "index_only_labels": data["index_only"],
        "eligibility": {"classification": verdict, "reason": why, "source_authenticity": "PASS", "vessel_attribution": "PASS_BY_TITLE" if identity_ok else "BLOCKED_CANONICAL_IMO",
                        "edition_and_freshness": "UNKNOWN_RECORDED", "claim_support": f"{counts['AGREED']} agreed, {counts['TABLE_ONLY']} single reading, {counts['CONFLICT']} rejected",
                        "governance": "CITE_ONLY_NO_ARTIFACT_NO_DECISIONS"},
    }
    package = {"schema": "timonelo.ship-map-observations.v0", "state": "RESEARCH_ONLY_NOT_REGISTERED_NOT_ADMITTED", "target_contract": "timonelo.evidence-batch.v1",
               "vessel": ship, "source": source, "classification": verdict, "first_review_batch": claims,
               "decisions": [{"claim_id": c["id"], "decision": None, "reviewer": None, "review_date": None, "decision_reason": None} for c in claims],
               "index_only_labels": data["index_only"], "observations": observations}
    return register, package


def compare_meraviglia():
    path = MAPS / "mr" / "mr_en-gb.pdf"
    data, raw = read_map(path), path.read_bytes()
    batch = json.loads((HERE.parent / "closure/meraviglia-review-batch.json").read_text(encoding="utf8"))
    rows = []
    for claim in batch["claims"]:
        match = [v for v in data["venues"] if v["key"] == claim["name"].upper()]
        venue = match[0] if match else None
        map_value = decks_of(venue) if venue else None
        rows.append({"claim_id": claim["id"], "venue": claim["name"], "held_plan_value": claim["value"], "held_plan_page": claim["page"], "map_value": map_value,
                     "map_tokens": venue["tokens"] if venue else None, "map_pages": sorted({r["page"] for r in venue["rows"]}) if venue else None,
                     "map_index_decks": venue["index_decks"] if venue else None, "agreement": "AGREE" if map_value == claim["value"] else "DIFFER"})
    return {"schema": "timonelo.meraviglia-source-comparison.v0", "use": "Comparison only. The held plan stays the source of MER-DK claims, and neither document replaces the other.",
            "held_plan": {"sha256": batch["claims"][0]["artifact_sha256"], "edition": "11.2025 DEU", "document_type": "cruise_line_deck_plan", "state": "UNREGISTERED"},
            "ship_map": {"url": BASE + path.name, "retrieved_on": RETRIEVED, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "cover_title": data["cover"], "pages": data["pages"],
                         "version": None, "version_status": "UNKNOWN_NOT_PRINTED", "pdf_metadata": data["metadata"], "state": "NOT_A_SOURCE_FOR_MER_DK_CLAIMS"},
            "comparison": rows}


def review_sheet(register, packages):
    lines = ["# Ship map human review sheet", "", "Prepared 2026-11-05. Every decision is open and nothing has been applied. Mark each row APPROVE, REJECT or DEFER, with reviewer, date and reason.", "",
             "A row states what the map prints, in a map whose version is unknown. It is not a statement of current operations.", ""]
    for entry, package in zip(register, packages):
        lines += [f"## {entry['vessel']}", "", f"Classification: **{entry['eligibility']['classification']}**. SHA-256 `{entry['sha256']}`.",
                  f"Readings: {entry['counts']['AGREED']} agreed, {entry['counts']['TABLE_ONLY']} from one reading, {entry['counts']['CONFLICT']} rejected.", ""]
        if package["vessel"]["identity_state"].startswith("BLOCKED"):
            lines += [f"Depends on the IMO decision for this ship: stored {package['vessel']['stored_imo']}, verified {package['vessel']['verified_imo']}.", ""]
        lines += ["| ID | Printed label | Deck(s) | Page | Decision |", "|---|---|---|---|---|"]
        lines += [f"| {c['id']} | {c['name']} | {', '.join(map(str, c['value']))} | {c['page']} | OPEN |" for c in package["first_review_batch"]]
        rejected = [o for o in package["observations"] if o["status"] == "CONFLICT"]
        if rejected:
            lines += ["", "Rejected as conflicting, no decision needed:", ""]
            for o in rejected:
                rows = "; ".join(f"page {r['page']} prints {r['token']}" for r in o["all_table_rows"])
                index = o["deck_index"]["decks_listed"]
                lines.append(f"- {o['exact_label']}: {rows}; deck index lists {index if index else 'nothing under this name'}")
        lines.append("")
    (HERE / "HUMAN_REVIEW.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf8", newline="\n")


def main():
    (HERE / "observations").mkdir(exist_ok=True)
    register, packages = [], []
    for code in SHIPS:
        entry, package = build(code)
        register.append(entry)
        packages.append(package)
        (HERE / "observations" / f"{entry['slug']}.json").write_text(json.dumps(package, indent=1, ensure_ascii=False) + "\n", encoding="utf8", newline="\n")
        print(entry["slug"], entry["eligibility"]["classification"], entry["counts"], len(package["first_review_batch"]), [c["name"] + str(c["value"]) for c in package["first_review_batch"]])
    review_sheet(register, packages)
    (HERE / "meraviglia-source-comparison.json").write_text(json.dumps(compare_meraviglia(), indent=2, ensure_ascii=False) + "\n", encoding="utf8", newline="\n")
    (HERE / "source-register.json").write_text(json.dumps({"schema": "timonelo.ship-map-register.v0", "documents": register}, indent=2, ensure_ascii=False) + "\n", encoding="utf8", newline="\n")


main()
