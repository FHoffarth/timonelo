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
  ReferenceFactViewModel,
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

  // Reference values carry no verification authority.
  const departure: PortStatusViewModel = {
    city: depLoc.city,
    country: depLoc.country,
    rawLocation: pack.departure_location,
    dateFormatted: formatDateShort(pack.departure_date),
    timeFormatted: pack.check_in_time ? `Check-in: ${pack.check_in_time}` : null,
    timeLabel: pack.check_in_time ? 'Check-in' : null,
    terminalStatusText: 'Not confirmed yet',
    berthStatusText: 'Not assigned yet',
    isConfirmed: false,
    unlocode: pack.departure_port_unlocode,
  };

  // Missing terminal and berth assignments remain unknown.
  const arrival: PortStatusViewModel = {
    city: arrLoc.city,
    country: arrLoc.country,
    rawLocation: pack.arrival_location,
    dateFormatted: formatDateShort(pack.arrival_date),
    terminalStatusText: 'Not confirmed yet',
    berthStatusText: 'Not assigned yet',
    isConfirmed: false,
    unlocode: pack.arrival_port_unlocode,
  };

  // Timeline describes reference inputs, not confirmed events.
  const timeline: TimelineDayViewModel[] = [];

  const depDateObj = parseIsoDate(pack.departure_date);
  const arrDateObj = parseIsoDate(pack.arrival_date);

  // Day 1: Embarkation / Departure
  const day1Events = [];
  if (pack.check_in_time) {
    day1Events.push({
      label: 'Check-in',
      time: pack.check_in_time,
      note: 'Check-in time recorded in reference data; not independently verified.',
    });
  } else {
    day1Events.push({
      label: 'Embarkation',
      note: 'Check-in time is not available in this reference.',
    });
  }

  timeline.push({
    dateFormatted: formatDateShort(pack.departure_date),
    dayOfWeek: depDateObj ? DAY_NAMES[depDateObj.getDay()] : undefined,
    locationTitle: `${depLoc.city}, Embarkation`,
    status: 'info',
    statusBadge: 'Reference data',
    events: day1Events,
  });

  // Final Day: Arrival / Debarkation
  timeline.push({
    dateFormatted: formatDateShort(pack.arrival_date),
    dayOfWeek: arrDateObj ? DAY_NAMES[arrDateObj.getDay()] : undefined,
    locationTitle: `${arrLoc.city}, Destination`,
    status: 'info',
    statusBadge: 'Reference data',
    events: [
      {
        label: 'Arrival',
        note: 'Terminal and berth details are not established by this reference.',
      },
    ],
  });

  const referenceFacts: ReferenceFactViewModel[] = [
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
    referenceFacts.push({
      label: 'Check-in Time',
      value: pack.check_in_time,
      category: 'timing',
    });
  }

  if (durationLabel) {
    referenceFacts.push({
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
      whatNext: 'This reference does not establish the terminal or berth used.',
    },
    {
      label: 'Arrival Terminal & Berth',
      statusText: 'Not confirmed yet',
      whyPending: 'Specific arrival terminal and berth details are not confirmed yet.',
      whatNext: 'This reference does not establish the terminal or berth used.',
    },
  ];

  // Generic Destination Port Facilities (strictly separated from voyage-specific facts)
  const genericPortFacilities: GenericFacilityViewModel[] = (
    pack.known_generic_infrastructure || []
  ).map(f => ({
    name: f.name,
    notice: 'Facility listed in reference data — not verified or assigned to this voyage.',
    facilityType: 'Cruise Terminal',
  }));

  // Before You Go Checklist (passenger guidance)
  const beforeYouGo: BeforeYouGoItemViewModel[] = [
    {
      title: 'Terminal and berth remain unknown',
      description: 'No voyage-specific assignment is established by this reference.',
      iconName: 'terminal',
    },
    {
      title: 'Reference data is not a booking',
      description: 'The displayed values are example context, not an independently verified travel record.',
      iconName: 'documents',
    },
    {
      title: 'No operational travel guidance',
      description: 'Do not use this reference for current check-in or port travel decisions.',
      iconName: 'port',
    },
  ];

  // Trust Summary - Scoped and Measured
  const verifiedCount = 0;
  const pendingCount = result?.gaps?.length || pendingFacts.length;

  const trustSummary: TrustSummaryViewModel = {
    statusBadge: 'Unverified reference data',
    sourceNotice: 'These values come from reference data and have not been independently verified. They do not confirm a booking or actual travel.',
    governanceNotice: 'Reference data does not establish evidence or publication approval.',
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
    referenceFacts,
    pendingFacts,
    genericPortFacilities,
    beforeYouGo,
    trustSummary,
  };
}
