"""Guided-removal instructions: built-in, versioned, and user-contributed.

Built-in steps exist for every platform x device x action the app can queue.
Anyone can flag a step set as outdated. Users can write their own corrected
steps (A7); those are private to the author until a moderator approves them
for sharing, and submissions that point at login or password pages are
rejected outright.
"""
from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

PLATFORMS = ("x", "facebook", "instagram", "tiktok", "linkedin")
DEVICES = ("web", "ios", "android")
ACTIONS = ("unfriend", "remove_follower", "unfollow")

# Which actions make sense on which platform.
PLATFORM_ACTIONS = {
    "x": ("remove_follower", "unfollow"),
    "facebook": ("unfriend", "remove_follower", "unfollow"),
    "instagram": ("remove_follower", "unfollow"),
    "tiktok": ("remove_follower", "unfollow"),
    "linkedin": ("unfriend", "unfollow"),
}


class InstructionSet(BaseModel):
    id: str
    platform: str
    device: str
    action: str
    app_version: str = ""
    steps: list[str]
    screenshots: list[str] = Field(default_factory=list)
    version: int = 1
    source: str = "builtin"          # builtin | user
    author_id: Optional[str] = None
    status: str = "published"        # published | private | pending | rejected
    outdated_flags: int = 0

    @field_validator("platform")
    @classmethod
    def _p(cls, v: str) -> str:
        if v not in PLATFORMS:
            raise ValueError(f"unknown platform {v}")
        return v

    @field_validator("device")
    @classmethod
    def _d(cls, v: str) -> str:
        if v not in DEVICES:
            raise ValueError(f"unknown device {v}")
        return v

    @field_validator("action")
    @classmethod
    def _a(cls, v: str) -> str:
        if v not in ACTIONS:
            raise ValueError(f"unknown action {v}")
        return v

    @property
    def outdated(self) -> bool:
        return self.outdated_flags >= 3


_OPEN = {
    "x": "Open the account's profile on X",
    "facebook": "Open the person's Facebook profile",
    "instagram": "Open the account's Instagram profile",
    "tiktok": "Open the account's TikTok profile",
    "linkedin": "Open the person's LinkedIn profile",
}

# (platform, action) -> device -> steps. {open} is replaced with the platform's first step.
_BUILTIN: dict[tuple[str, str], dict[str, list[str]]] = {
    ("x", "unfollow"): {
        "web": ["{open} (use the link next to the account).", "Hover over the 'Following' button until it reads 'Unfollow'.", "Click 'Unfollow', then confirm 'Unfollow' in the dialog."],
        "ios": ["{open} (tap the link next to the account).", "Tap 'Following'.", "Tap 'Unfollow @handle' to confirm."],
        "android": ["{open} (tap the link next to the account).", "Tap 'Following'.", "Tap 'Unfollow' to confirm."],
    },
    ("x", "remove_follower"): {
        "web": ["Go to your profile and click 'Followers'.", "Find the account and click the ... (More) button on its row.", "Choose 'Remove this follower', then confirm 'Remove'."],
        "ios": ["Go to your profile and tap 'Followers'.", "Find the account and tap the ... (More) button.", "Tap 'Remove this follower', then 'Remove'."],
        "android": ["Go to your profile and tap 'Followers'.", "Find the account and tap the ⋮ (More) button.", "Tap 'Remove this follower', then 'Remove'."],
    },
    ("facebook", "unfriend"): {
        "web": ["{open}.", "Click the 'Friends' button under their cover photo.", "Choose 'Unfriend', then confirm."],
        "ios": ["{open}.", "Tap the 'Friends' button.", "Tap 'Unfriend', then 'Confirm'."],
        "android": ["{open}.", "Tap the 'Friends' button.", "Tap 'Unfriend', then 'Confirm'."],
    },
    ("facebook", "remove_follower"): {
        "web": ["Go to your profile > Friends > Followers.", "Find the person and click ... next to their name.", "Choose 'Remove follower' (if missing, open their profile and choose Block; you can unblock later)."],
        "ios": ["Go to your profile > See all friends > Followers.", "Tap ... next to the person.", "Tap 'Remove follower' or, if missing, 'Block'."],
        "android": ["Go to your profile > See all friends > Followers.", "Tap ⋯ next to the person.", "Tap 'Remove follower' or, if missing, 'Block'."],
    },
    ("facebook", "unfollow"): {
        "web": ["{open} (or Page).", "Click 'Following' (or the ... menu).", "Choose 'Unfollow'."],
        "ios": ["{open} (or Page).", "Tap 'Following'.", "Tap 'Unfollow'."],
        "android": ["{open} (or Page).", "Tap 'Following'.", "Tap 'Unfollow'."],
    },
    ("instagram", "remove_follower"): {
        "web": ["Go to your profile and click 'followers'.", "Find the account in the list.", "Click 'Remove' next to it, then confirm 'Remove'."],
        "ios": ["Go to your profile and tap 'followers'.", "Search for the account.", "Tap 'Remove', then 'Remove' again to confirm."],
        "android": ["Go to your profile and tap 'followers'.", "Search for the account.", "Tap 'Remove', then 'Remove' again to confirm."],
    },
    ("instagram", "unfollow"): {
        "web": ["{open}.", "Click 'Following'.", "Click 'Unfollow'."],
        "ios": ["{open}.", "Tap 'Following'.", "Tap 'Unfollow'."],
        "android": ["{open}.", "Tap 'Following'.", "Tap 'Unfollow'."],
    },
    ("tiktok", "remove_follower"): {
        "web": ["Go to your profile and click 'Followers'.", "Find the account and click ... next to it.", "Choose 'Remove this follower' and confirm."],
        "ios": ["Go to Profile and tap 'Followers'.", "Tap ... next to the account.", "Tap 'Remove this follower', then 'Remove'."],
        "android": ["Go to Profile and tap 'Followers'.", "Tap ⋮ next to the account.", "Tap 'Remove this follower', then 'Remove'."],
    },
    ("tiktok", "unfollow"): {
        "web": ["{open}.", "Click the 'Following' button (person icon with a check).", "It switches to 'Follow' — done."],
        "ios": ["{open}.", "Tap the 'Following' button.", "Tap 'Unfollow' if asked to confirm."],
        "android": ["{open}.", "Tap the 'Following' button.", "Tap 'Unfollow' if asked to confirm."],
    },
    ("linkedin", "unfriend"): {
        "web": ["{open}.", "Click 'More' under their headline.", "Choose 'Remove connection', then 'Remove'."],
        "ios": ["{open}.", "Tap '...' (More).", "Tap 'Remove connection', then 'Remove'."],
        "android": ["{open}.", "Tap '...' (More).", "Tap 'Remove connection', then 'Remove'."],
    },
    ("linkedin", "unfollow"): {
        "web": ["{open}.", "Click 'More', then 'Unfollow'.", "Confirm 'Unfollow'."],
        "ios": ["{open}.", "Tap '...', then 'Unfollow'.", "Confirm."],
        "android": ["{open}.", "Tap '...', then 'Unfollow'.", "Confirm."],
    },
}


