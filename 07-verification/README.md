# 07 · Verification and rescue

"It compiles" is not "it works". Three layers of checking caught different mistakes in the build: running
things, a reviewer in a fresh context, and a person looking at the screens.

## What is in this folder

| File | What it is | Why it exists | Used in the build |
|---|---|---|---|
| `review-prompt.md` | The review prompt: judge the work, not the report; re-run the done-when; look at the screens as a user; verdict ACCEPT, FIX or REDO; a FIX writes the builder's next prompt. | The session that built something is the worst judge of it, and a builder's "all green" is a claim until someone else reproduces it. | Generalized from [prompts/07](../prompts/07-orchestrator-review.md) (after every builder step) and [prompts/12](../prompts/12-review-in-a-fresh-session.md) (the P0 review, in a fresh session). |
| `rescue-prompt.md` | Three short prompts: when a session loops, after an interruption, and before blaming anyone for unexpected changes. | Each sends the session back to evidence before it changes more code. | The interruption prompt is [prompts/09](../prompts/09-resume-after-interruption.md), sent to both sessions after a usage limit. |

## 1. Done-when is a command

Every step and work package ends in a command that exits 0 only when the thing works, and prints a line you can
look for (`SMOKE OK`). Write it before the work starts ([02-plan](../02-plan/work-package.md)), have the builder
show its output, and run it again yourself. Checks can be wrong too: in the build, one feature's check was
broken (`git check-ignore -q` accepts a single path and was given several, so it exited 128), and only running
it showed that.

Exercise the real thing once. A data contract written from the docs said one export shape; exporting a single
real annotation from the running tool showed another. The builder caught it, and the architect updated the
contract.

## 2. Independent review in a fresh context

- **Fresh context**: a `reviewer` subagent ([06-agents](../06-agents/README.md)) or the architect after `/clear`.
  It never saw the reasoning it is judging, so it cannot be talked into it.
- **Judge the work, not the report**: read the diff since the last tag, run the done-when, count anything not
  reproduced as unverified.
- **Say why the review exists**: "a mid-tier model built this; it is usually right and occasionally
  confidently wrong". Naming the failure mode points the reviewer at it.
- **Find everything, filter later**: ask for every issue with severity and confidence. "Only high severity" is
  followed literally and costs recall.
- **Review what was deferred, too**: when a builder lists known limits, run each one. In the build, the reviewer
  fed the guard hook the deferred cases and found that `docker compose exec <c> env` would print the server's
  secrets into a transcript; closing it became a precondition for the ops package.

In the first work package, the builder's own Opus reviewer, reading the diff against the next package, caught
a hand-written proxy route that would collide with the one another package generates and stop the proxy for
every project.

## 3. Look at the screens as a user would

Every command in that package passed, and `SMOKE OK` printed. The architect's review prompt said: look at the
two screenshots the way a volunteer would. The first page a volunteer would see, the login page, was the tool's
stock look: English, the default colours, no logo, an open Register tab. No test checks for that. Ask for
screenshots in the done-when ([03-prompting/annotated-example.md](../03-prompting/annotated-example.md)), and
tell the reviewer who the user is.

## 4. Rescue

- **When a session loops**: stop it, and ask for certain facts with evidence, assumptions, and the smallest
  experiment that separates them ([rescue-prompt.md](rescue-prompt.md)).
- **After an interruption**: orient from the repository, not from memory: `git status`, the progress log, the
  files the step should have produced ([prompts/09](../prompts/09-resume-after-interruption.md)).
- **Trace before you blame**: in the build, a research subagent ran `cd /tmp/x && mkdir -p /tmp/x`; the `cd`
  failed, so its download loop wrote nine files into the repo root. The orchestrator then said "another session"
  did it. The subagent's own transcript showed otherwise. The fix went into CLAUDE.md as a known pitfall
  (`mkdir -p` before `cd`; subagents download into the scratchpad).
