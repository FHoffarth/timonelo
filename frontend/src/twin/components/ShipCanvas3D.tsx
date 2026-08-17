import React, { useRef, useMemo, useEffect } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Text, Float, Line } from "@react-three/drei";
import * as THREE from "three";
import { CabinData, DeckData, VenueData, ElevatorData, ToiletData, ViewMode, ActiveLayers, RouteResult } from "../types";
import { normToThree, getDeckCabins, getDeckVenues, getDeckToilets, getDeckElevators, DECKS_MAP } from "../twinEngine";

interface ShipCanvasProps {
  viewMode: ViewMode;
  activeDeck: number;
  selectedCabin: CabinData | null;
  selectedVenue: VenueData | null;
  hoveredCabin: CabinData | null;
  activeRoute: RouteResult | null;
  layers: ActiveLayers;
  onSelectCabin: (cabin: CabinData) => void;
  onHoverCabin: (cabin: CabinData | null) => void;
  onSelectVenue: (venue: VenueData) => void;
  onSelectDeck: (deckNum: number) => void;
}

// ----------------------------------------------------------------------
// Camera Controller for Smooth Transitions
// ----------------------------------------------------------------------
function CameraRig({
  viewMode,
  activeDeck,
  selectedCabin,
  selectedVenue,
}: {
  viewMode: ViewMode;
  activeDeck: number;
  selectedCabin: CabinData | null;
  selectedVenue: VenueData | null;
}) {
  const { camera } = useThree();
  const targetPos = useRef(new THREE.Vector3(0, 45, 120));
  const targetLook = useRef(new THREE.Vector3(0, 0, 0));

  useEffect(() => {
    if (viewMode === "deck_topdown") {
      const d = DECKS_MAP.get(activeDeck);
      const zElev = d?.elevation_m ?? 25.0;
      const yOffset = (zElev - 25.0) * 0.4;

      if (selectedCabin && selectedCabin.deck === activeDeck) {
        const [cx, cy, cz] = normToThree(selectedCabin.x, selectedCabin.y, activeDeck);
        targetPos.current.set(cx, cy + 32, cz + 10);
        targetLook.current.set(cx, cy, cz);
      } else if (selectedVenue && selectedVenue.deck === activeDeck) {
        const [vx, vy, vz] = normToThree(selectedVenue.x, selectedVenue.y, activeDeck);
        targetPos.current.set(vx, vy + 40, vz + 15);
        targetLook.current.set(vx, vy, vz);
      } else {
        targetPos.current.set(0, yOffset + 70, 0.1);
        targetLook.current.set(0, yOffset, 0);
      }
    } else {
      // 3D Exterior
      targetPos.current.set(0, 35, 140);
      targetLook.current.set(0, 0, 0);
    }
  }, [viewMode, activeDeck, selectedCabin, selectedVenue]);

  useFrame((_, delta) => {
    camera.position.lerp(targetPos.current, 0.06);
  });

  return (
    <OrbitControls
      makeDefault
      enableDamping
      dampingFactor={0.08}
      minDistance={10}
      maxDistance={350}
      maxPolarAngle={viewMode === "deck_topdown" ? Math.PI / 2.2 : Math.PI / 2.05}
    />
  );
}

