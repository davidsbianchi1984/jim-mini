import { useState } from "react";
import { useSession } from "./store";
import { t as tr, visitorLang } from "./l10n";
import { ProblemNotice } from "./ProblemNotice";
import { VersionGuard } from "./VersionGuard";
import { GuardianLights } from "./GuardianLights";
import { Help } from "./Help";
import { Onboarding } from "./screens/Onboarding";
import { Home } from "./screens/Home";
import { Monitor } from "./screens/Monitor";
import { Baseline } from "./screens/Baseline";
import { Meds } from "./screens/Meds";
import { CareTeam } from "./screens/CareTeam";
import { SelfProfile } from "./screens/SelfProfile";
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

type Tab = "home" | "monitor" | "baseline" | "meds" | "careteam" | "selfprofile" | "coach" | "wellness" | "checkin" | "journal" | "community" | "safety" | "channel" | "aims" | "wards" | "attending" | "reach" | "bearing" | "held" | "settings";
// Labels live in `l10n.ts` and are looked up by id — see `nav.*` there.
//
// They used to sit here as English literals, which made the console's own
// navigation the one surface no language could reach: the phones carry ten,
// the server answers in the reader's, and the frame around both was English
// whatever anybody chose.
const NAV: { id: Tab; icon: string }[] = [
  { id: "home", icon: "◎" },
  { id: "monitor", icon: "❤" },
  { id: "safety", icon: "🆘" },
  { id: "baseline", icon: "📈" },
  { id: "meds", icon: "💊" },
  { id: "careteam", icon: "👥" },
  { id: "selfprofile", icon: "🪞" },
  { id: "coach", icon: "🧠" },
  { id: "wellness", icon: "🧘" },
  { id: "checkin", icon: "🌿" },
  { id: "journal", icon: "📖" },
  { id: "aims", icon: "🎯" },
  { id: "wards", icon: "🧒" },
  { id: "attending", icon: "🩺" },
  { id: "reach", icon: "🤖" },
  { id: "bearing", icon: "🧭" },
  { id: "community", icon: "🗣" },
  { id: "channel", icon: "🎙" },
  { id: "held", icon: "🗄" },
  { id: "settings", icon: "🛡" },
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
              <span className="nav-icon">{n.icon}</span>{tr(`nav.${n.id}`, visitorLang())}
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
        {tab === "selfprofile" && <SelfProfile />}
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
      {/* Like Help: part of the shell, on every screen — the Guardian's
          lights, minimizable, and never silently absent. */}
      <GuardianLights />
    </div>
  );
}
