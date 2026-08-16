/**
 * Boarding Intelligence (Presentation layer, Plane 5).
 *
 * Translates ship language (port/starboard, frame zones, elevator cores) into
 * how a first-time passenger actually thinks: "do I turn left or right?".
 * It removes no precision — the authoritative hull side and measured distances
 * still drive every statement; this module only presents them naturally.
 *
 * No routing logic is duplicated: turns come from the authoritative hull_side
 * (Spatial Ontology) and step counts from the Spatial Calculus distances.
 */
import type { ShipData, CabinData } from './types';

export type HullSide = CabinData['hull_side'];
export type Turn = 'left' | 'right' | 'ahead';

/** Even/odd cabin conventions are per-operator and configurable, never global. */
export interface CabinConvention {
  operatorMatch: RegExp;
  label: string;
  even: HullSide;
  odd: HullSide;
}

const CONVENTIONS: CabinConvention[] = [
  // MSC Cruises: even cabins starboard, odd cabins port.
  { operatorMatch: /msc/i, label: 'MSC even/odd convention', even: 'STARBOARD', odd: 'PORT' },
];

export function conventionFor(ship: ShipData): CabinConvention | null {
  const hay = `${ship.name}`;
  return CONVENTIONS.find((c) => c.operatorMatch.test(hay)) ?? null;
}

export function isEven(cabinNumber: string): boolean | null {
  const m = cabinNumber.match(/(\d)\D*$/);
  return m ? Number(m[1]) % 2 === 0 : null;
}

export function turnFromSide(side: HullSide): Turn {
  return side === 'STARBOARD' ? 'right' : side === 'PORT' ? 'left' : 'ahead';
}

/** Human translation of a hull side (Feature 6). Maritime terms stay elsewhere. */
export function humanSide(side: HullSide): string {
  return side === 'STARBOARD' ? 'the right side of the ship' : side === 'PORT' ? 'the left side of the ship' : 'the centre of the ship';
}

export function longitudinalLabel(zone: string): 'aft' | 'forward' | 'midship' {
  const z = zone.toLowerCase();
  if (z.includes('aft')) return 'aft';
  if (z.includes('forward') || z.includes('bow')) return 'forward';
  return 'midship';
}

export function elevatorLabel(zone: string): string {
  const l = longitudinalLabel(zone);
  return l === 'aft' ? 'aft elevators' : l === 'forward' ? 'forward elevators' : 'nearest elevators';
}

export interface ParityInsight {
  even: boolean;
  side: HullSide;
  turn: Turn;
  convention: CabinConvention | null;
  /** true when the ship's convention explains this cabin's side (safe mnemonic). */
  conventionExplains: boolean;
}

export function parityInsight(ship: ShipData, cabin: CabinData): ParityInsight | null {
  const even = isEven(cabin.cabin_number);
  if (even === null) return null;
  const convention = conventionFor(ship);
  const expected = convention ? (even ? convention.even : convention.odd) : null;
  return {
    even,
    side: cabin.hull_side,
    turn: turnFromSide(cabin.hull_side),
    convention,
    conventionExplains: expected != null && expected === cabin.hull_side,
  };
}

export interface FirstWalkStep {
  text: string;
}

/** "First walk to your cabin" — generated from ontology + calculus, no invention. */
export function firstWalk(cabin: CabinData): FirstWalkStep[] {
  const turn = turnFromSide(cabin.hull_side);
  const elev = cabin.distances.elevator;
  const steps: FirstWalkStep[] = [];
  steps.push({ text: `Leave the ${elevatorLabel(cabin.zone)} on Deck ${cabin.deck_number}.` });
  if (turn !== 'ahead') {
    steps.push({ text: `Turn ${turn} — toward ${humanSide(cabin.hull_side)}.` });
  } else {
    steps.push({ text: `Continue straight ahead along the corridor.` });
  }
  if (elev) {
    steps.push({ text: `Walk about ${elev.steps} steps (${elev.meters} m) along the corridor.` });
  }
  steps.push({ text: `Cabin ${cabin.cabin_number} is on ${humanSide(cabin.hull_side)}.` });
  return steps;
}

export interface ReturnJourney {
  id: string;
  from: string;
  text: string;
}

const RETURN_LABELS: Record<string, string> = {
  buffet: 'the buffet',
  theater: 'the theatre',
  pool: 'the pool',
  dining: 'the main dining room',
  elevator: 'the lifts',
};

export function returnJourneys(cabin: CabinData): ReturnJourney[] {
  const turn = turnFromSide(cabin.hull_side);
  const out: ReturnJourney[] = [];
  for (const key of ['buffet', 'theater', 'pool', 'dining'] as const) {
    const d = cabin.distances[key];
    if (!d) continue;
    out.push({
      id: key,
      from: RETURN_LABELS[key],
      text: `Take a lift to Deck ${cabin.deck_number}, then turn ${turn} toward ${humanSide(cabin.hull_side)} — about ${d.steps} steps back to your door.`,
    });
  }
  // Always include the aft-elevator return as the reliable anchor.
  const elev = cabin.distances.elevator;
  if (elev) {
    out.push({
      id: 'elevator',
      from: `the ${elevatorLabel(cabin.zone)}`,
      text: `Step out, turn ${turn}, and walk about ${elev.steps} steps to Cabin ${cabin.cabin_number}.`,
    });
  }
  return out;
}

export interface OrientationMoment {
  id: string;
  label: string;
  guidance: string;
}

/** Orientation Moments — presentation concepts, not backend entities. */
export function orientationMoments(cabin: CabinData): OrientationMoment[] {
  const turn = turnFromSide(cabin.hull_side);
  const elev = cabin.distances.elevator;
  const buffet = cabin.distances.buffet;
  const theater = cabin.distances.theater;
  const back = elev ? `turn ${turn} and walk about ${elev.steps} steps` : `turn ${turn} along the corridor`;
  const moments: OrientationMoment[] = [
    { id: 'finding-cabin', label: 'Finding your cabin', guidance: `From the ${elevatorLabel(cabin.zone)}, ${back} to Cabin ${cabin.cabin_number} on ${humanSide(cabin.hull_side)}.` },
    { id: 'leaving-cabin', label: 'Leaving your cabin', guidance: `Turn ${turn === 'left' ? 'right' : turn === 'right' ? 'left' : 'back'} out of your door to reach the ${elevatorLabel(cabin.zone)}.` },
    { id: 'returning-dinner', label: 'Returning after dinner', guidance: buffet ? `From the buffet, ride to Deck ${cabin.deck_number}; ${back} to your door.` : `Ride to Deck ${cabin.deck_number}; ${back} to your door.` },
    { id: 'returning-theatre', label: 'Returning after the theatre', guidance: theater ? `From the theatre on a lower deck, take a lift to Deck ${cabin.deck_number}, then ${back}.` : `Take a lift to Deck ${cabin.deck_number}, then ${back}.` },
    { id: 'finding-lifts', label: 'Finding the lifts', guidance: `Your nearest lifts are the ${elevatorLabel(cabin.zone)}${elev ? `, about ${elev.steps} steps from your door` : ''}.` },
    { id: 'muster', label: 'Finding your muster station', guidance: `Your muster station is printed on your cruise card — check it before the safety drill on boarding day.` },
  ];
  return moments;
}
