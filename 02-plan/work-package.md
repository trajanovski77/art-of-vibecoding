# Build plan

<!-- Starter template (02-plan). Save as docs/BUILD-PLAN.md. One section per work package, in the shape below.
     The architect writes it (prompts/05), a fresh session attacks it (prompts/06), and every builder starts
     from its own section (prompts/11). -->

Work packages for parallel builder sessions. Design: `docs/PLAN.md`; contracts: `docs/contracts.md`.
Every package has a done-when that is a command. The architect reviews each package against it; a package
is finished when that review passes and the step is recorded with `/step-done`.

## How a builder session starts

1. Read `CLAUDE.md`, the tail of `docs/progress.md` (the SessionStart hook prints it), this file's section
   for your package, and the contract sections it names. Read the rest of the design only if your package
   says so: every file you read is context you pay for on every call.
2. Work in your own git worktree on a branch named after the package (`p3-generator`). When the done-when
   passes, run `/step-done` on your branch; tags are repo-wide, so step numbers never race. The architect
   reviews and merges. After a FIX verdict, merge `main` into your branch first, apply the fixes, rerun the
   done-when, and run `/step-done` again.
3. `./init.sh check` must pass before you start. If it does not, fix the environment first and say so.
4. Edit only the files your package owns. If you need a change in another package's file, add one line to
   `docs/reviews/requests.md` (package, file, what, why) and continue with a stub.
5. Every step: run the package's done-when. Flip `passes` in `features.json` only for features whose steps
   you ran and saw pass, and commit the flip with the work.
6. When you ask for review, paste the done-when output and `./init.sh status` into the request.

## Shared resources

<!-- Worktrees isolate files, not the machine. List everything two builders could both grab. -->

| Resource | Owner | Everyone else |
|---|---|---|
| <the running stack: compose project, container names, port 80> | <one session, e.g. S0> | <test with their own container name and a port from their block> |
| <ports> | <block per package, e.g. P3 18100-18119> | <stay inside your block> |
| <database, cache, external sandbox account> | <owner> | <how to get an isolated copy> |

## Package table

| Id | Package | Model | Parallel | Depends on |
|---|---|---|---|---|
| P0 | Harness and deployment skeleton | Opus | starts first | none |
| P1 | <name> | Sonnet | yes | <contracts; P0 for the stack> |
| P2 | <name> | Opus | yes | <what, from which package> |

Model: Opus for concurrency, security and data-integrity logic; Sonnet for well-specified UI, CRUD and
chores. A Sonnet package counts after an Opus or Fable review. A Sonnet package that hits a data-integrity
question hands it to the architect.

Single owners for shared paths: <`path`: package, one per line, for every file two packages might both edit>.

---

## P<N>. <Package name> (<Model>)

**Goal.** <One or two sentences: the observable outcome when this package is done.>

**Owns.** <Every file and directory this package creates or edits. Anything not listed belongs to someone
else.>

**Implements.** <Contract sections (for example C2 and C3 in `docs/contracts.md`) and feature ids in
`features.json`.>

**Must not touch.** <Files owned by other packages. Changes go through `docs/reviews/requests.md`.>

**Depends on.** <Packages, what this one needs from each, and what to stub until it lands.>

**Done when.**
```bash
<one command, or an && chain, that exits 0 only when the package works>
```
prints `<expected output>`. <A second check if needed, and any evidence to save, such as screenshots in
`docs/journey/P<N>/`.>

---

<!-- An example from the build, abridged. Note the done-when: a chain a reviewer can run without guessing,
     with the exact line it must print.

## P0. Harness and deployment skeleton (Opus)

**Goal.** `./init.sh` brings up the reverse proxy plus one smoke project and proves it; the files every
other package builds on.
...
**Done when.**
    ./init.sh check && ./init.sh up && ./init.sh smoke
prints `SMOKE OK` (proxy 200 on `/`; the smoke project 200 on its login page through the proxy; both fixture
files validate against their schemas), and `python3 scripts/check_features.py --list` prints every feature id
with its status. -->
