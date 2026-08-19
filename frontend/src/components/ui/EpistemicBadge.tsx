import React from "react";

export type EpistemicTag =
  | "DIRECT"
  | "CALCULATED"
  | "INFERRED"
  | "SUPPORTED"
  | "UNSUPPORTED"
  | "CONFLICTED"
  | "UNKNOWN"
  | "KNOWN"
  | "DERIVED"
  | "LIKELY"
  | "CONFLICT";

interface EpistemicBadgeProps {
  status?: EpistemicTag;
  className?: string;
}

const KNOWN_TAGS = new Set<string>([
  "DIRECT",
  "CALCULATED",
  "INFERRED",
  "SUPPORTED",
  "UNSUPPORTED",
  "CONFLICTED",
  "UNKNOWN",
  "KNOWN",
  "DERIVED",
  "LIKELY",
  "CONFLICT",
]);

export default function EpistemicBadge({ status, className = "" }: EpistemicBadgeProps) {
  const rawStatus = (status || "UNKNOWN").toUpperCase();
  const normalized: EpistemicTag = KNOWN_TAGS.has(rawStatus)
    ? (rawStatus as EpistemicTag)
    : "UNKNOWN";

  let style = "bg-slate-200/80 text-slate-700 border-slate-300";
  if (normalized === "DIRECT" || normalized === "SUPPORTED" || normalized === "KNOWN") {
    style = "bg-emerald-100/80 text-emerald-900 border-emerald-300/60";
  } else if (normalized === "CALCULATED" || normalized === "DERIVED") {
    style = "bg-sky-100/80 text-sky-900 border-sky-300/60";
  } else if (normalized === "INFERRED" || normalized === "LIKELY") {
    style = "bg-emerald-50 text-emerald-800 border-emerald-200";
  } else if (normalized === "CONFLICT" || normalized === "CONFLICTED" || normalized === "UNSUPPORTED") {
    style = "bg-rose-100 text-rose-900 border-rose-300";
  } else {
    style = "bg-slate-200/80 text-slate-700 border-slate-300";
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[9.5px] font-mono font-bold uppercase tracking-wider border ${style} ${className}`}
    >
      {normalized}
    </span>
  );
}
