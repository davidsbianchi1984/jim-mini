"""HTTP client for the tandem PDI (Private Data Infrastructure) vault.

When configured, JIM stores its most sensitive payloads — medical/biometric
samples, detection details, check-in notes, and context-event data — in PDI's
encrypted vault instead of its own database, keeping only key references
locally. JIM never imports PDI internals; the boundary is HTTP.

Accepts an injected ``client`` (FastAPI ``TestClient`` / ``httpx.Client``) or
a ``base_url`` + tenant token for a real deployment.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request


class _Response:
    def __init__(self, status_code: int, body: bytes):
        self.status_code = status_code
        self._body = body

    def json(self):
        return json.loads(self._body) if self._body else None


class _UrllibClient:
    def __init__(self, base_url: str):
        self._base = base_url.rstrip("/")

    def request(self, method, path, json_body=None, headers=None) -> _Response:
        data = json.dumps(json_body).encode() if json_body is not None else None
        h = {"content-type": "application/json"}
        if headers:
            h.update(headers)
        from . import offline
        offline.allow(self._base + path, "the PDI vault")
        req = urllib.request.Request(
            self._base + path, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(req) as r:
                return _Response(r.status, r.read())
        except urllib.error.HTTPError as e:
            return _Response(e.code, e.read())


class PDIClient:
    def __init__(self, token: str, base_url: str | None = None, client=None):
        self._token = token
        self._client = client
        self._urllib = _UrllibClient(base_url) if base_url else None
        if client is None and base_url is None:
            raise ValueError("PDIClient needs base_url or an injected client")

    def _auth(self):
        return {"Authorization": f"Bearer {self._token}"}

    def _do(self, method, path, body=None):
        if self._client is not None:
            fn = getattr(self._client, method.lower())
            if body is not None:
                return fn(path, json=body, headers=self._auth())
            return fn(path, headers=self._auth())
        return self._urllib.request(method, path, json_body=body,
                                    headers=self._auth())

    def put(self, key: str, value: str) -> None:
        r = self._do("PUT", "/records", {"key": key, "value": value})
        if r.status_code >= 300:
            raise RuntimeError(f"PDI put failed: {r.status_code}")

    def get(self, key: str) -> str | None:
        r = self._do("GET", f"/records/{key}")
        if r.status_code == 404:
            return None
        if r.status_code >= 300:
            raise RuntimeError(f"PDI get failed: {r.status_code}")
        return r.json()["value"]

    # -- the resident intelligence (PDI 0.86.0, pdi/resident.py) ------------
    # The vault made smart: an embedding index, a vector search, and plans
    # whose steps write structured rows into queryable datasets. These three
    # answer False / [] against an older PDI rather than raising — the
    # caller (jim/recall.py) treats "the vault has no memory index" as a
    # state to report, not a failure to crash on.

    def resident_embed(self, key: str, text: str) -> bool:
        """Index one sealed record's text for vector search. PDI stores the
        vector and a hash of the text — never the text, which stays sealed
        under `put`."""
        r = self._do("POST", "/resident/embeddings",
                     {"key": key, "text": text})
        if r.status_code == 404:
            return False
        if r.status_code >= 300:
            raise RuntimeError(f"PDI embed failed: {r.status_code}")
        return True

    def resident_forget(self, key: str, prefix: bool = False) -> int:
        """Remove embedding vector(s) — one key, or everything under a
        prefix. The other half of `resident_embed`, and the half erasure
        stands on: a deleted memory must stop being findable. Answers 0
        against an older PDI rather than raising."""
        path = f"/resident/embeddings/{key}"
        if prefix:
            path += "?prefix=true"
        r = self._do("DELETE", path)
        if r.status_code == 404:
            return 0
        if r.status_code >= 300:
            raise RuntimeError(f"PDI forget failed: {r.status_code}")
        return r.json().get("vectors_removed", 0)

    def resident_search(self, query: str, top_k: int = 5) -> list[dict]:
        """This tenant's nearest vectors: [{key, score}], best first."""
        r = self._do("POST", "/resident/search",
                     {"query": query, "top_k": top_k})
        if r.status_code == 404:
            return []
        if r.status_code >= 300:
            raise RuntimeError(f"PDI search failed: {r.status_code}")
        return r.json().get("matches", [])

    def resident_tabulate(self, dataset: str, rows: list,
                          source_ref: str | None = None) -> bool:
        """Rows into a queryable dataset, through the resident's own doors:
        one plan carrying one `table.append` step, run in the same breath.
        There is deliberately no bare rows route — the plan is the audited
        unit — so the tandem speaks the same shape a facility tenant does."""
        step = {"tool": "table.append",
                "args": {"dataset": dataset, "rows": rows,
                         **({"source_ref": source_ref} if source_ref else {})}}
        r = self._do("POST", "/resident/tasks",
                     {"goal": f"jim-mini rows into {dataset}",
                      "steps": [step]})
        if r.status_code == 404:
            return False
        if r.status_code >= 300:
            raise RuntimeError(f"PDI tabulate plan failed: {r.status_code}")
        tid = r.json()["id"]
        ran = self._do("POST", f"/resident/tasks/{tid}/run")
        if ran.status_code >= 300:
            raise RuntimeError(f"PDI tabulate run failed: {ran.status_code}")
        return ran.json().get("status") == "done"

    def delete(self, key: str) -> bool:
        r = self._do("DELETE", f"/records/{key}")
        return r.status_code == 204

    def provenance(self, key: str) -> dict | None:
        """PDI's verifiable derivation trail for a sealed record: origin,
        seal details, audit history, chain status. None if unreadable."""
        try:
            r = self._do("GET", f"/provenance/{key}")
        except Exception:
            return None
        if r.status_code >= 300:
            return None
        return r.json()

    def audit(self) -> list[dict] | None:
        """The tenant's audit log (every vault access). None if unreadable."""
        try:
            r = self._do("GET", "/audit")
        except Exception:
            return None
        if r.status_code >= 300:
            return None
        return r.json()

    def audit_verify(self) -> bool | None:
        """Whether PDI's tamper-evident hash chain is intact. None if unknown."""
        try:
            r = self._do("GET", "/audit/verify")
        except Exception:
            return None
        if r.status_code >= 300:
            return None
        body = r.json() or {}
        return bool(body.get("valid", body.get("intact")))
