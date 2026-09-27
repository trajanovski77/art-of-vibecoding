# Vault: the LLM-maintained wiki of this repository

This directory is a wiki about the repository, written and kept current by Claude sessions. A session
starts from `index.md` (its "Current state" is printed at session start by `.claude/hooks/session_start.py`),
asks the wiki where things are and why, and only then opens code. Humans can read it in Obsidian.

<!-- Starter schema (04-context). Replace <placeholders>, add page folders your project needs, and register each
     new folder in FOLDER_TYPES in scripts/vault_lint.py. Because this file is named CLAUDE.md, Claude loads it
     when it reads files under vault/, so the schema arrives exactly when a wiki operation starts. -->

## The three layers

- **Raw sources**: the repository itself: code, `docs/`, ADRs, configs. Wiki work never modifies them.
  Pages point into them by path and line; they never copy source.
- **The wiki**: `index.md`, `log.md` and `wiki/<folder>/<Title>.md`. Claude owns it.
- **This schema**: how pages look and how the three operations work. Change it with the user.

**When the wiki and the code disagree, the code wins.** Fix the page in the same session and note the fix
in `log.md`. If the disagreement is between two sources (for example an ADR and the code), record it on
[[Documentation contradictions]] instead of picking a winner silently.

## Layout

```
vault/
  CLAUDE.md        this schema
  index.md         "Current state" (<= 30 lines), then every page by folder with a one-line summary
  log.md           append-only; one entry per ingest, query filed back, or lint pass
  wiki/
    components/    one page per component (built or planned): services, modules, scripts, hooks, skills
    contracts/     one page per data contract or API between components
    decisions/     one page per ADR in docs/adr/
    concepts/      ideas that recur across documents (policies, invariants, naming, ...)
    playbooks/     step-by-step procedures for implementers
```

## Page conventions

- One topic per file. The file name is the page title: `wiki/components/Payment service.md` has
  `title: Payment service`. Titles are unique across folders.
- Frontmatter on every page, all six keys, flow lists only (the linter parses this subset):

  ```yaml
  ---
  title: Payment service
  type: component           # component | contract | decision | concept | playbook
  created: YYYY-MM-DD
  updated: YYYY-MM-DD       # the day of the last content change
  sources: [src/payments/service.py, docs/adr/0002-payments.md]   # repo paths the page was compiled from; must exist
  tags: [component, payments, planned]
  ---
  ```

- Link other pages with Obsidian wikilinks by title: `[[Payment service]]`, `[[Payment service|the service]]`.
  Every page links to at least one other page and is linked from at least one.
- Cite the repository as `<path>:<line>` or `<path>:<start>-<end>` in backticks, relative to the repo root,
  for example `vault/CLAUDE.md:1`. Cite a whole file as a plain path. Never paste code or long quotes; one
  short phrase in quotation marks is the limit. The linter checks every citation still resolves.
- Say what is built and what is planned. A planned component's page carries the tag `planned` and names the
  work package that owns it. When it lands, retag `built` and point at the real files.
- Keep pages short: what it is, where it lives, what it reads and writes, why it is this way, the traps,
  related pages. The "why" is the valuable part; the code already says "what".

### Page shapes

- **component**: Status (built or planned, owning package) / Where it lives / Reads and writes / Why it is
  this way / Traps / Related.
- **contract**: File or endpoint and producer / Consumers / Key fields and rules / Traps / Related.
- **decision**: Status and date / Decision in two sentences / What it forces / Alternatives rejected / Related.
- **concept**: the idea in two or three sentences / where it shows up (with citations) / Related.
- **playbook**: When to use / Steps (each names the file to touch and the check to run) / Related.

## Operations

### Ingest (after every completed step; the `step-done` skill runs this)

1. Find what changed: `git diff --stat <last ingested step tag>..HEAD` plus this step's uncommitted files.
   The last ingested step is named in the newest `ingest` entry of `log.md`; steps committed by other
   sessions since then are ingested too.
2. For each changed source, update the pages that cite it or that it now contradicts. Re-check every
   `<path>:<line>` that points into a changed file.
3. Create pages for new topics; add them to `index.md` under their folder and link them from at least one
   related page. Update "Current state" in `index.md` when the project's state changed.
4. Append to `log.md`: `## [YYYY-MM-DD] ingest | step-NN <title>`, then `- pages: <created/updated titles>`
   and `- notes: <contradictions found, anything left for later>`.
5. Run `python3 scripts/vault_lint.py`; it must exit 0 before the step is committed.

### Query

Read `index.md`, open the pages it points to, follow their citations into the code, and answer with page
links and `<path>:<line>` citations. If the answer took real synthesis (a comparison, a trace through several
components), file it back as a concept or playbook page and log it as `## [YYYY-MM-DD] query | <question>`.

### Lint

`python3 scripts/vault_lint.py` checks frontmatter, broken links, orphans, index coverage, the size of
"Current state" and that every `<path>:<line>` still exists. It cannot see drift (a line that still exists
but now says something else) or contradictions; for those, a lint pass also re-reads pages whose sources
changed since their `updated` date and records findings on [[Documentation contradictions]].
Log it as `## [YYYY-MM-DD] lint | <summary>`.

## Rules that hold during every wiki operation

- Write only inside `vault/`. Sources are fixed by their owners, not by the wiki.
- Keep secrets, personal data and customer data out of the wiki.
- `log.md` is append-only.
