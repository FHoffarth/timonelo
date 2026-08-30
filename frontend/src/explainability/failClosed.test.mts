// P0-H2 targeted tests. Run with plain Node:
//   node frontend/src/explainability/failClosed.test.mts
//
// EvidenceResolver is imported and EXECUTED for real (its only imports are
// type-only, so Node's type-stripping erases them). ExplainabilityEngine cannot
// be imported under plain Node (it pulls value imports from modules that use
// extensionless specifiers), so meanBackedConfidence is exercised by executing
// its real shipped function body, extracted from the engine source.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { EvidenceResolver } from "./EvidenceResolver.ts";

const here = path.dirname(fileURLToPath(import.meta.url));

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

// --- Fixtures --------------------------------------------------------------
const RULE_WALK: any = {
  id: "RULE-WALK-001",
  category: "walking",
  title: "Direct Lift Access",
  description: "Direct corridor access to the nearest vertical core.",
  weight: 8,
  polarity: "POSITIVE",
  required_graph_relations: ["connected_vertical_core"],
  required_knowledge_entities: ["KE-LIFT-CORE"],
  required_geometry: [],
  required_evidence: { artifact_id: "RULE-LEVEL-ART", page: 7, title: "Rule Level Title" },
};

const RULE_QUIET: any = {
  ...RULE_WALK,
  id: "RULE-QUIET-004",
  description: "A catering venue is positioned on the deck above.",
  required_graph_relations: ["adjacent_overhead"],
};

const backedEntity: any = {
  data_origin: "CANONICAL_TRUTH_ENGINE",
  evidence_condition: "SUPPORTED",
  human_review_state: "APPROVED",
  publish_status: "PUBLISH_ALLOWED",
  geometry_provenance: "DIRECT_SOURCE_GEOMETRY",
  method: "DIRECT",
  derivation: "LOCAL",
  admitted_fact_keys: ["connected_vertical_core", "walking_intelligence", "source_artifact"],
  id: "14122",
  level: 14,
  zone: "MIDSHIP",
  side: "STARBOARD",
  accessible: true,
  has_balcony: false,
  epistemic_state: "DERIVED",
  confidence: 0.85,
  statements: ["STM-BEL-REAL-001"],
  evidence_links: [
    { artifact_id: "MSC-BEL-ART-007", source_title: null, digest: "abc", locator: "Deck 14 plan", page: 5 },
  ],
  relations: { connected_vertical_core: "Lift Core A", adjacent_overhead: null },
};

const unbackedEntity: any = {
  data_origin: "LEGACY_SCHEMATIC",
  evidence_condition: "UNKNOWN",
  human_review_state: "DRAFT",
  publish_status: "PUBLISH_BLOCKED",
  geometry_provenance: "UNKNOWN_PROVENANCE",
  method: null,
  derivation: null,
  admitted_fact_keys: [],
  id: "49999",
  level: 9,
  zone: "MIDSHIP",
  side: "PORT",
  accessible: false,
  has_balcony: false,
  epistemic_state: "UNKNOWN",
  confidence: null,
  statements: [],
  evidence_links: [],
  relations: {},
};

const backedAdmission: any = {
  entityAdmitted: true,
  admittedFactKeys: new Set(["connected_vertical_core", "walking_intelligence", "source_artifact"]),
};

console.log("P0-H2 explainability fail-closed:");

// --- EvidenceResolver (real execution) ------------------------------------
check("backed entity uses actual artifact_id / page / statement_id / status / confidence", () => {
  const p = EvidenceResolver.resolveRuleEvidence(RULE_WALK, backedEntity, "msc-bellissima", backedAdmission);
  assert.equal(p.artifact_id, "MSC-BEL-ART-007");
  assert.equal(p.page, 5);
  assert.equal(p.locator, "Deck 14 plan");
  assert.equal(p.statement_id, "STM-BEL-REAL-001");
  assert.equal(p.status, "DERIVED");
  assert.equal(p.confidence, 0.85);
});

