import React from "react";

export type EpistemicTag = "KNOWN" | "DERIVED" | "VERIFIED" | "LIKELY" | "UNKNOWN" | "CONFLICT";

interface EpistemicBadgeProps {
  status: EpistemicTag | string;
  className?: string;
}

export default function EpistemicBadge({ status, className = "" }: EpistemicBadgeProps) {
  const normalized = status.toUpperCase();

  let style = "bg-amber-100/80 text-amber-900 border-amber-300/60";
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
      {normalized}
    </span>
  );
}
