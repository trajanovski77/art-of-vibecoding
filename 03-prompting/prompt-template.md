<context>
<Who this is for and what exists right now: the project in two sentences, what earlier steps produced,
and why this task matters. Name the documents to read by path; for long ones, put them in <documents>.>
</context>

<documents>
<@path/to/long/input.md, one per line. Long inputs go before the task: the request reads better after them.>
</documents>

<task>
<One observable outcome, in one or two sentences. What exists when you are done that doesn't exist now.>
</task>

<constraints>
- <What to do, with the reason: "Edit only the files package P3 owns; another session is editing docs/ now.">
- <Scope: "Keep it as small as the spec allows; add no flags or abstractions it doesn't ask for.">
- <Where state goes: "Write findings to docs/reviews/<name>.md so the next session can pick them up.">
</constraints>

<done_when>
<Checks it will run and show you: literal commands and the output they must print. For UI, the screens to
capture and what a first-time user should see on them.>
</done_when>

<report>
<The shape of the answer: a verdict line first, then pass/fail counts, one line per changed file, anything
it could not verify, and anything it needs from files it doesn't own.>
</report>
