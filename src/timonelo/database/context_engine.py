"""
Context Engine and Bridge Officer Tim Proactive Evaluation for Timonelo (Chapter III - Sprint 09).
"I have reviewed your journey. Everything is proceeding as expected. I remain on the bridge."
Context-aware travel intelligence evaluating traveller context, cabin suitability,
journey phase, outstanding tasks, memory layer, and top 3 priorities deterministically.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, date


# =========================================================================
# 1. CANONICAL CABIN CONTEXT MODELS (Backward Compatibility)
# =========================================================================

class PassengerProfileType(str, Enum):
    MOTION_SENSITIVE = "MOTION_SENSITIVE"
    LIGHT_SLEEPER = "LIGHT_SLEEPER"
    PHOTOGRAPHER = "PHOTOGRAPHER"
    MOBILITY_REDUCED = "MOBILITY_REDUCED"
    SHOW_LOVER = "SHOW_LOVER"
    STANDARD = "STANDARD"


class Season(str, Enum):
    SPRING = "SPRING"
    SUMMER = "SUMMER"
    AUTUMN = "AUTUMN"
    WINTER = "WINTER"


class SeaState(str, Enum):
    CALM = "CALM"
    MODERATE = "MODERATE"
    ROUGH = "ROUGH"


class RouteHeading(str, Enum):
    NORTHBOUND = "NORTHBOUND"
    SOUTHBOUND = "SOUTHBOUND"
    EASTBOUND = "EASTBOUND"
    WESTBOUND = "WESTBOUND"
    CIRCULAR = "CIRCULAR"


@dataclass(frozen=True)
class CabinFactProfile:
    cabin_number: str
    deck_number: int
    deck_name: str
    category: str
    hull_side: str  # "PORT" or "STARBOARD"
    zone: str       # "FORWARD", "MID", "AFT"
    interior_sqm: float
    balcony_sqm: float
    distance_to_nearest_lift_m: float
    distance_to_nearest_stairs_m: float
    distance_to_main_theatre_m: float
    distance_to_buffet_m: float
    noise_risk_fact: str
    view_category_fact: str
    step_free_accessible: bool
    vertical_neighbor_above: str
    vertical_neighbor_below: str


@dataclass(frozen=True)
class PassengerContext:
    profile_type: PassengerProfileType = PassengerProfileType.STANDARD
    motion_sensitive: bool = False
    light_sleeper: bool = False
    priority_theatre_and_shows: bool = False
    priority_scenic_photography: bool = False
    requires_step_free: bool = False


@dataclass(frozen=True)
class TripContext:
    ship_slug: str
    route_slug: str
    route_name: str
    season: Season
    heading: RouteHeading
    expected_sea_state: SeaState = SeaState.MODERATE


@dataclass(frozen=True)
class CabinContextAdvice:
    cabin_number: str
    suitability_score: float
    suitability_verdict: str
    benefits_for_you: List[str]
    trade_offs_for_you: List[str]
    evidence_source: str


# =========================================================================
# 2. SPRINT 09 JOURNEY & TRAVELLER CONTEXT ENGINE
# =========================================================================

class CurrentPhase(str, Enum):
    PLANNING = "PLANNING (Reiseplanung)"
    BOOKED = "BOOKED (Reise bestätigt)"
    PREPARATION = "PREPARATION (Reisevorbereitung T-30 bis T-4)"
    CHECK_IN = "CHECK_IN (Online Check-in offen T-3)"
    TRAVEL_DAY = "TRAVEL_DAY (Anreisetag / Langstreckenflug)"
    HOTEL = "HOTEL (Vorabend-Hotelaufenthalt)"
    EMBARKATION = "EMBARKATION (Einschiffungstag)"
    FIRST_DAY = "FIRST_DAY (Erster Tag an Bord)"
    SEA_DAY = "SEA_DAY (Seetag auf See)"
    PORT_DAY = "PORT_DAY (Hafentag & Landgang)"
    LAST_NIGHT = "LAST_NIGHT (Vorabend der Ausschiffung)"
    DISEMBARKATION = "DISEMBARKATION (Ausschiffung & Heimreise)"
    RETURN_HOME = "RETURN_HOME (Wohlbehalten zu Hause)"


class TaskPriority(str, Enum):
    CRITICAL = "CRITICAL (Dringend erforderlich)"
    HIGH = "HIGH (Hohe Priorität)"
    MEDIUM = "MEDIUM (Empfohlen)"
    LOW = "LOW (Optional / Komfort)"


@dataclass(frozen=True)
class OutstandingTask:
    task_id: str
    title: str
    priority: TaskPriority
    deadline_display: str
    days_remaining: int
    evidence_source: str
    reason: str
    recommended_action: str
    is_completed: bool = False


@dataclass(frozen=True)
class BotMemory:
    completed_task_ids: List[str] = field(default_factory=list)
    preferred_cabin_type: str = "Balkonkabine Steuerbord (Mitte)"
    preferred_airline_alliance: str = "Star Alliance (Lufthansa / ANA)"
    preferred_hotel_chain: str = "World of Hyatt / LHW"
    past_cruises_count: int = 4
    loyalty_tier_cache: Dict[str, str] = field(
        default_factory=lambda: {
            "msc": "Diamond",
            "hyatt": "Globalist",
            "miles_and_more": "Senator",
        }
    )


@dataclass(frozen=True)
class TravellerContext:
    traveller_name: str
    language: str
    home_airport: str
    cruise_loyalty_status: str
    hotel_loyalty_status: str
    airline_loyalty_status: str
    passport_expiry_date: str
    visa_status: str
    mobility_requirements: str = "None (Keine Einschränkungen)"
    dietary_preferences: str = "Keine besonderen Diäten hinterlegt"


@dataclass(frozen=True)
class JourneyContext:
    ship_slug: str
    ship_name: str
    cabin_number: str
    departure_date_iso: str
    return_date_iso: str
    origin_city: str
    embarkation_port_slug: str
    hotel_name: Optional[str] = "Hyatt on the Bund"
    flight_number: Optional[str] = "LH728"


@dataclass(frozen=True)
class DailyBriefing:
    briefing_id: str
    phase: CurrentPhase
    date_display: str
    greeting_line: str
    status_headline: str
    proactive_bot_notices: List[str]
    top_priorities: List[OutstandingTask]
    completed_milestones: List[str]
    sign_off_phrase: str
    confidence_score: float = 99.5
    is_deterministic: bool = True


class ContextEngine:
    """Canonical engine evaluating traveller situation, auto-detecting phases, and synthesizing Top 3 Priorities."""

    @classmethod
    def evaluate_cabin_for_passenger(
        cls,
        cabin: CabinFactProfile,
        passenger: PassengerContext,
        trip: TripContext,
    ) -> CabinContextAdvice:
        score = 85.0
        benefits = []
        trade_offs = []

        if passenger.motion_sensitive:
            if cabin.deck_number >= 12 or cabin.zone in ["FORWARD", "AFT"]:
                score -= 40.0
                trade_offs.append("High deck aft location experiences amplified roll and pitch motions in rough sea states.")
            else:
                score += 10.0
                benefits.append("Midship lower deck provides superior stability during open sea transits.")

        if passenger.priority_scenic_photography:
            if trip.heading == RouteHeading.NORTHBOUND and cabin.hull_side == "STARBOARD":
                score += 12.0
                benefits.append("Starboard facing balcony enjoys unobstructed morning natural light and coastal topography on northbound routes.")

        if passenger.requires_step_free:
            if not cabin.step_free_accessible:
                score -= 35.0
                trade_offs.append("Standard cabin entry and raised bathroom threshold are not certified step-free for wheelchair transit.")

        verdict = "GREAT_FIT_FOR_YOUR_CONTEXT" if score >= 80.0 else (
            "ACCEPTABLE_FIT_WITH_TRADE_OFFS" if score >= 60.0 else "NOT_RECOMMENDED_FOR_YOUR_CONTEXT"
        )

        return CabinContextAdvice(
            cabin_number=cabin.cabin_number,
            suitability_score=max(0.0, min(100.0, score)),
            suitability_verdict=verdict,
            benefits_for_you=benefits,
            trade_offs_for_you=trade_offs,
            evidence_source="src:timonelo-context-engine",
        )

    @classmethod
    def detect_journey_phase(
        cls,
        simulated_current_date_iso: str,
        departure_date_iso: str,
        return_date_iso: str,
    ) -> CurrentPhase:
        cur = datetime.strptime(simulated_current_date_iso, "%Y-%m-%d").date()
        dep = datetime.strptime(departure_date_iso, "%Y-%m-%d").date()
        ret = datetime.strptime(return_date_iso, "%Y-%m-%d").date()

        days_to_dep = (dep - cur).days

        if days_to_dep > 30:
            return CurrentPhase.BOOKED
        elif 4 <= days_to_dep <= 30:
            return CurrentPhase.PREPARATION
        elif 1 < days_to_dep <= 3:
            return CurrentPhase.CHECK_IN
        elif days_to_dep == 1:
            return CurrentPhase.TRAVEL_DAY
        elif days_to_dep == 0:
            return CurrentPhase.EMBARKATION
        elif cur < ret:
            delta = (cur - dep).days
            if delta == 1:
                return CurrentPhase.FIRST_DAY
            elif delta % 2 == 0:
                return CurrentPhase.PORT_DAY
            else:
                return CurrentPhase.SEA_DAY
        elif cur == ret:
            return CurrentPhase.DISEMBARKATION
        else:
            return CurrentPhase.RETURN_HOME

    @classmethod
    def evaluate_outstanding_tasks(
        cls,
        phase: CurrentPhase,
        traveller: TravellerContext,
        journey: JourneyContext,
        memory: BotMemory,
    ) -> List[OutstandingTask]:
        tasks: List[OutstandingTask] = []

        # 1. Visa & Entry Verification
        if "china" in journey.embarkation_port_slug.lower() or "shanghai" in journey.embarkation_port_slug.lower():
            if "visa:china-15d-exempt" not in memory.completed_task_ids:
                tasks.append(
                    OutstandingTask(
                        task_id="task:visa-check",
                        title="Reisepass-Gültigkeit & 15-Tage-Visumbefreiung China",
                        priority=TaskPriority.CRITICAL,
                        deadline_display="Vor Abflug",
                        days_remaining=12,
                        evidence_source="src:auswaertiges-amt-china",
                        reason="Für die visumfreie Einreise nach China muss der Reisepass am Einreisetag noch mindestens 6 Monate gültig sein.",
                        recommended_action="Reisepass-Ablaufdatum abgleichen und China Arrival Card digital bereithalten.",
                        is_completed=False,
                    )
                )

        # 2. Online Check-in & Bag Tags
        if phase in [CurrentPhase.PREPARATION, CurrentPhase.CHECK_IN]:
            tasks.append(
                OutstandingTask(
                    task_id="task:checkin-msc",
                    title="Online-Check-in & Kofferanhänger Kabine 14122 drucken",
                    priority=TaskPriority.HIGH,
                    deadline_display="T-3 Tage",
                    days_remaining=3,
                    evidence_source="src:msc-cruises-operations",
                    reason="Ein abgeschlossener Web-Check-in spart 15–20 Minuten am Schalter im Terminal Baoshan.",
                    recommended_action="Kofferanhänger ausdrucken und am Handgepäck befestigen.",
                    is_completed=False,
                )
            )

        # 3. eSIM & Payment Setup
        tasks.append(
            OutstandingTask(
                task_id="task:alipay-esim",
                title="Alipay TourCard & eSIM mit VPN installieren",
                priority=TaskPriority.HIGH,
                deadline_display="T-2 Tage",
                days_remaining=2,
                evidence_source="src:field-audit-shanghai-2026",
                reason="In Shanghai ist Kartenzahlung in Taxis unüblich; Google Maps & WhatsApp funktionieren ohne VPN nicht.",
                recommended_action="Alipay App mit Visa verknüpfen und Airalo eSIM aktivieren.",
                is_completed=False,
            )
        )

        # 4. Medication Carry-on Reminder
        tasks.append(
            OutstandingTask(
                task_id="task:meds-handluggage",
                title="Reiseapotheke & Medikamente ins Handgepäck packen",
                priority=TaskPriority.MEDIUM,
                deadline_display="Packtag",
                days_remaining=1,
                evidence_source="src:timonelo-safety-regret-score",
                reason="Aufgegebene Koffer werden erst am späten Nachmittag auf die Kabine geliefert.",
                recommended_action="Tagesdosis für 48 Stunden stets im persönlichen Handgepäck führen.",
                is_completed=False,
            )
        )

        return tasks

    @classmethod
    def generate_context_briefing(
        cls,
        simulated_date_iso: str = "2026-10-03",
        traveller: Optional[TravellerContext] = None,
        journey: Optional[JourneyContext] = None,
        memory: Optional[BotMemory] = None,
    ) -> DailyBriefing:
        if traveller is None:
            traveller = TravellerContext(
                traveller_name="Florian",
                language="Deutsch",
                home_airport="FRA",
                cruise_loyalty_status="Diamond (MSC Voyagers Club)",
                hotel_loyalty_status="Globalist (World of Hyatt)",
                airline_loyalty_status="Senator (Miles & More)",
                passport_expiry_date="2028-11-20",
                visa_status="Visumfrei (15 Tage China Sonderregelung)",
            )

        if journey is None:
            journey = JourneyContext(
                ship_slug="msc-bellissima",
                ship_name="MSC Bellissima",
                cabin_number="14122",
                departure_date_iso="2026-10-15",
                return_date_iso="2026-10-22",
                origin_city="Frankfurt",
                embarkation_port_slug="shanghai",
                hotel_name="Hyatt on the Bund",
                flight_number="LH728",
            )

        if memory is None:
            memory = BotMemory(
                completed_task_ids=["task:flight-booked", "task:hotel-booked"]
            )

        phase = cls.detect_journey_phase(
            simulated_date_iso, journey.departure_date_iso, journey.return_date_iso
        )
        all_tasks = cls.evaluate_outstanding_tasks(phase, traveller, journey, memory)

        # Context Priority Engine: MAXIMUM 3 PRIORITIES
        top_3_priorities = all_tasks[:3]

        bot_notices = [
            f"BOT noticed: Ihre Reise mit {journey.ship_name} (Kabine {journey.cabin_number}) beginnt in 12 Tagen.",
            f"BOT noticed: Ihr Langstreckenflug {journey.flight_number} und Vorabend-Hotel {journey.hotel_name} sind im System hinterlegt.",
            "BOT noticed: Mit Ihrem Status 'World of Hyatt Globalist' steht Ihnen im Hyatt on the Bund ein garantierter Late Check-out bis 16:00 Uhr und Club-Lounge-Zugang zu.",
        ]

        completed_milestones = [
            "Langstreckenflug LH728 (FRA -> PVG) bestätigt",
            "Vorabend-Hotel Hyatt on the Bund reserviert",
            "Reisepass-Gültigkeit bis 2028 bestätigt (>6 Monate)",
            "MSC Voyagers Club Diamond Status hinterlegt (Priority Boarding)",
        ]

        greeting = f"Guten Morgen, {traveller.traveller_name}."
        headline = "Ich habe Ihre Reise über Nacht geprüft. Drei Punkte verdienen heute Ihre Aufmerksamkeit."

        return DailyBriefing(
            briefing_id=f"briefing:{simulated_date_iso}",
            phase=phase,
            date_display=f"Samstag, 3. Oktober 2026 · T-12 Tage",
            greeting_line=greeting,
            status_headline=headline,
            proactive_bot_notices=bot_notices,
            top_priorities=top_3_priorities,
            completed_milestones=completed_milestones,
            sign_off_phrase="I have reviewed your journey. Everything is proceeding as expected. I remain on the bridge.",
        )
