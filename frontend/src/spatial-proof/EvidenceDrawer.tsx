/**
 * Per-object provenance panel.
 *
 * Every value shown is read straight from the artifact. Nothing is computed,
 * rounded for display, or converted into a unit. Coordinates appear as
 * provenance, explicitly labelled as page fractions, never as a measurement.
 */

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

export default function EvidenceDrawer({
  object,
  doc,
}: {
  object: ProofObject | null;
  doc: ProofDocument;
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
