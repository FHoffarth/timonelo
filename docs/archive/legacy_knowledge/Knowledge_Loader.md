# Knowledge Loader

The Knowledge Loader provides metadata-only runtime access to the Timonelo Knowledge Repository. It contains no recommendation, inference, document-body parsing, or application integration.

## Architecture

`src/knowledge/loader.py` discovers Markdown records and reads only their `## Metadata` section. `models.py` defines immutable records and structured validation results. `validators.py` checks identity, placement, aliases, and references. `registry.py` provides case-insensitive lookup by canonical ID or alias. `exceptions.py` separates repository and document failures from record validation findings.

## Loading Lifecycle

1. Confirm that the knowledge root exists.
2. Discover Markdown files while excluding generated files, guidance, templates, and images.
3. Read metadata without interpreting document bodies.
4. Construct KnowledgeRecord and SourceRecord models.
5. Validate mandatory metadata, placement, IDs, aliases, and references.
6. Return a KnowledgeRegistry with all records and one ValidationResult.

## Registry Concept

The registry keeps knowledge records, source records, and aliases in separate case-insensitive maps. `resolve()` accepts any canonical ID or unambiguous alias; `resolve_record()` and `resolve_source()` enforce the expected record kind. The registry is an in-memory boundary and does not prescribe persistence.

## Validation Flow

Validation is non-destructive and accumulates structured issues with a code, file path, message, and optional reference. Supported findings are `DUPLICATE_ID`, `MISSING_METADATA`, `MISSING_RELATED_RECORD`, `MISSING_SOURCE_RECORD`, `DUPLICATE_ALIAS`, and `INVALID_FILE_PLACEMENT`. Callers decide whether an invalid registry may be inspected or rejected.

Relationships, sources, and aliases use the optional comma-separated metadata fields `Related IDs`, `Source IDs`, and `Aliases`. Business content below metadata is never loaded.