// ----------------------------------------------------------------------
// 3D Ship Exterior & Superstructure Model
// ----------------------------------------------------------------------
function ShipHullModel({
  activeDeck,
  viewMode,
  onSelectDeck,
}: {
  activeDeck: number;
  viewMode: ViewMode;
  onSelectDeck: (d: number) => void;
}) {
  const isTopDown = viewMode === "deck_topdown";

  return (
    <group position={[0, -5, 0]}>
      {/* Ocean Base Layer */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -14, 0]} receiveShadow>
        <planeGeometry args={[600, 350]} />
        <meshStandardMaterial
          color="#061226"
          roughness={0.1}
          metalness={0.8}
          transparent
          opacity={0.85}
        />
      </mesh>

      {/* Main Hull (Deep Navy / Charcoal Lower Hull) */}
      <mesh position={[0, -7, 0]} castShadow receiveShadow>
        <boxGeometry args={[145, 12, 28]} />
        <meshStandardMaterial color="#0c192c" roughness={0.3} metalness={0.7} />
      </mesh>

      {/* Bow Bulge / Forward Clipper */}
      <mesh position={[75, -6, 0]} rotation={[0, 0, -Math.PI / 8]} castShadow>
        <coneGeometry args={[14, 18, 4]} />
        <meshStandardMaterial color="#0c192c" roughness={0.3} metalness={0.7} />
      </mesh>

      {/* Transom Stern */}
      <mesh position={[-74, -6, 0]} castShadow>
        <boxGeometry args={[6, 12, 26]} />
        <meshStandardMaterial color="#0a1526" roughness={0.4} />
      </mesh>

      {/* White Superstructure Decks */}
      {!isTopDown && (
        <group>
          {/* Deck 5 - 7 Promenade Tier */}
          <mesh position={[0, 0, 0]} castShadow receiveShadow>
            <boxGeometry args={[136, 6, 27]} />
            <meshStandardMaterial color="#f8fafc" roughness={0.4} />
          </mesh>

          {/* LED Sky Dome Curved Roof (Galleria Bellissima) */}
          <mesh position={[5, 4, 0]} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[4.5, 4.5, 45, 16, 1, false, 0, Math.PI]} />
            <meshStandardMaterial
              color="#38bdf8"
              emissive="#0284c7"
              emissiveIntensity={0.6}
              transparent
              opacity={0.6}
              wireframe={false}
            />
          </mesh>

          {/* Deck 8 - 14 Residential Stateroom Tiers with Balcony Textures */}
          <mesh position={[0, 8, 0]} castShadow receiveShadow>
            <boxGeometry args={[128, 12, 25]} />
            <meshStandardMaterial color="#f1f5f9" roughness={0.5} />
          </mesh>

          {/* Deck 15 - 16 Lido Decks & Pools */}
          <mesh position={[-5, 15, 0]} castShadow>
            <boxGeometry args={[118, 3, 27]} />
            <meshStandardMaterial color="#e2e8f0" roughness={0.3} />
          </mesh>

          {/* Atmosphere Pool (Main Pool Water) */}
          <mesh position={[12, 16.6, 0]}>
            <boxGeometry args={[18, 0.4, 12]} />
            <meshStandardMaterial color="#0284c7" roughness={0.1} metalness={0.9} />
          </mesh>

          {/* Grand Canyon Solarium Pool */}
          <mesh position={[-18, 16.6, 0]}>
            <boxGeometry args={[14, 0.4, 10]} />
            <meshStandardMaterial color="#06b6d4" roughness={0.1} metalness={0.9} />
          </mesh>

          {/* Arizona Aquapark Water Slides on Deck 18 */}
          <mesh position={[-25, 20, 4]} rotation={[0.4, 0.2, 0.3]}>
            <torusGeometry args={[5, 0.8, 8, 24, Math.PI * 1.5]} />
            <meshStandardMaterial color="#e11d48" roughness={0.3} />
          </mesh>

          {/* Iconic MSC Funnel (Navy & White with Compass Star) */}
          <group position={[-12, 22, 0]}>
            <mesh rotation={[0, 0, -0.2]}>
              <boxGeometry args={[8, 11, 6]} />
              <meshStandardMaterial color="#0f172a" roughness={0.2} />
            </mesh>
            <mesh position={[0, 2, 0]}>
              <cylinderGeometry args={[2.2, 2.2, 0.5, 16]} rotation={[Math.PI / 2, 0, 0]} />
              <meshStandardMaterial color="#fbbf24" emissive="#f59e0b" emissiveIntensity={0.8} />
            </mesh>
          </group>

          {/* Lifeboat Arrays along Deck 8 (Port & Starboard) */}
          {[-50, -35, -20, -5, 10, 25, 40].map((lx, idx) => (
            <React.Fragment key={idx}>
              <mesh position={[lx, 2.5, 13.8]}>
                <capsuleGeometry args={[1.1, 4.5, 4, 8]} rotation={[0, 0, Math.PI / 2]} />
                <meshStandardMaterial color="#f97316" roughness={0.4} />
              </mesh>
              <mesh position={[lx, 2.5, -13.8]}>
                <capsuleGeometry args={[1.1, 4.5, 4, 8]} rotation={[0, 0, Math.PI / 2]} />
                <meshStandardMaterial color="#f97316" roughness={0.4} />
              </mesh>
            </React.Fragment>
          ))}
        </group>
      )}
    </group>
  );
}

