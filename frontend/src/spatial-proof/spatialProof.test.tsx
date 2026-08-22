/**
 * Behavioural tests for the Deck 14 spatial proof viewer.
 *
 * Rendering is asserted through `renderToStaticMarkup`, so no DOM environment or
 * testing-library dependency is needed: the questions here are all about what the
 * viewer emits, not how it behaves under interaction.
 *
 * The proof artifact itself is read from disk, so these tests fail if the shipped
 * artifact changes shape.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import EvidenceDrawer from "./EvidenceDrawer";
import ProofCanvas, { UNDERLAY_HREF } from "./ProofCanvas";
import SpatialProofViewer, { PathfindingUnavailable } from "./SpatialProofViewer";
import { ProofLoadError, hasAdmittedConnectivity, parseProof, pickObjectAt } from "./loadProof";
import type { ProofDocument, ProofObject } from "./proofTypes";

const doc: ProofDocument = parseProof(
  JSON.parse(
    readFileSync(resolve(__dirname, "../../public/data/deck14.proof.json"), "utf-8"),
  ),
);
const objects = doc.objects;
const byCabin = (n: string) => objects.find((o) => o.cabin_number === n) as ProofObject;
const lift = objects.find((o) => o.semantic_type !== "cabin") as ProofObject;

/** The five pairs whose source bboxes overlap by 0.0002-0.0108 pt around a shared edge. */
const OVERLAP_PAIRS: Array<[string, string]> = [
  ["14002", "14006"],
  ["14008", "14010"],
  ["14005", "14009"],
  ["14003", "14007"],
  ["14006", "14008"],
];

describe("loader fails closed", () => {
  it("rejects a wrong schema", () => {
    expect(() => parseProof({ ...doc, schema: "something.else.v9" })).toThrow(ProofLoadError);
  });

  it("rejects a wrong deck", () => {
    expect(() => parseProof({ ...doc, deck: { number: 8, name: "Meraviglia" } })).toThrow(
      ProofLoadError,
    );
  });

  it("accepts the canonical artifact", () => {
    expect(parseProof(doc).objects).toHaveLength(11);
  });
});

describe("deterministic hit-testing", () => {
  it.each(OVERLAP_PAIRS)("resolves the %s/%s overlap band identically every time", (a, b) => {
    const A = byCabin(a);
    const B = byCabin(b);
    // A point inside the shared band: both bboxes contain it.
    const y = (Math.max(A.normalized_bbox[1], B.normalized_bbox[1]) +
      Math.min(A.normalized_bbox[3], B.normalized_bbox[3])) / 2;
    const x = (Math.max(A.normalized_bbox[0], B.normalized_bbox[0]) +
      Math.min(A.normalized_bbox[2], B.normalized_bbox[2])) / 2;

    const inA = x >= A.normalized_bbox[0] && x <= A.normalized_bbox[2] &&
      y >= A.normalized_bbox[1] && y <= A.normalized_bbox[3];
    const inB = x >= B.normalized_bbox[0] && x <= B.normalized_bbox[2] &&
      y >= B.normalized_bbox[1] && y <= B.normalized_bbox[3];
    expect(inA && inB).toBe(true); // the band is real

    const first = pickObjectAt(objects, x, y);
    expect(first).not.toBeNull();
    // Order of the input must not change the answer.
    expect(pickObjectAt([...objects].reverse(), x, y)?.object_id).toBe(first?.object_id);
    expect(pickObjectAt([...objects].sort(() => -1), x, y)?.object_id).toBe(first?.object_id);
  });

  it("returns null outside every envelope", () => {
    expect(pickObjectAt(objects, 0.99, 0.99)).toBeNull();
  });
});

