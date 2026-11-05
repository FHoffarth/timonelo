"""Read venue/deck tables and the per-deck index from official MSC ship maps. Read-only research tool.

Each document is read twice and independently: the "Deck" tables and the page listing labels under
"DECK n" headings. A reading becomes an observation only when both agree.
"""
import re
import unicodedata

import fitz

DECK_TOKEN = re.compile(r"^(\d{1,2})(?:\s*-\s*(\d{1,2}))?$")
HEAD = re.compile(r"^DECK (\d{1,2})$")


def spans(page):
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if span["text"].strip() and line["dir"] == (1.0, 0.0):
                    yield {"text": " ".join(span["text"].split()), "box": list(span["bbox"]), "size": span["size"],
                           "bold": "Bold" in span["font"]}


def key(label):
    text = label.replace("’", "'").replace("–", "-").replace("®", "")
    text = re.sub(r"\s*\(.*?\)\*?", "", text).replace("*", "")
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    return " ".join(text.upper().replace(" - ", " ").split())


def read_tables(doc):
    """Rows of every table: label, printed deck token, section, page, row box."""
    rows = []
    for number, page in enumerate(doc, 1):
        items = list(spans(page))
        heads = sorted((s for s in items if s["text"].lower() == "deck" and s["bold"] and s["size"] >= 7), key=lambda s: s["box"][2])
        title = next((s["text"] for s in sorted(items, key=lambda s: s["box"][1]) if s["bold"]), "")
        for index, head in enumerate(heads):
            left = 0 if index == 0 else heads[index - 1]["box"][2] + 1
            right = head["box"][2] + 1.5
            tokens = [s for s in items if DECK_TOKEN.match(s["text"]) and abs(s["box"][2] - head["box"][2]) < 3 and s["box"][1] > head["box"][1]]
            names = [s for s in items if not s["bold"] and left <= s["box"][0] and s["box"][2] < head["box"][0] and s["box"][1] > head["box"][1] - 1]
            starts = [round(s["box"][0]) for s in names]
            if not tokens or not starts:
                continue
            margin = max(set(starts), key=starts.count)
            section = next((s["text"] for s in sorted(items, key=lambda s: -s["box"][1]) if s["bold"] and s is not head and
                            s["box"][1] < head["box"][3] and left <= s["box"][0] < head["box"][0] and s["box"][1] > head["box"][1] - 3), title)
            for token in sorted(tokens, key=lambda s: s["box"][1]):
                mid = (token["box"][1] + token["box"][3]) / 2
                parts = sorted((s for s in names if abs((s["box"][1] + s["box"][3]) / 2 - mid) <= 6),
                               key=lambda s: (round(s["box"][1]), s["box"][0]))
                if not parts or abs(parts[0]["box"][0] - margin) >= 2:
                    continue
                box = [min(s["box"][0] for s in parts), min(token["box"][1], parts[0]["box"][1]), token["box"][2],
                       max(token["box"][3], parts[-1]["box"][3])]
                rows.append({"label": " ".join(s["text"] for s in parts), "token": token["text"], "page": number, "section": section, "box": [round(v, 2) for v in box]})
    return rows


def read_index(doc):
    """Labels under each DECK n heading on the deck-selector page."""
    found = {}
    for number, page in enumerate(doc, 1):
        items = list(spans(page))
        heads = [(int(HEAD.match(s["text"]).group(1)), s) for s in items if HEAD.match(s["text"]) and s["bold"] and s["size"] >= 6.5]
        if len(heads) < 6:
            continue
        columns = sorted({round(s["box"][0]) for _, s in heads})
        for deck, head in heads:
            x = head["box"][0]
            below = [other["box"][1] for _, other in heads if abs(other["box"][0] - x) < 5 and other["box"][1] > head["box"][1]]
            limit = min(below) if below else page.rect.height
            nxt = min([c for c in columns if c > x + 5], default=page.rect.width)
            lines = sorted((s for s in items if not s["bold"] and abs(s["size"] - head["size"]) < 0.6 and
                            x + 2 < s["box"][0] < nxt - 2 and head["box"][1] < s["box"][1] < limit), key=lambda s: s["box"][1])
            group = []
            for line in lines:
                # Index labels wrap to at most two lines, so a third close line starts a new label.
                if group and (line["box"][1] - group[-1]["box"][1] > 10 or len(group) == 2):
                    found.setdefault(number, []).append((deck, " ".join(g["text"] for g in group), group[0]["box"]))
                    group = []
                group.append(line)
            if group:
                found.setdefault(number, []).append((deck, " ".join(g["text"] for g in group), group[0]["box"]))
    return found


def expand(token):
    match = DECK_TOKEN.match(token)
    low, high = int(match.group(1)), int(match.group(2) or match.group(1))
    return low, high


def reconcile(doc):
    rows, index = read_tables(doc), read_index(doc)
    entries = [e for page in index.values() for e in page]
    pages = sorted(index)
    decks_listed = {}
    for deck, label, _ in entries:
        decks_listed.setdefault(key(label), set()).add(deck)
    grouped = {}
    for row in rows:
        grouped.setdefault(key(row["label"]), []).append(row)
    results = []
    for name, group in sorted(grouped.items()):
        tokens = sorted({r["token"] for r in group})
        listed = sorted(decks_listed.get(name, ()))
        issues, value = [], None
        if len(tokens) > 1:
            issues.append("TABLES_DISAGREE: " + ", ".join(tokens))
        low, high = expand(tokens[0])
        if not listed:
            issues.append("NOT_IN_DECK_INDEX")
        elif len(tokens) == 1:
            if low == high and listed != [low]:
                issues.append(f"INDEX_DISAGREES: table {tokens[0]}, index {listed}")
            elif low != high and (listed[0] != low or listed[-1] != high):
                issues.append(f"INDEX_DISAGREES: table {tokens[0]}, index {listed}")
        if not issues:
            value = listed
        results.append({"key": name, "labels": sorted({r["label"] for r in group}), "tokens": tokens, "index_decks": listed, "value": value, "issues": issues,
                        "rows": group})
    only_index = sorted(n for n in decks_listed if n not in grouped)
    return {"rows": rows, "index_pages": pages, "index_entries": entries, "venues": results,
            "index_only": [{"key": n, "index_decks": sorted(decks_listed[n])} for n in only_index]}


def read_map(path):
    with fitz.open(path) as doc:
        data = reconcile(doc)
        data["pages"] = len(doc)
        data["metadata"] = {k: doc.metadata.get(k) for k in ("creator", "producer", "creationDate", "modDate")}
        data["text"] = "\n".join(p.get_text() for p in doc)
        # Covers carry a \x08 InDesign break after the ship name.
        data["cover"] = " ".join(doc[0].get_text().replace("\x08", " ").split())
    return data
