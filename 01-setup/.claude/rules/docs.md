---
paths:
  - "docs/**"
---

# Docs rules

## Plans (`docs/plans/<short-title>.md`)
Goal, the steps (each one small enough for one commit), how each step will be verified, open questions.

## Architecture decision records (`docs/adr/NNNN-short-title.md`)
One decision per file. Number it with the next free four-digit number and start from
`docs/adr/0000-template.md`. An accepted ADR stays as written, so the history of why stays readable:
to change a decision, write a new ADR and set the old one's Status to `superseded by NNNN`.
Every ADR has these sections, in this order:
- **Status** and **Date**: status is `proposed`, `accepted`, or `superseded by NNNN`; date is `YYYY-MM-DD`.
- **Context**: the problem and the constraints that force a choice. Facts only; cite sources.
- **Decision**: what we chose, in one paragraph, starting "We will".
- **Consequences**: what gets easier, what gets harder, what we must now do. Include the negatives.
- **Alternatives**: every option seriously considered and why it lost. Each one links to the evidence
  (docs, repo, benchmark, paper). An alternative without a link is an opinion.

## Progress log
`docs/progress.md` is append-only and written by `/step-done`. Add new entries at the end and leave past
entries as they are: other sessions and the SessionStart hook read them as the record of what happened.
