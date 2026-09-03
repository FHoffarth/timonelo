"""Fixtures shared across the evidence suites."""

import pytest

from tests.evidence_fixtures import RuleStore


@pytest.fixture
def rule_store():
    """A resolvable rule store, installed for the duration of one test.

    Publication admission fails closed on any INFERRED statement whose
    `rule_hash` cannot be resolved, and this repository holds no rules. Tests
    whose subject is downstream of inference install this so the thing they are
    actually testing is what fails.
    """
    store = RuleStore().install()
    try:
        yield store
    finally:
        store.uninstall()
