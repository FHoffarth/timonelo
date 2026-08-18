import React from "react";
import { AlertTriangle, AlertOctagon, Info } from "lucide-react";

interface WarningCardProps {
  title: string;
  message: string;
  variant?: "amber" | "navy" | "sky";
  className?: string;
}

export default function WarningCard({
  title,
  message,
  variant = "amber",
  className = "",
}: WarningCardProps) {
  if (variant === "navy") {
    return (
      <div className={`p-6 rounded-3xl bg-[#0C1B2A] text-white shadow-lg space-y-2 border border-white/10 select-none ${className}`}>
        <div className="flex items-center gap-2 text-xs font-mono font-bold text-[#C58A46] uppercase">
          <AlertOctagon className="w-4 h-4 text-[#C58A46] shrink-0" />
          <span>{title}</span>
        </div>
        <p className="text-xs text-[#94A3B8] leading-relaxed">
          {message}
        </p>
      </div>
    );
  }

  if (variant === "sky") {
    return (
      <div className={`p-6 rounded-2xl bg-sky-50 border border-sky-200 text-sky-950 space-y-2 select-none ${className}`}>
        <div className="flex items-center gap-2 font-display text-lg font-bold text-sky-900">
          <Info className="w-5 h-5 text-sky-600 shrink-0" />
          <span>{title}</span>
        </div>
        <p className="text-xs text-sky-900/90 leading-relaxed font-sans">
          {message}
        </p>
      </div>
    );
  }

  // Default Amber
  return (
    <div className={`p-6 rounded-2xl bg-amber-50 border border-amber-200/80 text-amber-950 space-y-2 select-none ${className}`}>
      <div className="flex items-center gap-2 font-display text-lg font-bold text-amber-900">
        <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
        <span>{title}</span>
      </div>
      <p className="text-xs text-amber-900/90 leading-relaxed font-sans">
        {message}
      </p>
    </div>
  );
}
