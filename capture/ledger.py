#!/usr/bin/env python3
"""Token ledger for every Claude Code session in one project: usage per session, role and model.

Usage: ledger.py PROJECT_DIR [--names id8=Label ...] [--json]
PROJECT_DIR is a transcript folder under ~/.claude/projects/ (required). Subagent transcripts
(<session>/subagents/*.jsonl) are counted separately as role "sub".
"""
import collections, glob, json, os, sys

args = sys.argv[1:]
if not args or args[0] in ("-h", "--help") or args[0].startswith("--"):
    print(__doc__)
    sys.exit(0 if args and args[0] in ("-h", "--help") else 2)
proj = os.path.expanduser(args[0])
names = {}
if "--names" in args:
    for kv in args[args.index("--names") + 1:]:
        if kv.startswith("--"):
            break
        k, v = kv.split("=", 1)
        names[k] = v

tot = collections.defaultdict(collections.Counter)
for main in glob.glob(os.path.join(proj, "*.jsonl")):
    sid = os.path.basename(main)[:8]
    label = names.get(sid, sid)
    files = [(main, "main")] + [(f, "sub") for f in glob.glob(main[:-6] + "/subagents/*.jsonl")]
    for f, role in files:
        for line in open(f):
            try:
                j = json.loads(line)
            except ValueError:
                continue
            if j.get("type") != "assistant":
                continue
            m = j["message"]
            u = m.get("usage") or {}
            c = tot[(label, role, m.get("model", "?"))]
            c["calls"] += 1
            c["output"] += u.get("output_tokens", 0) or 0
            c["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
            c["cache_write"] += u.get("cache_creation_input_tokens", 0) or 0
            c["input"] += u.get("input_tokens", 0) or 0

if "--json" in args:
    print(json.dumps([{"session": k[0], "role": k[1], "model": k[2], **v} for k, v in sorted(tot.items())], indent=1))
else:
    for (label, role, model), v in sorted(tot.items()):
        print(f"{label:<26} {role:<4} {model:<18} calls={v['calls']:>5} out={v['output']:>9,} "
              f"cache_read={v['cache_read']:>12,} cache_write={v['cache_write']:>10,}")
