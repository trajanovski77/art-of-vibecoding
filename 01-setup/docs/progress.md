# Progress log

Append-only, newest last. Written by `/step-done` (`.claude/skills/step-done/SKILL.md`).
The SessionStart hook prints the last 15 lines, so keep each entry to 12 lines or fewer.
Each entry has this shape:

    ## step-NN (YYYY-MM-DD): <title>
    - **Changed:** <files and behaviour, one or two lines>
    - **Verified:** <commands run and what they showed; "not verified" and why, if so>
    - **Next:** <the next step, concrete enough for a fresh session to start on>
