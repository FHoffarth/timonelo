import { useState, useMemo } from 'react';
import {
  Shield,
  CheckCircle,
  XCircle,
  AlertTriangle,
  ZoomIn,
  ZoomOut,
  Maximize2,
  FileText,
  Eye,
  Info,
  UserCheck,
  Download,
} from 'lucide-react';
import {
  DeckReviewWorkspaceViewModel,
  ReviewDecisionState,
  FinalizeReviewResult,
} from './types';
import {
  SUPPORTED_REVIEW_DECKS,
  buildDeckReviewWorkspaceViewModel,
  finalizeReviewedDecisions,
} from './adapter';
import { isAdmittedPassengerEntity } from '../ship-overview/adapter';

interface DeckReviewWorkspaceProps {
  initialDeckNumber?: number;
  className?: string;
}

export default function DeckReviewWorkspace({
  initialDeckNumber = 5,
  className = '',
}: DeckReviewWorkspaceProps) {
  const [selectedDeckNumber, setSelectedDeckNumber] = useState<number>(initialDeckNumber);
  const [reviewerName, setReviewerName] = useState<string>('');
  const [reviewerError, setReviewerError] = useState<string | null>(null);
  const [stagedDecisions, setStagedDecisions] = useState<
    Record<string, { state: ReviewDecisionState; note?: string; reviewer?: string; reviewedAt?: string }>
  >({});
  const [selectedObjectId, setSelectedObjectId] = useState<string | null>(null);
  const [filterState, setFilterState] = useState<string>('ALL');
  const [zoom, setZoom] = useState<number>(1.0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isFinalizeModalOpen, setIsFinalizeModalOpen] = useState<boolean>(false);
  const [finalizeResult, setFinalizeResult] = useState<FinalizeReviewResult | null>(null);
  const [previewMode, setPreviewMode] = useState<'REVIEW' | 'PASSENGER_PREVIEW'>('REVIEW');
  const [searchText, setSearchText] = useState<string>('');

  // Fail closed: an unsupported deck yields an explicit refusal, never another deck's proof.
  const loaded = useMemo((): { viewModel: DeckReviewWorkspaceViewModel | null; error: string | null } => {
    try {
      return { viewModel: buildDeckReviewWorkspaceViewModel(selectedDeckNumber, stagedDecisions), error: null };
    } catch (err: any) {
      return { viewModel: null, error: err?.message || `Deck ${selectedDeckNumber} is not available for review.` };
    }
  }, [selectedDeckNumber, stagedDecisions]);
  const candidates = loaded.viewModel?.candidates ?? [];

  const selectedCandidate = useMemo(() => {
    if (!selectedObjectId) return candidates[0] || null;
    return candidates.find((c) => c.objectId === selectedObjectId) || candidates[0] || null;
  }, [selectedObjectId, candidates]);

  const filteredCandidates = useMemo(() => {
    const byState = filterState === 'ALL' ? candidates : candidates.filter((c) => c.decision.state === filterState);
    const q = searchText.trim().toLowerCase();
    if (!q) return byState;
    return byState.filter((c) => c.extractedLabel.toLowerCase().includes(q) || c.objectId.toLowerCase().includes(q));
  }, [candidates, filterState, searchText]);

  const handleDecision = (objectId: string, decision: ReviewDecisionState) => {
    const actor = reviewerName.trim();
    setStagedDecisions((prev) => ({
      ...prev,
      [objectId]: {
        state: decision,
        reviewer: actor || undefined,
        note: prev[objectId]?.note || '',
        reviewedAt: new Date().toISOString(),
      },
    }));
  };

  const handleNoteChange = (objectId: string, note: string) => {
    const actor = reviewerName.trim();
    setStagedDecisions((prev) => ({
      ...prev,
      [objectId]: {
        state: prev[objectId]?.state || 'UNREVIEWED',
        reviewer: actor || undefined,
        note,
        reviewedAt: new Date().toISOString(),
      },
    }));
  };

  const handleDownloadStagedRecord = () => {
    if (!finalizeResult) return;
    const rec = finalizeResult.stagedRecord;
    const blob = new Blob([JSON.stringify(rec, null, 2) + '\n'], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `deck${String(rec.deck_number).padStart(2, '0')}.review.staged.${rec.generated_at.replace(/[:.]/g, '-')}.json`;
    // Attached before clicking and revoked out of band: a detached anchor plus a
    // synchronous revoke cancels the download in some browsers.
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  };

  const handleFinalize = () => {
    const actor = reviewerName.trim();
    if (!actor) {
      setReviewerError('Reviewer name is required before finalizing decisions.');
      return;
    }
    setReviewerError(null);
    try {
      const result = finalizeReviewedDecisions(selectedDeckNumber, stagedDecisions, actor);
      if (result.applicationStatus !== 'STAGED_NOT_APPLIED' || result.stagedRecord.applied_to_repository !== false) {
        throw new Error('Unexpected review application status; refusing to display result.');
      }
      setFinalizeResult(result);
    } catch (err: any) {
      setReviewerError(err?.message || 'Reviewer name is required before finalizing decisions.');
    }
  };

  if (!loaded.viewModel) {
    return (
      <div className={`w-full max-w-7xl mx-auto px-4 py-6 space-y-6 ${className}`}>
        <div role="alert" className="bg-white rounded-3xl p-6 border border-red-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2 text-red-700">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-xs font-mono font-bold uppercase tracking-widest">Review unavailable</span>
          </div>
          <h1 className="text-xl font-bold text-[#0C1B2A]">Deck {String(selectedDeckNumber)} is not available for review</h1>
          <p className="text-xs text-[#5B6570]">{loaded.error}</p>
          <p className="text-xs text-[#5B6570]">No other deck&apos;s proof is shown in its place.</p>
          <div className="flex flex-wrap gap-2 pt-1">
            {SUPPORTED_REVIEW_DECKS.map((n) => (
              <button
                key={n}
                onClick={() => {
                  setSelectedDeckNumber(n);
                  setSelectedObjectId(null);
                  setStagedDecisions({});
                }}
                className="px-3 py-1.5 rounded-xl text-xs font-semibold border border-slate-200 bg-white text-[#0C1B2A] hover:bg-slate-50 cursor-pointer"
              >
                Open Deck {n}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }
  const viewModel: DeckReviewWorkspaceViewModel = loaded.viewModel;
  const currentlyAdmittedCount = viewModel.candidates.filter((c) =>
    isAdmittedPassengerEntity({
      evidence_condition: c.evidenceCondition,
      human_review_state: c.humanReviewState,
      publish_status: c.publishStatus,
      geometry_provenance: c.geometryProvenance,
    }),
  ).length;

  // Display-only zoom, centred on the selected candidate so a human can read a
  // single cabin cell against the source raster. Never changes geometry.
  const baseViewBox = viewModel.sourceInfo.viewBox;
  const effectiveViewBox = (() => {
    if (zoom <= 1 || !selectedCandidate) return baseViewBox;
    const width = baseViewBox.width / zoom;
    const height = baseViewBox.height / zoom;
    return {
      minX: selectedCandidate.center[0] - width / 2,
      minY: selectedCandidate.center[1] - height / 2,
      width,
      height,
    };
  })();

  return (
    <div className={`w-full max-w-7xl mx-auto px-4 py-6 space-y-6 ${className}`}>
      {/* 1. Header & Mode Switcher */}
      <header className="bg-white rounded-3xl p-6 border border-[#0C1B2A]/10 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-full bg-[#0C1B2A]/5 text-[#0C1B2A]">
              <Shield className="w-4 h-4 text-[#C58A46]" />
            </span>
            <span className="text-xs font-mono font-bold tracking-widest text-[#C58A46] uppercase">
              HUMAN REVIEW WORKSPACE • ADR-0002 §5
            </span>
          </div>
          <h1 className="text-2xl font-display font-bold text-[#0C1B2A]">
            Public Deck Geometry Adjudication
          </h1>
          <p className="text-xs text-[#5B6570]">
            Visually compare extracted vector objects against official source drawings. Agent proposes, human reviewer decides.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto">
          <div className="inline-flex p-1 bg-slate-100 rounded-2xl border border-slate-200 text-xs font-semibold">
            <button
              onClick={() => setPreviewMode('REVIEW')}
              className={`px-4 py-2 rounded-xl transition-all cursor-pointer ${
                previewMode === 'REVIEW'
                  ? 'bg-white text-[#0C1B2A] shadow-sm'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Adjudication Workspace
            </button>
            <button
              onClick={() => setPreviewMode('PASSENGER_PREVIEW')}
              className={`px-4 py-2 rounded-xl transition-all cursor-pointer flex items-center gap-1.5 ${
                previewMode === 'PASSENGER_PREVIEW'
                  ? 'bg-white text-[#0C1B2A] shadow-sm'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Post-Gate Passenger Preview</span>
            </button>
          </div>
        </div>
      </header>

      {/* 2. Deck Selection, Reviewer Identity & Statistics Bar */}
      <section className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          {viewModel.availableDecks.map((deck) => {
            const isSelected = deck.deckNumber === selectedDeckNumber;
            return (
              <button
                key={deck.deckNumber}
                onClick={() => {
                  setSelectedDeckNumber(deck.deckNumber);
                  setSelectedObjectId(null);
                  setZoom(1.0);
                  setPan({ x: 0, y: 0 });
                }}
                className={`px-4 py-2 rounded-2xl text-xs font-semibold transition-all border flex items-center gap-2 cursor-pointer ${
                  isSelected
                    ? 'bg-[#0C1B2A] text-white border-[#0C1B2A] shadow-md'
                    : 'bg-white text-[#0C1B2A] border-slate-200 hover:bg-slate-50'
                }`}
              >
                <span>{deck.deckName}</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-200/40 text-slate-300">
                  {deck.objectCount} objects
                </span>
              </button>
            );
          })}
        </div>

        {/* Reviewer Name Input with Validation */}
        <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-2xl border border-slate-200 text-xs">
          <UserCheck className="w-3.5 h-3.5 text-[#C58A46]" />
          <span className="text-slate-500 font-medium">Reviewer:</span>
          <input
            type="text"
            value={reviewerName}
            onChange={(e) => {
              setReviewerName(e.target.value);
              if (e.target.value.trim()) setReviewerError(null);
            }}
            placeholder="Enter reviewer name"
            className="w-40 text-xs font-semibold text-[#0C1B2A] focus:outline-none placeholder:text-slate-300"
          />
        </div>

        {/* Staged Review Summary Counts */}
        <div className="flex items-center gap-3 text-xs font-mono">
          <span className="px-3 py-1 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200">
            Accept: {viewModel.summary.accepted}
          </span>
          <span className="px-3 py-1 rounded-xl bg-red-50 text-red-800 border border-red-200">
            Reject: {viewModel.summary.rejected}
          </span>
          <span className="px-3 py-1 rounded-xl bg-amber-50 text-amber-800 border border-amber-200">
            Correction: {viewModel.summary.needsCorrection}
          </span>
          <span className="px-3 py-1 rounded-xl bg-slate-100 text-slate-700 border border-slate-200">
            Unreviewed: {viewModel.summary.unreviewed}
          </span>
          <button
            onClick={() => {
              setIsFinalizeModalOpen(true);
              setFinalizeResult(null);
              setReviewerError(null);
            }}
            className="px-4 py-2 rounded-xl bg-[#C58A46] text-white text-xs font-semibold hover:bg-[#b07838] transition-colors shadow-sm cursor-pointer ml-2"
          >
            Finalize Decisions
          </button>
        </div>
      </section>

      {/* 3. Main Adjudication Grid: Canvas (Left) + Candidate List & Detail (Right) */}
      {previewMode === 'REVIEW' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Canvas Overlay Area (7 cols) */}
          <div className="lg:col-span-7 bg-[#111C28] rounded-3xl p-4 border border-slate-800 shadow-inner relative overflow-hidden flex flex-col items-center justify-center min-h-[500px]">
            <div className="absolute top-4 left-4 z-10 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-xl text-[11px] text-slate-300 font-mono flex items-center gap-2 border border-white/10">
              <FileText className="w-3.5 h-3.5 text-[#C58A46]" />
              <span>Source: {viewModel.sourceInfo.artifactId} (Page {viewModel.sourceInfo.pageNumber})</span>
              {viewModel.sourceInfo.sourceImageSha256 ? (
                <span
                  className={viewModel.sourceInfo.sourceImageVerification === 'REPRODUCED' ? 'text-slate-500' : 'text-amber-400'}
                  title={viewModel.sourceInfo.sourceImageProvenanceRecord || undefined}
                >
                  raster sha256 {viewModel.sourceInfo.sourceImageSha256.slice(0, 12)}…{' '}
                  {viewModel.sourceInfo.sourceImageVerification === 'REPRODUCED'
                    ? '(re-rendered from source)'
                    : '(page binding declared, not reproduced)'}
                </span>
              ) : (
                <span className="text-amber-400">raster provenance not recorded</span>
              )}
              <span className="text-slate-500">proof sha256 {viewModel.sourceInfo.proofSha256.slice(0, 12)}…</span>
            </div>

            {/* SVG Canvas Overlaying Source Background */}
            <div className="w-full h-full relative flex items-center justify-center">
              <svg
                className="w-full h-auto max-h-[600px] select-none"
                viewBox={`${effectiveViewBox.minX} ${effectiveViewBox.minY} ${effectiveViewBox.width} ${effectiveViewBox.height}`}
                preserveAspectRatio="xMidYMid meet"
              >
                {/* Source raster drawing crop underlay */}
                {/* Source context only. Not proof geometry, not hit-test
                    authority, and nothing semantic is derived from its pixels.
                    Marked and made unpickable the same way the spatial-proof
                    viewer marks it, so the same invariant holds on both
                    surfaces that draw this raster. */}
                <image
                  href={viewModel.sourceInfo.sourceImageUri}
                  data-layer="source-context"
                  style={{ pointerEvents: "none" }}
                  x="0"
                  y="0"
                  width="1"
                  height="1"
                  preserveAspectRatio="none"
                  opacity="0.85"
                />

                {/* Extracted Vector Polygons */}
                {viewModel.candidates.map((c) => {
                  const isSelected = c.objectId === selectedCandidate?.objectId;
                  const pts = c.normalizedPolygon.map((p) => `${p[0]},${p[1]}`).join(' ');

                  let fill = 'rgba(255, 255, 255, 0.15)';
                  let stroke = '#60A5FA';

                  if (c.decision.state === 'ACCEPT') {
                    fill = 'rgba(16, 185, 129, 0.25)';
                    stroke = '#10B981';
                  } else if (c.decision.state === 'REJECT') {
                    fill = 'rgba(239, 68, 68, 0.25)';
                    stroke = '#EF4444';
                  } else if (c.decision.state === 'NEEDS_CORRECTION') {
                    fill = 'rgba(245, 158, 11, 0.25)';
                    stroke = '#F59E0B';
                  }

                  if (isSelected) {
                    fill = zoom > 1 ? 'rgba(197, 138, 70, 0.12)' : 'rgba(197, 138, 70, 0.4)';
                    stroke = '#C58A46';
                  }

                  return (
                    <g key={c.objectId} onClick={() => setSelectedObjectId(c.objectId)} className="cursor-pointer">
                      <polygon
                        points={pts}
                        fill={fill}
                        stroke={stroke}
                        strokeWidth={(isSelected ? 0.003 : 0.0012) / zoom}
                      />
                      {isSelected && (
                        <polygon
                          points={pts}
                          fill="none"
                          stroke="#FFFFFF"
                          strokeWidth={0.004 / zoom}
                          strokeDasharray={`${0.003 / zoom} ${0.002 / zoom}`}
                        />
                      )}
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* Canvas Zoom Controls */}
            <div className="absolute bottom-4 right-4 flex gap-2 z-10">
              <button
                onClick={() => setZoom((z) => Math.min(z * 1.5, 12.0))}
                aria-label="Zoom in"
                className="p-2 rounded-xl bg-white/90 text-[#0C1B2A] hover:bg-white cursor-pointer shadow-md"
              >
                <ZoomIn className="w-4 h-4" />
              </button>
              <button
                onClick={() => setZoom((z) => Math.max(z / 1.5, 1.0))}
                aria-label="Zoom out"
                className="p-2 rounded-xl bg-white/90 text-[#0C1B2A] hover:bg-white cursor-pointer shadow-md"
              >
                <ZoomOut className="w-4 h-4" />
              </button>
              <button
                onClick={() => {
                  setZoom(1.0);
                  setPan({ x: 0, y: 0 });
                }}
                aria-label="Fit to deck"
                className="p-2 rounded-xl bg-white/90 text-[#0C1B2A] hover:bg-white cursor-pointer shadow-md"
              >
                <Maximize2 className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Right Panels (5 cols): Object List + Selected Object Detail */}
          <div className="lg:col-span-5 space-y-6">
            {/* Candidate List Filter */}
            <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-[#0C1B2A] uppercase tracking-wider">CANDIDATE OBJECTS</span>
                <span className="text-slate-400 font-mono">{filteredCandidates.length} of {viewModel.candidates.length}</span>
              </div>

              <input
                type="search"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                placeholder="Find candidate (e.g. 14122)"
                aria-label="Find candidate"
                className="w-full text-xs p-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-1 focus:ring-[#C58A46]"
              />

              <div className="flex gap-1.5 overflow-x-auto pb-1 text-[11px] font-semibold">
                {['ALL', 'UNREVIEWED', 'ACCEPT', 'REJECT', 'NEEDS_CORRECTION'].map((st) => (
                  <button
                    key={st}
                    onClick={() => setFilterState(st)}
                    className={`px-2.5 py-1 rounded-lg border transition-colors cursor-pointer ${
                      filterState === st
                        ? 'bg-[#0C1B2A] text-white border-[#0C1B2A]'
                        : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {st}
                  </button>
                ))}
              </div>

              {/* Scrollable Object Items */}
              <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1">
                {filteredCandidates.map((c) => {
                  const isSelected = c.objectId === selectedCandidate?.objectId;
                  return (
                    <button
                      key={c.objectId}
                      onClick={() => setSelectedObjectId(c.objectId)}
                      className={`w-full text-left p-2.5 rounded-xl border text-xs flex items-center justify-between transition-all cursor-pointer ${
                        isSelected
                          ? 'bg-[#C58A46]/10 border-[#C58A46] text-[#0C1B2A] font-semibold shadow-sm'
                          : 'bg-slate-50/60 border-slate-200/60 text-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      <div>
                        <span className="block">{c.extractedLabel}</span>
                        <span className="text-[10px] text-slate-400 font-mono">{c.candidateCategory}</span>
                      </div>
                      <span
                        className={`text-[9px] font-mono px-2 py-0.5 rounded-full border ${
                          c.decision.state === 'ACCEPT'
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                            : c.decision.state === 'REJECT'
                            ? 'bg-red-50 text-red-700 border-red-200'
                            : c.decision.state === 'NEEDS_CORRECTION'
                            ? 'bg-amber-50 text-amber-700 border-amber-200'
                            : 'bg-slate-200 text-slate-600 border-slate-300'
                        }`}
                      >
                        {c.decision.state}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Selected Object Detail & Decision Card */}
            {selectedCandidate && (
              <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-md space-y-4">
                <div className="flex items-start justify-between gap-2 border-b border-slate-100 pb-3">
                  <div>
                    <span className="text-[10px] font-mono uppercase tracking-wider text-[#C58A46] font-bold">
                      DECK {selectedCandidate.deckNumber} • {selectedCandidate.candidateCategory}
                    </span>
                    <h3 className="text-lg font-bold text-[#0C1B2A]">
                      Candidate label: {selectedCandidate.extractedLabel}
                    </h3>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-1 rounded bg-slate-100 text-slate-600 border">
                    {selectedCandidate.geometryProvenance}
                  </span>
                </div>

                {/* Scope Disclosure Alert */}
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-500 leading-relaxed">
                  <strong className="text-slate-700 block">Geometry Review Scope:</strong>
                  Acceptance confirms this polygon corresponds to the labeled region on official drawings. It does not establish entrance location, passenger access, connectivity, or accessibility.
                  <span className="block mt-1 font-semibold">
                    Accepting is a review act, not evidence. It does not change this object&apos;s evidence condition and cannot make it publishable.
                  </span>
                </div>

                {selectedCandidate.identityPath === 'CABIN' && (
                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-700">Cabin Identity Statement Association:</span>
                      <span className="font-mono text-[10px] px-2 py-0.5 rounded border font-bold bg-slate-200 text-slate-700 border-slate-300">
                        {selectedCandidate.cabinIdentity?.state}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 leading-relaxed">{selectedCandidate.cabinIdentity?.reason}</p>
                    <div className="text-[11px] font-mono text-slate-500 space-y-0.5">
                      <div>Entity: {selectedCandidate.cabinIdentity?.expectedEntityId || '—'}</div>
                      <div>cabin.exists: {selectedCandidate.cabinIdentity?.existsStatementId || '—'}</div>
                      <div>cabin.deck: {selectedCandidate.cabinIdentity?.deckStatementId || '—'}</div>
                      <div>Vessel ownership consistent: {selectedCandidate.cabinIdentity?.vesselOwnershipConsistent ? 'yes' : 'no'}</div>
                    </div>
                    {(selectedCandidate.cabinIdentity?.blockers.length ?? 0) > 0 && (
                      <ul className="list-disc pl-4 text-[11px] text-amber-800 space-y-0.5">
                        {selectedCandidate.cabinIdentity!.blockers.map((b) => (
                          <li key={b}>{b}</li>
                        ))}
                      </ul>
                    )}
                    <p className="text-[11px] text-slate-500">
                      Accepting geometry confirms the envelope only. It does not admit the cabin&apos;s identity.
                    </p>
                    <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px]">
                      <span className="text-slate-500">Admitted Passenger Identity:</span>
                      <span className={`font-semibold ${selectedCandidate.isAdmittedIdentity ? 'text-emerald-700' : 'text-amber-700'}`}>
                        {selectedCandidate.isAdmittedIdentity ? 'ADMITTED (Verified)' : 'UNADMITTED (Draft/Blocked)'}
                      </span>
                    </div>
                  </div>
                )}

                {/* Evidence & Identity Admissibility Box */}
                {selectedCandidate.identityPath !== 'CABIN' && (
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-700">Venue Statement Association:</span>
                    <span
                      className={`font-mono text-[10px] px-2 py-0.5 rounded border font-bold ${
                        selectedCandidate.venueAssociation.state === 'MATCHED'
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                          : selectedCandidate.venueAssociation.state === 'AMBIGUOUS'
                          ? 'bg-amber-50 text-amber-700 border-amber-200'
                          : 'bg-slate-200 text-slate-700 border-slate-300'
                      }`}
                    >
                      {selectedCandidate.venueAssociation.state}
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-500 leading-relaxed">
                    {selectedCandidate.venueAssociation.reason}
                  </p>

                  <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px]">
                    <span className="text-slate-500">Admitted Passenger Identity:</span>
                    <span
                      className={`font-semibold ${
                        selectedCandidate.isAdmittedIdentity ? 'text-emerald-700' : 'text-amber-700'
                      }`}
                    >
                      {selectedCandidate.isAdmittedIdentity ? 'ADMITTED (Verified)' : 'UNADMITTED (Draft/Blocked)'}
                    </span>
                  </div>
                </div>
                )}

                {/* Technical Coordinates */}
                <div className="text-[11px] font-mono text-slate-500 space-y-1 bg-slate-100/50 p-2.5 rounded-xl">
                  <div>ID: {selectedCandidate.objectId}</div>
                  <div>Source: PDF page {selectedCandidate.sourcePage}</div>
                  <div>Locator: {selectedCandidate.sourceLocator}</div>
                  <div>
                    Lifecycle: {selectedCandidate.evidenceCondition} / {selectedCandidate.humanReviewState} / {selectedCandidate.publishStatus}
                  </div>
                  <div>
                    BBox: [{selectedCandidate.normalizedBbox.map((n) => n.toFixed(4)).join(', ')}]
                  </div>
                </div>

                {/* Decision Actions */}
                <div className="space-y-2 pt-2">
                  <span className="text-xs font-bold text-[#0C1B2A] block uppercase tracking-wider">
                    HUMAN REVIEW DECISION
                  </span>
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      onClick={() => handleDecision(selectedCandidate.objectId, 'ACCEPT')}
                      className={`py-2 px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 border transition-all cursor-pointer ${
                        selectedCandidate.decision.state === 'ACCEPT'
                          ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                          : 'bg-white text-emerald-700 border-emerald-200 hover:bg-emerald-50'
                      }`}
                    >
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>Accept</span>
                    </button>

                    <button
                      onClick={() => handleDecision(selectedCandidate.objectId, 'REJECT')}
                      className={`py-2 px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 border transition-all cursor-pointer ${
                        selectedCandidate.decision.state === 'REJECT'
                          ? 'bg-red-600 text-white border-red-600 shadow-sm'
                          : 'bg-white text-red-700 border-red-200 hover:bg-red-50'
                      }`}
                    >
                      <XCircle className="w-3.5 h-3.5" />
                      <span>Reject</span>
                    </button>

                    <button
                      onClick={() => handleDecision(selectedCandidate.objectId, 'NEEDS_CORRECTION')}
                      className={`py-2 px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 border transition-all cursor-pointer ${
                        selectedCandidate.decision.state === 'NEEDS_CORRECTION'
                          ? 'bg-amber-500 text-white border-amber-500 shadow-sm'
                          : 'bg-white text-amber-700 border-amber-200 hover:bg-amber-50'
                      }`}
                    >
                      <AlertTriangle className="w-3.5 h-3.5" />
                      <span>Correction</span>
                    </button>
                  </div>

                  {selectedCandidate.decision.state !== 'UNREVIEWED' && (
                    <button
                      onClick={() => handleDecision(selectedCandidate.objectId, 'UNREVIEWED')}
                      className="text-[11px] text-slate-400 hover:text-slate-600 underline text-center block w-full pt-1 cursor-pointer"
                    >
                      Clear decision
                    </button>
                  )}
                </div>

                {/* Reviewer Note */}
                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-slate-600">Reviewer Note (Optional):</label>
                  <input
                    type="text"
                    value={selectedCandidate.decision.note || ''}
                    onChange={(e) => handleNoteChange(selectedCandidate.objectId, e.target.value)}
                    placeholder="What did you compare on the source drawing?"
                    className="w-full text-xs p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-1 focus:ring-[#C58A46]"
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Post-Gate Passenger Preview */
        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-6">
          <div className="flex items-center gap-3">
            <span className="p-2 rounded-xl bg-emerald-100 text-emerald-800">
              <Eye className="w-5 h-5" />
            </span>
            <div>
              <h2 className="text-lg font-bold text-[#0C1B2A]">Post-Gate Passenger Preview</h2>
              <p className="text-xs text-[#5B6570]">
                Shows exclusively what is currently admitted for passenger publication under Gatekeeper rules.
              </p>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200 text-center space-y-3">
            <Info className="w-6 h-6 text-slate-400 mx-auto" />
            <p className="text-xs text-slate-600 font-medium max-w-lg mx-auto leading-relaxed">
              In repository truth, {currentlyAdmittedCount} of {viewModel.summary.total} Deck {viewModel.selectedDeckNumber} objects are currently admitted for passenger publication. Decisions made in this workspace are staged only and do not change this count.
            </p>
            <div className="inline-block px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-xs font-mono text-slate-700 font-bold">
              Admitted on Deck {viewModel.selectedDeckNumber}: {currentlyAdmittedCount}
            </div>
          </div>
        </div>
      )}

      {/* 4. Finalization Modal */}
      {isFinalizeModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl border border-slate-200 space-y-6 animate-fadeIn">
            <div className="space-y-1">
              <span className="text-xs font-mono text-[#C58A46] font-bold uppercase">FINALIZATION SUMMARY</span>
              <h2 className="text-xl font-bold text-[#0C1B2A]">Generate Staged Review Record</h2>
              <p className="text-xs text-[#5B6570]">
                Produces a review record of your explicit decisions for Deck {selectedDeckNumber}. It is not saved to the repository and changes no proof or lifecycle state until applied through the governed repository path.
              </p>
            </div>

            {/* Reviewer Name Required Indicator */}
            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
                <UserCheck className="w-3.5 h-3.5 text-[#C58A46]" />
                <span>Explicit Reviewer Name (Required):</span>
              </label>
              <input
                type="text"
                value={reviewerName}
                onChange={(e) => {
                  setReviewerName(e.target.value);
                  if (e.target.value.trim()) setReviewerError(null);
                }}
                placeholder="e.g. Curator Name (cannot be empty)"
                className="w-full text-xs p-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-1 focus:ring-[#C58A46] bg-white font-medium"
              />
              {reviewerError && (
                <div className="text-[11px] font-semibold text-red-600 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" />
                  <span>{reviewerError}</span>
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 rounded-xl bg-slate-50 border">
                <span className="text-slate-500 block">Deck {selectedDeckNumber}:</span>
                <span className="font-bold text-[#0C1B2A] text-sm">{viewModel.summary.total} Total Objects</span>
              </div>
              <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800">
                <span className="block">Accepted:</span>
                <span className="font-bold text-sm">{viewModel.summary.accepted}</span>
              </div>
              <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-800">
                <span className="block">Rejected:</span>
                <span className="font-bold text-sm">{viewModel.summary.rejected}</span>
              </div>
              <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-800">
                <span className="block">Needs Correction:</span>
                <span className="font-bold text-sm">{viewModel.summary.needsCorrection}</span>
              </div>
            </div>

            {finalizeResult && (
              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 space-y-1">
                <span className="font-bold block">Review record STAGED — not applied to the repository</span>
                <div>Decisions in record: {finalizeResult.adjudicatedObjectsCount} objects</div>
                <div>Reviewer: {finalizeResult.stagedRecord.reviewer}</div>
                <div>Source: {finalizeResult.stagedRecord.source.artifact_id} PDF page {finalizeResult.stagedRecord.source.pdf_page_number}</div>
                <div>Would become publishable if applied: {finalizeResult.promotedToPassengerCount} (a review decision never creates evidence)</div>
                <div>Would remain publication-blocked: {finalizeResult.blockedCount}</div>
                <div>Proof reviewed: {finalizeResult.stagedRecord.proof_sha256.slice(0, 12)}…</div>
                <div>Nothing has been persisted. Download the record and apply it through the repository to make it durable.</div>
                <button
                  onClick={handleDownloadStagedRecord}
                  className="mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-amber-300 bg-white text-amber-900 font-semibold cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download staged review record (JSON)</span>
                </button>
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => {
                  setIsFinalizeModalOpen(false);
                  setFinalizeResult(null);
                  setReviewerError(null);
                }}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 cursor-pointer"
              >
                Close
              </button>
              <button
                onClick={handleFinalize}
                className="px-5 py-2.5 rounded-xl bg-[#0C1B2A] text-white text-xs font-semibold hover:bg-[#1e344d] transition-colors shadow-md cursor-pointer"
              >
                Generate Staged Record
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
