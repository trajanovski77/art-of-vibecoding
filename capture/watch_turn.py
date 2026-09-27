#!/usr/bin/env python3
"""Watch a goldsets session transcript: screenshot when a human prompt lands and when the turn ends.

Usage: watch_turn.py <step-name> [--window-title SUBSTR] [--project-dir DIR] [--timeout SEC]
Exits after the turn ends (last assistant message has stop_reason end_turn and the file has been
quiet for 20 s), printing the transcript path and capture files. Designed to run in the background.
"""
import argparse, glob, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = None  # transcript folder under ~/.claude/projects/, set from --project-dir

def windows():
    out = subprocess.run(["swift", os.path.join(HERE, "winlist.swift")], capture_output=True, text=True).stdout
    rows = []
    for line in out.strip().splitlines():
        wid, size, *title = line.split("\t")
        w, h = size.split("x")
        rows.append((int(wid), int(w) * int(h), title[0] if title else ""))
    return rows

def shoot(name, title_sub):
    rows = windows()
    if title_sub:  # strict: never fall back to another window (privacy)
        pick = [r for r in rows if title_sub.lower() in r[2].lower()]
    else:
        pick = sorted(rows, key=lambda r: -r[1])
    if not pick:
        return f"skipped: no window titled {title_sub!r}"
    path = os.path.join(HERE, "app", f"{name}.png")
    subprocess.run(["screencapture", "-x", "-o", "-l", str(pick[0][0]), path])
    return path

def latest_jsonl(since, exclude=()):
    files = [f for f in glob.glob(os.path.join(PROJ, "*.jsonl")) if os.path.getmtime(f) >= since
             and not any(os.path.basename(f).startswith(x) for x in exclude)]
    return max(files, key=os.path.getmtime) if files else None

def last_state(path):
    human_seen, last_stop, n = False, None, 0
    for line in open(path):
        try:
            j = json.loads(line)
        except ValueError:
            continue
        n += 1
        if j.get("type") == "user":
            c = (j.get("message") or {}).get("content")
            is_result = isinstance(c, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c)
            if not is_result and (j.get("origin") or {}).get("kind") != "task-notification":
                human_seen, last_stop = True, None
        elif j.get("type") == "assistant":
            last_stop = j["message"].get("stop_reason")
    return human_seen, last_stop, n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step")
    ap.add_argument("--window-title", default="")
    ap.add_argument("--timeout", type=int, default=5400)
    ap.add_argument("--jsonl")
    ap.add_argument("--project-dir", help="transcript folder under ~/.claude/projects/ (needed without --jsonl)")
    ap.add_argument("--exclude", nargs="*", default=[], help="transcript id prefixes to ignore when auto-detecting")
    ap.add_argument("--started", action="store_true", help="the prompt already landed; only wait for the end")
    ap.add_argument("--wait-new", action="store_true", help="ignore the current end-of-turn; wait for new activity to end")
    a = ap.parse_args()
    global PROJ
    if a.project_dir:
        PROJ = os.path.expanduser(a.project_dir)
    elif not a.jsonl:
        ap.error("pass --project-dir or --jsonl")
    t0 = time.time()
    path, shots, prompt_shot = a.jsonl, [], a.started
    base_lines = 0
    if path:
        base_lines = last_state(path)[2]
    while time.time() - t0 < a.timeout:
        if not path:
            path = latest_jsonl(t0 - 5, a.exclude)
            if not path:
                time.sleep(3); continue
        human, stop, n = last_state(path)
        if human and n > base_lines and not prompt_shot:
            time.sleep(6)
            shots.append(shoot(f"{a.step}-a-prompt", a.window_title)); prompt_shot = True
        if prompt_shot and stop == "tool_use" and time.time() - os.path.getmtime(path) > 600:
            shots.append(shoot(f"{a.step}-waiting", a.window_title))
            print(json.dumps({"jsonl": path, "shots": shots, "waiting_on_user": True}))
            return 2
        if a.wait_new and n <= base_lines:
            time.sleep(4); continue
        if prompt_shot and stop == "end_turn":
            quiet_since = os.path.getmtime(path)
            if time.time() - quiet_since > 20:
                shots.append(shoot(f"{a.step}-b-result", a.window_title))
                print(json.dumps({"jsonl": path, "shots": shots, "minutes": round((time.time() - t0) / 60, 1)}))
                return 0
        time.sleep(4)
    print(json.dumps({"jsonl": path, "shots": shots, "timeout": True}))
    return 1

if __name__ == "__main__":
    sys.exit(main())