// ----------------------------------------------------------------------
// Interactive 2D/3D Deck Layout with 2,217 Staterooms
// ----------------------------------------------------------------------
function DeckStateroomLayer({
  activeDeck,
  selectedCabin,
  selectedVenue,
  hoveredCabin,
  layers,
  onSelectCabin,
  onHoverCabin,
  onSelectVenue,
}: {
  activeDeck: number;
  selectedCabin: CabinData | null;
  selectedVenue: VenueData | null;
  hoveredCabin: CabinData | null;
  layers: ActiveLayers;
  onSelectCabin: (c: CabinData) => void;
  onHoverCabin: (c: CabinData | null) => void;
  onSelectVenue: (v: VenueData) => void;
}) {
  const cabins = useMemo(() => getDeckCabins(activeDeck), [activeDeck]);
  const venues = useMemo(() => getDeckVenues(activeDeck), [activeDeck]);
  const toilets = useMemo(() => getDeckToilets(activeDeck), [activeDeck]);
  const elevators = useMemo(() => getDeckElevators(activeDeck), [activeDeck]);

  const deckData = DECKS_MAP.get(activeDeck);
  const deckElevation = deckData?.elevation_m ?? 25.0;
  const yBase = (deckElevation - 25.0) * 0.4;

  return (
    <group position={[0, yBase, 0]}>
      {/* Active Deck Floor Plate */}
      <mesh position={[0, -0.2, 0]} receiveShadow>
        <boxGeometry args={[138, 0.4, 27]} />
        <meshStandardMaterial
          color="#0f172a"
          roughness={0.2}
          metalness={0.5}
        />
      </mesh>

      {/* Central Corridor Floor Light Grid */}
      <mesh position={[0, -0.05, 0]}>
        <planeGeometry args={[130, 2.5]} />
        <meshBasicMaterial color="#1e293b" />
      </mesh>

      {/* 2,217 Staterooms on Active Deck */}
      {layers.cabins &&
        cabins.map((c) => {
          const [cx, cy, cz] = normToThree(c.x, c.y, activeDeck);
          const isSelected = selectedCabin?.cabin_number === c.cabin_number;
          const isHovered = hoveredCabin?.cabin_number === c.cabin_number;

          // Color coding by stateroom category
          let color = "#3b82f6"; // Interior
          if (c.category.startsWith("BA") || c.category.startsWith("BR")) color = "#10b981"; // Balcony
          else if (c.category.startsWith("YC") || c.category.startsWith("SL")) color = "#f59e0b"; // Yacht Club
          else if (c.category.startsWith("OR")) color = "#38bdf8"; // Ocean View

          if (isSelected) color = "#ec4899"; // Selection Pulse Magenta
          else if (isHovered) color = "#ffffff"; // Hover Glow

          return (
            <group key={c.cabin_number} position={[cx, 0.1, cz]}>
              <mesh
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectCabin(c);
                }}
                onPointerOver={(e) => {
                  e.stopPropagation();
                  onHoverCabin(c);
                }}
                onPointerOut={() => onHoverCabin(null)}
                castShadow
              >
                <boxGeometry args={[0.9, isSelected ? 1.0 : 0.35, 1.4]} />
                <meshStandardMaterial
                  color={color}
                  emissive={isSelected ? "#db2777" : (isHovered ? "#38bdf8" : "#000000")}
                  emissiveIntensity={isSelected ? 0.9 : (isHovered ? 0.5 : 0)}
                  roughness={0.2}
                />
              </mesh>

              {/* Accessible 'H' Icon for PRM Staterooms */}
              {layers.accessible && c.accessible && (
                <Float speed={2} rotationIntensity={0} floatIntensity={0.5}>
                  <mesh position={[0, 1.2, 0]}>
                    <sphereGeometry args={[0.3, 8, 8]} />
                    <meshBasicMaterial color="#38bdf8" />
                  </mesh>
                </Float>
              )}

              {/* Selected Cabin Pointer Pin */}
              {isSelected && (
                <group position={[0, 2.5, 0]}>
                  <Float speed={4} floatIntensity={1}>
                    <Text
                      fontSize={1.2}
                      color="#f43f5e"
                      anchorX="center"
                      anchorY="middle"
                      outlineWidth={0.1}
                      outlineColor="#ffffff"
                    >
                      {`CABIN ${c.cabin_number}`}
                    </Text>
                  </Float>
                </group>
              )}
            </group>
          );
        })}

      {/* Venues on Active Deck */}
      {venues.map((v) => {
        const [vx, vy, vz] = normToThree(v.x, v.y, activeDeck);
        const isSelected = selectedVenue?.name === v.name;

        return (
          <group
            key={v.name}
            position={[vx, 0.3, vz]}
            onClick={(e) => {
              e.stopPropagation();
              onSelectVenue(v);
            }}
          >
            <mesh>
              <cylinderGeometry args={[2.0, 2.0, 0.6, 16]} />
              <meshStandardMaterial
                color={isSelected ? "#ec4899" : "#6366f1"}
                emissive="#4f46e5"
                emissiveIntensity={0.6}
              />
            </mesh>
            <Text
              position={[0, 2.2, 0]}
              fontSize={1.1}
              color="#ffffff"
              anchorX="center"
              anchorY="middle"
              outlineWidth={0.08}
              outlineColor="#000000"
            >
              {v.name}
            </Text>
          </group>
        );
      })}

      {/* Elevators on Active Deck */}
      {layers.elevators &&
        elevators.map((e) => {
          const [ex, ey, ez] = normToThree(e.x, e.y, activeDeck);
          return (
            <group key={e.id} position={[ex, 0.4, ez]}>
              <mesh>
                <boxGeometry args={[3.2, 0.8, 3.2]} />
                <meshStandardMaterial color="#06b6d4" emissive="#0891b2" emissiveIntensity={0.7} />
              </mesh>
              <Text
                position={[0, 2.0, 0]}
                fontSize={0.8}
                color="#06b6d4"
                anchorX="center"
                anchorY="middle"
                outlineWidth={0.05}
                outlineColor="#000000"
              >
                {e.name.includes("Aft") ? "AFT LIFT" : (e.name.includes("Mid") ? "MID PANORAMIC" : "FWD LIFT")}
              </Text>
            </group>
          );
        })}

      {/* Restrooms on Active Deck */}
      {layers.toilets &&
        toilets.map((t) => {
          const [tx, ty, tz] = normToThree(t.x, t.y, activeDeck);
          return (
            <group key={t.id} position={[tx, 0.3, tz]}>
              <mesh>
                <sphereGeometry args={[0.9, 12, 12]} />
                <meshStandardMaterial color="#a855f7" emissive="#9333ea" emissiveIntensity={0.6} />
              </mesh>
              <Text
                position={[0, 1.5, 0]}
                fontSize={0.7}
                color="#c084fc"
                anchorX="center"
                anchorY="middle"
                outlineWidth={0.04}
                outlineColor="#000000"
              >
                WC
              </Text>
            </group>
          );
        })}
    </group>
  );
}

