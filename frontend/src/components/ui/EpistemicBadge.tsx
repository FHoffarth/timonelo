import React from "react";
import {
  Method,
  Derivation,
  EvidenceCondition,
  HumanReviewState,
  PublishStatus,
  GeometryProvenance,
} from "../../generated/canon";

// ===========================================================================
// CANONICAL AXIS-SPECIFIC BADGES (ADR-0002)
// ===========================================================================

export interface MethodBadgeProps {
  method?: Method;
  className?: string;
}

export function MethodBadge({ method = "DIRECT", className = "" }: MethodBadgeProps) {
  let style = "bg-slate-200 text-slate-800 border-slate-300";
  if (method === "DIRECT") {
    style = "bg-emerald-100/90 text-emerald-900 border-emerald-300";
  } else if (method === "CALCULATED") {
    style = "bg-sky-100/90 text-sky-900 border-sky-300";
  } else if (method === "INFERRED") {
    style = "bg-purple-100/90 text-purple-900 border-purple-300";
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[9.5px] font-mono font-bold uppercase tracking-wider border ${style} ${className}`}
      title={`Production Method: ${method}`}
    >
      <span className="opacity-60 text-[8px] mr-1">METHOD:</span>
      {method}
    </span>
  );
}

export interface EvidenceConditionBadgeProps {
  condition?: EvidenceCondition;
  className?: string;
}

export function EvidenceConditionBadge({
  condition = "UNKNOWN",
  className = "",
}: EvidenceConditionBadgeProps) {
  let style = "bg-slate-200 text-slate-800 border-slate-300";
  if (condition === "SUPPORTED") {
    style = "bg-emerald-100/90 text-emerald-900 border-emerald-300";
  } else if (condition === "UNSUPPORTED") {
    style = "bg-amber-100/90 text-amber-900 border-amber-300";
  } else if (condition === "CONFLICTED") {
    style = "bg-rose-100 text-rose-900 border-rose-300";
  } else if (condition === "UNKNOWN") {
    style = "bg-slate-200 text-slate-700 border-slate-300";
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[9.5px] font-mono font-bold uppercase tracking-wider border ${style} ${className}`}
      title={`Evidence Condition: ${condition}`}
    >
      <span className="opacity-60 text-[8px] mr-1">CONDITION:</span>
      {condition}
    </span>
  );
}

export interface HumanReviewStateBadgeProps {
  state?: HumanReviewState;
  className?: string;
}

export function HumanReviewStateBadge({
  state = "DRAFT",
  className = "",
}: HumanReviewStateBadgeProps) {
  let style = "bg-slate-100 text-slate-700 border-slate-200";
  if (state === "APPROVED") {
    style = "bg-teal-100 text-teal-900 border-teal-300";
  } else if (state === "UNDER_REVIEW") {
    style = "bg-blue-100 text-blue-900 border-blue-300";
  } else if (state === "REJECTED") {
    style = "bg-rose-100 text-rose-900 border-rose-300";
  } else if (state === "SUPERSEDED") {
    style = "bg-zinc-200 text-zinc-700 border-zinc-300";
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[9.5px] font-mono font-bold uppercase tracking-wider border ${style} ${className}`}
      title={`Human Review State: ${state}`}
    >
      <span className="opacity-60 text-[8px] mr-1">REVIEW:</span>
      {state}
    </span>
  );
}

export interface PublishStatusBadgeProps {
  status?: PublishStatus;
  className?: string;
}

export function PublishStatusBadge({
  status = "PUBLISH_BLOCKED",
  className = "",
}: PublishStatusBadgeProps) {
  let style = "bg-slate-200 text-slate-800 border-slate-300";
  if (status === "PUBLISH_ALLOWED") {
    style = "bg-emerald-100 text-emerald-900 border-emerald-300";
  } else if (status === "PUBLISH_ALLOWED_WITH_WARNINGS") {
    style = "bg-amber-100 text-amber-900 border-amber-300";
  } else if (status === "PUBLISH_BLOCKED") {
    style = "bg-red-100 text-red-900 border-red-300";
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[9.5px] font-mono font-bold uppercase tracking-wider border ${style} ${className}`}
      title={`Publish Status: ${status}`}
    >
      <span className="opacity-60 text-[8px] mr-1">PUBLISH:</span>
      {status}
    </span>
  );
}

