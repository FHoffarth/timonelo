"""Bounded private Evidence Factory batches; no canonical-apply or remote-ingestion mode.

Decision input is a trusted operator's record of actual human instructions, not
proof of identity. Exact binding prevents replay/drift; it is not a signature.
All authority decisions and transitions remain in the existing evidence APIs.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import date, datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import tempfile

from timonelo.canonical import canonical_dump
from timonelo.evidence import authority
from timonelo.evidence.conflicts import values_disagree
from timonelo.evidence.editor import EditorError
from timonelo.evidence.events import EvidenceEvent
from timonelo.evidence.fleet_projection import project_fleet
from timonelo.evidence.publication_snapshot import make_snapshot
from timonelo.evidence.registry import normalize_vessel_imo
from timonelo.evidence.workspace import Workspace
from timonelo.ontology.models import EvidenceCondition, HumanReviewState

READER = "Codex AI / registered PDF observation"
SCOPE = "SOURCE_EDITION_VENUE_DECK_ONLY"


class BatchError(ValueError):
    pass


def _bytes(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":")).encode("utf8")


def _hash(value):
    return hashlib.sha256(_bytes(value)).hexdigest()


def _files(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob("*") if p.is_file()}


def _states(workspace):
    rows = {}
    for statement in workspace.editor.all():
        verdict = workspace.editor.authority.evaluate(statement)
        rows[statement.statement_id] = (statement.to_dict(), verdict.admitted,
                                       [r.value for r in verdict.reason_codes])
    return rows


def _workspace(root):
    root = Path(root).resolve()
    if not (root / "evidence/artifacts/index.json").is_file():
        raise BatchError("SOURCE_REGISTRY_UNAVAILABLE")
    return Workspace(str(root / "evidence"))


def _document_reading(path, claim):
    # Existing optional dev dependency, not a new runtime/import route.
    import fitz
    with fitz.open(path) as doc:
        page_number = claim["page"]
        if type(page_number) is not int or not 1 <= page_number <= len(doc):
            raise BatchError("SOURCE_PAGE_INVALID")
        page = doc[page_number - 1]
        boxes = claim["source_boxes"]
        if not isinstance(boxes, list) or not boxes:
            raise BatchError("SOURCE_BOXES_INVALID")
        fragments = []
        for box in boxes:
            if (not isinstance(box, list) or len(box) != 4 or
                    not all(type(v) in (float, int) and math.isfinite(v) for v in box)):
                raise BatchError("SOURCE_BOXES_INVALID")
            rect = fitz.Rect(box)
            if rect.is_empty or not page.rect.contains(rect):
                raise BatchError("SOURCE_BOXES_INVALID")
            fragments.append(page.get_textbox(rect + (-2, -2, 2, 2)).strip())
        actual = " / ".join(fragments)
        if " ".join(actual.split()) != " ".join(claim["observed_text"].split()):
            raise BatchError("SOURCE_OBSERVATION_CHANGED")
        return actual


def inspect_batch(source_root, batch, decisions):
    """Read-only preflight and exception package; never derive approval."""
    root = Path(source_root).resolve()
    if not (root / "evidence/artifacts/index.json").is_file():
        raise BatchError("SOURCE_REGISTRY_UNAVAILABLE")
    before = {name: _files(root / name) for name in ("evidence", "knowledge")}
    # Even Registry construction creates a blobs directory. Construct only on
    # the private copy, rather than relying on the directory already existing.
    with tempfile.TemporaryDirectory(prefix="timonelo-batch-inspection-") as temporary:
        fixture = Path(temporary)
        shutil.copytree(root / "evidence", fixture / "evidence")
        if _files(fixture / "evidence") != before["evidence"]:
            raise BatchError("SOURCE_CHANGED_DURING_COPY")
        result = _inspect_batch(root, batch, decisions, _workspace(fixture))
    if before != {name: _files(root / name) for name in before}:
        raise BatchError("SOURCE_CHECKOUT_CHANGED")
    return result


def _inspect_batch(root, batch, decisions, ws):
    if batch.get("source_route") != "REGISTERED_LOCAL_ARTIFACT":
        raise BatchError("UNCONFIGURED_SOURCE_ROUTE: Drive/network ingestion is disabled")
    claims = batch.get("claims")
    if (batch.get("schema") != "timonelo.evidence-batch.v1" or
            not isinstance(claims, list) or not 1 <= len(claims) <= 8 or
            not all(isinstance(c, dict) and isinstance(c.get("id"), str) for c in claims)):
        raise BatchError("INVALID_BOUNDED_BATCH")
    if len({c["id"] for c in claims}) != len(claims):
        raise BatchError("DUPLICATE_CLAIM_ID")
    slug = batch.get("vessel_slug", "")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise BatchError("INVALID_VESSEL_SLUG")
    identity = json.loads((root / "knowledge/ships" / slug / "identity.json").read_text(encoding="utf8"))
    vessel = normalize_vessel_imo(identity["imo_number"]["value"])
    if vessel != batch.get("vessel_imo"):
        raise BatchError("CANONICAL_VESSEL_IDENTITY_MISMATCH")
    if not isinstance(batch.get("origin_limit"), str) or not batch["origin_limit"].strip():
        raise BatchError("SOURCE_ORIGIN_LIMITATION_MISSING")
    entries = decisions.get("decisions", [])
    if (not isinstance(entries, list) or
            not all(isinstance(d, dict) and isinstance(d.get("claim_id"), str) for d in entries)):
        raise BatchError("INVALID_DECISION_RECORDS")
    if len({d["claim_id"] for d in entries}) != len(entries):
        raise BatchError("DUPLICATE_DECISION_ID")
    by_id = {d["claim_id"]: d for d in entries}
    metadata_valid = bool(decisions.get("reviewer") and decisions.get("owner_review_statement") and
                          decisions.get("publication_processing_authorization"))
    try:
        if date.fromisoformat(decisions.get("review_date", "")) > datetime.now(timezone.utc).date():
            metadata_valid = False
    except (TypeError, ValueError):
        metadata_valid = False
    rows, sources, seen = [], {}, set()
    for claim in claims:
        row = {"claim_id": claim["id"], "claim": deepcopy(claim), "reasons": [],
               "existing_statement_ids": [], "status": "PENDING"}
        reasons = row["reasons"]
        decision = by_id.get(claim["id"])
        if decision:
            if _bytes(decision.get("binding")) != _bytes(claim):
                reasons.append("APPROVAL_BINDING_MISMATCH" if decision.get("decision") == "APPROVE"
                               else "DECISION_BINDING_MISMATCH")
            if decision.get("decision") not in ("APPROVE", "REJECT", "DEFER"):
                reasons.append("INVALID_HUMAN_DECISION")
            if not metadata_valid:
                reasons.append("MISSING_HUMAN_REVIEW_METADATA")
            if decisions.get("reviewer") == READER:
                reasons.append("REVIEWER_EQUALS_SOURCE_READER")
        try:
            if (claim.get("scope") != SCOPE or claim.get("statement_type") != "deck.venue_present" or
                    not isinstance(claim.get("value"), list) or not claim["value"] or
                    not all(type(v) is int for v in claim["value"])):
                raise BatchError("UNSUPPORTED_OBSERVATION_SCOPE")
            if claim["target_vessel"] != vessel or slug not in claim["entity_id"].casefold().split(":"):
                raise BatchError("CLAIM_VESSEL_MISMATCH")
            artifact = ws.registry.get(claim["artifact_id"])
            if artifact.sha256 != claim["artifact_sha256"]:
                raise BatchError("ARTIFACT_SHA_MISMATCH")
            if not claim["source_version"] or artifact.version != claim["source_version"]:
                raise BatchError("SOURCE_VERSION_MISMATCH")
            if not ws.registry.artifact_establishes_vessel(artifact.artifact_id, vessel):
                raise BatchError("ARTIFACT_NOT_ATTRIBUTED_TO_VESSEL")
            if len([a for a in ws.registry.list_all() if a.sha256 == artifact.sha256]) != 1:
                raise BatchError("AMBIGUOUS_DUPLICATE_ARTIFACT")
            path = ws.registry.resolve_path(artifact.artifact_id)
            if not path:
                raise BatchError("HELD_ARTIFACT_UNAVAILABLE")
            question = ws.questions.get(claim["question_id"])
            if question.statement_type != claim["statement_type"] or not question.can_be_supported_by(artifact.document_class):
                raise BatchError("QUESTION_SOURCE_CLASS_MISMATCH")
            authority.check(claim["statement_type"], artifact.document_class)
            _document_reading(path, claim)
            key = _bytes([claim["entity_id"], claim["question_id"], claim["value"], artifact.sha256])
            if key in seen:
                raise BatchError("DUPLICATE_SELECTED_CLAIM")
            seen.add(key)
            for existing in ws.editor.all():
                if existing.entity_id == claim["entity_id"] and existing.question_id == claim["question_id"]:
                    row["existing_statement_ids"].append(existing.statement_id)
                    if values_disagree(existing.value, claim["value"]):
                        reasons.append("CONTRADICTORY_EXISTING_CLAIM")
                    elif existing.artifact_id == artifact.artifact_id:
                        reasons.append("DUPLICATE_EXISTING_SOURCE_CLAIM")
            sources[artifact.artifact_id] = {
                "artifact_id": artifact.artifact_id, "sha256": artifact.sha256,
                "version": artifact.version, "vessel_attribution": vessel,
                "document_authenticity": "NOT_INDEPENDENTLY_VERIFIED",
                "origin_limit": batch["origin_limit"],
                "use_permission": authority.DOCUMENT_CLASSES[artifact.document_class].use_permission.value,
                "artwork_redistribution": "NOT_AUTHORIZED",
                "potential_duplicate_ids": [a.artifact_id for a in ws.registry.list_all()
                    if a.artifact_id != artifact.artifact_id and a.filename == artifact.filename],
            }
        except (KeyError, ValueError, TypeError, OSError) as exc:
            reasons.append(str(exc))
        if reasons:
            row["status"] = "BLOCKED"
        elif decision and decision["decision"] == "APPROVE":
            row["status"] = "READY"
        elif decision and decision["decision"] == "REJECT":
            row["status"] = "REJECTED"
        rows.append(row)
    return {"claims": rows, "sources": list(sources.values()),
            "unused_decision_ids": sorted(set(by_id) - {c["id"] for c in claims})}


def process_private_batch(source_root, batch, decisions, output_dir):
    """Run canonical APIs only in a self-created temporary copy. No apply mode."""
    root, output = Path(source_root).resolve(), Path(output_dir).resolve()
    if output == root or root in output.parents:
        raise BatchError("OUTPUT_INSIDE_SOURCE")
    if output.exists():
        raise BatchError("OUTPUT_EXISTS")
    # Reject any Git checkout destination, including a different worktree.
    if any((p / ".git").exists() for p in [output, *output.parents]):
        raise BatchError("OUTPUT_INSIDE_GIT_CHECKOUT")
    protected = {name: _files(root / name) for name in ("evidence", "knowledge")}
    today = datetime.now(timezone.utc).date().isoformat()
    with tempfile.TemporaryDirectory(prefix="timonelo-private-batch-") as temporary:
        fixture = Path(temporary)
        shutil.copytree(root / "evidence", fixture / "evidence")
        if _files(fixture / "evidence") != protected["evidence"]:
            raise BatchError("SOURCE_CHANGED_DURING_COPY")
        ws = _workspace(fixture)
        original = _states(ws)
        art2 = ws.registry.get("ART-0002").to_dict()
        plan = _inspect_batch(root, batch, decisions, ws)
        for row in plan["claims"]:
            if row["status"] != "READY":
                continue
            claim = row["claim"]
            fingerprint = _hash(claim)
            locator = (f"{claim['artifact_id']}; source edition {claim['source_version']}; physical page {claim['page']}; "
                       f"{claim['locator']}; edition-specific observation, not current operations")
            event = ws.events.append(EvidenceEvent(
                event_id="EVT-BATCH-" + fingerprint[:20], artifact_sha256=claim["artifact_sha256"],
                locator=locator, entity_id=claim["entity_id"], question_id=claim["question_id"],
                observed_value=claim["value"], observed_by=READER, observed_on=today,
                notes=f"Actual registered-PDF reading; claim {claim['id']}; binding SHA-256 {fingerprint}."))
            statement = ws.editor.create(
                entity_id=claim["entity_id"], question_id=claim["question_id"],
                statement_type=claim["statement_type"], value=claim["value"],
                artifact_id=claim["artifact_id"], locator=locator, page=claim["page"],
                read_by=READER, read_on=today, evidence_event_ids=(event.event_id,),
                note=f"{claim['id']}; {SCOPE}; binding {fingerprint}; {batch['origin_limit']}")
            row.update(statement_id=statement.statement_id, event_id=event.event_id,
                       claim_sha256=fingerprint, evidence_event=event.to_dict())
            ws.editor.set_evidence_condition(statement.statement_id, EvidenceCondition.SUPPORTED,
                actor=READER, occurred_on=today, note="Registered digest, source region and exact claim binding verified.")
            ws.editor.transition(statement.statement_id, HumanReviewState.UNDER_REVIEW,
                                 actor=READER, occurred_on=today, note="Submit the actually recorded owner decision.")
            ws.editor.transition(statement.statement_id, HumanReviewState.APPROVED,
                actor=decisions["reviewer"], occurred_on=decisions["review_date"],
                note=f"{claim['id']}; binding {fingerprint}; {decisions['owner_review_statement']}")
            row.update(review_entry=next(e.to_dict() for e in ws.reviews.history(statement.statement_id)
                                        if e.to_state == "APPROVED"),
                       review_history=[e.to_dict() for e in ws.reviews.history(statement.statement_id)])
            try:
                # Actor is the genuine human principal who explicitly authorized
                # processing, not a fabricated second reviewer or renamed reader.
                ws.editor.publish(statement.statement_id, actor=decisions["reviewer"],
                    occurred_on=today, note=decisions["publication_processing_authorization"])
            except EditorError as exc:
                row.update(status="BLOCKED", reasons=[str(exc)],
                           statement_record=ws.editor.get(statement.statement_id).to_dict())
                continue
            current = ws.editor.get(statement.statement_id)
            verdict = ws.editor.authority.evaluate(current)
            answer = ws.engine.answer(current.entity_id, current.question_id, as_of=today)
            if not verdict.admitted or not answer.known or answer.provenance.statement_id != current.statement_id:
                raise BatchError("POST_PUBLICATION_AUTHORITY_OR_TRUTH_MISMATCH")
            row.update(status="ADMITTED", truth_engine_known=True,
                statement_record=current.to_dict(),
                source_trace=answer.provenance.__dict__,
                review_history=[e.to_dict() for e in ws.reviews.history(current.statement_id)])
        after = _states(ws)
        if {sid: after[sid] for sid in original} != original:
            raise BatchError("UNRELATED_STATEMENT_AUTHORITY_CHANGED")
        if ws.registry.get("ART-0002").to_dict() != art2:
            raise BatchError("ART0002_CHANGED")
        catalog = json.loads((root / "frontend/src/passenger/fleetCatalog.json").read_text(encoding="utf8"))
        snapshot = make_snapshot(project_fleet(ws, catalog, today))
    if protected != {name: _files(root / name) for name in protected}:
        raise BatchError("SOURCE_CHECKOUT_CHANGED")
    rows = plan["claims"]
    result = {"mode": "PRIVATE_COPY_ONLY", **plan,
        "counts": {key: sum(r["status"] == status for r in rows) for key, status in
                   [("admitted", "ADMITTED"), ("blocked", "BLOCKED"), ("pending", "PENDING"), ("rejected", "REJECTED")]},
        "original_statement_count": len(original), "original_states_and_authority_unchanged": True,
        "source_unchanged": True, "art2_unchanged": True,
        "human_approvals_recorded": sum(r.get("review_entry", {}).get("to_state") == "APPROVED" for r in rows),
        "decision_record_sha256": _hash(decisions), "source_artwork_exported": False,
        "remote_ingestion_performed": False, "canonical_apply_performed": False}
    output.mkdir(parents=True)
    canonical_dump(result, str(output / "result.json"))
    canonical_dump(decisions, str(output / "decision-records.json"))
    canonical_dump(snapshot, str(output / "private.snapshot.json"))
    exceptions = [r for r in rows if r["status"] != "ADMITTED"]
    lines = ["# Private Evidence Factory batch", "", "No canonical apply or public publication.",
             "", "## Unresolved exceptions"]
    lines += ([f"- {r['claim_id']}: {r['status']} - {', '.join(r['reasons']) or 'No matching human APPROVE decision.'}" for r in exceptions]
              if exceptions else ["None. All selected claims passed the existing gates with the recorded human decisions."])
    lines += ["", "## Selected claims", "", "| ID | Claim | Source / locator | Decision result |",
              "|---|---|---|---|"]
    for row in rows:
        c = row["claim"]
        lines.append(f"| {c['id']} | {c['exact_claim']} | {c['artifact_id']} / {c['locator']} | {row['status']} |")
    (output / "review-package.md").write_text("\n".join(lines) + "\n", encoding="utf8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = process_private_batch(args.root, json.loads(args.batch.read_text(encoding="utf8")),
                                   json.loads(args.decisions.read_text(encoding="utf8")), args.output)
    print(json.dumps(result["counts"]))
    return 1 if result["counts"]["blocked"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
