/**
 * Renders the Deck 14 proof objects.
 *
 * The SVG viewBox is the normalized unit square, because normalized fractions ARE
 * the coordinate system of the artifact. No scaling arithmetic is applied to the
 * geometry, so nothing can drift between the artifact and the picture.
 *
 * There is deliberately NO source-plan underlay. `deck14.review.png` is cropped to
 * a hand-picked viewport the artifact marks DISPLAY_ONLY with
 * `geometry_provenance: false`; adopting it as a backdrop would silently make a
 * non-canonical frame look canonical.
 */

import { provenanceClass, type ProofObject } from "./proofTypes";

/**
 * Full-MediaBox raster of the source deck plan, opt-in and off by default.
 *
 * Context, never evidence. Page 5 carries 243 Deck-14 cabin labels; the proof
 * accepts 10, so with this layer on, most of what is visible is NOT accepted
 * evidence. It is therefore desaturated and dimmed so the proof geometry stays
 * dominant, it is never hit-tested, and it carries no GeometryProvenance —
 * because it has none.
 *
 * See `frontend/public/data/deck14.page5.provenance.json` for its source
 * artifact, digest, page, MediaBox and exact render command.
 */
export const UNDERLAY_HREF = "/data/deck14.page5.png";

/**
 * Presentational inset, in normalized units, applied when drawing only.
 *
 * Adjacent cabin cells share an edge, so at low zoom their outlines merge and a
 * column of four cabins reads as one region. Insetting each envelope by a hair
 * keeps the seam visible. This NEVER mutates the artifact and is not replacement
 * geometry: `pickObjectAt` and the evidence drawer both use the untouched
 * `normalized_bbox`.
 */
const SEPARATION_INSET = 0.0004;

function insetPolygon(o: ProofObject): string {
  const [x0, y0, x1, y1] = o.normalized_bbox;
  const dx = Math.min(SEPARATION_INSET, (x1 - x0) / 4);
  const dy = Math.min(SEPARATION_INSET, (y1 - y0) / 4);
  const pts: Array<[number, number]> = [
    [x0 + dx, y0 + dy],
    [x1 - dx, y0 + dy],
    [x1 - dx, y1 - dy],
    [x0 + dx, y1 - dy],
  ];
  return pts.map(([x, y]) => `${x},${y}`).join(" ");
}

export interface ProofCanvasProps {
  objects: ProofObject[];
  selectedId: string | null;
  onSelect: (o: ProofObject) => void;
  /** Source-plan context layer. Off unless the reader explicitly asks for it. */
  showUnderlay?: boolean;
  /**
   * Breathing room around the objects' extent, in normalized units.
   *
   * Framing only. It widens the viewBox; it never moves, scales or crops an
   * object, and it is not a DISPLAY_ONLY viewport being promoted to truth — the
   * frame is still derived from the objects' own canonical coordinates.
   */
  padding?: number;
}

export default function ProofCanvas({
  objects,
  selectedId,
  onSelect,
  showUnderlay = false,
  padding = 0.006,
}: ProofCanvasProps) {
  if (objects.length === 0) return null;

  const xs = objects.flatMap((o) => [o.normalized_bbox[0], o.normalized_bbox[2]]);
  const ys = objects.flatMap((o) => [o.normalized_bbox[1], o.normalized_bbox[3]]);
  const minX = Math.min(...xs) - padding;
  const minY = Math.min(...ys) - padding;
  const width = Math.max(...xs) - minX + padding;
  const height = Math.max(...ys) - minY + padding;

  return (
    <svg
      viewBox={`${minX} ${minY} ${width} ${height}`}
      preserveAspectRatio="xMidYMid meet"
      role="img"
      aria-label="MSC Bellissima Deck 14 geometry proof"
      data-testid="proof-canvas"
      className="w-full h-full bg-[#0C1B2A]"
    >
      {showUnderlay && (
        <image
          href={UNDERLAY_HREF}
          x={0}
          y={0}
          width={1}
          height={1}
          preserveAspectRatio="none"
          data-testid="source-underlay"
          data-layer="source-context"
          opacity={0.24}
          style={{ filter: "grayscale(1)", pointerEvents: "none" }}
        />
      )}

      <defs>
        {/* Hatch marks the derived region as an area whose exact boundary is not established. */}
        <pattern
          id="derived-hatch"
          patternUnits="userSpaceOnUse"
          width="0.006"
          height="0.006"
          patternTransform="rotate(45)"
        >
          <line
            x1="0"
            y1="0"
            x2="0"
            y2="0.006"
            stroke="#C58A46"
            strokeWidth="0.0015"
            opacity="0.7"
          />
        </pattern>
      </defs>

      {objects.map((o) => {
        const kind = provenanceClass(o);
        const selected = o.object_id === selectedId;
        const derived = kind === "derived";
        return (
          <g key={o.object_id} data-testid={`object-${o.object_id}`}>
            <polygon
              points={insetPolygon(o)}
              data-object-id={o.object_id}
              data-provenance={o.geometry_provenance}
              data-publish-status={o.publish_status}
              data-provenance-style={kind}
              fill={derived ? "url(#derived-hatch)" : "#7FB2E5"}
              fillOpacity={derived ? 1 : selected ? 0.55 : 0.28}
              stroke={derived ? "#C58A46" : "#7FB2E5"}
              strokeWidth={selected ? 2.2 : 1.4}
              strokeDasharray={derived ? "4 3" : undefined}
              vectorEffect="non-scaling-stroke"
              onClick={() => onSelect(o)}
              style={{ cursor: "pointer" }}
            />
            <text
              x={(o.normalized_bbox[0] + o.normalized_bbox[2]) / 2}
              y={(o.normalized_bbox[1] + o.normalized_bbox[3]) / 2}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#F5F1EA"
              fontSize={derived ? 0.006 : 0.0055}
              style={{ pointerEvents: "none", userSelect: "none" }}
            >
              {o.cabin_number ?? "Lift"}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

export { SEPARATION_INSET, insetPolygon };
