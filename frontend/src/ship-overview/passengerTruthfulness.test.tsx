/**
 * BC-1 — the Ships surface may not claim more than it is showing.
 *
 * The passenger page used to render `src/fixtures/bellissima_deck14_spatial.json`,
 * which carries the governed Deck 14 proof's 244 object ids and bounding boxes
 * with the lifecycle axes rewritten to SUPPORTED / APPROVED / PUBLISH_ALLOWED.
 * Everything passed the admission gate and the page announced "244 verified
 * spaces" of "reviewed, publication-approved" data. The gate was correct; its
 * input was pre-adjudicated.
 *
 * These tests pin the behaviour rather than the wiring: given the governed
 * state, the page must show a pending state and must not claim verification.
 * Given genuinely admitted state, it must still work.
 */

import { describe, it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import ShipOverview from './ShipOverview';
import { buildSpatialPassengerViewModel } from './adapter';
import { RawSpatialPayload } from './types';
import { payloadFromProof } from '../components/pages/ShipOverviewPage';
import governedProof from '../../public/data/deck14.proof.json';
import spatialFixture from '../fixtures/bellissima_deck14_spatial.json';

// The proof as the repository actually holds it, served at /data/deck14.proof.json.
const governedPayload = payloadFromProof(governedProof as never);
const preAdjudicatedFixture = spatialFixture as unknown as RawSpatialPayload;

function html(payload: RawSpatialPayload): string {
  return renderToStaticMarkup(
    <ShipOverview viewModel={buildSpatialPassengerViewModel(payload, 14)} />,
  );
}

describe('BC-1: the Ships surface tells the truth about what is admitted', () => {
  it('the governed proof still describes 244 objects, none of them publishable', () => {
    const objects = governedPayload.deck14_proof.objects;
    expect(objects.length).toBe(244);
    expect(objects.every((o) => o.publish_status === 'PUBLISH_BLOCKED')).toBe(true);
    expect(objects.every((o) => o.human_review_state === 'DRAFT')).toBe(true);
    expect(objects.every((o) => o.evidence_condition === 'UNKNOWN')).toBe(true);
  });

  it('admits nothing from the governed proof', () => {
    const vm = buildSpatialPassengerViewModel(governedPayload, 14);
    expect(vm.spatialEntities.length).toBe(0);
    expect(vm.trustSummary.admittedObjectsCount).toBe(0);
    expect(vm.trustSummary.admittedCabinsCount).toBe(0);
  });

  it('does not claim verified or publication-approved spaces when nothing is admitted', () => {
    const markup = html(governedPayload);
    expect(markup).not.toMatch(/verified spaces/i);
    expect(markup).not.toMatch(/244 verified/i);
    expect(markup).not.toMatch(/publication-approved/i);
    expect(markup).not.toMatch(/verified staterooms/i);
  });

  it('renders a passenger-readable pending state instead of an empty deck', () => {
    const markup = html(governedPayload);
    expect(markup).toContain('spatial-pending-state');
    expect(markup).toMatch(/still checking this deck/i);
    // Says it is deliberate, not a fault.
    expect(markup).toMatch(/not a fault/i);
    // Offers a next step that already exists in the product.
    expect(markup).toMatch(/My Cruise/);
  });

  it('keeps engineering lifecycle vocabulary out of the passenger surface', () => {
    const markup = html(governedPayload);
    for (const jargon of [
      'PUBLISH_BLOCKED',
      'PUBLISH_ALLOWED',
      'DRAFT',
      'UNKNOWN_PROVENANCE',
      'evidence gate',
      'adjudication',
      'canonical predicate',
    ]) {
      expect(markup).not.toContain(jargon);
    }
  });

  it('the pre-adjudicated fixture is not what the passenger page reads', () => {
    // The fixture still admits everything -- that is what makes it a useful test
    // payload, and exactly why it must not reach a passenger.
    const fixtureVm = buildSpatialPassengerViewModel(preAdjudicatedFixture, 14);
    expect(fixtureVm.spatialEntities.length).toBe(244);

    // Same object identities, opposite verdicts. The difference is the axes.
    const governedIds = governedPayload.deck14_proof.objects.map((o) => o.object_id).sort();
    const fixtureIds = preAdjudicatedFixture.deck14_proof.objects.map((o) => o.object_id).sort();
    expect(fixtureIds).toEqual(governedIds);

    const governedVm = buildSpatialPassengerViewModel(governedPayload, 14);
    expect(governedVm.spatialEntities.length).toBe(0);
  });

  it('still shows the deck when objects are genuinely admitted', () => {
    // The gate must not have been replaced by a blanket refusal: given admitted
    // input the page publishes, and says so in passenger language.
    const markup = html(preAdjudicatedFixture);
    expect(markup).not.toContain('spatial-pending-state');
    expect(markup).toMatch(/244 published spaces/);
    expect(markup).toMatch(/Deck 14 available/);
    // The stronger source notice is only reachable when something was admitted.
    const vm = buildSpatialPassengerViewModel(preAdjudicatedFixture, 14);
    expect(vm.trustSummary.statusBadge).toBe('Deck 14 Mapped');
    expect(vm.trustSummary.sourceNotice).toMatch(/checked by a person/);
  });
});
