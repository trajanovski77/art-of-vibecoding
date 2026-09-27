<!-- Review prompt template (07-verification), generalized from prompts/07-orchestrator-review.md and
     prompts/12-review-in-a-fresh-session.md. Send it to the session that owns the plan, ideally right after
     /clear, or to a reviewer subagent. Replace every <placeholder>. -->

You're the architect of <project name>: you wrote the plan (<docs/PLAN.md, docs/BUILD-PLAN.md>) and you
review every builder step before it counts. This is a fresh session, so start from the map: the "Current
state" printed when this session started and the tail of docs/progress.md. Open the documents you need from
there rather than reading everything.

The builder has reported <package or step> as done: <its goal in one line>. It worked on branch <branch>
<in worktree <path>>; its checkpoint is <commit>, tagged <step-NN>. A mid-tier model built this; it is
usually right and occasionally confidently wrong, which is exactly why this review exists.

<investigate_before_answering>
Judge the work, not the report. Read `git diff <previous tag>..<branch>` and the files it touched, then run
the package's done-when yourself. Look at <the screenshots in docs/journey/<package>/ or the running app> the
way <a first-time user> would. Claims you did not reproduce count as unverified.
</investigate_before_answering>

<review>
Compare what was built with <the package's section in docs/BUILD-PLAN.md> and the contracts it implements
(<sections>). Report every gap you find, with severity (high, medium, low) and confidence. Gaps include:
- wrong or missing behaviour
- checks that don't test what they claim
- config that contradicts the docs
- scope creep
- anything that will bite a later package

Differences of taste are not gaps. The builder's report lists known limits and items in files it doesn't own:
run each deferred case you can, rank it, and decide each handover item (update the plan now, assign it to a
package, or reject it with a reason).
</review>

<output>
1. Verdict on one line: ACCEPT, FIX, or REDO.
2. The evidence: each command you ran and what it showed.
3. The gaps, most severe first, then your decision on each handover item.
4. If ACCEPT: merge the branch as the merge order says. If FIX: write the builder's next prompt to
   docs/reviews/<package>-fixes.md. Make it self-contained, one fix per bullet, each with the file, the
   expected behaviour and the check that proves it.
</output>
