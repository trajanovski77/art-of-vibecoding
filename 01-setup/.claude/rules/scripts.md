---
paths:
  - "scripts/**"
---

# Script rules

- Standard-library Python 3 first. Add a third-party dependency only when the standard library cannot do
  the job, and record the reason in the script's docstring: every dependency is something a fresh
  session, a CI runner and a teammate's laptop must install.
- Every script runs with `--help` (use `argparse`): purpose, arguments, one example. `--help` exits 0
  and touches nothing, so any session can learn what a script does without reading it.
- Check `python3 scripts/<name>.py --help` before committing.
- Fail loudly: a clear message on stderr and a non-zero exit code. A silent failure looks like success to
  the next command and to the model reading its output.
- Read secrets from environment variables named in `.env.example`. Keep them out of code and output.
