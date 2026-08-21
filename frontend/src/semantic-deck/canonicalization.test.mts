// P0-H1 targeted tests: transformRawToCanonical() must not invent trust or
// provenance values. Runnable with plain Node:
//   node frontend/src/semantic-deck/canonicalization.test.mts
//
// apiClient.ts cannot be imported directly under plain Node (extensionless
// module specifiers + bundler JSON imports), so this test pairs:
//   (A) a source contract over the mapping block — the removed fabrications
//       must not reappear, and the fail-closed operators must be present;
//   (B) real raw-data checks — the values the mapping passes through are
//       genuinely present, and the honest UNKNOWN / zero-confidence entities
//       that must never be forced to VERIFIED / 1.0 do exist.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const src = fs.readFileSync(path.join(here, "apiClient.ts"), "utf8");
// The object literal built per space inside transformRawToCanonical.
const mapStart = src.indexOf("epistemic_state: epistemic");
const mapEnd = src.indexOf("unknown_fields: unkFields");
assert.ok(mapStart > 0 && mapEnd > mapStart, "could not locate mapping block");
const block = src.slice(mapStart, mapEnd);

const raw: any = (
  await import("../data/semantic_vessel_bellissima.json", { with: { type: "json" } })
).default;
const objs: any[] = (raw.decks || []).flatMap((d: any) => d.objects || []);

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

console.log("P0-H1 fail-closed canonicalization:");

// --- (A) no fabricated defaults remain in the mapping ----------------------
check("no hardcoded source title appears", () => {
  assert.equal(src.includes("Official Builder Spatial Register"), false);
  assert.match(block, /source_title:\s*ev\.source_title\s*\?\?\s*null/);
});

check("no artifact_id / digest / locator fallbacks", () => {
  assert.equal(src.includes('"MSC-BEL-ART-001"'), false);
  assert.equal(src.includes("085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0"), false);
  assert.equal(block.includes("Space Locator ["), false);
  for (const f of ["artifact_id", "digest", "locator"]) {
    assert.match(block, new RegExp(`${f}:\\s*ev\\.${f}\\s*\\?\\?\\s*null`), `${f} must fail closed`);
  }
});

check("review_state does not default to PUBLISHED_VERIFIED", () => {
  assert.equal(block.includes('"PUBLISHED_VERIFIED"'), false);
  assert.match(block, /review_state:\s*o\.review_state\s*\?\?\s*null/);
});

check("confidence does not default to 1.0", () => {
  assert.match(block, /confidence:.*:\s*null/);
  assert.equal(/confidence:.*:\s*1(\.0)?\b/.test(block), false);
});

check("counts are actual length, never floored to 1", () => {
  assert.match(block, /statement_count:\s*\(o\.statements\s*\|\|\s*\[\]\)\.length\s*,/);
  assert.match(block, /artifact_count:\s*\(o\.evidence_links\s*\|\|\s*\[\]\)\.length\s*,/);
  assert.equal(/\.length\s*\|\|\s*1/.test(block), false);
});

check("no synthesized statement IDs", () => {
  assert.equal(block.includes("STM-${raw.vessel_id}"), false);
  assert.match(block, /statements:\s*o\.statements\s*\|\|\s*\[\]/);
});

check("missing relations stay null (no Core-Midship / Assembly-B)", () => {
  assert.equal(src.includes('"Core-Midship"'), false);
  assert.equal(src.includes('"Assembly-B"'), false);
  assert.match(block, /connected_vertical_core:\s*o\.known_relations\?\.nearest_elevator\s*\|\|\s*null/);
  assert.match(block, /nearest_assembly_station:\s*o\.known_relations\?\.nearest_emergency_station\s*\|\|\s*null/);
});

// --- (B) real values exist, so pass-through is meaningful ------------------
check("populated raw trust values are present to pass through", () => {
  assert.ok(objs.length > 0);
  for (const o of objs) {
    assert.equal(typeof o.epistemic_state, "string");
    assert.equal(typeof o.confidence, "number");
    assert.ok(Array.isArray(o.evidence_links) && o.evidence_links.length > 0);
    assert.ok(o.evidence_links[0].artifact_id, "raw artifact_id present");
  }
});

check("raw carries honest UNKNOWN / zero-confidence entities", () => {
  // These must never be coerced to DIRECT / 1.0 by the frontend.
  assert.ok(objs.some((o) => o.epistemic_state === "UNKNOWN"), "UNKNOWN entities exist");
  assert.ok(objs.some((o) => o.confidence === 0), "zero-confidence entities exist");
  assert.ok(objs.some((o) => o.epistemic_state === "DERIVED"), "DERIVED entities exist");
});

check("raw supplies no source_title, so none may be rendered", () => {
  const anyTitle = objs.some((o) =>
    (o.evidence_links || []).some((ev: any) => ev.source_title != null),
  );
  assert.equal(anyTitle, false, "raw has no source_title; it must resolve to null");
});

if (failures > 0) {
  console.error(`\n${failures} test(s) failed`);
  process.exit(1);
}
console.log("\nAll P0-H1 canonicalization tests passed.");
