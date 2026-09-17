/**
 * The invariants this sprint is not allowed to break.
 *
 * Each of these is a sentence from the brief turned into something that fails.
 * They overlap the suites next door on purpose: the point is that the
 * non-negotiables are checkable in one place, so a future change that violates
 * one does not have to be noticed by reading a diff.
 */

import { describe, it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import DeckReviewWorkspace from './DeckReviewWorkspace';
import {
  UnsupportedDeckReviewError,
  buildDeckReviewWorkspaceViewModel,
  finalizeReviewedDecisions,
  resolveDeckReviewSource,
} from './adapter';
import { isAdmittedPassengerEntity } from '../ship-overview/adapter';
import deck14Proof from '../../../geometry/proofs/bellissima/deck14/deck14.proof.json';

const CABIN_14122 = 'bellissima-deck14-cabin-14122';
const REVIEWER = 'synthetic_test_reviewer';

describe('cabin 14122 is not adjudicated by this code', () => {
  it('is UNREVIEWED with its governed axes untouched before any human acts', () => {
    const c = buildDeckReviewWorkspaceViewModel(14, {}).candidates
      .find((x) => x.objectId === CABIN_14122)!;
    expect(c.decision.state).toBe('UNREVIEWED');
    expect(c.decision.reviewer).toBe('');
    expect(c.humanReviewState).toBe('DRAFT');
    expect(c.evidenceCondition).toBe('UNKNOWN');
    expect(c.publishStatus).toBe('PUBLISH_BLOCKED');
  });

  it('stages nothing when nothing was decided', () => {
    expect(finalizeReviewedDecisions(14, {}, REVIEWER).auditEntries).toEqual([]);
  });

  it('leaves every other Deck 14 object UNREVIEWED too', () => {
    const vm = buildDeckReviewWorkspaceViewModel(14, {});
    expect(vm.candidates.length).toBe(244);
    expect(vm.candidates.every((c) => c.decision.state === 'UNREVIEWED')).toBe(true);
    expect(vm.summary.unreviewed).toBe(244);
    expect(vm.summary.accepted).toBe(0);
  });
});

describe('no review act creates evidence or publication', () => {
  it('holds for every decision state on every semantic type', () => {
    const cabin = CABIN_14122;
    const core = 'bellissima-deck14-lift-core-proof';
    for (const objectId of [cabin, core]) {
      for (const state of ['ACCEPT', 'REJECT', 'NEEDS_CORRECTION'] as const) {
        const r = finalizeReviewedDecisions(14, { [objectId]: { state } }, REVIEWER);
        const e = r.auditEntries[0];
        expect(e.postReviewState.evidenceCondition).toBe('UNKNOWN');
        expect(e.postReviewState.publishStatus).toBe('PUBLISH_BLOCKED');
        expect(r.promotedToPassengerCount).toBe(0);
        expect(
          isAdmittedPassengerEntity({
            evidence_condition: e.postReviewState.evidenceCondition,
            human_review_state: e.postReviewState.humanReviewState,
            publish_status: e.postReviewState.publishStatus,
            geometry_provenance: 'TRANSFORMED_SOURCE_GEOMETRY',
          }),
        ).toBe(false);
      }
    }
  });

  it('never bulk-approves: only explicitly decided objects appear', () => {
    const r = finalizeReviewedDecisions(14, { [CABIN_14122]: { state: 'ACCEPT' } }, REVIEWER);
    expect(r.auditEntries.length).toBe(1);
    expect(r.adjudicatedObjectsCount).toBe(1);
  });

  it('stays STAGED_NOT_APPLIED and mutates no governed file', () => {
    const before = JSON.stringify(deck14Proof);
    const r = finalizeReviewedDecisions(14, { [CABIN_14122]: { state: 'ACCEPT' } }, REVIEWER);
    expect(r.applicationStatus).toBe('STAGED_NOT_APPLIED');
    expect(r.stagedRecord.applied_to_repository).toBe(false);
    expect(JSON.stringify(deck14Proof)).toBe(before);
  });
});

describe('zero Deck 14 objects are admitted for passengers', () => {
  it('holds across the whole governed proof', () => {
    const admitted = deck14Proof.objects.filter((o: any) => isAdmittedPassengerEntity(o));
    expect(admitted.length).toBe(0);
    expect(deck14Proof.objects.length).toBe(244);
  });
});

describe('unsupported decks still fail closed', () => {
  it('throws rather than substituting another deck', () => {
    for (const deck of [0, 4, 8, 13, 15, 99]) {
      expect(() => resolveDeckReviewSource(deck)).toThrow(UnsupportedDeckReviewError);
    }
    const html = renderToStaticMarkup(<DeckReviewWorkspace initialDeckNumber={8} />);
    expect(html).toContain('Deck 8 is not available for review');
    expect(html).not.toContain('bellissima-deck05-');
    expect(html).not.toContain('bellissima-deck14-');
  });
});

describe('Decks 5/6/7 keep their source binding', () => {
  it('still resolve their own proofs on PDF page 3', () => {
    for (const [deck, count] of [[5, 30], [6, 26], [7, 15]] as const) {
      const vm = buildDeckReviewWorkspaceViewModel(deck, {});
      expect(vm.candidates.length).toBe(count);
      expect(vm.sourceInfo.pageNumber).toBe(3);
      expect(vm.candidates.every((c) => c.publishStatus === 'PUBLISH_BLOCKED')).toBe(true);
      expect(vm.candidates.every((c) => c.evidenceCondition === 'UNKNOWN')).toBe(true);
      expect(vm.candidates.every((c) => c.isAdmittedIdentity === false)).toBe(true);
    }
  });
});
