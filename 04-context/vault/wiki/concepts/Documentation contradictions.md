---
title: Documentation contradictions
type: concept
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [vault/CLAUDE.md]
tags: [concept, wiki, quality]
---

# Documentation contradictions

Where two sources in the repository disagree (an ADR and the code, a plan and a contract, a README and a
config), the wiki records the disagreement here with both citations instead of silently picking a winner.
The owner of the sources fixes them; the next ingest moves the entry to Resolved. The rule behind it is in
the schema: when the wiki and the code disagree, the code wins (`vault/CLAUDE.md:18-20`).

## Open

- none

## Resolved

- none yet

<!-- Entry shape: - <YYYY-MM-DD> <what disagrees>: `<path>:<line>` says <x>; `<path>:<line>` says <y>. Owner: <who fixes it>.
     In the build this came from, the first lint pass found eight such contradictions in fresh design docs;
     all eight were fixed at their sources in the next step. -->

## Related

- [[Add a wiki page]]: where a new page goes and how it gets linked and linted
