"""
Port & City Intelligence Engine for Timonelo (Chapter III - Sprint 08).
"You only have eight hours ashore. How do I make those eight hours as enjoyable and stress-free as possible?"
Provides structured cruise port, shore-time buffer, gangway-to-city transfer,
and Negative Intelligence for world destinations with Bridge Officer Tim (BOT).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class TapWaterSafety(str, Enum):
    POTABLE_SAFE = "POTABLE_SAFE (Trinkwasserqualität aus dem Hahn)"
    BOTTLED_RECOMMENDED = "BOTTLED_RECOMMENDED (Abgefülltes Wasser empfohlen)"


@dataclass(frozen=True)
class GangwayStep:
    step_num: int
    title: str
    instruction: str
    typical_minutes: int
    orientation_hint: str


@dataclass(frozen=True)
class ShoreTimeWindow:
    scheduled_arrival: str
    scheduled_all_aboard: str
    recommended_latest_return: str
    safe_buffer_minutes: int
    rush_hour_warning_window: str
    safe_walking_radius_km: float


@dataclass(frozen=True)
class PortCityProfile:
    city_slug: str
    official_name: str
    country: str
    timezone: str
    currency: str
    language: str
    emergency_police: str
    emergency_medical: str
    plug_type: str
    tap_water: TapWaterSafety
    card_vs_cash_culture: str
    sim_esim_advice: str
    ride_hailing_apps: List[str]
    public_transport_summary: str
    walking_friendliness: str
    accessibility_notes: str
    weather_profile_summary: str
    terminal_name: str
    gangway_steps: List[GangwayStep]
    shore_time: ShoreTimeWindow
    negative_intelligence_traps: List[str]
    local_culinary_tips: List[str]
    bot_proactive_notices: List[str]
    evidence_sources: List[str]
    confidence_score: float = 99.5
    bot_closing_phrase: str = "Enjoy your time ashore. I will be here when you return."


class PortCityIntelligenceEngine:
    """Canonical registry of structured Port & City destination intelligence."""

    CITIES_REGISTRY: Dict[str, PortCityProfile] = {
        "yokohama": PortCityProfile(
            city_slug="yokohama",
            official_name="Yokohama (Greater Tokyo Port)",
            country="Japan",
            timezone="Asia/Tokyo (JST, UTC+9)",
            currency="Japanese Yen (¥ / JPY) · Suica / Credit Card accepted",
            language="Japanese",
            emergency_police="110",
            emergency_medical="119",
            plug_type="Type A (US/Japan 2-pin 100V)",
            tap_water=TapWaterSafety.POTABLE_SAFE,
            card_vs_cash_culture="Kartenzahlung & Suica IC Card ubiquitär; Kleingeld nur für Tempel & alte Ramen-Automaten.",
            sim_esim_advice="Ubigi eSIM oder Airalo für stabiles NTT Docomo Netz.",
            ride_hailing_apps=["GO (Japan Taxi App)", "S.RIDE", "Uber (Taxi Dispatch)"],
            public_transport_summary="Minatomirai Line (Station Nihon-odori 7 min zu Fuß) -> Direkte Züge nach Shibuya/Shinjuku (35 min).",
            walking_friendliness="Exzellent · Stufenfreie Uferpromenaden, breite Gehwege, höchste Fußgängersicherheit weltweit.",
            accessibility_notes="100% stufenfreies Terminal am Osanbashi Pier mit hölzernen Rampen (Kujira-no-Senaka).",
            weather_profile_summary="Mild und sonnig im Frühling/Herbst (18–22°C); Taifunsaison August/September beachten.",
            terminal_name="Yokohama Osanbashi International Passenger Terminal",
            gangway_steps=[
                GangwayStep(1, "Gangway Deck 5 verlassen", "Bordkarte am Ausgangsscanner vorhalten.", 3, "Deck 5 Steuerbord / Backbord"),
                GangwayStep(2, "Terminal Lobby Osanbashi", "Japanische Einreisekontrolle (Biometrie-Scan in 2 min).", 5, "Ebene 2 Haupthalle"),
                GangwayStep(3, "Fußweg zur Minatomirai Line", "Über den Osanbashi Pier zur Station Nihon-odori spazieren.", 7, "Ebener Gehweg Richtung Kaigandori"),
                GangwayStep(4, "Bahnfahrt nach Tokio", "Direktzug nach Shibuya (35 min, ca. 500 ¥ via Apple Wallet Suica).", 35, "Gleis 1 Richtung Shibuya/Ikebukuro"),
            ],
            shore_time=ShoreTimeWindow(
                scheduled_arrival="05:30 Uhr",
                scheduled_all_aboard="17:30 Uhr",
                recommended_latest_return="16:45 Uhr",
                safe_buffer_minutes=45,
                rush_hour_warning_window="17:00–18:30 Uhr in Tokioter Bahnhöfen (Shibuya/Shinagawa)",
                safe_walking_radius_km=4.5,
            ),
            negative_intelligence_traps=[
                "Niemals Taxis für die Langstrecke zwischen Tokio und Yokohama nehmen (Kosten > 100 €); die Bahn fährt alle 6 Minuten und kostet nur ~3,50 €.",
                "Tokioter Großbahnhöfe (Shinjuku/Tokyo Station) sind riesig: Für den Rückweg zum richtigen Gleis 15 Minuten zusätzliche Orientierungszeit einplanen.",
                "Öffentliche Mülleimer sind in Japan extrem selten; kleine Plastiktüte im Tagesrucksack für eigenen Abfall mitführen.",
            ],
            local_culinary_tips=[
                "Yokohama Chinatown (Chukagai): Größtes Chinatown Asiens, nur 15 min zu Fuß von Osanbashi – berühmt für gedämpfte Nikuman-Teigtaschen.",
                "Shin-Yokohama Ramen Museum: Historische Rekonstruktion mit den 7 besten regionalen Ramen-Küchen Japans.",
            ],
            bot_proactive_notices=[
                "BOT noticed: Heute liegt das Schiff an Osanbashi – dem schönsten Pier Japans mit direktem Blick auf die Skyline.",
                "BOT noticed: Die Minatomirai-Bahn akzeptiert Suica auf der Apple Watch / Smartphone. Kein Ticketkauf am Automaten nötig.",
            ],
            evidence_sources=["src:port-authority-yokohama", "src:japan-coast-guard", "src:field-audit-2026"],
        ),

        "shanghai": PortCityProfile(
            city_slug="shanghai",
            official_name="Shanghai (Wusongkou Baoshan Port)",
            country="China",
            timezone="Asia/Shanghai (CST, UTC+8)",
            currency="Chinese Yuan (¥ / CNY) · Alipay / WeChat Pay Pflicht",
            language="Mandarin (Simplified Chinese)",
            emergency_police="110",
            emergency_medical="120",
            plug_type="Type I & Type A/C (220V)",
            tap_water=TapWaterSafety.BOTTLED_RECOMMENDED,
            card_vs_cash_culture="100% bargeldlos via QR-Code (Alipay TourCard mit Visa/Mastercard verknüpft). Bargeld wird kaum gewechselt.",
            sim_esim_advice="Airalo / Holafly eSIM mit integriertem VPN für Google/WhatsApp unverzichtbar.",
            ride_hailing_apps=["Didi (integriert in Alipay auf Englisch)"],
            public_transport_summary="Shuttle/Taxi zur Metro Linie 3 (Baoyang Road) -> Linie 3/2 zum Bund und People's Square.",
            walking_friendliness="Am Bund & in der Französischen Konzession hervorragend; rund um das Kreuzfahrtterminal Baoshan nur Industrie/Hafen.",
            accessibility_notes="Wusongkou Terminal hat lange ebene Rollsteige und Fahrstühle; Distanzen innerhalb des Terminals sind weit (bis zu 400 m).",
            weather_profile_summary="Subtropisch feucht; Herbst (Oktober) mit angenehmen 20–24°C die beste Reisezeit.",
            terminal_name="Shanghai Wusongkou International Cruise Terminal (Baoshan)",
            gangway_steps=[
                GangwayStep(1, "Gangway Deck 5", "Bordkarte scannen und Zollzettel bereithalten.", 4, "Terminal Fluggastbrücke"),
                GangwayStep(2, "Pass- & Sicherheitskontrolle T1/T2", "Schnelle automatische Gesichtserkennung für Transitgäste.", 6, "Zollhalle"),
                GangwayStep(3, "Offizieller Taxistand / Didi Pickup", "Didi-App öffnen und 'Gate 2 Passenger Pickup' wählen.", 8, "Vorplatz T1"),
                GangwayStep(4, "Fahrt ins Zentrum (Bund)", "Didi Fahrt über die Wusongkou Elevated Highway zum Bund (45–60 min).", 50, "Ziel: The Bund / People's Square"),
            ],
            shore_time=ShoreTimeWindow(
                scheduled_arrival="07:00 Uhr",
                scheduled_all_aboard="17:00 Uhr",
                recommended_latest_return="15:45 Uhr",
                safe_buffer_minutes=75,
                rush_hour_warning_window="16:00–18:30 Uhr auf dem North-South Elevated Highway",
                safe_walking_radius_km=3.0,
            ),
            negative_intelligence_traps=[
                "Niemals inoffizielle Taxifahrer annehmen, die Sie in der Ankunftshalle ansprechen – immer die Didi-App oder die offizielle Warteschlange nutzen.",
                "Teehaus-Scam am Bund: Junge Leute, die vorgeben, Englisch üben zu wollen und Sie zum Tee einladen (Kosten oft hunderte Euro).",
                "Zieladresse für Taxifahrer immer in chinesischen Schriftzeichen (上海吴淞口国际邮轮港) bereithalten.",
            ],
            local_culinary_tips=[
                "Xiao Long Bao (Suppen-Dumplings) bei Din Tai Fung oder Jia Jia Tang Bao am People's Square.",
                "Shengjianbao (gebratene Schweinefleisch-Knödel mit krossem Boden) bei Yang's Fried Dumplings.",
            ],
            bot_proactive_notices=[
                "BOT noticed: Wusongkou liegt 24 km nördlich des Bunds. Planen Sie für die Rückfahrt mindestens 75 Minuten Puffer ein.",
                "BOT noticed: Google Maps hat in China GPS-Versatz. Nutzen Sie Apple Maps für präzise Fußgängernavigation.",
            ],
            evidence_sources=["src:port-authority-shanghai", "src:field-audit-2026"],
        ),

        "genoa": PortCityProfile(
            city_slug="genoa",
            official_name="Genua (Genova Stazione Marittima)",
            country="Italy",
            timezone="Europe/Rome (CEST, UTC+2)",
            currency="Euro (€ / EUR)",
            language="Italian",
            emergency_police="112",
            emergency_medical="118",
            plug_type="Type C / F / L (230V)",
            tap_water=TapWaterSafety.POTABLE_SAFE,
            card_vs_cash_culture="Kreditkarten überall akzeptiert; kleine Beträge für Espresso (1,20 €) in Bar oft bar bevorzugt.",
            sim_esim_advice="EU-Roaming gilt für europäische SIM-Karten.",
            ride_hailing_apps=["FreeNow", "ItTaxi", "Uber (Black/Van)"],
            public_transport_summary="Metro Principe direkt neben dem Terminal; Bahnhof Genova Piazza Principe in 5 min ebenerdiger Fußweg.",
            walking_friendliness="Hafen und Via Balbi/Via Garibaldi perfekt zu Fuß; Altstadt (Caruggi) steil und kopfsteingepflastert.",
            accessibility_notes="Ponte dei Mille ist über Aufzüge direkt mit der Fußgänger-Skybridge zur Piazza Principe verbunden.",
            weather_profile_summary="Mediterran; Ligurien ist im Frühjahr und Herbst mild (19–23°C).",
            terminal_name="Stazione Marittima di Genova (Ponte dei Mille & Andrea Doria)",
            gangway_steps=[
                GangwayStep(1, "Gangway Deck 5 Ponte dei Mille", "Bordkarte scannen.", 2, "Historisches Terminalgebäude"),
                GangwayStep(2, "Terminal Ausgang & Skybridge", "Über die verglaste Fußgängerbrücke zur Piazza Principe gehen.", 5, "Skybridge Richtung Bahnhof"),
                GangwayStep(3, "Via Balbi & UNESCO-Paläste", "Zu Fuß die Via Balbi hinunter zu den Palazzi dei Rolli spazieren.", 10, "Historische Prachtstraße"),
            ],
            shore_time=ShoreTimeWindow(
                scheduled_arrival="08:00 Uhr",
                scheduled_all_aboard="18:00 Uhr",
                recommended_latest_return="17:15 Uhr",
                safe_buffer_minutes=45,
                rush_hour_warning_window="17:30–18:30 Uhr rund um Piazza Acquaverde",
                safe_walking_radius_km=3.5,
            ),
            negative_intelligence_traps=[
                "Niemals Taxis für die 400 Meter zwischen Schiff und Bahnhof Piazza Principe nehmen (stufenfreier Fußweg dauert 5 Minuten).",
                "Altstadtgassen (Caruggi) nachts oder bei Dunkelheit meiden; tagsüber auf Hauptwegen (Via San Luca/Via Luccoli) bleiben.",
                "Vor dem Auslaufen Flugmodus aktivieren: Das ligurische Meer aktiviert schnell maritime Satelliten-Roamingnetze.",
            ],
            local_culinary_tips=[
                "Focaccia Genovese: Frisch gebacken in der Pasticceria/Panificio am Porto Antico in Cappuccino tunken.",
                "Trofiette al Pesto Genovese: Authentisches Basilikum-Pesto mit Pinienkernen und Pecorino in einer Trattoria in der Via Garibaldi.",
            ],
            bot_proactive_notices=[
                "BOT noticed: Das Terminal liegt direkt am Stadtzentrum. Sie können das historische Genua zu 100% zu Fuß erkunden.",
            ],
            evidence_sources=["src:port-authority-genoa", "src:field-audit-genoa-2026"],
        ),

        "naples": PortCityProfile(
            city_slug="naples",
            official_name="Neapel (Napoli Stazione Marittima Molo Beverello)",
            country="Italy",
            timezone="Europe/Rome (CEST, UTC+2)",
            currency="Euro (€ / EUR)",
            language="Italian",
            emergency_police="112",
            emergency_medical="118",
            plug_type="Type C / F / L (230V)",
            tap_water=TapWaterSafety.POTABLE_SAFE,
            card_vs_cash_culture="Kartenzahlung weit verbreitet; für Espresso & Sfogliatella kleine Euro-Münzen bereithalten.",
            sim_esim_advice="EU-Roaming gilt für europäische SIMs.",
            ride_hailing_apps=["FreeNow", "ItTaxi"],
            public_transport_summary="Metro Linie 1 (Station Municipio) liegt direkt gegenüber dem Terminalvorplatz (2 min Fußweg).",
            walking_friendliness="Sehr gut vom Hafen zum Castel Nuovo, Galleria Umberto und Piazza del Plebiscito.",
            accessibility_notes="Molo Beverello Terminal ist modernisiert und barrierefrei; Metro Municipio verfügt über Aufzüge.",
            weather_profile_summary="Mediterran sonnig; im Sommer heiß (bis 32°C), Herbst angenehm (22–25°C).",
            terminal_name="Stazione Marittima di Napoli (Molo Angioino & Beverello)",
            gangway_steps=[
                GangwayStep(1, "Gangway Deck 5", "Bordkartenscan am Pier.", 2, "Molo Angioino"),
                GangwayStep(2, "Terminalausgang Piazza Municipio", "Vorbei am Castel Nuovo zur Metro Municipio gehen.", 4, "Piazza Municipio"),
                GangwayStep(3, "Metro Linie 1", "3 Stationen bis Dante oder 4 Stationen bis Museo (Altstadt).", 8, "Metro L1"),
            ],
            shore_time=ShoreTimeWindow(
                scheduled_arrival="07:00 Uhr",
                scheduled_all_aboard="17:00 Uhr",
                recommended_latest_return="16:15 Uhr",
                safe_buffer_minutes=45,
                rush_hour_warning_window="16:30–18:00 Uhr rund um Via Marina",
                safe_walking_radius_km=3.0,
            ),
            negative_intelligence_traps=[
                "Taxipreise immer VOR dem Einsteigen als Festpreis (Tariffa Predefinita nach Gesetz) vereinbaren – z.B. 15 € nach Spaccanapoli.",
                "Taschendiebe rund um Piazza Garibaldi und in der überfüllten Circumvesuviana-Bahn nach Pompeji; Wertsachen eng am Körper tragen.",
                "Fähren nach Capri bei unruhigem Seegang vermeiden; Rückkehrfähren können bei Nachmittagswind ausfallen.",
            ],
            local_culinary_tips=[
                "Pizza Margherita nach STG-Standard bei Sorbillo (Via dei Tribunali) oder L'Antica Pizzeria da Michele.",
                "Sfogliatella Riccia (knuspriges Blätterteiggebäck mit Ricotta) bei Pintauro in der Via Toledo.",
            ],
            bot_proactive_notices=[
                "BOT noticed: Die Metro Municipio liegt genau gegenüber dem Pier. Sie erreichen das historische Zentrum in unter 10 Minuten.",
            ],
            evidence_sources=["src:port-authority-naples", "src:field-audit-2026"],
        ),

        "barcelona": PortCityProfile(
            city_slug="barcelona",
            official_name="Barcelona (Moll Adossat & Port Vell)",
            country="Spain",
            timezone="Europe/Madrid (CEST, UTC+2)",
            currency="Euro (€ / EUR)",
            language="Spanish / Catalan",
            emergency_police="112",
            emergency_medical="061",
            plug_type="Type C / F (230V)",
            tap_water=TapWaterSafety.POTABLE_SAFE,
            card_vs_cash_culture="Kartenzahlung / Apple Pay 100% akzeptiert.",
            sim_esim_advice="EU-Roaming gilt für europäische SIMs.",
            ride_hailing_apps=["FreeNow", "Cabify", "Uber"],
            public_transport_summary="Blauer T3 Cruise Bus (Portbus, 3 €) vom Moll Adossat zum Kolumbus-Denkmal -> Metro L3 Drassanes.",
            walking_friendliness="Innenstadt traumhaft zu Fuß; die Hafenbrücke (Pont d'Europa) vom Moll Adossat ist NICHT fußgängerfreundlich.",
            accessibility_notes="T3 Portbusse sind 100% niederflurig und rollstuhlgerecht mit Klapprampe.",
            weather_profile_summary="Mediterran sonnig; ganzjährig mild.",
            terminal_name="Moll Adossat Cruise Terminals (A, B, C, D, E, Helix)",
            gangway_steps=[
                GangwayStep(1, "Gangway Deck 5", "Bordkartenscan.", 2, "Terminal Vorplatz"),
                GangwayStep(2, "T3 Portbus Einstieg", "Direkt vor dem Terminalgebäude in den blauen T3 Portbus einsteigen.", 4, "3 € Ticket beim Fahrer"),
                GangwayStep(3, "Fahrt zum Kolumbus-Denkmal", "Über die Hafenbrücke zum Fuß der Ramblas fahren.", 12, "Haltestelle Portal de la Pau"),
            ],
            shore_time=ShoreTimeWindow(
                scheduled_arrival="08:00 Uhr",
                scheduled_all_aboard="18:00 Uhr",
                recommended_latest_return="17:00 Uhr",
                safe_buffer_minutes=60,
                rush_hour_warning_window="17:00–18:30 Uhr auf Passeig de Colom",
                safe_walking_radius_km=4.0,
            ),
            negative_intelligence_traps=[
                "Niemals zu Fuß über die 2,5 km lange Hafenbrücke (Pont d'Europa) laufen – es gibt keine Schattenplätze und heftige Winde.",
                "Las Ramblas, Plaça Reial und Metrostation Sagrada Família sind Hotspots professioneller Taschendiebe; Rucksäcke vorne tragen.",
                "Achten Sie genau auf Ihren Terminalbuchstaben (A–E) für die Rückfahrt mit dem T3 Bus; die Terminals liegen bis zu 1,5 km auseinander.",
            ],
            local_culinary_tips=[
                "Tapas im Mercat de la Boqueria oder El Xampanyet im El Born Viertel.",
                "Katalanische Paella im Fischerviertel Barceloneta (z.B. Can Solé oder 7 Portes).",
            ],
            bot_proactive_notices=[
                "BOT noticed: Nutzen Sie für die Rückkehr zum Schiff den blauen T3 Portbus ab Kolumbus-Denkmal spätestens um 16:30 Uhr.",
            ],
            evidence_sources=["src:port-authority-barcelona", "src:field-audit-2026"],
        ),

        "singapore": PortCityProfile(
            city_slug="singapore",
            official_name="Singapur (Marina Bay Cruise Centre MBCCS)",
            country="Singapore",
            timezone="Asia/Singapore (SGT, UTC+8)",
            currency="Singapore Dollar (S$ / SGD) · Kartenzahlung & EZ-Link ubiquitär",
            language="English / Mandarin / Malay",
            emergency_police="999",
            emergency_medical="995",
            plug_type="Type G (UK 3-pin 230V)",
            tap_water=TapWaterSafety.POTABLE_SAFE,
            card_vs_cash_culture="100% bargeldlos; Visa/Mastercard kontaktlos an allen MRT-Schranken und Taxis.",
            sim_esim_advice="Singtel / StarHub / Airalo eSIM.",
            ride_hailing_apps=["Grab", "Gojek", "CDG Zig (ComfortDelGro Taxi)"],
            public_transport_summary="MRT Station Marina South Pier (North-South Line) ist in 600m über einen überdachten Gang erreichbar.",
            walking_friendliness="Sehr sauber und sicher; extrem hohe Luftfeuchtigkeit, daher überdachte Passagen und klimatisierte MRT nutzen.",
            accessibility_notes="MBCCS und das gesamte MRT-Netz in Singapur sind zu 100% barrierefrei und stufenlos ausgebaut.",
            weather_profile_summary="Tropisch warm (30–32°C) mit täglichen kurzen Nachmittagsschauern.",
            terminal_name="Marina Bay Cruise Centre Singapore (MBCCS)",
            gangway_steps=[
                GangwayStep(1, "Gangway Deck 5 MBCCS", "Bordkartenscan & biometrische Zollschranke.", 3, "Terminal 2F"),
                GangwayStep(2, "Überdachter Gang zur MRT", "600 m überdachter Fußweg zur Station Marina South Pier.", 7, "Ausschilderung 'MRT Station'"),
                GangwayStep(3, "MRT Fahrt nach Marina Bay", "North-South Line direkt zu Marina Bay / Raffles Place.", 6, "MRT NS28"),
            ],
            shore_time=ShoreTimeWindow(
                scheduled_arrival="07:00 Uhr",
                scheduled_all_aboard="19:00 Uhr",
                recommended_latest_return="18:00 Uhr",
                safe_buffer_minutes=60,
                rush_hour_warning_window="18:00–19:30 Uhr im Finanzdistrikt",
                safe_walking_radius_km=3.0,
            ),
            negative_intelligence_traps=[
                "Kaugummi-Einfuhr ist in Singapur streng verboten (Zollstrafen bis zu 1.000 SGD).",
                "Rauchen nur in streng markierten gelben Zonen; Wegwerfen von Müll zieht sofortige Geldstrafen nach sich.",
                "Taxis am Terminal haben bei Kreuzfahrtankünften teilweise lange Schlangen; die MRT-Bahn Marina South Pier ist staufrei.",
            ],
            local_culinary_tips=[
                "Hainanese Chicken Rice bei Tian Tian im Maxwell Food Centre.",
                "Satay-Spieße im abendlichen Lau Pa Sat Hawker Centre unter freiem Himmel.",
            ],
            bot_proactive_notices=[
                "BOT noticed: Die MRT-Station Marina South Pier ist über einen überdachten Fußweg direkt vom Terminal erreichbar.",
            ],
            evidence_sources=["src:port-authority-singapore", "src:singapore-tourism-board"],
        ),
    }

    @classmethod
    def get_destination_profile(cls, city_slug: str) -> Optional[PortCityProfile]:
        return cls.CITIES_REGISTRY.get(city_slug.lower())

    @classmethod
    def list_all_destinations(cls) -> List[PortCityProfile]:
        return list(cls.CITIES_REGISTRY.values())
