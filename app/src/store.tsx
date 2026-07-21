import React, { createContext, useContext, useEffect, useState } from "react";

export interface Session {
  userId?: string;
  userToken?: string;
  displayName?: string;
}
interface Ctx {
  session: Session;
  setSession: (s: Session) => void;
  signOut: () => void;
}
const SessionContext = createContext<Ctx | null>(null);
const KEY = "jim.session";

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [session, setState] = useState<Session>(() => {
    try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch { return {}; }
  });
  useEffect(() => { localStorage.setItem(KEY, JSON.stringify(session)); }, [session]);
  const setSession = (s: Session) => setState((p) => ({ ...p, ...s }));
  const signOut = () => { setState({}); localStorage.removeItem(KEY); };
  return (
    <SessionContext.Provider value={{ session, setSession, signOut }}>
      {children}
    </SessionContext.Provider>
  );
}
export function useSession(): Ctx {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSession must be used within SessionProvider");
  return ctx;
}
