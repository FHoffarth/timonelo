# Knowledge freeze — 2026-08-17

Read in this order. These six documents supersede all chat history.

| # | Document | Answers |
|---|---|---|
| 1 | `ARCHITECTURE_STATE_2026-08-17.md` | Where truth lives, where UI lives, how the pipeline fits together |
| 2 | `SCIENTIFIC_PRINCIPLES.md` | What is forbidden, and what enforces it |
| 3 | `CURRENT_PROJECT_STATUS.md` | What is known, unknown, blocked, missing |
| 4 | `DECISION_LOG_2026-08-17.md` | Why each rule exists, and what it costs |
| 5 | `REPOSITORY_AUDIT_2026-08-17.md` | Every file classified across both repos |
| 6 | `ROADMAP_NEXT.md` | What comes next, with definitions of done |

## The four things a new engineer must know before touching anything

1. **Truth lives in the Truth Engine, nowhere else.** 32 published statements
   from 1 artifact. Anything not traceable to a held artifact is a hypothesis.
2. **UNKNOWN is a correct answer.** 4 of 2,217 cabins are curated. That number
   is honest and must not be improved by generating data.
3. **The Geometry Engine is empty on purpose.** No held artifact contains a
   scale or datum. No distance, route or walking time may be emitted.
4. **Two contradictions are live today.** `ontology/bellissima.py` still answers
   cabin 14122 differently from the evidence, and the evidence store sits in the
   wrong repository. Both are roadmap items M1 and M2 — read them before writing
   code that touches either.
