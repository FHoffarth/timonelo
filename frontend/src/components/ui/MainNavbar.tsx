import React from "react";
import { Menu, Search } from "lucide-react";

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
      <div className="max-w-7xl mx-auto px-2 sm:px-6 h-16 flex items-center justify-between gap-1">
        {/* Brand Logo */}
        <button
          onClick={() => onNavigate("home")}
          className="flex shrink-0 items-baseline gap-2.5 text-left cursor-pointer group"
        >
          <span className="font-display text-2xl font-bold text-[#0C1B2A] tracking-tight">
            Timonelo
          </span>
          <span className="hidden xl:inline text-[9.5px] font-mono font-bold tracking-[0.18em] text-[#C58A46] uppercase">
            CRUISE INTELLIGENCE
          </span>
        </button>

        {/* Center Navigation Links */}
        <nav aria-label="Main navigation" className="hidden lg:flex items-center gap-6 text-sm">
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
        <div className="flex shrink-0 items-center gap-1 sm:gap-3">
          <button
            onClick={onOpenSearch}
            aria-label="Search intelligence"
            className="flex min-h-11 min-w-11 items-center justify-center gap-2 px-3 sm:px-3.5 py-1.5 rounded-full bg-[#0C1B2A]/5 hover:bg-[#0C1B2A]/10 text-xs text-[#5B6570] transition-colors border border-[#0C1B2A]/5 cursor-pointer"
          >
            <Search className="w-3.5 h-3.5" />
            <span className="hidden xl:inline">Search intelligence...</span>
          </button>

          <button
            onClick={() => onNavigate("my-cruise")}
            className="min-h-11 whitespace-nowrap px-3 sm:px-4 py-1.5 rounded-full bg-[#0C1B2A] text-white text-xs font-semibold hover:bg-[#C58A46] transition-colors shadow-sm cursor-pointer"
          >
            My Cruise
          </button>
          <details
            className="lg:hidden"
            onKeyDown={(event) => {
              if (event.key === "Escape") {
                event.currentTarget.open = false;
                event.currentTarget.querySelector("summary")?.focus();
              }
            }}
          >
            <summary aria-label="Open main navigation" className="flex min-h-11 min-w-11 items-center justify-center rounded-full cursor-pointer list-none [&::-webkit-details-marker]:hidden hover:bg-[#0C1B2A]/5">
              <Menu className="w-5 h-5" aria-hidden="true" />
            </summary>
            <nav aria-label="Mobile main navigation" className="absolute top-full inset-x-0 bg-[#FBF8F3] border-b border-[#0C1B2A]/10 shadow-sm px-3 py-3 grid grid-cols-2 gap-2">
              {[{ id: "home" as const, label: "Home" }, ...navItems, { id: "my-cruise" as const, label: "My Cruise" }].map((item) => (
                <button
                  key={item.id}
                  aria-current={currentRoute === item.id ? "page" : undefined}
                  onClick={(event) => {
                    const disclosure = event.currentTarget.closest("details");
                    if (disclosure) {
                      disclosure.open = false;
                      disclosure.querySelector("summary")?.focus();
                    }
                    onNavigate(item.id);
                  }}
                  className={`min-h-11 rounded-xl px-3 text-left text-sm font-medium ${currentRoute === item.id ? "bg-[#0C1B2A] text-white" : "hover:bg-[#0C1B2A]/5 text-[#0C1B2A]"}`}
                >
                  {item.label}
                </button>
              ))}
            </nav>
          </details>
        </div>
      </div>
    </header>
  );
}
