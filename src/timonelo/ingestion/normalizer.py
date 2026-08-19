"""
Data Normalizer and Entity Provenance Engine.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import datetime

from timonelo.database.schema import TrustLevel


class DataNormalizer:
    """Normalizes heterogeneous imported dictionaries into canonical Timonelo entity structures."""

    @staticmethod
    def normalize_ship(raw_ship: Dict[str, Any], source_id: str, confidence: float = 1.0) -> Dict[str, Any]:
        slug = str(raw_ship.get("slug", "")).strip().lower()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        trust_level = raw_ship.get("trust_level", TrustLevel.UNKNOWN.value)

        def prov(val: Any) -> Dict[str, Any]:
            return {
                "value": val,
                "trust_level": trust_level,
                "source_id": source_id,
                "confidence": confidence,
                "retrieved_at": now,
            }

        return {
            "slug": slug,
            "name": prov(raw_ship.get("name")),
            "imo": prov(str(raw_ship.get("imo", "")).replace("IMO", "").strip()),
            "mmsi": prov(str(raw_ship.get("mmsi", "")).strip()) if raw_ship.get("mmsi") else None,
            "call_sign": prov(raw_ship.get("call_sign")) if raw_ship.get("call_sign") else None,
            "flag_state": prov(raw_ship.get("flag_state", "Unknown")),
            "operator": prov(raw_ship.get("operator")),
            "ship_class": prov(raw_ship.get("ship_class")),
            "class_id": raw_ship.get("class_id", slug),
            "builder": prov(raw_ship.get("builder", "Unknown")),
            "delivery_date": prov(raw_ship.get("delivery_date", f"{raw_ship.get('build_year', 2020)}-01-01")),
            "dimensions": {
                "length_m": prov(float(raw_ship.get("length_m", 0.0))),
                "beam_m": prov(float(raw_ship.get("beam_m", 0.0))),
                "draft_m": prov(float(raw_ship.get("draft_m", 8.0))),
                "gross_tonnage": prov(int(raw_ship.get("gross_tonnage", 0))),
            },
            "capacities": {
                "passenger_max": prov(int(raw_ship.get("passenger_capacity", raw_ship.get("passenger_max", 0)))),
                "passenger_double_occ": prov(int(raw_ship.get("passenger_double_occ", 0))),
                "crew": prov(int(raw_ship.get("crew", 0))),
                "total_staterooms": prov(int(raw_ship.get("cabin_count", raw_ship.get("total_staterooms", 0)))),
                "accessible_staterooms": prov(int(raw_ship.get("accessible_staterooms", 0))),
            },
            "signature_venues": raw_ship.get("signature_venues", []),
            "homeports": raw_ship.get("homeports", []),
        }

    @staticmethod
    def normalize_port(raw_port: Dict[str, Any], source_id: str, confidence: float = 1.0) -> Dict[str, Any]:
        slug = str(raw_port.get("slug", "")).strip().lower()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        trust_level = raw_port.get("trust_level", TrustLevel.UNKNOWN.value)

        return {
            "slug": slug,
            "name": raw_port.get("name", slug.title()),
            "un_locode": str(raw_port.get("un_locode", "")).upper(),
            "country": raw_port.get("country", "Unknown"),
            "region": raw_port.get("region", "Global"),
            "coordinates": {
                "latitude": float(raw_port.get("coordinates", {}).get("latitude", 0.0)),
                "longitude": float(raw_port.get("coordinates", {}).get("longitude", 0.0)),
            },
            "timezone": raw_port.get("timezone", "UTC"),
            "terminals": raw_port.get("terminals", []),
            "logistics": raw_port.get("logistics", {}),
            "negative_intelligence": raw_port.get("negative_intelligence", []),
            "sources": [
                {
                    "field": "all",
                    "source_id": source_id,
                    "trust_level": trust_level,
                    "retrieved_at": now,
                }
            ],
        }
