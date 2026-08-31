import { describe, expect, it } from "vitest";

import {
  getPassengerFact,
  isPassengerEntityAdmitted,
  type PassengerFactKey,
} from "./passengerAdmission";
import { TimoneloSpatialApiClient } from "./apiClient";

const admittedAxes = {
  vessel_id: "msc-bellissima",
  provenance_vessel_id: "msc-bellissima",
  data_origin: "CANONICAL_TRUTH_ENGINE" as const,
  evidence_condition: "SUPPORTED" as const,
  human_review_state: "APPROVED" as const,
  publish_status: "PUBLISH_ALLOWED" as const,
  geometry_provenance: "TRANSFORMED_SOURCE_GEOMETRY" as const,
  method: "DIRECT" as const,
  derivation: "LOCAL" as const,
  admitted_fact_keys: ["identity", "deck", "source_envelope"] as PassengerFactKey[],
};

describe("passenger spatial admission boundary", () => {
  it("quarantines the real legacy Cabin 14122 entity at ingress", () => {
    const client = new TimoneloSpatialApiClient("msc-bellissima");
    const entity = client.getEntity("14122");
    expect(entity).toBeDefined();
    expect(entity?.epistemic_state).toBe("DIRECT");
    expect(entity?.data_origin).toBe("LEGACY_SCHEMATIC");
    expect(entity?.admitted_fact_keys).toEqual([]);
    expect(isPassengerEntityAdmitted(entity || {}, "msc-bellissima")).toBe(false);

    const exported = client.exportStandardsPayload(entity!, "msc-bellissima");
    expect(exported.json_ld).not.toHaveProperty("@type");
    expect(exported.json_ld).not.toHaveProperty("bot:hasBuildingStorey");
    expect(exported.json_ld["bot:adjacentElement"]).toEqual([]);
    expect(exported.bot_turtle).toMatch(/topology unavailable/i);
    expect(exported.prov_o_turtle).toMatch(/provenance unavailable/i);
    expect(exported.indoor_gml_xml).toMatch(/IndoorGML unavailable/i);
  });

  it("does not admit legacy geometry merely because it says DIRECT", () => {
    const legacy = {
      ...admittedAxes,
      data_origin: "LEGACY_SCHEMATIC" as const,
      legacy_epistemic_state: "DIRECT",
    };

    expect(isPassengerEntityAdmitted(legacy, "msc-bellissima")).toBe(false);
    expect(getPassengerFact(legacy, "source_envelope", "polygon", "msc-bellissima")).toBeNull();
  });

  it("keeps UNKNOWN and blocked inputs unavailable", () => {
    const unknown = {
      ...admittedAxes,
      evidence_condition: "UNKNOWN" as const,
      publish_status: "PUBLISH_BLOCKED" as const,
    };

    expect(isPassengerEntityAdmitted(unknown, "msc-bellissima")).toBe(false);
    expect(getPassengerFact(unknown, "deck", 14, "msc-bellissima")).toBeNull();
  });

  it("fails closed when method or derivation is absent", () => {
    const { method: _method, ...withoutMethod } = admittedAxes;
    const { derivation: _derivation, ...withoutDerivation } = admittedAxes;

    expect(isPassengerEntityAdmitted(withoutMethod, "msc-bellissima")).toBe(false);
    expect(isPassengerEntityAdmitted(withoutDerivation, "msc-bellissima")).toBe(false);
  });

  it("does not treat schematic layout as geometry or topology admission", () => {
    const schematic = {
      ...admittedAxes,
      data_origin: "LEGACY_SCHEMATIC" as const,
      admitted_fact_keys: [
        "source_envelope",
        "adjacent_fore",
        "connected_vertical_core",
      ] as PassengerFactKey[],
    };

    expect(getPassengerFact(schematic, "source_envelope", "drawn box", "msc-bellissima")).toBeNull();
    expect(getPassengerFact(schematic, "adjacent_fore", "14120", "msc-bellissima")).toBeNull();
    expect(getPassengerFact(schematic, "connected_vertical_core", "Lift A", "msc-bellissima")).toBeNull();
  });

  it("admits only matching vessel ownership without strengthening other facts", () => {
    expect(isPassengerEntityAdmitted(admittedAxes, "msc-bellissima")).toBe(true);
    expect(isPassengerEntityAdmitted(admittedAxes, "msc-meraviglia")).toBe(false);
    expect(getPassengerFact(admittedAxes, "deck", 14, "msc-bellissima")).toBe(14);
    expect(getPassengerFact(admittedAxes, "source_envelope", "polygon", "msc-bellissima")).toBe("polygon");
    expect(getPassengerFact(admittedAxes, "adjacent_fore", "14120", "msc-bellissima")).toBeNull();
    expect(getPassengerFact(admittedAxes, "walking_time", 2, "msc-bellissima")).toBeNull();
  });

  it("fails closed for missing, wrong, and stale vessel ownership", () => {
    const { vessel_id: _vessel, ...withoutVessel } = admittedAxes;
    const { provenance_vessel_id: _provenanceVessel, ...withoutProvenanceVessel } = admittedAxes;
    const staleAndorinhaAdmission = {
      ...admittedAxes,
      vessel_id: "ms-andorinha",
      provenance_vessel_id: "ms-andorinha",
    };

    expect(isPassengerEntityAdmitted(withoutVessel, "msc-bellissima")).toBe(false);
    expect(isPassengerEntityAdmitted(withoutProvenanceVessel, "msc-bellissima")).toBe(false);
    expect(isPassengerEntityAdmitted(staleAndorinhaAdmission, "msc-bellissima")).toBe(false);
    expect(isPassengerEntityAdmitted(staleAndorinhaAdmission, "ms-andorinha")).toBe(true);
  });

  it("does not cross-admit identical local entity ids between vessels", () => {
    const bellissima14122 = admittedAxes;
    const meraviglia14122 = {
      ...admittedAxes,
      vessel_id: "msc-meraviglia",
      provenance_vessel_id: "msc-meraviglia",
    };

    expect(isPassengerEntityAdmitted(bellissima14122, "msc-meraviglia")).toBe(false);
    expect(isPassengerEntityAdmitted(meraviglia14122, "msc-bellissima")).toBe(false);
  });

  it("rejects generated inputs and never admits synthetic geometry as a spatial fact", () => {
    expect(
      isPassengerEntityAdmitted({
        ...admittedAxes,
        derivation: "GENERATED",
      }, "msc-bellissima"),
    ).toBe(false);
    const synthetic = {
      ...admittedAxes,
      geometry_provenance: "SYNTHETIC_GEOMETRY" as const,
    };
    expect(isPassengerEntityAdmitted(synthetic, "msc-bellissima")).toBe(true);
    expect(getPassengerFact(synthetic, "identity", "14122", "msc-bellissima")).toBe("14122");
    expect(getPassengerFact(synthetic, "source_envelope", "polygon", "msc-bellissima")).toBeNull();
  });

  it("never admits sister-ship derivation as passenger knowledge", () => {
    expect(isPassengerEntityAdmitted({
      ...admittedAxes,
      derivation: "SISTER_SHIP",
    }, "msc-bellissima")).toBe(false);
  });
});
