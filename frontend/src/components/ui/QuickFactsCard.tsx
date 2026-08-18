import React from "react";
import EpistemicBadge, { EpistemicTag } from "./EpistemicBadge";

export interface QuickFactItem {
  label: string;
  value: React.ReactNode;
  epistemic?: EpistemicTag | string;
  isMono?: boolean;
}

interface QuickFactsCardProps {
  title?: string;
  items: QuickFactItem[];
  variant?: "light" | "navy";
  className?: string;
}

export default function QuickFactsCard({
  title = "Quick Facts",
  items,
  variant = "light",
  className = "",
}: QuickFactsCardProps) {
  const isNavy = variant === "navy";

  return (
    <div
      className={`p-6 sm:p-7 rounded-3xl border select-none transition-all ${
        isNavy
          ? "bg-[#0C1B2A] text-white border-white/10 shadow-navy"
          : "bg-white text-[#0C1B2A] border-[#0C1B2A]/10 shadow-card"
      } ${className}`}
    >
      {title && (
        <h3 className={`font-display text-2xl font-bold mb-5 ${isNavy ? "text-white" : "text-[#0C1B2A]"}`}>
          {title}
        </h3>
      )}

      <div className="space-y-4 text-xs">
        {items.map((item, idx) => {
          const isLast = idx === items.length - 1;
          return (
            <div
              key={idx}
              className={`space-y-1 ${!isLast ? (isNavy ? "pb-3 border-b border-white/10" : "pb-3 border-b border-[#0C1B2A]/5") : "pt-0.5"}`}
            >
              <div className={`flex items-center justify-between ${isNavy ? "text-[#94A3B8]" : "text-slate-500"}`}>
                <span>{item.label}</span>
                {item.epistemic && <EpistemicBadge status={item.epistemic} />}
              </div>
              <div
                className={`font-bold text-sm ${item.isMono ? "font-mono text-[#C58A46] text-xs" : isNavy ? "text-white" : "text-[#0C1B2A]"}`}
              >
                {item.value}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
