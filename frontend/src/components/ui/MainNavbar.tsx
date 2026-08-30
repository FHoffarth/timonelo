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
        <nav className="hidden md:flex items-center gap-6 text-sm">
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
                {item.label}
                {isActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#C58A46] rounded-full" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Right Search & Profile Action */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenSearch}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#0C1B2A]/5 hover:bg-[#0C1B2A]/10 text-xs text-[#5B6570] transition-colors border border-[#0C1B2A]/5 cursor-pointer"
          >
            <Search className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Search intelligence...</span>
          </button>

          <button
            onClick={() => onNavigate("my-cruise")}
            className="px-4 py-1.5 rounded-full bg-[#0C1B2A] text-white text-xs font-semibold hover:bg-[#C58A46] transition-colors shadow-sm cursor-pointer"
          >
            My Cruise
          </button>
        </div>
      </div>
    </header>
  );
}
