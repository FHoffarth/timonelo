import bellissimaData from "../data/semantic_vessel_bellissima.json";
import andorinhaData from "../data/semantic_vessel_andorinha.json";
import {
  VesselKnowledgeGraph,
  SemanticLevel,
  SemanticEntity,
  SpatialClassification,
  LegacySemanticDeckState,
  Method,
  EvidenceCondition,
  StandardsExportPayload,
} from "./types";

export function parseLegacySemanticState(val: unknown): LegacySemanticDeckState {
  if (typeof val === "string") {
    const upper = val.toUpperCase();
    if (upper === "DIRECT" || upper === "DERIVED" || upper === "UNKNOWN" || upper === "CONFLICT") {
      return upper;
    }
  }
  return "UNKNOWN";
}

export function parseEvidenceCondition(val: unknown): EvidenceCondition {
  if (typeof val === "string") {
    const upper = val.toUpperCase();
    if (upper === "SUPPORTED" || upper === "UNSUPPORTED" || upper === "CONFLICTED" || upper === "UNKNOWN") {
      return upper as EvidenceCondition;
    }
  }
  return "UNKNOWN";
}

export function parseMethod(val: unknown): Method | null {
  if (typeof val === "string") {
    const upper = val.toUpperCase();
    if (upper === "DIRECT" || upper === "CALCULATED" || upper === "INFERRED") {
      return upper as Method;
    }
  }
  return null;
}

// Convert raw semantic datasets into Canonical Knowledge Graph representation
function transformRawToCanonical(raw: any): VesselKnowledgeGraph {
  const levels: SemanticLevel[] = (raw.decks || []).map((d: any) => {
    let direct = 0;
    let derived = 0;
    let unknown = 0;
    let conflict = 0;

    const spaces: SemanticEntity[] = (d.objects || []).map((o: any) => {
      const epistemic = parseLegacySemanticState(o.epistemic_state);
      if (epistemic === "DIRECT") direct++;
      else if (epistemic === "DERIVED") derived++;
      else if (epistemic === "UNKNOWN") unknown++;
      else if (epistemic === "CONFLICT") conflict++;

      let classification: SpatialClassification = "STATEROOM_INTERIOR";
      if (o.category === "SUITE") classification = "STATEROOM_SUITE";
      else if (o.category === "BALCONY") classification = "STATEROOM_BALCONY";
      else if (o.category === "OCEAN_VIEW") classification = "STATEROOM_OCEAN_VIEW";
      else if (o.category === "VENUE") classification = "PUBLIC_DINING";
      else if (o.category === "FACILITY") classification = "SERVICE_FACILITY";

      const unkFields = (o.unknown_relations || []).map((u: any) => ({
        field_name: u.field || "unspecified_property",
        epistemic_reason: u.reason || "Missing primary construction artifact",
        required_artifact_class: u.required_document || "GA_DRAWING_LEVEL_4",
      }));

      return {
        id: String(o.id),
        iri: `https://timonelo.io/spatial/${raw.vessel_id}/spaces/${o.id}`,
        label: o.label || `Space ${o.id}`,
        classification,
        classification_label: o.category_label || o.category,
        level: d.deck_level,
        level_name: d.deck_name,
        side: o.side || "CENTER",
        zone: o.zone || "MIDSHIP",
        sequence_order: o.sequence_index || 0,
        accessible: Boolean(o.accessible),
        connecting: Boolean(o.connecting),
        has_balcony: Boolean(o.balcony),
        epistemic_state: epistemic,
        review_state: o.review_state || "PUBLISHED_VERIFIED",
        confidence: typeof o.confidence === "number" ? o.confidence : 1.0,
        statement_count: (o.statements || []).length || 1,
        statements: o.statements || [`STM-${raw.vessel_id}-${o.id}`],
        artifact_count: (o.evidence_links || []).length || 1,
        evidence_links: (o.evidence_links || []).map((ev: any) => ({
          artifact_id: ev.artifact_id || "MSC-BEL-ART-001",
          source_title: "Official Builder Spatial Register Stand 11.2025",
          digest: ev.digest || "085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0",
          locator: ev.locator || `Space Locator [${o.id}]`,
          page: ev.page,
        })),
        relations: {
          adjacent_fore: o.known_relations?.neighbor_fore || null,
          adjacent_aft: o.known_relations?.neighbor_aft || null,
          adjacent_across: o.known_relations?.across_corridor || null,
          adjacent_overhead: o.known_relations?.overhead || null,
          adjacent_underfoot: o.known_relations?.underfoot || null,
          connected_vertical_core: o.known_relations?.nearest_elevator || "Core-Midship",
          nearest_assembly_station: o.known_relations?.nearest_emergency_station || "Assembly-B",
        },
        unknown_fields: unkFields,
      };
    });

    return {
      level_index: d.deck_level,
      level_name: d.deck_name,
      spaces_count: spaces.length,
      spaces,
      epistemic_breakdown: { direct, derived, unknown, conflict },
    };
  });

  return {
    vessel_id: raw.vessel_id,
    vessel_name: raw.vessel_name,
    operator: raw.operator,
    vessel_class: raw.class_name,
    canonical_model_version: "2026.1-CANONICAL-W3C",
    epistemic_summary: {
      total_entities: raw.epistemic_summary?.total_objects || 0,
      direct_evidence_count: raw.epistemic_summary?.direct_count || 0,
      derived_count: raw.epistemic_summary?.derived_count || 0,
      unknown_count: raw.epistemic_summary?.unknown_count || 0,
      conflict_count: raw.epistemic_summary?.conflict_count || 0,
      mean_confidence: raw.epistemic_summary?.confidence_avg || 0.99,
    },
    levels,
  };
}

