# capture: tools used to measure and record the build

These scripts read Claude Code's local session transcripts (`~/.claude/projects/<project-folder>/*.jsonl`).
They were written for the talk's build on macOS, not as a polished package. Only `ledger.py` is meant for
reuse; the others are kept to show how the numbers and screenshots were produced.

| File | What it does | Works outside the build? |
|---|---|---|
| [`ledger.py`](ledger.py) | Tokens per session, role (main or subagent) and model, from `message.usage`. See [04-context](../04-context/README.md#measure-your-own-sessions-captureledgerpy). | Yes. Pass your transcript folder: `python3 capture/ledger.py ~/.claude/projects/<your-project-folder>`. |
| [`extract.py`](extract.py) | One record per prompt in a transcript: redacted prompt text, models, tokens, tools, final answer. Tested by [`test_extract.py`](test_extract.py). | Yes, on any transcript file. Its redaction covers emails and a few token formats only. |
| [`desk_status.py`](desk_status.py) | One status line per running session (working, done, rate-limited, stalled). | Only for transcript folders whose name contains `vezilka-goldsets`; change the glob in `main()`. |
| [`watch_turn.py`](watch_turn.py), [`shot.sh`](shot.sh), [`winlist.swift`](winlist.swift) | Screenshot the Claude desktop app window when a prompt lands and when the turn ends, into `capture/app/`. | macOS only (`screencapture`, Swift). `watch_turn.py` needs `--project-dir` or `--jsonl`. |
| `app/*.png` | Window captures of the build's sessions, taken with the tools above. | Illustrations only. |

Transcripts hold everything a session saw, including file contents and command output. Keep them, and
anything generated from them (`capture/out/`), out of public repositories.

```bash
python3 -m pytest capture/test_extract.py -q     # or: python3 capture/test_extract.py
```
