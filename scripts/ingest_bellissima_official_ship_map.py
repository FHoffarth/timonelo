#!/usr/bin/env python3
"""
MSC Bellissima official ship map intake — second Bellissima evidence class.

Registers `be_en-gb.pdf` ("MSC BELLISSIMA SHIP MAP") through the canonical
ArtifactRegistry and ingests the venue-to-deck assignments printed in its
index tables.

WHAT THIS SOURCE SUPPORTS
    Which deck a named venue is on. The document prints this as explicit
    two-column index tables ("Restaurants | Deck", "Bars - Lounges | Deck",
    "Shops | Deck", "Fun | Deck", "Family Areas | Deck", ...) on pages 3-10.
    Only those tables are read.

WHAT IT DOES NOT SUPPORT, AND WHAT THIS SCRIPT THEREFORE NEVER PRODUCES
    Position, coordinates, metric distance, walking time, accessibility,
    cabin-to-venue adjacency, doors, corridors, lift or route connectivity.
    The ship silhouettes and the callout lines that tie a venue label to a
    drawn shape are PRESENTATIONAL: a thematic map places a label where the
    layout reads well, not where the venue is. `official_ship_map` is
    deliberately absent from `deck.venue_position` in the authority matrix.

    Nothing here writes geometry, and nothing here touches the spatial graph
    or the router. The intended bridge is future and manual:
        official_ship_map -> evidenced venue identity/deck
                          -> spatial object association (later)
                          -> navigation graph (later)

RANGES ARE NEVER COLLAPSED
    Values are always an ordered list of decks, even for a single deck, so a
    printed range cannot degrade to a scalar through a type change. A printed
    range ("5-6", "16-18") is expanded against the deck selector on page 2 of
    this same document, which lists the vessel's fifteen passenger decks:
    19, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4. Note the absence of
    Deck 17: "16-18" therefore resolves to [16, 18], NOT [16, 17, 18].
    Expanding a range consults a second printed fact, so those statements are
    CALCULATED with a derivation note; single-deck rows are DIRECT.

STATEMENT STORE
    Statements are authored by StatementEditor against a temporary store and
    then merged into `evidence/statements/statements.json`. Existing records
    are copied through untouched, byte-identical: the 113 ART-0001 statements
    are persisted in the pre-migration schema (`review_state`) and rewriting
    them into the current schema would be a silent mutation of accepted facts.
    StatementEditor's loader reads both shapes.

Every statement is created DRAFT / UNKNOWN / PUBLISH_BLOCKED, as
StatementEditor always does. This intake promotes nothing.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
from typing import Any, Dict, List, Optional, Sequence, Tuple

from timonelo.canonical import canonical_dump
from timonelo.evidence.conflicts import ConflictLog
from timonelo.evidence.editor import StatementEditor
from timonelo.evidence.registry import ArtifactRegistry, sha256_of_file
from timonelo.evidence.review import ReviewLog

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ARTIFACTS_ROOT = os.path.join(REPO_ROOT, "evidence", "artifacts")
STATEMENTS_PATH = os.path.join(REPO_ROOT, "evidence", "statements", "statements.json")
QUESTIONS_PATH = os.path.join(REPO_ROOT, "evidence", "registry", "questions.json")

DOCUMENT_CLASS = "official_ship_map"
STATEMENT_TYPE = "deck.venue_present"
QUESTION_ID = "Q-0016"
VESSEL_ID = "MSC-BELLISSIMA"
TITLE = "MSC BELLISSIMA SHIP MAP"
PUBLISHER = "MSC Cruises"
LANGUAGE = "en-GB"
ACQUIRED_ON = "2026-08-22"
ACQUISITION_METHOD = "supplied by project owner; obtained from the myMSC application"
READ_BY = "f.hoffarth"
READ_ON = "2026-08-22"

#: Pages carrying index tables. Pages 1 (cover) and 2 (overall map) carry no
#: venue-to-deck table and are read only for the deck selector.
TABLE_PAGES: Tuple[int, ...] = (3, 4, 5, 6, 7, 8, 9, 10)
DECK_SELECTOR_PAGE = 2

#: Category labels printed above a "Deck" column, used for the locator.
TABLE_HEADERS = frozenset({
    "MSC Yacht Club",
    "Restaurants",
    "Bars - Lounges",
    "Outdoor Bars",
    "Shops",
    "Fun",
    "Family Areas",
})

_DECK_VALUE = re.compile(r"^(\d{1,2})(?:-(\d{1,2}))?$")


class IngestError(RuntimeError):
    pass


def _fitz():
    try:
        import fitz  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment guard
        raise IngestError(
            "PyMuPDF is required to read the ship map. Install the dev extra."
        ) from exc
    return fitz


# --- artifact intake ------------------------------------------------------


def vault_path_for(digest: str, extension: str = ".pdf") -> str:
    return os.path.join(
        REPO_ROOT, "evidence", "raw", "sha256", digest[:2], f"{digest}{extension}"
    )


def register_source(source_path: str) -> Tuple[str, str]:
    """Register the ship map and place its bytes in the canonical SHA vault.

    Idempotent: ArtifactRegistry returns the existing artifact when the same
    bytes are already held, so re-running issues no second ID. Returns
    `(artifact_id, sha256)`.
    """
    if not os.path.isfile(source_path):
        raise IngestError(f"No file at {source_path!r}.")

    registry = ArtifactRegistry(ARTIFACTS_ROOT)
    artifact = registry.register(
        path=source_path,
        document_class=DOCUMENT_CLASS,
        acquired_on=ACQUIRED_ON,
        acquisition_method=ACQUISITION_METHOD,
        publisher=PUBLISHER,
        language=LANGUAGE,
        notes=(
            f"{TITLE}. Vessel: MSC Bellissima. Interactive ship map, "
            "10 pages, English (en-GB). Venue-to-deck index tables on pages "
            "3-10; page 2 carries the overall map and the deck selector."
        ),
    )

    # register() copies into the legacy blob directory. The canonical store is
    # the content-addressed vault, so move the copy there rather than leaving
    # the same bytes in two places. resolve_path() prefers the vault and falls
    # back to a blob only when the vault holds nothing.
    vault = vault_path_for(artifact.sha256)
    os.makedirs(os.path.dirname(vault), exist_ok=True)
    blob = registry.blob_path(artifact.artifact_id)
    if not os.path.exists(vault):
        if os.path.exists(blob):
            shutil.move(blob, vault)
        else:
            shutil.copy2(source_path, vault)
    elif os.path.exists(blob):
        os.remove(blob)

    resolved = registry.resolve_path(artifact.artifact_id)
    if resolved is None or os.path.abspath(resolved) != os.path.abspath(vault):
        raise IngestError(
            f"{artifact.artifact_id} did not resolve to the canonical vault "
            f"(got {resolved!r})."
        )
    if sha256_of_file(resolved) != artifact.sha256:
        raise IngestError("Digest changed after registration.")
    return artifact.artifact_id, artifact.sha256


# --- extraction -----------------------------------------------------------


def declared_decks(document) -> Tuple[int, ...]:
    """The vessel's decks, read from the page-2 deck selector.

    Each selector entry is the word "Deck" followed on the same baseline by a
    number. Nothing is assumed about which decks a ship has.
    """
    words = document[DECK_SELECTOR_PAGE - 1].get_text("words")
    decks: List[int] = []
    for word in words:
        if word[4] != "Deck":
            continue
        same_line = [
            w
            for w in words
            if w[4].isdigit() and abs(w[1] - word[1]) < 3 and 0 <= w[0] - word[2] < 20
        ]
        if len(same_line) == 1:
            decks.append(int(same_line[0][4]))
    if not decks:
        raise IngestError("No deck selector found on page 2.")
    return tuple(sorted(set(decks)))


def extract_rows(document, decks: Sequence[int]) -> List[Dict[str, Any]]:
    """Read the printed venue/deck index rows from the table pages.

    A row is a line that is exactly a deck value ("7", "5-6") preceded by the
    venue name. Restricting the value to a declared deck rejects the cabin
    number ranges printed elsewhere in the document.
    """
    valid = set(decks)
    rows: List[Dict[str, Any]] = []
    for page_number in TABLE_PAGES:
        lines = [l.strip() for l in document[page_number - 1].get_text().split("\n")]
        section = lines[0] if lines else ""
        header: Optional[str] = None
        for index, line in enumerate(lines):
            if line in TABLE_HEADERS:
                header = line
            match = _DECK_VALUE.match(line)
            if match is None:
                continue
            low = int(match.group(1))
            high = int(match.group(2)) if match.group(2) else None
            if low not in valid or (high is not None and high not in valid):
                continue
            if index == 0:
                continue
            name = lines[index - 1].strip()
            if not name or name == "Deck" or _DECK_VALUE.match(name):
                continue
            rows.append({
                "page": page_number,
                "section": section,
                "table": header or section,
                "venue_name": name,
                "printed_deck": line,
            })
    if not rows:
        raise IngestError("No venue/deck rows extracted.")
    return rows


def resolve_decks(printed: str, decks: Sequence[int]) -> Tuple[List[int], bool]:
    """Resolve a printed deck token to an ordered deck list.

    Returns `(decks, is_range)`. A range is expanded to the decks the document
    itself declares between the endpoints inclusive — never to every integer
    in between, because the vessel has no Deck 17.
    """
    match = _DECK_VALUE.match(printed)
    if match is None:
        raise IngestError(f"Unparseable deck token {printed!r}.")
    low = int(match.group(1))
    if match.group(2) is None:
        return [low], False
    high = int(match.group(2))
    span = sorted(d for d in decks if low <= d <= high)
    if span[0] != low or span[-1] != high:
        raise IngestError(f"Range {printed!r} does not align with declared decks.")
    return span, True


def slugify(name: str) -> str:
    slug = name.lower()
    slug = slug.replace("&", " and ")
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def build_facts(
    rows: Sequence[Dict[str, Any]], decks: Sequence[int]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Collapse repeated printings of one claim into one fact.

    A venue indexed on several category pages with the same deck is one claim
    observed several times, not several claims. Corroborating occurrences are
    kept with their pages. A venue printed with DIFFERENT decks on different
    pages is an intra-document disagreement: it is reported and NOT ingested.
    """
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(slugify(row["venue_name"]), []).append(row)

    facts: List[Dict[str, Any]] = []
    disagreements: List[Dict[str, Any]] = []
    for slug in sorted(grouped):
        occurrences = sorted(grouped[slug], key=lambda r: (r["page"], r["table"]))
        distinct = sorted({o["printed_deck"] for o in occurrences})
        if len(distinct) > 1:
            disagreements.append({
                "venue_slug": slug,
                "venue_name": occurrences[0]["venue_name"],
                "printed_values": distinct,
                "occurrences": [
                    {"page": o["page"], "table": o["table"], "value": o["printed_deck"]}
                    for o in occurrences
                ],
            })
            continue
        printed = distinct[0]
        deck_list, is_range = resolve_decks(printed, decks)
        facts.append({
            "venue_slug": slug,
            "venue_name": occurrences[0]["venue_name"],
            "printed_deck": printed,
            "decks": deck_list,
            "is_range": is_range,
            "occurrences": occurrences,
        })
    return facts, disagreements


