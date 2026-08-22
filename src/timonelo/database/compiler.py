"""
Cruise Intelligence Database Compiler.
Validates and compiles all modular Knowledge Packs into a normalized,
referentially verified master Cruise Intelligence Database.
"""

from __future__ import annotations
import os
import json
from typing import Dict, Any, List, Tuple

from timonelo.canonical import canonical_dump


class KnowledgeDBCompiler:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.knowledge_dir = os.path.join(root_dir, "knowledge")
        self.data_dir = os.path.join(root_dir, "data")
        
        self.sources: Dict[str, Any] = {}
        self.ship_classes: Dict[str, Any] = {}
        self.ships: Dict[str, Any] = {}
        self.ports: Dict[str, Any] = {}
        self.routes: Dict[str, Any] = {}
        self.venues: Dict[str, Any] = {}
        self.shipyards: Dict[str, Any] = {}
        self.regions: Dict[str, Any] = {}
        self.deployments: Dict[str, Any] = {}
        self.voyages: Dict[str, Any] = {}
        self.fleet_status: Dict[str, Any] = {}
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []

    def compile(self) -> Dict[str, Any]:
        """Compile and validate all knowledge packs."""
        self.validation_errors.clear()
        self.validation_warnings.clear()

        self._load_sources()
        self._load_shipyards()
        self._load_regions()
        self._load_ship_classes()
        self._load_ships()
        self._load_ports()
        self._load_routes()
        self._load_venues()
        self._load_deployments()
        self._load_voyages()
        self._load_fleet_status()

        self._verify_referential_integrity()

        # Build Knowledge Graph
        from .graph import KnowledgeGraphBuilder
        graph_builder = KnowledgeGraphBuilder({
            "sources": self.sources,
            "ship_classes": self.ship_classes,
            "ships": self.ships,
            "ports": self.ports,
            "routes": self.routes,
            "venues": self.venues,
            "shipyards": self.shipyards,
            "regions": self.regions,
            "deployments": self.deployments,
            "voyages": self.voyages,
            "fleet_status": self.fleet_status,
        })
        self.knowledge_graph = graph_builder.build()
        graph_errors, graph_warnings = self.knowledge_graph.validate_integrity()
        self.validation_errors.extend(graph_errors)
        self.validation_warnings.extend(graph_warnings)

        graph_export = self.knowledge_graph.export_graph_json()

        compiled_db = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "version": "2.0.0",
            "statistics": {
                "total_sources": len(self.sources),
                "total_shipyards": len(self.shipyards),
                "total_regions": len(self.regions),
                "total_ship_classes": len(self.ship_classes),
                "total_ships": len(self.ships),
                "total_ports": len(self.ports),
                "total_routes": len(self.routes),
                "total_venues": len(self.venues),
                "total_graph_nodes": len(self.knowledge_graph.nodes),
                "total_graph_edges": len(self.knowledge_graph.edges),
                "validation_errors_count": len(self.validation_errors),
                "validation_warnings_count": len(self.validation_warnings),
            },
            "sources": self.sources,
            "shipyards": self.shipyards,
            "regions": self.regions,
            "ship_classes": self.ship_classes,
            "ships": self.ships,
            "ports": self.ports,
            "routes": self.routes,
            "venues": self.venues,
            "deployments": self.deployments,
            "voyages": self.voyages,
            "fleet_status": self.fleet_status,
            "graph_summary": graph_export["statistics"],
        }

        # Save to data/cruise_intelligence_db.json and data/cruise_knowledge_graph.json.
        # Both go through canonical_dump: same sorted keys, indent and encoding
        # as before, plus LF newlines on every platform and the trailing newline
        # the canonical form requires.
        os.makedirs(self.data_dir, exist_ok=True)
        canonical_dump(
            compiled_db, os.path.join(self.data_dir, "cruise_intelligence_db.json")
        )
        canonical_dump(
            graph_export, os.path.join(self.data_dir, "cruise_knowledge_graph.json")
        )

        return compiled_db

    def _load_sources(self):
        sources_root = os.path.join(self.knowledge_dir, "sources")
        if not os.path.exists(sources_root):
            return

        # 1. Master registry if exists
        src_path = os.path.join(sources_root, "registry.json")
        if os.path.exists(src_path):
            with open(src_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.sources.update(data.get("sources", {}))

        # 2. Categorized source files in subdirectories
        for root, dirs, files in os.walk(sources_root):
            for file in files:
                if file.endswith(".json") and file != "registry.json":
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            sid = data.get("source_id", data.get("id"))
                            if sid:
                                self.sources[sid] = data
                    except Exception:
                        pass

    def _load_shipyards(self):
        yards_dir = os.path.join(self.knowledge_dir, "shipyards")
        if not os.path.exists(yards_dir):
            return
        for fname in os.listdir(yards_dir):
            if fname.endswith(".json"):
                path = os.path.join(yards_dir, fname)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    slug = data.get("slug", fname.replace(".json", ""))
                    self.shipyards[slug] = data

    def _load_regions(self):
        reg_dir = os.path.join(self.knowledge_dir, "regions")
        if not os.path.exists(reg_dir):
            return
        for fname in os.listdir(reg_dir):
            if fname.endswith(".json"):
                path = os.path.join(reg_dir, fname)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    slug = data.get("slug", fname.replace(".json", ""))
                    self.regions[slug] = data
        else:
            self.validation_warnings.append("No master sources registry found at knowledge/sources/registry.json")

    def _load_ship_classes(self):
        classes_dir = os.path.join(self.knowledge_dir, "ship-classes")
        if not os.path.exists(classes_dir):
            return
        for fname in os.listdir(classes_dir):
            if fname.endswith(".json"):
                path = os.path.join(classes_dir, fname)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    slug = data.get("slug", fname.replace(".json", ""))
                    self.ship_classes[slug] = data

    def _load_ships(self):
        ships_dir = os.path.join(self.knowledge_dir, "ships")
        if not os.path.exists(ships_dir):
            return
        for item in os.listdir(ships_dir):
            item_path = os.path.join(ships_dir, item)
            if os.path.isdir(item_path):
                identity_path = os.path.join(item_path, "identity.json")
                if os.path.exists(identity_path):
                    with open(identity_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        slug = data.get("slug", item)

                        # Load Depth Packs
                        cabins_path = os.path.join(item_path, "cabins.json")
                        if os.path.exists(cabins_path):
                            with open(cabins_path, "r", encoding="utf-8") as cf:
                                data["cabins"] = json.load(cf)

                        venues_path = os.path.join(item_path, "venues.json")
                        if os.path.exists(venues_path):
                            with open(venues_path, "r", encoding="utf-8") as vf:
                                ship_venues = json.load(vf)
                                data["venues"] = ship_venues
                                for sv in ship_venues:
                                    self.venues[sv.get("slug", sv.get("name"))] = sv

                        ops_path = os.path.join(item_path, "operations.json")
                        if os.path.exists(ops_path):
                            with open(ops_path, "r", encoding="utf-8") as opf:
                                data["operations"] = json.load(opf)

                        neg_path = os.path.join(item_path, "negative_intelligence.json")
                        if os.path.exists(neg_path):
                            with open(neg_path, "r", encoding="utf-8") as nf:
                                data["negative_intelligence"] = json.load(nf)

                        # Compute Intelligence Level (0 to 7)
                        level = 1  # Base registered technical entity
                        if "cabins" in data and len(data["cabins"]) > 0:
                            level = max(level, 3)
                        if "venues" in data and len(data["venues"]) > 0:
                            level = max(level, 4)
                        if "operations" in data:
                            level = max(level, 5)
                        if "negative_intelligence" in data and len(data["negative_intelligence"]) > 0:
                            level = max(level, 6)
                        if slug == "msc-bellissima":
                            level = 7  # Verified Reference Premium Twin

                        data["intelligence_level"] = level
                        self.ships[slug] = data
            elif item.endswith(".json"):
                with open(item_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    slug = data.get("slug", item.replace(".json", ""))
                    data["intelligence_level"] = 1
                    self.ships[slug] = data

    def _load_ports(self):
        ports_dir = os.path.join(self.knowledge_dir, "ports")
        if not os.path.exists(ports_dir):
            return
        for item in os.listdir(ports_dir):
            item_path = os.path.join(ports_dir, item)
            if os.path.isdir(item_path):
                identity_path = os.path.join(item_path, "identity.json")
                if os.path.exists(identity_path):
                    with open(identity_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        slug = data.get("slug", item)
                        self.ports[slug] = data
            elif item.endswith(".json"):
                with open(item_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    slug = data.get("slug", item.replace(".json", ""))
                    self.ports[slug] = data

    def _load_routes(self):
        routes_dir = os.path.join(self.knowledge_dir, "routes")
        if not os.path.exists(routes_dir):
            return
        for item in os.listdir(routes_dir):
            item_path = os.path.join(routes_dir, item)
            if os.path.isdir(item_path):
                identity_path = os.path.join(item_path, "identity.json")
                if os.path.exists(identity_path):
                    with open(identity_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        slug = data.get("slug", item)
                        self.routes[slug] = data
            elif item.endswith(".json"):
                with open(item_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    slug = data.get("slug", item.replace(".json", ""))
                    self.routes[slug] = data

    def _load_venues(self):
        venues_dir = os.path.join(self.knowledge_dir, "venues")
        if not os.path.exists(venues_dir):
            return
        for fname in os.listdir(venues_dir):
            if fname.endswith(".json"):
                path = os.path.join(venues_dir, fname)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    slug = data.get("slug", fname.replace(".json", ""))
                    self.venues[slug] = data

    def _load_deployments(self):
        dep_dir = os.path.join(self.knowledge_dir, "deployments")
        if not os.path.exists(dep_dir):
            return
        for fname in os.listdir(dep_dir):
            if fname.endswith(".json"):
                path = os.path.join(dep_dir, fname)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    slug = data.get("deployment_id", fname.replace(".json", ""))
                    self.deployments[slug] = data

    def _load_voyages(self):
        voy_dir = os.path.join(self.knowledge_dir, "voyages")
        if not os.path.exists(voy_dir):
            return
        for fname in os.listdir(voy_dir):
            if fname.endswith(".json"):
                path = os.path.join(voy_dir, fname)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    slug = data.get("voyage_id", fname.replace(".json", ""))
                    self.voyages[slug] = data

    def _load_fleet_status(self):
        status_dir = os.path.join(self.knowledge_dir, "fleet-status")
        if not os.path.exists(status_dir):
            return
        for fname in os.listdir(status_dir):
            if fname.endswith(".json"):
                path = os.path.join(status_dir, fname)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    slug = data.get("ship_slug", fname.replace(".json", ""))
                    self.fleet_status[slug] = data

    def _verify_referential_integrity(self):
        """Cross-check entity foreign keys."""
        # 1. Check Routes referencing Ports
        for route_slug, route in self.routes.items():
            ports_seq = route.get("ports_sequence", [])
            for entry in ports_seq:
                pslug = entry.get("port_slug")
                if pslug and pslug != "sea-day" and pslug not in self.ports:
                    self.validation_warnings.append(
                        f"Route '{route_slug}' references port '{pslug}' not yet indexed in knowledge/ports/"
                    )

        # 2. Check Ships referencing Classes
        for ship_slug, ship in self.ships.items():
            sclass = ship.get("class_id")
            if sclass and sclass not in self.ship_classes:
                self.validation_warnings.append(
                    f"Ship '{ship_slug}' references class '{sclass}' not yet indexed in knowledge/ship-classes/"
                )
