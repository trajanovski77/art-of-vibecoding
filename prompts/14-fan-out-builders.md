Change of plan for wave 1. The owner is away and no new sessions can be opened, so you'll run the nine
new packages as your own background subagents, each in its own git worktree. The existing Builder
(S0) has already started P3 and the vertical slice as planned.

<task>
Launch P1, P2, P4-core, P4-rest, P5, P7, P8, P9 and P10 now as background subagents: the Agent tool,
run in the background, with worktree isolation. Give each the model from docs/launch/wave-1.md: opus
for P4-core, P5 and P7, sonnet for the rest.

Brief each one with its prompt file in docs/launch/prompts/, plus these three adjustments:
- Its worktree already exists. Rename the branch first (`git branch -m <branch named in the prompt
  file>`), then start the way the prompt file says.
- Where the prompt file says to message the desk, put that report in the final response instead.
  P4-core should send its interim message with SendMessage to "main" when CHOICE-text boots with
  Macedonian strings.
- Commit on the package branch and run the checkpoint step as the prompt file says, but never merge
  into main.

As you launch them, record each agent's id, package, model, branch and worktree path in
docs/launch/wave-1-agents.md (no commit needed). The file is how builders get resumed after a
usage-limit stop, or after your own context is reset.
</task>

<as_they_finish>
- Review each one with the wave-1 review protocol, using an Opus reviewer subagent for Sonnet
  packages, and merge in the wave order.
- For a FIX verdict, resume the same builder with SendMessage to its agent id and the fixes file.
  Don't start a new one.
- When P4-core, P1 and P2, P7, or P5's first version merge, tell the Builder session
  (<builder-session-id>) directly with SendMessage, as the relay rules in
  wave-1.md say, and copy the desk.
- When both P4-core and P5's first version have merged, launch P6 the same way.
</as_they_finish>

<after_a_usage_limit>
All sessions stop when the 5-hour limit is reached. After the reset I'll message you. Then resume
every builder that hadn't finished, using SendMessage to its agent id: "You were stopped by the usage
limit. Orient from the repository (git status, git log -3, your prompt file) and continue."
</after_a_usage_limit>

Send me (the <desk-session>) a short message after the launch, with the agents file, and after each
merge, with the package, the verdict and the merge commit. Keep your own turns short between events;
the builders carry the work.
