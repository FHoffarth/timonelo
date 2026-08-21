// Targeted P0-D fail-closed tests for cabin resolution.
// Runnable with plain Node (native TS type-stripping): `node cabinResolution.test.mts`.
//
// These prove the resolution decision that gates CabinDeepDivePage:
//   (a) a known cabin resolves true (via canonical OR spatial graph)
//   (b) an unknown 4-5 digit ID resolves false -> component fails closed and
//       never substitutes cabin 14122
//   (c) an unknown ID resolves false -> no synthetic entity is built, so no
//       DIRECT / PUBLISHED_VERIFIED / confidence / adjacency claim is emitted
import assert from "node:assert/strict";
import { isKnownCabin, resolveCabinMeta } from "./cabinResolution.ts";

// --- Fixtures mirroring the real data contract -----------------------------
// Canonical frontend map (shape of CANONICAL_CABINS): only a handful of cabins.
const CANONICAL: Record<string, unknown> = {
  "12142": { id: "12142", shipSlug: "msc-virtuosa" },
  "14122": { id: "14122", shipSlug: "msc-bellissima" },
};

// Spatial graph: has real bellissima spaces (incl. some NOT in canonical), but
// NOT arbitrary unknown 4-5 digit IDs. Mirrors apiClient.getEntity(id).
const GRAPH_IDS = new Set(["14122", "14120", "14124"]);
const lookupEntity = (id: string): unknown =>
  GRAPH_IDS.has(id) ? { id, epistemic_state: "DIRECT" } : undefined;

let failures = 0;
function check(name: string, fn: () => void): void {
  try {
    fn();
    console.log(`  ok - ${name}`);
  } catch (e) {
    failures++;
    console.error(`  FAIL - ${name}: ${(e as Error).message}`);
  }
}

console.log("P0-D cabin resolution (fail-closed):");

// (a) Known cabin keeps working -- canonical-backed and graph-backed.
check("known canonical cabin 14122 -> true", () => {
  assert.equal(isKnownCabin("14122", CANONICAL, lookupEntity), true);
});
check("known cabin 12142 (canonical only) -> true", () => {
  assert.equal(isKnownCabin("12142", CANONICAL, lookupEntity), true);
});
check("known cabin 14120 (spatial graph only) -> true", () => {
  assert.equal(isKnownCabin("14120", CANONICAL, lookupEntity), true);
});

// (b) Unknown 4-5 digit ID does NOT resolve -> component must not reuse 14122.
check("unknown 5-digit 49999 -> false (no 14122 substitution)", () => {
  assert.equal(isKnownCabin("49999", CANONICAL, lookupEntity), false);
});
check("unknown 4-digit 3011 -> false", () => {
  assert.equal(isKnownCabin("3011", CANONICAL, lookupEntity), false);
});

// (c) Because unknown resolves false, the synthetic DIRECT/PUBLISHED_VERIFIED
// entity path is never entered. Assert the invariant at the decision boundary:
// no canonical hit AND no graph hit for the unknown ID.
check("unknown ID has neither canonical nor graph backing", () => {
  const id = "49999";
  assert.equal(CANONICAL[id] == null, true, "must not be in canonical");
  assert.equal(lookupEntity(id) == null, true, "must not be in spatial graph");
  assert.equal(isKnownCabin(id, CANONICAL, lookupEntity), false);
});

// Guard: empty / missing IDs fail closed too.
check("empty id -> false", () => {
  assert.equal(isKnownCabin("", CANONICAL, lookupEntity), false);
  assert.equal(isKnownCabin(undefined, CANONICAL, lookupEntity), false);
});

// --- P0-D follow-up: metadata resolution (no 14122 leakage) ----------------
// A representative canonical record (14122) and a graph-only entity (18001).
const CANONICAL_14122 = {
  id: "14122",
  shipSlug: "msc-bellissima",
  deckNumber: 14,
  deckName: "Waterfront",
  category: "Deluxe Interior (IR2)",
  tier: "Fantastica Tier",
  side: "STARBOARD",
  sqmInterior: 16,
  sqmBalcony: 0,
  bedConfig: "Twin convertible to double",
  heroImageUrl: "https://example/14122.jpg",
  evidenceArtifactId: "MSC-BEL-14122-ART",
};
const CANON_META: Record<string, unknown> = { "14122": CANONICAL_14122 };
const GRAPH_18001 = {
  level: 18,
  level_name: "Pyramids / Divina",
  classification_label: "Yacht Club Suite (YC1)",
  side: "PORT",
  zone: "FORWARD",
  accessible: false,
  evidence_links: [{ artifact_id: "MSC-BEL-18001-ART" }],
};

console.log("\nP0-D metadata resolution (no 14122 leakage):");

check("canonical-known cabin returns its own record verbatim (unchanged)", () => {
  const meta = resolveCabinMeta("14122", CANONICAL_14122, undefined);
  assert.equal(meta, CANONICAL_14122); // same reference -> behavior unchanged
});

check("graph-only cabin uses ONLY its own available data", () => {
  const meta: any = resolveCabinMeta("18001", undefined, GRAPH_18001);
  assert.equal(meta.id, "18001");
  assert.equal(meta.deckNumber, 18);
  assert.equal(meta.deckName, "Pyramids / Divina");
  assert.equal(meta.category, "Yacht Club Suite (YC1)");
  assert.equal(meta.side, "PORT");
  assert.equal(meta.isPRM, false);
  assert.equal(meta.evidenceArtifactId, "MSC-BEL-18001-ART");
});

check("graph-only missing metadata stays null (renders Unavailable)", () => {
  const meta: any = resolveCabinMeta("18001", undefined, GRAPH_18001);
  assert.equal(meta.tier, null);
  assert.equal(meta.sqmInterior, null);
  assert.equal(meta.sqmBalcony, null);
  assert.equal(meta.bedConfig, null);
  assert.equal(meta.heroImageUrl, null);
});

check("NO 14122 metadata leaks into a graph-only cabin", () => {
  const meta: any = resolveCabinMeta("18001", undefined, GRAPH_18001);
  // None of 14122's distinctive values may appear on a different cabin.
  assert.notEqual(meta.deckNumber, CANONICAL_14122.deckNumber);
  assert.notEqual(meta.deckName, CANONICAL_14122.deckName);
  assert.notEqual(meta.category, CANONICAL_14122.category);
  assert.notEqual(meta.heroImageUrl, CANONICAL_14122.heroImageUrl);
  assert.notEqual(meta.evidenceArtifactId, CANONICAL_14122.evidenceArtifactId);
  const values = Object.values(meta);
  assert.equal(values.includes(CANONICAL_14122.heroImageUrl), false);
  assert.equal(values.includes("Fantastica Tier"), false);
  assert.equal(values.includes(16), false); // 14122 sqmInterior
});

check("neither canonical nor graph -> null (caller fails closed)", () => {
  assert.equal(resolveCabinMeta("49999", undefined, undefined), null);
  assert.equal(resolveCabinMeta("49999", undefined, null), null);
});

if (failures > 0) {
  console.error(`\n${failures} test(s) failed`);
  process.exit(1);
}
console.log("\nAll cabin-resolution tests passed.");
