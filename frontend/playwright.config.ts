import { defineConfig } from "@playwright/test";
export default defineConfig({
  testMatch: "e2e.spec.ts",
  workers: 1,
  timeout: 60000,
  use: {
    headless: true,
    viewport: { width: 1440, height: 1000 },
    launchOptions: {
      ...(process.platform === "win32" ? { channel: "msedge" } : {}),
    },
  },
  reporter: "list",
});
