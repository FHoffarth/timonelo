from __future__ import annotations
import re
from typing import Dict, Any, List, Tuple, Set, Optional


class IngestionValidator:
    """Rigorous gatekeeper validating candidate entities."""

    @classmethod
    def validate_ship(cls, ship: Dict[str, Any], existing_imos: Set[str] = None) -> List[str]:
        errors: List[str] = []
        slug = ship.get("slug", "unknown-ship")

        # 1. IMO / ENI validation
        imo_entry = ship.get("imo")
        imo_val = imo_entry.get("value") if isinstance(imo_entry, dict) else imo_entry
        if not imo_val:
            errors.append(f"Ship '{slug}' is missing statutory IMO / ENI identifier.")
        else:
            clean_imo = re.sub(r"[^0-9]", "", str(imo_val))
            if len(clean_imo) not in (7, 8):
                errors.append(f"Ship '{slug}' has invalid IMO/ENI format: '{imo_val}' (must be 7 or 8 digits).")
            elif existing_imos and clean_imo in existing_imos:
                errors.append(f"Duplicate IMO collision: '{clean_imo}' already exists in verified database.")

        # 2. Dimensions physical plausibility check
        dims = ship.get("dimensions", {})
        length = cls._extract_val(dims.get("length_m"))
        beam = cls._extract_val(dims.get("beam_m"))
        draft = cls._extract_val(dims.get("draft_m"))
        gt = cls._extract_val(dims.get("gross_tonnage"))

        if length and beam and length <= beam:
            errors.append(f"Ship '{slug}' has physically impossible dimensions: Length ({length}m) <= Beam ({beam}m).")
        if draft and beam and draft >= beam:
            errors.append(f"Ship '{slug}' has impossible draft: Draft ({draft}m) >= Beam ({beam}m).")
        if gt and gt <= 0:
            errors.append(f"Ship '{slug}' has invalid Gross Tonnage: {gt}.")

        return errors

    @classmethod
    def validate_port(cls, port: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        slug = port.get("slug", "unknown-port")

        # 1. UN/LOCODE check
        locode = port.get("un_locode", "")
        if locode and not re.match(r"^[A-Z]{2}[A-Z0-9]{3}$", locode):
            errors.append(f"Port '{slug}' has invalid UN/LOCODE: '{locode}' (must be 5 alphanumeric characters).")

        # 2. Coordinates bounding check
        coords = port.get("coordinates", {})
        lat = coords.get("latitude")
        lon = coords.get("longitude")
        if lat is not None and (lat < -90.0 or lat > 90.0):
            errors.append(f"Port '{slug}' has latitude out of bounds [-90, +90]: {lat}.")
        if lon is not None and (lon < -180.0 or lon > 180.0):
            errors.append(f"Port '{slug}' has longitude out of bounds [-180, +180]: {lon}.")

        return errors

    @staticmethod
    def _extract_val(entry: Any) -> Optional[float]:
        if isinstance(entry, dict):
            v = entry.get("value")
            return float(v) if v is not None else None
        return float(entry) if entry is not None else None
