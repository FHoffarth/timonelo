"""
World's First Cruise Genome Engine.
Computes multidimensional experiential DNA profiles, similarity vectors, and explainable passenger matching.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import math
import json


class ShipArchetype(str, Enum):
    MEGA_RESORT_INNOVATOR = "MEGA_RESORT_INNOVATOR"
    ELEGANT_PROMENADE_CONTEMPORARY = "ELEGANT_PROMENADE_CONTEMPORARY"
    MODERN_OUTWARD_FACING_LUXURY = "MODERN_OUTWARD_FACING_LUXURY"
    FREESTYLE_THRILL_SEEKER = "FREESTYLE_THRILL_SEEKER"
    INTIMATE_SCENIC_RIVER_YACHT = "INTIMATE_SCENIC_RIVER_YACHT"
    ADULTS_ONLY_CONTEMPORARY = "ADULTS_ONLY_CONTEMPORARY"
    TRADITIONAL_OCEAN_LINER = "TRADITIONAL_OCEAN_LINER"
    EXPEDITION_DISCOVERY_YACHT = "EXPEDITION_DISCOVERY_YACHT"


@dataclass(frozen=True)
class CruiseDNADimensions:
    atmosphere_energy: float       # 0.0 (Serene/Quiet) to 1.0 (High Energy/Party)
    luxury_level: float            # 0.0 (Budget/Standard) to 1.0 (6-Star Ultra-Luxury)
    family_and_kids: float         # 0.0 (Adults-Only) to 1.0 (Extensive Kids Clubs/Waterparks)
    adventure_and_thrills: float   # 0.0 (None) to 1.0 (Coasters, Racetracks, Slides)
    nightlife_and_parties: float   # 0.0 (Quiet Evenings) to 1.0 (DJ Clubs, Gala Parties)
    quiet_sanctuaries: float       # 0.0 (Few quiet spots) to 1.0 (Abundant serene lounges)
    space_ratio_calm: float        # 0.0 (High density crowding) to 1.0 (Spacious/Uncrowded)
    walking_compactness: float     # 0.0 (Huge mega-sprawl 360m) to 1.0 (Intimate compact 80-130m)
    accessibility_ease: float      # 0.0 (Standard) to 1.0 (Exceptional step-free/lift ratio)
    food_variety_and_craft: float  # 0.0 (Standard buffet) to 1.0 (Michelin/Specialty variety)
    outdoor_deck_promenade: float  # 0.0 (Enclosed) to 1.0 (Expansive open-air ocean decks)
    scenic_and_destination: float  # 0.0 (Ship-is-destination) to 1.0 (Port-focused scenic immersion)
    pool_and_water_focus: float    # 0.0 (Small plunge) to 1.0 (Multiple pools, aquaparks)
    entertainment_theatre: float   # 0.0 (Enrichment lectures) to 1.0 (Broadway productions/LED Dome)
    wellness_and_spa: float        # 0.0 (Basic gym) to 1.0 (Balinese/Thermal thermal suites)
    technology_smart_ship: float   # 0.0 (Traditional keycards) to 1.0 (Robotics/Starlink/App IoT)
    formality_tradition: float     # 0.0 (Casual flip-flops) to 1.0 (Black-tie Gala Balls)
    river_feeling: float           # 0.0 (Ocean liner) to 1.0 (Intimate river yacht <200 pax)

    def to_vector(self) -> List[float]:
        return [
            self.atmosphere_energy,
            self.luxury_level,
            self.family_and_kids,
            self.adventure_and_thrills,
            self.nightlife_and_parties,
            self.quiet_sanctuaries,
            self.space_ratio_calm,
            self.walking_compactness,
            self.accessibility_ease,
            self.food_variety_and_craft,
            self.outdoor_deck_promenade,
            self.scenic_and_destination,
            self.pool_and_water_focus,
            self.entertainment_theatre,
            self.wellness_and_spa,
            self.technology_smart_ship,
            self.formality_tradition,
            self.river_feeling,
        ]


@dataclass
class CruiseGenome:
    ship_slug: str
    ship_name: str
    archetype: ShipArchetype
    dna: CruiseDNADimensions
    signature_traits: List[str]
    evidence_basis: str


@dataclass
class PassengerPreferenceDNA:
    loves_promenades: bool = False
    enjoys_theatre_and_shows: bool = False
    seeks_quiet_and_relaxation: bool = False
    avoids_crowded_buffets: bool = False
    avoids_children_and_noise: bool = False
    dislikes_long_walking_distances: bool = False
    requires_high_accessibility: bool = False
    loves_culinary_variety: bool = False
    loves_thrills_and_activities: bool = False
    prefers_intimate_river_feeling: bool = False
    prefers_modern_luxury: bool = False


# Canonical Vessel Genome Profiles
CANONICAL_GENOMES: Dict[str, CruiseGenome] = {
    "msc-bellissima": CruiseGenome(
        ship_slug="msc-bellissima",
        ship_name="MSC Bellissima",
        archetype=ShipArchetype.ELEGANT_PROMENADE_CONTEMPORARY,
        dna=CruiseDNADimensions(
            atmosphere_energy=0.82,
            luxury_level=0.72,
            family_and_kids=0.88,
            adventure_and_thrills=0.75,
            nightlife_and_parties=0.85,
            quiet_sanctuaries=0.68,
            space_ratio_calm=0.60,
            walking_compactness=0.45,  # 315m long
            accessibility_ease=0.85,
            food_variety_and_craft=0.84,
            outdoor_deck_promenade=0.82,
            scenic_and_destination=0.75,
            pool_and_water_focus=0.88,
            entertainment_theatre=0.96,  # 80m LED Dome & London Theatre
            wellness_and_spa=0.88,       # 1100m2 Aurea Balinese Spa
            technology_smart_ship=0.90,  # MSC for Me IoT, Starlink
            formality_tradition=0.65,    # Elegant Gala Nights
            river_feeling=0.0,
        ),
        signature_traits=["80m LED Sky Dome Promenade", "Swarovski Crystal Atrium", "Aurea Balinese Spa", "Carousel Lounge"],
        evidence_basis="Verified from General Arrangement plans, onboard acoustic audits, and official technical specs.",
    ),
    "msc-meraviglia": CruiseGenome(
        ship_slug="msc-meraviglia",
        ship_name="MSC Meraviglia",
        archetype=ShipArchetype.ELEGANT_PROMENADE_CONTEMPORARY,
        dna=CruiseDNADimensions(
            atmosphere_energy=0.80,
            luxury_level=0.70,
            family_and_kids=0.88,
            adventure_and_thrills=0.75,
            nightlife_and_parties=0.82,
            quiet_sanctuaries=0.65,
            space_ratio_calm=0.60,
            walking_compactness=0.45,
            accessibility_ease=0.85,
            food_variety_and_craft=0.82,
            outdoor_deck_promenade=0.80,
            scenic_and_destination=0.75,
            pool_and_water_focus=0.88,
            entertainment_theatre=0.94,
            wellness_and_spa=0.86,
            technology_smart_ship=0.88,
            formality_tradition=0.65,
            river_feeling=0.0,
        ),
        signature_traits=["Original Meraviglia Prototype", "80m LED Dome", "Broadway Theatre", "Polar Aquapark"],
        evidence_basis="Chantiers de l'Atlantique Hull B34 statutory builder specifications.",
    ),
    "msc-virtuosa": CruiseGenome(
        ship_slug="msc-virtuosa",
        ship_name="MSC Virtuosa",
        archetype=ShipArchetype.ELEGANT_PROMENADE_CONTEMPORARY,
        dna=CruiseDNADimensions(
            atmosphere_energy=0.84,
            luxury_level=0.74,
            family_and_kids=0.88,
            adventure_and_thrills=0.78,
            nightlife_and_parties=0.86,
            quiet_sanctuaries=0.70,
            space_ratio_calm=0.62,
            walking_compactness=0.40,  # 331m extended
            accessibility_ease=0.86,
            food_variety_and_craft=0.88,
            outdoor_deck_promenade=0.84,
            scenic_and_destination=0.75,
            pool_and_water_focus=0.90,
            entertainment_theatre=0.97,  # 93m LED Sky Screen & Starship Rob
            wellness_and_spa=0.88,
            technology_smart_ship=0.94,  # Robotic humanoid bartender Rob
            formality_tradition=0.65,
            river_feeling=0.0,
        ),
        signature_traits=["93m LED Sky Screen", "Starship Club Rob Humanoid Bartender", "Indochine & HOLA! Dining"],
        evidence_basis="Meraviglia Plus shipyard delivery certification and guest flow logs.",
    ),
    "msc-grandiosa": CruiseGenome(
        ship_slug="msc-grandiosa",
        ship_name="MSC Grandiosa",
        archetype=ShipArchetype.ELEGANT_PROMENADE_CONTEMPORARY,
        dna=CruiseDNADimensions(
            atmosphere_energy=0.83,
            luxury_level=0.73,
            family_and_kids=0.88,
            adventure_and_thrills=0.76,
            nightlife_and_parties=0.84,
            quiet_sanctuaries=0.68,
            space_ratio_calm=0.62,
            walking_compactness=0.40,
            accessibility_ease=0.86,
            food_variety_and_craft=0.86,
            outdoor_deck_promenade=0.84,
            scenic_and_destination=0.75,
            pool_and_water_focus=0.88,
            entertainment_theatre=0.95,
            wellness_and_spa=0.88,
            technology_smart_ship=0.90,
            formality_tradition=0.65,
            river_feeling=0.0,
        ),
        signature_traits=["93m LED Galleria Grandiosa", "L'Atelier Bistrot Art Lounge", "HOLA! Tapas Bar"],
        evidence_basis="Chantiers de l'Atlantique Meraviglia-Plus launch documentation.",
    ),
    "msc-world-europa": CruiseGenome(
        ship_slug="msc-world-europa",
        ship_name="MSC World Europa",
        archetype=ShipArchetype.MEGA_RESORT_INNOVATOR,
        dna=CruiseDNADimensions(
            atmosphere_energy=0.88,
            luxury_level=0.78,
            family_and_kids=0.92,
            adventure_and_thrills=0.88,
            nightlife_and_parties=0.88,
            quiet_sanctuaries=0.72,
            space_ratio_calm=0.70,
            walking_compactness=0.35,  # 333m long, 47m beam
            accessibility_ease=0.90,
            food_variety_and_craft=0.92,
            outdoor_deck_promenade=0.95,  # 104m Y-shaped outdoor ocean promenade
            scenic_and_destination=0.80,
            pool_and_water_focus=0.94,
            entertainment_theatre=0.96,
            wellness_and_spa=0.90,
            technology_smart_ship=0.96,  # Dual-Fuel LNG, Solid Oxide Fuel Cell
            formality_tradition=0.60,
            river_feeling=0.0,
        ),
        signature_traits=["104m Outdoor Y-Promenade", "Venom Drop 11-deck slide", "Microbrewery Oceanic Beers"],
        evidence_basis="World Class prototype engineering documentation and LNG operational logs.",
    ),
    "icon-of-the-seas": CruiseGenome(
        ship_slug="icon-of-the-seas",
        ship_name="Icon of the Seas",
        archetype=ShipArchetype.MEGA_RESORT_INNOVATOR,
        dna=CruiseDNADimensions(
            atmosphere_energy=0.96,
            luxury_level=0.75,
            family_and_kids=0.99,
            adventure_and_thrills=0.99,  # Category 6 Waterpark & Crown's Edge
            nightlife_and_parties=0.92,
            quiet_sanctuaries=0.55,
            space_ratio_calm=0.68,
            walking_compactness=0.25,  # 365m mega-sprawl
            accessibility_ease=0.92,
            food_variety_and_craft=0.94,
            outdoor_deck_promenade=0.94,
            scenic_and_destination=0.70,
            pool_and_water_focus=0.99,   # 7 pools, 6 record slides
            entertainment_theatre=0.98,  # AquaDome & Absolute Zero Ice Arena
            wellness_and_spa=0.82,
            technology_smart_ship=0.98,
            formality_tradition=0.45,
            river_feeling=0.0,
        ),
        signature_traits=["AquaDome Geodesic Sanctuary", "Category 6 Waterpark", "Surfside Family Neighborhood"],
        evidence_basis="Meyer Turku statutory builder specs and Royal Caribbean technical fact sheets.",
    ),
    "celebrity-ascent": CruiseGenome(
        ship_slug="celebrity-ascent",
        ship_name="Celebrity Ascent",
        archetype=ShipArchetype.MODERN_OUTWARD_FACING_LUXURY,
        dna=CruiseDNADimensions(
            atmosphere_energy=0.65,
            luxury_level=0.88,
            family_and_kids=0.45,
            adventure_and_thrills=0.35,
            nightlife_and_parties=0.72,
            quiet_sanctuaries=0.90,
            space_ratio_calm=0.86,
            walking_compactness=0.55,
            accessibility_ease=0.92,
            food_variety_and_craft=0.96,  # Le Voyage by Daniel Boulud
            outdoor_deck_promenade=0.94,  # Magic Carpet outward cantilever
            scenic_and_destination=0.92,
            pool_and_water_focus=0.80,
            entertainment_theatre=0.88,
            wellness_and_spa=0.94,
            technology_smart_ship=0.92,
            formality_tradition=0.70,
            river_feeling=0.0,
        ),
        signature_traits=["Cantilevered Magic Carpet", "The Rooftop Garden", "Le Voyage by Daniel Boulud"],
        evidence_basis="Chantiers de l'Atlantique Edge-class architecture review.",
    ),
    "norwegian-prima": CruiseGenome(
        ship_slug="norwegian-prima",
        ship_name="Norwegian Prima",
        archetype=ShipArchetype.FREESTYLE_THRILL_SEEKER,
        dna=CruiseDNADimensions(
            atmosphere_energy=0.85,
            luxury_level=0.78,
            family_and_kids=0.80,
            adventure_and_thrills=0.92,  # 3-deck go-kart racetrack
            nightlife_and_parties=0.88,
            quiet_sanctuaries=0.75,
            space_ratio_calm=0.80,
            walking_compactness=0.58,  # 293m spacious layout
            accessibility_ease=0.88,
            food_variety_and_craft=0.94,  # Indulge Food Hall & Onda by Scarpetta
            outdoor_deck_promenade=0.96,  # 44,000 sq ft Ocean Boulevard
            scenic_and_destination=0.85,
            pool_and_water_focus=0.85,
            entertainment_theatre=0.90,  # Donna Summer Musical Theatre
            wellness_and_spa=0.92,       # Mandara Spa with Charcoal Sauna
            technology_smart_ship=0.90,
            formality_tradition=0.30,    # 100% Freestyle
            river_feeling=0.0,
        ),
        signature_traits=["3-Level Prima Speedway", "Ocean Boulevard 360 Walkway", "Indulge Food Hall"],
        evidence_basis="Fincantieri Marghera shipyard specifications and NCL operational data.",
    ),
    "scarlet-lady": CruiseGenome(
        ship_slug="scarlet-lady",
        ship_name="Scarlet Lady",
        archetype=ShipArchetype.ADULTS_ONLY_CONTEMPORARY,
        dna=CruiseDNADimensions(
            atmosphere_energy=0.88,
            luxury_level=0.80,
            family_and_kids=0.0,   # Strictly 18+ Adults Only
            adventure_and_thrills=0.45,
            nightlife_and_parties=0.96,  # The Manor, Scarlet Night, DJ Sets
            quiet_sanctuaries=0.82,
            space_ratio_calm=0.82,
            walking_compactness=0.62,
            accessibility_ease=0.88,
            food_variety_and_craft=0.95,  # 20+ eateries, zero buffets
            outdoor_deck_promenade=0.90,
            scenic_and_destination=0.80,
            pool_and_water_focus=0.75,
            entertainment_theatre=0.86,
            wellness_and_spa=0.94,       # Redemption Spa & B-Complex
            technology_smart_ship=0.94,  # The Band RFID wearable & Virgin App
            formality_tradition=0.20,    # Strictly informal / stylish
            river_feeling=0.0,
        ),
        signature_traits=["Adults-Only 18+", "Zero Buffets (20+ Included Eateries)", "Squid Ink Tattoo Studio"],
        evidence_basis="Fincantieri Sestri Ponente build records and Virgin Voyages brand rules.",
    ),
    "ms-andorinha": CruiseGenome(
        ship_slug="ms-andorinha",
        ship_name="MS Andorinha",
        archetype=ShipArchetype.INTIMATE_SCENIC_RIVER_YACHT,
        dna=CruiseDNADimensions(
            atmosphere_energy=0.35,
            luxury_level=0.95,           # Ultra-luxury custom river yacht
            family_and_kids=0.10,
            adventure_and_thrills=0.10,
            nightlife_and_parties=0.30,  # Acoustic fado & wine tastings
            quiet_sanctuaries=0.98,      # 84 guests maximum
            space_ratio_calm=0.98,
            walking_compactness=0.98,    # 80m length, zero elevator waits
            accessibility_ease=0.90,
            food_variety_and_craft=0.92, # Regional Douro gastronomy & wines
            outdoor_deck_promenade=0.95, # 360-degree open Sun Deck
            scenic_and_destination=0.99, # Gliding past Douro vineyards
            pool_and_water_focus=0.40,   # Sun deck plunge pool
            entertainment_theatre=0.30,  # Local enrichment
            wellness_and_spa=0.60,
            technology_smart_ship=0.75,
            formality_tradition=0.60,
            river_feeling=1.0,           # Pure Douro River immersion
        ),
        signature_traits=["84-Guest Exclusive Yacht", "Custom Douro Lock Proportions", "Arthur's Bistro & Compass Rose"],
        evidence_basis="Scylla AG & Tauck official river naval engineering data.",
    ),
}


class CruiseDNAMatcher:
    """Calculates cosine similarity and personal passenger matching."""

    @staticmethod
    def compute_similarity(dna_a: CruiseDNADimensions, dna_b: CruiseDNADimensions) -> float:
        vec_a = dna_a.to_vector()
        vec_b = dna_b.to_vector()

        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return round((dot / (norm_a * norm_b)) * 100, 1)

    @classmethod
    def find_top_matches(cls, target_slug: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if target_slug not in CANONICAL_GENOMES:
            return []

        target_genome = CANONICAL_GENOMES[target_slug]
        scores: List[Dict[str, Any]] = []

        for slug, genome in CANONICAL_GENOMES.items():
            if slug == target_slug:
                continue
            sim = cls.compute_similarity(target_genome.dna, genome.dna)

            # Determine relationship classification
            if sim >= 93.0:
                rel = "Direct Sister / Class Evolution"
            elif genome.dna.luxury_level > target_genome.dna.luxury_level + 0.1:
                rel = "Luxury Upgrade Alternative"
            elif genome.dna.river_feeling > 0.5 and target_genome.dna.river_feeling == 0.0:
                rel = "Intimate River Discovery"
            else:
                rel = "Experience Alternative"

            scores.append({
                "slug": slug,
                "name": genome.ship_name,
                "similarity_pct": sim,
                "archetype": genome.archetype.value,
                "relationship": rel,
                "signature_traits": genome.signature_traits,
            })

        scores.sort(key=lambda x: x["similarity_pct"], reverse=True)
        return scores[:top_k]

    @classmethod
    def match_passenger_preferences(cls, pref: PassengerPreferenceDNA, top_k: int = 4) -> List[Dict[str, Any]]:
        scored_ships: List[Dict[str, Any]] = []

        for slug, genome in CANONICAL_GENOMES.items():
            score = 70.0  # Base score
            why_reasons: List[str] = []

            dna = genome.dna

            if pref.loves_promenades and dna.outdoor_deck_promenade >= 0.85:
                score += 15.0
                why_reasons.append("Features expansive 360-degree ocean promenade or iconic indoor LED gallery.")

            if pref.enjoys_theatre_and_shows and dna.entertainment_theatre >= 0.90:
                score += 15.0
                why_reasons.append(f"World-class entertainment with {genome.signature_traits[0]}.")

            if pref.seeks_quiet_and_relaxation and dna.quiet_sanctuaries >= 0.80:
                score += 15.0
                why_reasons.append("High space-to-passenger ratio with dedicated quiet sanctuaries.")

            if pref.avoids_children_and_noise:
                if dna.family_and_kids <= 0.2:
                    score += 20.0
                    why_reasons.append("Strictly adults-only or mature cultural passenger profile.")
                elif dna.family_and_kids >= 0.85:
                    score -= 25.0
                    why_reasons.append("High volume of multi-generational family and youth activities.")

            if pref.dislikes_long_walking_distances:
                if dna.walking_compactness >= 0.70:
                    score += 20.0
                    why_reasons.append("Compact hull geometry with short, frictionless corridor transit.")
                elif dna.walking_compactness <= 0.40:
                    score -= 20.0
                    why_reasons.append("330m+ mega-hull requires extensive daily walking.")

            if pref.prefers_intimate_river_feeling:
                if dna.river_feeling >= 0.8:
                    score += 30.0
                    why_reasons.append("Intimate river yacht gliding directly into historic city centers.")
                else:
                    score -= 15.0

            if pref.prefers_modern_luxury and dna.luxury_level >= 0.85:
                score += 15.0
                why_reasons.append("Modern luxury styling with Michelin-partnered culinary craft.")

            score = min(max(round(score, 1), 0.0), 99.9)

            scored_ships.append({
                "slug": slug,
                "name": genome.ship_name,
                "archetype": genome.archetype.value,
                "match_score_pct": score,
                "why": why_reasons or ["Balanced contemporary maritime profile."],
                "signature_traits": genome.signature_traits,
            })

        scored_ships.sort(key=lambda x: x["match_score_pct"], reverse=True)
        return scored_ships[:top_k]
