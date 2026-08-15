# Timonelo

**Know your cabin before you book.**

Timonelo is an independent cruise knowledge platform. It helps travelers understand a cabin through objective spatial evidence before making a booking decision. Timonelo does not sell cruises and does not rank cabins on behalf of cruise lines.

> **Core principle:** Timonelo must never sound more certain than its evidence.

## Mission

Cruise booking presents cabins as inventory: category, price, a short description, and sometimes a simplified deck plan. Timonelo is built to turn verifiable ship geometry into clear, appropriately qualified spatial orientation and cabin information.

## Current Status: Foundation Freeze v1.0

The Timonelo foundations are established and **Frozen at Milestone v1.0**. The repository contains the canonical Knowledge Pack architecture, the Spatial Evidence Engine contracts, the Knowledge Factory foundation, the Explorer runtime MVP, and the authoritative Foundation Documentation Suite.

## Architecture

The system operates as an end-to-end spatial evidence pipeline:

- **Spatial Evidence Engine** — derives reproducible spatial evidence from ship geometry.
- **Canonical Knowledge Pack** — immutable, self-validating spatial twin data contract.
- **Ship Knowledge Factory** — multi-source blueprint ingestion, verification, and linting.
- **Cruise Explorer Platform** — publishes spatial orientation without modifying claims.

Detailed boundaries and technical contracts are specified in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Repository Structure

```text
.
├── assets/          Documentation and brand assets
├── data/            Source, processed, and ship-specific canonical packs
├── docs/            The Timonelo Foundation Documentation Suite
├── frontend/        Vite / React Cruise Explorer runtime
├── knowledge/       Structured markdown knowledge base & templates
├── src/timonelo/    Python package (Engine & Knowledge Pack schema)
└── tests/           Package unit and schema contract tests
```

## Development

The foundation has no runtime dependencies. Python 3.12 or later is required.

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

The Cruise Explorer lives in `frontend/` and is developed independently:

```bash
cd frontend
npm install
npm run dev
```

## Documentation Suite (v1.0 Frozen)

The complete documentation suite is housed under [`docs/`](docs/README.md):

- **[Documentation Hub](docs/README.md)** — Master documentation index & reading guide
- **[Manifesto](docs/MANIFESTO.md)** — Mission, philosophy, and negative boundaries
- **[Canon](docs/CANON.md)** — Epistemic definitions, terminology, and 20 spatial laws
- **[Product Specification](docs/PRODUCT.md)** — Cabin briefings, 16 experience dimensions, and user personas
- **[Architecture](docs/ARCHITECTURE.md)** — Technical module boundaries & Spatial Engine v1.0
- **[Engineering Principles](docs/ENGINEERING_PRINCIPLES.md)** — Invariants, determinism, and code standards
- **[Trust Framework](docs/TRUST_FRAMEWORK.md)** — Evidence hierarchy, provenance, and neutrality
- **[Roadmap](docs/ROADMAP.md)** — Milestone execution plan & scaling roadmap
- **[Contributing](docs/CONTRIBUTING.md)** — Contribution standards for code, cartography, and data

## License

Timonelo is licensed under the [MIT License](LICENSE).
