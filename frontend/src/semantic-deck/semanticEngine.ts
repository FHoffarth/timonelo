import bellissimaData from "../data/semantic_vessel_bellissima.json";
import andorinhaData from "../data/semantic_vessel_andorinha.json";
import {
  VesselSemanticModel,
  SemanticDeck,
  SemanticObject,
  SemanticCategory,
  EpistemicState,
} from "./types";

export const REGISTERED_VESSELS: Record<string, VesselSemanticModel> = {
  "msc-bellissima": bellissimaData as unknown as VesselSemanticModel,
  "ms-andorinha": andorinhaData as unknown as VesselSemanticModel,
};

export class SemanticDeckEngine {
  private currentVessel: VesselSemanticModel;
  private objectMap = new Map<string, SemanticObject>();
  private deckMap = new Map<number, SemanticDeck>();

  constructor(vesselId: string = "msc-bellissima") {
    this.currentVessel = REGISTERED_VESSELS[vesselId] || REGISTERED_VESSELS["msc-bellissima"];
    this.reindex();
  }

  public setVessel(vesselId: string): void {
    if (REGISTERED_VESSELS[vesselId]) {
      this.currentVessel = REGISTERED_VESSELS[vesselId];
      this.reindex();
    }
  }

  private reindex(): void {
    this.objectMap.clear();
    this.deckMap.clear();

    this.currentVessel.decks.forEach((deck: SemanticDeck) => {
      this.deckMap.set(deck.deck_level, deck);
      deck.objects.forEach((obj: SemanticObject) => {
        this.objectMap.set(obj.id.toLowerCase(), obj);
        this.objectMap.set(obj.id, obj);
      });
    });
  }

  public getVessel(): VesselSemanticModel {
    return this.currentVessel;
  }

  public getDecks(): SemanticDeck[] {
    return this.currentVessel.decks;
  }

  public getDeck(level: number): SemanticDeck | undefined {
    return this.deckMap.get(level);
  }

  public getObject(id: string): SemanticObject | undefined {
    return this.objectMap.get(id.toLowerCase()) || this.objectMap.get(id);
  }

  public search(query: string): SemanticObject[] {
    const q = query.trim().toLowerCase();
    if (!q) return [];

    const results: SemanticObject[] = [];
    const exact = this.objectMap.get(q);
    if (exact) results.push(exact);

    for (const deck of this.currentVessel.decks) {
      for (const obj of deck.objects) {
        if (results.length >= 10) break;
        if (
          obj.id !== q &&
          (obj.id.toLowerCase().includes(q) ||
            obj.label.toLowerCase().includes(q) ||
            obj.category_label.toLowerCase().includes(q) ||
            obj.zone.toLowerCase().includes(q))
        ) {
          results.push(obj);
        }
      }
    }

    return results;
  }
}

// -------------------------------------------------------------------------
// Visual Encoding Tokens: Orthogonal Separation of Content vs Knowledge
// -------------------------------------------------------------------------

export function getCategoryStyle(category: SemanticCategory): {
  bg: string;
  text: string;
  badgeBg: string;
  accent: string;
} {
  switch (category) {
    case "INTERIOR":
      return {
        bg: "bg-indigo-950/40",
        text: "text-indigo-300",
        badgeBg: "bg-indigo-500/20 text-indigo-300 border-indigo-500/30",
        accent: "#6366f1",
      };
    case "OCEAN_VIEW":
      return {
        bg: "bg-sky-950/40",
        text: "text-sky-300",
        badgeBg: "bg-sky-500/20 text-sky-300 border-sky-500/30",
        accent: "#0ea5e9",
      };
    case "BALCONY":
      return {
        bg: "bg-emerald-950/40",
        text: "text-emerald-300",
        badgeBg: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
        accent: "#10b981",
      };
    case "SUITE":
      return {
        bg: "bg-amber-950/40",
        text: "text-amber-300",
        badgeBg: "bg-amber-500/20 text-amber-300 border-amber-500/30",
        accent: "#f59e0b",
      };
    case "VENUE":
      return {
        bg: "bg-fuchsia-950/40",
        text: "text-fuchsia-300",
        badgeBg: "bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/30",
        accent: "#d946ef",
      };
    case "FACILITY":
    default:
      return {
        bg: "bg-slate-900/60",
        text: "text-slate-300",
        badgeBg: "bg-slate-700/40 text-slate-300 border-slate-600/30",
        accent: "#64748b",
      };
  }
}

export function getEpistemicStyle(state: EpistemicState): {
  borderClass: string;
  badgeClass: string;
  label: string;
  iconName: string;
  isTranslucent: boolean;
} {
  switch (state) {
    case "DIRECT":
      return {
        borderClass: "border-slate-700/80 hover:border-sky-400",
        badgeClass: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
        label: "DIRECT EVIDENCE",
        iconName: "ShieldCheck",
        isTranslucent: false,
      };
    case "DERIVED":
      return {
        borderClass: "border-dashed border-sky-400/60 hover:border-sky-300",
        badgeClass: "bg-sky-500/20 text-sky-300 border-sky-400/30",
        label: "DERIVED FORMULA",
        iconName: "Calculator",
        isTranslucent: false,
      };
    case "UNKNOWN":
      return {
        borderClass: "border-dotted border-slate-600/40 bg-slate-950/20 opacity-50 hover:opacity-100",
        badgeClass: "bg-slate-800/80 text-slate-400 border-slate-700",
        label: "UNKNOWN CITATION NEEDED",
        iconName: "HelpCircle",
        isTranslucent: true,
      };
    case "CONFLICT":
      return {
        borderClass: "border-amber-500/80 bg-amber-950/20",
        badgeClass: "bg-amber-500/20 text-amber-300 border-amber-500/30",
        label: "CONFLICT RECORDED",
        iconName: "AlertTriangle",
        isTranslucent: false,
      };
  }
}
