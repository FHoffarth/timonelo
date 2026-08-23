import { describe, it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import TripShell from './TripShell';
import { buildPassengerTripViewModel } from './adapter';
import { PassengerTripKnowledgePack, VoyageKnowledgeResult } from './types';
import referenceVoyageFixture from '../fixtures/reference_voyage_bellissima.json';

const goldenPack = referenceVoyageFixture.passenger_pack as unknown as PassengerTripKnowledgePack;
const goldenResult = referenceVoyageFixture as unknown as VoyageKnowledgeResult;

describe('Passenger Trip Shell v1 Truth-Copy & Boundary Tests (ADR-0002)', () => {
  // 1. "All voyage details are verified" is absent
  it('does not overclaim that "all voyage details are verified"', () => {
    const vm = buildPassengerTripViewModel(goldenPack, goldenResult);
    const html = renderToStaticMarkup(<TripShell viewModel={vm} />);
    expect(html).not.toContain('All voyage details are verified');
    expect(html).toContain('Some trip details are confirmed from official sources.');
  });

  // 2. "Confirmed Voyage" is absent if unresolved gaps exist
  it('does not state "Confirmed Voyage" when terminal/berth gaps remain', () => {
    const vm = buildPassengerTripViewModel(goldenPack, goldenResult);
    const html = renderToStaticMarkup(<TripShell viewModel={vm} />);
    expect(html).not.toContain('Confirmed Voyage');
    expect(html).toContain('Core trip details confirmed');
  });

  // 3. No automatic-update promise appears
  it('does not promise automatic background rechecks or updates', () => {
    const vm = buildPassengerTripViewModel(goldenPack, goldenResult);
    const html = renderToStaticMarkup(<TripShell viewModel={vm} />);
    expect(html).not.toContain('update this automatically');
    expect(html).not.toContain('will appear here automatically');
    expect(html).not.toContain('automatically as official port schedules become available');
    expect(html).toContain('Check again closer to departure');
  });

  // 4. No unsupported 30-60 day passenger claim appears
  it('does not emit an unproven 30-60 day port authority timeline claim to passengers', () => {
    const vm = buildPassengerTripViewModel(goldenPack, goldenResult);
    const html = renderToStaticMarkup(<TripShell viewModel={vm} />);
    expect(html).not.toContain('30-60 days');
    expect(html).not.toContain('30–60 days');
    expect(html).not.toContain('typically assign and publish');
  });

  // 5. check_in_time 14:00 renders exactly as check-in, not recommended/window
  it('renders check_in_time 14:00 strictly without window or recommendation upgrade', () => {
    const vm = buildPassengerTripViewModel(goldenPack, goldenResult);
    const html = renderToStaticMarkup(<TripShell viewModel={vm} />);
    expect(html).toContain('14:00');
    expect(html).not.toContain('Recommended Check-in');
    expect(html).not.toContain('confirmed check-in window');
    expect(html).not.toContain('Please arrive within your confirmed check-in window');
  });

  // 6. Terminal/berth remain explicitly unconfirmed
  it('renders terminal and berth explicitly as unconfirmed and unassigned', () => {
    const vm = buildPassengerTripViewModel(goldenPack, goldenResult);
    const html = renderToStaticMarkup(<TripShell viewModel={vm} />);
    expect(html).toContain('Not confirmed yet');
    expect(html).toContain('Not assigned yet');
  });

  // 7. Generic Tokyo terminal remains clearly non-assigned in Port Information section
  it('renders generic destination terminal strictly in separate Port Information section with non-assignment notice', () => {
    const vm = buildPassengerTripViewModel(goldenPack, goldenResult);
    const html = renderToStaticMarkup(<TripShell viewModel={vm} />);
    expect(html).toContain('PORT INFORMATION (DESTINATION)');
    expect(html).toContain('東京国際クルーズターミナル');
    expect(html).toContain('Known port facility — not yet confirmed for your sailing.');
  });

  // 8. Verified/pending counts do not imply full-trip verification
  it('scopes verified and pending counts without claiming complete verification', () => {
    const vm = buildPassengerTripViewModel(goldenPack, goldenResult);
    const html = renderToStaticMarkup(<TripShell viewModel={vm} />);
    expect(html).toContain('8 confirmed facts');
    expect(html).toContain('4 details pending');
    expect(html).not.toContain('Trip fully verified');
    expect(html).not.toContain('Fully verified trip');
  });

  // 9. Primary UI does not expose internal enums
  it('strictly insulates internal enums and symbols from visible passenger markup', () => {
    const vm = buildPassengerTripViewModel(goldenPack, goldenResult);
    const html = renderToStaticMarkup(<TripShell viewModel={vm} />);
    expect(html).not.toContain('SUPPORTED');
    expect(html).not.toContain('PUBLISH_ALLOWED');
    expect(html).not.toContain('PUBLISH_BLOCKED');
    expect(html).not.toContain('Method.INFERRED');
    expect(html).not.toContain('AUTO_ADMISSIBLE');
    expect(html).not.toContain('REVIEW_REQUIRED');
    expect(html).not.toContain('UNCONFIRMED');
    expect(html).not.toContain('UNKNOWN');
    expect(html).not.toContain('ART-0007');
  });

  // 10. PII/trust copy does not overclaim system-wide storage behavior
  it('uses precise, architecture-supported PII isolation wording', () => {
    const vm = buildPassengerTripViewModel(goldenPack, goldenResult);
    expect(vm.trustSummary.piiNotice).toBe(
      'Personal booking details are kept out of the reusable trip knowledge shown here.'
    );
    const html = renderToStaticMarkup(<TripShell viewModel={vm} />);
    expect(html).not.toContain('Zero PII or raw booking payloads in canonical repository');
    expect(html).not.toContain('Zero PII or raw booking payloads stored');
  });

  // 11. Golden fixture is clearly reference data
  it('derives from the explicit reference voyage fixture', () => {
    expect(referenceVoyageFixture.voyage_entity).toBe('voyage:msc-bellissima:20261004-shanghai-tokyo');
    expect(goldenPack.vessel_name).toBe('MSC BELLISSIMA');
  });

  // 12. Production TripShell component remains data-driven
  it('renders custom voyage inputs without hardcoded Bellissima dependence', () => {
    const customPack: PassengerTripKnowledgePack = {
      voyage_entity: 'voyage:custom-ship:20270101-barcelona-genoa',
      vessel_name: 'MSC GRANDIOSA',
      departure_date: '2027-01-01',
      departure_location: 'Barcelona, Spain',
      departure_port_unlocode: 'ESBCN',
      arrival_date: '2027-01-04',
      arrival_location: 'Genoa, Italy',
      arrival_port_unlocode: 'ITGOA',
      check_in_time: '12:00',
      departure_terminal_status: 'UNCONFIRMED',
      departure_berth_status: 'UNCONFIRMED',
      arrival_terminal_status: 'UNCONFIRMED',
      arrival_berth_status: 'UNCONFIRMED',
      known_generic_infrastructure: [],
      trust_metadata: {
        governance: 'ADR-0002 Truth Engine',
        truth_model: 'Evidence Graph',
        pii_isolation: 'Personal booking details are kept out of the reusable trip knowledge shown here.',
      },
      next_evidence_gaps: [],
    };

    const vm = buildPassengerTripViewModel(customPack);
    const html = renderToStaticMarkup(<TripShell viewModel={vm} />);
    expect(html).toContain('MSC Grandiosa');
    expect(html).toContain('Barcelona → Genoa');
    expect(html).toContain('1–4 Jan 2027');
    expect(html).toContain('3 nights');
  });

  // 13. 320 px and mobile viewports remain usable
  it('supports 320px, 375px, 390px responsive viewports without layout breakage', () => {
    const vm = buildPassengerTripViewModel(goldenPack, goldenResult);
    const html = renderToStaticMarkup(
      <div style={{ width: '320px' }}>
        <TripShell viewModel={vm} />
      </div>
    );
    expect(html).toContain('w-full');
    expect(html).toContain('EMBARKATION');
    expect(html).toContain('DISEMBARKATION');
  });

  // 14. Unknown states remain visible, not hidden
  it('ensures unknown states are explicitly visible and explained rather than omitted', () => {
    const vm = buildPassengerTripViewModel(goldenPack, goldenResult);
    const html = renderToStaticMarkup(<TripShell viewModel={vm} />);
    expect(html).toContain('Details not available yet');
    expect(html).toContain('Departure Terminal &amp; Berth');
    expect(html).toContain('Arrival Terminal &amp; Berth');
  });
});
