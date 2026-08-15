"""Transactional SQLite projection for immutable knowledge pack versions."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .codec import canonical_json_bytes, load_pack
from .models import Cabin, CabinCategory, Deck, KnowledgePack, PublicArea, Ship


SCHEMA_VERSION = 1


class PersistenceConflictError(RuntimeError):
    """Raised when an immutable pack version is presented with new content."""


@dataclass(frozen=True, slots=True)
class ImportResult:
    pack_version_id: int
    pack_id: str
    version: str
    content_sha256: str
    inserted: bool


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS knowledge_pack_versions (
    pack_version_id INTEGER PRIMARY KEY,
    pack_id TEXT NOT NULL,
    version TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    effective_date TEXT NOT NULL,
    status TEXT NOT NULL,
    ship_entity_id TEXT NOT NULL,
    limitations_json TEXT NOT NULL,
    content_sha256 TEXT NOT NULL UNIQUE,
    source_path TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    UNIQUE (pack_id, version)
);

CREATE TABLE IF NOT EXISTS entities (
    pack_version_id INTEGER NOT NULL,
    entity_id TEXT NOT NULL,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('ship', 'deck', 'cabin_category', 'cabin', 'public_area')),
    PRIMARY KEY (pack_version_id, entity_id),
    FOREIGN KEY (pack_version_id) REFERENCES knowledge_pack_versions(pack_version_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS sources (
    pack_version_id INTEGER NOT NULL,
    source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    publisher TEXT NOT NULL,
    url TEXT NOT NULL,
    accessed_at TEXT NOT NULL,
    source_type TEXT NOT NULL,
    published_at TEXT,
    limitations_json TEXT NOT NULL,
    PRIMARY KEY (pack_version_id, source_id),
    FOREIGN KEY (pack_version_id) REFERENCES knowledge_pack_versions(pack_version_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS entity_sources (
    pack_version_id INTEGER NOT NULL,
    entity_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    PRIMARY KEY (pack_version_id, entity_id, source_id),
    FOREIGN KEY (pack_version_id, entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT,
    FOREIGN KEY (pack_version_id, source_id) REFERENCES sources(pack_version_id, source_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ships (
    pack_version_id INTEGER NOT NULL,
    entity_id TEXT NOT NULL,
    name TEXT NOT NULL,
    operator_name TEXT NOT NULL,
    cabin_count INTEGER,
    guest_capacity INTEGER,
    source_locator TEXT NOT NULL,
    PRIMARY KEY (pack_version_id, entity_id),
    FOREIGN KEY (pack_version_id, entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS decks (
    pack_version_id INTEGER NOT NULL,
    entity_id TEXT NOT NULL,
    ship_entity_id TEXT NOT NULL,
    number INTEGER NOT NULL,
    name TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    source_locator TEXT NOT NULL,
    PRIMARY KEY (pack_version_id, entity_id),
    UNIQUE (pack_version_id, ship_entity_id, number),
    UNIQUE (pack_version_id, ship_entity_id, ordinal),
    FOREIGN KEY (pack_version_id, entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT,
    FOREIGN KEY (pack_version_id, ship_entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS cabin_categories (
    pack_version_id INTEGER NOT NULL,
    entity_id TEXT NOT NULL,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    accommodation_type TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    PRIMARY KEY (pack_version_id, entity_id),
    UNIQUE (pack_version_id, code),
    FOREIGN KEY (pack_version_id, entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS cabin_category_decks (
    pack_version_id INTEGER NOT NULL,
    category_entity_id TEXT NOT NULL,
    deck_entity_id TEXT NOT NULL,
    PRIMARY KEY (pack_version_id, category_entity_id, deck_entity_id),
    FOREIGN KEY (pack_version_id, category_entity_id) REFERENCES cabin_categories(pack_version_id, entity_id) ON DELETE RESTRICT,
    FOREIGN KEY (pack_version_id, deck_entity_id) REFERENCES decks(pack_version_id, entity_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS cabins (
    pack_version_id INTEGER NOT NULL,
    entity_id TEXT NOT NULL,
    ship_entity_id TEXT NOT NULL,
    deck_entity_id TEXT NOT NULL,
    number TEXT NOT NULL,
    category_entity_id TEXT,
    limitations_json TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    PRIMARY KEY (pack_version_id, entity_id),
    UNIQUE (pack_version_id, ship_entity_id, number),
    FOREIGN KEY (pack_version_id, entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT,
    FOREIGN KEY (pack_version_id, ship_entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT,
    FOREIGN KEY (pack_version_id, deck_entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT,
    FOREIGN KEY (pack_version_id, category_entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_cabins_deck ON cabins(pack_version_id, deck_entity_id);
CREATE INDEX IF NOT EXISTS idx_cabins_category ON cabins(pack_version_id, category_entity_id);

CREATE TABLE IF NOT EXISTS cabin_features (
    pack_version_id INTEGER NOT NULL,
    cabin_entity_id TEXT NOT NULL,
    feature_code TEXT NOT NULL,
    PRIMARY KEY (pack_version_id, cabin_entity_id, feature_code),
    FOREIGN KEY (pack_version_id, cabin_entity_id) REFERENCES cabins(pack_version_id, entity_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public_areas (
    pack_version_id INTEGER NOT NULL,
    entity_id TEXT NOT NULL,
    ship_entity_id TEXT NOT NULL,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    limitations_json TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    PRIMARY KEY (pack_version_id, entity_id),
    FOREIGN KEY (pack_version_id, entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT,
    FOREIGN KEY (pack_version_id, ship_entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public_area_decks (
    pack_version_id INTEGER NOT NULL,
    public_area_entity_id TEXT NOT NULL,
    deck_entity_id TEXT NOT NULL,
    PRIMARY KEY (pack_version_id, public_area_entity_id, deck_entity_id),
    FOREIGN KEY (pack_version_id, public_area_entity_id) REFERENCES public_areas(pack_version_id, entity_id) ON DELETE RESTRICT,
    FOREIGN KEY (pack_version_id, deck_entity_id) REFERENCES decks(pack_version_id, entity_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS relationships (
    pack_version_id INTEGER NOT NULL,
    relationship_id TEXT NOT NULL,
    source_entity_id TEXT NOT NULL,
    target_entity_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    evidence_kind TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    derivation_rule TEXT,
    limitation TEXT,
    PRIMARY KEY (pack_version_id, relationship_id),
    UNIQUE (pack_version_id, source_entity_id, target_entity_id, kind),
    FOREIGN KEY (pack_version_id, source_entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT,
    FOREIGN KEY (pack_version_id, target_entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(pack_version_id, source_entity_id, kind);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(pack_version_id, target_entity_id, kind);

CREATE TABLE IF NOT EXISTS relationship_sources (
    pack_version_id INTEGER NOT NULL,
    relationship_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    PRIMARY KEY (pack_version_id, relationship_id, source_id),
    FOREIGN KEY (pack_version_id, relationship_id) REFERENCES relationships(pack_version_id, relationship_id) ON DELETE RESTRICT,
    FOREIGN KEY (pack_version_id, source_id) REFERENCES sources(pack_version_id, source_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS claims (
    pack_version_id INTEGER NOT NULL,
    claim_id TEXT NOT NULL,
    subject_entity_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    statement TEXT NOT NULL,
    value_json TEXT NOT NULL,
    unit TEXT,
    evidence_kind TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    derivation_rule TEXT,
    limitation TEXT,
    PRIMARY KEY (pack_version_id, claim_id),
    FOREIGN KEY (pack_version_id, subject_entity_id) REFERENCES entities(pack_version_id, entity_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_claims_subject ON claims(pack_version_id, subject_entity_id, predicate);

CREATE TABLE IF NOT EXISTS claim_sources (
    pack_version_id INTEGER NOT NULL,
    claim_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    PRIMARY KEY (pack_version_id, claim_id, source_id),
    FOREIGN KEY (pack_version_id, claim_id) REFERENCES claims(pack_version_id, claim_id) ON DELETE RESTRICT,
    FOREIGN KEY (pack_version_id, source_id) REFERENCES sources(pack_version_id, source_id) ON DELETE RESTRICT
);
"""


