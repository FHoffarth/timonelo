import { describe, expect, it } from "vitest";

import {
  getPassengerFact,
  isPassengerEntityAdmitted,
  type PassengerFactKey,
} from "./passengerAdmission";
import { TimoneloSpatialApiClient } from "./apiClient";

const admittedAxes = {
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
    expect(isPassengerEntityAdmitted(entity || {})).toBe(false);

    const exported = client.exportStandardsPayload(entity!);
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

    expect(isPassengerEntityAdmitted(legacy)).toBe(false);
    expect(getPassengerFact(legacy, "source_envelope", "polygon")).toBeNull();
  });

  it("keeps UNKNOWN and blocked inputs unavailable", () => {
    const unknown = {
      ...admittedAxes,
      evidence_condition: "UNKNOWN" as const,
      publish_status: "PUBLISH_BLOCKED" as const,
    };

    expect(isPassengerEntityAdmitted(unknown)).toBe(false);
    expect(getPassengerFact(unknown, "deck", 14)).toBeNull();
  });

  it("fails closed when method or derivation is absent", () => {
    const { method: _method, ...withoutMethod } = admittedAxes;
    const { derivation: _derivation, ...withoutDerivation } = admittedAxes;

    expect(isPassengerEntityAdmitted(withoutMethod)).toBe(false);
    expect(isPassengerEntityAdmitted(withoutDerivation)).toBe(false);
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

    expect(getPassengerFact(schematic, "source_envelope", "drawn box")).toBeNull();
    expect(getPassengerFact(schematic, "adjacent_fore", "14120")).toBeNull();
    expect(getPassengerFact(schematic, "connected_vertical_core", "Lift A")).toBeNull();
  });

  it("passes an explicitly admitted fact without strengthening other facts", () => {
    expect(isPassengerEntityAdmitted(admittedAxes)).toBe(true);
    expect(getPassengerFact(admittedAxes, "deck", 14)).toBe(14);
    expect(getPassengerFact(admittedAxes, "source_envelope", "polygon")).toBe("polygon");
    expect(getPassengerFact(admittedAxes, "adjacent_fore", "14120")).toBeNull();
    expect(getPassengerFact(admittedAxes, "walking_time", 2)).toBeNull();
  });

  it("rejects generated inputs and never admits synthetic geometry as a spatial fact", () => {
    expect(
      isPassengerEntityAdmitted({
        ...admittedAxes,
        derivation: "GENERATED",
      }),
    ).toBe(false);
    const synthetic = {
      ...admittedAxes,
      geometry_provenance: "SYNTHETIC_GEOMETRY" as const,
    };
    expect(isPassengerEntityAdmitted(synthetic)).toBe(true);
    expect(getPassengerFact(synthetic, "identity", "14122")).toBe("14122");
    expect(getPassengerFact(synthetic, "source_envelope", "polygon")).toBeNull();
  });
});
