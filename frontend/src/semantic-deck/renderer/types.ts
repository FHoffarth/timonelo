import { SemanticEntity, SemanticLevel, VesselKnowledgeGraph } from "../types";

export interface ViewportState {
  x: number;
  y: number;
  zoom: number;
}

export type RenderOverlayMode =
  | "none"
  | "epistemic"
  | "acoustic"
  | "safety_muster"
  | "distance_to_lift"
  | "category_classes";

export interface RenderLayersConfig {
  showHull: boolean;
  showGrid: boolean;
  showCabins: boolean;
  showVenues: boolean;
  showLifts: boolean;
  showLabels: boolean;
  showOverlays: boolean;
  showLegend: boolean;
}

export interface DeckRendererProps {
  vesselId: string;
  level: SemanticLevel;
  allLevels: SemanticLevel[];
  vesselGraph?: VesselKnowledgeGraph;
  selectedEntity: SemanticEntity | null;
  hoveredEntity: SemanticEntity | null;
  overlayMode?: RenderOverlayMode;
  layersConfig?: Partial<RenderLayersConfig>;
  onSelectEntity: (entity: SemanticEntity | null) => void;
  onHoverEntity: (entity: SemanticEntity | null) => void;
  onSelectLevel: (levelIndex: number) => void;
  onNavigateAdjacent?: (direction: "fore" | "aft" | "across" | "overhead" | "underfoot") => void;
  className?: string;
}

export interface LayerProps {
  vesselId: string;
  level: SemanticLevel;
  allLevels?: SemanticLevel[];
  selectedEntity: SemanticEntity | null;
  hoveredEntity: SemanticEntity | null;
  overlayMode: RenderOverlayMode;
  onSelectEntity: (entity: SemanticEntity) => void;
  onHoverEntity: (entity: SemanticEntity | null) => void;
  isNight?: boolean;
}
