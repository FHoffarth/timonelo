import { useMemo } from 'react';
import ShipOverview from '../../ship-overview/ShipOverview';
import { buildSpatialPassengerViewModel } from '../../ship-overview/adapter';
import { SpatialPassengerViewModel, RawSpatialPayload } from '../../ship-overview/types';
import bellissimaSpatialFixture from '../../fixtures/bellissima_deck14_spatial.json';

export interface ShipOverviewPageProps {
  viewModel?: SpatialPassengerViewModel;
  rawPayload?: RawSpatialPayload;
  selectedDeckNumber?: number;
  previewNotice?: string;
}

export default function ShipOverviewPage({
  viewModel,
  rawPayload,
  selectedDeckNumber = 14,
  previewNotice,
}: ShipOverviewPageProps) {
  const activeViewModel = useMemo(() => {
    if (viewModel) return viewModel;
    const payload = rawPayload || (bellissimaSpatialFixture as unknown as RawSpatialPayload);
    return buildSpatialPassengerViewModel(payload, selectedDeckNumber);
  }, [viewModel, rawPayload, selectedDeckNumber]);

  return (
    <div className="w-full flex-1 bg-[#FBF8F3]">
      {previewNotice && (
        <div className="bg-[#0C1B2A]/5 border-b border-[#0C1B2A]/10 px-4 py-2 text-center text-xs font-mono text-[#5B6570]">
          <span>{previewNotice}</span>
        </div>
      )}
      <ShipOverview viewModel={activeViewModel} />
    </div>
  );
}

export function ReferenceShipOverviewPreview() {
  const payload = bellissimaSpatialFixture as unknown as RawSpatialPayload;
  const viewModel = buildSpatialPassengerViewModel(payload, 14);

  return (
    <ShipOverviewPage
      viewModel={viewModel}
      previewNotice="Spatial Overview Reference • MSC Bellissima (Deck 14 Geometry Proof)"
    />
  );
}

export function hasAdmittedSpatialOverview(vesselId: string | undefined | null): boolean {
  return vesselId === 'msc-bellissima';
}

export function PassengerShipOverview({ vesselId }: { vesselId?: string }) {
  if (!hasAdmittedSpatialOverview(vesselId)) {
    return (
      <div className="w-full flex-1 bg-[#FBF8F3] px-6 py-16">
        <div className="max-w-2xl mx-auto rounded-3xl border border-[#0C1B2A]/10 bg-white p-8 text-center">
          <p className="font-mono text-xs text-[#5B6570]">UNKNOWN</p>
          <h1 className="mt-3 font-display text-2xl font-bold text-[#0C1B2A]">
            No admitted spatial overview is available for this vessel
          </h1>
        </div>
      </div>
    );
  }
  return <ReferenceShipOverviewPreview />;
}
