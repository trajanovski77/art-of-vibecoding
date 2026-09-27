---
title: Add a wiki page
type: playbook
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [vault/CLAUDE.md, vault/index.md]
tags: [playbook, wiki]
---

# Add a wiki page

## When to use

A step created something a future session will ask about: a component, a contract, a decision, a recurring
idea, or a procedure. Usually during an ingest run by the `step-done` skill.

## Steps

1. Pick the folder by type (`components/`, `contracts/`, `decisions/`, `concepts/`, `playbooks/`) and name the
   file after the title. The folders are listed in the schema (`vault/CLAUDE.md:29-34`).
2. Write the six frontmatter keys; `sources` lists the repo paths you read, and each must exist.
3. Write the page in its shape, citing code as `<path>:<line>`, never copying it. Say whether it is built or
   planned.
4. Link it from at least one related page and list it in `vault/index.md` under its folder with a one-line
   summary. If it contradicts another source, add an entry on [[Documentation contradictions]].
5. Run `python3 scripts/vault_lint.py`. It must print `OK` and exit 0.

## Related

- [[Documentation contradictions]]: what to do when the new page disagrees with another source
