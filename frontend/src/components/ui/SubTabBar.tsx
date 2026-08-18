import React from "react";

export interface TabOption {
  id: string;
  label: string;
  count?: number;
}

interface SubTabBarProps {
  tabs: TabOption[];
  activeTab: string;
  onSelectTab: (tabId: string) => void;
  className?: string;
}

export default function SubTabBar({
  tabs,
  activeTab,
  onSelectTab,
  className = "",
}: SubTabBarProps) {
  return (
    <div className={`flex items-center gap-8 border-b border-[#0C1B2A]/10 text-sm select-none ${className}`}>
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            onClick={() => onSelectTab(tab.id)}
            className={`pb-3 font-medium transition-all relative cursor-pointer ${
              isActive
                ? "text-[#0C1B2A] font-semibold"
                : "text-[#5B6570] hover:text-[#0C1B2A]"
            }`}
          >
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span className="ml-1.5 text-xs text-[#5B6570] font-mono">
                ({tab.count})
              </span>
            )}
            {isActive && (
              <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#C58A46] rounded-full" />
            )}
          </button>
        );
      })}
    </div>
  );
}
