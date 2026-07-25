"""The container image's contract with the code that runs inside it.

These are static checks on the Dockerfile, not a build — CI has no Docker
daemon. They exist because the ways this image can be wrong are quiet ones:
the console silently not served, the database written into a layer the next
deploy discards. Both are invisible until a user hits them, and both are a
mismatch between two files that nothing else keeps in step.
"""

import re
from pathlib import Path

from jim import mobile

DOCKERFILE = (Path(__file__).resolve().parents[2] / "Dockerfile").read_text()


def _env(name: str) -> str | None:
    """The value the Dockerfile's ENV instructions give ``name``."""
    m = re.search(rf"^\s*{name}=(\S+)", DOCKERFILE, re.MULTILINE)
    return m.group(1) if m else None


def test_console_dir_points_at_where_the_build_is_copied():
    """The regression this file was written for.

    ``console_dir`` resolves ``app/dist`` relative to the *package*, and after
    ``pip install`` the package lives in site-packages — nowhere near the dist
    the image copies to /srv. Only the explicit override makes the two agree,
    so the image must set it, and to exactly the COPY destination.
    """
    assert _env("JIM_CONSOLE_DIR") == "/srv/app/dist"
    assert re.search(r"COPY --from=console /src/app/dist \./app/dist", DOCKERFILE)
    assert "WORKDIR /srv" in DOCKERFILE


def test_console_dir_honours_the_override(tmp_path, monkeypatch):
    """And that the override is load-bearing in the code, not just the image."""
    dist = tmp_path / "dist"
    dist.mkdir()
    monkeypatch.setenv("JIM_CONSOLE_DIR", str(dist))
    assert mobile.console_dir() is None          # nothing built there yet
    (dist / "index.html").write_text("<!doctype html>")
    assert mobile.console_dir() == dist


def test_health_history_lives_on_a_mounted_volume():
    """A container restart must not lose a person's baseline: the default DB
    path has to sit under the declared volume."""
    assert _env("JIM_DB") == "/data/jim.db"
    assert 'VOLUME ["/data"]' in DOCKERFILE


def test_service_does_not_run_as_root():
    assert re.search(r"^USER jim", DOCKERFILE, re.MULTILINE)
    assert DOCKERFILE.index("USER jim") < DOCKERFILE.index("CMD ")


def test_listens_on_all_interfaces_and_honours_platform_port():
    """Binding to localhost inside a container publishes nothing; and hosts
    that assign a port need it honoured or the health check never passes."""
    cmd = DOCKERFILE[DOCKERFILE.index("CMD ["):]
    assert "--host 0.0.0.0" in cmd
    assert "${PORT:-8200}" in cmd


def test_healthcheck_matches_the_port_the_suite_harness_expects():
    """The suite compose file health-checks jim on 8200; a default that
    disagreed would leave the service permanently unhealthy there."""
    assert "EXPOSE 8200" in DOCKERFILE
    assert "http://127.0.0.1:8200/health" in DOCKERFILE
