<documents>
<idea_file source="https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f">
<paste the full text of https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f here>
</idea_file>
</documents>

<context>
Several sessions build this repository over several days, and every fresh session spends its first
tokens rediscovering the same facts by re-reading files. Instantiate the idea file above for this
codebase, so that a session starts from a map, and so that anyone implementing a feature months from
now can ask the wiki where things are and why they are that way before touching code.
</context>

<mapping>
- Raw sources = the repository itself (code, docs/, research/, ADRs, configs). Wiki operations never
  modify them. Reference code by path and line; never copy source into the wiki.
- Wiki = vault/: index.md, log.md, and wiki/ with components/, contracts/, decisions/, layouts/,
  benchmarks/, concepts/ and playbooks/.
- Schema = vault/CLAUDE.md. Follow the conventions of the vault I already use: YAML frontmatter with
  title, type, created, updated, sources and tags on every page; Obsidian wikilinks by page title; one
  topic per file; a "Current state" section at the top of index.md that orients a new reader in under
  thirty lines.
</mapping>

<tasks>
1. Write vault/CLAUDE.md: layout, page types, ingest/query/lint as they apply to a codebase, and the
   rule that when the wiki and the code disagree, the code wins and the wiki gets fixed.
2. Ingest everything committed so far: one page per component, data contract, ADR, and layout, a page
   for each EuroEval-first benchmark, and concept pages for the ideas that recur across documents.
3. Write three playbooks a future implementer will need: add a benchmark, add a layout, run a campaign.
4. Wire it into the workflow: the SessionStart hook also prints the index's "Current state" (only that
   section, to keep every session's context small), and the step-done skill ingests the step's changes
   and appends to log.md.
5. Run a lint pass and report orphans, contradictions and pages whose code references no longer resolve.
</tasks>

<done_when>
scripts/vault_lint.py exits 0: every page has frontmatter and at least one inbound link, index.md lists
every page, and every path:line reference resolves. Show its output and the page count per folder.
</done_when>
