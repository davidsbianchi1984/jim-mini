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


# GitHub renders a markdown file as a formatted page up to 512 KiB and falls
# back to plain text above it. A history this long passes that on its own, so
# a page that would go over is written as numbered parts under an index.
RENDER_CAP = 400 * 1024


def paginate(blocks: list[str], cap: int = RENDER_CAP) -> list[list[str]]:
    """Pack rendered blocks into parts, none of them over the cap.

    The count is settled first and the blocks spread evenly across it, so a
    history that needs two parts gets two halves rather than a full part and
    a stub.
    """
    sizes = [len(b.encode()) for b in blocks]
    total = sum(sizes)
    if total <= cap:
        return [list(blocks)]
    count = -(-total // cap)
    target = total / count
    parts: list[list[str]] = [[]]
    size = 0
    for block, n in zip(blocks, sizes):
        if parts[-1] and len(parts) < count and size + n / 2 > target:
            parts.append([])
            size = 0
        parts[-1].append(block)
        size += n
    return parts


def write_pages(here, stem: str, head: str, blocks: list[str],
                label) -> list[str]:
    """Write `stem`.md, or an index and `stem`-NN.md parts when it is long.

    Returns the filenames written, index first.
    """
    parts = paginate(blocks)
    if len(parts) == 1:
        (here / f"{stem}.md").write_text(head + "".join(parts[0]))
        return [f"{stem}.md"]

    names = [f"{stem}-{i + 1:02d}.md" for i in range(len(parts))]
    rows = []
    for name, part in zip(names, parts):
        first, last = label(part[0]), label(part[-1])
        span = first if first == last else f"{first} to {last}"
        (here / name).write_text(
            f"{head}This is one part of a page GitHub is too long to render "
            f"whole — see [{stem}.md]({stem}.md) for the rest.\n\n"
            f"**{span}.**\n\n" + "".join(part))
        rows.append(f"| [{name}]({name}) | {span} | {len(part)} |")
    (here / f"{stem}.md").write_text(
        head
        + "GitHub renders a markdown file as a formatted page up to 512 KiB "
          "and shows plain text above it. This history passes that, so it is "
          "written as parts, newest first — every entry is in exactly one of "
          "them.\n\n"
        + "| Part | Covers | Entries |\n| --- | --- | ---: |\n"
        + "\n".join(rows) + "\n")
    return [f"{stem}.md"] + names


def releases_pages(repo: str, owner: str, rows: list) -> tuple[str, list]:
    head = "\n".join([
        f"# {repo} — release notes", "",
        f"Every release published to <https://github.com/{owner}/{repo}/releases>, "
        "newest first. GitHub keeps these in its own database, not in the "
        "repository; this page is the copy that travels with a clone.", "",
        f"**{len(rows)} releases.**", "", ""])
    blocks = []
    for r in rows:
        tag = r.get("tag_name") or "(untagged)"
        blocks.append("\n".join([
            f"## {tag} — {(r.get('name') or tag).strip()}", "",
            f"- Published: {day(r.get('published_at') or r.get('created_at'))}",
            f"- Commit: `{r.get('target_commitish', '')}`",
            f"- Assets: {len(r.get('assets') or [])}",
            f"- Page: <{r.get('html_url', '')}>",
            "", quote(body_of(r)), "", ""]))
    return head, blocks


def pulls_pages(repo: str, owner: str, rows: list,
                comments: list) -> tuple[str, list]:
    by_issue: dict[str, list] = {}
    for c in comments:
        by_issue.setdefault(c.get("issue_url", "").rsplit("/", 1)[-1], []).append(c)
    merged = sum(1 for p in rows if p.get("merged_at"))
    head = "\n".join([
        f"# {repo} — pull requests", "",
        f"Every pull request opened against <https://github.com/{owner}/{repo}>, "
        "newest first, with the body as written. The body is the argument for "
        "the change; git keeps the diff but not the argument.", "",
        f"**{len(rows)} pull requests, {merged} merged.**", "", ""])
    blocks = []
    for p in sorted(rows, key=lambda r: r["number"], reverse=True):
        n = p["number"]
        state = "merged" if p.get("merged_at") else p.get("state", "?")
        lines = [f"## #{n} — {(p.get('title') or '').strip()}", "",
                 f"- {state} · opened {day(p.get('created_at'))}"
                 + (f" · merged {day(p['merged_at'])}" if p.get("merged_at") else ""),
                 f"- `{p['head']['ref']}` → `{p['base']['ref']}`",
                 f"- Author: {p.get('user', {}).get('login', '')}",
                 f"- Page: <{p.get('html_url', '')}>",
                 "", quote(body_of(p)), ""]
        for c in sorted(by_issue.get(str(n), []), key=lambda c: c["created_at"]):
            lines += [f"### Comment — {c['user']['login']}, {day(c['created_at'])}",
                      "", quote(body_of(c)), ""]
        blocks.append("\n".join(lines + [""]))
    return head, blocks


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
    def note(files: list[str]) -> str:
        n = len(files) - 1
        return f", in {n} parts" if n > 1 else ""

    split = ""
    if len(counts["rel_files"]) > 1 or len(counts["pr_files"]) > 1:
        long = " and ".join(
            name for name, files in (("RELEASE-NOTES.md", counts["rel_files"]),
                                     ("PULL-REQUESTS.md", counts["pr_files"]))
            if len(files) > 1)
        split = ("\nGitHub renders a markdown file as a formatted page up to "
                 f"512 KiB and shows plain text above it. {long} pass"
                 f"{'' if ' and ' in long else 'es'} that, so it is an index "
                 "over numbered parts; every entry is in exactly one part, "
                 "and a clone holds all of them either way.\n")
    return f"""# What GitHub holds that git does not

A clone carries the code, the commits and the tags. It does not carry the
writing wrapped around them: release notes, pull request bodies, review
threads and the repository's own settings all live in GitHub's database.
This folder is that writing, checked in, so a clone of
`{owner}/{repo}` is a complete copy of the app.

| Page | What it holds | Count |
| --- | --- | ---: |
| [RELEASE-NOTES.md](RELEASE-NOTES.md) | Every release, newest first, with its notes{note(counts['rel_files'])} | {counts['releases']} releases |
| [PULL-REQUESTS.md](PULL-REQUESTS.md) | Every pull request body, and the comments on it{note(counts['pr_files'])} | {counts['pulls']} pull requests |
| [REVIEW-THREADS.md](REVIEW-THREADS.md) | Inline review comments and review summaries | {counts['reviews']} |
| [repository.json](repository.json) | The repository's settings as GitHub stores them | — |
{split}
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

    for stale in HERE.glob("RELEASE-NOTES-*.md"):
        stale.unlink()
    for stale in HERE.glob("PULL-REQUESTS-*.md"):
        stale.unlink()

    head, blocks = releases_pages(repo, owner, releases)
    rel_files = write_pages(HERE, "RELEASE-NOTES", head, blocks,
                            lambda b: b.split(" — ", 1)[0][3:])
    head, blocks = pulls_pages(repo, owner, pulls, issue_comments)
    pr_files = write_pages(HERE, "PULL-REQUESTS", head, blocks,
                           lambda b: b.split(" — ", 1)[0][3:])

    (HERE / "REVIEW-THREADS.md").write_text(
        reviews_page(repo, review_comments, reviews, issue_comments))
    (HERE / "repository.json").write_text(settings_page(meta))

    stamp = subprocess.run(["git", "-C", str(HERE), "log", "-1", "--format=%cs"],
                           capture_output=True, text=True).stdout.strip()
    (HERE / "README.md").write_text(index_page(repo, owner, {
        "releases": len(releases), "pulls": len(pulls), "stamp": stamp,
        "rel_files": rel_files, "pr_files": pr_files,
        "reviews": (len(review_comments)
                    + sum(len(v) for v in reviews.values())) or "none"}))

    for name in sorted(p.name for p in HERE.iterdir() if p.name != "harvest.py"):
        print(f"{name:24s} {(HERE / name).stat().st_size // 1024:>5d} KiB")


if __name__ == "__main__":
    main()
