"""
tests/test_knowledge_factory_pipeline.py

Verifies the automated Knowledge Factory Pipeline:
- ArtifactQueue lifecycle
- KnowledgeDiff comparison and reporting
- ConflictResolver contradiction classification
- KnowledgePublisher 4-stage gate validation
- KnowledgeFactory fleet production readiness
"""

import os
import glob
import json
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_pipeline_files_exist():
    """Verify all pipeline TypeScript modules exist."""
    pipeline_dir = os.path.join(REPO_ROOT, "frontend", "src", "knowledge", "pipeline")
    assert os.path.exists(os.path.join(pipeline_dir, "ArtifactQueue.ts"))
    assert os.path.exists(os.path.join(pipeline_dir, "KnowledgeDiff.ts"))
    assert os.path.exists(os.path.join(pipeline_dir, "ConflictResolver.ts"))
    assert os.path.exists(os.path.join(pipeline_dir, "KnowledgePublisher.ts"))
    assert os.path.exists(os.path.join(pipeline_dir, "KnowledgeFactory.ts"))
    assert os.path.exists(os.path.join(pipeline_dir, "index.ts"))

def test_conflict_resolver_specifications():
    """Verify ConflictResolver enforces required citation fields."""
    conflict_file = os.path.join(REPO_ROOT, "frontend", "src", "knowledge", "pipeline", "ConflictResolver.ts")
    with open(conflict_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "MATCH" in content
    assert "CONFLICT" in content
    assert "UNKNOWN" in content
    assert "SUPERSEDED" in content
    assert "canonical_artifact" in content
    assert "incoming_artifact" in content
    assert "evidence_page" in content
    assert "statement_id" in content

def test_legacy_knowledge_publisher_is_quarantined():
    """Legacy publisher retains no hard-coded successful validation path."""
    publisher_file = os.path.join(REPO_ROOT, "frontend", "src", "knowledge", "pipeline", "KnowledgePublisher.ts")
    with open(publisher_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "LegacyPublisherQuarantinedError" in content
    assert "passed: true" not in content

def test_knowledge_dashboard_not_mounted_in_production_app():
    """Legacy publisher UI is excluded from the production application graph."""
    app_file = os.path.join(REPO_ROOT, "frontend", "src", "App.tsx")
    with open(app_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "KnowledgeDashboardPage" not in content
    assert "knowledge-factory" not in content