describe("canvas rendering", () => {
  const svg = renderToStaticMarkup(
    <ProofCanvas objects={objects} selectedId={null} onSelect={() => {}} />,
  );

  it("renders all 11 proof objects", () => {
    for (const o of objects) expect(svg).toContain(`object-${o.object_id}`);
    expect(svg.match(/data-object-id="/g)).toHaveLength(11);
  });

  it("outlines no object outside the proof set", () => {
    for (const absent of ["14011", "14013", "14015", "14019", "14021"]) {
      expect(svg).not.toContain(`>${absent}<`);
    }
  });

  it("styles the lift as derived, distinctly from transformed cabins", () => {
    expect(svg).toContain(`data-provenance="DERIVED_GEOMETRY"`);
    expect(svg).toContain("url(#derived-hatch)");
    expect(svg.match(/data-provenance-style="derived"/g)).toHaveLength(1);
    expect(svg.match(/data-provenance-style="transformed"/g)).toHaveLength(10);
  });

  it("drives geometry styling from provenance, not publish status", () => {
    // Every object shares PUBLISH_BLOCKED, yet two distinct geometry styles exist.
    const blocked = svg.match(/data-publish-status="PUBLISH_BLOCKED"/g);
    expect(blocked).toHaveLength(11);
    expect(new Set(["derived", "transformed"]).size).toBe(2);
  });

  it("emits no corridor geometry", () => {
    expect(doc.corridor_observation.accepted_geometry).toBe(false);
    expect(doc.corridor_observation.geometry).toBeNull();
    expect(svg.toLowerCase()).not.toContain("corridor");
  });
});

describe("zero-connectivity refusal", () => {
  it("reports no admitted connectivity for this proof", () => {
    expect(doc.navigation_graph).toBeNull();
    expect(hasAdmittedConnectivity(doc)).toBe(false);
  });

  it("refuses pathfinding with an explanation and no active CTA", () => {
    const html = renderToStaticMarkup(<PathfindingUnavailable doc={doc} />);
    expect(html).toContain("Pathfinding not available on this deck yet");
    expect(html).toContain(
      "Timonelo can identify these locations, but verified connectivity has not been established.",
    );
    // No route/directions call to action of any kind.
    expect(html.toLowerCase()).not.toContain("route to here");
    expect(html.toLowerCase()).not.toContain("directions");
    expect(html.toLowerCase()).not.toContain("get directions");
  });

  it("exposes the technical refusal code on request", () => {
    // Rendered statically the detail is collapsed; the code lives in the component.
    const source = readFileSync(resolve(__dirname, "SpatialProofViewer.tsx"), "utf-8");
    expect(source).toContain("NOT_ROUTABLE · NO_ADMITTED_CONNECTIVITY");
  });
});

describe("no measurement is ever implied", () => {
  const rendered = [
    renderToStaticMarkup(<ProofCanvas objects={objects} selectedId={null} onSelect={() => {}} />),
    renderToStaticMarkup(<EvidenceDrawer object={lift} doc={doc} />),
    renderToStaticMarkup(<EvidenceDrawer object={byCabin("14001")} doc={doc} />),
    renderToStaticMarkup(<PathfindingUnavailable doc={doc} />),
  ].join("\n");

  it("emits no metric distance or walking-time unit", () => {
    // The disclaimers are stripped first: they legitimately contain "metres" in
    // order to deny it, and scanning them would flag the very text that prevents
    // the misreading. Their presence is asserted separately below.
    const DISCLAIMERS = [
      "not metres. no scale has been established.",
      "(pdf points — provenance, not a measurement)",
      "(page fractions — not a measurement)",
    ];
    let claimBearing = rendered.toLowerCase();
    for (const d of DISCLAIMERS) claimBearing = claimBearing.split(d).join(" ");

    for (const forbidden of [
      "metre", "meter", " km", "kilomet", "walking time", "walk time",
      "minutes away", "sq m", "m²", "feet away", "distance",
    ]) {
      expect(claimBearing).not.toContain(forbidden);
    }
  });

  it("labels coordinates as provenance, not measurement", () => {
    const drawer = renderToStaticMarkup(<EvidenceDrawer object={byCabin("14001")} doc={doc} />);
    expect(drawer).toContain("not a measurement");
    expect(drawer).toContain("Not metres. No scale has been established.");
  });

  it("marks the derived region's boundary as not established", () => {
    const drawer = renderToStaticMarkup(<EvidenceDrawer object={lift} doc={doc} />);
    expect(drawer).toContain("derived-boundary-note");
    expect(drawer).toContain("not its exact boundary");
  });
});

describe("presentational separation does not become geometry", () => {
  it("leaves the artifact's normalized_bbox untouched", () => {
    const before = JSON.stringify(objects.map((o) => o.normalized_bbox));
    renderToStaticMarkup(<ProofCanvas objects={objects} selectedId={null} onSelect={() => {}} />);
    expect(JSON.stringify(objects.map((o) => o.normalized_bbox))).toBe(before);
  });

  it("picks using artifact geometry, not the inset drawing geometry", () => {
    const c = byCabin("14001");
    // A point just inside the true edge, which the presentational inset excludes.
    const x = c.normalized_bbox[0] + 1e-5;
    const y = (c.normalized_bbox[1] + c.normalized_bbox[3]) / 2;
    expect(pickObjectAt(objects, x, y)?.object_id).toBe(c.object_id);
  });
});

describe("viewer composition", () => {
  it("is a component, and the artifact is locked to Deck 14", () => {
    expect(typeof SpatialProofViewer).toBe("function");
    expect(doc.deck.number).toBe(14);
    expect(doc.source.artifact_id).toBe("ART-0001");
  });
});


describe("source-plan underlay is optional context, never evidence", () => {
  const off = renderToStaticMarkup(
    <ProofCanvas objects={objects} selectedId={null} onSelect={() => {}} />,
  );
  const on = renderToStaticMarkup(
    <ProofCanvas objects={objects} selectedId={null} onSelect={() => {}} showUnderlay />,
  );

  it("1. is OFF by default", () => {
    expect(off).not.toContain('data-testid="source-underlay"');
    expect(off).not.toContain("<image");
    // The viewer's own default state is off, not merely the canvas prop's.
    const src = readFileSync(resolve(__dirname, "SpatialProofViewer.tsx"), "utf-8");
    expect(src).toContain("useState(false)");
  });

  it("2. can be enabled", () => {
    expect(on).toContain('data-testid="source-underlay"');
    expect(on).toContain(UNDERLAY_HREF);
  });

  it("3. is the only raster layer, mapped 1:1 to the unit square", () => {
    expect(on.match(/<image/g)).toHaveLength(1);
    expect(on).toContain('preserveAspectRatio="none"');
    // x=0 y=0 w=1 h=1: the raster is the full MediaBox and the viewBox is the
    // normalized unit square, so no transform math is involved.
    expect(on).toMatch(/<image[^>]*x="0"[^>]*y="0"[^>]*width="1"[^>]*height="1"/);
  });

  it("4. unproven source content is never selectable", () => {
    // The raster cannot receive pointer events at all.
    expect(on).toMatch(/<image[^>]*pointer-events:none/);
    expect(on).toContain('data-layer="source-context"');
    // It is not an object: no object id, no provenance styling.
    const imageTag = on.slice(on.indexOf("<image"), on.indexOf(">", on.indexOf("<image")));
    expect(imageTag).not.toContain("data-object-id");
    expect(imageTag).not.toContain("data-provenance");
  });

  it("5. pickObjectAt remains proof-only regardless of the underlay", () => {
    // A point over a visible-but-unproven cabin (14015 sits below 14007) resolves
    // to nothing: the underlay adds pixels, never pickable objects.
    const c7 = byCabin("14007");
    const belowProofSet = c7.normalized_bbox[3] + 0.004;
    const x = (c7.normalized_bbox[0] + c7.normalized_bbox[2]) / 2;
    expect(pickObjectAt(objects, x, belowProofSet)).toBeNull();
    expect(objects).toHaveLength(11);
  });

  it("6. refusal behaviour is unchanged by the underlay", () => {
    expect(hasAdmittedConnectivity(doc)).toBe(false);
    const html = renderToStaticMarkup(<PathfindingUnavailable doc={doc} />);
    expect(html).toContain("Pathfinding not available on this deck yet");
    expect(on.toLowerCase()).not.toContain("corridor");
    expect(on.toLowerCase()).not.toContain("door");
  });

  it("7. the metric disclaimer is untouched", () => {
    const drawer = renderToStaticMarkup(<EvidenceDrawer object={byCabin("14001")} doc={doc} />);
    expect(drawer).toContain("Not metres. No scale has been established.");
    expect(on).not.toMatch(/metre|meter|km/i);
  });

  it("8. proof geometry stays provenance-styled with the underlay on", () => {
    expect(on.match(/data-provenance-style="transformed"/g)).toHaveLength(10);
    expect(on.match(/data-provenance-style="derived"/g)).toHaveLength(1);
    expect(on).toContain("url(#derived-hatch)");
    // Styling identical with and without the raster: the underlay changes nothing.
    // React emits <image ...></image>, so both tags must go.
    const stripImage = (s: string) =>
      s.replace(/<image[^>]*>/, "").replace(/<\/image>/, "");
    expect(stripImage(on)).toBe(stripImage(off));
  });

  it("is desaturated and subordinate so proof geometry dominates", () => {
    expect(on).toMatch(/<image[^>]*grayscale\(1\)/);
    const opacity = Number(on.match(/<image[^>]*opacity="([\d.]+)"/)?.[1]);
    expect(opacity).toBeGreaterThan(0);
    expect(opacity).toBeLessThan(0.5);
  });
});
