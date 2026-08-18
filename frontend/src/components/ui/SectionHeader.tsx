import React from "react";

interface SectionHeaderProps {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  align?: "left" | "center";
  className?: string;
}

export default function SectionHeader({
  eyebrow,
  title,
  subtitle,
  align = "left",
  className = "",
}: SectionHeaderProps) {
  const isCenter = align === "center";

  return (
    <div className={`space-y-2 select-none ${isCenter ? "text-center mx-auto max-w-3xl" : ""} ${className}`}>
      {eyebrow && (
        <span className="eyebrow-tag block">
          {eyebrow}
        </span>
      )}
      <h2 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold text-[#0C1B2A] tracking-tight leading-tight">
        {title}
      </h2>
      {subtitle && (
        <p className="text-sm sm:text-base text-[#5B6570] leading-relaxed">
          {subtitle}
        </p>
      )}
    </div>
  );
}
