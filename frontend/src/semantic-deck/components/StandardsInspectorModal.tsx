import React, { useState } from "react";
import { SemanticEntity, StandardsExportPayload } from "../types";
import { TimoneloSpatialApiClient } from "../apiClient";
import { X, Code2, Layers, History, Globe2, Copy, Check } from "lucide-react";

interface StandardsInspectorModalProps {
  entity: SemanticEntity;
  client: TimoneloSpatialApiClient;
  requestedVesselId: string;
  onClose: () => void;
}

export default function StandardsInspectorModal({
  entity,
  client,
  requestedVesselId,
  onClose,
}: StandardsInspectorModalProps) {
  const [activeFormat, setActiveFormat] = useState<"json_ld" | "bot" | "prov_o" | "indoor_gml">("json_ld");
  const [copied, setCopied] = useState(false);

  const payload: StandardsExportPayload = client.exportStandardsPayload(
    entity,
    requestedVesselId,
  );

  const getActiveContent = (): string => {
    switch (activeFormat) {
      case "json_ld":
        return JSON.stringify(payload.json_ld, null, 2);
      case "bot":
        return payload.bot_turtle;
      case "prov_o":
        return payload.prov_o_turtle;
      case "indoor_gml":
        return payload.indoor_gml_xml;
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(getActiveContent());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-in fade-in duration-200 select-none">
      <div className="relative w-full max-w-4xl max-h-[85vh] bg-slate-900/95 border border-white/10 rounded-3xl shadow-2xl flex flex-col overflow-hidden text-slate-300">
        {/* Header */}
        <div className="p-6 bg-gradient-to-r from-slate-900 via-sky-950/40 to-slate-900 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-sky-500/20 border border-sky-400/30 flex items-center justify-center text-sky-400">
              <Code2 className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white tracking-tight">
                  International Standards & Linked Data Inspector
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  CANONICAL GRAPH EXPORT
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                {entity.iri} • Epistemic State: {entity.epistemic_state}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Format Selector Tabs */}
        <div className="px-6 py-2.5 bg-slate-900/80 border-b border-white/5 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveFormat("json_ld")}
              className={`px-3 py-1.5 rounded-xl font-semibold transition-colors flex items-center gap-1.5 ${
                activeFormat === "json_ld"
                  ? "bg-sky-500/20 text-sky-300 border border-sky-400/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
              }`}
            >
              <Globe2 className="w-3.5 h-3.5" />
              JSON-LD (Linked Data)
            </button>
            <button
              onClick={() => setActiveFormat("bot")}
              className={`px-3 py-1.5 rounded-xl font-semibold transition-colors flex items-center gap-1.5 ${
                activeFormat === "bot"
                  ? "bg-sky-500/20 text-sky-300 border border-sky-400/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              W3C BOT (Building Topology)
            </button>
            <button
              onClick={() => setActiveFormat("prov_o")}
              className={`px-3 py-1.5 rounded-xl font-semibold transition-colors flex items-center gap-1.5 ${
                activeFormat === "prov_o"
                  ? "bg-sky-500/20 text-sky-300 border border-sky-400/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
              }`}
            >
              <History className="w-3.5 h-3.5" />
              W3C PROV-O (Provenance)
            </button>
            <button
              onClick={() => setActiveFormat("indoor_gml")}
              className={`px-3 py-1.5 rounded-xl font-semibold transition-colors flex items-center gap-1.5 ${
                activeFormat === "indoor_gml"
                  ? "bg-sky-500/20 text-sky-300 border border-sky-400/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
              }`}
            >
              <Code2 className="w-3.5 h-3.5" />
              OGC IndoorGML (Spatial)
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center gap-1.5 border border-white/10 transition-all active:scale-95"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? "Copied" : "Copy"}
          </button>
        </div>

        {/* Code Content */}
        <div className="flex-1 p-6 overflow-y-auto font-mono text-xs text-sky-200 bg-slate-950/80 no-scrollbar">
          <pre className="whitespace-pre-wrap leading-relaxed">
            {getActiveContent()}
          </pre>
        </div>
      </div>
    </div>
  );
}
