/**
 * knowledge/pipeline/ArtifactQueue.ts
 * 
 * Pipeline Stage 1: TimEvidence -> TimArtifact -> Artifact Queue.
 * Ingests raw evidence documents, validates metadata, and tracks parsing lifecycle.
 */

export interface TimEvidence {
  evidence_id: string;
  filename: string;
  source_title: string;
  publisher: string;
  edition: string;
  target_vessel_id: string;
  artifact_type: "DECK_PLAN_PDF" | "TECHNICAL_SPEC" | "HARBOR_RECORD" | "ACOUSTIC_SURVEY";
  uploaded_at: string;
  file_size_bytes: number;
}

export type QueueStage =
  | "QUEUED"
  | "PARSING"
  | "SCHEMA_VALIDATING"
  | "DIFF_READY"
  | "AWAITING_OFFICER_APPROVAL"
  | "PUBLISHED"
  | "REJECTED";

export interface QueuedArtifact {
  queue_id: string;
  evidence: TimEvidence;
  stage: QueueStage;
  extracted_entities_count: number;
  conflicts_detected_count: number;
  assigned_officer: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export class ArtifactQueueManager {
  private static queue: QueuedArtifact[] = [
    {
      queue_id: "Q-ART-001",
      evidence: {
        evidence_id: "MSC_BELLISSIMA_DECK_PLANS_11.2025_DEU",
        filename: "msc_bellissima_deck_plans_11_2025.pdf",
        source_title: "MSC Bellissima Official Deck Plans (Edition 11.2025 DEU)",
        publisher: "MSC Cruises S.A.",
        edition: "11.2025",
        target_vessel_id: "msc-bellissima",
        artifact_type: "DECK_PLAN_PDF",
        uploaded_at: "2026-08-17T19:57:41Z",
        file_size_bytes: 4280192,
      },
      stage: "PUBLISHED",
      extracted_entities_count: 2257,
      conflicts_detected_count: 9,
      assigned_officer: "Bridge Officer Tim",
      created_at: "2026-08-17T20:00:00Z",
      updated_at: "2026-08-18T18:00:00Z",
    },
    {
      queue_id: "Q-ART-002",
      evidence: {
        evidence_id: "MSC_GRANDIOSA_DECK_PLANS_03.2026_DEU",
        filename: "msc_grandiosa_deck_plans_03_2026.pdf",
        source_title: "MSC Grandiosa Official Deck Plans (Edition 03.2026 DEU)",
        publisher: "MSC Cruises S.A.",
        edition: "03.2026",
        target_vessel_id: "msc-grandiosa",
        artifact_type: "DECK_PLAN_PDF",
        uploaded_at: "2026-08-18T14:30:00Z",
        file_size_bytes: 5120400,
      },
      stage: "AWAITING_OFFICER_APPROVAL",
      extracted_entities_count: 2421,
      conflicts_detected_count: 3,
      assigned_officer: "Bridge Officer Tim",
      created_at: "2026-08-18T14:35:00Z",
      updated_at: "2026-08-18T19:00:00Z",
    },
    {
      queue_id: "Q-ART-003",
      evidence: {
        evidence_id: "MS_ANDORINHA_TECHNICAL_GA_2025",
        filename: "ms_andorinha_general_arrangement.pdf",
        source_title: "MS Andorinha Douro River GA Blueprint",
        publisher: "Scylla AG / Tauck",
        edition: "2025.1",
        target_vessel_id: "ms-andorinha",
        artifact_type: "DECK_PLAN_PDF",
        uploaded_at: "2026-08-18T16:00:00Z",
        file_size_bytes: 2840100,
      },
      stage: "AWAITING_OFFICER_APPROVAL",
      extracted_entities_count: 84,
      conflicts_detected_count: 0,
      assigned_officer: "Bridge Officer Tim",
      created_at: "2026-08-18T16:05:00Z",
      updated_at: "2026-08-18T19:10:00Z",
    },
  ];

  public static getQueue(): QueuedArtifact[] {
    return [...this.queue];
  }

  public static getPendingApprovals(): QueuedArtifact[] {
    return this.queue.filter((q) => q.stage === "AWAITING_OFFICER_APPROVAL");
  }

  public static enqueueArtifact(evidence: TimEvidence): QueuedArtifact {
    const newEntry: QueuedArtifact = {
      queue_id: `Q-ART-${String(this.queue.length + 1).padStart(3, "0")}`,
      evidence,
      stage: "QUEUED",
      extracted_entities_count: 0,
      conflicts_detected_count: 0,
      assigned_officer: "Bridge Officer Tim",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    this.queue.unshift(newEntry);
    return newEntry;
  }

  public static advanceStage(queueId: string, nextStage: QueueStage): QueuedArtifact | null {
    const item = this.queue.find((q) => q.queue_id === queueId);
    if (item) {
      item.stage = nextStage;
      item.updated_at = new Date().toISOString();
      return item;
    }
    return null;
  }
}
