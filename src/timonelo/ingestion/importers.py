"""
Concrete Maritime Importers for Official and Public Sources.
"""

from __future__ import annotations
import hashlib
import json
import datetime
from typing import Dict, Any, List
from .base_importer import BaseImporter, RawPayload, SourceCategory


class OfficialCruiseLineImporter(BaseImporter):
    """Imports official cruise line technical fact sheets and general arrangements."""

    def __init__(self, source_id: str, operator_name: str):
        super().__init__(
            source_id=source_id,
            source_name=f"{operator_name} Official Fact Sheet Importer",
            category=SourceCategory.OFFICIAL_CRUISE_LINE,
            license_note="Public Informational & Promotional Specification",
        )

    def ingest_payload(self, raw_data: Dict[str, Any], source_url: str, confidence: float = 1.0) -> RawPayload:
        payload_str = json.dumps(raw_data, sort_keys=True)
        checksum = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return RawPayload(
            source_id=self.source_id,
            source_name=self.source_name,
            category=self.category,
            source_url=source_url,
            license_note=self.license_note,
            retrieval_timestamp=now,
            confidence=confidence,
            payload=raw_data,
            sha256_checksum=checksum,
        )

    def extract_entities(self, payload: RawPayload) -> Dict[str, List[Dict[str, Any]]]:
        p = payload.payload
        ship_entity = {
            "slug": p.get("slug"),
            "name": p.get("name"),
            "imo": p.get("imo"),
            "operator": p.get("operator"),
            "ship_class": p.get("ship_class"),
            "gross_tonnage": p.get("gross_tonnage"),
            "length_m": p.get("length_m"),
            "beam_m": p.get("beam_m"),
            "total_decks": p.get("total_decks"),
            "cabin_count": p.get("cabin_count"),
            "passenger_capacity": p.get("passenger_capacity"),
            "builder": p.get("builder"),
            "build_year": p.get("build_year"),
            "signature_venues": p.get("signature_venues", []),
            "homeports": p.get("homeports", []),
            "source_provenance": {
                "source_id": payload.source_id,
                "url": payload.source_url,
                "sha256": payload.sha256_checksum,
                "confidence": payload.confidence,
            },
        }
        return {"ships": [ship_entity]}


class MaritimeIMOImporter(BaseImporter):
    """Imports statutory maritime data from IMO / GISIS / Class Society registries."""

    def __init__(self, source_id: str = "src:imo-gisis"):
        super().__init__(
            source_id=source_id,
            source_name="IMO GISIS Statutory Vessel Register",
            category=SourceCategory.OFFICIAL_MARITIME_REGULATOR,
            license_note="Public Maritime Safety & Identity Record",
        )

    def ingest_payload(self, raw_data: Dict[str, Any], source_url: str, confidence: float = 1.0) -> RawPayload:
        payload_str = json.dumps(raw_data, sort_keys=True)
        checksum = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return RawPayload(
            source_id=self.source_id,
            source_name=self.source_name,
            category=self.category,
            source_url=source_url,
            license_note=self.license_note,
            retrieval_timestamp=now,
            confidence=confidence,
            payload=raw_data,
            sha256_checksum=checksum,
        )

    def extract_entities(self, payload: RawPayload) -> Dict[str, List[Dict[str, Any]]]:
        p = payload.payload
        return {
            "statutory_records": [
                {
                    "imo": p.get("imo"),
                    "mmsi": p.get("mmsi"),
                    "call_sign": p.get("call_sign"),
                    "flag_state": p.get("flag_state"),
                    "registered_owner": p.get("registered_owner"),
                    "source_id": payload.source_id,
                }
            ]
        }


class PortAuthorityImporter(BaseImporter):
    """Imports passenger cruise terminal specifications from official Port Authorities."""

    def __init__(self, source_id: str, port_name: str):
        super().__init__(
            source_id=source_id,
            source_name=f"{port_name} Authority Importer",
            category=SourceCategory.OFFICIAL_PORT_AUTHORITY,
            license_note="Public Port Navigation & Passenger Terminal Schedule",
        )

    def ingest_payload(self, raw_data: Dict[str, Any], source_url: str, confidence: float = 1.0) -> RawPayload:
        payload_str = json.dumps(raw_data, sort_keys=True)
        checksum = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return RawPayload(
            source_id=self.source_id,
            source_name=self.source_name,
            category=self.category,
            source_url=source_url,
            license_note=self.license_note,
            retrieval_timestamp=now,
            confidence=confidence,
            payload=raw_data,
            sha256_checksum=checksum,
        )

    def extract_entities(self, payload: RawPayload) -> Dict[str, List[Dict[str, Any]]]:
        p = payload.payload
        port_entity = {
            "slug": p.get("slug"),
            "name": p.get("name"),
            "un_locode": p.get("un_locode"),
            "country": p.get("country"),
            "region": p.get("region"),
            "coordinates": p.get("coordinates", {}),
            "terminals": p.get("terminals", []),
            "logistics": p.get("logistics", {}),
            "negative_intelligence": p.get("negative_intelligence", []),
            "source_id": payload.source_id,
        }
        return {"ports": [port_entity]}
