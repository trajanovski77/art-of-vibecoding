# <Project name>

<!-- Starter template (01-setup). Claude loads this file into every session, so every line costs context
     on every call: keep it short and point to deeper docs by path. Block-level HTML comments like this one
     are stripped before Claude sees the file, so they cost nothing. Replace every <placeholder>. -->

<What this is, in two sentences: who uses it, and what it does for them.>
Goal: <the outcome that tells you it worked>.

Status: <one line, e.g. "stack not chosen yet" or "ADR 0001 accepted: <stack>" with the ADR path>.
Read first: `docs/<BRIEF>.md` (problem, users, constraints), then the newest ADR in `docs/adr/`.

## How we work
- Plan before code: write the plan in `docs/plans/` and get it agreed before writing product code.
  Decisions go in `docs/adr/`; start from `docs/adr/0000-template.md` (reading it also loads the docs rule).
- One step, one commit. When a step is complete and verified, the user (or a prompt) runs `/step-done`:
  it logs the step in `docs/progress.md`, commits and tags `step-NN`. Run it only when asked.
- Several sessions may work here in parallel, so conventions live in files, not in chat. The SessionStart
  hook shows you the tail of `docs/progress.md` and the last commits; read the full log before a new step.
- Stage the files you changed by name. Another session may have work in the tree, and `git add -A` or
  `git add .` would sweep it into your commit.
- Keep secrets out of transcripts, because transcripts get shared: leave `.env` files and `secrets/` unread,
  and put variable names (never values) in `.env.example`.
- Ask before `git push`: pushing is outward-facing. Force-pushing rewrites history others build on.
- Hooks in `.claude/hooks/` block secret leaks, force-push and deletes outside the repo. If one blocks you,
  tell the user instead of working around it; the block is usually right.
- Done means a check you ran and saw pass. Show the command and its output.
- Prefer accuracy over tokens. Delegate when it helps: `reviewer` (opus; independent review of a plan or
  diff before `/step-done`), `explorer` (sonnet; codebase questions, under 300 words), `researcher`
  (sonnet; web research, every claim cited).

## Where things live
- `<src/>`: <what lives here>. `<tests/>`: <how to run them, e.g. `pytest -q`>.
- `docs/plans/`: plans, one file per topic. `docs/adr/`: decisions. `docs/progress.md`: append-only step log.
- `scripts/`: helper scripts, each runnable with `--help`.
- `.claude/`: settings, hooks (`hooks/`), path-scoped rules (`rules/`), subagents (`agents/`), skills (`skills/`).
- `vault/` (optional): the LLM-maintained wiki of this repo (schema `vault/CLAUDE.md`). Ask it where things
  are and why before opening code; `python3 scripts/vault_lint.py` checks it.

## Known pitfalls
One line per mistake: the date, what went wrong, what to do instead. Add a line the second time you
correct the same thing.
- <YYYY-MM-DD>: <what went wrong>. <what to do instead>.

<!-- A real line from the build this template comes from:
- 2026-09-24: a research subagent's `cd /tmp/x && mkdir -p /tmp/x` failed because the folder did not exist
  yet, and its download loop wrote nine files into the repo root. Subagents download into the scratchpad
  or research/, and always `mkdir -p` before `cd`. -->
