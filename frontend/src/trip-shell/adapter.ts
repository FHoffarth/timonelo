/**
 * Passenger Trip Shell Adapter (ADR-0002).
 * Pure transformer from Factory Contract to Passenger View Model.
 * Strictly insulates internal enums and ensures fact-scoped, evidence-safe copy.
 */

import {
  PassengerTripKnowledgePack,
  VoyageKnowledgeResult,
  PassengerTripViewModel,
  PortStatusViewModel,
  TimelineDayViewModel,
  ConfirmedFactViewModel,
  PendingFactViewModel,
  GenericFacilityViewModel,
  BeforeYouGoItemViewModel,
  TrustSummaryViewModel,
} from './types';

const MONTH_NAMES = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

const DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function parseIsoDate(isoString: string): Date | null {
  if (!isoString || isoString === 'UNVERIFIED') return null;
  const match = isoString.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return null;
  const year = parseInt(match[1], 10);
  const month = parseInt(match[2], 10) - 1;
  const day = parseInt(match[3], 10);
  return new Date(year, month, day);
}

function formatDateShort(isoString: string): string {
  const d = parseIsoDate(isoString);
  if (!d) return 'Date pending';
  return `${d.getDate()} ${MONTH_NAMES[d.getMonth()]} ${d.getFullYear()}`;
}

function formatDateRange(depIso: string, arrIso: string): string {
  const dep = parseIsoDate(depIso);
  const arr = parseIsoDate(arrIso);
  if (!dep || !arr) return 'Dates to be announced';

  if (dep.getFullYear() === arr.getFullYear() && dep.getMonth() === arr.getMonth()) {
    return `${dep.getDate()}–${arr.getDate()} ${MONTH_NAMES[dep.getMonth()]} ${dep.getFullYear()}`;
  }
  if (dep.getFullYear() === arr.getFullYear()) {
    return `${dep.getDate()} ${MONTH_NAMES[dep.getMonth()]} – ${arr.getDate()} ${MONTH_NAMES[arr.getMonth()]} ${dep.getFullYear()}`;
  }
  return `${dep.getDate()} ${MONTH_NAMES[dep.getMonth()]} ${dep.getFullYear()} – ${arr.getDate()} ${MONTH_NAMES[arr.getMonth()]} ${arr.getFullYear()}`;
}

function calculateNights(depIso: string, arrIso: string): string | null {
  const dep = parseIsoDate(depIso);
  const arr = parseIsoDate(arrIso);
  if (!dep || !arr) return null;
  const diffTime = arr.getTime() - dep.getTime();
  const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
  if (diffDays > 0) {
    return `${diffDays} night${diffDays > 1 ? 's' : ''}`;
  }
  return null;
}

function formatShipName(raw: string): string {
  if (!raw || raw === 'UNVERIFIED') return 'Vessel to be confirmed';
  const clean = raw.trim();
  if (clean.toUpperCase().startsWith('MSC ')) {
    const rest = clean.substring(4);
    return `MSC ${rest.charAt(0).toUpperCase() + rest.slice(1).toLowerCase()}`;
  }
  return clean.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');
}

function parseLocation(loc: string): { city: string; country: string } {
  if (!loc || loc === 'UNVERIFIED') return { city: 'Location pending', country: '' };
  const parts = loc.split(',').map(s => s.trim());
  return {
    city: parts[0] || 'Location pending',
    country: parts.slice(1).join(', ') || '',
  };
}