export interface DerivationBadgeProps {
  derivation?: Derivation;
  className?: string;
}

export function DerivationBadge({
  derivation = "LOCAL",
  className = "",
}: DerivationBadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[9.5px] font-mono font-bold uppercase tracking-wider border bg-indigo-100/90 text-indigo-900 border-indigo-300 ${className}`}
      title={`Derivation: ${derivation}`}
    >
      <span className="opacity-60 text-[8px] mr-1">ORIGIN:</span>
      {derivation}
    </span>
  );
}

export interface GeometryProvenanceBadgeProps {
  provenance?: GeometryProvenance;
  className?: string;
}

export function GeometryProvenanceBadge({
  provenance = "UNKNOWN_PROVENANCE",
  className = "",
}: GeometryProvenanceBadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[9.5px] font-mono font-bold uppercase tracking-wider border bg-cyan-100/90 text-cyan-900 border-cyan-300 ${className}`}
      title={`Geometry Provenance: ${provenance}`}
    >
      <span className="opacity-60 text-[8px] mr-1">GEOMETRY:</span>
      {provenance}
    </span>
  );
}

// ===========================================================================
// GENERIC CANONICAL BADGE WITH EXPLICIT AXIS (ADR-0002)
// ===========================================================================

export type CanonAxisProps =
  | { axis: "method"; value?: Method }
  | { axis: "evidence_condition"; value?: EvidenceCondition }
  | { axis: "human_review_state"; value?: HumanReviewState }
  | { axis: "publish_status"; value?: PublishStatus }
  | { axis: "derivation"; value?: Derivation }
  | { axis: "geometry_provenance"; value?: GeometryProvenance };

export function CanonBadge(props: CanonAxisProps & { className?: string }) {
  const { className = "" } = props;
  switch (props.axis) {
    case "method":
      return <MethodBadge method={props.value} className={className} />;
    case "evidence_condition":
      return <EvidenceConditionBadge condition={props.value} className={className} />;
    case "human_review_state":
      return <HumanReviewStateBadge state={props.value} className={className} />;
    case "publish_status":
      return <PublishStatusBadge status={props.value} className={className} />;
    case "derivation":
      return <DerivationBadge derivation={props.value} className={className} />;
    case "geometry_provenance":
      return <GeometryProvenanceBadge provenance={props.value} className={className} />;
  }
}

// ===========================================================================
// NON-CANONICAL LEGACY BADGE (PROTOTYPE VIEWPORTS ONLY)
// ===========================================================================

export type LegacyEpistemicTag = "KNOWN" | "DERIVED" | "VERIFIED" | "LIKELY" | "UNKNOWN" | "CONFLICT";

export interface LegacyEpistemicBadgeProps {
  status?: LegacyEpistemicTag | string;
  className?: string;
}

export function LegacyEpistemicBadge({
  status,
  className = "",
}: LegacyEpistemicBadgeProps) {
  const normalized = (status || "UNKNOWN").toUpperCase();

  let style = "bg-slate-200/80 text-slate-700 border-slate-300";
  if (normalized === "VERIFIED" || normalized === "DIRECT") {
    style = "bg-emerald-100/80 text-emerald-900 border-emerald-300/60";
  } else if (normalized === "DERIVED") {
    style = "bg-sky-100/80 text-sky-900 border-sky-300/60";
  } else if (normalized === "LIKELY") {
    style = "bg-emerald-50 text-emerald-800 border-emerald-200";
  } else if (normalized === "UNKNOWN") {
    style = "bg-slate-200/80 text-slate-700 border-slate-300";
  } else if (normalized === "CONFLICT") {
    style = "bg-rose-100 text-rose-900 border-rose-300";
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[9.5px] font-mono font-bold uppercase tracking-wider border ${style} ${className}`}
    >
      <span className="opacity-50 text-[7.5px] mr-1">LEGACY:</span>
      {normalized}
    </span>
  );
}

// Default export delegates to LegacyEpistemicBadge for backwards compatibility with existing UI fixtures
export default LegacyEpistemicBadge;
