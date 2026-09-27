#!/usr/bin/env bash
# <Project name> build harness. Starter from 02-plan: fill in the CONFIG block below.
#
#   ./init.sh check    verify the environment (tools, .env, features.json)
#   ./init.sh up       start the stack and wait until it answers
#   ./init.sh smoke    prove the stack works: every SMOKE_CHECKS command must pass, then prints SMOKE OK
#   ./init.sh down     stop the stack
#   ./init.sh status   list the features in features.json and whether each passes
#
# Why this exists: a fresh session, a builder in another worktree, or a teammate needs one command that says
# whether the project works, without reading the code. Work-package done-whens call these subcommands, so
# keep their names and exit codes stable. Exit codes: 0 ok, 1 a check failed (the message names it), 2 usage.
# The script loads .env but never prints a value from it.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FEATURES="$ROOT/features.json"

# ---- CONFIG: adapt these ------------------------------------------------------------------------------------
REQUIRED_TOOLS="python3 git"      # e.g. "docker curl python3 node"
UP_CMD=""                         # e.g. "docker compose up -d --remove-orphans"
DOWN_CMD=""                       # e.g. "docker compose down"  (no -v: volumes hold your data)
READY_CMD=""                      # e.g. "curl -fsS -o /dev/null http://localhost:${APP_PORT}/health"
READY_TIMEOUT=90                  # seconds `up` waits for READY_CMD
APP_PORT="${APP_PORT:-8080}"      # ports and names come from variables with defaults, so two worktrees on one
                                  # machine can run side by side (APP_PORT=18080 ./init.sh up); fixed names collide
SMOKE_CHECKS=(                    # one shell command per entry, run from the repo root; each must exit 0
  "python3 -c 'import json; json.load(open(\"features.json\"))'"
  # "curl -fsS -o /dev/null http://localhost:${APP_PORT}/"
)
# -------------------------------------------------------------------------------------------------------------

fail() { echo "init.sh: $*" >&2; exit 1; }
note() { echo "init.sh: $*"; }

load_env() {
  if [ -f "$ROOT/.env" ]; then
    set -a; . "$ROOT/.env"; set +a
  fi
}

cmd_check() {
  local ok=1 tool
  load_env
  for tool in $REQUIRED_TOOLS; do
    command -v "$tool" >/dev/null 2>&1 || { echo "missing: $tool"; ok=0; }
  done
  if [ -f "$ROOT/.env.example" ] && [ ! -f "$ROOT/.env" ]; then
    echo "warning: no .env (copy .env.example and fill in the values)"
  fi
  python3 - "$FEATURES" <<'PY' || ok=0
import json, sys
try:
    with open(sys.argv[1], encoding="utf-8") as f:
        features = json.load(f)["features"]
    ids = [x["id"] for x in features]
    assert len(ids) == len(set(ids)), "duplicate feature ids"
    for x in features:
        missing = {"id", "package", "description", "steps", "passes"} - set(x)
        assert not missing, f"{x.get('id', '?')} lacks {sorted(missing)}"
    print(f"features.json: {len(ids)} features, {sum(1 for x in features if x['passes'])} passing")
except Exception as error:  # noqa: BLE001
    print(f"features.json invalid: {error}", file=sys.stderr)
    sys.exit(1)
PY
  [ "$ok" = 1 ] || fail "check failed"
  note "check OK"
}

cmd_up() {
  load_env
  [ -n "$UP_CMD" ] || fail "UP_CMD is empty: set it in the CONFIG block of init.sh"
  (cd "$ROOT" && bash -c "$UP_CMD")
  [ -n "$READY_CMD" ] || { note "started (no READY_CMD set, so not waited for)"; return 0; }
  local waited=0
  until (cd "$ROOT" && bash -c "$READY_CMD") >/dev/null 2>&1; do
    [ "$waited" -ge "$READY_TIMEOUT" ] && fail "the stack did not answer within ${READY_TIMEOUT}s"
    sleep 2; waited=$((waited + 2))
  done
  note "up and answering"
}

cmd_smoke() {
  local ok=1 check
  load_env
  for check in "${SMOKE_CHECKS[@]}"; do
    if (cd "$ROOT" && bash -c "$check") >/dev/null 2>&1; then
      echo "ok:     $check"
    else
      echo "FAILED: $check"; ok=0
    fi
  done
  [ "$ok" = 1 ] || fail "SMOKE FAILED"
  echo "SMOKE OK"
}

cmd_down() {
  load_env
  [ -n "$DOWN_CMD" ] || fail "DOWN_CMD is empty: set it in the CONFIG block of init.sh"
  (cd "$ROOT" && bash -c "$DOWN_CMD")
}

cmd_status() {
  python3 - "$FEATURES" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as f:
    for x in json.load(f)["features"]:
        print(f"{x['id']:<6} {x['package']:<5} {'PASS' if x['passes'] else 'todo'}  {x['description']}")
PY
}

case "${1:-}" in
  check) cmd_check ;;
  up) cmd_up ;;
  smoke) cmd_smoke ;;
  down) cmd_down ;;
  status) cmd_status ;;
  *) sed -n '4,8p' "$0"; exit 2 ;;
esac
