Before we design anything, find out what already exists. The cheapest code is the code we don't
write, and a volunteer platform has well-known hard parts (roles, review, agreement, exports)
that other teams may have solved already.

<documents>
@docs/BRIEF.md
@research/LAYOUTS.md  (being written in parallel by another session; read it if it exists)
</documents>

<questions>
1. What exactly does EuroEval need to accept a new language and a new dataset: task types, the
   column schema per task, split names and sizes, length limits, licence expectations, and the
   contribution process? Is Macedonian already partly present?
2. Which open-source annotation tools could we adopt or adapt instead of building: include
   Label Studio, Argilla, Potato, doccano, INCEpTION and anything newer you find? Judge each
   against the brief, not in general: roles and review workflow, inter-annotator agreement,
   Macedonian UI, Google or passwordless login, the annotation jobs our layouts need, export with
   train/val/test splits, licence, and whether it is still maintained. Separate what the free
   edition does from what is paid-only.
3. What Macedonian datasets already exist for each EuroEval task, with licence and size?
4. What do we already own? Our team open-sourced a Django + Next.js volunteer platform at
   <path-to-open-source-platform>; read its CLAUDE.md files and note which parts (auth,
   internationalisation, task leasing, admin review, deployment) we could reuse.
</questions>

<how>
Dispatch one researcher subagent per question, in parallel. Give each the brief, its question,
and this output contract: findings as a table, every claim with a URL, a line on what could not
be verified, under 1,500 words. Local reading (question 4) goes to the explorer. While they run,
don't research the same topics yourself. When they return, check any claim that decides the
outcome against its source before relying on it; subagents can be confidently wrong.
</how>

<deliverables>
- research/RESEARCH.md: the four answers, merged and de-duplicated, with sources.
- docs/adr/0001-adopt-adapt-or-build.md: the decision (adopt a tool, adapt one, or build on our
  own platform), the evidence, the alternatives with why they lost, and what we would borrow from
  each even if we don't use it.
</deliverables>

Scale the effort to the question: a table and a decision, not a literature review.
