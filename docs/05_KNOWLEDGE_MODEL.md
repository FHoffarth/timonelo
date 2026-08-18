# 05_KNOWLEDGE_MODEL — Semantic Knowledge Graph & International Standards

## 1. The Graph as the Source of Truth

In Timonelo, **the Knowledge Graph is the product**.

Every web page, card, modal, or Living Deck visualization is merely a **reactive projection of graph edges**.

---

## 2. Standardized Ontologies

### A. W3C Building Topology Ontology (BOT)
We model vessels using W3C BOT classes:
* `bot:Building` $\rightarrow$ `Vessel` (e.g. `msc-bellissima`)
* `bot:Storey` $\rightarrow$ `DeckLevel` (e.g. `Deck 14 Girasole / World Class`)
* `bot:Space` $\rightarrow$ `Stateroom` / `Venue` (e.g. `Cabin 14122`, `London Theatre`)
* `bot:adjacentElement` $\rightarrow$ Structural boundaries, corridor interfaces, vertical elevator shafts.

```turtle
@prefix bot: <https://w3id.org/bot#> .
@prefix tim: <https://timonelo.com/ontology#> .

tim:msc-bellissima a bot:Building ;
    tim:vesselName "MSC Bellissima" ;
    bot:hasStorey tim:deck-14 .

tim:deck-14 a bot:Storey ;
    bot:hasSpace tim:cabin-14122 .

tim:cabin-14122 a bot:Space, tim:Stateroom ;
    tim:stateroomCategory "STATEROOM_INTERIOR" ;
    tim:accessible true ;
    bot:adjacentElement tim:cabin-14120, tim:cabin-14124 .
```

### B. W3C Provenance Ontology (PROV-O)
* `prov:Entity`: The spatial statement or stateroom attribute.
* `prov:Activity`: The feature extraction or human verification process.
* `prov:Agent`: The researcher, auditor, or extraction algorithm.
* `prov:wasDerivedFrom`: Cryptographic link to the source document with SHA-256 integrity digest.

### C. OGC IndoorGML & JSON-LD
* **IndoorGML**: Supports navigational wayfinding from any cabin door to the nearest emergency assembly station or elevator lobby.
* **JSON-LD**: Provides schema.org and RDF-compliant linked data endpoints for search crawlers and semantic agents.
