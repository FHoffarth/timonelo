#!/usr/bin/env python3
"""Validate the canonical Timonelo knowledge repository."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


FILENAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\.md")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
METADATA_RE = re.compile(r"^-\s+([^:]+):\s*(.*)$")
RECORD_FOLDERS = {
    "cruise-lines",
    "ship-classes",
    "ships",
    "cabin-types",
    "structural-features",
    "ship-systems",
    "operations",
    "regulations",
    "glossary",
    "sources",
}
ENTITY_FOLDERS = RECORD_FOLDERS - {"glossary", "sources"}
ROOT_FILES = {"README.md", "CONTRIBUTING.md"}
TEMPLATE_FILES = {
    "KNOWLEDGE_RECORD_TEMPLATE.md",
    "SOURCE_TEMPLATE.md",
    "GLOSSARY_TEMPLATE.md",
    "ENTITY_TEMPLATE.md",
}
SCHEMAS = {
    "source": {
        "id": "Source ID",
        "metadata": (
            "Source ID", "Title", "Publisher", "URL", "Published date",
            "Accessed date", "Source type", "Review status",
        ),
        "headings": ("Metadata", "Scope", "Supported Claims", "Limitations"),
    },
    "glossary": {
        "id": "Term ID",
        "metadata": ("Term ID", "Canonical term", "Status", "Last reviewed"),
        "headings": ("Metadata", "Definition", "Aliases", "Usage Notes", "Sources"),
    },
    "entity": {
        "id": "Entity ID",
        "metadata": ("Entity ID", "Canonical name", "Entity type", "Status", "Last reviewed"),
        "headings": ("Metadata", "Description", "Attributes", "Relationships", "Sources", "Review Notes"),
    },
    "knowledge": {
        "id": "ID",
        "metadata": ("ID", "Canonical name", "Record type", "Status", "Last reviewed"),
        "headings": ("Metadata", "Summary", "Claims", "Relationships", "Sources", "Review Notes"),
    },
}


@dataclass(frozen=True, order=True)
class Finding:
    code: str
    path: str
    message: str


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def add(findings: list[Finding], code: str, path: Path, root: Path, message: str) -> None:
    findings.append(Finding(code, relative(path, root), message))


def parse_document(path: Path, root: Path, findings: list[Finding]) -> tuple[list[str], dict[str, str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        add(findings, "MARKDOWN_STRUCTURE", path, root, f"cannot read UTF-8 Markdown: {exc}")
        return [], {}

    headings: list[tuple[int, str]] = []
    metadata: dict[str, str] = {}
    first_content = next((line for line in lines if line.strip()), "")
    in_metadata = False

    for number, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if match:
            level, title = len(match.group(1)), match.group(2).strip()
            headings.append((level, title))
            in_metadata = level == 2 and title == "Metadata"
            continue
        if line.startswith("#") and line.strip():
            add(findings, "MARKDOWN_STRUCTURE", path, root, f"invalid heading syntax on line {number}")
        if in_metadata:
            item = METADATA_RE.match(line)
            if item:
                key, value = item.group(1).strip(), item.group(2).strip()
                if key in metadata:
                    add(findings, "MARKDOWN_STRUCTURE", path, root, f"duplicate metadata key '{key}'")
                metadata[key] = value
            elif line.strip() and not line.startswith("-"):
                in_metadata = False

    if not first_content.startswith("# "):
        add(findings, "MARKDOWN_STRUCTURE", path, root, "first content line must be one level-one heading")
    if sum(level == 1 for level, _ in headings) != 1:
        add(findings, "MARKDOWN_STRUCTURE", path, root, "document must contain exactly one level-one heading")
    for previous, current in zip(headings, headings[1:]):
        if current[0] > previous[0] + 1:
            add(findings, "MARKDOWN_STRUCTURE", path, root, f"heading level jumps from H{previous[0]} to H{current[0]}")
    titles = [title for level, title in headings if level == 2]
    if len(titles) != len(set(titles)):
        add(findings, "MARKDOWN_STRUCTURE", path, root, "duplicate level-two heading")
    return titles, metadata


def record_kind(metadata: dict[str, str]) -> str | None:
    matches = [kind for kind, schema in SCHEMAS.items() if schema["id"] in metadata]
    return matches[0] if len(matches) == 1 else None


def validate_placement(path: Path, root: Path, kind: str | None, findings: list[Finding]) -> None:
    rel = path.relative_to(root)
    folder = rel.parts[0] if len(rel.parts) > 1 else ""
    if len(rel.parts) != 2 or folder not in RECORD_FOLDERS:
        add(findings, "FOLDER_PLACEMENT", path, root, "record must be placed directly in an approved record folder")
        return
    if kind == "source" and folder != "sources":
        add(findings, "FOLDER_PLACEMENT", path, root, "source records belong in sources/")
    elif kind == "glossary" and folder != "glossary":
        add(findings, "FOLDER_PLACEMENT", path, root, "glossary records belong in glossary/")
    elif kind == "entity" and folder not in ENTITY_FOLDERS:
        add(findings, "FOLDER_PLACEMENT", path, root, "entity records belong in an entity record folder")
    elif kind not in {"source", "glossary", "entity", "knowledge"}:
        add(findings, "FOLDER_PLACEMENT", path, root, "record type cannot be determined from metadata")


def validate(root: Path) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    identifiers: dict[str, list[Path]] = defaultdict(list)
    source_identifiers: dict[str, list[Path]] = defaultdict(list)
    records = 0

    if not root.is_dir():
        return [Finding("KNOWLEDGE_ROOT", ".", f"directory does not exist: {root}")], 0

    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if len(rel.parts) == 1 and path.name in ROOT_FILES:
            parse_document(path, root, findings)
            continue
        if rel.parts[0] == "templates":
            if len(rel.parts) != 2 or path.name not in TEMPLATE_FILES:
                add(findings, "FOLDER_PLACEMENT", path, root, "unexpected file in templates/")
            parse_document(path, root, findings)
            continue
        if path.name == "README.md":
            parse_document(path, root, findings)
            continue

        records += 1
        if not FILENAME_RE.fullmatch(path.name):
            add(findings, "INVALID_FILENAME", path, root, "use a lowercase kebab-case .md filename")
        headings, metadata = parse_document(path, root, findings)
        kind = record_kind(metadata)
        validate_placement(path, root, kind, findings)
        if kind is None:
            add(findings, "MISSING_METADATA", path, root, "record must contain exactly one recognized ID field")
            continue

        schema = SCHEMAS[kind]
        for key in schema["metadata"]:
            if not metadata.get(key, "").strip():
                add(findings, "MISSING_METADATA", path, root, f"missing value for '{key}'")
        for heading in schema["headings"]:
            if heading not in headings:
                add(findings, "MISSING_HEADING", path, root, f"missing mandatory heading '## {heading}'")

        identifier = metadata.get(schema["id"], "").strip().casefold()
        if identifier:
            target = source_identifiers if kind == "source" else identifiers
            target[identifier].append(path)

    for identifier, paths in sorted(identifiers.items()):
        if len(paths) > 1:
            joined = ", ".join(relative(path, root) for path in paths)
            for path in paths:
                add(findings, "DUPLICATE_ID", path, root, f"ID '{identifier}' also appears in: {joined}")
    for identifier, paths in sorted(source_identifiers.items()):
        if len(paths) > 1:
            joined = ", ".join(relative(path, root) for path in paths)
            for path in paths:
                add(findings, "DUPLICATE_SOURCE_ID", path, root, f"source ID '{identifier}' also appears in: {joined}")
    return sorted(set(findings)), records


def main(argv: list[str] | None = None) -> int:
    default_root = Path(__file__).resolve().parents[1] / "knowledge"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--knowledge-dir", type=Path, default=default_root)
    args = parser.parse_args(argv)

    findings, records = validate(args.knowledge_dir.resolve())
    if findings:
        print("Knowledge validation: FAIL")
        print(f"Checked {records} record(s); found {len(findings)} issue(s).")
        for finding in findings:
            print(f"[{finding.code}] {finding.path}: {finding.message}")
        return 1

    print("Knowledge validation: PASS")
    print(f"Checked {records} record(s); no issues found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
