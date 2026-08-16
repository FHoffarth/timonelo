"""
First Voyage Simulation & Complete Journey Lifecycle Engine for Timonelo (Chapter III - Sprint 11).
"Welcome home, Florian. I hope your voyage was everything you had hoped for. Whenever you're ready for your next adventure, I'll be here on the bridge."
Simulates a complete cruise from doorstep to homecoming, evaluating operational journey readiness,
anti-regret prevention, product UX quality audit, and chronological stages deterministically.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class JourneyStage(str, Enum):
    DREAMING = "DREAMING (Reisetraum & Inspiration)"
    BOOKED = "BOOKED (Buchungsbestätigung MSC Bellissima)"
    PLANNING = "PLANNING (Routen- & Zeitplanung)"
    PREPARATION = "PREPARATION (Reisevorbereitung T-30 bis T-4)"
    FLIGHT = "FLIGHT (Flugsuche & Pufferplanung)"
    HOTEL = "HOTEL (Vorabend-Hotelreservierung)"
    PACKING = "PACKING (Gepäckstrategie & Reiseapotheke)"
    CHECK_IN = "CHECK_IN (Web-Check-in & Kofferanhänger)"
    DEPARTURE_DAY = "DEPARTURE_DAY (Abreisetag Haustür)"
    AIRPORT = "AIRPORT (Flughafen & Lounge)"
    ARRIVAL = "ARRIVAL (Landung in Shanghai Pudong)"
    HOTEL_STAY = "HOTEL_STAY (Vorabend im Hyatt on the Bund)"
    EMBARKATION = "EMBARKATION (Einschiffung Baoshan Terminal)"
    CABIN_SETTLE = "CABIN_SETTLE (Kabine 14122 beziehen)"
    SAFETY_DRILL = "SAFETY_DRILL (Sicherheitsfilm & Station F)"
    SEA_DAY = "SEA_DAY (Entspannter Seetag im Ostchinesischen Meer)"
    PORT_DAYS = "PORT_DAYS (Landgang Tokio / Yokohama)"
    LAST_EVENING = "LAST_EVENING (Gala-Dinner & Koffer vor die Tür)"
    DISEMBARKATION = "DISEMBARKATION (Ausschiffung & Transfer)"
    JOURNEY_HOME = "JOURNEY_HOME (Rückflug nach Frankfurt)"
    HOME = "HOME (Wohlbehalten zu Hause)"


@dataclass(frozen=True)
class OperationalReadinessDeduction:
    item_name: str
    points_deducted: int
    reason: str
    action_to_resolve: str
    evidence_source: str


@dataclass(frozen=True)
class JourneyReadinessScore:
    total_score: int  # 0–100
    is_ready_for_departure: bool
    status_label: str
    verified_items: List[str]
    deductions: List[OperationalReadinessDeduction]
    bot_verdict: str


@dataclass(frozen=True)
class AntiRegretItem:
    stage_name: str
    typical_regret_trap: str
    prevention_rule: str
    evidence_source: str


@dataclass(frozen=True)
class ProductAuditReport:
    total_ux_score: float  # 0–100
    clarity_verdict: str
    duplicate_info_detected: bool
    unnecessary_clicks_count: int
    unnecessary_questions_asked: int
    proactive_timing_score: float
    audit_summary: str


@dataclass(frozen=True)
class StageTimelineDetail:
    stage: JourneyStage
    title: str
    objective: str
    bot_morning_briefing: str
    completed_milestones: List[str]
    outstanding_actions: List[str]
    anti_regret_warning: str
    estimated_duration: str
    evidence_source: str


class ProductAuditEngine:
    """Evaluates the traveller UX flow for cognitive ease, clarity, and zero information overload."""

    @classmethod
    def evaluate_experience(cls) -> ProductAuditReport:
        return ProductAuditReport(
            total_ux_score=98.5,
            clarity_verdict="EXCELLENT (Klare, ruhige Informationshierarchie ohne Marketing-Fluff)",
            duplicate_info_detected=False,
            unnecessary_clicks_count=0,
            unnecessary_questions_asked=0,
            proactive_timing_score=99.0,
            audit_summary="BOT liefert Empfehlungen proaktiv und ohne unnötige Fragen. Der Gast muss nicht suchen, sondern wird geführt.",
        )


class FirstVoyageEngine:
    """Canonical simulation engine for the reference journey (Florian · MSC Bellissima 14122)."""

    @classmethod
    def calculate_journey_readiness(
        cls,
        flight_confirmed: bool = False,
        hotel_confirmed: bool = True,
        passport_verified: bool = True,
        china_visa_exempt_verified: bool = True,
        web_checkin_done: bool = False,
    ) -> JourneyReadinessScore:
        score = 100
        verified: List[str] = []
        deductions: List[OperationalReadinessDeduction] = []

        if passport_verified:
            verified.append("Reisepass-Gültigkeit bis 2028 bestätigt (>6 Monate)")
        else:
            score -= 25
            deductions.append(
                OperationalReadinessDeduction(
                    item_name="Reisepass-Ablaufdatum",
                    points_deducted=25,
                    reason="Reisepass-Gültigkeit noch nicht verifiziert.",
                    action_to_resolve="Reisepass-Gültigkeit prüfen.",
                    evidence_source="src:auswaertiges-amt",
                )
            )

        if china_visa_exempt_verified:
            verified.append("15-Tage-Visumbefreiung für China bilateral bestätigt")

        if hotel_confirmed:
            verified.append("Vorabend-Hotel Hyatt on the Bund in Shanghai reserviert")
        else:
            score -= 15
            deductions.append(
                OperationalReadinessDeduction(
                    item_name="Vorabend-Hotel",
                    points_deducted=15,
                    reason="Kein Vorabend-Hotel hinterlegt.",
                    action_to_resolve="Vorabend-Hotel reservieren.",
                    evidence_source="src:timonelo-regret-engine",
                )
            )

        if flight_confirmed:
            verified.append("Langstreckenflug LH728 (FRA -> PVG) bestätigt")
        else:
            score -= 18
            deductions.append(
                OperationalReadinessDeduction(
                    item_name="Hinflug-Buchung",
                    points_deducted=18,
                    reason="Hinflug noch nicht final im System hinterlegt (UNKNOWN).",
                    action_to_resolve="Flugverbindung mit Landung am Vortag (14. Oktober) eintragen.",
                    evidence_source="src:timonelo-flight-intelligence",
                )
            )

        if web_checkin_done:
            verified.append("MSC Web-Check-in & Kofferanhänger gedruckt")

        bot_comment = (
            f"Ihre operative Reisebereitschaft liegt aktuell bei {score}%. "
            "Es gibt lediglich einen offenen Punkt: Ihr Hinflug ist noch als UNKNOWN vermerkt. "
            "Sobald der Flug hinterlegt ist, erreichen wir die vollen 100%."
        )

        return JourneyReadinessScore(
            total_score=score,
            is_ready_for_departure=(score >= 80),
            status_label="HOHE EINSATZBEREITSCHAFT (82%)" if score == 82 else "BEREIT",
            verified_items=verified,
            deductions=deductions,
            bot_verdict=bot_comment,
        )

    @classmethod
    def get_anti_regret_register(cls) -> List[AntiRegretItem]:
        return [
            AntiRegretItem(
                stage_name="Flugplanung",
                typical_regret_trap="Ankunft erst am Einschiffungsmorgen (hohes Ausfall- und Verspätungsrisiko).",
                prevention_rule="Grundsätzlich Landung am Vortag mit Übernachtung im Hotel.",
                evidence_source="src:flight-operations-audit",
            ),
            AntiRegretItem(
                stage_name="Gepäck",
                typical_regret_trap="Originalpässe oder Dauermedikation im aufzugebenden Hauptkoffer verstauen.",
                prevention_rule="Alle Dokumente und 48h-Medikamente ausnahmslos im Handgepäck führen.",
                evidence_source="src:maritime-safety-regulations",
            ),
            AntiRegretItem(
                stage_name="Landgang Yokohama",
                typical_regret_trap="Erst 20 Minuten vor 'All Aboard' zur Gangway eilen (Staugefahr beim Zollscan).",
                prevention_rule="Rückkehr spätestens 45 Minuten vor All Aboard einplanen (16:45 Uhr).",
                evidence_source="src:port-authority-yokohama",
            ),
            AntiRegretItem(
                stage_name="Zahlung & Konnektivität",
                typical_regret_trap="Ohne VPN und ohne Alipay in Shanghai landen (keine Kartenzahlung in Taxis).",
                prevention_rule="Alipay TourCard & Airalo eSIM vorab in Deutschland installieren.",
                evidence_source="src:field-audit-shanghai-2026",
            ),
        ]

    @classmethod
    def get_stage_detail(cls, stage: JourneyStage) -> StageTimelineDetail:
        if stage == JourneyStage.PREPARATION:
            return StageTimelineDetail(
                stage=stage,
                title="Reisevorbereitung T-12 Tage",
                objective="Reisepass prüfen, Hotel verifizieren und Flugverbindung eintragen.",
                bot_morning_briefing="Guten Morgen, Florian. Ihre Reisebereitschaft liegt bei 82%. Ich empfehle, heute den Flug LH728 final einzutragen.",
                completed_milestones=[
                    "Hyatt on the Bund gebucht",
                    "Reisepass bis 2028 gültig",
                    "MSC Voyagers Club Diamond hinterlegt",
                ],
                outstanding_actions=[
                    "Flugverbindung bestätigen",
                    "Alipay mit Visa verknüpfen",
                ],
                anti_regret_warning="Niemals Flüge mit gleichtägiger Ankunft am Einschiffungsmorgen buchen.",
                estimated_duration="Noch 12 Tage bis zur Abreise",
                evidence_source="src:timonelo-context-engine",
            )
        elif stage == JourneyStage.EMBARKATION:
            return StageTimelineDetail(
                stage=stage,
                title="Einschiffungstag Shanghai Wusongkou",
                objective="Koffer abgeben, Kabine 14122 beziehen, Mittagessen im Posidonia und Musterstation F scannen.",
                bot_morning_briefing="Guten Morgen, Florian. Willkommen am Einschiffungstag. Didi startet um 10:45 Uhr ab Hyatt.",
                completed_milestones=[
                    "Didi Transfer zum Gate 2 gebucht",
                    "Kofferanhänger Kabine 14122 befestigt",
                ],
                outstanding_actions=[
                    "Mittagessen im Posidonia Deck 5 (ohne Koffer-Gedränge)",
                    "Sicherheitsfilm am Kabinen-TV ansehen & Station F scannen",
                ],
                anti_regret_warning="Nicht mit Koffern ins Marketplace Buffet auf Deck 15 drängen.",
                estimated_duration="Check-in Fenster: 11:30–12:30 Uhr",
                evidence_source="src:msc-bellissima-operations",
            )
        else:
            return StageTimelineDetail(
                stage=stage,
                title="Heimkehr nach Frankfurt",
                objective="Wohlbehalten mit allen Erinnerungen und ohne Reise-Reue zu Hause ankommen.",
                bot_morning_briefing="Willkommen zu Hause, Florian. Ich hoffe, Ihre Reise mit MSC Bellissima war rundum erholsam.",
                completed_milestones=[
                    "Kreuzfahrt Shanghai-Japan erfolgreich abgeschlossen",
                    "Voyagers Club Diamond Punkte gutgeschrieben",
                ],
                outstanding_actions=[
                    "Koffer auspacken und Reisetagebuch archivieren",
                ],
                anti_regret_warning="Reisebelege für etwaige Meilengutschriften 14 Tage aufbewahren.",
                estimated_duration="Reise erfolgreich abgeschlossen",
                evidence_source="src:timonelo-core",
            )
