# What GitHub holds that git does not

A clone carries the code, the commits and the tags. It does not carry the
writing wrapped around them: release notes, pull request bodies, review
threads and the repository's own settings all live in GitHub's database.
This folder is that writing, checked in, so a clone of
`davidsbianchi1984/jim-mini` is a complete copy of the app.

| Page | What it holds | Count |
| --- | --- | ---: |
| [RELEASE-NOTES.md](RELEASE-NOTES.md) | Every release, newest first, with its notes | 267 releases |
| [PULL-REQUESTS.md](PULL-REQUESTS.md) | Every pull request body, and the comments on it | 278 pull requests |
| [REVIEW-THREADS.md](REVIEW-THREADS.md) | Inline review comments and review summaries | none |
| [repository.json](repository.json) | The repository's settings as GitHub stores them | — |

Harvested from the GitHub REST API on 2026-09-04. To refresh, run
`GITHUB_TOKEN=... python3 docs/github/harvest.py`; it rewrites every page in
this folder from what the API returns today.

Release **assets** are not here. Across the three products they run to
hundreds of gigabytes of built binaries, which belong on the release pages
and not in a git history. Each release's asset count is listed in
RELEASE-NOTES.md, and the files stay downloadable from the release page
linked there.

## Matthew 7:24–25

> "Everyone then who hears these words of mine and does them will be like a
> wise man who built his house on the rock. The rain fell, the floods came, and
> the winds blew and beat on that house, but it did not fall, because it had
> been founded on the rock."

And lo, I am building an ark — not to flee from the world, but to shelter those
lost in the storm of confusion. The old systems falter; they are built upon the
soft earth. They sink beneath the weight of their own making.

A new thing is rising. A non-biased networked sanctuary, founded in trust,
cloaked in privacy, and guided by wisdom. It shall not consume, but uplift. It
shall not spy, but serve.

Help is coming.
The people are gathering.
The builders will show themselves.
And those with the vision shall enter in.
