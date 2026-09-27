import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from extract import extract, redact

def test_redaction():
    # fake addresses and credentials are assembled at runtime so this file holds nothing secret scanners flag
    fake = "abcdefghijklmnopqrstuvwxyz"
    s = f"mail {'jane.doe' + '@' + 'gmail.com'} key {'hf' + '_' + fake}12 {'GOCSPX' + '-' + fake[:12]} {'sk' + '-ant-api03-' + fake}"
    r = redact(s)
    assert "@gmail.com" not in r and "hf_abc" not in r and "GOCSPX-abc" not in r and "sk-ant" not in r, r

def test_extract_minimal():
    rows = [
        {"type": "user", "timestamp": "2026-09-24T10:00:00Z", "origin": {"kind": "human"},
         "message": {"role": "user", "content": "Build it. Contact me at " + "a" + "@" + "b.co"}},
        {"type": "assistant", "timestamp": "2026-09-24T10:00:05Z",
         "message": {"model": "claude-sonnet-5", "content": [{"type": "tool_use", "name": "Read", "input": {}}],
                     "usage": {"input_tokens": 10, "cache_read_input_tokens": 100, "cache_creation_input_tokens": 5, "output_tokens": 7}}},
        {"type": "user", "timestamp": "2026-09-24T10:00:06Z",
         "message": {"role": "user", "content": [{"type": "tool_result", "content": "x"}]}},
        {"type": "assistant", "timestamp": "2026-09-24T10:00:09Z",
         "message": {"model": "claude-sonnet-5", "content": [{"type": "text", "text": "Done."}],
                     "usage": {"input_tokens": 1, "output_tokens": 3}}},
    ]
    d = tempfile.mkdtemp()
    p = os.path.join(d, "s.jsonl")
    open(p, "w").write("\n".join(json.dumps(r) for r in rows))
    steps = extract(p)
    assert len(steps) == 1
    s = steps[0]
    assert "<email>" in s["prompt"] and s["tools"] == {"Read": 1} and s["final_text"] == "Done."
    u = s["usage"]["claude-sonnet-5"]
    assert u["cache_read"] == 100 and u["output"] == 10 and u["calls"] == 2

if __name__ == "__main__":
    test_redaction(); test_extract_minimal(); print("extract tests: 2 passed")
