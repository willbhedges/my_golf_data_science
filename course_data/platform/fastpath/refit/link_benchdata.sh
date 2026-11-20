#!/bin/bash
# On a fresh checkout: point the bench's TRAIN-BIG paths at the committed frozen inputs (benchdata/big). Links
# cache/big/{courses,manifest.json,status} and cache/v2root/big/{...} when they do not exist yet. The scenes / probs /
# maps (cache/v2root/big/{scenes,probs,maps}) are not in git: rebuild them (route_big.py / segv2 rebuild) or copy them.
set -eu
FP=$(cd "$(dirname "$0")/.." && pwd)
for d in "$FP/cache/big" "$FP/cache/v2root/big"; do
  mkdir -p "$d"
  for x in courses manifest.json status; do
    [ -e "$d/$x" ] || ln -s "$FP/benchdata/big/$x" "$d/$x"
  done
done
ls -la "$FP/cache/big" "$FP/cache/v2root/big" | grep -E "courses|manifest|status"
