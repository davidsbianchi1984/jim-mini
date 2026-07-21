import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Relative base so the built bundle also loads from Electron's file:// origin.
export default defineConfig({
  plugins: [react()],
  base: "./",
  server: { port: 5173 },
});
