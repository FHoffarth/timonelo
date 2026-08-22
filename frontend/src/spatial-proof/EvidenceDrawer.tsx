/**
 * Per-object provenance panel.
 *
 * Every value shown is read straight from the artifact. Nothing is computed,
 * rounded for display, or converted into a unit. Coordinates appear as
 * provenance, explicitly labelled as page fractions, never as a measurement.
 */

import { useState } from "react";

import {
  UNKNOWN_FEATURES_COPY,
  featuresForCabin,
  type CabinFeature,
  type FeatureDocument,
} from "./cabinFeatures";
import {
  REFERENCE_FRAME_STATEMENT,
  type ProofDocument,
  type ProofObject,
} from "./proofTypes";

function Group({ title }: { title: string }) {
  return (
    <h3 className="pt-3 pb-1 text-[10px] uppercase tracking-[0.14em] text-[#C58A46]/80">
      {title}
    </h3>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5 py-1.5 border-b border-white/10">
      <span className="text-[10px] uppercase tracking-wider text-[#8FA3B8]">{label}</span>
      <span className="text-[12px] text-[#F5F1EA] font-mono break-all">{value}</span>
    </div>
  );
}

/**
 * One positively evidenced feature, with its provenance one click away.
 *
 * The feature line states what the operator printed. The provenance panel
 * states where that was read and how far it is from being publishable — every
 * one of these is DRAFT and PUBLISH_BLOCKED, and hiding that behind a clean
 * bullet would overstate what is known.
 */
function FeatureItem({ feature }: { feature: CabinFeature }) {
  const [open, setOpen] = useState(false);
  return (
    <li data-testid="cabin-feature" data-family={feature.family_id} className="py-1">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-[12px] text-[#F5F1EA]">• {feature.label_en}</span>
        <button
          type="button"
          data-testid="feature-provenance-toggle"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          className="text-[10px] uppercase tracking-wider text-[#C58A46] hover:underline shrink-0"
        >
          Evidence
        </button>
      </div>
      <div
        data-testid="feature-provenance"
        hidden={!open}
        className="mt-1 pl-3 border-l border-white/10 space-y-0.5"
      >
        <p className="text-[10px] text-[#8FA3B8]">
          Official MSC deck plan ({feature.artifact_id}), page {feature.page}
        </p>
        <p className="text-[10px] text-[#8FA3B8] break-all">{feature.locator}</p>
        <p className="text-[10px] text-[#8FA3B8]">
          Legend symbol: {feature.legend_de}
        </p>
        <p className="text-[10px] text-[#8FA3B8]">
          {feature.statement_id} · {feature.statement_type} · {feature.question_id}
        </p>
        <p className="text-[10px] text-[#8FA3B8]">
          Method {feature.method} · {feature.human_review_state} ·{" "}
          {feature.evidence_condition} · {feature.publish_status}
        </p>
        {feature.derivation_note && (
          <p className="text-[10px] text-[#8FA3B8] leading-relaxed">
            {feature.derivation_note}
          </p>
        )}
      </div>
    </li>
  );
}

export function CabinFeatures({
  object,
  features,
}: {
  object: ProofObject;
  features: FeatureDocument | null;
}) {
  if (object.semantic_type !== "cabin") return null;
  const found = featuresForCabin(features, object.cabin_number);
  return (
    <section data-testid="cabin-features">
      <Group title="Cabin features" />
      {found.length > 0 ? (
        <ul data-testid="cabin-feature-list" className="space-y-0.5">
          {found.map((feature) => (
            <FeatureItem key={feature.statement_id} feature={feature} />
          ))}
        </ul>
      ) : (
        <p
          data-testid="cabin-features-unknown"
          className="text-[11px] text-[#8FA3B8] leading-relaxed"
        >
          {UNKNOWN_FEATURES_COPY}
        </p>
      )}
    </section>
  );
}

export default function EvidenceDrawer({
  object,
  doc,
  features = null,
}: {
  object: ProofObject | null;
  doc: ProofDocument;
  features?: FeatureDocument | null;
}) {
  if (!object) {
    return (
      <aside data-testid="evidence-drawer-empty" className="p-4 text-[12px] text-[#8FA3B8]">
        Select an object to inspect its evidence.
      </aside>
    );
  }

  const derived = object.geometry_provenance === "DERIVED_GEOMETRY";

  return (
    <aside data-testid="evidence-drawer" className="p-4 space-y-1 overflow-y-auto">
      <h2 className="text-[15px] text-[#F5F1EA] mb-2">
        {object.cabin_number ?? "Lift region"}
      </h2>

      {derived && (
        <p
          data-testid="derived-boundary-note"
          className="text-[11px] text-[#C58A46] mb-2 leading-relaxed"
        >
          Derived region. The source supports a labelled lift area, not its exact
          boundary. This shape is a union of two source vector groups and must not be
          read as the lift's footprint.
        </p>
      )}

      <CabinFeatures object={object} features={features} />

      <Group title="Identity" />
      <Row label="Object ID" value={object.object_id} />
      <Row label="Semantic type" value={object.semantic_type} />
      <Group title="Provenance" />
      <Row label="Geometry provenance" value={object.geometry_provenance} />
      {object.derivation && <Row label="Derivation" value={object.derivation} />}
      <Row label="Association method" value={object.semantic_association_method} />
      {object.association_staging_note && (
        <Row label="Staging note" value={object.association_staging_note} />
      )}
      <Group title="Source" />
      <Row label="Source references" value={object.source_references.join("  •  ")} />
      <Row label="Transform" value={object.transform_id} />

      <Row
        label="Source bbox (PDF points — provenance, not a measurement)"
        value={object.source_bbox.join(", ")}
      />
      <Row
        label="Normalized bbox (page fractions — not a measurement)"
        value={object.normalized_bbox.join(", ")}
      />

      <Group title="Lifecycle" />
      <Row label="Evidence condition" value={object.evidence_condition} />
      <Row label="Human review state" value={object.human_review_state} />
      <Row label="Publish status" value={object.publish_status} />

      <Group title="Artifact" />
      <Row label="Artifact" value={doc.source.artifact_id} />
      <Row label="Artifact SHA-256" value={doc.source.artifact_sha256} />
      <Row label="Source page" value={String(doc.source.pdf_page_number)} />

      <p className="pt-3 text-[10px] text-[#8FA3B8] leading-relaxed">
        {REFERENCE_FRAME_STATEMENT}
      </p>
    </aside>
  );
}
