import { useState } from 'react';
import { ChevronDown, Check, ArrowLeft, Search } from 'lucide-react';
import { FLEET_REGISTRY, getVesselBySlug } from '../fleet';
import type { ShipData, CabinData } from '../types';
import { useI18n } from '../i18n';

interface NavigationProps {
  currentView: 'landing' | 'vessel' | 'cabin' | 'port' | 'crew' | 'mission';
  currentSlug: string;
  ship: ShipData | null;
  cabin: CabinData | null;
  onNavigateHome: () => void;
  onNavigateFleet: () => void;
  onNavigatePorts: () => void;
  onNavigateCrew: () => void;
  onNavigateMission: () => void;
  onSelectVessel: (slug: string) => void;
  onOpenSearch: () => void;
}

export function Navigation({
  currentView,
  currentSlug,
  onNavigateHome,
  onNavigateFleet,
  onNavigatePorts,
  onNavigateCrew,
  onNavigateMission,
  onSelectVessel,
  onOpenSearch,
}: NavigationProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const activeMeta = getVesselBySlug(currentSlug);
  const { t, locale, setLocale } = useI18n();

  return (
    <header className="sticky top-0 z-40 bg-[#f4f2ed]/95 border-b border-slate-200/80 backdrop-blur-md transition-colors">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between gap-4 sm:gap-6">
        {/* Left: Brand Identity */}
        <div className="flex items-center gap-8">
          <button
            onClick={onNavigateHome}
            className="flex items-center gap-2.5 text-left cursor-pointer group"
            title="Timonelo"
          >
            <span className="w-5 h-5 bg-[#0c1b2a] grid place-items-center rounded-xs group-hover:bg-amber-600 transition-colors">
              <span className="w-0.5 h-2.5 bg-[#f4f2ed] rotate-45" />
            </span>
            <span className="font-serif text-xl tracking-tight text-[#0c1b2a] font-medium leading-none">
              {t.common.brandName}
            </span>
          </button>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-7 text-[14px] text-slate-600 font-sans">
            <button
              onClick={onNavigateFleet}
              className={`hover:text-slate-900 transition-colors cursor-pointer ${
                currentView === 'landing' ? 'text-slate-900 font-medium' : ''
              }`}
            >
              {t.navigation.ships}
            </button>
            <button
              onClick={onNavigatePorts}
              className={`hover:text-slate-900 transition-colors cursor-pointer ${
                currentView === 'port' ? 'text-slate-900 font-medium' : ''
              }`}
            >
              {t.navigation.destinations}
            </button>
            <button
              onClick={onNavigateCrew}
              className={`hover:text-slate-900 transition-colors cursor-pointer ${
                currentView === 'crew' ? 'text-slate-900 font-medium' : ''
              }`}
            >
              {t.navigation.bridgeTeam}
            </button>
            <button
              onClick={onNavigateMission}
              className={`hover:text-slate-900 transition-colors cursor-pointer ${
                currentView === 'mission' ? 'text-slate-900 font-medium' : ''
              }`}
            >
              {t.navigation.philosophy}
            </button>
          </nav>
        </div>

        {/* Right Actions: Search + Quick Switcher + Language Selector */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          {/* Universal Search Trigger */}
          <button
            onClick={onOpenSearch}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-slate-200 bg-white/80 hover:bg-white text-slate-600 hover:text-slate-900 text-xs transition-colors cursor-pointer shadow-2xs"
            title={t.navigation.searchAria}
          >
            <Search className="w-3.5 h-3.5 text-amber-600" />
            <span className="hidden sm:inline">{t.common.search}</span>
            <kbd className="hidden lg:inline text-[10px] font-sans bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200 text-slate-500">
              {t.common.searchShortcut}
            </kbd>
          </button>

          {/* Language Switcher: Subtle text selector (no flags) */}
          <div className="inline-flex items-center rounded-full bg-white/80 border border-slate-200 p-0.5 text-xs font-sans shadow-2xs">
            <button
              onClick={() => setLocale('en')}
              className={`px-2.5 py-1 rounded-full text-[11px] font-medium transition-all cursor-pointer ${
                locale === 'en'
                  ? 'bg-slate-900 text-white shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              aria-label="Switch language to English"
            >
              English
            </button>
            <button
              onClick={() => setLocale('de')}
              className={`px-2.5 py-1 rounded-full text-[11px] font-medium transition-all cursor-pointer ${
                locale === 'de'
                  ? 'bg-slate-900 text-white shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              aria-label="Sprache auf Deutsch umstellen"
            >
              Deutsch
            </button>
          </div>

          {currentView !== 'landing' && (
            <button
              onClick={onNavigateHome}
              className="hidden sm:inline-flex items-center gap-1 text-xs text-slate-600 hover:text-slate-900 transition-colors px-2 py-1 rounded cursor-pointer"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>{t.navigation.ships}</span>
            </button>
          )}

          {/* Ship Switcher Dropdown */}
          <div className="relative">
            <button
              onClick={() => setDropdownOpen((prev) => !prev)}
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-slate-200 bg-white hover:border-slate-300 transition text-left cursor-pointer text-xs shadow-2xs"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span className="font-medium text-slate-900 truncate max-w-[110px] sm:max-w-[150px]">
                {currentView === 'landing' ? t.common.activeBridge : activeMeta.name}
              </span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {dropdownOpen && (
              <>
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setDropdownOpen(false)}
                />
                <div className="absolute right-0 mt-2 w-72 bg-white rounded-2xl shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in zoom-in-95 duration-100">
                  <div className="px-3.5 py-1.5 border-b border-slate-100">
                    <span className="text-[10px] uppercase tracking-widest text-slate-400 font-semibold block">
                      {t.navigation.ships}
                    </span>
                  </div>

                  <div className="max-h-80 overflow-y-auto py-1">
                    {FLEET_REGISTRY.map((vessel) => {
                      const isCurrent = vessel.slug === currentSlug && currentView !== 'landing';
                      return (
                        <button
                          key={vessel.slug}
                          onClick={() => {
                            onSelectVessel(vessel.slug);
                            setDropdownOpen(false);
                          }}
                          className={`w-full px-3.5 py-2.5 text-left flex items-start justify-between gap-2 hover:bg-slate-50 transition cursor-pointer ${
                            isCurrent ? 'bg-amber-50/50' : ''
                          }`}
                        >
                          <div>
                            <div className="text-xs font-serif font-medium text-slate-900 flex items-center gap-1.5">
                              <span>{vessel.name}</span>
                              <span className="text-[10px] text-slate-400 font-sans">
                                ({vessel.buildYear})
                              </span>
                            </div>
                            <div className="text-[10px] text-slate-500 font-sans mt-0.5">
                              {vessel.operator} · {vessel.cabinCount} Staterooms
                            </div>
                          </div>
                          {isCurrent && (
                            <Check className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