check("unbacked entity fabricates no evidence or statement IDs", () => {
  const p = EvidenceResolver.resolveRuleEvidence(RULE_WALK, unbackedEntity);
  assert.equal(p.evidence_id, null);
  assert.equal(p.statement_id, null);
  assert.equal(p.artifact_id, null);
  assert.equal(p.source_title, null);
  assert.equal(p.geometry_file, null);
  for (const v of Object.values(p)) {
    if (typeof v === "string") {
      assert.equal(/^EV-/.test(v), false, `fabricated evidence id: ${v}`);
      assert.equal(/^STM-/.test(v), false, `fabricated statement id: ${v}`);
    }
  }
});

check("unbacked entity returns status UNKNOWN", () => {
  const p = EvidenceResolver.resolveRuleEvidence(RULE_WALK, unbackedEntity);
  assert.equal(p.status, "UNKNOWN");
  assert.notEqual(p.status, "DIRECT");
});

check("unbacked confidence is null (never a hardcoded 0.9-1.0)", () => {
  const p = EvidenceResolver.resolveRuleEvidence(RULE_WALK, unbackedEntity);
  assert.equal(p.confidence, null);
});

check("graph_edge is null when the required relation is absent", () => {
  // adjacent_overhead is null on the backed entity -> no edge may be claimed.
  const p = EvidenceResolver.resolveRuleEvidence(RULE_QUIET, backedEntity, "msc-bellissima", backedAdmission);
  assert.equal(p.graph_edge, null);
  const u = EvidenceResolver.resolveRuleEvidence(RULE_WALK, unbackedEntity);
  assert.equal(u.graph_edge, null);
});

check("graph_edge is emitted only from a real relation value", () => {
  const p = EvidenceResolver.resolveRuleEvidence(RULE_WALK, backedEntity, "msc-bellissima", backedAdmission);
  assert.equal(typeof p.graph_edge, "string");
  assert.match(p.graph_edge as string, /Lift Core A/);
});

check("no synthetic Marketplace_Buffet / Lift_Core_B fallbacks", () => {
  const src = fs.readFileSync(path.join(here, "EvidenceResolver.ts"), "utf8");
  assert.equal(src.includes("Marketplace_Buffet"), false);
  assert.equal(src.includes("Lift_Core_B"), false);
  assert.equal(src.includes("Midship Lift Bank"), false);
  assert.equal(src.includes(".geometry.json"), false);
  for (const e of [backedEntity, unbackedEntity]) {
    for (const rule of [RULE_WALK, RULE_QUIET]) {
      const p: any = EvidenceResolver.resolveRuleEvidence(
        rule,
        e,
        "msc-bellissima",
        e === backedEntity ? backedAdmission : undefined,
      );
      const blob = JSON.stringify(p);
      assert.equal(blob.includes("Marketplace_Buffet"), false);
      assert.equal(blob.includes("Lift_Core_B"), false);
    }
  }
});

check("raw_finding degrades to the neutral rule description", () => {
  const p = EvidenceResolver.resolveRuleEvidence(RULE_QUIET, unbackedEntity);
  assert.equal(p.raw_finding, RULE_QUIET.description);
  assert.equal(p.raw_finding.includes("49999"), false, "no entity-specific claim");
});

// --- meanBackedConfidence (real shipped body) ------------------------------
const engineSrc = fs.readFileSync(path.join(here, "ExplainabilityEngine.ts"), "utf8");
const sigIdx = engineSrc.indexOf("export function meanBackedConfidence");
assert.ok(sigIdx > 0, "meanBackedConfidence not found in engine");
const bodyStart = engineSrc.indexOf("{", sigIdx);
let depth = 0;
let bodyEnd = -1;
for (let i = bodyStart; i < engineSrc.length; i++) {
  if (engineSrc[i] === "{") depth++;
  else if (engineSrc[i] === "}") {
    depth--;
    if (depth === 0) { bodyEnd = i; break; }
  }
}
assert.ok(bodyEnd > bodyStart, "could not extract function body");
const meanBackedConfidence = new Function(
  "values",
  engineSrc.slice(bodyStart + 1, bodyEnd),
) as (v: Array<number | null | undefined>) => number | null;

check("all null -> null", () => {
  assert.equal(meanBackedConfidence([null, null, undefined]), null);
  assert.equal(meanBackedConfidence([]), null);
});

check("mix of null + numeric -> averages numeric only", () => {
  // Nulls must be excluded, not coerced to 0.
  assert.equal(meanBackedConfidence([null, 0.8, null, 1.0]), 0.9);
  assert.equal(meanBackedConfidence([0.5, null]), 0.5);
});

