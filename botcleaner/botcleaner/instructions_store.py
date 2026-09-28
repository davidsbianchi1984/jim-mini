"""Versioned instructions library (A6) and the user instruction editor (A7)."""
from __future__ import annotations

from typing import Optional

from . import security as sec
from .db import DB
from .instructions import InstructionSet, builtin_sets, validate_submission


class InstructionStore:
    def __init__(self, db: DB):
        self.db = db
        if not self.db.one("SELECT 1 FROM instructions WHERE id LIKE 'builtin:%' LIMIT 1"):
            self.seed()

    def seed(self) -> None:
        with self.db.tx() as tx:
            for s in builtin_sets():
                tx.execute("INSERT OR IGNORE INTO instructions VALUES (?,?,?)", (s.id, s.model_dump_json(), sec.iso()))

    def _all(self) -> list[InstructionSet]:
        return [InstructionSet.model_validate_json(r["data_json"]) for r in self.db.q("SELECT data_json FROM instructions")]

    def get(self, iid: str) -> InstructionSet:
        r = self.db.one("SELECT data_json FROM instructions WHERE id=?", (iid,))
        if not r:
            raise LookupError("instructions not found")
        return InstructionSet.model_validate_json(r["data_json"])

    def _put(self, s: InstructionSet) -> None:
        self.db.x("INSERT OR REPLACE INTO instructions VALUES (?,?,?)", (s.id, s.model_dump_json(), sec.iso()))

    def visible(self, s: InstructionSet, user_id: Optional[str]) -> bool:
        return s.status == "published" or (user_id is not None and s.author_id == user_id)

    def list(self, platform: Optional[str] = None, device: Optional[str] = None, action: Optional[str] = None,
             user_id: Optional[str] = None) -> list[dict]:
        out = []
        for s in self._all():
            if platform and s.platform != platform or device and s.device != device or action and s.action != action:
                continue
            if self.visible(s, user_id):
                out.append({**s.model_dump(), "outdated": s.outdated})
        out.sort(key=lambda d: (d["platform"], d["action"], d["device"], d["source"] != "user", -d["version"]))
        return out

    def best(self, platform: str, device: str, action: str, user_id: Optional[str] = None) -> dict:
        """User's own steps first, then current built-ins, then approved community steps."""
        cands = [s for s in self._all() if (s.platform, s.device, s.action) == (platform, device, action)]
        own = [s for s in cands if user_id and s.author_id == user_id and s.status != "rejected"]
        builtin = [s for s in cands if s.source == "builtin" and not s.outdated]
        community = sorted((s for s in cands if s.source == "user" and s.status == "published" and not s.outdated),
                           key=lambda s: s.outdated_flags)
        fallback = [s for s in cands if s.source == "builtin"]
        pick = (own or builtin or community or fallback or [None])[0]
        if pick is None:
            return {"steps": ["Open the profile and use the platform's Remove / Unfollow option."], "id": None}
        return {**pick.model_dump(), "outdated": pick.outdated}

    def submit(self, user_id: str, platform: str, device: str, action: str, steps: list[str],
               app_version: str = "", screenshots: Optional[list[str]] = None, share: bool = False,
               replaces: Optional[str] = None) -> dict:
        screenshots = screenshots or []
        steps = [s.strip() for s in steps if s.strip()]
        problems = validate_submission(steps, screenshots)
        if problems:
            raise ValueError(" ".join(problems))
        version = 1
        iid = sec.new_id("ins_")
        if replaces:
            old = self.get(replaces)
            if old.author_id != user_id:
                raise PermissionError("You can only edit your own instructions")
            iid, version = old.id, old.version + 1
        s = InstructionSet(id=iid, platform=platform, device=device, action=action, app_version=app_version,
                           steps=steps, screenshots=screenshots, version=version, source="user", author_id=user_id,
                           status="pending" if share else "private")
        self._put(s)
        return s.model_dump()

    def flag_outdated(self, iid: str, user_id: str) -> dict:
        s = self.get(iid)
        if self.db.one("SELECT 1 FROM instruction_flags WHERE instruction_id=? AND user_id=?", (iid, user_id)):
            return {**s.model_dump(), "outdated": s.outdated}
        self.db.x("INSERT INTO instruction_flags VALUES (?,?,?)", (iid, user_id, sec.iso()))
        s.outdated_flags += 1
        self._put(s)
        return {**s.model_dump(), "outdated": s.outdated}

    def pending(self) -> list[dict]:
        return [s.model_dump() for s in self._all() if s.status == "pending"]

    def moderate(self, iid: str, approve: bool) -> dict:
        s = self.get(iid)
        if s.status != "pending":
            raise ValueError("Only pending submissions can be moderated")
        # Re-validate at publish time: the rules may have tightened since submission.
        if approve and validate_submission(s.steps, s.screenshots):
            approve = False
        s.status = "published" if approve else "rejected"
        self._put(s)
        return s.model_dump()

    def update_builtin(self, platform: str, device: str, action: str, steps: list[str]) -> dict:
        """Ops publishes a new built-in version (resets outdated flags)."""
        iid = f"builtin:{platform}:{device}:{action}"
        s = self.get(iid)
        s.steps, s.version, s.outdated_flags = steps, s.version + 1, 0
        self._put(s)
        self.db.x("DELETE FROM instruction_flags WHERE instruction_id=?", (iid,))
        return s.model_dump()

