#!/bin/zsh
# Usage: shot.sh <name> [windowID]  -> capture/app/<name>.png (window only, no shadow)
set -e
DIR=${0:A:h}
ID=${2:-$(swift "$DIR/winlist.swift" | sort -t$'\t' -k2 -nr | head -1 | cut -f1)}
[[ -z "$ID" ]] && { echo "no Claude window found" >&2; exit 1; }
OUT="$DIR/app/$1.png"
screencapture -x -o -l "$ID" "$OUT"
echo "$OUT"
