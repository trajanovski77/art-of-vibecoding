# One prompt, annotated

This is [prompts/11-builder-work-package.md](../prompts/11-builder-work-package.md), the prompt that started the
builder on the first work package, exactly as it was sent. It has all five parts of the anatomy. The notes under
each block say what the block does and what would go wrong without it.

---

```text
<context>
You're building one work package of Vezilka Goldsets. The design is settled: @docs/BUILD-PLAN.md
(package P0), @docs/contracts.md (C7 and the environment variables), and ADR-0002 and ADR-0003. Read
the wiki's index and the pages for the components you touch before writing code; they point at the
exact lines that matter. Other packages will be built on top of this one, and in parallel with it.
</context>
```

**Context: what exists, what to read, why it matters.**
- "The design is settled" closes a door: this session builds, it does not redesign.
- `@docs/BUILD-PLAN.md` pulls the file into the prompt. It names the one package and the contract sections to
  read, not the whole design, so the session spends its context on what it will build.
- "Read the wiki's index … they point at the exact lines" sends it to the map first ([04-context](../04-context/README.md)).
- The last sentence is the reason behind every constraint below: others build on this, in parallel.

```text
<task>
Implement P0, the harness and deployment skeleton, exactly as BUILD-PLAN.md specifies: `./init.sh up`
brings up nginx and the smoke project `sample-l01` (Potato, pinned image, our theme), and `./init.sh
smoke` proves it.
</task>
```

**Task: one observable outcome.** Not "set up deployment" but two commands and what they do. "Exactly as
BUILD-PLAN.md specifies" makes the plan the authority, so the review can compare the two.

```text
<constraints>
- Touch only the files P0 owns in BUILD-PLAN.md. The orchestrator is editing docs/ and .env.example
  right now; if you need a new variable or a doc change, write it down in your report instead of
  editing those files.
- Start the session the way BUILD-PLAN.md's "How a builder session starts" says, and flip a feature in
  features.json to passing only when its own command passes in front of you.
- Keep it as small as the spec allows. Don't add services, flags or abstractions the spec doesn't ask for.
</constraints>
```

**Constraints: each with its reason, and each says what to do instead.**
- "The orchestrator is editing docs/ … right now" is the reason; "write it down in your report instead" is the
  alternative. A rule with a reason generalises to cases the rule didn't name.
- "Only when its own command passes in front of you" ties progress tracking to evidence.
- "As small as the spec allows" heads off the most common failure of capable models: extra layers nobody asked for.

```text
<done_when>
The P0 done-when commands print `SMOKE OK` and the feature list. Then take screenshots of the themed
login page and of one annotated item at 1440 px with headless Chrome into docs/journey/p0/.
</done_when>
```

**Done-when: checks it runs and shows.** A literal output (`SMOKE OK`) is the stop signal. The screenshots are
evidence a human (or a reviewer) can look at later: in the review of this package, those screenshots are how
the architect spotted that the login page was still the tool's default look, while every command passed
([07-verification](../07-verification/README.md)).

```text
<report>
Pass/fail counts, one line per changed file, the Potato image tag you pinned, anything you could not
verify, and anything you needed from files you don't own. Then run /checkpoint.
</report>
```

**Report: the shape of the answer.** Counts first, then files, then the one fact the next package depends on
(the pinned image tag), then what is unverified. "Anything you needed from files you don't own" turns the
ownership constraint into a handover list for the architect instead of silent edits. The last line closes the
step with the skill (called `checkpoint` in the build, `step-done` in [05-skills](../05-skills/README.md)).

---

What it is missing, on purpose: no persona beyond one clause, no capital letters, no "think step by step", no
"double-check your work". The effort level is set on the session, and the double-check is a separate reviewer
in a fresh context ([prompts/12](../prompts/12-review-in-a-fresh-session.md)).
