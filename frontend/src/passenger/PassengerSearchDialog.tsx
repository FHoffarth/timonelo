import { useEffect, useRef, useState } from 'react';
import { searchPassengerDestinations, type PassengerDestination } from './search';

export default function PassengerSearchDialog({ initialQuery, vesselSlug, onSelect, onClose }: {
  initialQuery: string;
  vesselSlug?: string;
  onSelect: (destination: PassengerDestination) => void;
  onClose: () => void;
}) {
  const [query, setQuery] = useState(initialQuery);
  const dialog = useRef<HTMLDialogElement>(null);
  const input = useRef<HTMLInputElement>(null);
  useEffect(() => {
    dialog.current?.showModal();
    input.current?.focus();
  }, []);
  const results = searchPassengerDestinations(query, vesselSlug);
  return (
    <dialog ref={dialog} onCancel={onClose} aria-labelledby="passenger-search-title" className="m-auto w-[calc(100%-2rem)] max-w-xl max-h-[80dvh] overflow-y-auto rounded-3xl bg-white p-5 text-[#0C1B2A] shadow-xl backdrop:bg-[#0C1B2A]/60">
      <div className="flex items-center justify-between gap-3">
        <h2 id="passenger-search-title" className="font-display text-xl font-bold">Find a page or cabin</h2>
        <button onClick={onClose} className="min-h-11 px-3 rounded-xl border">Close</button>
      </div>
      <label htmlFor="passenger-search" className="block text-sm mt-4">Ship, reference port, restaurant or cabin number</label>
      <input ref={input} id="passenger-search" value={query} onChange={e => setQuery(e.target.value)} placeholder="Bellissima, Genoa, 14122, drink packages" className="mt-2 w-full min-w-0 rounded-xl border p-3" />
      <p role="status" className="text-xs text-[#5B6570] my-3">{!query.trim() ? 'Search the pages and reference material available here.' : results.length ? `${results.length} destinations. Availability and evidence are checked on the destination page.` : 'No matching destination. Try Bellissima, Genoa, Cruise Math or a cabin number.'}</p>
      <ul className="space-y-2">
        {results.map(result => <li key={`${result.kind}:${result.label}`}><button onClick={() => onSelect(result)} className="w-full min-h-11 text-left rounded-xl bg-slate-50 p-3 hover:bg-slate-100"><span className="block font-semibold">{result.label}</span><span className="block text-xs text-[#5B6570] mt-1">{result.detail}</span></button></li>)}
      </ul>
    </dialog>
  );
}