class KnowledgePackRepository:
    """Persist and query immutable knowledge pack projections."""

    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as connection, connection:
            connection.executescript(SCHEMA_SQL)
            existing = connection.execute(
                "SELECT value FROM schema_metadata WHERE key = 'schema_version'"
            ).fetchone()
            if existing is not None and int(existing["value"]) != SCHEMA_VERSION:
                raise PersistenceConflictError("database schema version is not supported")
            connection.execute(
                "INSERT OR IGNORE INTO schema_metadata(key, value) VALUES ('schema_version', ?)",
                (str(SCHEMA_VERSION),),
            )

    def import_path(self, path: Path | str) -> ImportResult:
        source_path = Path(path).resolve()
        pack = load_pack(source_path)
        digest = hashlib.sha256(canonical_json_bytes(source_path)).hexdigest()
        self.initialize()
        with closing(self.connect()) as connection, connection:
            existing = connection.execute(
                "SELECT pack_version_id, content_sha256 FROM knowledge_pack_versions WHERE pack_id = ? AND version = ?",
                (pack.pack_id, pack.version),
            ).fetchone()
            if existing is not None:
                if existing["content_sha256"] != digest:
                    raise PersistenceConflictError(
                        f"immutable pack {pack.pack_id}@{pack.version} already exists with different content"
                    )
                return ImportResult(existing["pack_version_id"], pack.pack_id, pack.version, digest, False)
            pack_version_id = self._insert_pack(connection, pack, source_path, digest)
            return ImportResult(pack_version_id, pack.pack_id, pack.version, digest, True)

    def _insert_pack(
        self,
        connection: sqlite3.Connection,
        pack: KnowledgePack,
        source_path: Path,
        digest: str,
    ) -> int:
        cursor = connection.execute(
            """INSERT INTO knowledge_pack_versions(
                pack_id, version, schema_version, effective_date, status, ship_entity_id,
                limitations_json, content_sha256, source_path, imported_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                pack.pack_id, pack.version, pack.schema_version, pack.effective_date, pack.status,
                pack.ship.entity_id, _json(pack.limitations), digest, str(source_path),
                datetime.now(UTC).isoformat(),
            ),
        )
        pack_version_id = int(cursor.lastrowid)
        for source in pack.sources:
            connection.execute(
                "INSERT INTO sources VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    pack_version_id, source.source_id, source.title, source.publisher, source.url,
                    source.accessed_at, source.source_type, source.published_at, _json(source.limitations),
                ),
            )
        for entity in pack.entities():
            entity_type = _entity_type(entity)
            connection.execute("INSERT INTO entities VALUES (?, ?, ?)", (pack_version_id, entity.entity_id, entity_type))
            for source_id in entity.source_ids:
                connection.execute("INSERT INTO entity_sources VALUES (?, ?, ?)", (pack_version_id, entity.entity_id, source_id))
        self._insert_entities(connection, pack_version_id, pack)
        for relationship in pack.relationships:
            connection.execute(
                "INSERT INTO relationships VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    pack_version_id, relationship.relationship_id, relationship.source_entity_id,
                    relationship.target_entity_id, relationship.kind.value, relationship.evidence_kind.value,
                    relationship.source_locator, relationship.derivation_rule, relationship.limitation,
                ),
            )
            for source_id in relationship.source_ids:
                connection.execute(
                    "INSERT INTO relationship_sources VALUES (?, ?, ?)",
                    (pack_version_id, relationship.relationship_id, source_id),
                )
        for claim in pack.claims:
            connection.execute(
                "INSERT INTO claims VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    pack_version_id, claim.claim_id, claim.subject_entity_id, claim.predicate, claim.statement,
                    _json(claim.value), claim.unit, claim.evidence_kind.value, claim.source_locator,
                    claim.derivation_rule, claim.limitation,
                ),
            )
            for source_id in claim.source_ids:
                connection.execute("INSERT INTO claim_sources VALUES (?, ?, ?)", (pack_version_id, claim.claim_id, source_id))
        return pack_version_id

    def _insert_entities(self, connection: sqlite3.Connection, pack_version_id: int, pack: KnowledgePack) -> None:
        ship = pack.ship
        connection.execute(
            "INSERT INTO ships VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                pack_version_id, ship.entity_id, ship.name, ship.operator_name,
                ship.cabin_count, ship.guest_capacity, ship.source_locator,
            ),
        )
        for deck in pack.decks:
            connection.execute(
                "INSERT INTO decks VALUES (?, ?, ?, ?, ?, ?, ?)",
                (pack_version_id, deck.entity_id, deck.ship_id, deck.number, deck.name, deck.ordinal, deck.source_locator),
            )
        deck_ids_by_number = {deck.number: deck.entity_id for deck in pack.decks}
        for category in pack.cabin_categories:
            connection.execute(
                "INSERT INTO cabin_categories VALUES (?, ?, ?, ?, ?, ?)",
                (
                    pack_version_id, category.entity_id, category.code, category.name,
                    category.accommodation_type.value, category.source_locator,
                ),
            )
            for deck_number in category.deck_numbers:
                connection.execute(
                    "INSERT INTO cabin_category_decks VALUES (?, ?, ?)",
                    (pack_version_id, category.entity_id, deck_ids_by_number[deck_number]),
                )
        for cabin in pack.cabins:
            connection.execute(
                "INSERT INTO cabins VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    pack_version_id, cabin.entity_id, cabin.ship_id, cabin.deck_id, cabin.number,
                    cabin.category_id, _json(cabin.limitations), cabin.source_locator,
                ),
            )
            for feature_code in cabin.feature_codes:
                connection.execute(
                    "INSERT INTO cabin_features VALUES (?, ?, ?)",
                    (pack_version_id, cabin.entity_id, feature_code),
                )
        for area in pack.public_areas:
            connection.execute(
                "INSERT INTO public_areas VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    pack_version_id, area.entity_id, area.ship_id, area.name, area.kind.value,
                    _json(area.limitations), area.source_locator,
                ),
            )
            for deck_id in area.deck_ids:
                connection.execute("INSERT INTO public_area_decks VALUES (?, ?, ?)", (pack_version_id, area.entity_id, deck_id))

    def summary(self, pack_id: str, version: str) -> dict[str, int | str]:
        with closing(self.connect()) as connection:
            row = connection.execute(
                "SELECT pack_version_id, ship_entity_id FROM knowledge_pack_versions WHERE pack_id = ? AND version = ?",
                (pack_id, version),
            ).fetchone()
            if row is None:
                raise KeyError(f"unknown pack {pack_id}@{version}")
            pack_version_id = row["pack_version_id"]
            counts = {
                table: connection.execute(
                    f"SELECT COUNT(*) AS count FROM {table} WHERE pack_version_id = ?",  # noqa: S608 - fixed table names
                    (pack_version_id,),
                ).fetchone()["count"]
                for table in ("decks", "cabin_categories", "cabins", "public_areas", "relationships", "claims", "sources")
            }
            return {"pack_version_id": pack_version_id, "ship_entity_id": row["ship_entity_id"], **counts}

    def provenance_for(self, pack_id: str, version: str, entity_id: str) -> tuple[sqlite3.Row, ...]:
        with closing(self.connect()) as connection:
            return tuple(connection.execute(
                """SELECT s.* FROM sources s
                JOIN entity_sources es ON es.pack_version_id = s.pack_version_id AND es.source_id = s.source_id
                JOIN knowledge_pack_versions p ON p.pack_version_id = s.pack_version_id
                WHERE p.pack_id = ? AND p.version = ? AND es.entity_id = ?
                ORDER BY s.source_id""",
                (pack_id, version, entity_id),
            ).fetchall())


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _entity_type(entity: Ship | Deck | CabinCategory | Cabin | PublicArea) -> str:
    if isinstance(entity, Ship):
        return "ship"
    if isinstance(entity, Deck):
        return "deck"
    if isinstance(entity, CabinCategory):
        return "cabin_category"
    if isinstance(entity, Cabin):
        return "cabin"
    return "public_area"
