<context>
You're building one work package of Vezilka Goldsets. The design is settled: @docs/BUILD-PLAN.md
(package P0), @docs/contracts.md (C7 and the environment variables), and ADR-0002 and ADR-0003. Read
the wiki's index and the pages for the components you touch before writing code; they point at the
exact lines that matter. Other packages will be built on top of this one, and in parallel with it.
</context>

<task>
Implement P0, the harness and deployment skeleton, exactly as BUILD-PLAN.md specifies: `./init.sh up`
brings up nginx and the smoke project `sample-l01` (Potato, pinned image, our theme), and `./init.sh
smoke` proves it.
</task>

<constraints>
- Touch only the files P0 owns in BUILD-PLAN.md. The orchestrator is editing docs/ and .env.example
  right now; if you need a new variable or a doc change, write it down in your report instead of
  editing those files.
- Start the session the way BUILD-PLAN.md's "How a builder session starts" says, and flip a feature in
  features.json to passing only when its own command passes in front of you.
- Keep it as small as the spec allows. Don't add services, flags or abstractions the spec doesn't ask for.
</constraints>

<done_when>
The P0 done-when commands print `SMOKE OK` and the feature list. Then take screenshots of the themed
login page and of one annotated item at 1440 px with headless Chrome into docs/journey/p0/.
</done_when>

<report>
Pass/fail counts, one line per changed file, the Potato image tag you pinned, anything you could not
verify, and anything you needed from files you don't own. Then run /checkpoint.
</report>
