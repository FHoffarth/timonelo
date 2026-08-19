"""
Evidence Workspace CLI.

    python -m timonelo.evidence.cli <command> [options]

A curator's tool. Every command is a thin wrapper over the workspace; the CLI
holds no logic of its own beyond argument handling and exit codes.

Dates are required arguments rather than defaults from the clock: `--read-on`
records when a human read a document, which is not necessarily today, and
`as_of` must be explicit (ADR-0002 §4.1).
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from timonelo.evidence import authority
from timonelo.ontology.models import HumanReviewState, PublishStatus
from timonelo.evidence.workspace import DEFAULT_ROOT, Workspace


def _ws(args) -> Workspace:
    return Workspace(args.root)


# -- artifacts ---------------------------------------------------------------

def cmd_artifact_create(args) -> int:
    ws = _ws(args)
    a = ws.import_artifact(
        args.path, document_class=args.document_class,
        acquired_on=args.acquired_on, acquisition_method=args.acquisition_method,
        publisher=args.publisher, published_on=args.published_on,
        version=args.version, language=args.language, notes=args.notes or "")
    print(f"Registered {a.artifact_id}")
    print(f"  {a.filename}  {a.byte_size} bytes")
    print(f"  sha256 {a.sha256}")
    print("\nImport ends here. Statements are created separately with "
          "'statement create'.")
    return 0


def cmd_artifact_list(args) -> int:
    ws = _ws(args)
    arts = ws.list_artifacts()
    if not arts:
        print("No artifacts. The store is empty.")
        return 0
    print(f"{'ID':<10} {'CLASS':<32} {'FILE':<28} STATEMENTS")
    for a in arts:
        n = len(ws.statements_for_artifact(a.artifact_id))
        print(f"{a.artifact_id:<10} {a.document_class:<32} {a.filename:<28} {n}")
    return 0


def cmd_artifact_inspect(args) -> int:
    print(_ws(args).format_artifact(args.artifact_id))
    return 0


def cmd_artifact_coverage(args) -> int:
    ws = _ws(args)
    c = ws.document_coverage(args.artifact_id)
    print(f"DOCUMENT COVERAGE — {c['artifact_id']} ({c['document_class']})")
    print(f"  Questions supported:  {c['questions_supported']}")
    print(f"  Questions answered:   {c['questions_answered']}")
    print(f"  Questions UNKNOWN:    {c['questions_unknown']}")
    print(f"  Coverage:             {c['coverage_pct']}%")
    if c["unknown_question_ids"]:
        print(f"  Unanswered:           {', '.join(c['unknown_question_ids'])}")
    return 0


# -- statements --------------------------------------------------------------

def cmd_statement_create(args) -> int:
    ws = _ws(args)
    s = ws.create_statement(
        entity_id=args.entity, question_id=args.question,
        statement_type=args.statement_type, value=args.value,
        artifact_id=args.artifact, page=args.page, locator=args.locator,
        read_by=args.read_by, read_on=args.read_on,
        method=args.method, derivation_note=args.derivation_note,
        valid_from=args.valid_from, valid_until=args.valid_until,
        note=args.note or "")
    print(f"Created {s.statement_id} in {s.review_state}")
    print(f"  {s.question_id} = {s.value}")
    print(f"  from {s.artifact_id}"
          + (f", page {s.page}" if s.page is not None else "")
          + f", {s.locator}")
    print("\nNot answerable until reviewed and approved.")
    return 0


def cmd_statement_list(args) -> int:
    ws = _ws(args)
    stmts = ws.list_statements()
    if not stmts:
        print("No statements.")
        return 0
    print(f"{'ID':<10} {'STATE':<14} {'ENTITY':<26} {'QUESTION':<10} VALUE")
    for s in stmts:
        if args.state and s.review_state != args.state:
            continue
        print(f"{s.statement_id:<10} {s.review_state:<14} {s.entity_id:<26} "
              f"{s.question_id:<10} {s.value}")
    return 0


def cmd_statement_inspect(args) -> int:
    print(_ws(args).format_statement(args.statement_id))
    return 0


def _transition(args, to_state: HumanReviewState) -> int:
    ws = _ws(args)
    s = ws.transition(args.statement_id, to_state, args.actor, args.on,
                      args.note or "")
    print(f"{s.statement_id} -> {s.review_state}  by {args.actor} on {args.on}")
    return 0


def cmd_submit(args) -> int:
    return _transition(args, HumanReviewState.UNDER_REVIEW)


def cmd_approve(args) -> int:
    return _transition(args, HumanReviewState.APPROVED)


def cmd_publish(args) -> int:
    ws = _ws(args)
    s = ws.publish_statement(args.statement_id, args.actor, args.on, args.note or "")
    print(f"{s.statement_id} -> PUBLISH_ALLOWED by {args.actor} on {args.on}")
    return 0


def cmd_reject(args) -> int:
    return _transition(args, HumanReviewState.REJECTED)


# -- reading -----------------------------------------------------------------

def cmd_answer(args) -> int:
    ws = _ws(args)
    ans = ws.engine.answer(args.entity, args.question, args.as_of)
    q = ws.questions.get(args.question)
    label = q.labels.get("en", args.question)
    if ans.contested:
        print(f"[CONTESTED — open conflict(s): {', '.join(ans.conflict_ids)}]")
    if not ans.known:
        print(f"{label}: UNKNOWN")
        if ans.unknown_guidance:
            print(f"  {ans.unknown_guidance}")
    else:
        print(f"{label}: {ans.value}")
        p = ans.provenance
        print(f"  source: {p.filename} ({p.artifact_id})"
              + (f", page {p.page}" if p.page is not None else "")
              + f", {p.locator}")
    if args.trace:
        print()
        print(ws.format_trace(ans))
    return 0


def cmd_trace(args) -> int:
    ws = _ws(args)
    print(ws.format_trace(ws.engine.answer(args.entity, args.question, args.as_of)))
    return 0


def cmd_conflict_list(args) -> int:
    ws = _ws(args)
    conflicts = ws.conflicts.open_conflicts() if args.open_only else ws.conflicts.all()
    if not conflicts:
        print("No conflicts." if not args.open_only else "No open conflicts.")
        return 0
    print(f"{'ID':<10} {'STATUS':<15} {'QUESTION':<10} INCUMBENT vs CHALLENGER")
    for c in conflicts:
        print(f"{c.conflict_id:<10} {c.status:<15} {c.question_id:<10} "
              f"{c.incumbent_statement_id}={c.incumbent_value!r} vs "
              f"{c.challenger_statement_id}={c.challenger_value!r}")
    return 0


def cmd_conflict_inspect(args) -> int:
    print(_ws(args).format_conflict(args.conflict_id))
    return 0


def cmd_conflict_resolve(args) -> int:
    ws = _ws(args)
    winner = None if args.reject_both else args.winner
    if winner is None and not args.reject_both:
        print("error: give --winner STM-XXXX or --reject-both", file=sys.stderr)
        return 1
    c = ws.editor.resolve_conflict(args.conflict_id, winner, args.actor,
                                   args.on, args.note)
    print(f"{c.conflict_id} -> {c.status}")
    print(f"  winner: {c.resolved_statement_id or 'none — both rejected'}")
    print(f"  reason: {c.resolution_note}")
    return 0


def cmd_questions(args) -> int:
    ws = _ws(args)
    qs = ws.questions.all()
    if not qs:
        print("No questions registered. The registry is empty.")
        return 0
    print(f"{'ID':<10} {'ENTITY':<10} {'STATEMENT TYPE':<30} LABEL")
    for q in qs:
        print(f"{q.question_id:<10} {q.entity_type:<10} "
              f"{q.statement_type or '-':<30} {q.labels.get('en','')}")
    return 0


def cmd_classes(args) -> int:
    print(f"{'CLASS':<32} {'REL':<6} {'SCOPE':<16} {'ACQUISITION':<14} PERMISSION")
    for c in authority.DOCUMENT_CLASSES.values():
        print(f"{c.class_id:<32} {c.reliability:<6} {c.validity_scope.value:<16} "
              f"{c.acquisition.value:<14} {c.use_permission.value}")
    return 0


# -- parser ------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="timonelo-evidence",
        description="Evidence Workspace — manual curation of ground truth.")
    p.add_argument("--root", default=DEFAULT_ROOT, help="evidence store root")
    sub = p.add_subparsers(dest="command", required=True)

    ac = sub.add_parser("artifact-create", help="register one PDF")
    ac.add_argument("path")
    ac.add_argument("--document-class", required=True)
    ac.add_argument("--acquired-on", required=True, help="ISO date obtained")
    ac.add_argument("--acquisition-method", required=True)
    ac.add_argument("--publisher")
    ac.add_argument("--published-on")
    ac.add_argument("--version")
    ac.add_argument("--language")
    ac.add_argument("--notes")
    ac.set_defaults(func=cmd_artifact_create)

    al = sub.add_parser("artifact-list", help="list registered artifacts")
    al.set_defaults(func=cmd_artifact_list)

    ai = sub.add_parser("artifact-inspect", help="full artifact detail")
    ai.add_argument("artifact_id")
    ai.set_defaults(func=cmd_artifact_inspect)

    acv = sub.add_parser("artifact-coverage", help="coverage of one document")
    acv.add_argument("artifact_id")
    acv.set_defaults(func=cmd_artifact_coverage)

    sc = sub.add_parser("statement-create", help="author one statement")
    sc.add_argument("--entity", required=True)
    sc.add_argument("--question", required=True)
    sc.add_argument("--statement-type", required=True)
    sc.add_argument("--value", required=True)
    sc.add_argument("--artifact", required=True)
    sc.add_argument("--locator", required=True,
                    help='free text, e.g. "Cabin table, top right, legend B"')
    sc.add_argument("--page", type=int)
    sc.add_argument("--read-by", required=True)
    sc.add_argument("--read-on", required=True)
    sc.add_argument("--valid-from")
    sc.add_argument("--valid-until")
    sc.add_argument("--note")
    sc.add_argument("--method", default="DIRECT",
                    choices=["DIRECT", "CALCULATED", "INFERRED"])
    sc.add_argument("--derivation-note", default="")
    sc.set_defaults(func=cmd_statement_create)

    sl = sub.add_parser("statement-list", help="list statements")
    sl.add_argument("--state", help="filter by workflow state")
    sl.set_defaults(func=cmd_statement_list)

    si = sub.add_parser("statement-inspect", help="full statement detail")
    si.add_argument("statement_id")
    si.set_defaults(func=cmd_statement_inspect)

    for name, fn, helptext in (
        ("submit", cmd_submit, "DRAFT -> UNDER_REVIEW"),
        ("approve", cmd_approve, "UNDER_REVIEW -> APPROVED"),
        ("publish", cmd_publish, "APPROVED -> PUBLISHED"),
        ("reject", cmd_reject, "-> REJECTED"),
    ):
        t = sub.add_parser(name, help=helptext)
        t.add_argument("statement_id")
        t.add_argument("--actor", required=True)
        t.add_argument("--on", required=True, help="ISO date")
        t.add_argument("--note")
        t.set_defaults(func=fn)

    an = sub.add_parser("answer", help="ask one question")
    an.add_argument("--entity", required=True)
    an.add_argument("--question", required=True)
    an.add_argument("--as-of")
    an.add_argument("--trace", action="store_true")
    an.set_defaults(func=cmd_answer)

    tr = sub.add_parser("trace", help="full provenance chain for an answer")
    tr.add_argument("--entity", required=True)
    tr.add_argument("--question", required=True)
    tr.add_argument("--as-of")
    tr.set_defaults(func=cmd_trace)

    cl = sub.add_parser("conflict-list", help="list conflicts")
    cl.add_argument("--open-only", action="store_true")
    cl.set_defaults(func=cmd_conflict_list)

    ci = sub.add_parser("conflict-inspect", help="full conflict detail")
    ci.add_argument("conflict_id")
    ci.set_defaults(func=cmd_conflict_inspect)

    cr = sub.add_parser("conflict-resolve", help="choose a winner, or reject both")
    cr.add_argument("conflict_id")
    cr.add_argument("--winner")
    cr.add_argument("--reject-both", action="store_true")
    cr.add_argument("--actor", required=True)
    cr.add_argument("--on", required=True)
    cr.add_argument("--note", required=True, help="why this reading was preferred")
    cr.set_defaults(func=cmd_conflict_resolve)

    sub.add_parser("questions", help="list registered questions").set_defaults(
        func=cmd_questions)
    sub.add_parser("classes", help="list document classes").set_defaults(
        func=cmd_classes)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:            # curator-facing: message, not traceback
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