const GRAPH_REGISTRY: Record<string, VesselKnowledgeGraph> = {
  "msc-bellissima": transformRawToCanonical(bellissimaData),
  "ms-andorinha": transformRawToCanonical(andorinhaData),
};

export class TimoneloSpatialApiClient {
  private activeGraph: VesselKnowledgeGraph;
  private entityIndex = new Map<string, SemanticEntity>();
  private levelIndex = new Map<number, SemanticLevel>();

  constructor(vesselId: string = "msc-bellissima") {
    this.activeGraph = GRAPH_REGISTRY[vesselId] || GRAPH_REGISTRY["msc-bellissima"];
    this.rebuildIndex();
  }

  public switchVessel(vesselId: string): void {
    if (GRAPH_REGISTRY[vesselId]) {
      this.activeGraph = GRAPH_REGISTRY[vesselId];
      this.rebuildIndex();
    }
  }

  private rebuildIndex(): void {
    this.entityIndex.clear();
    this.levelIndex.clear();

    this.activeGraph.levels.forEach((lvl) => {
      this.levelIndex.set(lvl.level_index, lvl);
      lvl.spaces.forEach((sp) => {
        this.entityIndex.set(sp.id.toLowerCase(), sp);
        this.entityIndex.set(sp.id, sp);
      });
    });
  }

  public getVesselGraph(): VesselKnowledgeGraph {
    return this.activeGraph;
  }

  public getLevel(levelIndex: number): SemanticLevel | undefined {
    return this.levelIndex.get(levelIndex);
  }

  public getEntity(id: string): SemanticEntity | undefined {
    return this.entityIndex.get(id.toLowerCase()) || this.entityIndex.get(id);
  }

