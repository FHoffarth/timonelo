import React from "react";
import { SemanticLevel, SemanticEntity } from "../types";
import DeckRenderer from "../renderer/DeckRenderer";

interface SpatialGrammarCanvasProps {
  level: SemanticLevel;
  selectedEntity: SemanticEntity | null;
  hoveredEntity: SemanticEntity | null;
  allLevels: SemanticLevel[];
  onSelectLevel: (levelIndex: number) => void;
  onSelectEntity: (entity: SemanticEntity | null) => void;
  onHoverEntity: (entity: SemanticEntity | null) => void;
}

export default function SpatialGrammarCanvas({
  level,
  selectedEntity,
  hoveredEntity,
  allLevels,
  onSelectLevel,
  onSelectEntity,
  onHoverEntity,
}: SpatialGrammarCanvasProps) {
  return (
    <div className="flex-1 w-full h-full relative overflow-hidden flex flex-col">
      <DeckRenderer
        level={level}
        allLevels={allLevels}
        selectedEntity={selectedEntity}
        hoveredEntity={hoveredEntity}
        onSelectEntity={onSelectEntity}
        onHoverEntity={onHoverEntity}
        onSelectLevel={onSelectLevel}
        className="w-full h-full"
      />
    </div>
  );
}
