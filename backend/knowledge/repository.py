import os
import json
from typing import Any, Optional
import jsonschema

from .exceptions import (
    KnowledgeRepositoryError,
    ShipNotFoundError,
    DeckNotFoundError,
    DomainNotFoundError,
    SchemaValidationError,
)

# Standard schema mapping per domain file
DOMAIN_SCHEMA_MAP = {
    "technical.json": "ship.schema.json",
    "decks.json": "deck.schema.json",
    "public_areas.json": "venue.schema.json",
    "restaurants.json": "restaurant.schema.json",
    "bars.json": "bar.schema.json",
    "lounges.json": "lounge.schema.json",
    "pools.json": "pool.schema.json",
    "spa.json": "spa.schema.json",
    "sports.json": "sport.schema.json",
    "entertainment.json": "entertainment.schema.json",
    "muster.json": "muster.schema.json",
    "kids.json": "venue.schema.json", # Or general venue schema
    "cabins.json": "cabin.schema.json",
}


class KnowledgeRepository:
    """
    Canonical Knowledge Repository for Timonelo.
    
    Provides lazy-loaded, in-memory cached, schema-validated access
    to canonical knowledge assets for cruise vessels.
    """

    def __init__(self, knowledge_root: Optional[str] = None, validate_schemas: bool = True):
        if knowledge_root is None:
            # Look relative to repository root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            knowledge_root = os.path.join(base_dir, "knowledge")

        self.knowledge_root = knowledge_root
        self.ships_dir = os.path.join(self.knowledge_root, "ships")
        self.schema_dir = os.path.join(self.knowledge_root, "schema")
        self.validate_schemas = validate_schemas

        # In-memory document and schema cache: (ship_id, domain_file) -> parsed JSON dict
        self._doc_cache: dict[tuple[str, str], dict[str, Any]] = {}
        self._schema_cache: dict[str, dict[str, Any]] = {}

    def clear_cache(self) -> None:
        """Clear the in-memory cache."""
        self._doc_cache.clear()
        self._schema_cache.clear()

    def _load_schema(self, schema_filename: str) -> dict[str, Any]:
        if schema_filename in self._schema_cache:
            return self._schema_cache[schema_filename]

        schema_path = os.path.join(self.schema_dir, schema_filename)
        if not os.path.exists(schema_path):
            raise KnowledgeRepositoryError(f"Schema file '{schema_filename}' not found at {schema_path}")

        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
                self._schema_cache[schema_filename] = schema
                return schema
        except Exception as e:
            raise KnowledgeRepositoryError(f"Failed to load schema '{schema_filename}': {e}") from e

    def _load_and_validate(self, ship_id: str, domain_file: str) -> dict[str, Any]:
        cache_key = (ship_id, domain_file)
        if cache_key in self._doc_cache:
            return self._doc_cache[cache_key]

        ship_dir = os.path.join(self.ships_dir, ship_id)
        if not os.path.exists(ship_dir):
            raise ShipNotFoundError(ship_id)

        doc_path = os.path.join(ship_dir, domain_file)
        if not os.path.exists(doc_path):
            raise DomainNotFoundError(ship_id, domain_file)

        try:
            with open(doc_path, "r", encoding="utf-8") as f:
                doc_data = json.load(f)
        except Exception as e:
            raise KnowledgeRepositoryError(f"Failed to parse JSON for '{ship_id}/{domain_file}': {e}") from e

        # Validate against JSON Schema Draft 2020-12
        if self.validate_schemas:
            schema_file = DOMAIN_SCHEMA_MAP.get(domain_file)
            if schema_file and os.path.exists(os.path.join(self.schema_dir, schema_file)):
                schema = self._load_schema(schema_file)
                validator_cls = jsonschema.validators.validator_for(schema)
                validator = validator_cls(schema)
                errors = [f"Path {list(err.path)}: {err.message}" for err in validator.iter_errors(doc_data)]
                if errors:
                    raise SchemaValidationError(f"{ship_id}/{domain_file}", errors)

        self._doc_cache[cache_key] = doc_data
        return doc_data

    # -------------------------------------------------------------------------
    # Canonical Knowledge Access Methods
    # -------------------------------------------------------------------------

    def getShip(self, shipId: str) -> dict[str, Any]:
        """Retrieve complete technical specifications and metadata for a vessel."""
        return self._load_and_validate(shipId, "technical.json")

    get_ship = getShip

    def getDecks(self, shipId: str) -> list[dict[str, Any]]:
        """Retrieve all decks for a vessel."""
        data = self._load_and_validate(shipId, "decks.json")
        return data.get("decks", [])

    get_decks = getDecks

    def getDeck(self, shipId: str, deck: int | str) -> dict[str, Any]:
        """Retrieve a specific deck by number or name."""
        decks = self.getDecks(shipId)
        
        target_num = None
        if isinstance(deck, int) or (isinstance(deck, str) and deck.isdigit()):
            target_num = int(deck)

        for d in decks:
            if target_num is not None and d.get("deck_number") == target_num:
                return d
            if isinstance(deck, str):
                d_id = str(d.get("id", "")).lower()
                d_name = str(d.get("name", "")).lower()
                if deck.lower() in [d_id, d_name, f"deck-{deck.lower()}", f"deck {deck.lower()}"]:
                    return d

        raise DeckNotFoundError(shipId, deck)

    get_deck = getDeck

    def getRestaurants(self, shipId: str) -> list[dict[str, Any]]:
        """Retrieve all restaurants and dining venues for a vessel."""
        data = self._load_and_validate(shipId, "restaurants.json")
        return data.get("restaurants", [])

    get_restaurants = getRestaurants

    def getBars(self, shipId: str) -> list[dict[str, Any]]:
        """Retrieve all bars and beverage venues for a vessel."""
        data = self._load_and_validate(shipId, "bars.json")
        return data.get("bars", [])

    get_bars = getBars

    def getLounges(self, shipId: str) -> list[dict[str, Any]]:
        """Retrieve all lounges and observation salons for a vessel."""
        data = self._load_and_validate(shipId, "lounges.json")
        return data.get("lounges", [])

    get_lounges = getLounges

    def getPools(self, shipId: str) -> list[dict[str, Any]]:
        """Retrieve all pools, magrodome areas, and whirlpool networks."""
        data = self._load_and_validate(shipId, "pools.json")
        return data.get("pools_and_water_areas", [])

    get_pools = getPools

    def getSpa(self, shipId: str) -> dict[str, Any]:
        """Retrieve the spa complex, thermal suite, and salon catalog."""
        data = self._load_and_validate(shipId, "spa.json")
        return data.get("spa_and_wellness", {})

    get_spa = getSpa

    def getEntertainment(self, shipId: str) -> list[dict[str, Any]]:
        """Retrieve entertainment venues, theaters, and casinos."""
        data = self._load_and_validate(shipId, "entertainment.json")
        return data.get("entertainment_venues", [])

    get_entertainment = getEntertainment

    def getSports(self, shipId: str) -> list[dict[str, Any]]:
        """Retrieve sportplex arenas, fitness centers, and arcade attractions."""
        data = self._load_and_validate(shipId, "sports.json")
        return data.get("sports_and_recreation", [])

    get_sports = getSports

    def getCabins(self, shipId: str) -> dict[str, Any]:
        """Retrieve stateroom categories, suite directories, and amenities."""
        return self._load_and_validate(shipId, "cabins.json")

    get_cabins = getCabins

    def getPublicAreas(self, shipId: str) -> list[dict[str, Any]]:
        """Retrieve central promenades, atriums, and public landmarks."""
        data = self._load_and_validate(shipId, "public_areas.json")
        return data.get("public_areas", [])

    get_public_areas = getPublicAreas

    def getMuster(self, shipId: str) -> dict[str, Any]:
        """Retrieve emergency muster protocols and assembly stations."""
        data = self._load_and_validate(shipId, "muster.json")
        return data.get("emergency_and_muster_protocol", {})

    get_muster = getMuster

    def getKids(self, shipId: str) -> list[dict[str, Any]]:
        """Retrieve youth clubs, Chicco nursery, LEGO rooms, and teen lounges."""
        data = self._load_and_validate(shipId, "kids.json")
        return data.get("kids_areas", [])

    get_kids = getKids

    # -------------------------------------------------------------------------
    # Cross-Reference & Relationship Graph Methods
    # -------------------------------------------------------------------------

    def getRelationships(self) -> dict[str, Any]:
        """Retrieve the canonical relationship index."""
        rel_path = os.path.join(self.knowledge_root, "indexes", "relationships.json")
        if not os.path.exists(rel_path):
            raise KnowledgeRepositoryError(f"Relationship index not found at {rel_path}")
        with open(rel_path, "r", encoding="utf-8") as f:
            return json.load(f)

    get_relationships = getRelationships

    def getShipRoutes(self, shipId: str) -> list[str]:
        """Retrieve all canonical route IDs deployed for a vessel."""
        rel = self.getRelationships()
        return rel.get("ships_to_routes", {}).get(shipId, [])

    get_ship_routes = getShipRoutes

    def getRoute(self, routeId: str) -> dict[str, Any]:
        """Retrieve canonical route document by route ID."""
        # Find route folder in knowledge/routes
        routes_dir = os.path.join(self.knowledge_root, "routes")
        for folder in os.listdir(routes_dir):
            r_path = os.path.join(routes_dir, folder, "route.json")
            if os.path.exists(r_path):
                with open(r_path, "r", encoding="utf-8") as f:
                    r_data = json.load(f)
                    if r_data.get("route_id") == routeId or folder == routeId:
                        return r_data
        raise KnowledgeRepositoryError(f"Route '{routeId}' not found in knowledge repository.")

    get_route = getRoute

    def getRoutePorts(self, routeId: str) -> list[str]:
        """Retrieve UN/LOCODE canonical port IDs referenced in a route."""
        rel = self.getRelationships()
        return rel.get("routes_to_ports", {}).get(routeId, [])

    get_route_ports = getRoutePorts

    def getPortTerminals(self, portIdOrUnlocode: str) -> list[str]:
        """Retrieve canonical terminal IDs for a port by slug or UN/LOCODE."""
        rel = self.getRelationships()
        unlocode = rel.get("port_slug_to_unlocode", {}).get(portIdOrUnlocode, portIdOrUnlocode)
        return rel.get("ports_to_terminals", {}).get(unlocode, [])

    get_port_terminals = getPortTerminals
