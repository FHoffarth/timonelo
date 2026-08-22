/**
 * Deck 14 spatial proof viewer, v0.
 *
 * A proof and evidence viewer, not passenger navigation. It shows what the source
 * establishes, what was derived from it, and what the proof explicitly refuses to
 * establish — that last part being the reason the viewer exists at all.
 */

import { useEffect, useState } from "react";
import EvidenceDrawer from "./EvidenceDrawer";
import ProofCanvas from "./ProofCanvas";
import { hasAdmittedConnectivity, loadProof } from "./loadProof";
import {
  REFERENCE_FRAME_STATEMENT,
  type ProofDocument,
  type ProofObject,
} from "./proofTypes";

/**
 * Shown wherever a passenger product would offer directions.
 *
 * There is no active call to action. An enabled control that always fails reads as
 * a bug; a disabled one reads as "not built yet". Neither is the claim. The claim
 * is that Timonelo knows where these rooms are and has not established that you
 * can walk between them.
 */
export function PathfindingUnavailable({ doc }: { doc: ProofDocument }) {
  const [showDetail, setShowDetail] = useState(false);
  const corridor = doc.corridor_observation;

  return (
    <section
      data-testid="pathfinding-unavailable"
      className="rounded-2xl border border-white/10 bg-white/5 p-4 space-y-2"
    >
      <h3 className="text-[13px] text-[#F5F1EA]">
        Pathfinding not available on this deck yet
      </h3>
      <p className="text-[12px] text-[#8FA3B8] leading-relaxed">
        Timonelo can identify these locations, but verified connectivity has not been
        established.
      </p>
      <button
        type="button"
        data-testid="pathfinding-detail-toggle"
        onClick={() => setShowDetail((v) => !v)}
        className="text-[11px] text-[#C58A46] underline underline-offset-2 cursor-pointer"
      >
        {showDetail ? "Hide technical detail" : "Why?"}
      </button>
      {showDetail && (
        <div
          data-testid="pathfinding-detail"
          className="text-[11px] font-mono text-[#8FA3B8] space-y-1 pt-1"
        >
          <div data-testid="refusal-code">NOT_ROUTABLE · NO_ADMITTED_CONNECTIVITY</div>
          <div>navigation_graph: null</div>
          <div>
            corridor: {String(corridor.classification)} · accepted_geometry:{" "}
            {String(corridor.accepted_geometry)}
          </div>
          <div>nearest_core_calculation: null</div>
        </div>
      )}
    </section>
  );
}

export default function SpatialProofViewer() {
  const [doc, setDoc] = useState<ProofDocument | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<ProofObject | null>(null);
  // Default OFF. The evidence-only view is the default view: with the source
  // plan on, most visible content is unproven, so seeing it must be a choice.
  const [showUnderlay, setShowUnderlay] = useState(false);

  useEffect(() => {
    loadProof()
      .then(setDoc)
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div data-testid="proof-load-error" className="p-8 text-[13px] text-[#C58A46]">
        {error}
      </div>
    );
  }
  if (!doc) {
    return <div className="p-8 text-[13px] text-[#8FA3B8]">Loading proof…</div>;
  }

  const blocked = doc.objects.filter((o) => o.publish_status === "PUBLISH_BLOCKED").length;

  return (
    <div className="min-h-screen bg-[#0C1B2A] text-[#F5F1EA]">
      <header className="px-6 py-4 border-b border-white/10 space-y-1">
        <h1 className="text-[17px]">
          MSC Bellissima · Deck {doc.deck.number} ({doc.deck.name}) · Geometry Proof
        </h1>
        <p className="text-[11px] text-[#8FA3B8]">
          Evidence viewer. Not navigation.
        </p>
        {blocked > 0 && (
          <p
            data-testid="publish-status-banner"
            className="text-[11px] text-[#C58A46]"
          >
            {blocked} of {doc.objects.length} objects are DRAFT / UNKNOWN /
            PUBLISH_BLOCKED — pending human adjudication.
          </p>
        )}
        <p data-testid="reference-frame-banner" className="text-[11px] text-[#8FA3B8]">
          {REFERENCE_FRAME_STATEMENT}
        </p>
      </header>

      {/*
        The canvas row is height-bounded on desktop and aspect-bounded on mobile,
        and the side column scrolls inside itself. Without that, selecting an
        object grew the drawer, the drawer grew the shared grid row, and the proof
        silently rescaled as a side effect of reading its own evidence.
      */}
      <main className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-4 p-4 lg:h-[calc(100vh-172px)]">
        <div className="flex flex-col gap-2 lg:h-full lg:min-h-0">
          <div className="flex flex-wrap items-center gap-3">
            <label className="flex items-center gap-2 text-[11px] text-[#8FA3B8] cursor-pointer">
              <input
                type="checkbox"
                data-testid="underlay-toggle"
                checked={showUnderlay}
                onChange={(e) => setShowUnderlay(e.target.checked)}
              />
              Show source plan context
            </label>
            {showUnderlay && (
              <div data-testid="underlay-legend" className="flex flex-wrap items-center gap-3 text-[11px]">
                <span className="flex items-center gap-1.5 text-[#8FA3B8]">
                  <span className="inline-block w-3 h-3 bg-[#8FA3B8]/40 border border-[#8FA3B8]/60" />
                  Source plan context — not accepted evidence
                </span>
                <span className="flex items-center gap-1.5 text-[#7FB2E5]">
                  <span className="inline-block w-3 h-3 bg-[#7FB2E5]/40 border border-[#7FB2E5]" />
                  Accepted proof geometry
                </span>
              </div>
            )}
          </div>
          <div className="rounded-2xl overflow-hidden border border-white/10 aspect-[5/4] lg:aspect-auto lg:flex-1 lg:min-h-0">
            <ProofCanvas
              objects={doc.objects}
              selectedId={selected?.object_id ?? null}
              onSelect={setSelected}
              showUnderlay={showUnderlay}
            />
          </div>
        </div>

        <div className="flex flex-col gap-4 lg:h-full lg:min-h-0">
          {!hasAdmittedConnectivity(doc) && <PathfindingUnavailable doc={doc} />}
          <div className="rounded-2xl border border-white/10 bg-white/5 lg:flex-1 lg:min-h-0 lg:overflow-y-auto">
            <EvidenceDrawer object={selected} doc={doc} />
          </div>
        </div>
      </main>
    </div>
  );
}
