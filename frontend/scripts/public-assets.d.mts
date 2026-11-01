export const PROTECTED_PATHS: string[];
export function excludeProtectedAssets(dist?: string, source?: string): void;
export function checkPublicAssets(dist?: string, source?: string): void;
export function publicMediaPlugin(): import('vite').Plugin;
