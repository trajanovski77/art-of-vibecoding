# 03 · Prompting

Most prompts fail on context, not on wording. Every prompt in this build used the same anatomy, and every
card in [prompts/](../prompts/) is an example of it.

## What is in this folder

| File | What it is | Why it exists | Used in the build |
|---|---|---|---|
| `prompt-template.md` | A blank prompt in the anatomy below, with a note in each block on what goes there. | Start from the structure so you only have to think about the content. | Every card in `prompts/` follows it; [prompts/01](../prompts/01-setup-brief.md) and [prompts/05](../prompts/05-architecture-and-work-packages.md) are the longest examples. |
| `annotated-example.md` | [prompts/11](../prompts/11-builder-work-package.md), the builder's work-package prompt, verbatim, with a note under each block. | Shows why each block is there and what goes wrong without it. | It started the first work package (step 11). |
| `frontend-brief.md` | A frontend prompt built on references: live sites, your own tokens, screenshots, named patterns to avoid, a source for every value. | Adjectives get you the model's defaults; references get you your design. | Generalized from [prompts/08](../prompts/08-brand-from-live-sites.md), which themed the build's annotation tool (step 06). |

## The anatomy

```text
<context>     who it's for, what exists, and why the task matters
<documents>   long inputs, first
<task>        one observable outcome
<constraints> what to do, each with its reason
<done_when>   checks it will run and show you
<report>      the shape of the answer
```

- **Give reasons, not only rules.** "CLAUDE.md is loaded into every session, so treat each line as a cost"
  explains the line limit, and Claude applies the reason to cases the rule didn't name.
- **Say what to do.** "Write it in your report instead of editing that file" works better than a list of don'ts.
- **Use calm wording.** Capitals and "CRITICAL: YOU MUST" make newer models over-apply the instruction.
  Plain sentences, with emphasis on one line at most.
- **Put long documents first and the request last.** Quality improves when the question comes after the material.
- **Make done a check it can run.** A command and its expected output is the only reliable stop signal.
- **Point at today's docs instead of trusting memory.** Tools change faster than training data:
  [prompts/01](../prompts/01-setup-brief.md) opens by telling the model to fetch the current docs and to say where
  they contradict the prompt.
- **Name a propose-only mode when you want one.** "Don't choose a stack, draw diagrams or write code in this
  step; interview me" ([prompts/02](../prompts/02-discovery-brief.md)). Newer models take that literally.

## Habits the current guidance contradicts

| Habit | What works on today's models |
|---|---|
| "YOU MUST…" in capitals | Plain wording; emphasis on one line at most |
| More rules, more control | The smallest set of high-signal instructions, each with its reason |
| Prefilling the answer to force a format | Structured output or an output contract in `<report>`; prefill returns an error on Claude 4.6 and later models |
| "Think step by step" | Set the effort level on the session |
| "Double-check your work" | A runnable check, plus a separate reviewer in a fresh context |

Sources: [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices),
[Claude Code best practices](https://code.claude.com/docs/en/best-practices).

## Frontend: give references, not adjectives

"Make it modern and clean" or "avoid the AI look" gets you the model's defaults. Anthropic's
[Opus 5.5 prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5#frontend-design-defaults)
notes that a general instruction to avoid a generic look mostly swaps one default for another, and that
naming the specific patterns to avoid works. What worked in the build:

1. **Live URLs** of the sites the result should match: they are the source of truth.
2. **Your own tokens**: Tailwind config, CSS variables, the original logo files, for exact values.
3. **Screenshots** of the look you want, and of the look you don't.
4. **Patterns to avoid, named specifically**, extended after you see which defaults the first result used.
5. **Every value with its source**, a contrast check, then a screenshot of the result next to the reference.

No references yet? Name the defaults you don't want, look at what the first result used instead, and extend
the list. Or install a design skill. The brand prompt ([prompts/08](../prompts/08-brand-from-live-sites.md))
gave the reason too: recognisable branding is what makes a user trust a login page they have never seen.