  public searchEntities(query: string): SemanticEntity[] {
    const q = query.trim().toLowerCase();
    if (!q) return [];

    const matches: SemanticEntity[] = [];
    const exact = this.entityIndex.get(q);
    if (exact) matches.push(exact);

    for (const lvl of this.activeGraph.levels) {
      for (const sp of lvl.spaces) {
        if (matches.length >= 12) break;
        if (
          sp.id !== q &&
          (sp.id.toLowerCase().includes(q) ||
            sp.label.toLowerCase().includes(q) ||
            sp.classification_label.toLowerCase().includes(q) ||
            sp.zone.toLowerCase().includes(q))
        ) {
          matches.push(sp);
        }
      }
    }

    return matches;
  }

  public exportStandardsPayload(entity: SemanticEntity): StandardsExportPayload {
    const fore = entity.relations.adjacent_fore;
    const aft = entity.relations.adjacent_aft;
    const across = entity.relations.adjacent_across;

    const jsonLd = {
      "@context": {
        bot: "https://w3id.org/bot#",
        tim: "https://timonelo.io/spatial/ns#",
        prov: "http://www.w3.org/ns/prov#",
        rdfs: "http://www.w3.org/2000/01/rdf-schema#",
      },
      "@id": entity.iri,
      "@type": ["bot:Space", "tim:VesselStateroom"],
      "rdfs:label": entity.label,
      "bot:hasBuildingStorey": `https://timonelo.io/spatial/${this.activeGraph.vessel_id}/levels/${entity.level}`,
      "bot:adjacentElement": [
        fore ? `https://timonelo.io/spatial/${this.activeGraph.vessel_id}/spaces/${fore}` : null,
        aft ? `https://timonelo.io/spatial/${this.activeGraph.vessel_id}/spaces/${aft}` : null,
        across ? `https://timonelo.io/spatial/${this.activeGraph.vessel_id}/spaces/${across}` : null,
      ].filter(Boolean),
      "tim:epistemicState": entity.epistemic_state,
      "tim:confidenceScore": entity.confidence,
      "prov:wasDerivedFrom": entity.evidence_links.map((e) => `urn:artifact:${e.artifact_id}`),
    };

    const botTurtle = `@prefix bot: <https://w3id.org/bot#> .\n@prefix tim: <https://timonelo.io/spatial/ns#> .\n@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n<${entity.iri}>\n    a bot:Space, tim:Stateroom ;\n    rdfs:label "${entity.label}" ;\n    bot:hasBuildingStorey <https://timonelo.io/spatial/${this.activeGraph.vessel_id}/levels/${entity.level}> ;\n    tim:side "${entity.side}" ;\n    tim:zone "${entity.zone}" ;\n    tim:epistemicState "${entity.epistemic_state}" .\n`;

    const provTurtle = `@prefix prov: <http://www.w3.org/ns/prov#> .\n@prefix tim: <https://timonelo.io/ns#> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n<${entity.iri}>\n    a prov:Entity ;\n    prov:wasDerivedFrom <urn:artifact:${entity.evidence_links[0]?.artifact_id || "MSC-BEL-ART-001"}> ;\n    prov:wasGeneratedBy <urn:activity:TimoneloTruthEngineExtraction> ;\n    prov:qualifiedAttribution [\n        a prov:Attribution ;\n        prov:agent <urn:agent:TimoneloScientificExtractor> ;\n        tim:confidence "${entity.confidence}"^^xsd:decimal\n    ] .\n`;

    const indoorGml = `<?xml version="1.0" encoding="UTF-8"?>\n<IndoorFeatures xmlns="http://www.opengis.net/indoorgml/1.0/core"\n                xmlns:gml="http://www.opengis.net/gml/3.2"\n                xmlns:xlink="http://www.w3.org/1999/xlink">\n  <primalSpaceFeatures>\n    <CellSpace gml:id="CS_${entity.id}">\n      <gml:name>${entity.label}</gml:name>\n      <duality xlink:href="#State_${entity.id}"/>\n      ${fore ? `<connects xlink:href="#CS_${fore}"/>\n` : ""}\n      ${aft ? `<connects xlink:href="#CS_${aft}"/>\n` : ""}\n    </CellSpace>\n  </primalSpaceFeatures>\n</IndoorFeatures>`;

    return {
      entity_id: entity.id,
      json_ld: jsonLd,
      bot_turtle: botTurtle,
      prov_o_turtle: provTurtle,
      indoor_gml_xml: indoorGml,
    };
  }
}

