"""
src/timonelo/harvester/vessel_resolver.py

Deterministic vessel name and slug resolution for MSC Cruises fleet.
"""

import re
from typing import Optional, Dict, List, Tuple

MSC_VESSEL_CANONICAL_MAP: Dict[str, Dict[str, Any]] = {
    "msc-meraviglia": {
        "canonical_name": "MSC Meraviglia",
        "aliases": ["meraviglia", "msc meraviglia", "msc_meraviglia", "mscmeraviglia", "msc-meraviglia"]
    },
    "msc-bellissima": {
        "canonical_name": "MSC Bellissima",
        "aliases": ["bellissima", "msc bellissima", "msc_bellissima", "mscbellissima", "msc-bellissima"]
    },
    "msc-grandiosa": {
        "canonical_name": "MSC Grandiosa",
        "aliases": ["grandiosa", "msc grandiosa", "msc_grandiosa", "mscgrandiosa", "msc-grandiosa"]
    },
    "msc-virtuosa": {
        "canonical_name": "MSC Virtuosa",
        "aliases": ["virtuosa", "msc virtuosa", "msc_virtuosa", "mscvirtuosa", "msc-virtuosa"]
    },
    "msc-euribia": {
        "canonical_name": "MSC Euribia",
        "aliases": ["euribia", "msc euribia", "msc_euribia", "msceuribia", "msc-euribia"]
    },
    "msc-seaside": {
        "canonical_name": "MSC Seaside",
        "aliases": ["seaside", "msc seaside", "msc_seaside", "mscseaside", "msc-seaside"]
    },
    "msc-seaview": {
        "canonical_name": "MSC Seaview",
        "aliases": ["seaview", "msc seaview", "msc_seaview", "mscseaview", "msc-seaview"]
    },
    "msc-seashore": {
        "canonical_name": "MSC Seashore",
        "aliases": ["seashore", "msc seashore", "msc_seashore", "mscseashore", "msc-seashore"]
    },
    "msc-seascape": {
        "canonical_name": "MSC Seascape",
        "aliases": ["seascape", "msc seascape", "msc_seascape", "mscseascape", "msc-seascape"]
    },
    "msc-world-europa": {
        "canonical_name": "MSC World Europa",
        "aliases": ["world europa", "world-europa", "world_europa", "msc world europa", "msc-world-europa"]
    },
    "msc-world-america": {
        "canonical_name": "MSC World America",
        "aliases": ["world america", "world-america", "world_america", "msc world america", "msc-world-america"]
    }
}


def normalize_string(text: str) -> str:
    """Normalizes string for matching."""
    text = text.lower().strip()
    text = re.sub(r"[_\-\s]+", " ", text)
    return text


def resolve_vessel(
    text: str,
    url: Optional[str] = None,
    filename: Optional[str] = None
) -> Tuple[Optional[str], str]:
    """
    Deterministically resolves a vessel_id from text cues, URL, or filename.
    Returns: (vessel_id, resolution_status)
    resolution_status: "RESOLVED" | "VESSEL_UNRESOLVED" | "MANUAL_REVIEW_REQUIRED"
    """
    search_corpus = f"{text} {url or ''} {filename or ''}"
    norm_corpus = normalize_string(search_corpus)

    matched_vessels: List[str] = []

    for vid, vdata in MSC_VESSEL_CANONICAL_MAP.items():
        for alias in vdata["aliases"]:
            # Use word-boundary or distinct token search
            pattern = r"\b" + re.escape(alias.replace(" ", "[\\s_\\-]")) + r"\b"
            if re.search(pattern, norm_corpus) or alias in norm_corpus:
                if vid not in matched_vessels:
                    matched_vessels.append(vid)
                break

    if len(matched_vessels) == 1:
        return matched_vessels[0], "RESOLVED"
    elif len(matched_vessels) > 1:
        return None, "MANUAL_REVIEW_REQUIRED"
    else:
        return None, "VESSEL_UNRESOLVED"
