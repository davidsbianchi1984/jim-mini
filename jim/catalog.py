"""The connected-apps catalog.

Beyond the social platforms (``social.py``), the Guardian and its agents can
connect to the AI-integrated **apps** on a person's devices — the same surfaces
Apple Intelligence, Google Gemini, Microsoft Copilot and Canva expose.
Each entry declares:

- ``provider`` / ``app`` — who and what;
- ``capabilities`` — the AI features that app offers;
- ``directions`` — how a connector uses it:
    * ``collect`` — pull context in (build the profile / inform the agent),
    * ``act``     — drive the app agentically (create an event, run a shortcut),
    * ``produce`` — generate output (images, movies, designs).

This is reference data — read-only — that the connect flow validates against.
"""

from __future__ import annotations

# provider, app, label, capabilities, directions
_ROWS = [
    # ---- Apple Intelligence -------------------------------------------------
    ("apple", "photos", "Photos",
     ["semantic-search", "clean-up", "memory-movies", "spatial-reframe",
      "image-playground", "genmoji"], ["collect", "produce"]),
    ("apple", "calendar", "Calendar",
     ["nl-event", "suggested-reminders", "siri-actions"], ["collect", "act"]),
    ("apple", "mail", "Mail",
     ["thread-summary", "smart-reply", "priority", "order-tracking"], ["collect", "act"]),
    ("apple", "messages", "Messages",
     ["summaries", "smart-reply", "live-translation", "poll-suggestions",
      "context-suggestions", "backgrounds"], ["collect", "act"]),
    ("apple", "files", "Files", ["file-management"], ["collect", "act"]),
    ("apple", "notes", "Notes",
     ["transcription-summary", "intelligent-processing"], ["collect", "act"]),
    ("apple", "reminders", "Reminders",
     ["auto-categorize", "suggested", "nl-siri"], ["collect", "act"]),
    ("apple", "safari", "Safari",
     ["browsing-tools", "describe-extension"], ["collect", "act"]),
    ("apple", "shortcuts", "Shortcuts",
     ["intelligent-actions", "on-device-model"], ["act"]),
    ("apple", "passwords", "Passwords", ["weak-password-detect"], ["collect", "act"]),
    ("apple", "wallet", "Wallet", ["order-tracking"], ["collect"]),
    ("apple", "phone", "Phone & FaceTime",
     ["live-translation", "context-aware"], ["act"]),
    ("apple", "system", "System (Writing Tools · Siri · Visual Intelligence)",
     ["writing-tools", "siri", "visual-intelligence", "genmoji",
      "image-playground"], ["collect", "act", "produce"]),

    # ---- Google Gemini ------------------------------------------------------
    ("google", "photos", "Google Photos",
     ["nl-search", "personal-intelligence", "video-remix", "remix",
      "moods", "ask-photos"], ["collect", "produce"]),
    ("google", "calendar", "Google Calendar",
     ["nl-schedule", "live-automation"], ["collect", "act"]),
    ("google", "gmail", "Gmail",
     ["summaries", "smart-reply", "workspace-automation"], ["collect", "act"]),
    ("google", "keep", "Keep & Tasks",
     ["read-write", "multi-step"], ["collect", "act"]),
    ("google", "maps", "Maps",
     ["navigation", "location-tasks"], ["collect", "act"]),
    ("google", "chrome", "Chrome",
     ["sidebar-summary", "auto-browse"], ["collect", "act"]),
    ("google", "youtube", "YouTube",
     ["recommendations"], ["collect", "produce"]),
    ("google", "play_store", "Play Store",
     ["conversational-search", "install"], ["act"]),
    ("google", "gboard", "Gboard", ["typing-assist"], ["act"]),
    ("google", "files", "Files",
     ["file-handling", "appfunctions"], ["collect", "act"]),
    ("google", "system", "Gemini (agentic · Live · AppFunctions)",
     ["agentic-tasks", "gemini-live", "appfunctions", "autofill"],
     ["collect", "act", "produce"]),

    # ---- Microsoft Copilot --------------------------------------------------
    ("microsoft", "photos", "Photos",
     ["generative-erase", "restyle", "super-resolution", "relight",
      "auto-categorize", "semantic-search"], ["collect", "produce"]),
    ("microsoft", "file_explorer", "File Explorer",
     ["summarize", "extract", "nl-search", "ai-actions"], ["collect", "act"]),
    ("microsoft", "notepad", "Notepad", ["writing-tools"], ["act", "produce"]),
    ("microsoft", "paint", "Paint", ["cocreator", "image-gen"], ["produce"]),
    ("microsoft", "snipping_tool", "Snipping Tool", ["capture-ai"], ["collect"]),
    ("microsoft", "settings", "Settings", ["nl-settings"], ["act"]),
    ("microsoft", "m365", "Microsoft 365",
     ["drafting", "excel-analysis", "ppt-creation", "email-mgmt", "agents"],
     ["collect", "act", "produce"]),
    ("microsoft", "copilot", "Copilot (Vision · Recall · Click-to-Do)",
     ["vision", "voice", "recall", "click-to-do", "agents"],
     ["collect", "act", "produce"]),

    # ---- Canva Magic Studio -------------------------------------------------
    ("canva", "magic_studio", "Canva Magic Studio",
     ["magic-design", "magic-media", "magic-write", "magic-edit",
      "magic-switch", "magic-layers", "background-remover", "translate"],
     ["act", "produce"]),
]

_PROVIDER_LABEL = {
    "apple": "Apple Intelligence",
    "google": "Google Gemini",
    "microsoft": "Microsoft Copilot",
    "canva": "Canva Magic Studio",
}

CONNECTORS = [
    {"provider": p, "app": a, "label": lbl, "capabilities": caps, "directions": dirs}
    for (p, a, lbl, caps, dirs) in _ROWS
]

# Fast lookup for validation: (provider, app) -> entry.
BY_KEY = {(c["provider"], c["app"]): c for c in CONNECTORS}


def catalog() -> dict:
    """The full catalog, grouped by provider (for the connect picker)."""
    groups: dict[str, dict] = {}
    for c in CONNECTORS:
        g = groups.setdefault(c["provider"], {
            "provider": c["provider"],
            "label": _PROVIDER_LABEL[c["provider"]],
            "apps": [],
        })
        g["apps"].append({"app": c["app"], "label": c["label"],
                          "capabilities": c["capabilities"], "directions": c["directions"]})
    return {"providers": list(groups.values()),
            "app_count": len(CONNECTORS),
            "provider_count": len(groups)}
