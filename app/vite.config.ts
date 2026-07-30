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
  define: {
    // The console knows its own version, so it can notice when the backend
    // answering its base URL is an older install's — see VersionGuard.tsx.
    __APP_VERSION__: JSON.stringify(pkg.version),
    // Which product this is. `errors.ts` is byte-identical in all three repos,
    // so it cannot work this out for itself; naming it here is cheaper than
    // three copies of a file that differ by one string.
    __APP_SOURCE__: JSON.stringify("jim-mini"),
    // Where content-free error reports go, and the token to post them with.
    // Unset means an installer with nowhere to send — which is the default,
    // and a stronger one than a flag: there is no address for a later mistake
    // to switch on. Set both when building a release that should report:
    //   PROBLEM_COLLECTOR=https://gw.example.com PROBLEM_TOKEN=… npm run build
    __PROBLEM_COLLECTOR__: JSON.stringify(process.env.PROBLEM_COLLECTOR || ""),
    __PROBLEM_TOKEN__: JSON.stringify(process.env.PROBLEM_TOKEN || ""),
  },
});
