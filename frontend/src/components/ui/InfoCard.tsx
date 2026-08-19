import React from "react";
import { LegacyEpistemicBadge, LegacyEpistemicTag } from "./EpistemicBadge";

interface InfoCardProps {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  description?: string;
  epistemic?: LegacyEpistemicTag | string;
  onClick?: () => void;
  className?: string;
}

export default function InfoCard({
  eyebrow,
  title,
  subtitle,
  description,
  epistemic,
  onClick,
  className = "",
}: InfoCardProps) {
  return (
    <div
      onClick={onClick}
      className={`p-6 bg-white rounded-2xl border border-[#0C1B2A]/10 space-y-2 select-none transition-all ${
        onClick ? "cursor-pointer hover:border-[#C58A46] hover:shadow-sm" : ""
      } ${className}`}
    >
      <div className="flex items-center justify-between">
        {eyebrow && <span className="eyebrow-tag block">{eyebrow}</span>}
        {epistemic && <LegacyEpistemicBadge status={epistemic} />}
      </div>

      <div className="space-y-0.5">
        <h4 className="font-display text-lg font-bold text-[#0C1B2A]">
          {title}
        </h4>
        {subtitle && (
          <p className="text-xs text-[#5B6570] font-sans">
            {subtitle}
          </p>
        )}
      </div>

      {description && (
        <p className="text-xs text-[#5B6570] leading-relaxed pt-1">
          {description}
        </p>
      )}
    </div>
  );
}
