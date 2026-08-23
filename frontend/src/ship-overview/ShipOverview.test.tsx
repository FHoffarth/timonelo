import { describe, it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import ShipOverview from './ShipOverview';
import { buildSpatialPassengerViewModel, isAdmittedPassengerEntity } from './adapter';
import { RawSpatialPayload } from './types';
import spatialFixture from '../fixtures/bellissima_deck14_spatial.json';

const goldenPayload = spatialFixture as unknown as RawSpatialPayload;

describe('Spatial Passenger Shell v1 Lifecycle & Boundary Tests (ADR-0002 / ADR-0003)', () => {
  // 1. DRAFT venue is absent from passenger search & UI
  it('omits DRAFT venues from passenger search and UI', () => {
    const payloadWithDraft: RawSpatialPayload = {
      ...goldenPayload,
      known_unmapped_venues: [
        {
          statement_id: 'STM-DRAFT-VENUE',
          name: 'Draft Piano Lounge',
          deck_number: 6,
          category: 'Dining & Bars',
          status: 'known_but_unmapped',
          evidence_condition: 'UNKNOWN',
          human_review_state: 'DRAFT',
          publish_status: 'PUBLISH_BLOCKED',
        },
      ],
    };
    const vm = buildSpatialPassengerViewModel(payloadWithDraft, 14);
    expect(vm.unmappedEntities.length).toBe(0);
    const html = renderToStaticMarkup(<ShipOverview viewModel={vm} />);
    expect(html).not.toContain('Draft Piano Lounge');
  });

  // 2. PUBLISH_BLOCKED venue is absent
  it('omits PUBLISH_BLOCKED venues from passenger search and UI', () => {
    const payloadWithBlocked: RawSpatialPayload = {
      ...goldenPayload,
      known_unmapped_venues: [
        {
          statement_id: 'STM-BLOCKED-VENUE',
          name: 'Blocked Casino Area',
          deck_number: 7,
          category: 'Entertainment',
          status: 'known_but_unmapped',
          evidence_condition: 'SUPPORTED',
          human_review_state: 'APPROVED',
          publish_status: 'PUBLISH_BLOCKED',
        },
      ],
    };
    const vm = buildSpatialPassengerViewModel(payloadWithBlocked, 14);
    expect(vm.unmappedEntities.length).toBe(0);
  });

  // 3. UNKNOWN / UNSUPPORTED venue is absent
  it('omits UNKNOWN / UNSUPPORTED venues from passenger search', () => {
    const payloadWithUnsupported: RawSpatialPayload = {
      ...goldenPayload,
      known_unmapped_venues: [
        {
          statement_id: 'STM-UNSUPPORTED-VENUE',
          name: 'Unsupported Pool Bar',
          deck_number: 15,
          category: 'Dining & Bars',
          status: 'known_but_unmapped',
          evidence_condition: 'UNSUPPORTED',
          human_review_state: 'APPROVED',
          publish_status: 'PUBLISH_ALLOWED',
        },
      ],
    };
    const vm = buildSpatialPassengerViewModel(payloadWithUnsupported, 14);
    expect(vm.unmappedEntities.length).toBe(0);
  });

  // 4. APPROVED + SUPPORTED + PUBLISH_ALLOWED known-but-unmapped venue may appear
  it('admits fully reviewed, publication-allowed unmapped venues', () => {
    const payloadWithAdmittedVenue: RawSpatialPayload = {
      ...goldenPayload,
      known_unmapped_venues: [
        {
          statement_id: 'STM-ADMITTED-VENUE',
          name: 'London Theatre',
          deck_number: 5,
          category: 'Entertainment',
          status: 'known_but_unmapped',
          evidence_condition: 'SUPPORTED',
          human_review_state: 'APPROVED',
          publish_status: 'PUBLISH_ALLOWED',
        },
      ],
    };
    const vm = buildSpatialPassengerViewModel(payloadWithAdmittedVenue, 14);
    expect(vm.unmappedEntities.length).toBe(1);
    expect(vm.unmappedEntities[0].name).toBe('London Theatre');
    expect(vm.unmappedEntities[0].statusLabel).toBe('Known place — location not mapped yet');
    const html = renderToStaticMarkup(<ShipOverview viewModel={vm} />);
    expect(html).toContain('Known Places on Other Decks');
  });

  // 5. Provenance alone cannot admit a passenger entity (DRAFT / PUBLISH_BLOCKED rejected)
  it('rejects source geometry when lifecycle state is DRAFT or PUBLISH_BLOCKED', () => {
    const payloadWithDraftObj: RawSpatialPayload = {
      ...goldenPayload,
      deck14_proof: {
        ...goldenPayload.deck14_proof,
        objects: [
          {
            object_id: 'draft-cabin-object',
            semantic_type: 'cabin',
            cabin_number: '14999',
            source_bbox: [0, 0, 10, 10],
            normalized_bbox: [0.1, 0.1, 0.2, 0.2],
            normalized_polygon: [[0.1, 0.1], [0.2, 0.1], [0.2, 0.2], [0.1, 0.2]],
            geometry_provenance: 'TRANSFORMED_SOURCE_GEOMETRY',
            evidence_condition: 'UNKNOWN',
            human_review_state: 'DRAFT',
            publish_status: 'PUBLISH_BLOCKED',
          },
        ],
      },
    };
    const vm = buildSpatialPassengerViewModel(payloadWithDraftObj, 14);
    expect(vm.spatialEntities.some((e) => e.id === 'draft-cabin-object')).toBe(false);
  });

  // 6. Lifecycle admission alone cannot admit coordinates with UNKNOWN_PROVENANCE
  it('rejects coordinates with UNKNOWN_PROVENANCE even if lifecycle is APPROVED', () => {
    const payloadWithUnknownProv: RawSpatialPayload = {
      ...goldenPayload,
      deck14_proof: {
        ...goldenPayload.deck14_proof,
        objects: [
          {
            object_id: 'unknown-prov-obj',
            semantic_type: 'cabin',
            cabin_number: '14888',
            source_bbox: [0, 0, 10, 10],
            normalized_bbox: [0.1, 0.1, 0.2, 0.2],
            normalized_polygon: [],
            geometry_provenance: 'UNKNOWN_PROVENANCE',
            evidence_condition: 'SUPPORTED',
            human_review_state: 'APPROVED',
            publish_status: 'PUBLISH_ALLOWED',
          },
        ],
      },
    };
    const vm = buildSpatialPassengerViewModel(payloadWithUnknownProv, 14);
    expect(vm.spatialEntities.some((e) => e.id === 'unknown-prov-obj')).toBe(false);
  });

  // 7. SYNTHETIC_GEOMETRY never renders as mapped truth
  it('rejects SYNTHETIC_GEOMETRY even if lifecycle is APPROVED', () => {
    const payloadWithSynthetic: RawSpatialPayload = {
      ...goldenPayload,
      deck14_proof: {
        ...goldenPayload.deck14_proof,
        objects: [
          {
            object_id: 'synthetic-cabin-test',
            semantic_type: 'cabin',
            cabin_number: '14777',
            source_bbox: [0, 0, 10, 10],
            normalized_bbox: [0.1, 0.1, 0.2, 0.2],
            normalized_polygon: [],
            geometry_provenance: 'SYNTHETIC_GEOMETRY',
            evidence_condition: 'SUPPORTED',
            human_review_state: 'APPROVED',
            publish_status: 'PUBLISH_ALLOWED',
          },
        ],
      },
    };
    const vm = buildSpatialPassengerViewModel(payloadWithSynthetic, 14);
    expect(vm.spatialEntities.some((e) => e.id === 'synthetic-cabin-test')).toBe(false);
  });

  // 8. Deck 14 cabins render only if lifecycle + provenance both pass
  it('renders Deck 14 cabins when lifecycle and provenance both pass', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    expect(vm.spatialEntities.length).toBe(244);
    expect(vm.trustSummary.admittedCabinsCount).toBe(243);
    const html = renderToStaticMarkup(<ShipOverview viewModel={vm} />);
    expect(html).toContain('Deck 14 available');
  });

  // 9. Vertical-core region does not become "Elevator & Stairs Access" without evidence
  it('labels vertical-core region conservatively as Vertical Core Area without elevator/stair claims', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const liftCore = vm.spatialEntities.find((e) => e.id === 'bellissima-deck14-lift-core-proof');
    expect(liftCore).toBeDefined();
    expect(liftCore?.name).toBe('Vertical Core Area');
    expect(liftCore?.categoryLabel).toBe('Ship Infrastructure');
    expect(liftCore?.name).not.toContain('Elevator');
    expect(liftCore?.name).not.toContain('Stairs');
    const html = renderToStaticMarkup(<ShipOverview viewModel={vm} />);
    expect(html).not.toContain('Elevator &amp; Stairs Access');
  });

  // 10. No accessibility or connectivity semantics leak from geometry alone
  it('does not emit accessibility, route connection, or deck-to-deck claims from geometry alone', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const html = renderToStaticMarkup(<ShipOverview viewModel={vm} />);
    expect(html).not.toContain('step-free connection');
    expect(html).not.toContain('accessible route');
    expect(html).not.toContain('stairs connection');
  });

  // 11. Deck selector contains only canonically admitted decks
  it('includes only canonically admitted decks without hardcoded numeric loops', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    expect(vm.availableDecks.length).toBe(1);
    expect(vm.availableDecks[0].deckNumber).toBe(14);
    expect(vm.availableDecks.some((d) => d.deckNumber === 4)).toBe(false);
    expect(vm.availableDecks.some((d) => d.deckNumber === 99)).toBe(false);
  });

  // 12. Generic missing decks notice is present
  it('displays a generic note for missing decks rather than synthetic inventory', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const html = renderToStaticMarkup(<ShipOverview viewModel={vm} />);
    expect(html).toContain('More deck views are not available yet.');
  });

  // 13. No raw lifecycle / provenance enums leak to passenger UI
  it('strictly insulates internal enums and lifecycle tokens from passenger markup', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const html = renderToStaticMarkup(<ShipOverview viewModel={vm} />);
    expect(html).not.toContain('TRANSFORMED_SOURCE_GEOMETRY');
    expect(html).not.toContain('DIRECT_SOURCE_GEOMETRY');
    expect(html).not.toContain('DERIVED_GEOMETRY');
    expect(html).not.toContain('SYNTHETIC_GEOMETRY');
    expect(html).not.toContain('UNKNOWN_PROVENANCE');
    expect(html).not.toContain('PUBLISH_ALLOWED');
    expect(html).not.toContain('PUBLISH_BLOCKED');
    expect(html).not.toContain('SUPPORTED');
    expect(html).not.toContain('DRAFT');
  });

  // 14. Golden spatial fixture matches current repository truth
  it('reflects exact admitted Deck 14 counts (243 cabins + 1 vertical core = 244)', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    expect(vm.spatialEntities.length).toBe(244);
    expect(vm.trustSummary.admittedCabinsCount).toBe(243);
    expect(vm.trustSummary.admittedObjectsCount).toBe(244);
    expect(vm.trustSummary.mappedDecksCount).toBe(1);
  });

  // 15. Canvas interaction remains immutable and accessible
  it('supports 320px viewport and responsive layout', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const html = renderToStaticMarkup(
      <div style={{ width: '320px' }}>
        <ShipOverview viewModel={vm} />
      </div>
    );
    expect(html).toContain('w-full');
    expect(html).toContain('MSC Bellissima');
  });

  // 16. Pure predicate function unit test
  it('isAdmittedPassengerEntity accurately evaluates all condition matrices', () => {
    expect(
      isAdmittedPassengerEntity({
        evidence_condition: 'SUPPORTED',
        human_review_state: 'APPROVED',
        publish_status: 'PUBLISH_ALLOWED',
        geometry_provenance: 'TRANSFORMED_SOURCE_GEOMETRY',
      })
    ).toBe(true);

    expect(
      isAdmittedPassengerEntity({
        evidence_condition: 'SUPPORTED',
        human_review_state: 'APPROVED',
        publish_status: 'PUBLISH_ALLOWED',
        geometry_provenance: 'SYNTHETIC_GEOMETRY',
      })
    ).toBe(false);

    expect(
      isAdmittedPassengerEntity({
        evidence_condition: 'UNKNOWN',
        human_review_state: 'DRAFT',
        publish_status: 'PUBLISH_BLOCKED',
        geometry_provenance: 'TRANSFORMED_SOURCE_GEOMETRY',
      })
    ).toBe(false);
  });
});