def builtin_sets() -> list[InstructionSet]:
    out: list[InstructionSet] = []
    for (platform, action), devices in _BUILTIN.items():
        for device, steps in devices.items():
            out.append(InstructionSet(
                id=f"builtin:{platform}:{device}:{action}",
                platform=platform, device=device, action=action,
                steps=[s.replace("{open}", _OPEN[platform]) for s in steps],
            ))
    return out


# Anything that looks like it wants credentials is refused for community steps.
_CREDENTIAL = re.compile(
    r"(password|passcode|log ?in|sign ?in|verify (your )?account|2fa|two[- ]factor|otp|one[- ]time code|"
    r"recovery code|seed phrase|credit card)",
    re.I,
)
_URL = re.compile(r"(https?://\S+|www\.\S+|\b[\w-]+\.(com|net|org|io|ly|me|co|app)\b\S*)", re.I)
_ALLOWED_HOSTS = ("x.com", "twitter.com", "facebook.com", "instagram.com", "tiktok.com", "linkedin.com", "help.")


def validate_submission(steps: list[str], screenshots: list[str]) -> list[str]:
    """Problems with a user submission; empty when acceptable."""
    problems: list[str] = []
    if not steps or not any(s.strip() for s in steps):
        problems.append("Add at least one step.")
    if len(steps) > 20:
        problems.append("Keep it to 20 steps or fewer.")
    for i, s in enumerate(steps, 1):
        if len(s) > 500:
            problems.append(f"Step {i} is too long.")
        for m in _URL.finditer(s):
            url = m.group(0).lower()
            if not any(h in url for h in _ALLOWED_HOSTS):
                problems.append(f"Step {i} links outside the platform ({m.group(0)}); links are only allowed to the platform itself.")
            if _CREDENTIAL.search(url):
                problems.append(f"Step {i} links to a login or password page; that's never needed to remove an account.")
        if _CREDENTIAL.search(s) and re.search(r"(enter|type|give|share|send|provide)", s, re.I):
            problems.append(f"Step {i} asks for a password or code; removal never needs one.")
    for u in screenshots:
        if not u.startswith(("data:image/", "/uploads/")):
            problems.append("Screenshots must be uploaded images, not links.")
    return problems
