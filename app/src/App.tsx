import { useState } from "react";
import { useSession } from "./store";
import { ProblemNotice } from "./ProblemNotice";
import { VersionGuard } from "./VersionGuard";
import { Help } from "./Help";
import { Onboarding } from "./screens/Onboarding";
import { Home } from "./screens/Home";
import { Monitor } from "./screens/Monitor";
import { Baseline } from "./screens/Baseline";
import { Meds } from "./screens/Meds";
import { CareTeam } from "./screens/CareTeam";
import { Community } from "./screens/Community";
import { Coach } from "./screens/Coach";
import { Checkin } from "./screens/Checkin";
import { Journal } from "./screens/Journal";
import { Wellness } from "./screens/Wellness";
import { Channel } from "./screens/Channel";
import { Safety } from "./screens/Safety";
import { Settings } from "./screens/Settings";
import { Aims } from "./screens/Aims";
import { Wards } from "./screens/Wards";
import { Attending } from "./screens/Attending";
import { Reach } from "./screens/Reach";
import { Bearing } from "./screens/Bearing";
import { Held } from "./screens/Held";

type Tab = "home" | "monitor" | "baseline" | "meds" | "careteam" | "coach" | "wellness" | "checkin" | "journal" | "community" | "safety" | "channel" | "aims" | "wards" | "attending" | "reach" | "bearing" | "held" | "settings";
const NAV: { id: Tab; label: string; icon: string }[] = [
  { id: "home", label: "Overview", icon: "◎" },
  { id: "monitor", label: "Live Monitoring", icon: "❤" },
  { id: "safety", label: "Safety", icon: "🆘" },
  { id: "baseline", label: "Your Baseline", icon: "📈" },
  { id: "meds", label: "Medications", icon: "💊" },
  { id: "careteam", label: "Care Team", icon: "👥" },
  { id: "coach", label: "Coach", icon: "🧠" },
  { id: "wellness", label: "Wellness", icon: "🧘" },
  { id: "checkin", label: "Check-in", icon: "🌿" },
  { id: "journal", label: "Journal", icon: "📖" },
  { id: "aims", label: "What you're working on", icon: "🎯" },
  { id: "wards", label: "Who you watch", icon: "🧒" },
  { id: "attending", label: "Who else is looking", icon: "🩺" },
  { id: "reach", label: "What reaches out", icon: "🤖" },
  { id: "bearing", label: "Bearing", icon: "🧭" },
  { id: "community", label: "Community", icon: "🗣" },
  { id: "channel", label: "Channel & camera", icon: "🎙" },
  { id: "held", label: "What's held about you", icon: "🗄" },
  { id: "settings", label: "Privacy", icon: "🛡" },
];

export function App() {
  const { session, signOut } = useSession();
  const [tab, setTab] = useState<Tab>("home");
  // The guard wraps onboarding too: a mismatched backend at sign-up is
  // the same trap, one screen earlier.
  if (!session.userId) return <><VersionGuard /><Onboarding /><Help /></>;
  return (
    <div className="app">
      <VersionGuard />
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
        <ProblemNotice />
        {tab === "home" && <Home go={setTab} />}
        {tab === "meds" && <Meds />}
        {tab === "careteam" && <CareTeam />}
        {tab === "monitor" && <Monitor />}
        {tab === "baseline" && <Baseline />}
        {tab === "coach" && <Coach />}
        {tab === "wellness" && <Wellness />}
        {tab === "checkin" && <Checkin />}
        {tab === "journal" && <Journal />}
        {tab === "community" && <Community />}
        {tab === "safety" && <Safety />}
        {tab === "channel" && <Channel />}
        {tab === "aims" && <Aims />}
        {tab === "wards" && <Wards />}
        {tab === "attending" && <Attending />}
        {tab === "reach" && <Reach />}
        {tab === "bearing" && <Bearing />}
        {tab === "held" && <Held />}
        {tab === "settings" && <Settings />}
      </main>
      {/* Part of the shell: the help box is on every screen, like the
          version guard — the one screen without it is the one somebody is
          lost on. */}
      <Help />
    </div>
  );
}
