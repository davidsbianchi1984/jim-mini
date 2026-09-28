"""Parse each platform's data export into the one ``Connection`` schema.

Users download their own data ("Download Your Information" on Facebook,
"Download your information" on Instagram, TikTok's "Download your data",
LinkedIn's "Get a copy of your data", X's archive) and upload the file here.
We accept the whole .zip or the individual JSON/CSV/JS files inside it.

The raw upload is parsed in memory and never written to disk; the store keeps
only the normalised connections, and those are purged with the raw-data TTL.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import zipfile
from datetime import datetime, timezone
from typing import Any, Iterator

from .models import Connection, Direction, Platform


class ImportError_(ValueError):
    """The upload could not be understood as the named platform's export."""


def _ts(v: Any) -> datetime | None:
    if v in (None, "", 0):
        return None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(float(v), tz=timezone.utc)
    s = str(v).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d %b %Y", "%Y-%m-%d", "%b %d, %Y"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _name_id(platform: str, name: str) -> str:
    """Stable id for exports that give only a display name (Facebook)."""
    return "n-" + hashlib.sha1(f"{platform}:{name.strip().lower()}".encode()).hexdigest()[:16]


# ---- Instagram ----------------------------------------------------------------

def _ig_entries(items: list) -> Iterator[tuple[str, str | None, Any]]:
    for it in items:
        sld = it.get("string_list_data") or [{}]
        d = sld[0] if sld else {}
        handle = d.get("value") or it.get("title") or ""
        href = d.get("href")
        if not handle and href:
            handle = href.rstrip("/").split("/")[-1]
        if handle:
            yield handle, href, d.get("timestamp")


def parse_instagram(name: str, data: bytes) -> list[Connection]:
    obj = json.loads(data.decode("utf-8"))
    out: list[Connection] = []
    if isinstance(obj, list):  # followers_1.json is a bare list
        direction, items = Direction.follower, obj
    elif isinstance(obj, dict) and "relationships_following" in obj:
        direction, items = Direction.following, obj["relationships_following"]
    elif isinstance(obj, dict) and "relationships_followers" in obj:
        direction, items = Direction.follower, obj["relationships_followers"]
    else:
        return []
    for handle, href, ts in _ig_entries(items):
        out.append(Connection(
            platform=Platform.instagram, account_id=handle.lower(), handle=handle, name="",
            direction=direction, connected_at=_ts(ts),
            profile_url=href or f"https://www.instagram.com/{handle}/",
        ))
    return out


# ---- Facebook -----------------------------------------------------------------

_FB_KEYS = {
    "friends_v2": Direction.friend,
    "friends": Direction.friend,
    "following_v3": Direction.following,
    "following_v2": Direction.following,
    "followers_v2": Direction.follower,
    "followers": Direction.follower,
}


def _fb_fix(s: str) -> str:
    # Facebook exports double-encode UTF-8 as latin-1 escapes.
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def parse_facebook(name: str, data: bytes) -> list[Connection]:
    obj = json.loads(data.decode("utf-8"))
    out: list[Connection] = []
    if isinstance(obj, list):
        pairs = [("followers" if "follow" in name.lower() and "who_you" not in name.lower() else "following_v3", obj)]
    else:
        pairs = [(k, v) for k, v in obj.items() if k in _FB_KEYS]
    for key, items in pairs:
        direction = _FB_KEYS.get(key, Direction.following)
        for it in items:
            nm = _fb_fix(it.get("name") or it.get("title") or "")
            if not nm:
                continue
            out.append(Connection(
                platform=Platform.facebook, account_id=_name_id("facebook", nm), handle="", name=nm,
                direction=direction, connected_at=_ts(it.get("timestamp")),
                profile_url="https://www.facebook.com/search/top?q=" + re.sub(r"\s+", "%20", nm),
            ))
    return out


# ---- TikTok -------------------------------------------------------------------

def _walk(obj: Any, key: str) -> Iterator[Any]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                yield v
            else:
                yield from _walk(v, key)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v, key)


def parse_tiktok(name: str, data: bytes) -> list[Connection]:
    text = data.decode("utf-8")
    out: list[Connection] = []
    if name.lower().endswith(".txt"):
        # TXT exports: blocks of "Date: ...\nUsername: ..."
        direction = Direction.following if "following" in name.lower() else Direction.follower
        for m in re.finditer(r"Date:\s*(.+?)\s*\n\s*User(?:name|Name):\s*(\S+)", text):
            out.append(_tt(m.group(2), m.group(1), direction))
        return out
    obj = json.loads(text)
    for lst in _walk(obj, "FansList"):
        for it in lst or []:
            out.append(_tt(it.get("UserName"), it.get("Date"), Direction.follower))
    for lst in _walk(obj, "Following"):
        if isinstance(lst, list):
            for it in lst:
                out.append(_tt(it.get("UserName"), it.get("Date"), Direction.following))
    return [c for c in out if c.handle]


def _tt(handle: str | None, date: Any, direction: Direction) -> Connection:
    handle = (handle or "").strip()
    return Connection(
        platform=Platform.tiktok, account_id=handle.lower(), handle=handle, direction=direction,
        connected_at=_ts(date), profile_url=f"https://www.tiktok.com/@{handle}",
    )


# ---- LinkedIn -----------------------------------------------------------------

