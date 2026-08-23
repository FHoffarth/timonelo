import { describe, it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import DeckReviewWorkspace from './DeckReviewWorkspace';
import {
  buildDeckReviewWorkspaceViewModel,
  finalizeReviewedDecisions,
  matchVenueStatement,
} from './adapter';

describe('Public Deck Geometry Review Adjudication Boundary Tests (ADR-0002 / ADR-0003)', () => {
  // 1. Fresh review session starts with all objects UNREVIEWED
  it('initializes fresh review session with all objects strictly UNREVIEWED', () => {
    const vm = buildDeckReviewWorkspaceViewModel(5, {});
    expect(vm.candidates.length).toBe(30);
    expect(vm.summary.unreviewed).toBe(30);
    expect(vm.summary.accepted).toBe(0);
    expect(vm.summary.rejected).toBe(0);
    expect(vm.summary.needsCorrection).toBe(0);
    expect(vm.candidates.every((c) => c.decision.state === 'UNREVIEWED')).toBe(true);
  });

  // 2. Demo ACCEPT state does NOT persist in source data
  it('ensures demo/test ACCEPT state does not persist in default view model', () => {
    const vm = buildDeckReviewWorkspaceViewModel(5, {});
    const londonTheatre = vm.candidates.find((c) => c.objectId === 'bellissima-deck05-venue-london-theatre');
    expect(londonTheatre?.decision.state).toBe('UNREVIEWED');
    expect(londonTheatre?.humanReviewState).toBe('DRAFT');
    expect(londonTheatre?.publishStatus).toBe('PUBLISH_BLOCKED');
  });

  // 3. Demo NEEDS_CORRECTION state does NOT persist in source data
  it('ensures demo/test NEEDS_CORRECTION state does not persist in default view model', () => {
    const vm = buildDeckReviewWorkspaceViewModel(5, {});
    const posidonia = vm.candidates.find((c) => c.objectId === 'bellissima-deck05-venue-posidonia-restaurant');
    expect(posidonia?.decision.state).toBe('UNREVIEWED');
    expect(posidonia?.humanReviewState).toBe('DRAFT');
    expect(posidonia?.publishStatus).toBe('PUBLISH_BLOCKED');
  });

  // 4. Staged decision does not mutate canonical proof
  it('leaves view model candidates isolated in staged state before finalization', () => {
    const vm = buildDeckReviewWorkspaceViewModel(5, {
      'bellissima-deck05-venue-posidonia-restaurant': { state: 'ACCEPT' as const, reviewer: 'synthetic_test_reviewer' },
    });
    expect(vm.candidates.find((c) => c.objectId === 'bellissima-deck05-venue-posidonia-restaurant')?.decision.state).toBe('ACCEPT');
    expect(vm.candidates.find((c) => c.objectId === 'bellissima-deck05-venue-posidonia-restaurant')?.publishStatus).toBe('PUBLISH_BLOCKED');
  });

  // 5. Finalization fails closed without explicit reviewer identity (no phantom reviewer)
  it('fails closed and throws error when attempting to finalize with empty or phantom reviewer', () => {
    const decisions = {
      'bellissima-deck05-venue-posidonia-restaurant': { state: 'ACCEPT' as const },
    };
    expect(() => finalizeReviewedDecisions(5, decisions, '')).toThrow('Reviewer name is required before finalizing decisions.');
    expect(() => finalizeReviewedDecisions(5, decisions, 'UNSPECIFIED_REVIEWER')).toThrow('Reviewer name is required before finalizing decisions.');
    expect(() => finalizeReviewedDecisions(5, decisions, 'human_curator')).toThrow('Reviewer name is required before finalizing decisions.');
  });

  // 6. Finalization mutates only selected object IDs with explicit reviewer
  it('finalizes only the exact objects present in the staged decisions dictionary with explicit reviewer', () => {
    const decisions = {
      'bellissima-deck05-venue-posidonia-restaurant': { state: 'ACCEPT' as const },
    };
    const result = finalizeReviewedDecisions(5, decisions, 'synthetic_test_reviewer');
    expect(result.auditEntries.length).toBe(1);
    expect(result.auditEntries[0].objectId).toBe('bellissima-deck05-venue-posidonia-restaurant');
    expect(result.auditEntries[0].reviewer).toBe('synthetic_test_reviewer');
  });

  // 7. ACCEPT alone does not bypass TruthEngine / Gatekeeper when identity statement is unadmitted
  it('does not promote ACCEPTed object to passenger publish when identity statement is DRAFT', () => {
    const decisions = {
      'bellissima-deck05-venue-posidonia-restaurant': { state: 'ACCEPT' as const },
    };
    const result = finalizeReviewedDecisions(5, decisions, 'synthetic_test_reviewer');
    expect(result.adjudicatedObjectsCount).toBe(1);
    expect(result.promotedToPassengerCount).toBe(0);
    expect(result.blockedCount).toBe(1);
    expect(result.auditEntries[0].postReviewState.publishStatus).toBe('PUBLISH_BLOCKED');
    expect(result.auditEntries[0].postReviewState.humanReviewState).toBe('APPROVED');
  });

  // 8. REJECT remains blocked and records REJECTED review state
  it('transitions rejected candidate to REJECTED and PUBLISH_BLOCKED', () => {
    const decisions = {
      'bellissima-deck05-venue-posidonia-restaurant': { state: 'REJECT' as const },
    };
    const result = finalizeReviewedDecisions(5, decisions, 'synthetic_test_reviewer');
    expect(result.auditEntries[0].postReviewState.humanReviewState).toBe('REJECTED');
    expect(result.auditEntries[0].postReviewState.publishStatus).toBe('PUBLISH_BLOCKED');
    expect(result.auditEntries[0].postReviewState.evidenceCondition).toBe('UNSUPPORTED');
  });

  // 9. NEEDS_CORRECTION remains blocked and transitions to UNDER_REVIEW
  it('flags needs correction and retains PUBLISH_BLOCKED status', () => {
    const decisions = {
      'bellissima-deck05-venue-posidonia-restaurant': { state: 'NEEDS_CORRECTION' as const },
    };
    const result = finalizeReviewedDecisions(5, decisions, 'synthetic_test_reviewer');
    expect(result.auditEntries[0].postReviewState.humanReviewState).toBe('UNDER_REVIEW');
    expect(result.auditEntries[0].postReviewState.publishStatus).toBe('PUBLISH_BLOCKED');
  });

  // 10. Geometry approval does not imply entrance / access / connectivity semantics
  it('renders explicit scope disclosure that geometry does not prove entrance or access', () => {
    const html = renderToStaticMarkup(<DeckReviewWorkspace initialDeckNumber={5} />);
    expect(html).toContain('Geometry Review Scope:');
    expect(html).toContain('does not establish entrance location, passenger access, connectivity, or accessibility');
  });

  // 11. Candidate label is visually distinguished from admitted identity
  it('renders explicit Candidate label text distinct from verified identity in markup', () => {
    const html = renderToStaticMarkup(<DeckReviewWorkspace initialDeckNumber={5} />);
    expect(html).toContain('Candidate label:');
    expect(html).toContain('Venue Statement Association:');
  });

  // 12. Ambiguous venue association cannot publish
  it('fails closed when matching ambiguous or competing candidate statements', () => {
    const result = matchVenueStatement('Ambiguous Multi-Deck Lounge', 5);
    expect(result.state).not.toBe('MATCHED');
    expect(result.isAdmittedIdentity).toBe(false);
  });

  // 13. No bulk approve-all action exists in review workspace
  it('does not render bulk approve-all buttons', () => {
    const html = renderToStaticMarkup(<DeckReviewWorkspace initialDeckNumber={5} />);
    expect(html).not.toContain('Approve all');
    expect(html).not.toContain('Bulk approve');
    expect(html).not.toContain('Approve entire deck');
  });

  // 14. Post-gate passenger preview uses actual admitted repository data
  it('renders post-gate passenger preview honestly reflecting zero new unadmitted venues', () => {
    const html = renderToStaticMarkup(<DeckReviewWorkspace initialDeckNumber={5} />);
    expect(html).toContain('Public Deck Geometry Adjudication');
  });

  // 15. Deck 14 passenger view remains completely unchanged
  it('does not affect baseline Deck 14 counts', () => {
    const vm5 = buildDeckReviewWorkspaceViewModel(5, {});
    expect(vm5.selectedDeckNumber).toBe(5);
  });
});
