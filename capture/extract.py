#!/usr/bin/env python3
"""Turn Claude Code session transcripts (JSONL) into per-prompt step records for slides.

Usage: extract.py <session.jsonl> [--out steps/NN.json] [--since ISO] [--until ISO] [--label NAME]

For every prompt (a text user turn that isn't a tool result) it records: verbatim text (redacted),
who sent it (human / another session / system), the models that answered, summed token usage
split by model (subagent transcripts included), tool calls by name, wall time, and the final
assistant text. Each record keeps the transcript path + line number it came from, so every card
on a slide can be traced back to the source.
"""
import argparse, collections, glob, json, os, re, sys

REDACTIONS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "<email>"),
    (re.compile(r"hf_[A-Za-z0-9]{20,}"), "<hf-token>"),
    (re.compile(r"GOCSPX-[A-Za-z0-9_-]{10,}"), "<google-secret>"),
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}"), "<api-key>"),
    (re.compile(r"AIza[0-9A-Za-z_-]{30,}"), "<google-key>"),
    (re.compile(r"ya29\.[0-9A-Za-z_-]{20,}"), "<oauth-token>"),
]

def redact(s):
    for rx, rep in REDACTIONS:
        s = rx.sub(rep, s)
    return s

def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""

def is_tool_result(content):
    return isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content)

def usage_add(acc, model, u):
    if not u:
        return
    a = acc[model]
    a["input"] += u.get("input_tokens", 0) or 0
    a["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
    a["cache_write"] += u.get("cache_creation_input_tokens", 0) or 0
    a["output"] += u.get("output_tokens", 0) or 0
    a["thinking"] += (u.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0
    a["calls"] += 1

def new_acc():
    return collections.defaultdict(lambda: collections.Counter())

def subagent_usage(session_path, since, until):
    """Usage of subagents spawned by this session within [since, until]."""
    acc = new_acc()
    base = session_path[:-len(".jsonl")]
    for p in glob.glob(os.path.join(base, "subagents", "*.jsonl")):
        for line in open(p):
            try:
                j = json.loads(line)
            except ValueError:
                continue
            if j.get("type") != "assistant":
                continue
            ts = j.get("timestamp", "")
            if since and ts < since or until and ts > until:
                continue
            m = j["message"]
            usage_add(acc, m.get("model", "?"), m.get("usage"))
    return acc

def extract(path, since=None, until=None):
    rows = [json.loads(l) for l in open(path)]
    steps, cur = [], None
    for i, j in enumerate(rows):
        t = j.get("type")
        ts = j.get("timestamp", "")
        if (since and ts and ts < since) or (until and ts and ts > until):
            continue
        if t == "user":
            c = j["message"].get("content")
            if is_tool_result(c) or j.get("isMeta"):
                continue
            origin = (j.get("origin") or {}).get("kind", "unknown")
            if origin == "task-notification":
                continue
            txt = text_of(c).strip()
            if not txt:
                continue
            cur = {"source": {"file": path, "line": i + 1}, "sent_by": origin,
                   "prompt": redact(txt), "started": ts, "ended": ts,
                   "models": collections.Counter(), "usage": new_acc(),
                   "tools": collections.Counter(), "final_text": "",
                   "permission_mode": j.get("permissionMode")}
            steps.append(cur)
        elif t == "assistant" and cur is not None:
            m = j["message"]
            model = m.get("model", "?")
            cur["models"][model] += 1
            usage_add(cur["usage"], model, m.get("usage"))
            cur["ended"] = ts
            cur["effort"] = j.get("effort") or cur.get("effort")
            for b in m.get("content", []):
                if b.get("type") == "tool_use":
                    cur["tools"][b.get("name")] += 1
                elif b.get("type") == "text" and b.get("text", "").strip():
                    cur["final_text"] = redact(b["text"].strip())
    for s in steps:
        sub = subagent_usage(path, s["started"], s["ended"])
        s["subagent_usage"] = {k: dict(v) for k, v in sub.items()}
        s["usage"] = {k: dict(v) for k, v in s["usage"].items()}
        s["models"] = dict(s["models"])
        s["tools"] = dict(s["tools"])
    return steps

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl")
    ap.add_argument("--out")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    steps = extract(a.jsonl, a.since, a.until)
    doc = {"label": a.label, "session": os.path.basename(a.jsonl), "steps": steps}
    out = json.dumps(doc, indent=1, ensure_ascii=False)
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        open(a.out, "w").write(out)
        print(f"{len(steps)} prompts -> {a.out}")
    else:
        print(out)

if __name__ == "__main__":
    main()
