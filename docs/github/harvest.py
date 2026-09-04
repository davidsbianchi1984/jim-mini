#!/usr/bin/env python3
"""Copy what GitHub holds and git does not into docs/github/.

A clone carries the code, the commits and the tags. Release notes, pull
request bodies, review threads and the repository's settings live in
GitHub's database instead. This script reads them back through the REST
API and writes them into this folder, so the clone is the whole app.

    GITHUB_TOKEN=... python3 docs/github/harvest.py

The owner and repository are read from the `origin` remote, so the same
script serves every product without editing.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
API = "https://api.github.com"


def slug() -> tuple[str, str]:
    """owner, repo — from the origin remote."""
    url = subprocess.run(["git", "-C", str(HERE), "remote", "get-url", "origin"],
                         capture_output=True, text=True, check=True).stdout.strip()
    m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?$", url)
    if not m:
        sys.exit(f"origin does not look like a GitHub remote: {url}")
    return m.group(1), m.group(2)


def get(path: str):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("set GITHUB_TOKEN in the environment first")
    req = urllib.request.Request(
        f"{API}{path}",
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "docs-github-harvest"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise


def pages(path: str) -> list:
    rows, page = [], 1
    sep = "&" if "?" in path else "?"
    while True:
        got = get(f"{path}{sep}per_page=100&page={page}")
        if not isinstance(got, list) or not got:
            return rows
        rows.extend(got)
        if len(got) < 100:
            return rows
        page += 1


def day(stamp: str | None) -> str:
    return (stamp or "")[:10]


def body_of(row: dict) -> str:
    text = (row.get("body") or "").strip()
    return text if text else "_(no body)_"


def quote(text: str) -> str:
    """Indent a body so its own headings cannot break the page's outline."""
    return "\n".join("> " + line if line.strip() else ">"
                     for line in text.replace("\r\n", "\n").split("\n"))


def releases_page(repo: str, owner: str, rows: list) -> str:
    out = [f"# {repo} — release notes", "",
           f"Every release published to <https://github.com/{owner}/{repo}/releases>, "
           "newest first. GitHub keeps these in its own database, not in the "
           "repository; this page is the copy that travels with a clone.", "",
           f"**{len(rows)} releases.**", ""]
    for r in rows:
        tag = r.get("tag_name") or "(untagged)"
        out += [f"## {tag} — {(r.get('name') or tag).strip()}", "",
                f"- Published: {day(r.get('published_at') or r.get('created_at'))}",
                f"- Commit: `{r.get('target_commitish', '')}`",
                f"- Assets: {len(r.get('assets') or [])}",
                f"- Page: <{r.get('html_url', '')}>",
                "", quote(body_of(r)), ""]
    return "\n".join(out) + "\n"


def pulls_page(repo: str, owner: str, rows: list, comments: list) -> str:
    by_issue: dict[str, list] = {}
    for c in comments:
        by_issue.setdefault(c.get("issue_url", "").rsplit("/", 1)[-1], []).append(c)
    merged = sum(1 for p in rows if p.get("merged_at"))
    out = [f"# {repo} — pull requests", "",
           f"Every pull request opened against <https://github.com/{owner}/{repo}>, "
           "newest first, with the body as written. The body is the argument for the "
           "change; git keeps the diff but not the argument.", "",
           f"**{len(rows)} pull requests, {merged} merged.**", ""]
    for p in sorted(rows, key=lambda r: r["number"], reverse=True):
        n = p["number"]
        state = "merged" if p.get("merged_at") else p.get("state", "?")
        out += [f"## #{n} — {(p.get('title') or '').strip()}", "",
                f"- {state} · opened {day(p.get('created_at'))}"
                + (f" · merged {day(p['merged_at'])}" if p.get("merged_at") else ""),
                f"- `{p['head']['ref']}` → `{p['base']['ref']}`",
                f"- Author: {p.get('user', {}).get('login', '')}",
                f"- Page: <{p.get('html_url', '')}>",
                "", quote(body_of(p)), ""]
        for c in sorted(by_issue.get(str(n), []), key=lambda c: c["created_at"]):
            out += [f"### Comment — {c['user']['login']}, {day(c['created_at'])}", "",
                    quote(body_of(c)), ""]
    return "\n".join(out) + "\n"


