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
