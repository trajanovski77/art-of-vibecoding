# Codex steering notes

Running memory for delegating to Codex, across projects. **Read before the first delegation of a session;
append after each significant one.** Governed by `SKILL.md` section 4. Keep it terse, dated, honest. Tag each
entry with the project so cross-project lessons stay separable.

Format per entry:

```
## [YYYY-MM-DD] <project> — <feature / unit delegated>
- Prompt/steering that worked:
- What Codex got wrong (and the correction):
- Reusable contract pattern:
```

The two entries below are generalised from the notes quoted in the talk. Replace them with your own.

---

## [YYYY-MM-DD] <project> — read-only plan critique before implementing
- Steering that worked: a `--fresh` read-only critique with a focus block listing the exact suspicion areas,
  and an output contract demanding file:line, failure scenario and fix per risk, verdict first.
- What it caught: an existing check used a strict `<`, so the new rule, as planned, would never fire.
- Reusable pattern: state the existing semantics the new code must preserve in the contract.

## [YYYY-MM-DD] <project> — backend unit with tests
- What Codex got wrong: it reported "12 passed" alongside 117 connection errors. Its sandbox could not reach
  the local database, so most tests never ran.
- Correction: re-run the touched suite on the real environment and read the whole output, not the summary line.
- Reusable pattern: in the delegation, require Codex to report errors and skips separately from passes.
