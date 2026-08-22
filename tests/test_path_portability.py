"""
Tests for Legacy Hygiene & Path Portability.
Governed by ADR-0002, ADR-0003, and P0 Path Portability Invariants.
"""

import ast
import os
from pathlib import Path
import subprocess
import sys
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_obsolete_meraviglia_ingest_script_is_deleted():
    """Ensure obsolete scripts/ingest_msc_meraviglia.py cannot be found or imported."""
    obsolete_path = REPO_ROOT / "scripts" / "ingest_msc_meraviglia.py"
    assert not obsolete_path.exists(), f"Obsolete script still exists: {obsolete_path}"

    with pytest.raises(ModuleNotFoundError):
        import scripts.ingest_msc_meraviglia  # noqa: F401


def test_no_hardcoded_user_paths_in_scripts_and_src():
    """Ensure no hardcoded user paths or agent brain directories exist in python files."""
    forbidden_patterns = [
        "C:\\Users",
        "C:/Users",
        "file:///C:",
        ".gemini/antigravity/brain",
    ]

    scanned_dirs = [REPO_ROOT / "scripts", REPO_ROOT / "src", REPO_ROOT / "knowledge" / "pipeline"]
    violations = []

    for s_dir in scanned_dirs:
        if not s_dir.exists():
            continue
        for file_path in s_dir.rglob("*.py"):
            text = file_path.read_text(encoding="utf-8")
            for pattern in forbidden_patterns:
                if pattern in text:
                    violations.append(f"{file_path.relative_to(REPO_ROOT)}: contains forbidden pattern '{pattern}'")

    assert not violations, f"Forbidden hardcoded absolute paths found:\n" + "\n".join(violations)


def test_no_hardcoded_file_uris_in_active_documentation():
    """Ensure pipeline README and geometry reports do not contain local file:///C: URIs."""
    docs_to_check = [
        REPO_ROOT / "knowledge" / "pipeline" / "README.md",
        REPO_ROOT / "knowledge" / "reports" / "geometry_coverage_report.md",
        REPO_ROOT / "evidence" / "README.md",
    ]

    violations = []
    for doc in docs_to_check:
        if doc.exists():
            text = doc.read_text(encoding="utf-8")
            if "file:///C:" in text:
                violations.append(f"{doc.relative_to(REPO_ROOT)}: contains file:///C: link")

    assert not violations, f"Machine-specific URIs found in documentation:\n" + "\n".join(violations)


def test_build_semantic_vessel_fails_closed_on_missing_input(tmp_path):
    """Ensure build_semantic_vessel.py fails closed with clear error when input dir is missing."""
    script_path = REPO_ROOT / "scripts" / "build_semantic_vessel.py"
    non_existent = tmp_path / "non_existent_bellissima"

    result = subprocess.run(
        [sys.executable, str(script_path), "--bellissima-dir", str(non_existent), "--out-dir", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "FileNotFoundError" in result.stderr or "not found" in result.stderr


def test_generate_living_deckplans_fails_closed_on_missing_input(tmp_path):
    """Ensure generate_living_deckplans.py fails closed with clear error when PDF or graph is missing."""
    script_path = REPO_ROOT / "scripts" / "generate_living_deckplans.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--pdf-path",
            str(tmp_path / "missing.pdf"),
            "--graph-path",
            str(tmp_path / "missing.json"),
            "--out-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "FileNotFoundError" in result.stderr or "not found" in result.stderr


def test_extract_spatial_geometry_fails_closed_on_missing_pdf(tmp_path):
    """Ensure extract_spatial_geometry.py fails closed when PDF is missing."""
    script_path = REPO_ROOT / "scripts" / "extract_spatial_geometry.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--pdf-path",
            str(tmp_path / "missing_bellissima.pdf"),
            "--geometry-dir",
            str(tmp_path / "geometry"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "FileNotFoundError" in result.stderr or "not found" in result.stderr


def test_scripts_resolve_repo_root_regardless_of_cwd(tmp_path):
    """Ensure script REPO_ROOT resolution is independent of working directory."""
    from scripts import build_semantic_vessel, generate_living_deckplans, extract_spatial_geometry

    assert build_semantic_vessel.REPO_ROOT == REPO_ROOT
    assert generate_living_deckplans.REPO_ROOT == REPO_ROOT
    assert extract_spatial_geometry.REPO_ROOT == REPO_ROOT
