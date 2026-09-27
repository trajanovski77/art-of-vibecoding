The owner has decided to build everything in BUILD-PLAN.md, including all five pass bars of the
vertical slice, before the build freeze on Friday at 17:00. Please plan the parallel build and write
the prompts the new builder sessions will start from.

<context>
- P0 is being fixed now against docs/reviews/p0-fixes.md. Assume you re-check it and it is on main
  within the hour.
- Usage budget is not the constraint tonight. Wasted or duplicated work still is.
- Available sessions:
  - The existing Builder (Opus 5.5), which knows P0 and the stack best.
  - As many new builder sessions as you need. Each starts in its own fresh git worktree of this
    repo, branched from main. I set each one's model and effort before it gets its prompt.
- One laptop and one Docker host. The compose file has a fixed project name (goldsets), fixed
  container names and nginx on port 80, and port 8100 belongs to an unrelated process. If two
  worktrees run `./init.sh up` at the same time, they replace each other's containers.
</context>

<task>
Plan wave 1: which packages start now, in which session, and in what order the rest follow. Order
them so the vertical slice can run its five pass bars as early as possible, and no package waits on
work that could already have started.
</task>

<deliverables>
1. docs/launch/wave-1.md with:
   - A table with one row per session: its packages in order, model and effort, branch name, what
     it needs from other packages, and when its work will be ready for your review.
   - The rule for the shared Docker host: who may run the stack, and how everyone else tests (for
     example `docker run` with its own container name and port).
   - The merge order you'll use as packages come back, and where you expect conflicts
     (features.json, docs/progress.md, vault/).
2. One prompt per new session, in docs/launch/prompts/<package>.md, in the same shape as the P0
   prompt: context, task, constraints, done-when as runnable commands, and a report section. The
   constraints cover files owned, files not to touch, and the Docker rule. Each prompt must stand
   alone, because the session reading it starts with no history.
3. The existing Builder's next prompt after the P0 fixes, in the same folder.
</deliverables>

<constraints>
- Follow the model tiers in the package table unless you have a reason to change one; write the
  reason down.
- A Sonnet package counts only after a review by you or by an Opus reviewer subagent you start.
- Change BUILD-PLAN.md only where this wave differs from it (the Docker rule, for example), and list
  what you changed.
- Hold the commit until the P0 fixes are merged into main, then run /checkpoint for this step.
</constraints>

When it's written, tell me which sessions to open, with each one's model, effort and prompt file.