# --- statement authoring --------------------------------------------------


def ensure_question() -> bool:
    """Register Q-0016 for deck.venue_present. Returns True if added."""
    with open(QUESTIONS_PATH, encoding="utf-8") as handle:
        registry = json.load(handle)
    if QUESTION_ID in registry["questions"]:
        return False
    registry["questions"][QUESTION_ID] = {
        "question_id": QUESTION_ID,
        "entity_type": "venue",
        "statement_type": STATEMENT_TYPE,
        "labels": {"en": "Which deck is this venue on?"},
        "supportable_by": [],
        "unknown_guidance": "Not listed on any ship map or deck plan held.",
    }
    canonical_dump(registry, QUESTIONS_PATH)
    return True


def _locator(fact: Dict[str, Any]) -> str:
    primary = fact["occurrences"][0]
    text = (
        f"Page {primary['page']}, {primary['section']} index table "
        f"\"{primary['table']} | Deck\", row \"{fact['venue_name']}\" with "
        f"printed deck value \"{fact['printed_deck']}\""
    )
    extra = fact["occurrences"][1:]
    if extra:
        repeats = "; ".join(
            f"page {o['page']} table \"{o['table']}\"" for o in extra
        )
        text += f" (same value also printed on {repeats})"
    return text


def _note(fact: Dict[str, Any]) -> str:
    pages = ", ".join(str(o["page"]) for o in fact["occurrences"])
    note = f"Printed on page(s) {pages}."
    if fact["is_range"]:
        note += (
            f" Source prints the range \"{fact['printed_deck']}\"; expanded to "
            f"{fact['decks']} using the page {DECK_SELECTOR_PAGE} deck selector "
            "of this same document."
        )
    note += (
        " Deck assignment only: this source establishes no position, distance, "
        "adjacency, door, corridor, connectivity or accessibility."
    )
    return note


