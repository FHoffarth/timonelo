# Timonelo frontend

The Timonelo landing page is a standalone Vite application.

```bash
npm install
npm run dev
```

Use `npm run build` for a production build and `npm run typecheck` to validate the TypeScript source.

## Cruise Explorer

The read-only explorer consumes the canonical MSC Bellissima pack directly from `data/ships/msc-bellissima/knowledge-pack.json`; it does not maintain a frontend copy.

- Ship: `/explore/ships/msc-bellissima`
- Deck: `/explore/decks/:number`
- Cabin: `/explore/cabins/:number`

Explorer pages expose source locators, source limitations, explicit unknowns, and the pack snapshot boundary. They MUST NOT introduce recommendations, scores, suitability claims, or inferred cabin attributes.
