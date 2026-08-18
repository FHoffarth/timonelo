import React from "react";
import { Search } from "lucide-react";

export type NavRoute = "home" | "ships" | "ports" | "routes" | "cruise-math" | "travel-info" | "my-cruise";

interface MainNavbarProps {
  currentRoute: NavRoute;
  onNavigate: (route: NavRoute, param?: string) => void;
  onOpenSearch?: () => void;
}

export default function MainNavbar({
  currentRoute,
  onNavigate,
  onOpenSearch,
}: MainNavbarProps) {
  const navItems: { id: NavRoute; label: string }[] = [
    { id: "ships", label: "Ships" },
    { id: "ports", label: "Ports" },
    { id: "routes", label: "Routes" },
    { id: "cruise-math", label: "Cruise Math" },
    { id: "travel-info", label: "Travel Info" },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#FBF8F3]/95 backdrop-blur-md border-b border-[#0C1B2A]/10 select-none">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <button
          onClick={() => onNavigate("home")}
          className="flex items-baseline gap-2.5 text-left cursor-pointer group"
        >
          <span className="font-display text-2xl font-bold text-[#0C1B2A] tracking-tight">
            Timonelo
          </span>
          <span className="text-[9.5px] font-mono font-bold tracking-[0.18em] text-[#C58A46] uppercase">
            CRUISE INTELLIGENCE
          </span>
        </button>

        {/* Center Navigation Links */}
        <nav className="hidden md:flex items-center gap-7 text-sm">
          {navItems.map((item) => {
            const isActive = currentRoute === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`py-1 font-medium transition-colors relative cursor-pointer ${
                  isActive
                    ? "text-[#0C1B2A] font-semibold"
                    : "text-[#5B6570] hover:text-[#0C1B2A]"
                }`}
              >
                <span>{item.label}</span>
                {isActive && (
                  <span className="absolute -bottom-1 left-0 right-0 h-[2px] bg-[#C58A46] rounded-full" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Right Search & CTA */}
        <div className="flex items-center gap-3">
          <div
            onClick={onOpenSearch}
            className="hidden sm:flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white border border-[#0C1B2A]/10 text-xs text-[#5B6570] hover:border-[#C58A46] cursor-pointer shadow-sm transition-all"
          >
            <Search className="w-3.5 h-3.5 text-[#C58A46]" />
            <span>Search intelligence...</span>
          </div>

          <button
            onClick={() => onNavigate("my-cruise")}
            className="px-4 py-2 rounded-full bg-[#0C1B2A] hover:bg-[#132238] text-white text-xs font-semibold tracking-wide transition-all active:scale-95 cursor-pointer shadow-sm"
          >
            My Cruise
          </button>
        </div>
      </div>
    </header>
  );
}
