#!/bin/bash
# smoke_bench.sh OUT.json [INPUT_DIR]: on the courses of benchdata/smoke/slugs.txt, SMOKE_MODE=
#   oof (default): the shipped default's out-of-fold bench protocol (rsel w2_0.5: re-ranker / tee picks, out-of-fold
#        route_learn scores via ROUTE_BENCH_SC, ROUTE_RERANK=0 ROUTE_TEE=0, the bench card `chosen` the picks were made
#        with). The picks and scores belong to the committed scenes: on rebuilt scenes use fold.
#   fold: scene-independent: each course rescored by its route_learn state-fold model (benchdata/smoke/folds,
#        ROUTE_BENCH_FOLD_RESCORE=1), the production re-ranker and tee step live (route_models/v2), no picks. Scenes / probs / maps from INPUT_DIR/big
# (default benchdata/smoke/big: copies of the local bench cache); truth + cards from benchdata/big. A scratch
# FASTPATH_CACHE is assembled under $TMPDIR. Used by .github/workflows/routing_bench.yml and for the local reference.
set -eu
FP=$(cd "$(dirname "$0")/.." && pwd)
SM=$FP/benchdata/smoke
IN=$(cd "${2:-$SM}" && pwd)
OUT=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
C=$(mktemp -d)/cache
mkdir -p $C/big
for x in courses manifest.json status; do ln -s $FP/benchdata/big/$x $C/big/$x; done
for x in scenes probs maps; do ln -s $IN/big/$x $C/big/$x; done
export FASTPATH_CACHE=$C ROUTE_BENCH_PREP=$C/prep ROUTE_LEARN_VER=v2seg_d0+yall FASTPATH_TILE_CACHE=off FASTSCENE_UNET_MODEL=v2
export ROUTE_P_TEE=0.0 ROUTE_TEE_PEAKS=0.1 ROUTE_TEE_PEAK_FILL=2 ROUTE_BENCH_PROBS=d0+yall ROUTE_BENCH_CARD=chosen
if [ "${SMOKE_MODE:-oof}" = fold ]; then
  export ROUTE_TEE=1 ROUTE_RERANK=1 ROUTE_BENCH_FOLD_RESCORE=1 ROUTE_BENCH_FOLDS=$SM/folds
else
  export ROUTE_TEE=0 ROUTE_RERANK=0 ROUTE_RERANK_PICKS=$SM/picks_tb.json ROUTE_TEE_PICKS=$SM/tee_picks.json ROUTE_BENCH_SC=$SM/sc
fi
cd $FP
python3 route_bench.py eval --scene fast --router v2 --card-only --prep --ver v2seg_d0+yall --split train+big \
  --slugs "$(cat $SM/slugs.txt)" --procs 2 --out "$OUT" 2>&1 | tail -1
