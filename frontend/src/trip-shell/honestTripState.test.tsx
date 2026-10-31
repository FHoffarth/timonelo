import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { ReferenceTripShellPreview } from '../components/pages/TripShellPage';
import { buildPassengerTripViewModel } from './adapter';
import fixture from '../fixtures/reference_voyage_bellissima.json';
import type { PassengerTripKnowledgePack, VoyageKnowledgeResult } from './types';

describe('reference trip trust boundary', () => {
  it('does not promote legacy publishability or known-fact counts to verification', () => {
    const source = structuredClone(fixture);
    const before = JSON.stringify(source);
    const vm = buildPassengerTripViewModel(source.passenger_pack as PassengerTripKnowledgePack, source as VoyageKnowledgeResult);
    expect(vm.departure.isConfirmed).toBe(false);
    expect(vm.arrival.isConfirmed).toBe(false);
    expect(vm.timeline.every(day => day.status === 'info')).toBe(true);
    expect(vm.trustSummary.verifiedCount).toBe(0);
    expect(vm.departure.terminalStatusText).toBe('Not confirmed yet');
    expect(vm.arrival.berthStatusText).toBe('Not assigned yet');
    expect(JSON.stringify(source)).toBe(before);
  });

  it('labels the actual My Cruise entry as a past reference without official-source claims', () => {
    const html = renderToStaticMarkup(<ReferenceTripShellPreview />);
    expect(html).toContain('Past reference voyage');
    expect(html).toContain('4–7 Oct 2026');
    expect(html).toContain('Not a current booking');
    expect(html).not.toMatch(/Core trip details confirmed|confirmed facts|confirmed from official sources|Live-test trip/);
    expect(html).toContain('Details not available yet');
  });

  it('keeps absent trip data unavailable rather than confirming it', () => {
    const pack = { ...fixture.passenger_pack, departure_date: 'UNVERIFIED', arrival_date: 'UNVERIFIED', departure_location: 'UNVERIFIED', arrival_location: 'UNVERIFIED', check_in_time: null } as PassengerTripKnowledgePack;
    const vm = buildPassengerTripViewModel(pack);
    expect(vm.departure.dateFormatted).toBe('Date pending');
    expect(vm.arrival.city).toBe('Location pending');
    expect(vm.departure.timeFormatted).toBeNull();
    expect(vm.trustSummary.verifiedCount).toBe(0);
    expect(vm.timeline.some(day => day.status === 'confirmed')).toBe(false);
  });
});
