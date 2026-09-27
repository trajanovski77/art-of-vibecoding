<context>
This folder is the ground zero of Vezilka Goldsets: a web app where non-technical Macedonian
volunteers turn machine-translated English benchmarks into human-validated Macedonian gold sets,
so Macedonian can be added to the EuroEval leaderboard. Right now the repo holds one file:
data/benchmark-catalogue.xlsx (83 benchmarks). No stack has been chosen and no code exists.

Before anyone writes a line of product code, I want the repo set up so that every future Claude
session starts oriented, works safely, and leaves a trail. Several sessions will work here in
parallel over the next two days, so conventions have to live in files, not in chat.
</context>

<investigate_before_answering>
Claude Code's configuration formats change often and your training data may be out of date.
Before writing any config, fetch the current official docs and follow them exactly:
- https://code.claude.com/docs/en/memory (CLAUDE.md, @imports, .claude/rules with `paths:`)
- https://code.claude.com/docs/en/settings and /permissions
- https://code.claude.com/docs/en/hooks (event names, stdin JSON input, exit-code semantics)
- https://code.claude.com/docs/en/sub-agents and /skills (frontmatter fields)
Fetch these in parallel. If a doc contradicts something below, the doc wins; tell me where.
</investigate_before_answering>

<deliverables>
1. CLAUDE.md, under 80 lines. It is loaded into every session, so treat each line as a cost:
   project purpose in two sentences, how we work (plan in docs/ before code; one step, one
   commit), where things live, and an empty "Known pitfalls" section we will grow over time.
   Point to deeper docs with @imports instead of copying them in.
2. .claude/rules/ with path-scoped rules that load only when relevant: docs.md for docs/**
   (ADR format: context, decision, consequences, alternatives with links) and scripts.md for
   scripts/** (standard-library Python first, every script runnable with --help).
3. .claude/settings.json:
   - allow the read-only and routine commands a session runs constantly (git status/diff/log,
     ls, python3 scripts, pytest), so nobody drowns in approval prompts;
   - deny reading .env files and anything under secrets/, because transcripts get shared;
   - ask before git push, since pushing is outward-facing.
4. Hooks, each a small script in .claude/hooks/ that reads its JSON from stdin:
   - SessionStart: print the last 15 lines of docs/progress.md and `git log --oneline -5`, so
     every new session orients itself without being asked;
   - PreToolUse on Bash: block (exit 2, reason on stderr) commands that would print or commit
     secrets, force-push, or delete outside the repo;
   - PostToolUse on Edit|Write: run a formatter for the edited file's language when one is
     installed, and do nothing otherwise (the stack isn't chosen yet).
5. .claude/agents/: `reviewer` (read-only tools, model opus, reviews a diff or plan in a fresh
   context and reports every issue with severity and confidence), `explorer` (read-only, model
   sonnet, returns a summary under 300 words), `researcher` (web tools, model sonnet, every claim
   carries a URL). Nothing here runs on the smallest model: in this project, accuracy is worth
   more than the tokens it would save.
6. .claude/skills/checkpoint/SKILL.md, run as /checkpoint at the end of each completed step, by
   me or by you when a prompt asks for it: append a dated entry to docs/progress.md (what
   changed, what was verified, what is next), commit, and tag step-NN with the next free number.
7. docs/progress.md, docs/adr/, .gitignore, .env.example, and docs/setup-notes.md explaining
   every setting above in one line each, with its doc link.
</deliverables>

<constraints>
- Keep everything stack-agnostic; we choose the stack after research.
- Prefer the smallest configuration that does the job; no speculative settings.
</constraints>

<done_when>
- Every JSON file parses (show the command and its output).
- Each hook script is exercised with a sample stdin payload: the blocked cases exit 2 with a
  clear reason and a harmless command exits 0 (show the runs).
- `git status` is clean after a commit "chore: project setup" tagged step-01.
</done_when>

<report>
A table of files created and why each exists, the doc URL each config choice follows, and
anything you could not verify.
</report>
