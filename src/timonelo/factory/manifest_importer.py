"""
Knowledge Factory Stage 01/02: Cabin Manifest & Evidence Importer.
Normalizes raw stateroom manifests into verified CabinManifestRecord objects.
"""

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from timonelo.ontology.models import HullSide, BalconyType


@dataclass(frozen=True)
class CabinManifestRecord:
    cabin_number: str
    deck_number: int
    hull_side: HullSide
    category_code: str
    square_meters: float
    balcony_type: BalconyType
    connecting_cabin: Optional[str]
    is_accessible: bool
    door_clear_width_mm: int
    bed_near_balcony: Optional[bool]
    eu_sockets: int
    us_sockets: int
    usb_a_sockets: int
    usb_c_sockets: int
    bedside_usb: bool
    station_x_fraction: float  # Longitudinal coordinate along ship length (0.0=stern, 1.0=bow)


class ManifestImporter:
    """Automated parser and validator for vessel stateroom manifests."""

    @staticmethod
    def parse_csv(csv_path: Path) -> List[CabinManifestRecord]:
        """Parses a structured CSV stateroom manifest."""
        records: List[CabinManifestRecord] = []
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rec = ManifestImporter._row_to_record(row)
                records.append(rec)
        return records

    @staticmethod
    def parse_json(json_path: Path) -> List[CabinManifestRecord]:
        """Parses a JSON stateroom manifest array."""
        with open(json_path, mode="r", encoding="utf-8") as f:
            data = json.load(f)
        return [ManifestImporter._dict_to_record(item) for item in data]

    @staticmethod
    def _row_to_record(row: Dict[str, str]) -> CabinManifestRecord:
        cabin_num = str(row["cabin_number"]).strip()
        deck_num = int(row.get("deck_number") or cabin_num[:2])
        
        # Hull side detection: explicit or maritime even=starboard, odd=port
        side_raw = row.get("hull_side", "").upper().strip()
        if side_raw in ("STARBOARD", "STBD", "RIGHT"):
            hull_side = HullSide.STARBOARD
        elif side_raw in ("PORT", "LEFT"):
            hull_side = HullSide.PORT
        else:
            # Naval standard: Even staterooms starboard, odd port
            last_digit = int(cabin_num[-1]) if cabin_num[-1].isdigit() else 0
            hull_side = HullSide.STARBOARD if last_digit % 2 == 0 else HullSide.PORT

        # Balcony type
        b_raw = row.get("balcony_type", "UNOBSTRUCTED").upper().strip()
        if "OBSTRUCT" in b_raw or "LIFEBOAT" in b_raw:
            balcony_type = BalconyType.PARTIAL_OBSTRUCTION_LIFEBOAT
        elif "NO_BALCONY" in b_raw or "INTERIOR" in b_raw or "OCEANVIEW" in b_raw:
            balcony_type = BalconyType.NO_BALCONY
        else:
            balcony_type = BalconyType.UNOBSTRUCTED

        is_acc = str(row.get("is_accessible", "false")).lower() in ("true", "1", "yes")
        door_width = int(row.get("door_clear_width_mm") or (950 if is_acc else 850))

        # Longitudinal estimation if not explicitly given
        station_x = float(row.get("station_x_fraction") or 0.35)

        return CabinManifestRecord(
            cabin_number=cabin_num,
            deck_number=deck_num,
            hull_side=hull_side,
            category_code=str(row.get("category_code", "BA")).strip(),
            square_meters=float(row.get("square_meters", 19.0)),
            balcony_type=balcony_type,
            connecting_cabin=str(row["connecting_cabin"]).strip() if row.get("connecting_cabin") else None,
            is_accessible=is_acc,
            door_clear_width_mm=door_width,
            bed_near_balcony=True if str(row.get("bed_near_balcony", "")).lower() == "true" else False,
            eu_sockets=int(row.get("eu_sockets", 2)),
            us_sockets=int(row.get("us_sockets", 2)),
            usb_a_sockets=int(row.get("usb_a_sockets", 2)),
            usb_c_sockets=int(row.get("usb_c_sockets", 1)),
            bedside_usb=True if str(row.get("bedside_usb", "true")).lower() == "true" else False,
            station_x_fraction=station_x,
        )

    @staticmethod
    def _dict_to_record(item: Dict) -> CabinManifestRecord:
        return ManifestImporter._row_to_record({k: str(v) for k, v in item.items()})
