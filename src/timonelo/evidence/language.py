"""
Language Layer — renders answers without strengthening them.

Governed by ADR-0002 §9.

Presentation is not downstream of truth; it is where truth is most easily
destroyed. The audit found briefing.py appending "(Pure residential buffer)"
unconditionally to a cabin sitting directly beneath the Marketplace Buffet:
the engine had resolved the venue, and the renderer overwrote it with
reassurance.

Three binding constraints, enforced here rather than by style guide:

  1. Hedging is a function of computed confidence and method. A low-confidence
     INFERRED statement cannot produce an unhedged declarative sentence.
  2. Confidence is never rendered as a number. It is ordinal, not
     probabilistic; a decimal reads to a passenger as measured likelihood.
  3. UNKNOWN renders as an explicit gap, never as silence. A hidden UNKNOWN is
     indistinguishable from a question never asked.
"""

from __future__ import annotations

from typing import List, Optional

from timonelo.evidence.engine import Answer, DerivationNode, Method

# Ordinal bands. Deliberately not exposed as numbers (ADR-0002 §7.1).
BANDS = (
    (0.90, "documented"),
    (0.75, "well supported"),
    (0.50, "indicated"),
    (0.25, "weakly indicated"),
    (0.00, "barely supported"),
)


def band_for(confidence: float) -> str:
    for threshold, label in BANDS:
        if confidence >= threshold:
            return label
    return "barely supported"


def render(answer: Answer, label: str) -> str:
    """Render one answer. `label` is the question's presentation text.

    This is the ONLY place a passenger-visible sentence about a statement may
    be produced. It reads from the Answer; it never consults another source.
    """
    if not answer.known:
        guidance = answer.unknown_guidance or (
            "Timonelo does not hold a source for this yet."
        )
        return f"{label}: UNKNOWN — {guidance}"

    value = answer.value
    conf = answer.confidence or 0.0
    method = answer.derivation.method if answer.derivation else Method.DIRECT.value

    # Documented direct observation: plain statement, no hedge needed.
    if method == Method.DIRECT.value and conf >= 0.90:
        return f"{label}: {value}"

    # Truth-preserving computation over documented inputs.
    if method == Method.CALCULATED.value and conf >= 0.90:
        return f"{label}: {value} (calculated)"

    # Everything else is hedged in proportion to what the engine could justify.
    return f"{label}: {value} — {band_for(conf)}"


def render_derivation(node: DerivationNode, depth: int = 0) -> List[str]:
    """Human-readable explanation, derived FROM the graph (ADR-0002 §9.1).

    Never composed independently: every line here is a projection of a node
    that the engine produced.
    """
    pad = "  " * depth
    lines = [
        f"{pad}{node.value}  [{node.method}/{node.derivation}, "
        f"{band_for(node.confidence)}]"
    ]
    for src in node.sources:
        lines.append(f"{pad}  source: {src}")
    for child in node.inputs:
        lines.extend(render_derivation(child, depth + 1))
    return lines
