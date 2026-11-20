#!/bin/bash
# refit_actions.sh WORKDIR [repeat]: the shipped routing refit (refit/run_pick.sh, refit/README.md, unchanged) on
# inputs rebuilt on Actions (refit/bench_inputs.py), as .github/workflows/routing_bench.yml stage `refit` runs it.
# The inputs must already be in $FP/cache/v2root (the inputs-* artifacts of an `inputs` run merged there); truth +
# cards come from benchdata (refit/link_benchdata.sh).
#   (default) the whole refit, then the out-of-fold bench step (6) once more on the same runner into
#             WORKDIR/oof_rerun.json, compared per hole and per routed line with WORKDIR/oof.json (determinism).
#   repeat:   WORKDIR holds a finished refit's fits / picks / scores (the refit artifact): only steps 6-7 again, on
#             this runner, into WORKDIR/oof.json (the caller compares it with the refit's own oof.json).
set -u
FP=$(cd "$(dirname "$0")/.." && pwd)
W=$(mkdir -p "$1" && cd "$1" && pwd)
bash $FP/refit/link_benchdata.sh > /dev/null
echo "cpu: $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2) | amx $(grep -c amx_tile /proc/cpuinfo) | nproc $(nproc)"
echo "threads: OMP $OMP_NUM_THREADS OPENBLAS $OPENBLAS_NUM_THREADS MKL $MKL_NUM_THREADS coretype ${OPENBLAS_CORETYPE:-} impl ${FASTPERC_IMPL:-auto}"
echo "inputs: $(ls $FP/cache/v2root/big/scenes | wc -l) TRAIN-BIG scenes, $(ls $FP/cache/v2root/val/scenes/v2seg_d0+yall 2>/dev/null | wc -l) validation scenes"
if [ "${2:-}" = repeat ]; then
  rm -f $W/done.oof $W/done.gate
  bash $FP/refit/run_pick.sh $W
  exit 0
fi
bash $FP/refit/run_pick.sh $W
[ -f $W/oof.json ] || { echo "refit failed: no oof.json"; ls $W; exit 1; }
cp $W/oof.json $W/oof_first.json
cp $W/models/route_gate.json $W/route_gate_first.json 2>/dev/null
rm -f $W/done.oof $W/done.gate
bash $FP/refit/run_pick.sh $W
mv $W/oof.json $W/oof_rerun.json
mv $W/oof_first.json $W/oof.json
python3 $FP/refit/oof_compare.py $W/oof.json $W/oof_rerun.json --identity | tail -3
cmp -s $W/route_gate_first.json $W/models/route_gate.json && echo "gate params identical" || echo "gate params DIFFER"
exit 0
