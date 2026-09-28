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
| `.claude/skills/codex-orchestration/SKILL.md` | Splits work between Claude Code and Codex: Claude plans, owns all design/frontend and verifies; Codex critiques the plan read-only, then implements backend units with tests. The loop: plan, adversarial review, delegate one unit with a hard contract, tiered verify, integrate. | Different models fail differently, and the build loop moves onto a second quota. Another agent's green tick is a claim, not evidence, so the skill names the paths Claude always re-verifies. | Not used in this build (it was Claude-only); from my own projects in July and August. It is the "Claude plans, Codex critiques" slide. Needs the [Codex plugin](#the-skills-from-the-talk). |
| `.claude/skills/codex-orchestration/notes.md` | The running notes file the skill reads before every delegation and appends to after each one. | What worked and what Codex got wrong carries across sessions and projects. | The two example entries are the two lessons quoted in the talk, generalised. Replace them with your own. |

`codex-orchestration` is a personal skill: install it in `~/.claude/skills/` so it applies to every project,
then replace `<codex-model>`, `<frontend>` and `<backend>` with your own.

```bash
cp -R 05-skills/.claude/skills/codex-orchestration ~/.claude/skills/
```

## The skills from the talk

The "My skills, and why" slide listed the skills I use every day. The others are other people's work, so they
are linked here, not copied. Links, licences and install commands were checked on 28 September 2026.

| Skill | What it is for | Source (licence) | Install in Claude Code |
|---|---|---|---|
| **codex-orchestration** | Claude plans and owns the UI; Codex critiques and builds the backend. | This folder (Apache-2.0) | Copy it (above). It needs the Codex plugin: `/plugin marketplace add openai/codex-plugin-cc`, then `/plugin install codex@openai-codex`, then `/codex:setup` ([openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc), Apache-2.0) |
| **frontend-design** | A deliberate design direction instead of templated defaults. | Anthropic, [claude-plugins-official/plugins/frontend-design](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design) (Apache-2.0) | `/plugin install frontend-design@claude-plugins-official` |
| **ui-ux-pro-max** | Searchable design data (styles, palettes, font pairings, UX guidelines); gives UI work a direction alongside frontend-design. | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (MIT) | `/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill`, then `/plugin install ui-ux-pro-max@ui-ux-pro-max-skill` |
| **humanizer** | Removes AI-writing tells from text, based on Wikipedia's "Signs of AI writing". | [blader/humanizer](https://github.com/blader/humanizer) (MIT) | `/plugin marketplace add blader/humanizer`, then `/plugin install humanizer@humanizer`; or `npx skills add blader/humanizer --global` |
| **skill-creator** | Builds, tests and benchmarks skills; measures whether a description triggers. | Anthropic, [claude-plugins-official/plugins/skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator), also in [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/skill-creator) (Apache-2.0) | `/plugin install skill-creator@claude-plugins-official` |
| **improve** | Audits a codebase with a strong model and writes self-contained plans for cheaper agents to execute. | shadcn, [shadcn/improve](https://github.com/shadcn/improve) (MIT) | `npx skills add shadcn/improve` |

Read a skill before you install it: it runs with your permissions, and the `allowed-tools` in its frontmatter
can pre-approve tools for itself. Start a new session after installing.

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