check("result is never NaN", () => {
  for (const input of [
    [null, undefined],
    [NaN, null],
    [Infinity, null],
    [0.5, NaN],
    [],
  ] as Array<Array<number | null | undefined>>) {
    const out = meanBackedConfidence(input);
    assert.equal(out === null || Number.isFinite(out), true, `NaN-ish for ${JSON.stringify(input)}`);
  }
});

check("zero confidence is kept as a real value, not treated as absent", () => {
  assert.equal(meanBackedConfidence([0, 1]), 0.5);
});

// --- ReasonTree fail-closed (source contract + real aggregation body) ------
// ReasonTree.ts cannot be imported under plain Node (its type imports use
// extensionless value syntax), so the baseline provenance is asserted from
// source and its aggregation body is executed directly.
const reasonSrc = fs.readFileSync(path.join(here, "ReasonTree.ts"), "utf8");

console.log("\nP0-H2 ReasonTree fail-closed:");

check("no fabricated BASELINE evidence identifiers", () => {
  assert.equal(reasonSrc.includes("EV-BASELINE"), false);
  assert.equal(reasonSrc.includes("TIMONELO-CORE-STANDARDS"), false);
  assert.equal(reasonSrc.includes("Timonelo Maritime Baseline Model"), false);
});

check("baseline provenance claims no DIRECT status or 1.0 confidence", () => {
  const start = reasonSrc.indexOf("rule_id: \"BASELINE\"");
  const end = reasonSrc.indexOf("triggeredRules.forEach");
  assert.ok(start > 0 && end > start, "could not locate baseline step");
  const baseline = reasonSrc.slice(start, end);
  assert.match(baseline, /evidence_id:\s*null/);
  assert.match(baseline, /source_title:\s*null/);
  assert.match(baseline, /artifact_id:\s*null/);
  assert.match(baseline, /confidence:\s*null/);
  assert.match(baseline, /status:\s*"UNKNOWN"/);
  assert.equal(/status:\s*"DIRECT"/.test(baseline), false);
  assert.equal(/confidence:\s*1(\.0)?\b/.test(baseline), false);
});

check("aggregation no longer sums raw confidences or defaults to 0.95", () => {
  assert.equal(reasonSrc.includes("0.95"), false);
  assert.equal(/confs\.reduce\(\(a, b\) => a \+ b, 0\) \/ confs\.length/.test(reasonSrc), false);
  assert.match(reasonSrc, /meanBackedConfidence\(/);
});

// Execute ReasonTree's real meanBackedConfidence body.
function extractFnBody(src: string, name: string): (v: Array<number | null | undefined>) => number | null {
  const sig = src.indexOf(`function ${name}`);
  assert.ok(sig > 0, `${name} not found`);
  const open = src.indexOf("{", sig);
  let d = 0;
  let close = -1;
  for (let i = open; i < src.length; i++) {
    if (src[i] === "{") d++;
    else if (src[i] === "}") { d--; if (d === 0) { close = i; break; } }
  }
  assert.ok(close > open, `could not extract ${name} body`);
  return new Function("values", src.slice(open + 1, close)) as (v: Array<number | null | undefined>) => number | null;
}
const rtMean = extractFnBody(reasonSrc, "meanBackedConfidence");

check("ReasonTree: all-null confidence -> null", () => {
  assert.equal(rtMean([null, null, undefined]), null);
  assert.equal(rtMean([]), null);
});

check("ReasonTree: numeric + null -> numeric-only average", () => {
  assert.equal(rtMean([null, 0.8, null, 1.0]), 0.9);
  assert.equal(rtMean([0.5, null]), 0.5);
  assert.equal(rtMean([0, 1]), 0.5); // zero is a real value, not "absent"
});

check("ReasonTree: never NaN", () => {
  for (const input of [
    [null, undefined],
    [NaN, null],
    [Infinity, null],
    [0.5, NaN],
    [],
  ] as Array<Array<number | null | undefined>>) {
    const out = rtMean(input);
    assert.equal(out === null || Number.isFinite(out), true, `NaN-ish for ${JSON.stringify(input)}`);
  }
});

if (failures > 0) {
  console.error(`\n${failures} test(s) failed`);
  process.exit(1);
}
console.log("\nAll P0-H2 tests passed.");