export function buildPassengerTripViewModel(
  pack: PassengerTripKnowledgePack,
  result?: VoyageKnowledgeResult | null
): PassengerTripViewModel {
  const depLoc = parseLocation(pack.departure_location);
  const arrLoc = parseLocation(pack.arrival_location);

  const shipName = formatShipName(pack.vessel_name);
  const routeLabel = `${depLoc.city} → ${arrLoc.city}`;
  const dateRangeLabel = formatDateRange(pack.departure_date, pack.arrival_date);
  const durationLabel = calculateNights(pack.departure_date, pack.arrival_date);

  // Departure View Model - strictly Proven
  const departure: PortStatusViewModel = {
    city: depLoc.city,
    country: depLoc.country,
    rawLocation: pack.departure_location,
    dateFormatted: formatDateShort(pack.departure_date),
    timeFormatted: pack.check_in_time ? `Check-in: ${pack.check_in_time}` : null,
    timeLabel: pack.check_in_time ? 'Check-in' : null,
    terminalStatusText: 'Not confirmed yet',
    berthStatusText: 'Not assigned yet',
    isConfirmed: pack.departure_date !== 'UNVERIFIED' && depLoc.city !== 'Location pending',
    unlocode: pack.departure_port_unlocode,
  };

  // Arrival View Model - strictly Proven
  const arrival: PortStatusViewModel = {
    city: arrLoc.city,
    country: arrLoc.country,
    rawLocation: pack.arrival_location,
    dateFormatted: formatDateShort(pack.arrival_date),
    terminalStatusText: 'Not confirmed yet',
    berthStatusText: 'Not assigned yet',
    isConfirmed: pack.arrival_date !== 'UNVERIFIED' && arrLoc.city !== 'Location pending',
    unlocode: pack.arrival_port_unlocode,
  };

  // Timeline derivation strictly from verified facts
  const timeline: TimelineDayViewModel[] = [];

  const depDateObj = parseIsoDate(pack.departure_date);
  const arrDateObj = parseIsoDate(pack.arrival_date);

  // Day 1: Embarkation / Departure
  const day1Events = [];
  if (pack.check_in_time) {
    day1Events.push({
      label: 'Check-in',
      time: pack.check_in_time,
      note: 'Check-in time from official booking confirmation.',
    });
  } else {
    day1Events.push({
      label: 'Embarkation',
      note: 'Check-in timing will be updated closer to sailing.',
    });
  }

  timeline.push({
    dateFormatted: formatDateShort(pack.departure_date),
    dayOfWeek: depDateObj ? DAY_NAMES[depDateObj.getDay()] : undefined,
    locationTitle: `${depLoc.city}, Embarkation`,
    status: 'confirmed',
    statusBadge: 'Confirmed',
    events: day1Events,
  });

  // Final Day: Arrival / Debarkation
  timeline.push({
    dateFormatted: formatDateShort(pack.arrival_date),
    dayOfWeek: arrDateObj ? DAY_NAMES[arrDateObj.getDay()] : undefined,
    locationTitle: `${arrLoc.city}, Destination`,
    status: 'confirmed',
    statusBadge: 'Confirmed',
    events: [
      {
        label: 'Arrival',
        note: 'Terminal and berth details will be available closer to arrival.',
      },
    ],
  });

  // Confirmed Facts list (passenger-safe)
  const confirmedFacts: ConfirmedFactViewModel[] = [
    {
      label: 'Ship',
      value: shipName,
      category: 'ship',
    },
    {
      label: 'Departure',
      value: `${depLoc.city} (${formatDateShort(pack.departure_date)})`,
      category: 'port',
    },
    {
      label: 'Arrival',
      value: `${arrLoc.city} (${formatDateShort(pack.arrival_date)})`,
      category: 'port',
    },
  ];

  if (pack.check_in_time) {
    confirmedFacts.push({
      label: 'Check-in Time',
      value: pack.check_in_time,
      category: 'timing',
    });
  }

  if (durationLabel) {
    confirmedFacts.push({
      label: 'Voyage Duration',
      value: durationLabel,
      category: 'date',
    });
  }

  // Pending Facts (intentional unknown handling without overclaiming)
  const pendingFacts: PendingFactViewModel[] = [
    {
      label: 'Departure Terminal & Berth',
      statusText: 'Not confirmed yet',
      whyPending: 'Specific departure terminal and berth details are not confirmed yet.',
      whatNext: 'Check again closer to departure for updated terminal information.',
    },
    {
      label: 'Arrival Terminal & Berth',
      statusText: 'Not confirmed yet',
      whyPending: 'Specific arrival terminal and berth details are not confirmed yet.',
      whatNext: 'Check again closer to departure for updated terminal information.',
    },
  ];

  // Generic Destination Port Facilities (strictly separated from voyage-specific facts)
  const genericPortFacilities: GenericFacilityViewModel[] = (
    pack.known_generic_infrastructure || []
  ).map(f => ({
    name: f.name,
    notice: 'Known port facility — not yet confirmed for your sailing.',
    facilityType: 'Cruise Terminal',
  }));

  // Before You Go Checklist (passenger guidance)
  const beforeYouGo: BeforeYouGoItemViewModel[] = [
    {
      title: 'Check terminal details closer to departure',
      description: 'Specific berth assignments are finalized by port authorities closer to travel date.',
      iconName: 'terminal',
    },
    {
      title: 'Keep your booking confirmation handy',
      description: 'Have your booking document and travel identification ready for port check-in.',
      iconName: 'documents',
    },
    {
      title: 'Review port travel directions before departure',
      description: 'Check local transit options to the port area in advance of sailing day.',
      iconName: 'port',
    },
  ];

  // Trust Summary - Scoped and Measured
  const verifiedCount = result?.known_facts?.length || confirmedFacts.length;
  const pendingCount = result?.gaps?.length || pendingFacts.length;

  const trustSummary: TrustSummaryViewModel = {
    statusBadge: 'Core trip details confirmed',
    sourceNotice: 'Some trip details are confirmed from official sources. Unconfirmed items are tracked as pending.',
    governanceNotice: pack.trust_metadata?.governance || 'Governed by Timonelo Evidence Architecture',
    piiNotice: 'Personal booking details are kept out of the reusable trip knowledge shown here.',
    verifiedCount: verifiedCount,
    pendingCount: pendingCount,
    lastCheckedDate: result?.gaps?.[0]?.last_checked_on || undefined,
  };

  return {
    shipName,
    routeLabel,
    departureCity: depLoc.city,
    arrivalCity: arrLoc.city,
    dateRangeLabel,
    durationLabel,
    departure,
    arrival,
    timeline,
    confirmedFacts,
    pendingFacts,
    genericPortFacilities,
    beforeYouGo,
    trustSummary,
  };
}
