# Timonelo

**Know your cabin before you book.**

Timonelo is an independent cabin intelligence platform. It helps travelers understand a cabin through objective spatial evidence before making a booking decision. Timonelo does not sell cruises and does not rank cabins on behalf of cruise lines.

> **Core principle:** Timonelo must never sound more certain than its evidence.

## Mission

Cruise booking presents cabins as inventory: category, price, a short description, and sometimes a simplified deck plan. Timonelo is being built to turn verifiable ship geometry into clear, appropriately qualified cabin information.

## Current status

Timonelo is at repository foundation stage. The project currently contains its product direction, architectural boundaries, data conventions, and a minimal Python package. There is no public product, booking integration, database, or user interface yet.

## Planned architecture

The system is planned as four independent modules:

- **Spatial Evidence Engine** — derives reproducible spatial evidence from ship geometry.
- **Ship Knowledge Graph** — represents cabins, decks, venues, connections, and provenance.
- **Cabin Briefing Generator** — translates available evidence into a bounded cabin briefing.
- **Web Platform** — publishes cabin briefings and supporting evidence without participating in their calculation.

Responsibilities and boundaries are described in [docs/architecture.md](docs/architecture.md).

## Repository structure

```text
.
├── assets/          Documentation and brand assets
├── data/            Source, processed, and ship-specific data
├── docs/            Vision, product, roadmap, and architecture
├── src/timonelo/    Python package
└── tests/           Package and future contract tests
```

## Development

The foundation has no runtime dependencies. Python 3.12 or later is required.

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

## Documentation

- [Vision](docs/vision.md)
- [Product](docs/product.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)

## License

Timonelo is licensed under the [MIT License](LICENSE).