def author_statements(
    artifact_id: str, facts: Sequence[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Create statements through StatementEditor in a temporary store.

    The editor is the sole creator of statements; running it against a scratch
    path lets the canonical store be merged deliberately rather than rewritten.
    """
    created: List[Dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as scratch:
        registry = ArtifactRegistry(ARTIFACTS_ROOT)
        editor = StatementEditor(
            path=os.path.join(scratch, "statements.json"),
            registry=registry,
            review_log=ReviewLog(os.path.join(scratch, "reviews.json")),
            conflict_log=ConflictLog(os.path.join(scratch, "conflicts.json")),
        )
        # Seed the editor with the existing store so ids continue the sequence
        # and conflict detection sees the incumbent facts.
        with open(STATEMENTS_PATH, encoding="utf-8") as handle:
            existing = json.load(handle)
        editor_ids = sorted(existing)
        next_number = 1 + max(int(sid.split("-")[1]) for sid in editor_ids)

        for offset, fact in enumerate(facts):
            statement = editor.create(
                entity_id=f"venue:{VESSEL_ID}:{fact['venue_slug']}",
                question_id=QUESTION_ID,
                statement_type=STATEMENT_TYPE,
                value=fact["decks"],
                artifact_id=artifact_id,
                locator=_locator(fact),
                read_by=READ_BY,
                read_on=READ_ON,
                page=fact["occurrences"][0]["page"],
                method="CALCULATED" if fact["is_range"] else "DIRECT",
                derivation_note=(
                    f"Printed range \"{fact['printed_deck']}\" expanded across the "
                    f"decks declared by the page {DECK_SELECTOR_PAGE} deck selector."
                    if fact["is_range"]
                    else ""
                ),
                note=_note(fact),
            )
            record = statement.to_dict()
            record["statement_id"] = f"STM-{next_number + offset:04d}"
            created.append(record)
    return created


def merge_into_store(records: Sequence[Dict[str, Any]]) -> int:
    """Append new records, copying existing ones through unchanged."""
    with open(STATEMENTS_PATH, encoding="utf-8") as handle:
        store = json.load(handle)
    added = 0
    for record in records:
        if record["statement_id"] in store:
            raise IngestError(f"Statement id collision {record['statement_id']}.")
        store[record["statement_id"]] = record
        added += 1
    canonical_dump(store, STATEMENTS_PATH)
    return added


# --- entry point ----------------------------------------------------------


def run(source_path: str) -> Dict[str, Any]:
    artifact_id, digest = register_source(source_path)

    fitz = _fitz()
    document = fitz.open(vault_path_for(digest))
    try:
        decks = declared_decks(document)
        rows = extract_rows(document, decks)
    finally:
        document.close()

    facts, disagreements = build_facts(rows, decks)
    question_added = ensure_question()

    with open(STATEMENTS_PATH, encoding="utf-8") as handle:
        before = json.load(handle)
    already = {
        s["entity_id"]
        for s in before.values()
        if s.get("statement_type") == STATEMENT_TYPE
    }
    new_facts = [
        f for f in facts if f"venue:{VESSEL_ID}:{f['venue_slug']}" not in already
    ]

    records = author_statements(artifact_id, new_facts)
    added = merge_into_store(records)

    return {
        "artifact_id": artifact_id,
        "sha256": digest,
        "byte_size": os.path.getsize(vault_path_for(digest)),
        "declared_decks": list(decks),
        "rows_read": len(rows),
        "facts": len(facts),
        "multi_deck_facts": sorted(
            (f["venue_name"], f["printed_deck"], f["decks"])
            for f in facts
            if f["is_range"]
        ),
        "corroborated_facts": sum(1 for f in facts if len(f["occurrences"]) > 1),
        "intra_document_disagreements": disagreements,
        "skipped_already_present": len(facts) - len(new_facts),
        "statements_added": added,
        "question_added": question_added,
    }


def main(argv: Sequence[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {os.path.basename(argv[0])} <path-to-be_en-gb.pdf>")
        return 2
    summary = run(argv[1])
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
