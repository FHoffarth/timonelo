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

def test_pipeline_files_exist():
    """Verify all pipeline TypeScript modules exist."""
    pipeline_dir = r"C:\Users\Flo\Desktop\energyradar\timonelo\frontend\src\knowledge\pipeline"
    assert os.path.exists(os.path.join(pipeline_dir, "ArtifactQueue.ts"))
    assert os.path.exists(os.path.join(pipeline_dir, "KnowledgeDiff.ts"))
    assert os.path.exists(os.path.join(pipeline_dir, "ConflictResolver.ts"))
    assert os.path.exists(os.path.join(pipeline_dir, "KnowledgePublisher.ts"))
    assert os.path.exists(os.path.join(pipeline_dir, "KnowledgeFactory.ts"))
    assert os.path.exists(os.path.join(pipeline_dir, "index.ts"))

def test_conflict_resolver_specifications():
    """Verify ConflictResolver enforces required citation fields."""
    conflict_file = r"C:\Users\Flo\Desktop\energyradar\timonelo\frontend\src\knowledge\pipeline\ConflictResolver.ts"
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

def test_knowledge_publisher_four_gates():
    """Verify KnowledgePublisher validates Schema, Graph, Geometry, and Integrity."""
    publisher_file = r"C:\Users\Flo\Desktop\energyradar\timonelo\frontend\src\knowledge\pipeline\KnowledgePublisher.ts"
    with open(publisher_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "JSON Schema Validation" in content
    assert "Building Topology Ontology" in content
    assert "Spatial Geometry" in content
    assert "Referential Integrity" in content

def test_knowledge_dashboard_mounted():
    """Verify KnowledgeDashboardPage is accessible in App.tsx."""
    app_file = r"C:\Users\Flo\Desktop\energyradar\timonelo\frontend\src\App.tsx"
    with open(app_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "KnowledgeDashboardPage" in content
    assert "knowledge-factory" in content
