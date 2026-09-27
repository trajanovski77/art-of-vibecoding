You're the Orchestrator / Architect of Vezilka Goldsets: you wrote the plan (docs/PLAN.md,
docs/contracts.md, docs/BUILD-PLAN.md) and you review every Builder step before it counts. This is a
fresh session, so start from the map: the "Current state" of vault/index.md, printed when this
session started, and the tail of docs/progress.md. Open the wiki pages and documents you need from
there rather than reading everything.

The Builder has reported work package P0 (harness and deployment skeleton) as done. It worked in its
own worktree, <path-to-worktree>, on branch p0-harness. Its
checkpoint is commit 88ca1b4, tagged step-11 on that branch only. Its stack is still running there,
with nginx on port 80 and the smoke project on 8199. It ran its own reviewer and applied 13 fixes;
the review that decides is still yours.

<investigate_before_answering>
Judge the work, not the report. Read `git diff step-10..p0-harness` and the files it touched, then
run P0's done-when yourself in the worktree. Port 8100 on this laptop belongs to an unrelated
process, so the Builder used GOLDSETS_SAMPLE_PORT=8199. Do the same, and leave that process alone.
Look at the two screenshots in docs/journey/p0/ the way a volunteer would. Claims you did not
reproduce count as unverified.
</investigate_before_answering>

<review>
Compare what was built with the P0 section of docs/BUILD-PLAN.md and the contracts it implements
(C2, C2b, C3, C4, C7, C12). Report every gap you find, with severity (high, medium, low) and
confidence. Gaps include:
- wrong or missing behaviour
- checks that don't test what they claim
- config that contradicts the docs
- scope creep
- anything that will bite a later package

Differences of taste are not gaps.

The Builder's report lists items in files it doesn't own:
- the C10 label shapes Potato 2.9.4 actually exports
- the .secret format in C7
- P3 taking over sample-l01
- notes for P7
- gaps in C2, C2b and C12
- the F100/F101 paths
- screenshots saved under docs/journey/

You own the plan, so decide each one: update the contract or package now, assign it to a package,
or reject it with a reason. One more item from me: vault/.obsidian/ holds Obsidian's per-user
workspace files and shows up as untracked on main. It should be ignored.
</review>

<output>
1. Verdict on one line: ACCEPT, FIX, or REDO.
2. The evidence: each command you ran and what it showed.
3. The gaps, most severe first, then your decision on each handover item.
4. If ACCEPT: fast-forward main to p0-harness (the step-11 tag comes with it) and leave the
   worktree and its running stack alone. If FIX: write the Builder's next prompt to
   docs/reviews/p0-fixes.md. Make it self-contained, one fix per bullet, each with the file, the
   expected behaviour and the check that proves it.
</output>
