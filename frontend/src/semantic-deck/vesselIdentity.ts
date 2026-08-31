export class UnknownVesselError extends Error {
  constructor(vesselId: string) {
    super(`Vessel '${vesselId || "<missing>"}' is not registered`);
    this.name = "UnknownVesselError";
  }
}

export class VesselOwnershipError extends Error {
  constructor() {
    super("Entity, provenance, active graph, and requested vessel ownership must match");
    this.name = "VesselOwnershipError";
  }
}

function normalizedVesselId(vesselId: string | undefined | null): string | null {
  const normalized = vesselId?.trim().toLowerCase();
  return normalized || null;
}

export function assertVesselOwnership(
  entityVesselId: string | undefined | null,
  provenanceVesselId: string | undefined | null,
  activeGraphVesselId: string | undefined | null,
  requestedVesselId: string | undefined | null,
): void {
  const identities = [
    entityVesselId,
    provenanceVesselId,
    activeGraphVesselId,
    requestedVesselId,
  ].map(normalizedVesselId);
  if (identities.some((identity) => identity === null)) {
    throw new VesselOwnershipError();
  }
  if (!identities.every((identity) => identity === identities[0])) {
    throw new VesselOwnershipError();
  }
}

/** Build an opaque lookup key only when both identity dimensions are present. */
export function vesselScopedEntityKey(
  vesselId: string | undefined | null,
  entityId: string | undefined | null,
): string | null {
  const vessel = normalizedVesselId(vesselId);
  const entity = entityId?.trim().toLowerCase();
  if (!vessel || !entity) return null;
  return `${vessel}\u0000${entity}`;
}
