<context>
Vezilka Goldsets will ask volunteers to review benchmark items one at a time. Before we can
design screens, we need to know what kinds of items actually exist. The 83 candidate benchmarks
are in @data/benchmark-catalogue.xlsx (name, category, link, paper). The links were collected by
hand, so expect some to be blank, moved, gated or pointing at the wrong page.
</context>

<task>
Look at real rows from every benchmark and derive the smallest set of review layouts that covers
all of them. A layout here has two parts: what the reviewer reads (stimulus blocks such as a
prompt, a long passage, a table, code, images, a conversation) and how the reviewer answers
(answer widgets such as single choice, multi-select, label, span highlight, rating, pairwise
preference, free text with accepted aliases). Many benchmarks will share a widget but store their
data differently, so also catalogue how options and gold answers are encoded.
</task>

<approach>
1. Write scripts/sample_hf.py that, for a Hugging Face dataset id, calls the datasets-server API
   (/splits, /first-rows, /size) and saves 4 rows, the features, the config list and row counts to
   research/samples/<name>.json. Run it for every row of the catalogue.
2. For suites whose configs have different schemas (for example GLUE, SuperGLUE, BIG-Bench,
   LegalBench, ETHICS), sample enough configs to see each distinct schema.
3. For rows that fail to resolve, dispatch researcher subagents in parallel, about ten rows each,
   to find a preview-enabled source. Each returns only: dataset, repo id used, why the original
   failed, and a URL as evidence. Record every substitution; nothing is silently replaced.
4. Only then classify. Base every classification on the saved samples, not on what you remember
   about the benchmark, and quote the field names you relied on.
</approach>

<use_parallel_tool_calls>
Sampling calls and subagent dispatches are independent of each other; issue them in parallel.
</use_parallel_tool_calls>

<deliverables>
- research/LAYOUTS.md: stimulus blocks and answer widgets, each with a definition, how many
  benchmarks use it as their primary widget, examples, and the traps it hides; a table of every
  distinct option/gold encoding with where it occurs; a proposed canonical item shape that all of
  them can be converted into; and the cross-cutting requirements you discover along the way
  (languages and scripts, offsets, item sizes, volumes).
- research/layout_map.csv: one row per benchmark with its layouts, stimulus blocks, gold encoding,
  row count and resolved source.
- research/link-health.md: every link that didn't resolve as written and what replaced it.
</deliverables>

<done_when>
Every one of the 83 benchmarks has a saved sample or a documented reason it couldn't be sampled,
and every row in layout_map.csv points to its sample file. Show the counts.
</done_when>

When you finish, run /checkpoint.
