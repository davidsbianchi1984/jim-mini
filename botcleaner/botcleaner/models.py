"""One schema for every platform's connections, and the shapes the engine hands back.

Every importer (data exports) and every connector (official APIs) produces
``Connection`` records. The scoring service turns them into ``ScoredAccount``s.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Platform(str, Enum):
    x = "x"
    facebook = "facebook"
    instagram = "instagram"
    tiktok = "tiktok"
    linkedin = "linkedin"


class Direction(str, Enum):
    friend = "friend"
    follower = "follower"
    following = "following"


class Label(str, Enum):
    likely_bot = "likely_bot"      # 85-100, pre-selected for removal
    suspicious = "suspicious"      # 60-84, shown for review
    low_confidence = "low_confidence"  # 40-59, hidden unless expanded
    looks_real = "looks_real"      # 0-39, not flagged


def label_for(score: float) -> Label:
    if score >= 85:
        return Label.likely_bot
    if score >= 60:
        return Label.suspicious
    if score >= 40:
        return Label.low_confidence
    return Label.looks_real


class Connection(BaseModel):
    """One account in one of the user's lists, in one direction."""

    platform: Platform
    account_id: str
    handle: str = ""
    name: str = ""
    direction: Direction
    connected_at: Optional[datetime] = None
    avatar_hash: Optional[str] = None  # 64-bit perceptual hash, hex

    # Profile details, when the source provides them (X API does; exports mostly don't).
    profile_url: Optional[str] = None
    created_at: Optional[datetime] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    bio: Optional[str] = None
    has_default_avatar: Optional[bool] = None
    verified: Optional[bool] = None

    # History the app has seen for this account (handle drift, follow-back bait).
    previous_handles: list[str] = Field(default_factory=list)
    previous_names: list[str] = Field(default_factory=list)
    followed_user_at: Optional[datetime] = None      # when they followed the user
    unfollowed_user_at: Optional[datetime] = None    # when they stopped
    user_followed_back_at: Optional[datetime] = None
    last_interaction_at: Optional[datetime] = None   # user's last like/comment/DM with them

    # Behaviour, where data exists.
    post_timestamps: list[datetime] = Field(default_factory=list)
    recent_posts: list[str] = Field(default_factory=list)
    repost_ratio: Optional[float] = None
    audience_bot_share: Optional[float] = None  # share of their own follower sample scoring as bots

    # Graph context: ids of the user's other connections this account is connected to.
    mutual_ids: list[str] = Field(default_factory=list)

    @property
    def key(self) -> str:
        return f"{self.platform.value}:{self.account_id}"


class Reason(BaseModel):
    code: str
    text: str
    weight: float


class ScoredAccount(BaseModel):
    connection: Connection
    score: float
    label: Label
    reasons: list[Reason]
    is_clone: bool = False
    clone_of: Optional[str] = None  # account_id of the real friend being impersonated
    ring_id: Optional[str] = None

    @property
    def top_reasons(self) -> list[str]:
        return [r.text for r in self.reasons[:3]]
