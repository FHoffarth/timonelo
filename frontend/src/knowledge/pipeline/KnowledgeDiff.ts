/**
 * knowledge/pipeline/KnowledgeDiff.ts
 * 
 * Compares incoming parsed artifact entities against existing canonical knowledge.
 * Generates an immutable, structured diff report.
 */

export interface FieldDiff {
  entity_id: string;
  field_name: string;
  old_value: any;
  new_value: any;
  old_provenance?: string;
  new_provenance: string;
  old_confidence?: number;
  new_confidence: number;
  evidence_page: number;
}

export interface KnowledgeDiffReport {
  diff_id: string;
  target_vessel_id: string;
  source_artifact_id: string;
  timestamp: string;
  added_entities: { id: string; label: string; type: string }[];
  removed_entities: { id: string; label: string; type: string }[];
  changed_values: FieldDiff[];
  changed_provenance: FieldDiff[];
  changed_confidence: FieldDiff[];
  total_changes_count: number;
}

export class KnowledgeDiffEngine {
  public static calculateDiff(
    targetVesselId: string,
    sourceArtifactId: string,
    existingKnowledge: Record<string, any>,
    incomingKnowledge: Record<string, any>,
    evidencePage: number = 1
  ): KnowledgeDiffReport {
    const addedEntities: { id: string; label: string; type: string }[] = [];
    const removedEntities: { id: string; label: string; type: string }[] = [];
    const changedValues: FieldDiff[] = [];
    const changedProvenance: FieldDiff[] = [];
    const changedConfidence: FieldDiff[] = [];

    const existingKeys = new Set(Object.keys(existingKnowledge));
    const incomingKeys = new Set(Object.keys(incomingKnowledge));

    // Detect Added Entities
    for (const key of incomingKeys) {
      if (!existingKeys.has(key)) {
        addedEntities.push({
          id: key,
          label: incomingKnowledge[key].name || incomingKnowledge[key].label || key,
          type: incomingKnowledge[key].type || "ENTITY",
        });
      }
    }

    // Detect Removed Entities
    for (const key of existingKeys) {
      if (!incomingKeys.has(key)) {
        removedEntities.push({
          id: key,
          label: existingKnowledge[key].name || existingKnowledge[key].label || key,
          type: existingKnowledge[key].type || "ENTITY",
        });
      }
    }

    // Compare Mutual Entities for Field Diffs
    for (const key of existingKeys) {
      if (incomingKeys.has(key)) {
        const oldEnt = existingKnowledge[key];
        const newEnt = incomingKnowledge[key];

        if (typeof oldEnt === "object" && typeof newEnt === "object" && oldEnt !== null && newEnt !== null) {
          for (const field of Object.keys(newEnt)) {
            const oldVal = oldEnt[field];
            const newVal = newEnt[field];

            if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
              const diffItem: FieldDiff = {
                entity_id: key,
                field_name: field,
                old_value: oldVal,
                new_value: newVal,
                old_provenance: oldEnt.provenance || "Legacy Dataset",
                new_provenance: sourceArtifactId,
                old_confidence: oldEnt.confidence || 0.85,
                new_confidence: newEnt.confidence || 0.98,
                evidence_page: evidencePage,
              };

              if (field === "provenance" || field === "verified_by") {
                changedProvenance.push(diffItem);
              } else if (field === "confidence") {
                changedConfidence.push(diffItem);
              } else {
                changedValues.push(diffItem);
              }
            }
          }
        }
      }
    }

    const totalChanges =
      addedEntities.length +
      removedEntities.length +
      changedValues.length +
      changedProvenance.length +
      changedConfidence.length;

    return {
      diff_id: `DIFF-${targetVesselId.toUpperCase()}-${Date.now()}`,
      target_vessel_id: targetVesselId,
      source_artifact_id: sourceArtifactId,
      timestamp: new Date().toISOString(),
      added_entities: addedEntities,
      removed_entities: removedEntities,
      changed_values: changedValues,
      changed_provenance: changedProvenance,
      changed_confidence: changedConfidence,
      total_changes_count: totalChanges,
    };
  }
}
