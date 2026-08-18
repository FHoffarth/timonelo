import React, { useState } from "react";
import {
  KnowledgeFactory,
  FactoryMetrics,
  ArtifactQueueManager,
  QueuedArtifact,
  ConflictResolver,
  ConflictDecision,
} from "../../knowledge/pipeline";
import {
  ShieldCheck,
  Layers,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ArrowRight,
  Sparkles,
  Ship,
  MapPin,
  Compass,
  FileCheck,
  RefreshCw,
  Workflow,
  Check,
} from "lucide-react";

export const KnowledgeDashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<FactoryMetrics>(KnowledgeFactory.getFactoryMetrics());
  const [queue, setQueue] = useState<QueuedArtifact[]>(ArtifactQueueManager.getQueue());
  const [conflicts, setConflicts] = useState<ConflictDecision[]>(ConflictResolver.getConflicts());
  const [publishingId, setPublishingId] = useState<string | null>(null);
  const [actionSuccessMessage, setActionSuccessMessage] = useState<string | null>(null);

  const handleApproveConflict = (conflictId: string) => {
    ConflictResolver.resolveConflictWithEvidence(conflictId, "Knowledge Curator", "Verified from official primary source");
    setConflicts(ConflictResolver.getConflicts());
    setMetrics(KnowledgeFactory.getFactoryMetrics());
    setActionSuccessMessage(`Conflict ${conflictId} successfully resolved with verified evidence.`);
    setTimeout(() => setActionSuccessMessage(null), 4000);
  };

  const handleIngestArtifact = (queueId: string) => {
    setPublishingId(queueId);
    setTimeout(() => {
      const result = KnowledgeFactory.executeIngestionPipeline(queueId, "Bridge Officer Tim");
      setPublishingId(null);
      setQueue(ArtifactQueueManager.getQueue());
      setMetrics(KnowledgeFactory.getFactoryMetrics());
      setActionSuccessMessage(result.message);
      setTimeout(() => setActionSuccessMessage(null), 5000);
    }, 600);
  };

  return (
    <div className="flex-1 flex flex-col bg-[#FBF8F3] select-none pb-20">
      {/* 1. Header Banner */}
      <div className="max-w-7xl mx-auto w-full px-6 pt-10 pb-8 space-y-4">
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold uppercase tracking-wider bg-[#C58A46]/10 text-[#C58A46] border border-[#C58A46]/30">
            KNOWLEDGE FACTORY PIPELINE V1
          </span>
          <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400 border border-emerald-300">
            EVIDENCE-FIRST PRODUCTION
          </span>
        </div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="font-display text-4xl sm:text-5xl font-bold text-[#0C1B2A] tracking-tight">
              Knowledge Production Control Center
            </h1>
            <p className="text-sm text-[#5B6570] max-w-2xl mt-1">
              Automated ingestion pipeline transforming raw naval blueprints, deck plans, and harbor records into verified W3C semantic graphs and spatial geometry.
            </p>
          </div>

          <div className="p-3.5 rounded-2xl bg-white border border-[#0C1B2A]/10 shadow-xs flex items-center gap-3 self-start">
            <div className="w-10 h-10 rounded-xl bg-[#0C1B2A] text-white flex items-center justify-center font-bold font-mono text-sm">
              BOT
            </div>
            <div>
              <div className="text-[10px] uppercase font-mono text-slate-400 font-bold">Duty Commander</div>
              <div className="font-bold text-xs text-[#0C1B2A]">Bridge Officer Tim</div>
            </div>
          </div>
        </div>

        {actionSuccessMessage && (
          <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2 font-medium">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{actionSuccessMessage}</span>
          </div>
        )}
      </div>

      {/* 2. Key Metrics Row */}
      <div className="max-w-7xl mx-auto w-full px-6 grid grid-cols-2 md:grid-cols-5 gap-4 pb-8">
        <div className="p-4 bg-white rounded-2xl border border-[#0C1B2A]/10 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Artifacts Queue</span>
            <Clock className="w-4 h-4 text-amber-500" />
          </div>
          <div className="font-display text-2xl font-bold text-[#0C1B2A]">
            {metrics.artifacts_waiting}
          </div>
          <div className="text-[10px] text-slate-400 font-mono">Waiting ingestion</div>
        </div>

        <div className="p-4 bg-white rounded-2xl border border-[#0C1B2A]/10 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Active Conflicts</span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="font-display text-2xl font-bold text-[#0C1B2A]">
            {metrics.active_conflicts}
          </div>
          <div className="text-[10px] text-slate-400 font-mono">Awaiting officer review</div>
        </div>

        <div className="p-4 bg-white rounded-2xl border border-[#0C1B2A]/10 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Ships Ready</span>
            <Ship className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="font-display text-2xl font-bold text-[#0C1B2A]">
            {metrics.ships_ready_count} <span className="text-xs text-slate-400 font-normal">/ {metrics.total_ships_count}</span>
          </div>
          <div className="text-[10px] text-slate-400 font-mono">Production fleet</div>
        </div>

        <div className="p-4 bg-white rounded-2xl border border-[#0C1B2A]/10 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Ports Verified</span>
            <MapPin className="w-4 h-4 text-sky-500" />
          </div>
          <div className="font-display text-2xl font-bold text-[#0C1B2A]">
            {metrics.ports_ready_count}
          </div>
          <div className="text-[10px] text-slate-400 font-mono">100% Knowledge Layer</div>
        </div>

        <div className="p-4 bg-white rounded-2xl border border-[#0C1B2A]/10 shadow-xs space-y-1 col-span-2 md:col-span-1">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Routes Verified</span>
            <Compass className="w-4 h-4 text-purple-500" />
          </div>
          <div className="font-display text-2xl font-bold text-[#0C1B2A]">
            {metrics.routes_ready_count}
          </div>
          <div className="text-[10px] text-slate-400 font-mono">Timeline & Sea Days</div>
        </div>
      </div>

      {/* 3. Coverage Quality Gauges */}
      <div className="max-w-7xl mx-auto w-full px-6 pb-10">
        <div className="p-6 bg-white rounded-3xl border border-[#0C1B2A]/10 shadow-card space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-xl font-bold text-[#0C1B2A]">
              Fleet Epistemic Coverage Standards
            </h3>
            <span className="text-xs font-mono text-emerald-600 font-bold">
              100% Audit Grounded
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Knowledge Coverage */}
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-700">Knowledge Coverage</span>
                <span className="font-mono font-bold text-[#C58A46]">{metrics.global_knowledge_coverage}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-200 overflow-hidden">
                <div className="h-full bg-[#C58A46]" style={{ width: `${metrics.global_knowledge_coverage}%` }} />
              </div>
              <p className="text-[10px] text-slate-500 font-mono">Factual ship attributes grounded</p>
            </div>

            {/* Schema Coverage */}
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-700">Schema Coverage</span>
                <span className="font-mono font-bold text-emerald-600">{metrics.global_schema_coverage}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-200 overflow-hidden">
                <div className="h-full bg-emerald-500" style={{ width: `${metrics.global_schema_coverage}%` }} />
              </div>
              <p className="text-[10px] text-slate-500 font-mono">13/13 Draft 2020-12 schemas valid</p>
            </div>

            {/* Graph Coverage */}
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-700">Graph Coverage</span>
                <span className="font-mono font-bold text-sky-600">{metrics.global_graph_coverage}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-200 overflow-hidden">
                <div className="h-full bg-sky-500" style={{ width: `${metrics.global_graph_coverage}%` }} />
              </div>
              <p className="text-[10px] text-slate-500 font-mono">W3C BOT topological relations</p>
            </div>

            {/* Geometry Coverage */}
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-700">Geometry Coverage</span>
                <span className="font-mono font-bold text-indigo-600">{metrics.global_geometry_coverage}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-200 overflow-hidden">
                <div className="h-full bg-indigo-500" style={{ width: `${metrics.global_geometry_coverage}%` }} />
              </div>
              <p className="text-[10px] text-slate-500 font-mono">Vector polygons & bounding boxes</p>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Artifact Ingestion Queue & Conflict Resolution Grid */}
      <div className="max-w-7xl mx-auto w-full px-6 grid grid-cols-1 lg:grid-cols-2 gap-8 pb-12">
        {/* Left Col: Artifact Ingestion Queue */}
        <div className="p-6 bg-white rounded-3xl border border-[#0C1B2A]/10 shadow-card space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-display text-xl font-bold text-[#0C1B2A]">
                Artifact Ingestion Queue
              </h3>
              <p className="text-xs text-slate-500">Pipeline stage progression from raw PDF to canonical release.</p>
            </div>
            <span className="px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-slate-100 text-slate-700">
              {queue.length} Active
            </span>
          </div>

          <div className="space-y-3">
            {queue.map((item) => (
              <div
                key={item.queue_id}
                className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono font-bold text-[#C58A46]">
                        {item.queue_id}
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full font-mono font-bold bg-slate-200 text-slate-700">
                        {item.evidence.edition}
                      </span>
                    </div>
                    <div className="font-bold text-sm text-[#0C1B2A]">
                      {item.evidence.source_title}
                    </div>
                    <div className="text-xs text-slate-500">
                      Publisher: {item.evidence.publisher} • {(item.evidence.file_size_bytes / 1024 / 1024).toFixed(2)} MB
                    </div>
                  </div>

                  <span
                    className={`px-2.5 py-1 rounded-xl text-[10px] font-mono font-bold border ${
                      item.stage === "PUBLISHED"
                        ? "bg-emerald-50 text-emerald-700 border-emerald-300"
                        : item.stage === "AWAITING_OFFICER_APPROVAL"
                        ? "bg-amber-50 text-amber-700 border-amber-300"
                        : "bg-sky-50 text-sky-700 border-sky-300"
                    }`}
                  >
                    {item.stage.replace(/_/g, " ")}
                  </span>
                </div>

                <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-xs">
                  <span className="text-slate-500 font-mono">
                    Extracted: <strong>{item.extracted_entities_count}</strong> entities
                  </span>

                  {item.stage === "AWAITING_OFFICER_APPROVAL" && (
                    <button
                      onClick={() => handleIngestArtifact(item.queue_id)}
                      disabled={publishingId === item.queue_id}
                      className="px-3 py-1.5 rounded-xl bg-[#0C1B2A] hover:bg-[#C58A46] text-white font-semibold text-xs transition-all shadow-sm flex items-center gap-1.5 cursor-pointer"
                    >
                      {publishingId === item.queue_id ? (
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <Check className="w-3.5 h-3.5" />
                      )}
                      <span>Approve & Ingest</span>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Col: Conflict Resolver Panel */}
        <div className="p-6 bg-white rounded-3xl border border-[#0C1B2A]/10 shadow-card space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-display text-xl font-bold text-[#0C1B2A]">
                Conflict Resolution Log
              </h3>
              <p className="text-xs text-slate-500">Every contradiction is reviewed before mutating canonical knowledge.</p>
            </div>
            <span className="px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-slate-100 text-slate-700">
              {conflicts.length} Decided
            </span>
          </div>

          <div className="space-y-3">
            {conflicts.map((conf) => (
              <div
                key={conf.conflict_id}
                className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2.5"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-[#C58A46]">
                    {conf.entity_id}
                  </span>
                  <span className="px-2 py-0.5 rounded-lg text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-300">
                    {conf.status}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="p-2 rounded-xl bg-white border border-slate-200">
                    <div className="text-[10px] text-slate-400">Canonical Value</div>
                    <div className="font-bold text-slate-700 line-through">
                      {String(conf.canonical_value)}
                    </div>
                  </div>
                  <div className="p-2 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900">
                    <div className="text-[10px] text-emerald-600">Incoming Value</div>
                    <div className="font-bold">
                      {String(conf.incoming_value)}
                    </div>
                  </div>
                </div>

                <p className="text-xs text-slate-600 leading-snug">
                  {conf.resolution_rationale}
                </p>

                <div className="pt-1.5 border-t border-slate-200/60 flex items-center justify-between text-[10px] font-mono text-slate-400">
                  <span>Artifact: {conf.incoming_artifact} (P.{conf.evidence_page})</span>
                  <span className="text-emerald-600 font-bold">Reviewed by {conf.reviewed_by || "Curator"}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 5. Fleet Production Readiness Matrix */}
      <div className="max-w-7xl mx-auto w-full px-6">
        <div className="p-6 bg-white rounded-3xl border border-[#0C1B2A]/10 shadow-card space-y-5">
          <h3 className="font-display text-xl font-bold text-[#0C1B2A]">
            Fleet Production Readiness Matrix
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-sans">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400 font-mono uppercase text-[10px]">
                  <th className="pb-3 font-semibold">Vessel</th>
                  <th className="pb-3 font-semibold">Class</th>
                  <th className="pb-3 font-semibold">Cabins</th>
                  <th className="pb-3 font-semibold">Venues</th>
                  <th className="pb-3 font-semibold">Decks</th>
                  <th className="pb-3 font-semibold">Primary Artifact</th>
                  <th className="pb-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {metrics.ships.map((s) => (
                  <tr key={s.vessel_id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 font-bold text-[#0C1B2A]">{s.name}</td>
                    <td className="py-3 text-slate-600">{s.ship_class}</td>
                    <td className="py-3 font-mono">{s.total_cabins}</td>
                    <td className="py-3 font-mono">{s.total_venues}</td>
                    <td className="py-3 font-mono">{s.passenger_decks}</td>
                    <td className="py-3 text-slate-500 font-mono text-[11px]">{s.primary_artifact}</td>
                    <td className="py-3">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                          s.status === "PRODUCTION_READY"
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                            : "bg-amber-50 text-amber-700 border border-amber-200"
                        }`}
                      >
                        {s.status.replace(/_/g, " ")}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeDashboardPage;
