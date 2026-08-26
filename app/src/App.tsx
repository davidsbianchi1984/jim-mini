import { useEffect, useRef, useState, type ReactNode } from "react";
import { useSession } from "./store";
import { t as tr, visitorLang } from "./l10n";
import { applyTheme, loadTheme } from "./theme";
import { ProblemNotice } from "./ProblemNotice";
import { Footsteps } from "./Footsteps";
import { VersionGuard } from "./VersionGuard";
import { GuardianLights } from "./GuardianLights";
import { Underway } from "./Underway";
import { WalkAlong } from "./WalkAlong";
import { onWalk } from "./walk";
import { Help } from "./Help";
import { JimMiniOS } from "./JimMiniOS";
import { Studio } from "./screens/Studio";
import { Talk } from "./screens/Talk";
import { Onboarding } from "./screens/Onboarding";
import { Home } from "./screens/Home";
import { Monitor } from "./screens/Monitor";
import { Baseline } from "./screens/Baseline";
import { Meds } from "./screens/Meds";
import { CareTeam } from "./screens/CareTeam";
import { SelfProfile } from "./screens/SelfProfile";
import { Community } from "./screens/Community";
import { Feed } from "./screens/Feed";
import { Presence } from "./screens/Presence";
import { Coach } from "./screens/Coach";
import { Engaged } from "./screens/Engaged";
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
import { Access } from "./screens/Access";
import { Watch } from "./screens/Watch";

type Tab = "watch" | "studio" | "permits" | "home" | "presence" | "feed" | "monitor" | "baseline" | "meds" | "careteam" | "selfprofile" | "coach" | "engaged" | "wellness" | "checkin" | "journal" | "community" | "safety" | "channel" | "aims" | "wards" | "attending" | "reach" | "bearing" | "held" | "access" | "settings";
// Labels live in `l10n.ts` and are looked up by id — see `nav.*` there.
//
// They used to sit here as English literals, which made the console's own
// navigation the one surface no language could reach: the phones carry ten,
// the server answers in the reader's, and the frame around both was English
// whatever anybody chose.
//
// `icon` is a node rather than a string because one of these is a drawn mark
// and not a glyph: ABRACADABRA carries the jim-mini amulet (`JimMiniOS.tsx`),
// which no character in any font can say. Everything else stays a character;
// widening the type costs nothing and does not oblige the other twenty-three
// to become art.
//
// It carries the *amulet*, not the whole lockup, and the tiles are back to
// menu size because of it. A field report: *menu icons are too large remove
// the word abracadabra if it helps make it smaller*. The lockup needs 72px
// to read, so a menu around it was a menu around its largest tile; the
// triangle survives at 34 and the word lives on the label underneath, where
// it is a word rather than eleven rows of 3px type.
const NAV: { id: Tab; icon: ReactNode }[] = [
  { id: "home", icon: "◎" },
  { id: "watch", icon: "⌚" },
  { id: "monitor", icon: "❤" },
  { id: "safety", icon: "🆘" },
  { id: "baseline", icon: "📈" },
  { id: "meds", icon: "💊" },
  { id: "careteam", icon: "👥" },
  { id: "selfprofile", icon: "🪞" },
  { id: "coach", icon: "🧠" },
  { id: "engaged", icon: <JimMiniOS /> },
  { id: "wellness", icon: "🧘" },
  { id: "checkin", icon: "🌿" },
  { id: "journal", icon: "📖" },
  { id: "aims", icon: "🎯" },
  { id: "wards", icon: "🧒" },
  { id: "attending", icon: "🩺" },
  { id: "reach", icon: "🤖" },
  { id: "bearing", icon: "🧭" },
  { id: "community", icon: "🗣" },
  { id: "presence", icon: "◍" },
  { id: "feed", icon: "▶" },
  { id: "channel", icon: "🎙" },
  // The permit switches had no door of their own — the screen existed,
  // rendered under `tab === "permits"`, and was reachable only through the
  // assistant's chip rail. A screen about what the assistant may change
  // must not be a screen only the assistant can open.
  { id: "permits", icon: "🛂" },
  { id: "held", icon: "🗄" },
  { id: "access", icon: "♿" },
  { id: "settings", icon: "🛡" },
];

