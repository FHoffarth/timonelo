import { ExternalLink } from 'lucide-react';
import { useI18n } from '../i18n';
import { knowledgeRepository } from '../knowledge';

const bellissima = knowledgeRepository.getShip('msc-bellissima');

export function Footer({
  onNavigateHome,
  onNavigateFleet,
  onNavigatePorts,
  onNavigateCrew,
  onNavigateMission,
}: {
  onNavigateHome: () => void;
  onNavigateFleet: () => void;
  onNavigatePorts: () => void;
  onNavigateCrew: () => void;
  onNavigateMission: () => void;
  onNavigatePrinciples: () => void;
}) {
  const { t } = useI18n();

  return (
    <footer className="border-t border-slate-200/80 mt-24 bg-white/40">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 mb-14">
          {/* Col 1: Brand */}
          <div className="md:col-span-2 max-w-sm">
            <button onClick={onNavigateHome} className="flex items-center gap-2.5 text-left mb-3 cursor-pointer">
              <span className="w-5 h-5 bg-[#0c1b2a] grid place-items-center rounded-xs">
                <span className="w-0.5 h-2.5 bg-[#f4f2ed] rotate-45" />
              </span>
              <span className="font-serif text-2xl tracking-tight text-[#0c1b2a] font-normal">
                {t.common.brandName}
              </span>
            </button>
            <p className="text-[13px] text-slate-600 leading-relaxed font-light">
              {t.footer.platformDescription}
            </p>
            <p className="text-[11px] text-slate-400 font-sans mt-3">
              Ocean Mega-Liners · Luxury Riverboats · Strategic Turnaround Ports
            </p>
          </div>

          {/* Col 2: Platform Navigation */}
          <div>
            <span className="text-[11px] uppercase tracking-widest text-slate-800 font-semibold block mb-3">
              {t.footer.navigationHeader}
            </span>
            <ul className="space-y-2 text-[13px] text-slate-600 font-light">
              <li>
                <button onClick={onNavigateFleet} className="hover:text-slate-900 transition-colors cursor-pointer">
                  {t.navigation.ships}
                </button>
              </li>
              <li>
                <button onClick={onNavigatePorts} className="hover:text-slate-900 transition-colors cursor-pointer">
                  {t.navigation.destinations}
                </button>
              </li>
              <li>
                <button onClick={onNavigateCrew} className="hover:text-slate-900 transition-colors cursor-pointer">
                  {t.navigation.bridgeTeam}
                </button>
              </li>
              <li>
                <button onClick={onNavigateMission} className="hover:text-slate-900 transition-colors cursor-pointer">
                  {t.navigation.philosophy}
                </button>
              </li>
            </ul>
          </div>

          {/* Col 3: Reference Vessels */}
          <div>
            <span className="text-[11px] uppercase tracking-widest text-slate-800 font-semibold block mb-3">
              {t.footer.shipsHeader}
            </span>
            <ul className="space-y-2 text-[13px] text-slate-600 font-light">
              <li>{bellissima.vessel_name} (IMO {bellissima.technical_specifications.imo_number})</li>
              <li>MS Andorinha (ENI 02338573)</li>
              <li>MSC Grandiosa (IMO 9803613)</li>
              <li>MSC Meraviglia (IMO 9647710)</li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-slate-200/60 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 font-light">
          <p>{t.footer.copyright}</p>
          <div className="flex items-center gap-6">
            <span className="text-[11px] uppercase tracking-widest text-slate-400">
              {t.footer.principles}
            </span>
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 hover:text-slate-900 transition"
            >
              <span>GitHub</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
