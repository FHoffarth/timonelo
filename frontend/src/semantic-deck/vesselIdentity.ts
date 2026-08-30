export class UnknownVesselError extends Error {
  constructor(vesselId: string) {
    super(`Vessel '${vesselId || "<missing>"}' is not registered`);
    this.name = "UnknownVesselError";
  }
}

/** Build an opaque lookup key only when both identity dimensions are present. */
export function vesselScopedEntityKey(
  vesselId: string | undefined | null,
  entityId: string | undefined | null,
): string | null {
  const vessel = vesselId?.trim().toLowerCase();
  const entity = entityId?.trim().toLowerCase();
  if (!vessel || !entity) return null;
  return `${vessel}\u0000${entity}`;
}
