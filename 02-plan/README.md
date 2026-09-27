# 02 · Plan before coding

Interview, look at real data, search before you build, then design, then attack the design. The output is
not a document for its own sake: it is the set of work packages parallel builders start from, and a harness
that tells any session, in one command, whether the project works.

Copy into your project root:

```bash
cp 02-plan/work-package.md <your-repo>/docs/BUILD-PLAN.md
cp 02-plan/features.json 02-plan/init.sh <your-repo>/ && chmod +x <your-repo>/init.sh
cd <your-repo> && ./init.sh check && ./init.sh smoke && ./init.sh status
```

Then fill in the CONFIG block at the top of `init.sh` (the commands that start, stop and check your stack),
replace the example features with your own, and write one section of `BUILD-PLAN.md` per package.

## What each file is for

| File | What it does | Why it exists | Used in the build |
|---|---|---|---|
| `work-package.md` | The build plan: how a builder session starts, shared resources, the package table, and one section per package: goal, owns, implements, must not touch, depends on, done when. | "Owns" plus "must not touch" is what lets builders work in parallel without meeting. A done-when that is a command lets a reviewer check the package without guessing. | `docs/BUILD-PLAN.md` was written at step 05 ([prompts/05](../prompts/05-architecture-and-work-packages.md)): packages P0 to P10 plus a vertical slice. The "Shared resources" section comes from the parallel wave ([prompts/13](../prompts/13-plan-the-parallel-wave.md)). |
| `features.json` | Every end-to-end behaviour as `{id, package, description, steps, passes}`, all `false` at the start. | Progress survives `/clear`, compaction and new sessions. A builder flips `passes` only after running the steps in front of them. | Written at step 05; 42 features, all `false`, by the time building started. P0 was the first package to flip any (2 of 42). |
| `init.sh` | `check`, `up`, `smoke`, `down`, `status`. Exit 0 ok, 1 a check failed, 2 usage. | One command that says whether the project works. Done-whens call it, so its names and exit codes stay stable. | Step 05 wrote it; P0 made `./init.sh check && ./init.sh up && ./init.sh smoke` print `SMOKE OK`. Ports and names come from variables here because fixed ones collide when two worktrees share one machine. |

## The planning prompts, in the order they ran

| Card | What it asks for | The habit it shows | What came back in the build |
|---|---|---|---|
| [02 Discovery brief](../prompts/02-discovery-brief.md) | Read the data and the conventions, then interview the owner. No stack, no diagrams, no code yet. | A named propose-only mode. At most eight questions, each with two to four options and a recommended default; inferences stated instead of asked. | `docs/BRIEF.md`. The architect asked 8 questions, stated 7 assumptions, and found a table of category owners in the spreadsheet nobody had mentioned. |
| [03 Derive layouts](../prompts/03-derive-layouts.md) | Sample real rows from every input, then classify. | Script first, subagents only for the mess, each returning four fields. Every classification quotes the field names it relied on. | 83 benchmarks sorted into six layout families, with the two unreadable ones documented. |
| [04 Search before build](../prompts/04-search-before-build.md) | Find what already exists, the team's own code first, judged against the brief. | One researcher per question, in parallel; the claims that decide the outcome re-checked against their sources. | ADR 0001: adopt an existing open-source annotation tool unmodified and build only the pipeline around it. |
| [05 Architecture and work packages](../prompts/05-architecture-and-work-packages.md) | Plan, diagrams, data contracts with exact field names, the build plan, `features.json`, `init.sh`. | Documents first, request last. Contracts before code, so builders can work in parallel. Every component earns its place against a requirement. | `docs/PLAN.md`, the contracts, `docs/BUILD-PLAN.md`, `features.json`, `init.sh`, ADRs 0002 and 0003. |
| [06 Attack the plan](../prompts/06-attack-the-plan.md) | Review the plan as someone who did not write it. | Fresh context. Report everything, including uncertain issues; a later pass filters. Differences of taste are not issues. Verdict first. | A written review: one verdict line, then one entry per issue with severity, confidence, the failure scenario and the smallest fix. |
| [13 Plan the parallel wave](../prompts/13-plan-the-parallel-wave.md) | Which packages start now, in which session and order, with a rule for the shared Docker host and a merge order. | Name the shared resources before launching builders. One standalone prompt per new session. | A sessions table, a rule that one session owns the stack while the others test with their own container names and ports, a merge order with the expected conflicts, and one prompt per builder. |

The builder side of the same plan is [prompts/11](../prompts/11-builder-work-package.md): one package, the files
it owns, and a done-when it must show passing.

## Adapt

- Keep each package small enough for one builder session and one review.
- Write done-whens a stranger could run: literal commands, the output they must print, where evidence goes.
- Write features from the user's side ("a volunteer can sign in with Google"), not the code's.
- Pick the model per package by what can go wrong: Opus where a mistake corrupts data or leaks access,
  Sonnet where the spec is complete and a reviewer will check the result.
