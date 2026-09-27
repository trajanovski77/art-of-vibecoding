# 04 · Context and tokens: an LLM wiki of your codebase

Context is a budget: every call re-reads the whole conversation. A session that starts by re-exploring the
repo spends that budget on facts the last session already found. The fix used in the build is a wiki the
model writes and keeps current, following Andrej Karpathy's LLM Wiki idea file:
<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>. Read it there; it is written to be pasted
to an agent, and [prompts/10](../prompts/10-map-the-codebase-llm-wiki.md) shows how the build did exactly that
and then mapped the idea onto a codebase.

Three layers: **raw sources** (your code, never modified by wiki work), **the wiki** (`vault/`, pages the model
writes), **the schema** (`vault/CLAUDE.md`, which makes the model a disciplined maintainer).

Copy into your project root:

```bash
cp -R 04-context/vault <your-repo>/
mkdir -p <your-repo>/scripts && cp 04-context/scripts/vault_lint.py <your-repo>/scripts/
python3 scripts/vault_lint.py      # from your repo root: prints OK and exits 0
```

Then ask a session to do the first ingest, for example: "Read `vault/CLAUDE.md`, ingest everything committed so
far, write the Current state, and run `python3 scripts/vault_lint.py` until it exits 0." The SessionStart hook in
[01-setup](../01-setup/README.md) prints "Current state" into every new session; the `step-done` skill in
[05-skills](../05-skills/README.md) ingests each step as it closes.

## What each file is for

| File | What it does | Why it exists | Used in the build |
|---|---|---|---|
| `vault/CLAUDE.md` | The schema: layers, folders, page frontmatter and shapes, and the ingest, query and lint operations. | Without a schema, a model writes a different wiki every session. Named `CLAUDE.md` so Claude loads it when it reads files under `vault/`, exactly when wiki work starts. | Written at step 09 ([prompts/10](../prompts/10-map-the-codebase-llm-wiki.md)). |
| `vault/index.md` | "Current state" (at most 30 lines), then every page by folder with a one-line summary. | Only "Current state" rides in every session; pages load on demand. | Step 09; the architect's fresh review session (step 12) started from it. |
| `vault/log.md` | Append-only record of ingests, queries filed back, and lint passes. | The newest ingest entry tells the next ingest where to start. | Every step since step 09. |
| `vault/wiki/concepts/Documentation contradictions.md` | Where two sources disagree, with both citations; Open and Resolved. | The wiki records disagreements instead of silently picking a winner; owners fix the sources. | The first lint pass found 8 contradictions in fresh design docs; all 8 were fixed at their sources in step 10. |
| `vault/wiki/playbooks/Add a wiki page.md` | A five-step playbook, also an example of the page format. | Shows the frontmatter, citations and links the linter expects. | New for the starter; the build had playbooks of the same shape. |
| `scripts/vault_lint.py` | Checks frontmatter, broken links, orphans, index coverage, "Current state" size, and that every `` `path:line` `` citation still resolves. Exit 1 on any error. | A wiki the model maintains drifts unless something fails when it does. | Step 09: 101 pages and 448 code citations, lint clean before the step was committed. |

Adapt: replace the `<placeholders>` in `index.md`, change the page folders in `vault/CLAUDE.md` and
`FOLDER_TYPES` in `vault_lint.py` together (the build also had `layouts/` and `benchmarks/`), and keep the rule
that the code wins.

## What it bought, in numbers

In the build, the architect's long session re-read about 577k tokens on every call by its last review
there. Before reviewing the first work package it was cleared with `/clear`. The fresh session started from
about 20 lines of Current state, the progress tail and five commits: about 70k tokens on its first call and
about 125k per call during the review. It opened the plan and contracts only when it needed them, and still
found six gaps, including one that the builder and the builder's own reviewer had both missed
([prompts/12](../prompts/12-review-in-a-fresh-session.md)).

## Measure your own sessions: `capture/ledger.py`

[`../capture/ledger.py`](../capture/ledger.py) adds up `message.usage` from Claude Code's session transcripts,
per session, role (main or subagent) and model. Run it from the root of this starter repo:

```bash
ls ~/.claude/projects/                               # one folder per project, named after its path
python3 capture/ledger.py ~/.claude/projects/<your-project-folder>
python3 capture/ledger.py ~/.claude/projects/<your-project-folder> --names 1a2b3c4d=Builder 5e6f7a8b=Architect
python3 capture/ledger.py ~/.claude/projects/<your-project-folder> --json
```

Always pass the folder: the script has no default. Each row prints
`calls`, `out` (tokens the model wrote), `cache_read` (context re-read from cache) and `cache_write`.
`cache_read / calls` is roughly the context each call carried; when it keeps climbing, write down the state,
`/clear`, and let the SessionStart hook re-orient the next session. `--names` takes the first 8 characters
of a transcript file name. Transcripts can contain everything a session saw, so keep them and the ledger's
output out of public repos.

## Habits that kept the sessions sharp

- **Subagents isolate context**: a 40-file search comes back as one paragraph ([06-agents](../06-agents/README.md)).
- **Rules load only when needed**: `.claude/rules/*.md` with `paths:` ([01-setup](../01-setup/README.md)).
- **State lives in files**: `docs/progress.md`, `features.json`, git tags and the wiki survive `/clear`,
  compaction and usage limits; chat does not ([prompts/09](../prompts/09-resume-after-interruption.md)).
- **Hand off, then clear**: when a session gets long, have it write down where it is, `/clear`, and start the
  next step fresh.
