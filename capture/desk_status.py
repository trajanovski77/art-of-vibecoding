#!/usr/bin/env python3
"""One-line status per Claude Code session working on vezilka-goldsets (main folder and worktrees).

Reads the transcript JSONL files only (no API calls), so it is cheap to run on every desk heartbeat.
States:
  WORKING      last record is recent and the turn has not ended
  DONE         the last turn ended normally (end_turn); read its last text to route it
  LIMITED      the last assistant record is a rate_limit error ("You've hit your session limit")
  API_ERROR    another API error ended the turn
  STALLED      turn not ended and no new record for --stall minutes (possible permission prompt or hang)

Usage: desk_status.py [--hours 16] [--stall 20] [--json]
"""
import argparse, glob, json, os, time

ROOT = os.path.expanduser("~/.claude/projects")


def scan(path):
    cwd = branch = None
    last_ts, last_text, stop, err, err_text, n, model = "", "", None, None, "", 0, None
    for line in open(path, errors="replace"):
        try:
            j = json.loads(line)
        except ValueError:
            continue
        n += 1
        cwd = j.get("cwd") or cwd
        branch = j.get("gitBranch") or branch
        if j.get("timestamp"):
            last_ts = max(last_ts, j["timestamp"])
        t = j.get("type")
        if t == "user":
            c = (j.get("message") or {}).get("content")
            is_result = isinstance(c, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c)
            if not is_result and (j.get("origin") or {}).get("kind") != "task-notification":
                stop, err = None, None  # a new turn started
        elif t == "assistant":
            m = j.get("message") or {}
            if j.get("isApiErrorMessage"):
                err = j.get("error") or "api_error"
                c = m.get("content") or []
                err_text = c[0].get("text", "") if c and isinstance(c[0], dict) else ""
                stop = "error"
                continue
            model = m.get("model") or model
            stop = m.get("stop_reason")
            for b in m.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip():
                    last_text = b["text"].strip()
    return dict(cwd=cwd, branch=branch, last_ts=last_ts, last_text=last_text, stop=stop, err=err,
                err_text=err_text, records=n, model=model)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--hours", type=float, default=16)
    ap.add_argument("--stall", type=float, default=20, help="minutes without records before WORKING becomes STALLED")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--subagents", action="store_true", help="also list subagent transcripts (<session>/subagents/)")
    a = ap.parse_args()
    now = time.time()
    rows = []
    for d in glob.glob(os.path.join(ROOT, "*vezilka-goldsets*")):
        files = glob.glob(os.path.join(d, "*.jsonl"))
        if a.subagents:
            files += glob.glob(os.path.join(d, "*", "subagents", "*.jsonl"))
        for f in files:
            age = now - os.path.getmtime(f)
            if age > a.hours * 3600:
                continue
            s = scan(f)
            if s["err"] == "rate_limit":
                state = "LIMITED"
            elif s["err"]:
                state = "API_ERROR"
            elif s["stop"] == "end_turn":
                state = "DONE"
            elif age > a.stall * 60:
                state = "STALLED"
            else:
                state = "WORKING"
            sid = os.path.basename(f)[:8] if "/subagents/" not in f else "sub:" + os.path.basename(f)[6:14]
            meta = f[:-6] + ".meta.json"
            if os.path.exists(meta):
                try:
                    s["cwd"] = (json.load(open(meta)).get("description") or "")[:40] + " | " + (s["cwd"] or "")
                except ValueError:
                    pass
            s.update(id=sid, state=state, idle_min=round(age / 60, 1), path=f)
            rows.append(s)
    rows.sort(key=lambda r: r["last_ts"], reverse=True)
    if a.json:
        print(json.dumps(rows, indent=1))
        return
    for r in rows:
        where = (r["cwd"] or "?").replace(os.path.expanduser("~"), "~")
        tail = (r["err_text"] if r["err"] else r["last_text"]).replace("\n", " ")[:110]
        print(f"{r['state']:<9} {r['id']} idle={r['idle_min']:>6}m {str(r['model'])[7:]:<10} {r['branch'] or '-':<18} {where}\n          {tail}")


if __name__ == "__main__":
    main()