def reviews_page(repo: str, review_comments: list, reviews: dict,
                 issue_comments: list) -> str:
    out = [f"# {repo} — review threads", "",
           "Inline review comments and review summaries left on pull requests. "
           "These live only in GitHub's database.", ""]
    if not review_comments and not reviews:
        out += [f"**None.** All {len(issue_comments)} recorded comment(s) on this "
                "repository are conversation comments, kept with their pull request "
                "in [PULL-REQUESTS.md](PULL-REQUESTS.md)."
                if issue_comments else
                "**None.** No pull request on this repository carries an inline "
                "review comment or a review summary.", ""]
        return "\n".join(out) + "\n"
    for pr, rows in sorted(reviews.items(), key=lambda kv: -int(kv[0])):
        for r in rows:
            out += [f"## Review on #{pr} — {r['user']['login']}, {r['state']}, "
                    f"{day(r.get('submitted_at'))}", "", quote(body_of(r)), ""]
    for c in sorted(review_comments, key=lambda c: c["created_at"]):
        pr = c["pull_request_url"].rsplit("/", 1)[-1]
        out += [f"## #{pr} `{c.get('path', '')}`:"
                f"{c.get('line') or c.get('original_line', '')}"
                f" — {c['user']['login']}, {day(c['created_at'])}", "",
                quote(body_of(c)), ""]
    return "\n".join(out) + "\n"


SETTINGS = ("name", "full_name", "description", "homepage", "private", "fork",
            "default_branch", "visibility", "license", "topics", "language",
            "has_issues", "has_projects", "has_wiki", "has_pages", "has_discussions",
            "archived", "disabled", "allow_squash_merge", "allow_merge_commit",
            "allow_rebase_merge", "allow_auto_merge", "delete_branch_on_merge",
            "web_commit_signoff_required", "created_at")


def settings_page(meta: dict) -> str:
    keep = {k: meta.get(k) for k in SETTINGS if k in meta}
    if isinstance(keep.get("license"), dict):
        keep["license"] = keep["license"].get("spdx_id")
    return json.dumps(keep, indent=2, sort_keys=True) + "\n"


def rock() -> str:
    """The Matthew 7:24-25 passage that closes every README in the repo."""
    text = (HERE.parents[1] / "README.md").read_text(encoding="utf-8")
    return text[text.index("## Matthew 7:24"):].rstrip()


def index_page(repo: str, owner: str, counts: dict) -> str:
    return f"""# What GitHub holds that git does not

A clone carries the code, the commits and the tags. It does not carry the
writing wrapped around them: release notes, pull request bodies, review
threads and the repository's own settings all live in GitHub's database.
This folder is that writing, checked in, so a clone of
`{owner}/{repo}` is a complete copy of the app.

| Page | What it holds | Count |
| --- | --- | ---: |
| [RELEASE-NOTES.md](RELEASE-NOTES.md) | Every release, newest first, with its notes | {counts['releases']} releases |
| [PULL-REQUESTS.md](PULL-REQUESTS.md) | Every pull request body, and the comments on it | {counts['pulls']} pull requests |
| [REVIEW-THREADS.md](REVIEW-THREADS.md) | Inline review comments and review summaries | {counts['reviews']} |
| [repository.json](repository.json) | The repository's settings as GitHub stores them | — |

Harvested from the GitHub REST API on {counts['stamp']}. To refresh, run
`GITHUB_TOKEN=... python3 docs/github/harvest.py`; it rewrites every page in
this folder from what the API returns today.

Release **assets** are not here. Across the three products they run to
hundreds of gigabytes of built binaries, which belong on the release pages
and not in a git history. Each release's asset count is listed in
RELEASE-NOTES.md, and the files stay downloadable from the release page
linked there.

{rock()}
"""


def main() -> None:
    owner, repo = slug()
    base = f"/repos/{owner}/{repo}"
    releases = sorted(pages(f"{base}/releases"),
                      key=lambda r: r.get("published_at") or r.get("created_at") or "",
                      reverse=True)
    pulls = pages(f"{base}/pulls?state=all")
    review_comments = pages(f"{base}/pulls/comments")
    issue_comments = pages(f"{base}/issues/comments")
    meta = get(base)

    with ThreadPoolExecutor(max_workers=8) as pool:
        got = pool.map(lambda n: (n, pages(f"{base}/pulls/{n}/reviews")),
                       [p["number"] for p in pulls])
        reviews = {str(n): r for n, r in got if r}

    stamp = subprocess.run(["git", "-C", str(HERE), "log", "-1", "--format=%cs"],
                           capture_output=True, text=True).stdout.strip()
    counts = {"releases": len(releases), "pulls": len(pulls), "stamp": stamp,
              "reviews": (len(review_comments)
                          + sum(len(v) for v in reviews.values())) or "none"}
    write = {
        "README.md": index_page(repo, owner, counts),
        "RELEASE-NOTES.md": releases_page(repo, owner, releases),
        "PULL-REQUESTS.md": pulls_page(repo, owner, pulls, issue_comments),
        "REVIEW-THREADS.md": reviews_page(repo, review_comments, reviews,
                                          issue_comments),
        "repository.json": settings_page(meta),
    }
    for name, text in write.items():
        (HERE / name).write_text(text)
        print(f"{name:20s} {len(text) // 1024:>5d} KiB")


if __name__ == "__main__":
    main()
