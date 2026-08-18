class KnowledgeRepositoryError(Exception):
    """Base exception for all Knowledge Repository operations."""
    pass


class ShipNotFoundError(KnowledgeRepositoryError):
    """Raised when a requested ship ID does not exist in the knowledge store."""
    def __init__(self, ship_id: str):
        super().__init__(f"Ship '{ship_id}' not found in canonical knowledge repository.")
        self.ship_id = ship_id


class DeckNotFoundError(KnowledgeRepositoryError):
    """Raised when a requested deck number does not exist on the vessel."""
    def __init__(self, ship_id: str, deck: int | str):
        super().__init__(f"Deck '{deck}' not found on vessel '{ship_id}'.")
        self.ship_id = ship_id
        self.deck = deck


class DomainNotFoundError(KnowledgeRepositoryError):
    """Raised when a specific domain dataset (e.g. spa, restaurants) does not exist."""
    def __init__(self, ship_id: str, domain: str):
        super().__init__(f"Domain resource '{domain}' not found for vessel '{ship_id}'.")
        self.ship_id = ship_id
        self.domain = domain


class SchemaValidationError(KnowledgeRepositoryError):
    """Raised when a knowledge JSON file violates its canonical JSON Schema."""
    def __init__(self, resource_name: str, errors: list[str]):
        err_str = "; ".join(errors)
        super().__init__(f"Schema validation failed for '{resource_name}': {err_str}")
        self.resource_name = resource_name
        self.errors = errors
