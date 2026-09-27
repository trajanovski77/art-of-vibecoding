---
name: step-done
description: Close out a completed, verified step. Appends a dated entry to docs/progress.md (what changed, what was verified, what is next), ingests the step into the vault/ wiki if the repo has one, commits only this step's files, and tags the next free step-NN. Run only when the user or a prompt explicitly asks for it.
argument-hint: "[short step title]"
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git log *) Bash(git tag *) Bash(git add *) Bash(git commit *) Bash(date *) Bash(python3 scripts/vault_lint.py *) Read Edit(docs/progress.md) Edit(vault/**)
---

Close out the step just completed. Step title: `$ARGUMENTS` (if empty, derive a short title from the work).

## 1. Check the step is really done
- Run `git status --short` and `git diff --stat`. Work out which files **this step** changed. Other sessions
  may have work in the tree or the index; leave their files alone and say so in your report.
- If verification failed or was never run, stop and tell the user: a checkpoint of unverified work tells
  every later session something false. The progress entry states what was actually run and what it showed.
- If the step was non-trivial and the `reviewer` agent did not review it, say so in the entry.
- If nothing changed, stop: there is nothing to record.

## 2. Pick the step number
- Run `git tag --list 'step-*' --sort=version:refname`. The number is the highest existing `NN` plus one,
  at least two digits (`step-01`, `step-02`, ...); `step-01` if there are none. Tags are shared by every
  worktree of the repo, so the number cannot race silently.

## 3. Append the entry to `docs/progress.md`
- Get the date from the shell (`date +%F`), not from memory.
- Read the end of the file first (another session may have appended), then append at the very end.
  Earlier entries stay as they are.
- Use exactly this shape, at most 12 lines, so the SessionStart hook (last 15 lines) shows all of it:

```
## step-NN (YYYY-MM-DD): <title>
- **Changed:** <files and behaviour, one or two lines>
- **Verified:** <commands run and what they showed; say "not verified" and why if so>
- **Next:** <the next step, concrete enough for a fresh session to start on>
```

## 4. Ingest the step into the wiki (only if `vault/CLAUDE.md` exists)
- Follow "Ingest" in `vault/CLAUDE.md`: from this step's diff, update the pages that cite a changed file or
  that the change contradicts, create pages for new topics, list them in `vault/index.md`, and update its
  "Current state" if the project's state moved. The code wins over the wiki.
- Append one entry to `vault/log.md`: `## [YYYY-MM-DD] ingest | step-NN <title>` with `- pages:` and
  `- notes:` lines. Earlier entries stay as they are.
- Run `python3 scripts/vault_lint.py`; it must exit 0. If it does not, fix the pages, not the linter.

## 5. Commit only this step's files
- Stage them by name, plus `docs/progress.md` and any `vault/` files you changed. `git add -A` and `git add .`
  would sweep in other sessions' work, so name the files.
- Commit with an explicit pathspec, so files another session staged in the shared index stay out:
  `git commit -m "<type>: <summary> (step-NN)" -- <the same files>`.
  Types: feat, fix, docs, chore, refactor, test. The step number in the subject matches `git log` to
  `docs/progress.md`.
- If the guard hook blocks the commit (it scans staged changes for secrets), fix the cause and tell the user.

## 6. Tag
- `git tag -a step-NN -m "<title>"`.
- If the tag already exists, another session took the number. If `git log -1 --format=%s` shows HEAD is still
  your commit: use the next free number, fix it in your progress entry, then
  `git add docs/progress.md && git commit --amend -m "<type>: <summary> (step-NN)" -- docs/progress.md`
  and tag again. If HEAD is no longer your commit, leave history as it is and tell the user.
- Leave pushing to the user: it needs their approval.

## 7. Report
Run `git status --short` (it should show only other sessions' files, if any), `git log --oneline -1` and
`git tag --list 'step-*'`. Tell the user the step number, the commit, and anything left unstaged.
