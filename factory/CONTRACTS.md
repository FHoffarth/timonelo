# Knowledge Factory Data Contracts & JSON Schemas
### Strict I/O Schemas for Factory Pipeline Stages

---

## 1. Stage 01 Output: `RawEvidenceBatch`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RawEvidenceBatch",
  "type": "object",
  "required": ["batch_id", "vessel_imo", "created_at_utc", "sources"],
  "properties": {
    "batch_id": { "type": "string", "pattern": "^BATCH-[A-Z0-9_-]+$" },
    "vessel_imo": { "type": "string", "pattern": "^IMO[0-9]{7}$" },
    "created_at_utc": { "type": "string", "format": "date-time" },
    "sources": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["source_id", "source_type", "file_path", "sha256", "license_type"],
        "properties": {
          "source_id": { "type": "string" },
          "source_type": { "type": "string", "enum": ["GA_BLUEPRINT", "CABIN_MANIFEST", "SURVEY_PHOTO", "BUILDER_SPEC"] },
          "file_path": { "type": "string" },
          "sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
          "license_type": { "type": "string" }
        }
      }
    }
  }
}
```

---

## 2. Stage 02 Output: `NormalizedShipDraft`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "NormalizedShipDraft",
  "type": "object",
  "required": ["vessel_imo", "coordinate_system", "decks", "cabins"],
  "properties": {
    "vessel_imo": { "type": "string" },
    "coordinate_system": {
      "type": "object",
      "required": ["length_overall_m", "beam_m", "normalized_bounds"],
      "properties": {
        "length_overall_m": { "type": "number", "minimum": 50 },
        "beam_m": { "type": "number", "minimum": 10 },
        "normalized_bounds": {
          "type": "object",
          "properties": {
            "x": { "type": "array", "items": { "type": "number" }, "minItems": 2, "maxItems": 2 },
            "y": { "type": "array", "items": { "type": "number" }, "minItems": 2, "maxItems": 2 }
          }
        }
      }
    },
    "decks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["deck_index", "elevation_m", "perimeter_polygon_wkt"],
        "properties": {
          "deck_index": { "type": "string" },
          "elevation_m": { "type": "number" },
          "perimeter_polygon_wkt": { "type": "string" }
        }
      }
    },
    "cabins": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["cabin_number", "deck_index", "boundary_polygon_wkt", "door_coordinate"],
        "properties": {
          "cabin_number": { "type": "string" },
          "deck_index": { "type": "string" },
          "boundary_polygon_wkt": { "type": "string" },
          "door_coordinate": {
            "type": "array",
            "items": { "type": "number" },
            "minItems": 2,
            "maxItems": 2
          }
        }
      }
    }
  }
}
```

---

## 3. Stage 04 Output: `MutationLedger`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MutationLedger",
  "type": "object",
  "required": ["vessel_imo", "base_archetype_id", "mutations"],
  "properties": {
    "vessel_imo": { "type": "string" },
    "base_archetype_id": { "type": "string" },
    "mutations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["mutation_type", "entity_type", "entity_id", "description", "evidence_ids"],
        "properties": {
          "mutation_type": { "type": "string", "enum": ["ADDED", "MODIFIED", "DEPRECATED"] },
          "entity_type": { "type": "string", "enum": ["CABIN", "VENUE", "DECK", "CORRIDOR"] },
          "entity_id": { "type": "string" },
          "description": { "type": "string" },
          "evidence_ids": { "type": "array", "items": { "type": "string" } }
        }
      }
    }
  }
}
```

---

## 4. Stage 06/07 Output: `ValidationReport`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ValidationReport",
  "type": "object",
  "required": ["report_id", "stage", "passed", "experience_ready_score", "findings"],
  "properties": {
    "report_id": { "type": "string" },
    "stage": { "type": "string", "enum": ["SPATIAL_VALIDATION", "EXPERIENCE_VALIDATION"] },
    "passed": { "type": "boolean" },
    "experience_ready_score": { "type": "number", "minimum": 0.0, "maximum": 100.0 },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["severity", "check_name", "message", "entity_id"],
        "properties": {
          "severity": { "type": "string", "enum": ["INFO", "WARNING", "BLOCKING_ERROR"] },
          "check_name": { "type": "string" },
          "message": { "type": "string" },
          "entity_id": { "type": "string" }
        }
      }
    }
  }
}
```

---

## 5. Stage 08 Output: `PublicationManifest`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PublicationManifest",
  "type": "object",
  "required": ["pack_id", "vessel_imo", "semantic_version", "sha256", "size_bytes", "published_at_utc"],
  "properties": {
    "pack_id": { "type": "string" },
    "vessel_imo": { "type": "string" },
    "semantic_version": { "type": "string" },
    "sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
    "size_bytes": { "type": "integer", "minimum": 1 },
    "published_at_utc": { "type": "string", "format": "date-time" },
    "cdn_distribution_urls": {
      "type": "array",
      "items": { "type": "string", "format": "uri" }
    }
  }
}
```
