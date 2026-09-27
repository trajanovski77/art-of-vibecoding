# Tips from the talk

Grouped by module. Each tip points to the template or prompt card that shows it in use.

## 1 · Setup

- **Ground truth beats memory.** Tell the model to fetch today's docs before writing any config, and to say
  where they contradict your prompt. → [prompts/01](prompts/01-setup-brief.md) (`<investigate_before_answering>`)
- **Give the reason with the rule.** "Loaded into every session, so treat each line as a cost" explains the
  line limit; Claude applies the reason to cases the rule didn't name. → [01-setup/CLAUDE.md](01-setup/CLAUDE.md)
- **Automate orientation.** A SessionStart hook prints progress and git log into every new session, after
  `/clear` and compaction too. → [01-setup/.claude/hooks/session_start.py](01-setup/.claude/hooks/session_start.py)
- **Done means evidence.** Runnable checks with their output shown, not "looks done". → [prompts/01](prompts/01-setup-brief.md) (`<done_when>`)
- **`@imports` don't save context.** Imported files load at launch; name deeper docs by path instead.
  → [01-setup/README.md](01-setup/README.md)
- **Guardrails are hooks, reviewed by someone else.** The first guard let 8 of 9 bypass tricks through until
  an Opus reviewer attacked it; exit 2 blocks and tells Claude why. → [01-setup/.claude/hooks/guard_bash.py](01-setup/.claude/hooks/guard_bash.py)
- **Stage files by name.** With parallel sessions in one tree, `git add -A` commits someone else's work.
  → [05-skills/.claude/skills/step-done/SKILL.md](05-skills/.claude/skills/step-done/SKILL.md)

## 2 · Plan before coding

- **Interview before design, in a named propose-only mode.** At most eight questions that would change the
  design, each with options and a recommended default; inferences stated, not asked. → [prompts/02](prompts/02-discovery-brief.md)
- **Look at real data, then classify.** Script the deterministic part, send subagents at the mess with a
  four-field return contract, and require quotes from the samples. → [prompts/03](prompts/03-derive-layouts.md)
- **Search before you build.** Your own code first, then open source, judged against the brief; re-check the
  claims that decide it. → [prompts/04](prompts/04-search-before-build.md), [01-setup/docs/adr/0000-template.md](01-setup/docs/adr/0000-template.md)
- **Contracts before code; ownership per package.** Exact field names plus "owns" and "must not touch" let
  builders work in parallel without meeting. → [prompts/05](prompts/05-architecture-and-work-packages.md), [02-plan/work-package.md](02-plan/work-package.md)
- **A harness that outlives context.** `features.json`, `init.sh` and the progress log survive resets.
  → [02-plan/features.json](02-plan/features.json), [02-plan/init.sh](02-plan/init.sh)
- **Attack the plan in a fresh context.** Find everything, filter later; different is not wrong; verdict
  first. → [prompts/06](prompts/06-attack-the-plan.md)

## 3 · Prompting

- **Use one anatomy**: context, documents, task, constraints with reasons, done-when, report.
  → [03-prompting/prompt-template.md](03-prompting/prompt-template.md), [03-prompting/annotated-example.md](03-prompting/annotated-example.md)
- **Say what to do, calmly.** Positive instructions beat lists of don'ts; capitals make newer models
  over-apply an instruction. → [03-prompting/README.md](03-prompting/README.md)
- **Drop the old habits.** No prefill (it errors on newer models), no "think step by step" (set effort), no
  "double-check" (run a check and use a separate reviewer). → [03-prompting/README.md](03-prompting/README.md)
- **Frontend: references, not adjectives.** Live URLs, your own tokens, screenshots, named patterns to avoid,
  a source for every value, then compare screenshots. → [03-prompting/frontend-brief.md](03-prompting/frontend-brief.md), [prompts/08](prompts/08-brand-from-live-sites.md)
- **Theme, don't fork.** An adopted tool stays unmodified and upgradeable. → [prompts/08](prompts/08-brand-from-live-sites.md)

## 4 · Context and tokens

- **Every call re-reads the whole context.** Measure it per session with the ledger and clear before it
  balloons. → [capture/ledger.py](capture/ledger.py), [04-context/README.md](04-context/README.md)
