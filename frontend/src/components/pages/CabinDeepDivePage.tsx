import { useMemo } from "react";
import { LegacyEpistemicBadge } from "../ui/EpistemicBadge";
import { CANONICAL_CABINS } from "../../data/canonicalPlatformData";
import { isKnownCabin, resolveCabinMeta } from "../../data/cabinResolution";
import { knowledgeRepository } from "../../knowledge";
import {
  isSpatialVesselRegistered,
  TimoneloSpatialApiClient,
} from "../../semantic-deck/apiClient";
import { SemanticEntity } from "../../semantic-deck/types";
import {
  isPassengerEntityAdmitted,
  isPassengerFactAdmitted,
  type PassengerFactKey,
} from "../../semantic-deck/passengerAdmission";
import CabinIntelligenceCard from "../../intelligence/CabinIntelligenceCard";
import ExplainabilityCard from "../../explainability/ExplainabilityCard";
import { ArrowLeft, MapPin, HelpCircle } from "lucide-react";

interface CabinDeepDivePageProps {
  vesselId?: string;
  cabinId?: string;
  onBack: () => void;
}

export default function CabinDeepDivePage({
  vesselId,
  cabinId,
  onBack,
}: CabinDeepDivePageProps) {
  const apiClient = useMemo(
    () =>
      isSpatialVesselRegistered(vesselId)
        ? new TimoneloSpatialApiClient(vesselId!)
        : null,
    [vesselId],
  );

  // P0-D FAIL-CLOSED: only treat this cabin as known if it is backed by real
  // data — a canonical record OR a real spatial-graph entity. Unknown IDs must
  // never be substituted with cabin 14122, nor have facts fabricated for them.
  const canonicalCandidate = cabinId ? CANONICAL_CABINS[cabinId] : undefined;
  const canonicalCabin =
    canonicalCandidate?.shipSlug === vesselId ? canonicalCandidate : undefined;
  const knownEntity =
    vesselId && cabinId ? apiClient?.getEntityForVessel(vesselId, cabinId) : undefined;
  const vesselCanonicalCabins =
    cabinId && canonicalCabin ? { [cabinId]: canonicalCabin } : {};
  const cabinIsKnown = isKnownCabin(
    cabinId,
    vesselCanonicalCabins,
    (id) => (vesselId ? apiClient?.getEntityForVessel(vesselId, id) : undefined),
  );
  const cabinIsPassengerAdmitted = Boolean(
    knownEntity &&
      isPassengerEntityAdmitted(knownEntity, vesselId) &&
      isPassengerFactAdmitted(knownEntity, "identity", vesselId),
  );

  // Metadata resolution (P0-D follow-up): a graph-only cabin (present in the
  // spatial graph but absent from CANONICAL_CABINS) renders ONLY its own
  // available data. It must NOT borrow cabin 14122's category / sqm / hero
  // image / deck name / PRM flag. Fields the graph does not carry stay null and
  // render as "Unavailable" below (null, never another cabin's value). The
  // No cross-cabin fallback: absence stays absent.
  const fallbackCabin: any =
    vesselId && cabinId
      ? resolveCabinMeta(vesselId, cabinId, canonicalCabin, knownEntity)
      : null;

  // Query knowledge layer for Bellissima stateroom
  const isBellissima = fallbackCabin?.shipSlug === "msc-bellissima";
  const bellissimaShip = isBellissima ? knowledgeRepository.getShip("msc-bellissima") : null;
  const bellissimaDeck = isBellissima && fallbackCabin
    ? knowledgeRepository.getDeck("msc-bellissima", fallbackCabin.deckNumber)
    : null;
  const shipName = bellissimaShip ? bellissimaShip.vessel_name : "Unavailable";
  const deckName = bellissimaDeck ? bellissimaDeck.name : fallbackCabin?.deckName || "Unavailable";

  // The passenger surface consumes an admitted spatial entity or nothing.
  // Canonical-looking metadata and schematic graph presence are not enough.
  const stateroomEntity: SemanticEntity | undefined = cabinIsPassengerAdmitted
    ? knownEntity
    : undefined;

  // P0-D FAIL-CLOSED: unknown cabin IDs render a calm "unavailable" state. We do
  // NOT substitute another cabin, invoke cabin intelligence / explainability on
  // fabricated data, or emit any DIRECT / PUBLISHED_VERIFIED / confidence /
  // adjacency / overhead / underfoot claims.
  if (!cabinIsKnown || !stateroomEntity || !fallbackCabin) {
    return (
      <div className="flex-1 flex flex-col bg-[#FBF8F3] select-none pb-20">
        <div className="max-w-7xl mx-auto w-full px-6 pt-10 pb-6 space-y-3">
          <button
            onClick={onBack}
            className="inline-flex items-center gap-1.5 text-xs text-[#5B6570] hover:text-[#0C1B2A] transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back</span>
          </button>
        </div>

        <div className="max-w-2xl mx-auto w-full px-6 pt-8">
          <div className="p-8 bg-white rounded-3xl border border-[#0C1B2A]/10 shadow-card space-y-4 text-center">
            <div className="mx-auto w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center">
              <HelpCircle className="w-6 h-6 text-slate-400" />
            </div>
            <div className="flex items-center justify-center">
              <LegacyEpistemicBadge status="UNKNOWN" />
            </div>
            <h1 className="font-display text-2xl sm:text-3xl font-bold text-[#0C1B2A] tracking-tight">
              Cabin {cabinId || "unknown"} has no admitted passenger briefing
            </h1>
            <p className="text-sm text-[#5B6570] leading-relaxed">
              A schematic or unreviewed record may exist, but it has not crossed
              the evidence gate. Location, adjacency, lift, route, and cabin
              intelligence remain unavailable.
            </p>
            <button
              onClick={onBack}
              className="inline-flex items-center gap-1.5 mt-2 px-4 py-2 rounded-xl bg-[#0C1B2A] text-white text-xs font-semibold hover:bg-[#0C1B2A]/90 transition-colors cursor-pointer"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Return to ship</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  const passengerFactIsAdmitted = (fact: PassengerFactKey): boolean =>
    isPassengerFactAdmitted(stateroomEntity, fact, vesselId);

  return (
    <div className="flex-1 flex flex-col bg-[#FBF8F3] select-none pb-20">
      {/* 1. Breadcrumbs & Title */}
      <div className="max-w-7xl mx-auto w-full px-6 pt-10 pb-6 space-y-3">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-xs text-[#5B6570] hover:text-[#0C1B2A] transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>{shipName}</span>
          <span>&gt;</span>
          <span>Deck {fallbackCabin.deckNumber} ({deckName})</span>
          <span>&gt;</span>
          <span className="font-semibold text-[#0C1B2A]">Cabin {fallbackCabin.id}</span>
        </button>

        <h1 className="font-display text-4xl sm:text-5xl font-bold text-[#0C1B2A] tracking-tight">
          Cabin {fallbackCabin.id} Analysis
        </h1>
      </div>

      {/* 2. Hero Photography with Floating Glass Pill */}
      <div className="max-w-7xl mx-auto w-full px-6 pb-10">
        <div className="relative w-full h-[360px] sm:h-[420px] rounded-3xl overflow-hidden shadow-lg">
          {fallbackCabin.heroImageUrl ? (
            <img
              src={fallbackCabin.heroImageUrl}
              alt={`Cabin ${fallbackCabin.id}`}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-slate-100 flex items-center justify-center text-xs font-mono text-slate-400 uppercase tracking-wider">
              No cabin photography available
            </div>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-[#0C1B2A]/50 to-transparent" />

          {/* Floating Pill Metadata */}
          <div className="absolute bottom-6 left-6 flex items-center gap-3 px-5 py-2.5 rounded-2xl bg-white/95 backdrop-blur-md shadow-xl border border-white/40 text-xs sm:text-sm font-sans font-medium text-[#0C1B2A]">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="font-bold">
              {passengerFactIsAdmitted("classification")
                ? fallbackCabin.category
                : "Category unavailable"}
            </span>
            <span>•</span>
            <span>{passengerFactIsAdmitted("deck")
              ? `Deck ${fallbackCabin.deckNumber}`
              : "Deck unavailable"}</span>
            <span>•</span>
            <span className="text-[#5B6570]">
              {passengerFactIsAdmitted("side")
                ? `${fallbackCabin.side} Side`
                : "Side unavailable"}
            </span>
            {passengerFactIsAdmitted("accessible_designation") && fallbackCabin.isPRM && (
              <>
                <span>•</span>
                <span className="px-2 py-0.5 rounded-full bg-sky-100 text-sky-800 text-xs font-bold">
                  PRM Accessible (H)
                </span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* 3. Cabin Intelligence Summary Card */}
      <div className="max-w-7xl mx-auto w-full px-6 pb-8">
        <CabinIntelligenceCard entity={stateroomEntity} vesselId={vesselId!} />
      </div>

      {/* 4. Explainability Engine Trace Card (Evidence -> Rule -> Score) */}
      <div className="max-w-7xl mx-auto w-full px-6 pb-12">
        <ExplainabilityCard entity={stateroomEntity} vesselId={vesselId!} />
      </div>

      {/* 5. Spatial Geometry & Quick Facts Layout */}
      <div className="max-w-7xl mx-auto w-full px-6 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Stateroom Amenities & Stack Elevation */}
        <div className="lg:col-span-2 space-y-8">
          {/* Elevation Stack */}
          <div className="p-6 bg-white rounded-3xl border border-[#0C1B2A]/10 shadow-card space-y-4">
            <div className="flex items-center justify-between text-xs font-mono text-slate-500 uppercase">
              <span>Vertical Relations</span>
              <span className="text-[#C58A46]">Evidence-gated</span>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-slate-500">DECK {fallbackCabin.deckNumber + 1} OVERHEAD</span>
                <span className="text-slate-700 font-semibold">
                  {passengerFactIsAdmitted("adjacent_overhead")
                    ? stateroomEntity.relations.adjacent_overhead || "None established"
                    : "Unavailable"}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-sky-50 border border-sky-200 font-bold text-sky-900">
                <span className="flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-sky-600" />
                  DECK {fallbackCabin.deckNumber} ({deckName})
                </span>
                <span>Cabin {fallbackCabin.id} (Inspected Space)</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-slate-500">DECK {fallbackCabin.deckNumber - 1} UNDERFOOT</span>
                <span className="text-slate-700 font-semibold">
                  {passengerFactIsAdmitted("adjacent_underfoot")
                    ? stateroomEntity.relations.adjacent_underfoot || "None established"
                    : "Unavailable"}
                </span>
              </div>
            </div>
          </div>

        </div>

        {/* Right Col: Quick Facts Card */}
        <div className="p-6 bg-white rounded-3xl border border-[#0C1B2A]/10 shadow-card space-y-5 self-start">
          <h3 className="font-display text-2xl font-bold text-[#0C1B2A]">
            Quick Facts
          </h3>

          <div className="space-y-4 text-xs">
            {/* Category */}
            <div className="space-y-1 pb-3 border-b border-[#0C1B2A]/5">
              <div className="flex items-center justify-between text-slate-500">
                <span>Category</span>
                <LegacyEpistemicBadge status={passengerFactIsAdmitted("classification") ? "KNOWN" : "UNKNOWN"} />
              </div>
              <div className="font-bold text-[#0C1B2A] text-sm">
                {passengerFactIsAdmitted("classification")
                  ? `${fallbackCabin.category}${fallbackCabin.tier ? ` (${fallbackCabin.tier})` : ""}`
                  : "Unavailable"}
              </div>
            </div>

            {/* Size */}
            <div className="space-y-1 pb-3 border-b border-[#0C1B2A]/5">
              <div className="flex items-center justify-between text-slate-500">
                <span>Size</span>
                <LegacyEpistemicBadge status={passengerFactIsAdmitted("interior_area") && fallbackCabin.sqmInterior != null ? "KNOWN" : "UNKNOWN"} />
              </div>
              <div className="font-bold text-[#0C1B2A] text-sm">
                {passengerFactIsAdmitted("interior_area") && fallbackCabin.sqmInterior != null
                  ? `Approx. ${fallbackCabin.sqmInterior}m² ${passengerFactIsAdmitted("balcony_area") && fallbackCabin.sqmBalcony > 0 ? `+ ${fallbackCabin.sqmBalcony}m² balcony` : ""}`
                  : "Unavailable"}
              </div>
            </div>

            {/* Bed Config */}
            <div className="space-y-1 pb-3 border-b border-[#0C1B2A]/5">
              <div className="flex items-center justify-between text-slate-500">
                <span>Bed Config</span>
                <LegacyEpistemicBadge status={passengerFactIsAdmitted("bed_configuration") && fallbackCabin.bedConfig ? "KNOWN" : "UNKNOWN"} />
              </div>
              <div className="font-bold text-[#0C1B2A] text-sm">
                {passengerFactIsAdmitted("bed_configuration")
                  ? fallbackCabin.bedConfig || "Unavailable"
                  : "Unavailable"}
              </div>
            </div>

            {/* Connecting */}
            {passengerFactIsAdmitted("connecting_cabin") && fallbackCabin.connectingCabinId && (
              <div className="space-y-1 pb-3 border-b border-[#0C1B2A]/5">
                <div className="flex items-center justify-between text-slate-500">
                  <span>Connecting Door</span>
                  <LegacyEpistemicBadge status="KNOWN" />
                </div>
                <div className="font-bold text-[#0C1B2A] text-sm">
                  Cabin {fallbackCabin.connectingCabinId}
                </div>
              </div>
            )}

            {/* Evidence Artifact */}
            <div className="space-y-1 pt-1">
              <div className="flex items-center justify-between text-slate-500">
                <span>Originating Artifact</span>
                <LegacyEpistemicBadge status={passengerFactIsAdmitted("source_artifact") && fallbackCabin.evidenceArtifactId ? "KNOWN" : "UNKNOWN"} />
              </div>
              <div className="font-mono font-bold text-[#C58A46] text-xs">
                {passengerFactIsAdmitted("source_artifact")
                  ? fallbackCabin.evidenceArtifactId || "Unavailable"
                  : "Unavailable"}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
