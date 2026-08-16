"""
Operations Data Layer Schema for Timonelo.
Manages temporal ship lifecycles: deployments, voyages, schedules, live port calls, and fleet status.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import datetime


class SeasonalPeriod(str, Enum):
    SUMMER_2026 = "SUMMER_2026"
    WINTER_2026_27 = "WINTER_2026_27"
    SUMMER_2027 = "SUMMER_2027"
    WINTER_2027_28 = "WINTER_2027_28"


class PortCallType(str, Enum):
    STANDARD_PORT_DAY = "STANDARD_PORT_DAY"
    TURNAROUND_EMBARKATION = "TURNAROUND_EMBARKATION"
    OVERNIGHT_STAY = "OVERNIGHT_STAY"
    TECHNICAL_BUNKERING = "TECHNICAL_BUNKERING"
    TENDER_OPERATION = "TENDER_OPERATION"


@dataclass(frozen=True)
class PortCall:
    call_id: str
    voyage_id: str
    ship_slug: str
    port_slug: str
    terminal_name: str
    arrival_iso: Optional[str]
    departure_iso: Optional[str]
    call_type: PortCallType = PortCallType.STANDARD_PORT_DAY
    gangway_deck: int = 5
    is_turnaround: bool = False
    is_tender: bool = False
    is_overnight: bool = False
    status: str = "SCHEDULED"  # "SCHEDULED", "DOCKED", "UNDERWAY", "CANCELLED"


@dataclass(frozen=True)
class Voyage:
    voyage_id: str
    ship_slug: str
    cruise_number: str
    route_slug: str
    start_date: str
    end_date: str
    embarkation_port: str
    disembarkation_port: str
    port_calls: List[PortCall] = field(default_factory=list)
    sea_days_count: int = 2
    nautical_miles: float = 1450.0
    weather_zone: str = "Western Mediterranean Warm Temperate"
    status: str = "SCHEDULED"  # "SCHEDULED", "ACTIVE", "COMPLETED"


@dataclass(frozen=True)
class SeasonalDeployment:
    deployment_id: str
    ship_slug: str
    season: SeasonalPeriod
    region_slug: str
    homeports: List[str]
    primary_routes: List[str]
    start_date: str
    end_date: str
    source_id: str = "src:official-msc-deployments-2026"


@dataclass(frozen=True)
class LiveFleetStatus:
    ship_slug: str
    current_season: SeasonalPeriod
    deployment_region: str
    current_voyage_id: Optional[str]
    operational_state: str  # "DOCKED", "UNDERWAY_CRUISING", "TENDER_STATION", "IN_DRYDOCK", "UNKNOWN"
    current_port_slug: Optional[str]
    next_port_slug: Optional[str]
    eta_next_port: Optional[str]
    etd_current_port: Optional[str]
    speed_knots: Optional[float]
    course_deg: Optional[float]
    position_lat_lon: Optional[Tuple[float, float]]
    local_time_zone: str
    last_observed_at: str
    source_feed: str = "src:official-cruise-line-schedule"
    freshness_seconds: int = 300