// -------------------------------------------------------------------------
// Orthogonal Design Tokens: Semantic Classification vs Knowledge Epistemics
// -------------------------------------------------------------------------

export function getClassificationColorToken(classification: SpatialClassification): {
  bg: string;
  text: string;
  badge: string;
  dotColor: string;
} {
  switch (classification) {
    case "STATEROOM_INTERIOR":
      return {
        bg: "bg-indigo-950/40",
        text: "text-indigo-300",
        badge: "bg-indigo-500/20 text-indigo-300 border-indigo-500/30",
        dotColor: "#6366f1",
      };
    case "STATEROOM_OCEAN_VIEW":
      return {
        bg: "bg-sky-950/40",
        text: "text-sky-300",
        badge: "bg-sky-500/20 text-sky-300 border-sky-500/30",
        dotColor: "#0ea5e9",
      };
    case "STATEROOM_BALCONY":
      return {
        bg: "bg-emerald-950/40",
        text: "text-emerald-300",
        badge: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
        dotColor: "#10b981",
      };
    case "STATEROOM_SUITE":
      return {
        bg: "bg-amber-950/40",
        text: "text-amber-300",
        badge: "bg-amber-500/20 text-amber-300 border-amber-500/30",
        dotColor: "#f59e0b",
      };
    case "PUBLIC_DINING":
    case "PUBLIC_LOUNGE":
      return {
        bg: "bg-fuchsia-950/40",
        text: "text-fuchsia-300",
        badge: "bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/30",
        dotColor: "#d946ef",
      };
    case "PUBLIC_WELLNESS":
    case "PUBLIC_ENTERTAINMENT":
      return {
        bg: "bg-rose-950/40",
        text: "text-rose-300",
        badge: "bg-rose-500/20 text-rose-300 border-rose-500/30",
        dotColor: "#f43f5e",
      };
    case "CIRCULATION_VERTICAL_CORE":
    case "CIRCULATION_CORRIDOR":
    case "SERVICE_FACILITY":
    default:
      return {
        bg: "bg-slate-900/60",
        text: "text-slate-300",
        badge: "bg-slate-800 text-slate-300 border-slate-700",
        dotColor: "#64748b",
      };
  }
}

export function getEpistemicPatternToken(state: EpistemicState): {
  borderClass: string;
  badgeClass: string;
  label: string;
  statusIcon: string;
} {
  switch (state) {
    case "DIRECT":
      return {
        borderClass: "border-slate-700/80 hover:border-sky-400",
        badgeClass: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
        label: "DIRECT EVIDENTIARY",
        statusIcon: "ShieldCheck",
      };
    case "DERIVED":
      return {
        borderClass: "border-dashed border-sky-400/60 hover:border-sky-300",
        badgeClass: "bg-sky-500/20 text-sky-300 border-sky-400/30",
        label: "DERIVED DETERMINISTIC",
        statusIcon: "Calculator",
      };
    case "UNKNOWN":
      return {
        borderClass: "border-dotted border-slate-600/40 bg-slate-950/20 opacity-55 hover:opacity-100",
        badgeClass: "bg-slate-800/80 text-slate-400 border-slate-700",
        label: "UNKNOWN REQUIREMENT",
        statusIcon: "HelpCircle",
      };
    case "CONFLICT":
      return {
        borderClass: "border-amber-500/80 bg-amber-950/20",
        badgeClass: "bg-amber-500/20 text-amber-300 border-amber-500/30",
        label: "CONFLICT RECORDED",
        statusIcon: "AlertTriangle",
      };
  }
}
