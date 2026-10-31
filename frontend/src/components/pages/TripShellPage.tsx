import { useMemo } from 'react';
import TripShell from '../../trip-shell/TripShell';
import { buildPassengerTripViewModel } from '../../trip-shell/adapter';
import { PassengerTripKnowledgePack, VoyageKnowledgeResult } from '../../trip-shell/types';
import referenceVoyageFixture from '../../fixtures/reference_voyage_bellissima.json';
import { LIVE_TEST_TRIP } from '../../trip-shell/liveTestContext';

export interface TripShellPageProps {
  pack: PassengerTripKnowledgePack;
  result?: VoyageKnowledgeResult;
  onBack?: () => void;
  previewNotice?: string;
}

/**
 * Generic, data-driven Trip Shell Page.
 * Strictly consumes an explicit PassengerTripKnowledgePack prop.
 */
export default function TripShellPage({ pack, result, onBack, previewNotice }: TripShellPageProps) {
  const viewModel = useMemo(() => {
    return buildPassengerTripViewModel(pack, result);
  }, [pack, result]);

  return (
    <div className="w-full flex-1 bg-[#FBF8F3]">
      {previewNotice && (
        <div className="bg-[#0C1B2A]/5 border-b border-[#0C1B2A]/10 px-4 py-2 text-center text-xs font-mono text-[#5B6570]">
          <span>{previewNotice}</span>
        </div>
      )}
      <TripShell viewModel={viewModel} />
    </div>
  );
}

/**
 * Historical product reference, never a verified booking or actual travel record.
 */
export function ReferenceTripShellPreview({ onBack }: { onBack?: () => void }) {
  const pack = referenceVoyageFixture.passenger_pack as unknown as PassengerTripKnowledgePack;
  const result = referenceVoyageFixture as unknown as VoyageKnowledgeResult;

  return (
    <TripShellPage
      pack={pack}
      result={result}
      onBack={onBack}
      previewNotice={`Past reference voyage • ${LIVE_TEST_TRIP.shortLabel} • Not a current booking`}
    />
  );
}