def parse_linkedin(name: str, data: bytes) -> list[Connection]:
    text = data.decode("utf-8-sig")
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("First Name")), None)
    if start is None:
        raise ImportError_("Connections.csv header not found")
    out: list[Connection] = []
    for row in csv.DictReader(io.StringIO("\n".join(lines[start:]))):
        first, last = (row.get("First Name") or "").strip(), (row.get("Last Name") or "").strip()
        url = (row.get("URL") or "").strip()
        nm = f"{first} {last}".strip()
        if not nm and not url:
            continue
        slug = url.rstrip("/").split("/")[-1] if url else ""
        out.append(Connection(
            platform=Platform.linkedin, account_id=slug.lower() or _name_id("linkedin", nm),
            handle=slug, name=nm, direction=Direction.friend,
            connected_at=_ts(row.get("Connected On")), profile_url=url or None,
            bio=" ".join(x for x in [(row.get("Position") or "").strip(), (row.get("Company") or "").strip()] if x) or None,
        ))
    return out


# ---- X archive (fallback when the API is unavailable) ----------------------------

def parse_x_archive(name: str, data: bytes) -> list[Connection]:
    text = data.decode("utf-8")
    text = re.sub(r"^\s*window\.YTD\.\w+\.part\d+\s*=\s*", "", text)
    items = json.loads(text)
    out: list[Connection] = []
    for it in items:
        for key, direction in (("follower", Direction.follower), ("following", Direction.following)):
            if key in it:
                acc = it[key]
                aid = str(acc.get("accountId", ""))
                if aid:
                    out.append(Connection(
                        platform=Platform.x, account_id=aid, direction=direction,
                        profile_url=acc.get("userLink") or f"https://x.com/i/user/{aid}",
                    ))
    return out


# ---- dispatch -------------------------------------------------------------------

_RELEVANT = {
    Platform.instagram: re.compile(r"(followers(_\d+)?|following)\.json$", re.I),
    Platform.facebook: re.compile(r"(your_friends|friends|who_you've_followed|who_you_follow|followers|people_who_followed_you)[^/]*\.json$", re.I),
    Platform.tiktok: re.compile(r"(user_data(_tiktok)?\.json|follower[^/]*\.txt|following[^/]*\.txt)$", re.I),
    Platform.linkedin: re.compile(r"connections\.csv$", re.I),
    Platform.x: re.compile(r"(follower|following)\.js$", re.I),
}
_PARSERS = {
    Platform.instagram: parse_instagram,
    Platform.facebook: parse_facebook,
    Platform.tiktok: parse_tiktok,
    Platform.linkedin: parse_linkedin,
    Platform.x: parse_x_archive,
}

MAX_UPLOAD = 200 * 1024 * 1024
MAX_UNCOMPRESSED = 500 * 1024 * 1024


def import_export(platform: Platform, filename: str, data: bytes) -> list[Connection]:
    """Parse an uploaded export (zip or single file) for ``platform``."""
    if len(data) > MAX_UPLOAD:
        raise ImportError_("Upload is too large")
    parser = _PARSERS[platform]
    files: list[tuple[str, bytes]] = []
    if data[:2] == b"PK":
        try:
            zf = zipfile.ZipFile(io.BytesIO(data))
        except zipfile.BadZipFile as exc:
            raise ImportError_("Not a valid zip file") from exc
        total = 0
        for info in zf.infolist():
            if info.is_dir() or not _RELEVANT[platform].search(info.filename):
                continue
            total += info.file_size
            if total > MAX_UNCOMPRESSED:
                raise ImportError_("Export is too large once unzipped")
            files.append((info.filename, zf.read(info)))
    else:
        files.append((filename, data))
    out: list[Connection] = []
    for name, blob in files:
        try:
            out.extend(parser(name, blob))
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            if len(files) == 1:
                raise ImportError_(f"Could not read {name} as a {platform.value} export: {exc}") from exc
    if not out:
        raise ImportError_(f"No {platform.value} friends, followers or following found in the upload")
    # One record per (account, direction).
    seen: dict[tuple, Connection] = {}
    for c in out:
        seen.setdefault((c.account_id, c.direction), c)
    return list(seen.values())


# In-app steps for getting each export (shown on the import screen).
EXPORT_HELP: dict[str, list[str]] = {
    "instagram": [
        "Open Instagram > Settings > Accounts Center > Your information and permissions > Download your information.",
        "Choose 'Some of your information' and tick 'Followers and following'.",
        "Pick Format: JSON, Date range: All time, then Create files.",
        "When the email arrives, download the .zip and upload it here.",
    ],
    "facebook": [
        "Open Facebook > Settings & privacy > Settings > Accounts Center > Your information and permissions > Download your information.",
        "Choose 'Some of your information' and tick 'Friends and followers'.",
        "Pick Format: JSON, Date range: All time, then Create files.",
        "Download the .zip when it's ready and upload it here.",
    ],
    "tiktok": [
        "Open TikTok > Profile > Menu > Settings and privacy > Account > Download your data.",
        "Choose 'Custom', tick 'Profile' and 'Activity', select file format JSON, and request data.",
        "When the file is ready (the 'Download data' tab), download it and upload it here.",
    ],
    "linkedin": [
        "Open LinkedIn > Me > Settings & Privacy > Data privacy > Get a copy of your data.",
        "Select 'Connections' and request the archive.",
        "Download the file (about 10 minutes later) and upload the .zip or Connections.csv here.",
    ],
    "x": [
        "Prefer 'Connect X' — it reads your lists through the official API and supports one-click removal.",
        "Without API access: Settings > Your account > Download an archive of your data, then upload the .zip here.",
    ],
}
