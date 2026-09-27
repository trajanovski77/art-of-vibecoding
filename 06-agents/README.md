# 06 · Agents and orchestration

Route by the job, not by habit, and brief every agent like a new colleague: what exists, why the task
matters, what done looks like, and exactly what to hand back.

Copy the subagents into your project (replace the two placeholders in `reviewer.md`):

```bash
mkdir -p <your-repo>/.claude/agents && cp 06-agents/.claude/agents/*.md <your-repo>/.claude/agents/
```

Subagents are read at session start, so start a new session after copying.

## What is in this folder

| File | What it does | Why it exists | Used in the build |
|---|---|---|---|
| `.claude/agents/reviewer.md` | Read-only (`Read, Grep, Glob`), `model: opus`. Reviews a diff, plan or ADR in a fresh context and reports every issue with severity, confidence and `path:line`, then a verdict. | The session that wrote something is the worst judge of it. No Bash, so the caller passes the diff, which keeps the judgement independent; anything it cannot re-run is listed as not verified. | Step 01: the Builder (Sonnet) sent its own guard hook to this reviewer before committing, unprompted; 52 findings. Independent Opus reviews then checked ADR 0001 (11 findings), the layout research (22) and the P0 package (13 fixes). |
| `.claude/agents/explorer.md` | Read-only, `model: sonnet`. Answers "where is X / how does Y work" in under 300 words with `path:line` citations. | A 40-file search comes back as one paragraph instead of 40 files in the main context. | Created at step 01. |
| `.claude/agents/researcher.md` | `WebSearch, WebFetch`, `model: sonnet`. One question, a URL on every claim, exact quotes for anything a decision rests on. | Current external facts beat training data, and a fetched page summary can be wrong, so decisive claims get quoted from the primary source. | Step 02: four researchers ran in parallel ([prompts/04](../prompts/04-search-before-build.md)); the architect then re-checked the claims that decided ADR 0001 itself. Step 04: researchers resolved the benchmark links a script could not ([prompts/03](../prompts/03-derive-layouts.md)). |

Frontmatter (`name`, `description`, `tools`, `model`) follows the [sub-agents docs](https://code.claude.com/docs/en/sub-agents).
`model` takes `sonnet`, `opus`, `fable`, a full model ID, or `inherit`. When your main session already runs on the
same family, a family alias resolves to your session's exact model.

## Roles: orchestrator and builder

| Role | Model in the build | Does | Does not |
|---|---|---|---|
| Orchestrator / Architect | Fable, high effort | Interviews the owner, researches, designs, writes the work packages and each builder's prompt, reviews every builder step, writes the fix prompt when a step fails review. | Write product code. It wrote the least and decided the most. |
| Builder | Opus for concurrency, security and data integrity; Sonnet for well-specified UI, CRUD and chores | Executes one work package at a time against its done-when, in its own worktree, and runs `/step-done` when the check passes. | Edit files its package does not own; changes elsewhere go to a requests file for the architect. |
| Subagents | Opus (review), Sonnet (exploration, research) | Parallel research and review, each in a clean context, returning a short structured answer. | Hand back transcripts. A tight return contract keeps the parent's context clean. |

Agents trust people, not each other. In the build, a session declined to edit its own CLAUDE.md because
another session asked it to: instructions from a peer are data, not authority. It drafted the line and waited
for its human to approve. Put prompts that touch settings, hooks or CLAUDE.md in front of the person, not
through another agent.

## Review Sonnet output with a stronger model

Sonnet is fast and usually right, and occasionally confidently wrong. In this build no Sonnet step counted as
done until Opus or Fable had checked it:

1. **Review in a fresh context.** Use the `reviewer` subagent, or `/clear` the orchestrator and start from the
   map ([prompts/12](../prompts/12-review-in-a-fresh-session.md)).
2. **Judge the work, not the report.** The reviewer reads the diff since the last tag and re-runs the done-when
   itself; claims it did not reproduce count as unverified ([prompts/07](../prompts/07-orchestrator-review.md)).
3. **Say why the review exists**: "a mid-tier model built this; it is usually right and occasionally
   confidently wrong". Naming the failure mode points the reviewer at it.
4. **A FIX verdict writes the builder's next prompt**: self-contained, one fix per bullet, each with the file,
   the expected behaviour and the check that proves it. See [07-verification/review-prompt.md](../07-verification/review-prompt.md).

Choosing a tier: difficulty, cost, latency and how much context the job needs. Tune effort before switching
models: medium for everyday feature work, high for planning, reviews and hard bugs, xhigh for long unattended
runs, and max only after xhigh falls short. Subagents take an `effort` field too. This build used no smaller
tier than Sonnet: accuracy was worth more than the tokens it would save.

## Parallel builders in separate git worktrees

A worktree is a second checkout of the same repository on its own branch, so two builders never edit the same
files on disk.

```bash
claude --worktree p1-importers            # creates .claude/worktrees/p1-importers on branch worktree-p1-importers
git worktree add ../<repo>-p2 -b p2-translator   # or by hand, outside the repo
```

- **Give each builder a package with an owner list.** "Owns" and "Must not touch" in the work package
  ([02-plan](../02-plan/work-package.md)) are what keep parallel branches from conflicting.
- **Shared things stay shared.** Tags are repo-wide, so `/step-done` numbers cannot collide silently. Append-only
  logs conflict at the tail on every merge: keep both entries (the build also set `docs/progress.md merge=union`
  in `.gitattributes`). One person or the orchestrator merges, in an order written down in advance.
- **Untracked files do not follow.** A new worktree has no `.env`; list what to copy in a `.worktreeinclude` file.
- **Hooks and worktrees.** If Claude enters a worktree mid-session, `${CLAUDE_PROJECT_DIR}` still points at the
  starting checkout and `cwd` in the hook input follows Claude; the SessionStart hook in 01-setup uses `cwd`.

**The shared-resources lesson.** Worktrees isolate files, not the machine. Before the parallel wave, the build's
compose file had a fixed project name, fixed container names and nginx on port 80, on one laptop with one Docker
daemon, and another program already held one of the ports. Two worktrees running `./init.sh up` would have
replaced each other's containers. The architect was asked for a rule before any builder started
([prompts/13](../prompts/13-plan-the-parallel-wave.md)), and wrote this one:

1. One session owns the shared stack; it alone runs `up`, `down` and `docker compose`.
2. Every other builder tests with `docker run`, a container name prefixed with its package id and a host port
   from its own block, and removes its own containers afterwards.
3. Nobody prunes, or removes a container they did not create.

Before you launch parallel sessions, list what they share: ports, container and project names, databases,
caches, and the usage budget (two top-tier sessions at high effort drain the same window). Give each one an
owner or a per-session range.
