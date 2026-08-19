import React from "react";
import { LegacyEpistemicBadge, LegacyEpistemicTag } from "./EpistemicBadge";

interface TimelineCardProps {
  stepLabel: string;
  title: string;
  subtitle: string;
  epistemic?: LegacyEpistemicTag | string;
  onClick?: () => void;
  className?: string;
}

export default function TimelineCard({
  stepLabel,
  title,
  subtitle,
  epistemic,
  onClick,
  className = "",
}: TimelineCardProps) {
  return (
    <div
      onClick={onClick}
      className={`p-4 bg-white rounded-2xl border border-[#0C1B2A]/10 shadow-sm flex items-center justify-between transition-all select-none ${
        onClick ? "cursor-pointer hover:shadow-md hover:border-[#C58A46]" : ""
      } ${className}`}
    >
      <div className="flex items-center gap-4">
        <span className="font-mono text-xs font-bold text-[#C58A46] min-w-[52px]">
          {stepLabel}
        </span>
        <div>
          <h4 className="font-display text-base font-bold text-[#0C1B2A]">
            {title}
          </h4>
          <p className="text-xs text-[#5B6570] font-sans">
            {subtitle}
          </p>
        </div>
      </div>

      {epistemic && <LegacyEpistemicBadge status={epistemic} />}
    </div>
  );
}
