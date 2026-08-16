export type Locale = 'en' | 'de';

export interface ScenarioTranslation {
  timeLabel: string;
  title: string;
  location: string;
  observation: string;
  recommendation: string;
  avoid: string;
  nextStep: string;
}

export interface Translations {
  common: {
    brandName: string;
    tagline: string;
    search: string;
    searchShortcut: string;
    searchPlaceholder: string;
    activeBridge: string;
    allAboard: string;
    readiness: string;
    musterStation: string;
    unknown: string;
    stepAboard: string;
    stepOnRiverDeck: string;
    openGangway: string;
  };
  navigation: {
    ships: string;
    destinations: string;
    bridgeTeam: string;
    philosophy: string;
    searchAria: string;
    switchLanguage: string;
  };
  hero: {
    officerStatus: string;
    deckLocation: string;
    welcome: string;
    greetingMorning: string;
    greetingAfternoon: string;
    greetingEvening: string;
    readyNotice: string;
    leadNotice: string;
    primaryCta: string;
  };
  todayOnWatch: {
    badge: string;
    title: string;
    subtitle: string;
    bridgeObservation: string;
    recommendation: string;
    whatToAvoid: string;
    nextStep: string;
    officerSignOff: string;
    officerName: string;
    scenarios: {
      embarkation: ScenarioTranslation;
      seaday: ScenarioTranslation;
      portday: ScenarioTranslation;
      evening: ScenarioTranslation;
    };
  };
  yourVoyage: {
    badge: string;
    title: string;
    subtitle: string;
    tabOcean: string;
    tabRiver: string;
    bellissimaTitle: string;
    bellissimaSubtitle: string;
    bellissimaDesc: string;
    bellissimaMuster: string;
    bellissimaStatus: string;
    andorinhaTitle: string;
    andorinhaSubtitle: string;
    andorinhaDesc: string;
    andorinhaLocks: string;
    andorinhaStyle: string;
  };
  philosophy: {
    badge: string;
    title: string;
    subtitle: string;
    reduceUncertaintyTitle: string;
    reduceUncertaintyDesc: string;
    neverInventTitle: string;
    neverInventDesc: string;
    buildCalmTitle: string;
    buildCalmDesc: string;
  };
  officerConduct: {
    badge: string;
    title: string;
    subtitle: string;
    whatIDoTitle: string;
    whatIDo1: string;
    whatIDo2: string;
    whatIDo3: string;
    whatINeverDoTitle: string;
    whatINeverDo1: string;
    whatINeverDo2: string;
    whatINeverDo3: string;
  };
  connectedSystems: {
    badge: string;
    title: string;
    subtitle: string;
    system1Badge: string;
    system1Title: string;
    system1Desc: string;
    system2Badge: string;
    system2Title: string;
    system2Desc: string;
    system3Badge: string;
    system3Title: string;
    system3Desc: string;
    system4Badge: string;
    system4Title: string;
    system4Desc: string;
  };
  logbook: {
    badge: string;
    title: string;
    subtitle: string;
    journalEntryBadge: string;
    journalLocation: string;
    journalQuote: string;
    journalSignOff: string;
    officerSignature: string;
    finalQuote: string;
  };
  footer: {
    platformDescription: string;
    navigationHeader: string;
    shipsHeader: string;
    copyright: string;
    principles: string;
  };
  notFound: {
    title: string;
    officerNote: string;
    returnToBridge: string;
    searchRegistry: string;
  };
  cabinNotice: {
    unmappedWarning: string;
    verifiedReference: string;
  };
  ports: {
    badge: string;
    title: string;
    subtitle: string;
    officerObservation: string;
    gangwayAccess: string;
    distanceToCity: string;
    terminalFacilities: string;
    localTransit: string;
    emergencyNumbers: string;
    callingFleet: string;
  };
  crew: {
    badge: string;
    title: string;
    subtitle: string;
    officerObservation: string;
    pillar1Title: string;
    pillar1Desc: string;
    pillar2Title: string;
    pillar2Desc: string;
    pillar3Title: string;
    pillar3Desc: string;
  };
  mission: {
    badge: string;
    title: string;
    subtitle: string;
    officerObservation: string;
    article1Title: string;
    article1Desc: string;
    article2Title: string;
    article2Desc: string;
    article3Title: string;
    article3Desc: string;
    article4Title: string;
    article4Desc: string;
  };
}
