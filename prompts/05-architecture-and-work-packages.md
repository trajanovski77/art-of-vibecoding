Now design Vezilka Goldsets, and plan the build so that several builder sessions can work in
parallel without stepping on each other.

<documents>
@docs/BRIEF.md
@research/LAYOUTS.md
@research/RESEARCH.md
@docs/adr/0001-adopt-adapt-or-build.md
</documents>

<constraints>
- Time box: about a day and a half of building, starting tonight. Design for the finished product,
  but order the work so that a thin vertical slice (sign-in, one task type end to end, export)
  works first and everything else is additive.
- ADR-0001 is accepted: Potato runs unmodified, and this repo holds only the pipeline around it.
  Design around its five pass bars; the vertical slice tonight must be able to test each of them.
- Keep the design as small as the brief allows. Every component must earn its place against a
  stated requirement; say which one.
</constraints>

<deliverables>
1. docs/PLAN.md: architecture overview, data model, item lifecycle (as a state machine), the
   review and agreement policy per task type, the export pipeline to EuroEval format with
   train/val/test splits, security and privacy model, and the decisions you made along the way
   with the reason for each.
2. docs/architecture/: Mermaid C4 context and container diagrams and an ER diagram. Every box
   must correspond to a directory or service that will exist.
3. docs/contracts.md: every data contract between components (source files, the translation
   script's output, Potato input JSONL, Potato configs, Potato's annotation output, the EuroEval
   export) with exact field names and one example record each. Builders will code against these in
   parallel, so ambiguity here becomes integration bugs later.
4. docs/BUILD-PLAN.md: the work split into packages. For each: goal, the files it owns, the
   contract sections it implements, files it must not touch, dependencies, whether it can run in
   parallel, the model it needs (Opus for concurrency, security and data-integrity logic;
   Sonnet for well-specified UI, CRUD and chores) and a done-when that is a command someone can
   run. You will review every package against its done-when before it counts as finished, so
   write each one so that a reviewer can check it without guessing.
5. The build harness, so progress survives across sessions and context resets:
   features.json listing every end-to-end behaviour as {"id", "description", "steps", "passes":
   false}; init.sh that starts the stack and runs a smoke test; and the first entry in
   docs/progress.md describing how a builder session should start.
</deliverables>

If the documents leave a decision open that changes the design, ask me before assuming; decide
everything else yourself and record why.
