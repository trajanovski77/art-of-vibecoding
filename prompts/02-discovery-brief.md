You're the architect for Vezilka Goldsets. Your first job is to understand the problem well
enough that the architecture almost writes itself, so for now we design nothing.

<situation>
EuroEval is the leaderboard European LLM teams use to compare models per language. Macedonian
has an open "help wanted" language request there, but no evaluation data. VEZILKA, North
Macedonia's national AI effort, wants to close that gap: take established English benchmarks,
machine-translate them upstream, and have Macedonian volunteers validate, correct and label them
until they are gold sets EuroEval can accept. The same data becomes train/val/test splits for
fine-tuning our own models. The volunteers are linguists, teachers and students, not engineers.
The candidate benchmarks are listed in @data/benchmark-catalogue.xlsx.
</situation>

<do_not_act_before_instructions>
Don't choose a stack, draw diagrams or write code in this step. Read the catalogue and the repo
conventions (@CLAUDE.md), then interview me.
</do_not_act_before_instructions>

<interview>
Ask only questions whose answers would change the architecture or the scope, at most eight, one
topic each, each with 2–4 concrete options and your recommended default. Write them as a
numbered list in your reply, in a single round, so I can answer them together in one message.
Skip anything you can reasonably infer; state those inferences instead so I can correct them.
</interview>

After my answers, write docs/BRIEF.md: the problem in one paragraph, who the users are and what
each needs to get done, constraints, success measures we could check in a month, explicit
non-goals, the biggest risks, and the open questions that research must settle next. Write it
for someone joining the project tomorrow, in plain prose with short sections.
