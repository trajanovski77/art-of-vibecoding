# 01 · Setup: the repo before the first prompt

Goal: every future session starts oriented, works safely and leaves a trail. Several sessions may work in the
same repo, so conventions live in files, not in chat.

Copy into the root of your project:

```bash
cp -R 01-setup/.claude 01-setup/CLAUDE.md <your-repo>/
mkdir -p <your-repo>/docs/adr && cp 01-setup/docs/adr/0000-template.md <your-repo>/docs/adr/
cp -n 01-setup/docs/progress.md <your-repo>/docs/   # -n: keep yours if you already have one
```

If your repo already has a `CLAUDE.md` or `.claude/settings.json`, merge them by hand instead: `cp` overwrites.

Then add `05-skills/.claude/skills/step-done/` (the command CLAUDE.md refers to) and, if you want delegation,
`06-agents/.claude/agents/`. Claude Code reads skills, subagents and SessionStart hooks at session start, so
start a new session after copying.

## What each file is for

| File | What it does | Why it exists | Used in the build |
|---|---|---|---|
| `CLAUDE.md` | Project purpose, how we work, where things live, known pitfalls. Under 60 lines. | It is loaded into every session, so each line costs context on every call. Deeper docs are named by path and read on demand. | Written at step 01 ([prompts/01](../prompts/01-setup-brief.md)); the architect updated its status line and added the first pitfall at step 03. |
| `.claude/settings.json` | Permissions (allow, ask, deny) and the three hooks. | Routine read-only commands run without prompts; pushing asks; `.env` files and `secrets/` are unreadable, because transcripts get shared. | Step 01. The deny rules and hooks were confirmed live in a running session. |
| `.claude/rules/docs.md` | Plan, ADR and progress-log rules, `paths: ["docs/**"]`. | Loads only when Claude reads a file under `docs/`, so it costs nothing the rest of the time. | Step 01; it shaped ADR 0001 (step 02) and ADRs 0002 and 0003 (step 05). |
| `.claude/rules/scripts.md` | Script conventions, `paths: ["scripts/**"]`: standard library first, `--help`, fail loudly. | Same: loads only for scripts. | Step 01; followed by the benchmark sampler (step 04) and the wiki linter (step 09). |
| `.claude/hooks/session_start.py` | SessionStart: prints the wiki's "Current state", the last 15 lines of `docs/progress.md` and `git log --oneline -5`. | Orientation without being asked, on startup, resume, `/clear` and compaction. | Step 01; the wiki's "Current state" was added at step 09. After a `/clear` before the P0 review, the architect went from about 577k to 125k tokens per call and still found six gaps. |
| `.claude/hooks/guard_bash.py` | PreToolUse on `Bash\|Monitor`: exit 2 blocks commands that print or commit secrets, force-push, delete outside the repo or its scratchpad, or delete Docker volumes. | Permission rules match command text; this also catches `/bin/rm`, `git -C . push -f`, `bash -c '...'`, heredocs and `git add … && git commit`. | Step 01: an independent Opus review found the first version let 8 of 9 bypass tricks through (52 findings in all). Step 07 fixed heredocs and Docker volumes; the step 08 review probed the gaps it still lists. |
| `.claude/hooks/format_edited.py` | PostToolUse on `Edit\|Write`: runs the formatter for the file's language if one is installed. | A hook runs every time; an instruction in CLAUDE.md is a request that can be forgotten. Small diffs keep reviews honest. | Step 01 (stack-agnostic); YAML and JSON added at step 07. |
| `docs/adr/0000-template.md` | Status, context, decision, consequences, alternatives with links. | "An alternative without a link is an opinion." Reading the template also loads the docs rule. | ADR 0001 (adopt an existing tool instead of building one) at step 02; ADRs 0002 and 0003 at step 05. |
| `docs/progress.md` | Append-only step log, one entry of at most 12 lines per step. | The SessionStart hook prints its tail, so a fresh session knows what happened and what is next. | Every step since step 01, written by `/step-done`. |

## Adapt three things

1. **`CLAUDE.md`**: replace every `<placeholder>`. Keep "How we work" as it is unless a line is wrong for you.
2. **`permissions.allow`** in `.claude/settings.json`: replace `Bash(pytest *)` and `Bash(python3 scripts/*)`
   with the commands your sessions run constantly (for example `Bash(npm test *)`). Settings files are strict
   JSON, so no comments.
