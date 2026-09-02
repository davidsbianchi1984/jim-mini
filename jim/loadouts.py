"""The model menu, by region — a loadout per market, and a lever to taper.

The registry (:mod:`jim.llm`) knows every provider and where it is from. This
module decides which of them an account is *offered*, and the answer depends on
where the person signed up:

* **A per-region loadout.** Each region gets its own particular set — its home
  providers first, then a curated few popular foreign ones for that market. A
  US account sees American models plus a handful of the foreign ones people
  actually ask for; a Chinese account sees Qwen, DeepSeek, Kimi and GLM first;
  Europe leads with Mistral. Anywhere not mapped gets the widest sensible set.
* **A lever, not a rewrite.** ``JIM_MODEL_POLICY=american`` tapers the
  *American-region* loadout to American, local and self-supplied providers —
  the change the government might one day ask for, made in one line and
  affecting only the accounts it would apply to. Other regions are not bound
  by it. Default is ``all``, which is the beta posture.
* **The region is a fact on the account**, chosen at sign-up and editable
  (``users.region``), never inferred from an address later.

Three menus read this: the basic model picker, the coding assistant
(:mod:`jim.appedits`), and video generation. One table to curate.
"""

from __future__ import annotations

import os

from . import audit, db, llm

#: The sign-up choices. Short codes, and `other` for anywhere unmapped.
REGIONS = ("us", "ca", "eu", "uk", "cn", "in", "jp", "kr", "br", "au", "other")
DEFAULT_REGION = "us"
POLICIES = ("all", "american")

#: The American set, in the order the menu shows it. Anthropic leads — it is
#: the beta default (the platform's own key carries users until they bring
#: their own).
_AMERICAN = ("anthropic", "openai", "gemini", "grok", "meta", "azure", "bedrock",
             "perplexity", "groq", "together", "fireworks", "nvidia")
#: The ones that never leave the machine, or point at the user's own endpoint.
#: Offered everywhere, under every policy.
_LOCAL = ("ollama", "vault", "custom", "stub")

#: region -> the providers offered there, home first, then a curated few
#: popular foreign. Edit here to grow a region; nothing else needs to change.
LOADOUTS: dict[str, tuple[str, ...]] = {
    "us": _AMERICAN + ("deepseek", "mistral", "qwen", "moonshot"),
    "ca": _AMERICAN + ("cohere", "mistral", "deepseek"),
    "eu": ("mistral",) + _AMERICAN + ("cohere", "deepseek", "qwen"),
    "uk": _AMERICAN + ("mistral", "cohere", "deepseek"),
    "cn": ("qwen", "deepseek", "moonshot", "zhipu") + _AMERICAN + ("mistral",),
    "in": _AMERICAN + ("deepseek", "qwen", "mistral", "cohere"),
    "jp": _AMERICAN + ("deepseek", "qwen", "mistral"),
    "kr": _AMERICAN + ("deepseek", "qwen", "mistral"),
    "br": _AMERICAN + ("deepseek", "mistral", "qwen"),
    "au": _AMERICAN + ("deepseek", "mistral", "cohere"),
    "other": _AMERICAN + ("deepseek", "mistral", "qwen", "moonshot", "zhipu",
                          "cohere"),
}

#: Video generation, the same shape. Mostly consumed by QRME (where profiles
#: render video); named here so all three menus curate from one place.
VIDEO_PROVIDERS: dict[str, dict] = {
    "runway": {"label": "Runway", "origin": "US"},
    "pika": {"label": "Pika", "origin": "US"},
    "luma": {"label": "Luma Dream Machine", "origin": "US"},
    "veo": {"label": "Veo (Google)", "origin": "US"},
    "sora": {"label": "Sora (OpenAI)", "origin": "US"},
    "higgsfield": {"label": "Higgsfield AI", "origin": "US"},
    "kling": {"label": "Kling", "origin": "CN"},
    "hailuo": {"label": "Hailuo (MiniMax)", "origin": "CN"},
    "vidu": {"label": "Vidu", "origin": "CN"},
    "seedance": {"label": "Seedance (ByteDance)", "origin": "CN"},
}
_VIDEO_AMERICAN = ("runway", "pika", "luma", "veo", "sora", "higgsfield")
VIDEO_LOADOUTS: dict[str, tuple[str, ...]] = {
    "us": _VIDEO_AMERICAN + ("kling", "hailuo"),
    "cn": ("kling", "hailuo", "vidu", "seedance") + _VIDEO_AMERICAN,
    "other": _VIDEO_AMERICAN + ("kling", "hailuo", "vidu", "seedance"),
}


def policy() -> str:
    got = os.environ.get("JIM_MODEL_POLICY", "all").strip().lower()
    return got if got in POLICIES else "all"


def region_of(user_id: str) -> str:
    row = db.connect().execute(
        "SELECT region FROM users WHERE id=?", (user_id,)).fetchone()
    region = (row["region"] if row else None) or DEFAULT_REGION
    return region if region in REGIONS else "other"


def set_region(user_id: str, region: str) -> dict:
    region = (region or "").strip().lower()
    if region not in REGIONS:
        raise ValueError("that is not a region this product offers a menu for")
    conn = db.connect()
    conn.execute("UPDATE users SET region=? WHERE id=?", (region, user_id))
    conn.commit()
    audit.record("region.set", user_id=user_id, ref=region)
    return {"user_id": user_id, "region": region,
            "providers": providers_for(user_id)}


def _tapered(names: tuple[str, ...], region: str) -> list[str]:
    """Apply the policy. `american` narrows the American-region loadout to
    American, local and self-supplied providers; every other region keeps its
    own loadout — the rule is about US accounts, not about the world."""
    if policy() == "american" and region == DEFAULT_REGION:
        return [n for n in names
                if llm.origin_of(n) in ("US", "local", "any")]
    return list(names)


def loadout_for(region: str) -> list[str]:
    base = LOADOUTS.get(region, LOADOUTS["other"])
    names = tuple(dict.fromkeys(base + _LOCAL))     # ordered, de-duplicated
    return [n for n in _tapered(names, region) if n in llm._REGISTRY]


def providers_for(user_id: str) -> list[str]:
    return loadout_for(region_of(user_id))


def allowed(user_id: str, name: str) -> bool:
    return name == "auto" or name in providers_for(user_id)


def offered(user_id: str) -> list[dict]:
    """The registry rows this account is offered, in loadout order, each
    carrying its origin so a screen can say where a model is from."""
    by_name = {p["name"]: p for p in llm.available()}
    return [by_name[n] for n in providers_for(user_id) if n in by_name]


def video_providers_for(user_id: str) -> list[dict]:
    region = region_of(user_id)
    base = VIDEO_LOADOUTS.get(region, VIDEO_LOADOUTS["other"])
    if policy() == "american" and region == DEFAULT_REGION:
        base = tuple(n for n in base if VIDEO_PROVIDERS[n]["origin"] == "US")
    return [{"name": n, **VIDEO_PROVIDERS[n]} for n in base]