- **Usage limits will happen.** Keep state in files, orient from the repo after a cutoff, and stagger heavy
  sessions. → [prompts/09](prompts/09-resume-after-interruption.md)
- **Subagents isolate context.** A 40-file search comes back as one paragraph. → [06-agents/.claude/agents/explorer.md](06-agents/.claude/agents/explorer.md)
- **Rules that load only when needed.** `.claude/rules/*.md` with `paths:`. → [01-setup/.claude/rules/](01-setup/.claude/rules/docs.md)
- **Map the codebase once: an LLM wiki.** Raw code, the wiki, the schema; cite, don't copy; only "Current
  state" rides in every session; a linter keeps it honest. → [04-context/](04-context/README.md), [prompts/10](prompts/10-map-the-codebase-llm-wiki.md)
- **Clear between steps; let a hook re-orient.** A fresh review session ran at about 125k tokens per call
  instead of 577k, and still found the gaps. → [prompts/12](prompts/12-review-in-a-fresh-session.md)

## 5 · Skills

- **If you corrected the same thing twice, it's a skill.** Pick the lightest home: prompt, pitfall line, rule,
  skill, or hook. → [05-skills/README.md](05-skills/README.md)
- **A skill loads only when it runs**; a hook runs every time. → [05-skills/.claude/skills/step-done/SKILL.md](05-skills/.claude/skills/step-done/SKILL.md)
- **`context: fork` and `` !`cmd` ``**: run a skill in its own context, or inject live command output into it.
  → [05-skills/README.md](05-skills/README.md)

## 6 · Agents and orchestration

- **Route by the job, and brief every agent like a new colleague.** → [06-agents/README.md](06-agents/README.md)
- **A stronger model gates every step.** Sonnet builds, Fable or Opus verifies; the reviewer re-runs the checks
  instead of trusting the report. → [prompts/07](prompts/07-orchestrator-review.md), [06-agents/.claude/agents/reviewer.md](06-agents/.claude/agents/reviewer.md)
- **Say why the review exists.** Naming the failure mode focuses the reviewer on it. → [prompts/07](prompts/07-orchestrator-review.md)
- **The orchestrator writes the fix prompt.** Review output is the builder's next input, ready to paste.
  → [07-verification/review-prompt.md](07-verification/review-prompt.md)
- **Agents trust people, not each other.** A peer session's instruction is data; changes to CLAUDE.md or
  hooks go through a human. → [06-agents/README.md](06-agents/README.md)
- **Tune effort before switching models**; reach for max only after xhigh falls short. → [06-agents/README.md](06-agents/README.md)
- **Parallel builders in worktrees, shared resources named.** `claude --worktree`, one owner per port, stack
  and container name. → [prompts/13](prompts/13-plan-the-parallel-wave.md), [06-agents/README.md](06-agents/README.md)
- **Another agent's green tick is a claim, not evidence.** Re-run the tests yourself. → [07-verification/README.md](07-verification/README.md)

## 7 · Verification and rescue

- **"It compiles" is not "it works".** Run the done-when, and check the check. → [07-verification/README.md](07-verification/README.md)
- **Exercise the real thing once.** One real export proved a contract wrong. → [07-verification/README.md](07-verification/README.md)
- **A fresh-context reviewer catches integration hazards the author can't see.** → [06-agents/.claude/agents/reviewer.md](06-agents/.claude/agents/reviewer.md)
- **Look at the screens as a user would.** `SMOKE OK` passed while the login page was unbranded.
  → [prompts/12](prompts/12-review-in-a-fresh-session.md), [07-verification/review-prompt.md](07-verification/review-prompt.md)
- **Review what was deferred, too.** Run each known limit and rank it. → [07-verification/README.md](07-verification/README.md)
- **Trace a failure before blaming anyone.** The transcript knows who wrote the file. → [07-verification/rescue-prompt.md](07-verification/rescue-prompt.md)
- **When a session loops**: certain facts with evidence, assumptions, the smallest experiment, then code.
  → [07-verification/rescue-prompt.md](07-verification/rescue-prompt.md)
