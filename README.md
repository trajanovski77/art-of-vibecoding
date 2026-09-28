# The Art of Vibecoding: starter repo

Templates, prompts and tools from the 45-minute Claude Code workshop *The Art of Vibecoding*
(26 September 2026). The talk follows one real build, **Vezilka Goldsets**: a web app where volunteers turn
machine-translated English benchmarks into human-validated Macedonian evaluation sets. Claude Code sessions
built it over two days: an orchestrator/architect on Fable, and builder sessions on Opus and Sonnet.

Each module folder holds files you can copy into your own repo and adapt in minutes, with a README that says
what every file is for, why it exists, and which step of the build used it. [TIPS.md](TIPS.md) collects the
talk's tips by module.

## Quick start (5 minutes)

1. Copy the setup into your project:

   ```bash
   cp -R 01-setup/.claude 01-setup/CLAUDE.md <your-repo>/
   mkdir -p <your-repo>/docs/adr <your-repo>/.claude/skills
   cp 01-setup/docs/adr/0000-template.md <your-repo>/docs/adr/
   cp -n 01-setup/docs/progress.md <your-repo>/docs/
   cp -R 05-skills/.claude/skills/step-done <your-repo>/.claude/skills/
   ```

   If your repo already has a `CLAUDE.md` or `.claude/settings.json`, merge them by hand instead: `cp` overwrites.

2. Adapt three things:
   - **`CLAUDE.md`**: replace the `<placeholders>`: what the project is, where things live, how to run tests.
   - **`.claude/settings.json`**, `permissions.allow`: swap `Bash(pytest *)` and `Bash(python3 scripts/*)` for the
     commands your sessions run all the time.
   - **`.claude/rules/*.md`**: point each `paths:` list at your own folders.

3. Start a new Claude Code session in your repo (accept the folder-trust prompt). The first thing it receives
   is the orientation printed by the SessionStart hook. Ask Claude to run `cat .env` and watch it get blocked.
   Close your first verified step with `/step-done <title>`.

You need Claude Code, `git`, and `python3` 3.9 or newer on your PATH. The hooks use the standard library only.

## Modules, folders and prompt cards

| # | Module | Folder | Prompt cards (in [prompts/](prompts/)) |
|---|---|---|---|
| 1 | Setup | [01-setup/](01-setup/README.md): CLAUDE.md, settings, rules, three hooks, ADR template, progress log | [01 Setup brief](prompts/01-setup-brief.md) |
| 2 | Plan before coding | [02-plan/](02-plan/README.md): work package template, `features.json`, `init.sh` | [02 Discovery brief](prompts/02-discovery-brief.md), [03 Derive layouts](prompts/03-derive-layouts.md), [04 Search before build](prompts/04-search-before-build.md), [05 Architecture and work packages](prompts/05-architecture-and-work-packages.md), [06 Attack the plan](prompts/06-attack-the-plan.md), [13 Plan the parallel wave](prompts/13-plan-the-parallel-wave.md) |
| 3 | Prompting | [03-prompting/](03-prompting/README.md): prompt anatomy, one annotated prompt, frontend brief | [08 Brand from live sites](prompts/08-brand-from-live-sites.md), [11 Builder work package](prompts/11-builder-work-package.md) (annotated) |
| 4 | Context and tokens | [04-context/](04-context/README.md): LLM wiki (`vault/`), linter, token ledger | [09 Resume after interruption](prompts/09-resume-after-interruption.md), [10 Map the codebase: LLM wiki](prompts/10-map-the-codebase-llm-wiki.md), [12 Review in a fresh session](prompts/12-review-in-a-fresh-session.md) |
| 5 | Skills | [05-skills/](05-skills/README.md): the `step-done` skill, from correction to skill, the `codex-orchestration` skill, and [links to every skill from the talk](05-skills/README.md#the-skills-from-the-talk) | [01 Setup brief](prompts/01-setup-brief.md) (deliverable 6), [10 Map the codebase](prompts/10-map-the-codebase-llm-wiki.md) (task 4) |
| 6 | Agents and orchestration | [06-agents/](06-agents/README.md): reviewer, explorer and researcher subagents; roles; worktrees | [07 Orchestrator review](prompts/07-orchestrator-review.md), [11 Builder work package](prompts/11-builder-work-package.md), [13 Plan the parallel wave](prompts/13-plan-the-parallel-wave.md), [14 Fan out builders](prompts/14-fan-out-builders.md) |
| 7 | Verification and rescue | [07-verification/](07-verification/README.md): review prompt, rescue prompts | [07 Orchestrator review](prompts/07-orchestrator-review.md), [12 Review in a fresh session](prompts/12-review-in-a-fresh-session.md), [09 Resume after interruption](prompts/09-resume-after-interruption.md) |

The other folders: [prompts/](prompts/) holds the fourteen prompt cards; [capture/](capture/README.md) holds the tools
used to measure and capture the build, including [`ledger.py`](capture/ledger.py) (tokens per session, see
[04-context](04-context/README.md)). The slide builders are not part of this repository.

## Models

The build used three tiers: **Fable** to plan, orchestrate and review, **Opus** to build anything touching
concurrency, security or data integrity and to review, and **Sonnet** for well-specified work, whose output a
stronger model always checked before the next step. The subagent templates use `opus` for review and `sonnet` for
exploration and research. Model names change monthly; the way to choose (difficulty, cost, latency, context) does not.

## A note on honesty

Every card in [prompts/](prompts/) is the text that was actually sent in the build. Cards with `{PLACEHOLDERS}`
([07](prompts/07-orchestrator-review.md)) are templates that were filled in for each step. Numbers in the READMEs
(tokens per call, findings, fixes) come from the build's session transcripts, progress log and review files.
Identifiers and local paths in the cards (session ids, folders on the builder's laptop) were replaced with
`<bracketed placeholders>`, and [prompts/10](prompts/10-map-the-codebase-llm-wiki.md) links to Karpathy's gist
instead of repeating it. The app repository itself is private. The templates here are generalized from its Claude Code setup: project
details replaced with `<placeholders>`, structure, comments and reasons kept.

Claude Code syntax in these templates (hook events and matchers, settings keys, `paths:` in rules, skill and
subagent frontmatter) was checked against [code.claude.com/docs](https://code.claude.com/docs) on 24 September
2026. If the docs and a template disagree, the docs win.

## Licence

Apache License 2.0, see [LICENSE](LICENSE). Potato, the annotation tool the build adopted, is GPL-3.0 and is not included here; Karpathy's LLM Wiki gist is linked, not copied.
