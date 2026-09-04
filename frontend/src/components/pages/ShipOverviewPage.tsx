import { useEffect, useMemo, useState } from 'react';
import ShipOverview from '../../ship-overview/ShipOverview';
import { buildSpatialPassengerViewModel } from '../../ship-overview/adapter';
import { SpatialPassengerViewModel, RawSpatialPayload, RawProofObject } from '../../ship-overview/types';
import { loadProof } from '../../spatial-proof/loadProof';
import type { ProofDocument } from '../../spatial-proof/proofTypes';

/**
 * The passenger Ships surface.
 *
 * Its spatial payload is the governed Deck 14 geometry proof, served at
 * `/data/deck14.proof.json` and byte-identical to
 * `geometry/proofs/bellissima/deck14/deck14.proof.json`.
 *
 * It used to be `src/fixtures/bellissima_deck14_spatial.json`, which carries the
 * same 244 object ids and the same normalized bounding boxes as the governed
 * proof but with the lifecycle axes rewritten -- UNKNOWN to SUPPORTED, DRAFT to
 * APPROVED, PUBLISH_BLOCKED to PUBLISH_ALLOWED. Every object passed the
 * adapter's admission gate on the strength of axes nobody had adjudicated, and
 * the page told passengers it was showing "244 verified spaces" of "reviewed,
 * publication-approved spatial data". The gate was never wrong; it was being
 * handed pre-adjudicated input.
 *
 * Reading the governed proof makes the page self-correcting in both directions:
 * today no object is admitted and the passenger sees an honest pending state,
 * and if Deck 14 is ever adjudicated the same code shows what was admitted,
 * without anyone editing a claim. The fixture remains where it belongs, as a
 * test payload proving the gate admits when it should.
 */
export interface ShipOverviewPageProps {
  viewModel?: SpatialPassengerViewModel;
  rawPayload?: RawSpatialPayload;
  selectedDeckNumber?: number;
  previewNotice?: string;
}

/** Reshapes the governed proof into the adapter's input. Admission is not touched. */
export function payloadFromProof(proof: ProofDocument): RawSpatialPayload {
  return {
    ship: {
      name: 'MSC Bellissima',
      decks: [{ number: 14, name: 'Deck 14 (Magico)', has_geometry: true }],
    },
    deck14_proof: {
      schema: proof.schema,
      deck: { number: proof.deck.number, name: proof.deck.name },
      // Passed through unchanged, lifecycle axes included. The adapter decides
      // what is admitted; this function decides nothing.
      objects: (proof.objects ?? []) as unknown as RawProofObject[],
    },
    known_unmapped_venues: [],
    trust_metadata: {
      governance: 'Governed by Timonelo Evidence Architecture',
      source_artifact: 'ART-0001 (Deck 14 Geometry Proof)',
    },
  };
}

export default function ShipOverviewPage({
  viewModel,
  rawPayload,
  selectedDeckNumber = 14,
  previewNotice,
}: ShipOverviewPageProps) {
  const activeViewModel = useMemo(() => {
    if (viewModel) return viewModel;
    if (rawPayload) return buildSpatialPassengerViewModel(rawPayload, selectedDeckNumber);
    return null;
  }, [viewModel, rawPayload, selectedDeckNumber]);

  if (!activeViewModel) return null;

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

export function hasAdmittedSpatialOverview(vesselId: string | undefined | null): boolean {
  return vesselId === 'msc-bellissima';
}

function SpatialShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="w-full flex-1 bg-[#FBF8F3] px-6 py-16">
      <div className="max-w-2xl mx-auto rounded-3xl border border-[#0C1B2A]/10 bg-white p-8 text-center space-y-3">
        {children}
      </div>
    </div>
  );
}

export function PassengerShipOverview({ vesselId }: { vesselId?: string }) {
  const [proof, setProof] = useState<ProofDocument | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let live = true;
    loadProof()
      .then((doc) => { if (live) setProof(doc); })
      .catch(() => { if (live) setFailed(true); });
    return () => { live = false; };
  }, []);

  if (!hasAdmittedSpatialOverview(vesselId)) {
    return (
      <SpatialShell>
        <h1 className="font-display text-2xl font-bold text-[#0C1B2A]">
          We have not mapped this ship yet
        </h1>
        <p className="text-sm text-[#5B6570] leading-relaxed">
          Timonelo only shows deck layouts once they have been checked against the
          operator&apos;s own drawings. This ship has not been through that yet.
        </p>
      </SpatialShell>
    );
  }

  // A proof that cannot be read is not permission to show something else. The
  // fixture is deliberately unreachable from here, so there is nothing to fall
  // back to and nothing that could quietly present unchecked geometry instead.
  if (failed) {
    return (
      <SpatialShell>
        <h1 className="font-display text-2xl font-bold text-[#0C1B2A]">
          Deck plans are unavailable right now
        </h1>
        <p className="text-sm text-[#5B6570] leading-relaxed">
          We could not open the source deck plan for this ship. Nothing is wrong
          with your booking — please try again in a moment.
        </p>
      </SpatialShell>
    );
  }

  if (!proof) {
    return (
      <SpatialShell>
        <p className="text-sm text-[#5B6570]">Opening deck plans…</p>
      </SpatialShell>
    );
  }

  return (
    <ShipOverviewPage
      rawPayload={payloadFromProof(proof)}
      previewNotice="MSC Bellissima • Deck 14, from the operator's own deck plan"
    />
  );
}
