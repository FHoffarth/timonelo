"""
Destination Intelligence Engine for Timonelo (Chapter III - Sprint 05).
Provides structured, non-hallucinated operational guides for arrival airports, transfers,
cruise terminals, hotel zones, and local negative intelligence across major world ports.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from .destination_schema import (
    DestinationIntelligence,
    AirportTransferOption,
    CruiseTerminalLayout,
    PowerPlugType,
)


class DestinationIntelligenceEngine:
    """Canonical registry and lookup for port city operational destination intelligence."""

    DESTINATIONS: Dict[str, DestinationIntelligence] = {
        "shanghai": DestinationIntelligence(
            port_slug="shanghai",
            city_name="Shanghai",
            country="China",
            primary_language="Mandarin (Simplified Chinese)",
            currency="Chinese Yuan (¥ / CNY) · Alipay / WeChat Pay ubiquitous",
            timezone="Asia/Shanghai (CST, UTC+8)",
            power_plugs=PowerPlugType.TYPE_I,
            sim_esim_recommendation="Airalo / Nomad eSIM or Holafly (VPN-enabled) for Google/WhatsApp access.",
            emergency_phone_police="110",
            emergency_phone_medical="120",
            local_transport_card="Shanghai Public Transportation Card / Alipay Metro QR",
            airports=[
                AirportTransferOption(
                    airport_name="Shanghai Pudong International Airport",
                    iata_code="PVG",
                    distance_to_terminal_km=58.0,
                    best_transit_mode="Maglev to Longyang Rd -> Metro Line 3 to Baoyang Rd -> 10-min taxi, or direct Didi Taxi (approx. 70 min).",
                    typical_duration_min=75,
                    estimated_cost_range="¥180 - ¥260 (Didi) / ¥60 (Maglev+Metro)",
                    negative_intelligence="Niemals inoffizielle Taxifahrer in der Ankunftshalle annehmen. Immer die offizielle Taxi-Warteschlange im Untergeschoss oder die Didi-App nutzen.",
                    evidence_source="src:shanghai-airport-authority",
                ),
                AirportTransferOption(
                    airport_name="Shanghai Hongqiao International Airport",
                    iata_code="SHA",
                    distance_to_terminal_km=34.0,
                    best_transit_mode="Metro Line 10/2 to Zhongshan Park -> Metro Line 3 to Baoyang Rd, or direct Didi (approx. 50 min).",
                    typical_duration_min=50,
                    estimated_cost_range="¥120 - ¥180 (Didi)",
                    negative_intelligence="Hongqiao ist deutlich näher am Terminal als Pudong, bedient aber primär Inlands- und Regionalflüge.",
                    evidence_source="src:shanghai-airport-authority",
                ),
            ],
            terminals=[
                CruiseTerminalLayout(
                    terminal_name="Wusongkou International Cruise Terminal (Baoshan)",
                    berths=["Berth 1", "Berth 2", "Berth 3", "Berth 4"],
                    porter_dropoff_location="Main Terminal Gate 2 Baggage Drop Area (Vorzone T1/T2)",
                    security_lane_notes="Strenge Zollkontrolle. Powerbanks müssen CE-Kennzeichnung haben und im Handgepäck geführt werden.",
                    distance_to_city_center_km=24.0,
                    nearest_metro_or_train="Metro Line 3 (Baoyang Road Station) + 8-min Taxi/Shuttle",
                    negative_intelligence="Das Terminal liegt 24 km nördlich des Stadtzentrums. Keine Fußwege vom Zentrum möglich. Bei Regen verlängern sich Didi-Wartezeiten am Terminal auf bis zu 30 Minuten.",
                )
            ],
            recommended_hotel_zones=[
                "Baoshan District (10–15 min zum Terminal für entspannten Einschiffungsmorgen)",
                "Pudong Lujiazui (45–60 min zum Terminal, erstklassige internationale Hotels)",
                "The Bund / People's Square (40–50 min zum Terminal, historisches Zentrum)"
            ],
            negative_intelligence_top_3=[
                "Niemals am Tag der Einschiffung einfliegen: Wusongkou liegt weit im Norden; Passkontrolle und Transfer dauern mindestens 2,5 Stunden.",
                "Zahlungen: Internationale Kreditkarten (Visa/Mastercard) werden in Taxis und kleinen Geschäften kaum akzeptiert; Alipay oder WeChat Pay vorab mit Kreditkarte verknüpfen.",
                "Zieladresse immer in chinesischen Schriftzeichen (上海吴淞口国际邮轮港) auf dem Smartphone bereithalten, da Taxifahrer kein Englisch sprechen."
            ],
            evidence_sources=["src:port-authority-shanghai", "src:field-audit-2026", "src:official-cruise-line-schedule"],
            confidence_score=99.0,
        ),

        "tokyo-yokohama": DestinationIntelligence(
            port_slug="tokyo-yokohama",
            city_name="Yokohama / Tokio",
            country="Japan",
            primary_language="Japanese",
            currency="Japanese Yen (¥ / JPY) · Suica/Pasmo & Credit Cards accepted",
            timezone="Asia/Tokyo (JST, UTC+9)",
            power_plugs=PowerPlugType.TYPE_A,
            sim_esim_recommendation="Ubigi eSIM oder Mobal Japan SIM für unterbrechungsfreies NTT Docomo Netz.",
            emergency_phone_police="110",
            emergency_phone_medical="119",
            local_transport_card="Suica / Pasmo IC Card (Apple Wallet kompatibel)",
            airports=[
                AirportTransferOption(
                    airport_name="Tokyo Haneda Airport",
                    iata_code="HND",
                    distance_to_terminal_km=22.0,
                    best_transit_mode="Keikyu Airport Line direct to Yokohama Station (approx. 25 min) -> Minatomirai Line to Nihon-odori.",
                    typical_duration_min=35,
                    estimated_cost_range="¥450 (Zug) / ¥9.000 (Taxi)",
                    negative_intelligence="Haneda ist der mit Abstand beste Flughafen für Kreuzfahrten ab Yokohama. Taxis sind teuer; der Keikyu-Zug ist schneller und fährt alle 10 Minuten.",
                    evidence_source="src:tokyo-haneda-airport",
                ),
                AirportTransferOption(
                    airport_name="Tokyo Narita International Airport",
                    iata_code="NRT",
                    distance_to_terminal_km=98.0,
                    best_transit_mode="JR Narita Express (N'EX) direct to Yokohama Station (approx. 90 min).",
                    typical_duration_min=95,
                    estimated_cost_range="¥4.370 (N'EX) / ¥35.000+ (Taxi)",
                    negative_intelligence="Niemals ein reguläres Taxi von Narita nach Yokohama nehmen (Kosten > 250 €). Immer den direkten Narita Express (N'EX) buchen.",
                    evidence_source="src:narita-airport-authority",
                ),
            ],
            terminals=[
                CruiseTerminalLayout(
                    terminal_name="Yokohama Osanbashi International Passenger Terminal",
                    berths=["Shinko Pier", "Osanbashi Pier", "Daikoku Pier"],
                    porter_dropoff_location="Ground Floor Dropoff Loop directly in front of Main Lobby",
                    security_lane_notes="Hocheffiziente japanische Einreise- und Sicherheitskontrolle mit Biometrie-Scannern.",
                    distance_to_city_center_km=1.5,
                    nearest_metro_or_train="Minatomirai Line (Nihon-odori Station) · 7 min level walk",
                    negative_intelligence="Prüfen Sie vorab, ob Ihr Schiff an Osanbashi (Zentrum) oder Daikoku Pier (Industriehafen für Megaliner) anlegt. Zu Daikoku gibt es keine direkte Bahnverbindung; es verkehren Reederei-Shuttles ab Bahnhof Sakuragicho.",
                )
            ],
            recommended_hotel_zones=[
                "Yokohama Minatomirai (5–10 min zum Pier, moderne Hotels mit Blick auf den Hafen)",
                "Yokohama Station / Sakuragicho (direkte Bahn-Knotenpunkte zu beiden Flughäfen)",
                "Tokio Shinjuku / Ginza (35–45 min Bahnfahrt nach Yokohama Station)"
            ],
            negative_intelligence_top_3=[
                "Yokohama ist eine eigenständige Millionenstadt und liegt 35 km südlich von Tokio; nicht mit dem Zentrum von Tokio verwechseln.",
                "Öffentliche Verkehrsmittel in Japan fahren nachts zwischen 00:30 und 05:00 Uhr nicht; Nachtankünfte erfordern vorab organisierte Shuttles.",
                "Gepäck-Lieferservice (Takkyubin/Yamato Transport) ist extrem zuverlässig: Koffer können direkt vom Flughafen zum Kreuzfahrthotel vorgeschickt werden."
            ],
            evidence_sources=["src:port-authority-yokohama", "src:japan-coast-guard", "src:field-audit-2026"],
            confidence_score=99.5,
        ),

        "genoa": DestinationIntelligence(
            port_slug="genoa",
            city_name="Genua (Genova)",
            country="Italy",
            primary_language="Italian",
            currency="Euro (€ / EUR)",
            timezone="Europe/Rome (CEST, UTC+2)",
            power_plugs=PowerPlugType.TYPE_C_F,
            sim_esim_recommendation="EU-Roaming gilt für europäische SIMs. Reisende außerhalb der EU: Airalo / Vodafone IT.",
            emergency_phone_police="112",
            emergency_phone_medical="118",
            local_transport_card="AMT Genova Single/24h Ticket (via AMT App)",
            airports=[
                AirportTransferOption(
                    airport_name="Genoa Cristoforo Colombo Airport",
                    iata_code="GOA",
                    distance_to_terminal_km=6.5,
                    best_transit_mode="Volabus Shuttle direkt zum Bahnhof Genova Piazza Principe (18 min, 6 €) oder Taxi (15 € Pauschale).",
                    typical_duration_min=20,
                    estimated_cost_range="6 € (Volabus) / 15 € (Taxi Festpreis)",
                    negative_intelligence="Der Flughafen Genua ist klein und nah. Taxis haben einen gesetzlichen Pauschaltarif von 15 € zum Bahnhof Principe/Hafen; lehnen Sie höhere Forderungen ab.",
                    evidence_source="src:port-authority-genoa",
                ),
                AirportTransferOption(
                    airport_name="Milan Malpensa Airport",
                    iata_code="MXP",
                    distance_to_terminal_km=180.0,
                    best_transit_mode="Malpensa Express zum Bahnhof Milano Centrale (50 min) -> Trenitalia Intercity nach Genova Piazza Principe (95 min).",
                    typical_duration_min=160,
                    estimated_cost_range="25 € - 35 € (Bahn gesamt)",
                    negative_intelligence="Bei Landung in Mailand Malpensa mindestens 4 Stunden Pufferzeit bis zum Einschiffungsschluss in Genua einplanen.",
                    evidence_source="src:trenitalia-official",
                ),
            ],
            terminals=[
                CruiseTerminalLayout(
                    terminal_name="Stazione Marittima di Genova (Ponte dei Mille & Andrea Doria)",
                    berths=["Ponte dei Mille Levante", "Ponte dei Mille Ponente", "Ponte Andrea Doria"],
                    porter_dropoff_location="Erdgeschoss-Kofferabgabe direkt an den Terminaleingängen Ponte dei Mille",
                    security_lane_notes="Ebene Glasaufzüge verbinden das Terminal direkt mit der Fußgängerbrücke zur Piazza Principe.",
                    distance_to_city_center_km=0.5,
                    nearest_metro_or_train="Bahnhof Genova Piazza Principe & Metro Principe (5–8 min ebener Fußweg)",
                    negative_intelligence="Ponte dei Mille (z.B. MSC Bellissima) und Ponte Andrea Doria sind zwei benachbarte Gebäude; prüfen Sie Ihr Einschiffungsticket, welches Terminal zugewiesen ist.",
                )
            ],
            recommended_hotel_zones=[
                "Piazza Principe / Via Balbi (5–8 min ebener Fußweg zum Kreuzfahrtterminal)",
                "Porto Antico (15 min ebener Spaziergang am Yachthafen entlang)",
                "Piazza De Ferrari / Centro Storico (15 min per Metro oder 20 min Fußweg)"
            ],
            negative_intelligence_top_3=[
                "Die historische Altstadt (Caruggi) ist nachts verwinkelt und für Rollkoffer wegen historischem Kopfsteinpflaster ungeeignet; für Hotelanreise immer die Hauptstraßen (Via Balbi/Via Garibaldi) nutzen.",
                "Piazza Principe ist 100% stufenfrei über die überdachte Fußgängerbrücke erreichbar – keine teuren Taxis für 400 Meter Distanz nötig.",
                "Vor dem Auslaufen Flugmodus aktivieren: Das ligurische Meer aktiviert schnell maritime Satellitenfunknetze mit horrenden Roaminggebühren."
            ],
            evidence_sources=["src:port-authority-genoa", "src:field-audit-genoa-2026", "src:msc-cruises-official"],
            confidence_score=100.0,
        ),

        "barcelona": DestinationIntelligence(
            port_slug="barcelona",
            city_name="Barcelona",
            country="Spain",
            primary_language="Spanish / Catalan",
            currency="Euro (€ / EUR)",
            timezone="Europe/Madrid (CEST, UTC+2)",
            power_plugs=PowerPlugType.TYPE_C_F,
            sim_esim_recommendation="EU-Roaming für EU-Gäste; Movistar / Orange / Airalo eSIM.",
            emergency_phone_police="112",
            emergency_phone_medical="061",
            local_transport_card="T-casual / T-familiar Card (TMB Metro/Bus)",
            airports=[
                AirportTransferOption(
                    airport_name="Josep Tarradellas Barcelona-El Prat Airport",
                    iata_code="BCN",
                    distance_to_terminal_km=16.0,
                    best_transit_mode="Offizielles Taxi (Fahrzeit 20-25 min, ca. 35-45 €) oder Aerobús nach Plaça Catalunya + T3 Cruise Bus ab Kolumbus-Säule.",
                    typical_duration_min=30,
                    estimated_cost_range="35 € - 45 € (Taxi) / 7.25 € (Aerobus) + 3 € (Portbus)",
                    negative_intelligence="Taxis vom Flughafen zum Hafen haben einen Hafenzuschlag (ca. 4,50 €), der legal auf dem Taxameter erscheint. Nutzen Sie ausschließlich die offizielle Taxi-Warteschlange am Terminal T1/T2.",
                    evidence_source="src:barcelona-airport-aena",
                )
            ],
            terminals=[
                CruiseTerminalLayout(
                    terminal_name="Moll Adossat Cruise Terminals (Terminals A, B, C, D, E, Helix)",
                    berths=["Terminal A", "Terminal B", "Terminal C", "Terminal D", "Terminal E"],
                    porter_dropoff_location="Direkte Vorfahrt vor dem jeweiligen Terminal-Buchstaben",
                    security_lane_notes="Sehr großes, modernes Terminalareal mit getrennten Zonen je Schiff.",
                    distance_to_city_center_km=3.5,
                    nearest_metro_or_train="Metro L3 (Drassanes) + Blauer T3 Portbus (Cruise Shuttle) ab Kolumbus-Denkmal",
                    negative_intelligence="Moll Adossat ist NICHT zu Fuß aus der Stadt erreichbar (lange, schattenlose Hafenbrücke von 2,5 km). Immer den offiziellen blauen T3 Cruise Bus (3 € Barzahlung/Karte) ab Kolumbus-Denkmal oder ein Taxi nehmen.",
                )
            ],
            recommended_hotel_zones=[
                "Poblesec / Paral·lel (10 min per Taxi oder Portbus zum Terminal)",
                "Plaça d'Espanya (direkte Aerobús-Verbindung vom Flughafen und kurze Taxifahrt zum Hafen)",
                "Eixample / Passeig de Gràcia (zentral, sicher und gehoben)"
            ],
            negative_intelligence_top_3=[
                "Las Ramblas und Gotisches Viertel sind extreme Taschendieb-Schwerpunkte; Rucksäcke vorne tragen und Smartphones in belebten Metrostationen nicht lose in der Hand halten.",
                "Versuchen Sie niemals, mit Koffern über die Hafenbrücke (Pont d'Europa) zu laufen – es gibt keinen durchgehenden Fußgängerschutz vor Wind und Hitze.",
                "Achten Sie genau auf den Terminal-Buchstaben (A, B, C, D oder E) auf Ihrer Bordkarte, da die Terminals auf dem Pier bis zu 1,5 km auseinander liegen."
            ],
            evidence_sources=["src:port-authority-barcelona", "src:field-audit-2026"],
            confidence_score=99.5,
        ),
    }

    @classmethod
    def get_destination_by_slug(cls, port_slug: str) -> Optional[DestinationIntelligence]:
        return cls.DESTINATIONS.get(port_slug)

    @classmethod
    def list_all_destinations(cls) -> List[DestinationIntelligence]:
        return list(cls.DESTINATIONS.values())