// ----------------------------------------------------------------------
// Animated Route Waypoint Trail
// ----------------------------------------------------------------------
function RouteOverlay({ activeRoute }: { activeRoute: RouteResult | null }) {
  if (!activeRoute || !activeRoute.waypoints_3d || activeRoute.waypoints_3d.length < 2) {
    return null;
  }

  const points = activeRoute.waypoints_3d.map((wp) => {
    const [x, y, z] = normToThree(wp.x, wp.y, wp.deck);
    return new THREE.Vector3(x, y + 0.8, z);
  });

  return (
    <group>
      <Line
        points={points}
        color="#f43f5e"
        lineWidth={4}
        dashed
        dashScale={2}
        dashSize={1}
        gapSize={0.5}
      />
      {points.map((p, idx) => (
        <mesh key={idx} position={p}>
          <sphereGeometry args={[0.5, 12, 12]} />
          <meshBasicMaterial color={idx === 0 ? "#10b981" : (idx === points.length - 1 ? "#f43f5e" : "#fbbf24")} />
        </mesh>
      ))}
    </group>
  );
}

// ----------------------------------------------------------------------
// Master Canvas Component
// ----------------------------------------------------------------------
export default function ShipCanvas3D({
  viewMode,
  activeDeck,
  selectedCabin,
  selectedVenue,
  hoveredCabin,
  activeRoute,
  layers,
  onSelectCabin,
  onHoverCabin,
  onSelectVenue,
  onSelectDeck,
}: ShipCanvasProps) {
  return (
    <div className="relative w-full h-full bg-slate-950 select-none">
      <Canvas
        camera={{ position: [0, 45, 120], fov: 45 }}
        gl={{ antialias: true, powerPreference: "high-performance" }}
      >
        <ambientLight intensity={0.7} />
        <directionalLight position={[60, 100, 50]} intensity={1.5} castShadow />
        <pointLight position={[0, 40, 0]} intensity={0.8} color="#38bdf8" />

        <CameraRig
          viewMode={viewMode}
          activeDeck={activeDeck}
          selectedCabin={selectedCabin}
          selectedVenue={selectedVenue}
        />

        <ShipHullModel
          activeDeck={activeDeck}
          viewMode={viewMode}
          onSelectDeck={onSelectDeck}
        />

        <DeckStateroomLayer
          activeDeck={activeDeck}
          selectedCabin={selectedCabin}
          selectedVenue={selectedVenue}
          hoveredCabin={hoveredCabin}
          layers={layers}
          onSelectCabin={onSelectCabin}
          onHoverCabin={onHoverCabin}
          onSelectVenue={onSelectVenue}
        />

        <RouteOverlay activeRoute={activeRoute} />
      </Canvas>
    </div>
  );
}
