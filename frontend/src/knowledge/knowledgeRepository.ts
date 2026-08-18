// Canonical Frontend Knowledge Repository
// Direct bridge to the canonical Knowledge Layer (knowledge/ships/ and knowledge/ports/)

import bellissimaTechnical from '../../../knowledge/ships/msc-bellissima/technical.json';
import bellissimaDecks from '../../../knowledge/ships/msc-bellissima/decks.json';
import bellissimaPublicAreas from '../../../knowledge/ships/msc-bellissima/public_areas.json';
import bellissimaRestaurants from '../../../knowledge/ships/msc-bellissima/restaurants.json';
import bellissimaBars from '../../../knowledge/ships/msc-bellissima/bars.json';
import bellissimaLounges from '../../../knowledge/ships/msc-bellissima/lounges.json';
import bellissimaPools from '../../../knowledge/ships/msc-bellissima/pools.json';
import bellissimaKids from '../../../knowledge/ships/msc-bellissima/kids.json';
import bellissimaSpa from '../../../knowledge/ships/msc-bellissima/spa.json';
import bellissimaSports from '../../../knowledge/ships/msc-bellissima/sports.json';
import bellissimaEntertainment from '../../../knowledge/ships/msc-bellissima/entertainment.json';
import bellissimaMuster from '../../../knowledge/ships/msc-bellissima/muster.json';
import bellissimaCabins from '../../../knowledge/ships/msc-bellissima/cabins.json';

import bcnPort from '../../../knowledge/ports/barcelona/port.json';
import bcnTransport from '../../../knowledge/ports/barcelona/transport.json';
import bcnEmergency from '../../../knowledge/ports/barcelona/emergency.json';
import bcnMedical from '../../../knowledge/ports/barcelona/medical.json';
import bcnWeather from '../../../knowledge/ports/barcelona/weather.json';
import bcnSustainability from '../../../knowledge/ports/barcelona/sustainability.json';

import mrsPort from '../../../knowledge/ports/marseille/port.json';
import mrsTransport from '../../../knowledge/ports/marseille/transport.json';
import mrsEmergency from '../../../knowledge/ports/marseille/emergency.json';
import mrsMedical from '../../../knowledge/ports/marseille/medical.json';
import mrsWeather from '../../../knowledge/ports/marseille/weather.json';
import mrsSustainability from '../../../knowledge/ports/marseille/sustainability.json';

import goaPort from '../../../knowledge/ports/genoa/port.json';
import goaTransport from '../../../knowledge/ports/genoa/transport.json';
import goaEmergency from '../../../knowledge/ports/genoa/emergency.json';
import goaMedical from '../../../knowledge/ports/genoa/medical.json';
import goaWeather from '../../../knowledge/ports/genoa/weather.json';
import goaSustainability from '../../../knowledge/ports/genoa/sustainability.json';

import napPort from '../../../knowledge/ports/naples/port.json';
import napTransport from '../../../knowledge/ports/naples/transport.json';
import napEmergency from '../../../knowledge/ports/naples/emergency.json';
import napMedical from '../../../knowledge/ports/naples/medical.json';
import napWeather from '../../../knowledge/ports/naples/weather.json';
import napSustainability from '../../../knowledge/ports/naples/sustainability.json';

import msnPort from '../../../knowledge/ports/messina/port.json';
import msnTransport from '../../../knowledge/ports/messina/transport.json';
import msnEmergency from '../../../knowledge/ports/messina/emergency.json';
import msnMedical from '../../../knowledge/ports/messina/medical.json';
import msnWeather from '../../../knowledge/ports/messina/weather.json';
import msnSustainability from '../../../knowledge/ports/messina/sustainability.json';

import mlaPort from '../../../knowledge/ports/valletta/port.json';
import mlaTransport from '../../../knowledge/ports/valletta/transport.json';
import mlaEmergency from '../../../knowledge/ports/valletta/emergency.json';
import mlaMedical from '../../../knowledge/ports/valletta/medical.json';
import mlaWeather from '../../../knowledge/ports/valletta/weather.json';
import mlaSustainability from '../../../knowledge/ports/valletta/sustainability.json';

export interface ShipTechnicalData {
  vessel_id: string;
  vessel_name: string;
  provenance: any;
  technical_specifications: {
    class: string;
    imo_number: number;
    builder: string;
    tonnage_gt: number;
    dimensions: {
      length_meters: number;
      length_feet: number;
      beam_meters: number;
      beam_feet: number;
      draft_meters: number;
      draft_feet_inches: string;
    };
    capacities: {
      total_decks: number;
      passenger_accessible_decks: number;
      passenger_capacity_double_occupancy: number;
      passenger_capacity_max_occupancy: number;
      crew_capacity_min: number;
      crew_capacity_max: number;
      total_cabins_min: number;
      total_cabins_max: number;
      balcony_cabin_percentage: number;
    };
    propulsion_and_power: any;
    key_milestones: any;
    connectivity_and_smart_systems: any;
  };
  refurbishment_history: any[];
}

