/**
 * Vertical deck selector — the primary navigation of the Explorer.
 * Renders decks top-to-bottom as they sit on the ship, current deck highlighted,
 * with previous/next (up/down) affordances and a jump-to on small screens.
 */
import { Link, useNavigate } from 'react-router-dom';
import { ChevronUp, ChevronDown } from 'lucide-react';
import type { PackModel } from './pack';

export function DeckRail({
  model,
  shipId,
  current,
}: {
  model: PackModel;
  shipId: string;
  current?: number;
}) {
  const decks = model.decksTopToBottom();
  const navigate = useNavigate();
  const idx = current != null ? decks.findIndex((d) => d.number === current) : -1;
  const prev = idx > 0 ? decks[idx - 1] : null; // deck above in the list
  const next = idx >= 0 && idx < decks.length - 1 ? decks[idx + 1] : null; // deck below

  const jump = (v: string) => {
    if (v) navigate(`/ship/${shipId}/deck/${v}`);
  };

  return (
    <div className="sticky top-20">
      <div className="flex items-center justify-between mb-4">
        <span className="eyebrow">Decks</span>
        <div className="flex gap-1">
          <button
            aria-label="Deck above"
            disabled={!prev}
            onClick={() => prev && navigate(`/ship/${shipId}/deck/${prev.number}`)}
            className="w-7 h-7 grid place-items-center border border-line text-mist disabled:opacity-30 hover:text-navy hover:border-sea transition-colors"
          >
            <ChevronUp className="w-4 h-4" />
          </button>
          <button
            aria-label="Deck below"
            disabled={!next}
            onClick={() => next && navigate(`/ship/${shipId}/deck/${next.number}`)}
            className="w-7 h-7 grid place-items-center border border-line text-mist disabled:opacity-30 hover:text-navy hover:border-sea transition-colors"
          >
            <ChevronDown className="w-4 h-4" />
          </button>
        </div>
      </div>

      <label className="block lg:hidden mb-4">
        <span className="sr-only">Jump to deck</span>
        <select
          value={current ?? ''}
          onChange={(e) => jump(e.target.value)}
          className="w-full border border-line bg-white px-3 py-2 text-[14px] text-navy"
        >
          <option value="" disabled>
            Jump to deck…
          </option>
          {decks.map((d) => (
            <option key={d.entity_id} value={d.number}>
              Deck {d.number} — {d.name}
            </option>
          ))}
        </select>
      </label>

      <ol className="hidden lg:block border-l border-line">
        {decks.map((d) => {
          const active = d.number === current;
          const cabins = model.cabinsOnDeck(d.entity_id).length;
          const areas = model.areasOnDeck(d.entity_id).length;
          return (
            <li key={d.entity_id}>
              <Link
                to={`/ship/${shipId}/deck/${d.number}`}
                aria-current={active ? 'page' : undefined}
                className={`rail-tick group flex items-baseline gap-3 -ml-px border-l-2 pl-4 py-2.5 ${
                  active ? 'border-brass' : 'border-transparent hover:border-line-cool'
                }`}
              >
                <span className={`font-mono text-[12px] w-6 ${active ? 'text-brass' : 'text-fog'}`}>
                  {d.number}
                </span>
                <span className="flex-1">
                  <span
                    className={`block text-[14px] leading-tight ${
                      active ? 'text-navy font-medium' : 'text-mist group-hover:text-navy'
                    }`}
                  >
                    {d.name}
                  </span>
                  <span className="block text-[11px] text-fog mt-0.5">
                    {cabins} cabins · {areas} areas
                  </span>
                </span>
              </Link>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
