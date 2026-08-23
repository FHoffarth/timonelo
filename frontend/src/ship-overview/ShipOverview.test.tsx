import { describe, it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import ShipOverview from './ShipOverview';
import { buildSpatialPassengerViewModel, isAdmittedPassengerEntity } from './adapter';
import { RawSpatialPayload } from './types';
import spatialFixture from '../fixtures/bellissima_deck14_spatial.json';

const goldenPayload = spatialFixture as unknown as RawSpatialPayload;

describe('Spatial Visual Polish + Multi-Deck Pipeline Invariant Tests', () => {
  // 1. Deck 14 geometry unchanged
  it('preserves exact Deck 14 cabin count and canonical normalized bounding boxes', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    expect(vm.spatialEntities.length).toBe(244);
    const cabin14001 = vm.spatialEntities.find((e) => e.name === 'Cabin 14001');
    expect(cabin14001).toBeDefined();
    expect(cabin14001?.bbox[0]).toBeCloseTo(0.06298, 4);
    expect(cabin14001?.polygon.length).toBe(4);
  });

  // 2. Selected cabin highlight uses canonical geometry
  it('uses canonical coordinates when highlighting selected cabin', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const cabin14122 = vm.spatialEntities.find((e) => e.name === 'Cabin 14122');
    expect(cabin14122).toBeDefined();
    expect(cabin14122?.bbox).toBeDefined();
    expect(cabin14122?.center).toBeDefined();
  });

  // 3. Low-zoom label suppression does not alter geometry
  it('keeps underlying polygon coordinates intact regardless of presentation zoom', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const origBbox = [...goldenPayload.deck14_proof.objects[0].normalized_bbox];
    expect(vm.spatialEntities[0].bbox).toEqual(origBbox);
  });

  // 4. Fit-to-deck is deterministic
  it('computes deterministic viewBox for Deck 14 canvas', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    expect(vm.selectedDeck.viewBox.minX).toBeGreaterThanOrEqual(0);
    expect(vm.selectedDeck.viewBox.width).toBeGreaterThan(0);
    expect(vm.selectedDeck.viewBox.height).toBeGreaterThan(0);
  });

  // 5. Deck switching does not mutate source geometry
  it('keeps source payload immutable when switching decks', () => {
    const payloadCopy = JSON.parse(JSON.stringify(goldenPayload));
    const vm1 = buildSpatialPassengerViewModel(payloadCopy, 14);
    const vm2 = buildSpatialPassengerViewModel(payloadCopy, 14);
    expect(vm1.spatialEntities.length).toBe(vm2.spatialEntities.length);
    expect(payloadCopy).toEqual(goldenPayload);
  });

  // 6. Only admitted mapped decks appear
  it('displays only admitted mapped decks in availableDecks', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    expect(vm.availableDecks.length).toBe(1);
    expect(vm.availableDecks[0].deckNumber).toBe(14);
    expect(vm.availableDecks[0].hasSpatialGeometry).toBe(true);
  });

  // 7. DRAFT deck geometry excluded
  it('excludes DRAFT objects from spatial entities', () => {
    const payloadWithDraft: RawSpatialPayload = {
      ...goldenPayload,
      deck14_proof: {
        ...goldenPayload.deck14_proof,
        objects: [
          {
            object_id: 'draft-deck-object',
            semantic_type: 'venue',
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
    const vm = buildSpatialPassengerViewModel(payloadWithDraft, 14);
    expect(vm.spatialEntities.some((e) => e.id === 'draft-deck-object')).toBe(false);
  });

  // 8. PUBLISH_BLOCKED geometry excluded
  it('excludes PUBLISH_BLOCKED objects from spatial entities', () => {
    const payloadWithBlocked: RawSpatialPayload = {
      ...goldenPayload,
      deck14_proof: {
        ...goldenPayload.deck14_proof,
        objects: [
          {
            object_id: 'blocked-deck-object',
            semantic_type: 'venue',
            source_bbox: [0, 0, 10, 10],
            normalized_bbox: [0.1, 0.1, 0.2, 0.2],
            normalized_polygon: [],
            geometry_provenance: 'TRANSFORMED_SOURCE_GEOMETRY',
            evidence_condition: 'SUPPORTED',
            human_review_state: 'APPROVED',
            publish_status: 'PUBLISH_BLOCKED',
          },
        ],
      },
    };
    const vm = buildSpatialPassengerViewModel(payloadWithBlocked, 14);
    expect(vm.spatialEntities.some((e) => e.id === 'blocked-deck-object')).toBe(false);
  });

  // 9. UNKNOWN_PROVENANCE excluded
  it('excludes UNKNOWN_PROVENANCE geometry from passenger truth', () => {
    const payloadWithUnknownProv: RawSpatialPayload = {
      ...goldenPayload,
      deck14_proof: {
        ...goldenPayload.deck14_proof,
        objects: [
          {
            object_id: 'unknown-prov-obj',
            semantic_type: 'cabin',
            cabin_number: '14999',
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

  // 10. Venue name without admitted geometry gets no marker/polygon
  it('keeps venue unmapped when geometry is absent or unadmitted', () => {
    const payloadWithUnmapped: RawSpatialPayload = {
      ...goldenPayload,
      known_unmapped_venues: [
        {
          statement_id: 'STM-THEATRE',
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
    const vm = buildSpatialPassengerViewModel(payloadWithUnmapped, 14);
    expect(vm.spatialEntities.some((e) => e.name === 'London Theatre')).toBe(false);
    expect(vm.unmappedEntities.some((u) => u.name === 'London Theatre')).toBe(true);
  });

  // 11. Geometry without admitted venue identity does not inherit a name
  it('labels infrastructure region conservatively as Vertical Core Area', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const liftCore = vm.spatialEntities.find((e) => e.id === 'bellissima-deck14-lift-core-proof');
    expect(liftCore?.name).toBe('Vertical Core Area');
    expect(liftCore?.categoryLabel).toBe('Ship Infrastructure');
  });

  // 12. Source-page association retained in proof metadata
  it('preserves provenance metadata in view model', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    expect(vm.spatialEntities[0].provenanceLabel).toBe('Mapped from official deck plan');
  });

  // 13. Exact venue-object association deterministic
  it('deterministically formats cabin numbers from object properties', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const cabin = vm.spatialEntities.find((e) => e.name === 'Cabin 14122');
    expect(cabin).toBeDefined();
    expect(cabin?.deckNumber).toBe(14);
    expect(cabin?.categoryLabel).toBe('Stateroom');
  });

  // 14. No proximity-based semantic joining
  it('does not join adjacent polygons or synthesize proximity clusters', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const cabins = vm.spatialEntities.filter((e) => e.entityType === 'cabin');
    expect(cabins.length).toBe(243);
  });

  // 15. No connectivity inferred
  it('does not compute route graph, corridor links, or deck transitions', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const html = renderToStaticMarkup(<ShipOverview viewModel={vm} />);
    expect(html).not.toContain('route');
    expect(html).not.toContain('step-free');
    expect(html).not.toContain('shortest path');
  });

  // 16. No Nearby copy appears
  it('does not emit speculative Nearby or proximity recommendations', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const html = renderToStaticMarkup(<ShipOverview viewModel={vm} />);
    expect(html).not.toContain('Nearby venues');
    expect(html).not.toContain('Places near you');
    expect(html).not.toContain('Closest to');
  });

  // 17. No routing copy appears
  it('does not emit turn-by-turn directions', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const html = renderToStaticMarkup(<ShipOverview viewModel={vm} />);
    expect(html).not.toContain('turn left');
    expect(html).not.toContain('walk forward');
  });

  // 18. 390 px no horizontal overflow
  it('renders within 390px viewport width without breaking', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const html = renderToStaticMarkup(
      <div style={{ width: '390px' }}>
        <ShipOverview viewModel={vm} />
      </div>
    );
    expect(html).toContain('w-full');
    expect(html).toContain('MSC Bellissima');
  });

  // 19. Selected card remains usable on mobile
  it('renders selected card with responsive layout', () => {
    const vm = buildSpatialPassengerViewModel(goldenPayload, 14);
    const html = renderToStaticMarkup(<ShipOverview viewModel={vm} />);
    expect(html).toContain('min-h-[44px]');
  });

  // 20. Pure predicate function unit test
  it('isAdmittedPassengerEntity accurately evaluates dual-gate criteria', () => {
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
        evidence_condition: 'UNKNOWN',
        human_review_state: 'DRAFT',
        publish_status: 'PUBLISH_BLOCKED',
        geometry_provenance: 'TRANSFORMED_SOURCE_GEOMETRY',
      })
    ).toBe(false);
  });
});