export class FrontendKnowledgeRepository {
  private ships: Record<string, {
    technical: ShipTechnicalData;
    decks: any;
    public_areas: any;
    restaurants: any;
    bars: any;
    lounges: any;
    pools: any;
    kids: any;
    spa: any;
    sports: any;
    entertainment: any;
    muster: any;
    cabins: any;
  }> = {
    'msc-bellissima': {
      technical: bellissimaTechnical as unknown as ShipTechnicalData,
      decks: bellissimaDecks,
      public_areas: bellissimaPublicAreas,
      restaurants: bellissimaRestaurants,
      bars: bellissimaBars,
      lounges: bellissimaLounges,
      pools: bellissimaPools,
      kids: bellissimaKids,
      spa: bellissimaSpa,
      sports: bellissimaSports,
      entertainment: bellissimaEntertainment,
      muster: bellissimaMuster,
      cabins: bellissimaCabins,
    }
  };

  private ports: Record<string, {
    port: any;
    transport: any;
    emergency: any;
    medical: any;
    weather: any;
    sustainability: any;
  }> = {
    barcelona: { port: bcnPort, transport: bcnTransport, emergency: bcnEmergency, medical: bcnMedical, weather: bcnWeather, sustainability: bcnSustainability },
    marseille: { port: mrsPort, transport: mrsTransport, emergency: mrsEmergency, medical: mrsMedical, weather: mrsWeather, sustainability: mrsSustainability },
    genoa: { port: goaPort, transport: goaTransport, emergency: goaEmergency, medical: goaMedical, weather: goaWeather, sustainability: goaSustainability },
    naples: { port: napPort, transport: napTransport, emergency: napEmergency, medical: napMedical, weather: napWeather, sustainability: napSustainability },
    messina: { port: msnPort, transport: msnTransport, emergency: msnEmergency, medical: msnMedical, weather: msnWeather, sustainability: msnSustainability },
    valletta: { port: mlaPort, transport: mlaTransport, emergency: mlaEmergency, medical: mlaMedical, weather: mlaWeather, sustainability: mlaSustainability },
  };

  public getShip(shipId: string): ShipTechnicalData {
    const vessel = this.ships[shipId];
    if (!vessel) {
      throw new Error(`Ship '${shipId}' not found in canonical KnowledgeRepository`);
    }
    return vessel.technical;
  }

  public getDecks(shipId: string): any[] {
    const vessel = this.ships[shipId];
    return vessel ? vessel.decks.decks : [];
  }

  public getDeck(shipId: string, deckNumberOrId: number | string): any {
    const decks = this.getDecks(shipId);
    const targetNum = typeof deckNumberOrId === 'number' ? deckNumberOrId : parseInt(String(deckNumberOrId), 10);
    for (const d of decks) {
      if (!isNaN(targetNum) && d.deck_number === targetNum) return d;
      if (String(d.id).toLowerCase() === String(deckNumberOrId).toLowerCase()) return d;
    }
    return null;
  }

  public getRestaurants(shipId: string): any[] {
    const vessel = this.ships[shipId];
    return vessel ? vessel.restaurants.restaurants : [];
  }

  public getBars(shipId: string): any[] {
    const vessel = this.ships[shipId];
    return vessel ? vessel.bars.bars : [];
  }

  public getLounges(shipId: string): any[] {
    const vessel = this.ships[shipId];
    return vessel ? vessel.lounges.lounges : [];
  }

  public getPools(shipId: string): any[] {
    const vessel = this.ships[shipId];
    return vessel ? vessel.pools.pools_and_water_areas : [];
  }

  public getSpa(shipId: string): any {
    const vessel = this.ships[shipId];
    return vessel ? vessel.spa.spa_and_wellness : null;
  }

  public getSports(shipId: string): any[] {
    const vessel = this.ships[shipId];
    return vessel ? vessel.sports.sports_and_recreation : [];
  }

  public getEntertainment(shipId: string): any[] {
    const vessel = this.ships[shipId];
    return vessel ? vessel.entertainment.entertainment_venues : [];
  }

  public getCabins(shipId: string): any {
    const vessel = this.ships[shipId];
    return vessel ? vessel.cabins : null;
  }

  public getPublicAreas(shipId: string): any[] {
    const vessel = this.ships[shipId];
    return vessel ? vessel.public_areas.public_areas : [];
  }

  public getMuster(shipId: string): any {
    const vessel = this.ships[shipId];
    return vessel ? vessel.muster.emergency_and_muster_protocol : null;
  }

  public getKids(shipId: string): any[] {
    const vessel = this.ships[shipId];
    return vessel ? vessel.kids.kids_areas : [];
  }

  public getPort(portId: string): any {
    const p = this.ports[portId];
    return p ? p.port : null;
  }

  public getPortDomain(portId: string, domain: 'transport' | 'emergency' | 'medical' | 'weather' | 'sustainability'): any {
    const p = this.ports[portId];
    return p ? p[domain] : null;
  }

  public getAllPorts(): any[] {
    return Object.values(this.ports).map((p) => p.port);
  }
}

export const knowledgeRepository = new FrontendKnowledgeRepository();
