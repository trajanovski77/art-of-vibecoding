# 05 · Skills: procedures the model loads on demand

"If you corrected the same thing twice, it's a skill." A skill is a folder with a `SKILL.md`: a description
that tells Claude when to use it, and instructions it loads only when needed. CLAUDE.md is paid for on every
call; a skill costs a line in the skill listing until it runs.

Copy into your project:

```bash
mkdir -p <your-repo>/.claude/skills && cp -R 05-skills/.claude/skills/step-done <your-repo>/.claude/skills/
```

Start a new session, then type `/step-done <short title>` when a step is complete and verified.

## What is in this folder

| File | What it does | Why it exists | Used in the build |
|---|---|---|---|
| `.claude/skills/step-done/SKILL.md` | Closes a step: checks it was verified, appends a 12-line entry to `docs/progress.md`, ingests the step into `vault/` if the repo has a wiki, commits only this step's files by pathspec, tags the next free `step-NN`. | Parallel sessions share one working tree and one tag namespace. Without a fixed procedure, someone runs `git add -A` and commits another session's half-finished work, or two sessions take the same step number. | Created at step 01 ([prompts/01](../prompts/01-setup-brief.md), deliverable 6) as `checkpoint`; extended with the wiki ingest at step 09 ([prompts/10](../prompts/10-map-the-codebase-llm-wiki.md), task 4). It closed every step of the build. |

**Why `step-done` and not `checkpoint`.** In the build the skill was called `checkpoint`. The
[commands reference](https://code.claude.com/docs/en/commands) lists `/checkpoint` as an alias of the built-in
`/rewind`, and once, early in the build, a session's Skill tool refused to run it for that reason (later the
same skill ran normally). A template should not depend on which one wins, so this one uses a name nothing
else claims. [prompts/09](../prompts/09-resume-after-interruption.md) refers to it as "step-done/checkpoint".

## The frontmatter, field by field

| Field | Value here | Why |
|---|---|---|
| `name` | `step-done` | The display name. The command itself comes from the folder name, `.claude/skills/step-done/`. |
| `description` | What it does, then "Run only when the user or a prompt explicitly asks" | Claude decides when to use a skill from its description, so the limit on when goes here. |
| `argument-hint` | `[short step title]` | Shown in the `/` menu; the text arrives in the skill as `$ARGUMENTS`. |
| `allowed-tools` | git read, add, commit and tag; `date`; the wiki linter; `Read`; edits to `docs/progress.md` and `vault/**` | Pre-approves exactly what the procedure needs, for the turn that runs it. It does not restrict other tools: the skill text and the guard hook do that. Review the `allowed-tools` of any skill in a repo you clone, because a skill can grant itself broad access. |
| `disable-model-invocation` | not set | Claude must be able to run it when a prompt says "then run /step-done". Setting it to `true` would make the skill user-only. |

All fields are described in the [skills docs](https://code.claude.com/docs/en/skills#frontmatter-reference).

## From a repeated correction to a skill

Pick the lightest tool that makes the correction stick:

| You notice | Put it in | Because |
|---|---|---|
| A one-off preference for this task | The prompt | It only matters now. |
| The same mistake a second time, fixable in one line | CLAUDE.md, "Known pitfalls" (date, what went wrong, what to do instead) | One line, loaded every session, cheap. |
| A convention for one kind of file | `.claude/rules/<topic>.md` with `paths:` | Loads only when Claude reads a matching file. |
| A multi-step procedure you keep re-explaining | A skill | The steps, their order and their checks load only when the procedure runs. |
| Something that must happen every time, with no judgement | A hook (see [01-setup](../01-setup/README.md)) | A hook runs deterministically; a skill is still a request to the model. |

To write the skill:

1. **Write down the correction as you gave it**, and the failure it prevents. That failure becomes the reason
   in the skill; Claude generalises better from a reason than from a bare rule.
2. **Name the trigger.** Put "when to use" and "when not to" in the `description`, key use first: the listing
   truncates long descriptions.
3. **Write the procedure as numbered steps, each with its check** (a command and what it should show). A step
   without a check is where the model improvises.
4. **Give the procedure its stop conditions**: what to do when a check fails, when to stop and ask.
5. **Pre-approve only what the steps need** with `allowed-tools`, so the procedure runs without prompts but
   nothing else gets a free pass.
6. **Test it in a fresh session** twice: once by typing `/<name>`, once by asking for the task in plain words to
   see whether Claude picks the skill up on its own. Fix the description if it doesn't.
7. **Keep `SKILL.md` under 500 lines**; move reference material into files next to it and link them.

Two more options the docs describe, useful once the basics work: `` !`command` `` in the skill body runs a
command first and pastes its output into the skill (live data instead of instructions to fetch it), and
`context: fork` runs the skill in a subagent with its own context. See
[inject dynamic context](https://code.claude.com/docs/en/skills#inject-dynamic-context) and
[run skills in a subagent](https://code.claude.com/docs/en/skills#run-skills-in-a-subagent).
