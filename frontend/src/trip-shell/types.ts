/**
 * Passenger Trip Shell v1 Types (ADR-0002).
 * Strictly defines the source contract and passenger view model.
 */

// --- Source Contract (Factory Output) ---

export interface GenericInfrastructureFacility {
  entity_id: string;
  name: string;
  notice: string;
}

export interface TrustMetadata {
  governance: string;
  truth_model: string;
  pii_isolation: string;
  [key: string]: unknown;
}

export interface PassengerTripKnowledgePack {
  voyage_entity: string;
  vessel_name: string;
  departure_date: string;
  departure_location: string;
  departure_port_unlocode: string | null;
  arrival_date: string;
  arrival_location: string;
  arrival_port_unlocode: string | null;
  check_in_time: string | null;
  departure_terminal_status: string;
  departure_berth_status: string;
  arrival_terminal_status: string;
  arrival_berth_status: string;
  known_generic_infrastructure: GenericInfrastructureFacility[];
  trust_metadata: TrustMetadata;
  next_evidence_gaps: string[];
}

export interface VoyageGapRecord {
  question_id: string;
  statement_type: string;
  status: string;
  reason: string;
  needed_source_class: string;
  authoritative_source_family: string;
  recheck_strategy: string;
  recheck_window?: string | null;
  last_checked_on?: string;
}

export interface KnownFactRecord {
  question_id: string;
  value: unknown;
  statement_id?: string | null;
}

export interface VoyageKnowledgeResult {
  voyage_entity: string;
  input_vessel: string;
  input_departure_date: string;
  input_departure_location: string;
  input_arrival_date: string;
  input_arrival_location: string;
  input_check_in_time?: string | null;
  vessel?: string | null;
  departure_port?: string | null;
  arrival_port?: string | null;
  departure_date?: string | null;
  departure_location?: string | null;
  arrival_date?: string | null;
  arrival_location?: string | null;
  check_in_time?: string | null;
  departure_terminal?: string | null;
  departure_berth?: string | null;
  arrival_terminal?: string | null;
  arrival_berth?: string | null;
  known_facts: KnownFactRecord[];
  gaps: VoyageGapRecord[];
  publishability: string;
  passenger_pack?: PassengerTripKnowledgePack | null;
}

// --- Passenger View Model ---

export interface PortStatusViewModel {
  city: string;
  country: string;
  rawLocation: string;
  dateFormatted: string;
  timeFormatted?: string | null;
  timeLabel?: string | null;
  terminalStatusText: string;
  berthStatusText: string;
  isConfirmed: boolean;
  unlocode?: string | null;
}

export interface TimelineEventViewModel {
  label: string;
  time?: string | null;
  badge?: string | null;
  note?: string | null;
}

export interface TimelineDayViewModel {
  dateFormatted: string;
  dayOfWeek?: string;
  locationTitle: string;
  status: 'confirmed' | 'pending' | 'info';
  statusBadge: string;
  events: TimelineEventViewModel[];
}

export interface ConfirmedFactViewModel {
  label: string;
  value: string;
  category: 'ship' | 'date' | 'port' | 'timing';
}

export interface PendingFactViewModel {
  label: string;
  statusText: string;
  whyPending: string;
  whatNext: string;
}

export interface GenericFacilityViewModel {
  name: string;
  notice: string;
  facilityType: string;
}

export interface BeforeYouGoItemViewModel {
  title: string;
  description: string;
  iconName: 'terminal' | 'documents' | 'port';
}

export interface TrustSummaryViewModel {
  statusBadge: string;
  sourceNotice: string;
  governanceNotice: string;
  piiNotice: string;
  verifiedCount: number;
  pendingCount: number;
  lastCheckedDate?: string;
}

export interface PassengerTripViewModel {
  shipName: string;
  routeLabel: string;
  departureCity: string;
  arrivalCity: string;
  dateRangeLabel: string;
  durationLabel: string | null;
  departure: PortStatusViewModel;
  arrival: PortStatusViewModel;
  timeline: TimelineDayViewModel[];
  confirmedFacts: ConfirmedFactViewModel[];
  pendingFacts: PendingFactViewModel[];
  genericPortFacilities: GenericFacilityViewModel[];
  beforeYouGo: BeforeYouGoItemViewModel[];
  trustSummary: TrustSummaryViewModel;
}