export function App() {
  const { session, signOut } = useSession();
  const [tab, setTab] = useState<Tab>("home");

  // Pressing walk lands on the front page.
  //
  // The point of taking a conversation with you is going somewhere, and the
  // screen you were on is the one place you have finished with. Leaving
  // somebody on the coach screen with the strip lit means the first thing
  // they do is find their way out of it; the overview is where the whole
  // console is reachable from, and from there the app itself is one swipe
  // from being left behind.
  //
  //     asked     did the conversation survive
  //     mattered  can they now go anywhere
  //
  // Here rather than in the four screens that offer the button: the shell
  // owns navigation, and a screen that set the tab itself would be a second
  // definition of where the front door is.
  useEffect(() => onWalk((w) => { if (w) setTab("home"); }), []);
  // Every screen opened where the last one was scrolled to. A field report:
  // *I just went to this menu and it still doesn't pin to the top it jumps
  // into the middle of the material*. `.content` is the scrolling element in
  // both layouts — the desktop column and the phone's single pane — so the
  // pane is scrolled rather than the window, which on a phone is not the
  // thing that moved. `instant` because this is a new screen, not a journey
  // through the old one, and an animated fly-up reads as content moving.
  const content = useRef<HTMLElement>(null);
  useEffect(() => {
    content.current?.scrollTo({ top: 0, behavior: "instant" });
  }, [tab]);
  // The accessibility statement and its report door open before sign-in —
  // the person that screen exists for may be the person the enrollment
  // shut out. `#access` in the URL lands there directly, so a line in an
  // email can point at the form rather than at a sign-up page.
  const [publicAccess, setPublicAccess] = useState(
    window.location.hash === "#access");
  // The watch surface answers to the URL the same way, and — like the
  // accessibility door — before sign-in: the README links every face
  // drawing to `#watch/<slug>`, and a link that demanded an account first
  // would land thirty-six drawings on a sign-up page. Signed out, each
  // face says what it needs; the CPR metronome needs nothing at all.
  const [watchOpen, setWatchOpen] = useState(
    window.location.hash.startsWith("#watch"));
  useEffect(() => {
    const onHash = () => {
      if (window.location.hash.startsWith("#watch")) setWatchOpen(true);
    };
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);
  // The document's own language attribute, so a screen reader pronounces
  // the page in the language it is actually written in — index.html ships
  // lang="en" and the app renders ten languages under it.
  useEffect(() => { document.documentElement.lang = visitorLang(); }, []);
  // The look this person chose — in Settings or by asking the engaged
  // agent — applied on sign-in and cleared on sign-out, so a shared
  // browser never wears the previous account's colors.
  useEffect(() => {
    if (session.userId && session.userToken) {
      void loadTheme(session.userId, session.userToken);
    } else {
      applyTheme("standard");
    }
  }, [session.userId]);
  if (watchOpen) {
    return (
      <>
        <VersionGuard />
        <Watch lang={visitorLang()} onClose={() => setWatchOpen(false)} />
      </>
    );
  }
  // The guard wraps onboarding too: a mismatched backend at sign-up is
  // the same trap, one screen earlier.
  if (!session.userId) {
    if (publicAccess) {
      return (
        <>
          <VersionGuard />
          <Footsteps />
          <div className="content" style={{ maxWidth: 720, margin: "0 auto", padding: 20 }}>
            <button className="linkish" onClick={() => {
              setPublicAccess(false);
              if (window.location.hash) window.location.hash = "";
            }}>{tr("onb.back", visitorLang())}</button>
            <Access />
          </div>
          <Help />
        </>
      );
    }
    return <><VersionGuard /><Footsteps /><Onboarding onAccess={() => setPublicAccess(true)} /><Help /></>;
  }
  return (
    <div className="app">
      <VersionGuard />
      <Footsteps />
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
            <button key={n.id} className={"nav-item" + (tab === n.id ? " active" : "")} onClick={() => {
              // The watch is a place rather than a pane — it takes the
              // whole viewport and the URL, so the README's face links
              // and the menu entry arrive through the same door.
              if (n.id === "watch") { window.location.hash = "#watch"; setWatchOpen(true); }
              else setTab(n.id);
            }}>
              <span className="nav-icon">{n.icon}</span>{tr(`nav.${n.id}`, visitorLang())}
            </button>
          ))}
        </nav>
        <div className="guard-chip"><span className="dot-online">●</span> Guardian on · watching</div>
        <button className="signout" onClick={signOut}>Sign out</button>
      </aside>
      <main className="content" ref={content}>
        <ProblemNotice />
        {tab === "home" && <Home go={setTab} />}
        {tab === "meds" && <Meds />}
        {tab === "careteam" && <CareTeam />}
        {tab === "selfprofile" && <SelfProfile />}
        {tab === "monitor" && <Monitor />}
        {tab === "baseline" && <Baseline />}
        {tab === "coach" && <Coach go={setTab} />}
        {tab === "engaged" && <Talk go={(id) => setTab(id as Tab)} />}
        {tab === "permits" && <Engaged />}
        {tab === "studio" && <Studio />}
        {tab === "wellness" && <Wellness />}
        {tab === "checkin" && <Checkin />}
        {tab === "journal" && <Journal />}
        {tab === "community" && <Community />}
        {tab === "presence" && <Presence />}
        {tab === "feed" && <Feed />}
        {tab === "safety" && <Safety />}
        {tab === "channel" && <Channel />}
        {tab === "aims" && <Aims />}
        {tab === "wards" && <Wards />}
        {tab === "attending" && <Attending />}
        {tab === "reach" && <Reach />}
        {tab === "bearing" && <Bearing />}
        {tab === "held" && <Held />}
        {tab === "access" && <Access />}
        {tab === "settings" && <Settings />}
      </main>
      {/* Part of the shell: the help box is on every screen, like the
          version guard — the one screen without it is the one somebody is
          lost on. */}
      <Help />
      {/* Like Help: part of the shell, on every screen — the Guardian's
          lights, minimizable, and never silently absent. */}
      <GuardianLights />
      {/* The task window, and shell furniture for the same reason: *which
          agent is running, which tasks are still running* is a question you
          ask when you do not know which screen to open, so it cannot live
          on one of them. Beside the lights rather than inside them — that
          panel answers whether anything is wrong, this one what is being
          done, and folding the two together would blur both. */}
      <Underway />
      {/* Shell furniture for the sharpest version of the same reason: this
          one *has* to outlive the screen it started on, because the whole
          point of it is that the person changed screens. Inside `<main>` it
          would unmount with the conversation it was carrying. */}
      <WalkAlong />
    </div>
  );
}
