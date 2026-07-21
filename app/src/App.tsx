import { useState } from "react";
import { useSession } from "./store";
import { Onboarding } from "./screens/Onboarding";
import { Home } from "./screens/Home";
import { Monitor } from "./screens/Monitor";
import { Coach } from "./screens/Coach";
import { Checkin } from "./screens/Checkin";
import { Settings } from "./screens/Settings";

type Tab = "home" | "monitor" | "coach" | "checkin" | "settings";
const NAV: { id: Tab; label: string; icon: string }[] = [
  { id: "home", label: "Overview", icon: "◎" },
  { id: "monitor", label: "Live Monitoring", icon: "❤" },
  { id: "coach", label: "Coach", icon: "🧠" },
  { id: "checkin", label: "Check-in", icon: "🌿" },
  { id: "settings", label: "Privacy", icon: "🛡" },
];

export function App() {
  const { session, signOut } = useSession();
  const [tab, setTab] = useState<Tab>("home");
  if (!session.userId) return <Onboarding />;
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="orb" />
          <div>
            <div className="brand-name">JIM</div>
            <div className="brand-sub">Guardian guidance</div>
          </div>
        </div>
        <nav>
          {NAV.map((n) => (
            <button key={n.id} className={"nav-item" + (tab === n.id ? " active" : "")} onClick={() => setTab(n.id)}>
              <span className="nav-icon">{n.icon}</span>{n.label}
            </button>
          ))}
        </nav>
        <div className="guard-chip"><span className="dot-online">●</span> Guardian on · watching</div>
        <button className="signout" onClick={signOut}>Sign out</button>
      </aside>
      <main className="content">
        {tab === "home" && <Home go={setTab} />}
        {tab === "monitor" && <Monitor />}
        {tab === "coach" && <Coach />}
        {tab === "checkin" && <Checkin />}
        {tab === "settings" && <Settings />}
      </main>
    </div>
  );
}
