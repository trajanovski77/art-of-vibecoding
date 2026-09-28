---
name: codex-orchestration
description: Claude Code + Codex orchestration workflow. Load at the START of any feature implementation, refactor, logic bug fix or multi-file task that will produce backend or non-design code. Defines the split (Claude orchestrates and owns all design/frontend; Codex implements backend and non-design via the openai/codex-plugin-cc plugin), the plan, adversarial review, delegate, verify, integrate loop, the Codex model, and the running notes file every session reads and updates. Purely visual work does not need this loop.
---

# Codex Orchestration

A standing rule for how coding work is split between **Claude Code** and **Codex** (the
[`openai/codex-plugin-cc`](https://github.com/openai/codex-plugin-cc) plugin). It lives in
`~/.claude/skills/` so it applies in every project; put it in a repo's `.claude/skills/` instead if a team
should share it. Every implementation runs through this loop.

Load it alongside whatever house-style skill the project defines (for example `<project>-engineering`, and
`<project>-design` whenever UI is in scope). Project rules still apply to everything both Codex and Claude write.

**Read `notes.md` in this folder before delegating anything** (section 4). It carries what has worked and what
Codex got wrong.

## When this triggers

At the start of any task that will produce backend or non-design code: a new feature, a refactor, a bug fix in
logic/services/data, a migration, an API change, or any multi-file change. If a task is purely visual (a
component's look, a token, an animation, copy), Claude does it and this loop is a no-op. The moment the same
task needs an endpoint, a model, a service or a job, this governs.

## 1. Roles: a hard split, by nature of the work

**Claude is the orchestrator and the sole implementer of everything design/frontend.** Never delegate these to
Codex:

- UI components and layout, styling and design tokens, animation and motion
- Accessibility, responsive behaviour, keyboard paths, `prefers-reduced-motion`
- Brand and design-system integrity
- UI-coupled state: anything whose correctness is judged by how the interface looks or behaves

**Codex implements everything backend and non-design.** Delegate these:

- API routes / views / serializers, business logic, services
- DB schema, models, migrations, access-control policies
- Auth, background jobs, the model/AI seam and providers, utilities
- Infra and config, and **the tests for all of the above**

**Repo mapping.** Write down which paths belong to whom, for example: Claude owns `<frontend>/src/**`
(components, styles, pages, hooks, UI-coupled client state); Codex owns `<backend>/**`. Non-visual utilities in
a frontend repo (an API client, pure helpers) may go to Codex **only** when they carry no design judgement.
When in doubt whether something is "design", it stays with Claude.

**How to delegate:** `/codex:rescue` (it runs the `codex:codex-rescue` subagent). Prefer
`/codex:rescue --background` for anything long-running so Claude keeps working; check with `/codex:status` and
collect the output with `/codex:result <job-id>`. Use `--wait` only for a short unit with nothing else to do
meanwhile.

Claude never writes the backend itself except as the last-resort takeover in section 2. Codex never touches
design/frontend. There is no overlap.

## 2. The orchestration loop

Run these in order. Do not delegate without a written plan.

### a. Write the plan first
A concrete plan, in the conversation, covering:
- **Goal**: the outcome in one or two lines.
- **Files touched**: actual paths, split into "Codex writes" and "Claude writes".
- **Backend contract**: API shape (routes, methods), request/response types, DB changes (models, fields,
  migrations), and any invariant the change touches.
- **Frontend contract**: what the UI consumes, the exact types and endpoints it binds to (derived from the
  backend contract, so it comes second).
- **The split**: who does what, explicitly.
- **Acceptance criteria**: the checks that decide "done" (tests pass, lints clean, behaviour verified end to
  end, access control holds, no scope creep).

### b. Pressure-test the plan (non-trivial plans only)
For anything beyond a one-file change, challenge the plan **before** writing code: run
`/codex:adversarial-review` with focus text naming the risky areas (the contract, the data model, the failure
modes, the assumptions). If there is no diff yet to point it at, delegate a **read-only plan critique** through
`/codex:rescue` that forbids edits and asks only for holes in the approach. Fold the findings into the plan.
**One review pass by default**; review again only if the plan materially changed.

### c. Delegate one coherent unit
The delegation prompt contains:
- the **exact contract** from the plan (types, routes, DB shape, behaviour),
- the **exact file paths** Codex should create or edit,
- an **explicit do-not-touch list** naming every frontend/design path,
- a **requirement to write tests** for the backend it produces,
- a **requirement to self-verify and report**: Codex runs the project's tests and linters and returns exact
  pass/fail counts plus a one-line-per-file diff summary,
- the project invariants that apply (for example access-control wrappers, idempotency, money in integer cents;
  cite the backend's `CLAUDE.md` or equivalent).

**One coherent unit per delegation.** Split unrelated asks into separate runs.

### d. Verify what Codex returns: tiered, not blind, not wasteful
Review at the altitude the code demands; re-verifying everything re-spends on Claude the budget this workflow
saves.
1. **Read the diff with attention proportional to risk.** Read the load-bearing code closely; skim boilerplate.
2. **Fully re-verify only the load-bearing paths** (access control, auth, money, idempotency, anything
   security- or data-critical): re-read the code *and* re-run their tests. For everything else, check against
   the acceptance criteria and Codex's reported counts, and spot-check.
3. **One confirming run**: re-run the touched suite once to confirm the reported counts (bring the environment
   up first). Read the output, not just the summary line: a sandbox that cannot reach the database can report
   "passed" next to a wall of connection errors.
4. Hunt for **scope creep** (files changed that were not in the plan) and **stubbed or shortcut logic** (TODOs,
   hardcoded returns, empty bodies, tests that assert nothing, dropped access-control wrappers).
5. Then **accept**, or send `/codex:rescue --resume` with specific, itemised corrections (the exact defect,
   only the delta).
6. Still wrong after **about two revision rounds**: **take over**, finish the unit, and **write down why**, in
   the conversation and in `notes.md`.

Trust rises with Codex's track record in `notes.md`: more clean deliveries mean a lighter review of the
non-load-bearing code. The load-bearing paths always get the full pass.

### e. Build the frontend against the settled contract, then integrate
Only after the backend contract is **settled and verified**, implement the frontend against it (loading the
project's design skill). Then verify **the seam actually built**, the frontend against the API. Do not repeat
on Claude an end-to-end check that Codex's tests already cover.

### f. Ship discipline
Follow the project's ship rules (progress log, wiki, commit per feature). No secrets, ever.

## Token economy

The point of this workflow is to move the token-heavy build loop onto Codex (a separate quota) so Claude's
budget lasts.

- **Context and planning stay on Claude, gathered once.** Read only what the plan needs; never re-read a file
  already in context.
- **Verification is tiered** (step d): full re-verify on load-bearing paths, spot-check the rest.
- **One background watcher, no manual polling loop.** When a long job needs a check, compare the job log's
  last-write time to now: a stale log under a "running" status means it hung; cancel and take over.
- **Keep the dev environment warm**: bring services up once per work session.
- **Orchestrate substantial units only.** For a one-file backend tweak the contract and review overhead exceed
  the work; do it on Claude directly.
- **Report tersely**: what shipped, what was verified, what is next.

## 3. Codex model

Codex runs on **`<codex-model>` at `high` (or higher) reasoning effort**. Model names change monthly; choose by
difficulty, cost and latency, and update this line when a newer model ships.

- The enforceable lever is Codex's own config, **`~/.codex/config.toml`**, which the CLI loads. Codex does not
  read a project-level `.codex/config.toml`, so set the model once, globally: `model = "<codex-model>"` and
  `model_reasoning_effort` at `high` or above.
- Before relying on it, confirm the **effective** model with `codex doctor`.
- If it shows a different model or a lower effort, fix the config, or pass `--model <codex-model> --effort high`
  on that `/codex:rescue` call.
- `~/.codex/config.toml` holds personal keys and machine state. Never copy it into a repo.

## 4. Running notes: read and update every session

`notes.md` (this folder) is a living log of how to steer Codex.

- **Read it before delegating.** Apply what worked; avoid what failed.
- **After every significant delegation, append**: what steering worked, what Codex got wrong (and the
  correction), and any contract pattern worth reusing. Tag entries with the project.
- Keep entries short and dated. Prune what is stale or superseded.

## Quick reference

| Step | Command |
| --- | --- |
| Delegate backend work (long) | `/codex:rescue --background <contract + paths + do-not-touch + tests>` |
| Delegate backend work (quick) | `/codex:rescue --wait <...>` |
| Check job progress | `/codex:status` (or `/codex:status <job-id>`) |
| Collect finished output | `/codex:result <job-id>` |
| Pressure-test the plan | `/codex:adversarial-review <focus text>` |
| Correct a delegation | `/codex:rescue --resume <specific corrections>` |
| Cancel a runaway job | `/codex:cancel <job-id>` |

The split is fixed: **Claude owns design/frontend and orchestration; Codex owns backend and non-design.** Plan,
adversarial review, delegate one unit with a hard contract, read the diff and verify, build the frontend against
it, integrate, ship. Read and update `notes.md`.