3. **`paths:`** in `.claude/rules/*.md`: point them at your folders, and change the language line in
   `scripts.md` if your scripts are not Python.

The hooks need no changes. They need `python3` (3.9 or newer) on the PATH of the process that runs Claude Code.
Set `PROTECT_DOCKER_VOLUMES = False` in `guard_bash.py` if you do not use Docker.

Add these lines to your `.gitignore`, so secrets and personal files stay local:

```gitignore
.env
.env.*
!.env.example
secrets/
.claude/settings.local.json
CLAUDE.local.md
.claude/worktrees/
```

## Check the hooks yourself

Each hook reads one JSON object on stdin. Run these from your repo root after copying:

```bash
export CLAUDE_PROJECT_DIR="$PWD"
echo '{"tool_name":"Bash","cwd":"'"$PWD"'","tool_input":{"command":"cat .env"}}' \
  | python3 .claude/hooks/guard_bash.py; echo "exit $?"      # exit 2, reason on stderr
echo '{"tool_name":"Bash","cwd":"'"$PWD"'","tool_input":{"command":"git status"}}' \
  | python3 .claude/hooks/guard_bash.py; echo "exit $?"      # exit 0
echo '{"source":"startup","cwd":"'"$PWD"'"}' | python3 .claude/hooks/session_start.py   # prints orientation
echo '{"tool_name":"Write","cwd":"'"$PWD"'","tool_input":{"file_path":"'"$PWD"'/x.py"}}' \
  | python3 .claude/hooks/format_edited.py; echo "exit $?"   # exit 0; x.py formatted if ruff or black is installed
```

The guard also blocks, among others: `echo $OPENAI_API_KEY`, `printenv`, `git push --force`, `git -C . push -f`,
`rm -rf /tmp/elsewhere`, `bash -c 'rm -rf ~/x'`, `docker compose down -v`, `git add .env`, and a `git commit`
whose staged diff contains something shaped like a GitHub token. It allows `cat .env.example`, `rm -rf build`
inside the repo, deletes in the session's scratchpad, `docker compose down`, and a heredoc that writes a note
mentioning `.env`. A hook bug exits 1: the command runs, and Claude Code shows a hook-error notice.

## Known limits

- **Rules load when Claude reads a matching file**, not when it creates one. A session writing a brand-new ADR
  gets `docs.md` only if it reads the template first, which is why CLAUDE.md tells it to.
- **The guard reads command text; it is not a security boundary.** It cannot see `grep -r` over a folder holding
  `.env`, a script that opens files itself, `xargs`, `find -exec sh -c`, globs like `.e*`, or secrets in a variable
  whose name does not look like one. `docker compose exec <c> env`, `docker compose config` and `docker inspect`
  can print values from `.env`. For OS-level enforcement use the [sandbox](https://code.claude.com/docs/en/sandboxing).
- **Project `allow` rules apply only after you accept the workspace-trust dialog**; `deny` and `ask` rules always
  apply, because they only restrict ([permissions](https://code.claude.com/docs/en/permissions#project-allow-rules-and-workspace-trust)).
- **`@imports` in CLAUDE.md do not save context**: imported files load at launch. Name deeper docs by path instead.

## The docs each choice follows

- CLAUDE.md size, HTML comments, `@imports`, rules with `paths:`: [memory](https://code.claude.com/docs/en/memory)
- `allow`/`ask`/`deny`, `Read(.env)`, the `!` carve-out for `.env.example`, trailing ` *`: [permissions](https://code.claude.com/docs/en/permissions), [settings](https://code.claude.com/docs/en/settings)
- Event names, matchers (`Bash|Monitor`, `Edit|Write`), exec form (`command` + `args`), `${CLAUDE_PROJECT_DIR}`, exit codes, stdin fields (`cwd`, `tool_input`, `scratchpad_dir`), the 10,000-character output cap: [hooks](https://code.claude.com/docs/en/hooks)
- Monitor runs commands under the same rules as Bash: [tools reference](https://code.claude.com/docs/en/tools-reference)
