"""Author Deck 14 cabin-feature statements from grounded deck-plan symbols.

Reads the six grounded sleeping-arrangement symbol families off ART-0001
page 5 via `timonelo.spatial.deck14_symbol_extract`, and records one statement
per observed symbol through the canonical `StatementEditor`.

Positive observations only. A cabin with no symbol for a family gets no
statement for it, which leaves that question UNKNOWN — computed from the
registry, never stored as a denial. Nothing here writes "no sofa bed".

Re-running is safe: statements already present for the same entity, question
and value are left alone rather than duplicated.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from timonelo.evidence.questions import Question, QuestionRegistry  # noqa: E402
from timonelo.evidence.workspace import Workspace  # noqa: E402
from timonelo.spatial import deck14_symbol_extract as symbols  # noqa: E402

EVIDENCE_ROOT = os.path.join(REPO_ROOT, "evidence")
VESSEL = "MSC-BELLISSIMA"
READ_BY = "deck14-symbol-extractor"
READ_ON = "2026-08-22"

UNKNOWN_GUIDANCE = (
    "The deck plan prints no such symbol for this stateroom. That is not a "
    "statement that the feature is absent; confirm with MSC when booking."
)


def questions_for_families() -> List[Question]:
    return [
        Question(
            question_id=family.question_id,
            entity_type="cabin",
            statement_type=family.statement_type,
            labels={"en": f"Does this stateroom have a {family.label_en.lower()}?",
                    "de": f"Hat diese Kabine ein {family.legend_de}?"},
            unknown_guidance=UNKNOWN_GUIDANCE,
        )
        for family in symbols.GROUNDED_FAMILIES
    ]


def register_questions(path: str) -> int:
    registry = QuestionRegistry.load(path)
    added = 0
    for question in questions_for_families():
        try:
            registry.get(question.question_id)
        except KeyError:
            registry.register(question)
            added += 1
    if added:
        registry.save(path)
    return added


def locator_for(observation: symbols.SymbolObservation) -> str:
    """Where in the artifact the symbol was read."""
    family = observation.family
    refs = ", ".join(observation.source_references)
    return (
        f"Page {symbols.SYMBOL_PAGE_NUMBER}, Deck 14 (World Class) plan, "
        f"cell labelled {observation.cabin_number}; legend symbol "
        f"'{family.legend_de}' (page {symbols.LEGEND_PAGE_NUMBER} legend); "
        f"symbol drawing {refs}"
    )


def derivation_note_for(observation: symbols.SymbolObservation) -> str:
    """Only cardinality-derived families carry one; direct reads do not."""
    family = observation.family
    if not family.is_derived:
        return ""
    return (
        f"The printed primitive is a bare "
        f"{'square' if 'bed' in family.family_id and 'bunk' not in family.family_id else 'circle'}"
        f", which carries no shape information on its own. The legend "
        f"distinguishes this family by cardinality: {family.cardinality} "
        f"adjacent instance(s) form one symbol. This observation grouped "
        f"{observation.instance_count} instance(s) using the legend's own pair "
        f"spacing, then attributed the group to exactly one cabin envelope by "
        f"strict centroid containment."
    )


def ingest() -> Dict[str, int]:
    import json
    from timonelo.canonical import canonical_dump

    added_questions = register_questions(
        os.path.join(EVIDENCE_ROOT, "registry", "questions.json")
    )
    report = symbols.extract_symbols()
    statements_path = os.path.join(EVIDENCE_ROOT, "statements", "statements.json")
    raw_existing: Dict[str, Any] = {}
    if os.path.exists(statements_path):
        with open(statements_path, "r", encoding="utf-8") as f:
            raw_existing = json.load(f)

    workspace = Workspace(EVIDENCE_ROOT)
    editor = workspace.editor

    existing = {
        (s.entity_id, s.question_id, str(s.value))
        for s in editor.all()
    }

    created = 0
    skipped = 0
    new_statements: Dict[str, Any] = {}
    for observation in report.observations:
        family = observation.family
        entity_id = f"cabin:{VESSEL}:{observation.cabin_number}"
        key = (entity_id, family.question_id, "true")
        if key in existing:
            skipped += 1
            continue
        stmt = editor.create(
            entity_id=entity_id,
            question_id=family.question_id,
            statement_type=family.statement_type,
            value="true",
            artifact_id=symbols.ARTIFACT_ID,
            page=symbols.SYMBOL_PAGE_NUMBER,
            locator=locator_for(observation),
            read_by=READ_BY,
            read_on=READ_ON,
            method="CALCULATED" if family.is_derived else "DIRECT",
            derivation_note=derivation_note_for(observation),
            note=(
                f"Legend family '{family.legend_de}'. Symbol matched its page-2 "
                f"legend exemplar to a normalized deviation of "
                f"{observation.shape_deviation}."
            ),
        )
        new_statements[stmt.statement_id] = stmt.to_dict()
        existing.add(key)
        created += 1

    if created:
        # Merge without normalizing pre-existing statement records
        merged = dict(raw_existing)
        merged.update(new_statements)
        canonical_dump(merged, statements_path)

    return {
        "questions_registered": added_questions,
        "statements_created": created,
        "statements_already_present": skipped,
        "observations": len(report.observations),
        "cabins_with_features": len(report.by_cabin()),
    }


FEATURES_OUTPUT = os.path.join(
    REPO_ROOT, "frontend", "public", "data", "deck14.features.json"
)
FEATURES_SCHEMA = "timonelo.deck14-cabin-features.v0"


def export_for_frontend(path: str = FEATURES_OUTPUT) -> Dict[str, int]:
    """Project the authored statements into the viewer's read model.

    The viewer reads this, not the geometry proof: features are statements
    about a cabin, not properties of its envelope, and the two must not be
    merged into one artifact. Only positive statements appear here, so a cabin
    absent from `cabins` is unknown rather than featureless.
    """
    import json

    workspace = Workspace(EVIDENCE_ROOT)
    by_type = {f.statement_type: f for f in symbols.GROUNDED_FAMILIES}

    cabins: Dict[str, List[Dict[str, object]]] = {}
    for statement in workspace.editor.all():
        family = by_type.get(statement.statement_type)
        if family is None or str(statement.value) != "true":
            continue
        if not statement.entity_id.startswith(f"cabin:{VESSEL}:"):
            continue
        cabin_number = statement.entity_id.rsplit(":", 1)[-1]
        cabins.setdefault(cabin_number, []).append(
            {
                "family_id": family.family_id,
                "label_en": family.label_en,
                "legend_de": family.legend_de,
                "statement_id": statement.statement_id,
                "statement_type": statement.statement_type,
                "question_id": statement.question_id,
                "artifact_id": statement.artifact_id,
                "page": statement.page,
                "locator": statement.locator,
                "method": statement.method.value,
                "derivation_note": statement.derivation_note,
                "evidence_condition": statement.evidence_condition.value,
                "human_review_state": statement.human_review_state.value,
                "publish_status": statement.publish_status.value,
            }
        )
    for entries in cabins.values():
        entries.sort(key=lambda e: str(e["family_id"]))

    document = {
        "schema": FEATURES_SCHEMA,
        "vessel": VESSEL,
        "deck": 14,
        "source": {
            "artifact_id": symbols.ARTIFACT_ID,
            "artifact_sha256": symbols.ARTIFACT_SHA256,
            "pdf_page_number": symbols.SYMBOL_PAGE_NUMBER,
            "legend_page_number": symbols.LEGEND_PAGE_NUMBER,
            "document_class": "cruise_line_deck_plan",
        },
        "unknown_guidance": UNKNOWN_GUIDANCE,
        "families": [
            {
                "family_id": f.family_id,
                "label_en": f.label_en,
                "legend_de": f.legend_de,
                "statement_type": f.statement_type,
                "question_id": f.question_id,
                "derived_from_cardinality": f.is_derived,
            }
            for f in symbols.GROUNDED_FAMILIES
        ],
        "cabins": {number: cabins[number] for number in sorted(cabins)},
    }
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(document, indent=2, ensure_ascii=False) + "\n")
    return {
        "cabins_exported": len(cabins),
        "features_exported": sum(len(v) for v in cabins.values()),
    }


if __name__ == "__main__":
    for key, value in ingest().items():
        print(f"{key}: {value}")
    for key, value in export_for_frontend().items():
        print(f"{key}: {value}")
