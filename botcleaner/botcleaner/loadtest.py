"""Load tests (PRD section 7.10): time a full import + scan end to end.

    python -m botcleaner.loadtest --module a --size 1000000
    python -m botcleaner.loadtest --module b --size 1000000

Module A: store connections and scan them for one user (the path an upload takes).
Module B: ingest accounts and scan them for one tenant.
Prints wall-clock time and throughput so results can be compared release to release.
"""
from __future__ import annotations

import argparse
import os
import tempfile
import time
from datetime import datetime, timezone

from . import evaluation as ev
from .db import DB
from .models import Platform
from .personal import PersonalService
from .purge.console import PurgeService


def run_a(size: int, db_path: str) -> dict:
    n_bots = max(1, size // 10)
    s = ev.seeded_network(n_real=size - n_bots, n_bots=n_bots, n_clones=min(500, size // 100 or 1),
                          n_following_bad=min(300, size // 100 or 1), seed=2, now=datetime.now(timezone.utc))
    svc = PersonalService(DB(db_path))
    uid, _ = svc.register("load@example.com")
    t0 = time.perf_counter()
    svc.store_connections(uid, Platform.x, s.conns)
    t1 = time.perf_counter()
    out = svc.scan(uid)
    t2 = time.perf_counter()
    return {"module": "A", "connections": len(s.conns), "store_s": round(t1 - t0, 1), "scan_s": round(t2 - t1, 1),
            "total_s": round(t2 - t0, 1), "per_second": round(len(s.conns) / (t2 - t0)), "labels": out["counts"]}


def run_b(size: int, db_path: str) -> dict:
    accs, _ = ev.seeded_site(n_real=size - size // 10, n_bots=size // 10, seed=3, now=datetime.now(timezone.utc))
    svc = PurgeService(DB(db_path))
    tid, _ = svc.create_tenant("load")
    t0 = time.perf_counter()
    svc.ingest(tid, accs)
    t1 = time.perf_counter()
    out = svc.scan(tid)
    t2 = time.perf_counter()
    return {"module": "B", "accounts": len(accs), "ingest_s": round(t1 - t0, 1), "scan_s": round(t2 - t1, 1),
            "total_s": round(t2 - t0, 1), "per_second": round(len(accs) / (t2 - t0)), "labels": out["labels"]}


def main() -> None:  # pragma: no cover - CLI
    p = argparse.ArgumentParser()
    p.add_argument("--module", choices=["a", "b"], default="a")
    p.add_argument("--size", type=int, default=100_000)
    a = p.parse_args()
    with tempfile.TemporaryDirectory() as d:
        os.environ.setdefault("BOTCLEANER_KEYFILE", os.path.join(d, "k"))
        fn = run_a if a.module == "a" else run_b
        print(fn(a.size, os.path.join(d, "load.sqlite3")))


if __name__ == "__main__":  # pragma: no cover
    main()
