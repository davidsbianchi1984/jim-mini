import { readFileSync } from "node:fs";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const pkg = JSON.parse(
  readFileSync(new URL("./package.json", import.meta.url), "utf8"));

// Relative base so the built bundle also loads from Electron's file:// origin.
export default defineConfig({
  plugins: [react()],
  base: "./",
  server: { port: 5173 },
  // The console knows its own version, so it can notice when the backend
  // answering its base URL is an older install's — see VersionGuard.tsx.
  define: { __APP_VERSION__: JSON.stringify(pkg.version) },
});
