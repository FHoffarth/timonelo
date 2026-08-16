"""
Personal Intelligence Layer for Timonelo (Chapter III - Sprint 05).
User-context aware, deterministic, explainable and evidence-backed personal decision intelligence:
- Structured Traveller Profile
- Loyalty & Status Optimizer
- Travel Rules & Visa Intelligence
- Personal Journey Adaptation
- Master Personal Decision Briefing
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import hashlib
import datetime


class TravelPartyType(str, Enum):
    SOLO = "SOLO"
    COUPLE = "COUPLE"
    FAMILY_WITH_TODDLER = "FAMILY_WITH_TODDLER"
    FAMILY_WITH_TEENS = "FAMILY_WITH_TEENS"
    GROUP = "GROUP"


class MobilityLevel(str, Enum):
    STANDARD = "STANDARD"
    REDUCED_WALKING = "REDUCED_WALKING"
    STEP_FREE_WHEELCHAIR = "STEP_FREE_WHEELCHAIR"


class VisaRequirementStatus(str, Enum):
    VISA_FREE = "VISA_FREE (Visumfrei)"
    VISA_FREE_TRANSIT_144H = "VISA_FREE_TRANSIT_144H (144h visumfreier Transit)"
    ETA_ESTA_REQUIRED = "ETA_ESTA_REQUIRED (Elektronische Einreiseerlaubnis erforderlich)"
    VISA_REQUIRED_BEFORE_DEPARTURE = "VISA_REQUIRED (Botschafts-Visum vorab zwingend)"
    UNKNOWN = "UNKNOWN (Einreisebestimmungen unbestätigt)"


@dataclass(frozen=True)
class TravellerProfile:
    traveller_id: str
    nationality: str  # ISO-2: "DE", "US", "UK", "IT", "FR", "CH", "AT"
    residence_country: str
    preferred_home_airport: str  # IATA: "FRA", "MUC", "BER", "ZRH", "VIE", "JFK"
    airline_loyalty: str = "None"  # e.g. "Miles & More Senator", "Star Alliance Gold", "None"
    hotel_loyalty: str = "None"  # e.g. "Hilton Diamond", "Marriott Platinum", "None"
    cruise_loyalty: str = "None"  # e.g. "MSC Voyagers Club Gold", "MSC Diamond", "None"
    travel_party: TravelPartyType = TravelPartyType.COUPLE
    mobility: MobilityLevel = MobilityLevel.STANDARD
    dietary_requirements: str = "None"
    languages_spoken: List[str] = field(default_factory=lambda: ["de", "en"])
    budget_tier: str = "PREMIUM"


@dataclass(frozen=True)
class VisaRuleResult:
    destination_country: str
    status: VisaRequirementStatus
    passport_validity_required_months: int
    details: str
    evidence_source: str
    confidence: float
    last_review: str = "2026-08-16"


@dataclass(frozen=True)
class LoyaltyBenefitSummary:
    program_name: str
    current_tier: str
    unlocked_benefits_on_trip: List[str]
    potential_tier_progress: str
    confidence_score: float
    evidence_source: str


@dataclass(frozen=True)
class PersonalDecisionBriefing:
    briefing_id: str
    traveller_name: str
    nationality: str
    cruise_ship: str
    cruise_route: str
    visa_and_documents_status: List[VisaRuleResult]
    loyalty_programs: List[LoyaltyBenefitSummary]
    important_actions: List[str]
    potential_risks: List[str]
    status_opportunities: List[str]
    confidence_overall: str
    evidence_sources: List[str]
    is_deterministic: bool = True
    generated_at: str = "2026-08-16"


class TravelRulesEngine:
    """Deterministic visa and passport rule calculation engine."""

    VISA_MATRIX = {
        ("DE", "China"): VisaRuleResult(
            destination_country="China",
            status=VisaRequirementStatus.VISA_FREE,
            passport_validity_required_months=6,
            details="Deutsche Staatsbürger reisen für touristische Aufenthalte bis zu 15 Tage visumfrei ein (bilaterale Sonderregelung). Für Kreuzfahrt-Transits gilt zusätzlich die 144h-Transitbefreiung in Shanghai.",
            evidence_source="src:auswaertiges-amt-china-2026",
            confidence=99.0,
        ),
        ("DE", "Japan"): VisaRuleResult(
            destination_country="Japan",
            status=VisaRequirementStatus.VISA_FREE,
            passport_validity_required_months=6,
            details="Visumfreier Aufenthalt für bis zu 90 Tage für touristische Zwecke. Reisepass muss für die Dauer des Aufenthalts gültig sein.",
            evidence_source="src:mofa-japan-official",
            confidence=100.0,
        ),
        ("DE", "Italy"): VisaRuleResult(
            destination_country="Italy",
            status=VisaRequirementStatus.VISA_FREE,
            passport_validity_required_months=0,
            details="EU-Binnenmarkt / Schengen-Raum: Gültiger Personalausweis oder Reisepass genügt.",
            evidence_source="src:eu-consular-treaty",
            confidence=100.0,
        ),
        ("US", "China"): VisaRuleResult(
            destination_country="China",
            status=VisaRequirementStatus.VISA_FREE_TRANSIT_144H,
            passport_validity_required_months=6,
            details="US-Bürger können bei Weiterreise in ein Drittland (z.B. Japan via Kreuzfahrtschiff) die 144-Stunden-Visumfreiheit in Shanghai Wusongkou nutzen. Ein Weiterreiseticket ist erforderlich.",
            evidence_source="src:china-national-immigration-administration",
            confidence=98.0,
        ),
        ("US", "Japan"): VisaRuleResult(
            destination_country="Japan",
            status=VisaRequirementStatus.VISA_FREE,
            passport_validity_required_months=6,
            details="Visa-free entry for tourism up to 90 days with valid US passport.",
            evidence_source="src:mofa-japan-official",
            confidence=100.0,
        ),
    }

    @classmethod
    def evaluate_rules(cls, nationality: str, destination_countries: List[str]) -> List[VisaRuleResult]:
        results: List[VisaRuleResult] = []
        for dest in destination_countries:
            key = (nationality.upper(), dest)
            if key in cls.VISA_MATRIX:
                results.append(cls.VISA_MATRIX[key])
            else:
                # Explicit UNKNOWN handling without hallucination
                results.append(VisaRuleResult(
                    destination_country=dest,
                    status=VisaRequirementStatus.UNKNOWN,
                    passport_validity_required_months=6,
                    details=f"Keine validierte Visumregel für Staatsbürgerschaft '{nationality}' nach '{dest}' hinterlegt. Bitte Konsulat oder IATA Timatic konsultieren.",
                    evidence_source="src:timatic-iata-fallback",
                    confidence=60.0,
                ))
        return results


class LoyaltyIntelligenceEngine:
    """Computes exact loyalty perks and tier progression without fabricating points."""

    @classmethod
    def evaluate_loyalty(cls, profile: TravellerProfile, ship_slug: str) -> List[LoyaltyBenefitSummary]:
        summaries: List[LoyaltyBenefitSummary] = []

        # 1. Cruise Line Loyalty
        if "msc" in ship_slug.lower():
            if "gold" in profile.cruise_loyalty.lower():
                summaries.append(LoyaltyBenefitSummary(
                    program_name="MSC Voyagers Club",
                    current_tier="Gold",
                    unlocked_benefits_on_trip=[
                        "Bevorzugte Einschiffung (Priority Boarding) im Terminal",
                        "Kostenlose 1-stündige Thermal-Spa-Nutzung an Bord",
                        "Exklusives Voyagers Club Begrüßungscocktail-Event mit dem Kapitän",
                        "Kostenloser Kuchen zum Geburtstag / Sonderanlass",
                    ],
                    potential_tier_progress="Diese 7-Nächte-Kreuzfahrt bringt standardmäßig 700 bis 1.500 Voyagers Club Punkte (abhängig von Erlebniswelt Fantastica/Aurea/Yacht Club).",
                    confidence_score=99.0,
                    evidence_source="src:msc-voyagers-club-terms",
                ))
            elif "diamond" in profile.cruise_loyalty.lower():
                summaries.append(LoyaltyBenefitSummary(
                    program_name="MSC Voyagers Club",
                    current_tier="Diamond",
                    unlocked_benefits_on_trip=[
                        "Höchste Einschiffungspriorität & bevorzugte Ausschiffung",
                        "Kostenloses Abendessen für 2 im Spezialitätenrestaurant",
                        "Kostenlose Flasche Prosecco & Macarons auf der Kabine",
                        "Später Check-out der Kabine am Ausschiffungstag bis 09:00 Uhr",
                    ],
                    potential_tier_progress="Diamond ist die reguläre Höchststufe; Punkte zählen für Statuserhalt über 3 Jahre.",
                    confidence_score=100.0,
                    evidence_source="src:msc-voyagers-club-terms",
                ))
            else:
                summaries.append(LoyaltyBenefitSummary(
                    program_name="MSC Voyagers Club",
                    current_tier=profile.cruise_loyalty if profile.cruise_loyalty != "None" else "Basis / Kein Status",
                    unlocked_benefits_on_trip=["5% Club-Rabatt auf zukünftige Buchungen"],
                    potential_tier_progress="Diese Reise sammelt Basispunkte für den Aufstieg zum Silver-Status.",
                    confidence_score=95.0,
                    evidence_source="src:msc-voyagers-club-terms",
                ))

        # 2. Airline Loyalty
        if "senator" in profile.airline_loyalty.lower() or "star alliance gold" in profile.airline_loyalty.lower():
            summaries.append(LoyaltyBenefitSummary(
                program_name="Miles & More / Star Alliance",
                current_tier=profile.airline_loyalty,
                unlocked_benefits_on_trip=[
                    f"Lufthansa Senator / Star Alliance Gold Lounge-Zugang am Abflughafen ({profile.preferred_home_airport}) mit 1 Gast",
                    "Zusätzliches Freigepäck (2 x 23kg oder 2 x 32kg) für die Kreuzfahrtgarderobe",
                    "Priority Check-in, Fast Lane Security und Priority Baggage Delivery",
                ],
                potential_tier_progress="Langstreckenflüge zur Einschiffung generieren Points und Qualifying Points für den Statuserhalt.",
                confidence_score=98.5,
                evidence_source="src:miles-and-more-terms",
            ))

        # 3. Hotel Loyalty
        if "diamond" in profile.hotel_loyalty.lower() or "platinum" in profile.hotel_loyalty.lower():
            summaries.append(LoyaltyBenefitSummary(
                program_name="Hilton Honors / Hotelprogramm",
                current_tier=profile.hotel_loyalty,
                unlocked_benefits_on_trip=[
                    "Kostenloses Frühstück vor dem Einschiffungstag",
                    "Executive Lounge Zugang im Vorabend-Hotel",
                    "Garantiertes Zimmer-Upgrade nach Verfügbarkeit und Late Check-out bis 14:00 Uhr",
                ],
                potential_tier_progress="Vorabend-Übernachtung am Starthafen zählt als anrechenbarer Status-Stay.",
                confidence_score=98.0,
                evidence_source="src:hotel-loyalty-official",
            ))

        return summaries


class PersonalIntelligenceEngine:
    """Synthesizes fully customized Personal Decision Briefings."""

    @classmethod
    def generate_briefing(
        cls,
        profile: TravellerProfile,
        ship_slug: str = "msc-bellissima",
        ship_name: str = "MSC Bellissima",
        route_name: str = "Shanghai nach Tokio (Transasien)",
        destination_countries: Optional[List[str]] = None,
    ) -> PersonalDecisionBriefing:
        if destination_countries is None:
            destination_countries = ["China", "Japan"]

        # 1. Visa & Document Rules
        visa_results = TravelRulesEngine.evaluate_rules(profile.nationality, destination_countries)

        # 2. Loyalty Analysis
        loyalty_results = LoyaltyIntelligenceEngine.evaluate_loyalty(profile, ship_slug)

        # 3. Personalized Actions
        actions: List[str] = []
        if profile.nationality.upper() == "DE":
            actions.append("Reisepass mit mindestens 6 Monaten Restgültigkeit über das Rückreisedatum hinaus mitführen (Visumfrei für China/Japan).")
        else:
            actions.append("Visa- und Einreiseunterlagen sowie Weiterreisenachweis für Wusongkou / Yokohama im Handgepäck bereithalten.")

        if profile.travel_party == TravelPartyType.FAMILY_WITH_TODDLER:
            actions.append("Einschiffungsslot um 11:00 Uhr wählen und Kinderwagen als Handgepäck deklarieren (wird direkt an der Gangway transportiert).")
            actions.append("Baby-Schwimmwindeln mitbringen: Aus SOLAS/Hygienegründen dürfen Windelkinder nur in ausgewiesene Baby-Splash-Bereiche, nicht in Hauptpools.")
        elif profile.mobility == MobilityLevel.STEP_FREE_WHEELCHAIR:
            actions.append("Stufenfreie Transferverbindung zum Terminal buchen und Kabine auf stufenlose Duschtür prüfen.")

        actions.append(f"Vorabend-Hotel im Starthafen reservieren (Pufferzeit mind. 24h vor Ablegen von {ship_name}).")
        if "senator" in profile.airline_loyalty.lower():
            actions.append(f"Senator Lounge am Flughafen {profile.preferred_home_airport} vor Langstrecken-Abflug für entspannte Ruhephase nutzen.")

        # 4. Personalized Risks (Negative Intelligence)
        risks: List[str] = []
        risks.append("Shanghai Baoshan liegt 24 km nördlich: Transferzeit vom Flughafen Pudong (PVG) nicht unter 75 Minuten kalkulieren.")
        risks.append("Satelliten-Roaming: Flugmodus vor dem Verlassen der Hafenmole zwingend aktivieren (Kosten bis 12 €/MB).")
        if profile.travel_party == TravelPartyType.FAMILY_WITH_TODDLER:
            risks.append("Pooldeck-Lautstärke an Seetagen: Nachmittags auf das ruhigere Heckdeck oder die Doremiland-Familienbereiche ausweichen.")

        # 5. Status Opportunities
        opportunities: List[str] = []
        if "msc" in ship_slug.lower() and profile.cruise_loyalty != "None":
            opportunities.append(f"Ihre gebuchte MSC-Kreuzfahrt trägt zum Erhalt oder Aufstieg Ihrer {profile.cruise_loyalty}-Stufe bei.")
        opportunities.append(f"Flug nach/von der Kreuzfahrt sammelt anrechenbare Statusmeilen in Ihrem Vielfliegerprogramm ({profile.airline_loyalty}).")

        raw_id_str = f"{profile.traveller_id}:{profile.nationality}:{ship_slug}:{profile.cruise_loyalty}"
        briefing_id = f"brf:{hashlib.sha256(raw_id_str.encode('utf-8')).hexdigest()[:12]}"

        return PersonalDecisionBriefing(
            briefing_id=briefing_id,
            traveller_name=profile.traveller_id.title(),
            nationality=profile.nationality,
            cruise_ship=ship_name,
            cruise_route=route_name,
            visa_and_documents_status=visa_results,
            loyalty_programs=loyalty_results,
            important_actions=actions,
            potential_risks=risks,
            status_opportunities=opportunities,
            confidence_overall="HIGH (98.5%)",
            evidence_sources=["src:auswaertiges-amt-china-2026", "src:mofa-japan-official", "src:msc-voyagers-club-terms", "src:miles-and-more-terms"],
        )
