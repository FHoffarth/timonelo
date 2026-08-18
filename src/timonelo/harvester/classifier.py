"""
src/timonelo/harvester/classifier.py

Deterministic document classification and metadata extraction for Deck Plans.
"""

import re
from typing import Tuple, Optional, Dict, Any
from timonelo.harvester.models import DocumentType


DECK_PLAN_KEYWORDS = [
    r"deck\s*plan",
    r"deckplans?",
    r"deckpl[äa]ne",
    r"deck-plan",
    r"deck_plan",
    r"piani\s*nave",
    r"plans?\s*des\s*ponts?",
    r"plano\s*de\s*cubiertas?"
]


def classify_document(
    first_page_text: str,
    filename: Optional[str] = None,
    url: Optional[str] = None,
    pdf_title: Optional[str] = None
) -> Tuple[DocumentType, Dict[str, Any]]:
    """
    Classifies a document deterministically as DECK_PLAN or UNKNOWN.
    Extracts title, detected language, and edition date if present.
    """
    corpus = f"{first_page_text} {filename or ''} {url or ''} {pdf_title or ''}".lower()
    
    is_deck_plan = False
    for kw in DECK_PLAN_KEYWORDS:
        if re.search(kw, corpus):
            is_deck_plan = True
            break
            
    doc_type = DocumentType.DECK_PLAN if is_deck_plan else DocumentType.UNKNOWN
    
    # Language detection
    detected_lang = "unknown"
    if any(term in corpus for term in ["deckpläne", "_ger", ".deu", "deu", "de-de", "kabinen", "gäste"]):
        detected_lang = "de"
    elif any(term in corpus for term in ["deck plan", "_eng", ".eng", "en-gl", "en-us", "staterooms", "guests"]):
        detected_lang = "en"
    elif any(term in corpus for term in ["piani nave", "_ita", ".ita", "it-it", "cabine", "ospiti"]):
        detected_lang = "it"
    elif any(term in corpus for term in ["plans des ponts", "_fra", ".fra", "fr-fr", "passagers"]):
        detected_lang = "fr"

    # Edition detection (e.g. 11.2025, 11/2025, 2025-11, 2025/2026)
    edition = None
    edition_match = re.search(r"\b(0[1-9]|1[0-2])[\./](202[0-9])\b", corpus)
    if edition_match:
        edition = f"{edition_match.group(1)}.{edition_match.group(2)}"
    else:
        year_match = re.search(r"\b(202[0-9])\b", corpus)
        if year_match:
            edition = year_match.group(1)

    # Title extraction
    title = pdf_title or "MSC Deck Plan"
    if "deckpläne" in corpus or "deckplane" in corpus:
        title = "MSC Meraviglia Deckpläne" if "meraviglia" in corpus else "MSC Deckpläne"
    elif "deck plan" in corpus:
        title = "MSC Meraviglia Deck Plan" if "meraviglia" in corpus else "MSC Deck Plan"

    extracted_meta = {
        "title": title,
        "language": detected_lang,
        "edition": edition
    }

    return doc_type, extracted_meta
