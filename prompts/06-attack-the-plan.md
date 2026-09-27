You didn't write this plan, and that's why you're reviewing it: the session that wrote a plan is
the worst judge of it. It will be built tomorrow by several sessions in parallel, so anything
wrong here gets built several times over.

<documents>
@docs/BRIEF.md
@docs/PLAN.md
@docs/api-contract.md
@docs/BUILD-PLAN.md
@features.json
</documents>

<review>
Look for what would break in production or in the parallel build, including:
- data integrity: two volunteers getting the same item, lost edits, gold answers changing after
  export, train/test leakage;
- security: an annotator seeing another's answers or the gold, privilege escalation, login abuse;
- EuroEval compatibility: column names, label sets, split names, length limits;
- contract gaps: an endpoint or field two work packages will interpret differently;
- plan feasibility: packages that claim to be parallel but share files, done-whens that can't be
  run, a vertical slice that doesn't actually reach export.
Report every issue you find, including low-severity and uncertain ones; a later pass decides
what to act on. Don't propose rewrites of parts that are merely different from how you'd do it.
</review>

<output>
Start with a one-line verdict: SHIP, SHIP WITH FIXES, or RETHINK. Then one entry per issue:
severity (high, medium, low), confidence (high, medium, low), where (file and section), the
concrete failure scenario, and the smallest fix. Write the review to docs/reviews/plan-review.md.
</output>
