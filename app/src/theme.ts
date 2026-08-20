// The look, applied. One place turns the server's `theme` word into the
// body class styles.css styles against, so the Settings select, the sign-in
// load, and the engaged agent's set_appearance all land on the same pixels.
import { api } from "./api";

const LOOKS = ["midnight", "paper"] as const;

/** Put the named look on the page. Unknown names (and "standard") clear
 *  back to the shipped palette rather than guessing — a stale word from an
 *  older server should never strand the console in a half-theme. */
export function applyTheme(theme: string): void {
  for (const look of LOOKS) {
    document.body.classList.toggle(`theme-${look}`,
                                   theme === look);
  }
}

/** Read this person's look and apply it. Never throws: an unreachable
 *  read leaves the palette as it is, which is the honest failure for a
 *  cosmetic setting. */
export async function loadTheme(uid: string, token: string): Promise<void> {
  try {
    applyTheme((await api.getAppearance(uid, token)).theme);
  } catch { /* the shipped palette stands */ }
}
