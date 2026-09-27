# Rescue prompts

Paste one of these when a session goes wrong. Both send it back to evidence before it changes anything.

## When a session loops

It keeps trying fixes, each one confident, none of them working.

```text
Stop. List what you know for certain, each with the file and line or command output that shows it.
Then list what you are assuming. Propose the smallest experiment that separates the two, run it, and
only then change code.
```

If the answer is still thin, the context is probably full of failed attempts: ask it to write the
certain facts and the open question to a file, `/clear`, and give the file to a fresh session.

## After an interruption

A usage limit, a crash or a closed laptop stopped a step halfway. The session's memory of where it stopped is
the least trustworthy thing it has. Generalized from [prompts/09](../prompts/09-resume-after-interruption.md),
which both sessions of the build received after a usage limit hit mid-step:

```text
You were interrupted partway through the last step, so your memory of where you stopped may be wrong.
Orient from the repository, not from memory: run `git status`, read the tail of docs/progress.md, and
look at the files your step was meant to produce.

Then finish the step: complete whatever the done-when still needs, run its checks and show their output,
commit only the files you own (by path, not `git add -A`: another session may be working in the same
tree), and record it with /step-done. Report what was already done, what you finished now, and anything
you could not verify.
```

## Before blaming anyone

When files appear that nobody asked for, or a change seems to come from "another session", trace it first:
file times, `git log`, and the transcripts of your own subagents.

```text
Before we fix this, find out where it came from. For each unexpected file or change, give the evidence of
its origin (modification time, commit, or the tool call that wrote it). Say "unknown" where you have none.
```
