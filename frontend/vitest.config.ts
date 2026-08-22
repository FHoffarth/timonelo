import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

/**
 * Vitest is scoped to `.test.ts` / `.test.tsx` deliberately.
 *
 * The repository also contains `.test.mts` files under `src/`. Those are
 * standalone Node scripts using `node:assert`, documented as "runnable with
 * plain Node", and they contain no Vitest suite. Collecting them would fail the
 * run for files that were never Vitest specs, so the include pattern excludes
 * them rather than the files being changed or removed.
 */
export default defineConfig({
  plugins: [react()],
  test: {
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
    environment: "node",
  },
});
