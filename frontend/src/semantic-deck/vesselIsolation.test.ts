import { existsSync, readFileSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { KnowledgeFactory } from "../knowledge/pipeline/KnowledgeFactory";
import {
  KnowledgePublisher,
  LegacyPublisherQuarantinedError,
} from "../knowledge/pipeline/KnowledgePublisher";
import { ArtifactQueueManager } from "../knowledge/pipeline/ArtifactQueue";
import { TimoneloSpatialApiClient } from "./apiClient";
import { getPassengerFact, LEGACY_SCHEMATIC_ADMISSION } from "./passengerAdmission";
import { SemanticDeckEngine } from "./semanticEngine";
import {
  UnknownVesselError,
  VesselOwnershipError,
  assertVesselOwnership,
  vesselScopedEntityKey,
} from "./vesselIdentity";
import { hasAdmittedSpatialOverview } from "../components/pages/ShipOverviewPage";

describe("vessel isolation and legacy output quarantine", () => {
  it("fails closed for missing and unknown vessel identities", () => {
    expect(() => new TimoneloSpatialApiClient("")).toThrow(UnknownVesselError);
    expect(() => new TimoneloSpatialApiClient("msc-meraviglia")).toThrow(
      UnknownVesselError,
    );
    expect(() => new SemanticDeckEngine("msc-world-europa")).toThrow(
      UnknownVesselError,
    );
  });

  it("qualifies identical cabin IDs by vessel and refuses cross-vessel lookup", () => {
    expect(vesselScopedEntityKey("msc-bellissima", "14122")).not.toBe(
      vesselScopedEntityKey("msc-meraviglia", "14122"),
    );
    expect(vesselScopedEntityKey("", "14122")).toBeNull();
    expect(vesselScopedEntityKey(undefined, "14122")).toBeNull();

    const bellissima = new TimoneloSpatialApiClient("msc-bellissima");
    expect(bellissima.getEntityForVessel("msc-bellissima", "14122")).toBeDefined();
    expect(bellissima.getEntityForVessel("msc-meraviglia", "14122")).toBeUndefined();
    expect(bellissima.getEntityForVessel("", "14122")).toBeUndefined();
  });

  it("does not change vessel after a refused switch", () => {
    const client = new TimoneloSpatialApiClient("msc-bellissima");
    expect(() => client.switchVessel("msc-meraviglia")).toThrow(UnknownVesselError);
    expect(client.getVesselGraph().vessel_id).toBe("msc-bellissima");
  });

  it("clears stale vessel-scoped UI state before changing vessel identity", () => {
    const app = readFileSync(resolve(__dirname, "./SemanticLivingDeckApp.tsx"), "utf-8");
    const handler = app.match(
      /const handleSelectVessel = \(vesselId: string\) => \{([\s\S]*?)\n  \};/,
    )?.[1] ?? "";

    expect(handler.indexOf("setInspectingStandardsEntity(null)")).toBeGreaterThan(-1);
    expect(handler.indexOf("setInspectingStandardsEntity(null)")).toBeLessThan(
      handler.indexOf("setSelectedVesselId(vesselId)"),
    );
  });

  it("does not substitute Bellissima spatial state for another ship profile", () => {
    const profile = readFileSync(
      resolve(__dirname, "../components/pages/ShipProfilePage.tsx"),
      "utf-8",
    );

    expect(profile).toContain('shipSlug === "msc-bellissima"');
    expect(profile).toContain("new TimoneloSpatialApiClient(shipSlug)");
    expect(profile).not.toContain('new TimoneloSpatialApiClient("msc-bellissima")');
    expect(profile).toContain("requestedVesselId={shipSlug}");
  });

  it("requires entity, provenance, graph, and requested vessel ownership to match", () => {
    expect(() =>
      assertVesselOwnership(
        "msc-bellissima",
        "msc-bellissima",
        "msc-bellissima",
        "msc-bellissima",
      ),
    ).not.toThrow();
    expect(() =>
      assertVesselOwnership(
        "msc-bellissima",
        "msc-bellissima",
        "msc-meraviglia",
        "msc-meraviglia",
      ),
    ).toThrow(VesselOwnershipError);
    expect(() =>
      assertVesselOwnership(
        "msc-meraviglia",
        "msc-meraviglia",
        "msc-bellissima",
        "msc-bellissima",
      ),
    ).toThrow(VesselOwnershipError);
    expect(() =>
      assertVesselOwnership(null, null, "msc-bellissima", "msc-bellissima"),
    ).toThrow(VesselOwnershipError);
  });

  it("refuses stale foreign entities at the standards export boundary", () => {
    const bellissima = new TimoneloSpatialApiClient("msc-bellissima");
    const andorinha = new TimoneloSpatialApiClient("ms-andorinha");
    const bellissimaEntity = bellissima.getEntity("14122");
    expect(bellissimaEntity).toBeDefined();

    expect(() =>
      bellissima.exportStandardsPayload(bellissimaEntity!, "msc-bellissima"),
    ).not.toThrow();
    expect(() =>
      bellissima.exportStandardsPayload(bellissimaEntity!, "msc-meraviglia"),
    ).toThrow(VesselOwnershipError);
    expect(() =>
      andorinha.exportStandardsPayload(bellissimaEntity!, "ms-andorinha"),
    ).toThrow(
      VesselOwnershipError,
    );
    expect(() =>
      bellissima.exportStandardsPayload({
        ...bellissimaEntity!,
        vessel_id: null,
        provenance_vessel_id: null,
      }, "msc-bellissima"),
    ).toThrow(VesselOwnershipError);
  });

  it("does not render Bellissima's overview for another vessel", () => {
    expect(hasAdmittedSpatialOverview("msc-bellissima")).toBe(true);
    expect(hasAdmittedSpatialOverview("msc-meraviglia")).toBe(false);
    expect(hasAdmittedSpatialOverview(undefined)).toBe(false);
  });

  it("refuses every legacy publisher entry point", () => {
    expect(() => KnowledgePublisher.validateAndPublish("msc-meraviglia")).toThrow(
      LegacyPublisherQuarantinedError,
    );
    const before = ArtifactQueueManager.getQueue().find((item) => item.queue_id === "Q-ART-002")?.stage;
    const result = KnowledgeFactory.executeIngestionPipeline("Q-ART-002");
    const after = ArtifactQueueManager.getQueue().find((item) => item.queue_id === "Q-ART-002")?.stage;
    expect(result.success).toBe(false);
    expect(result.release).toBeUndefined();
    expect(result.message).toMatch(/quarantined/i);
    expect(after).toBe(before);
  });

  it("rejects all committed unproven Meraviglia geometry at passenger admission", () => {
    const geometryDir = resolve(__dirname, "../../../geometry");
    const files = readdirSync(geometryDir).filter(
      (name) => name.startsWith("meraviglia_deck") && name.endsWith(".geometry.json"),
    );
    const documents = files.map((name) =>
      JSON.parse(readFileSync(resolve(geometryDir, name), "utf-8")),
    );
    const objects = documents.flatMap((document) => document.objects || []);

    expect(files).toHaveLength(15);
    expect(objects).toHaveLength(2180);
    expect(objects.every((object) => object.geometry_provenance == null)).toBe(true);
    expect(
      getPassengerFact(
        {
          ...LEGACY_SCHEMATIC_ADMISSION,
          admitted_fact_keys: ["source_envelope"],
        },
        "source_envelope",
        objects[0].polygon,
        "msc-meraviglia",
      ),
    ).toBeNull();
  });

  it("keeps the legacy Meraviglia runtime asset outside the public build input", () => {
    expect(existsSync(resolve(__dirname, "../../public/data/msc-meraviglia.json"))).toBe(false);
    expect(
      existsSync(resolve(__dirname, "../../../data/hypotheses/legacy-runtime/msc-meraviglia.json")),
    ).toBe(true);
  });

  it("keeps the legacy Grandiosa runtime asset outside the public build input", () => {
    expect(existsSync(resolve(__dirname, "../../public/data/msc-grandiosa.json"))).toBe(false);
    expect(
      existsSync(resolve(__dirname, "../../../data/hypotheses/legacy-runtime/msc-grandiosa.json")),
    ).toBe(true);
  });
});
