#!/bin/bash
# ONE read of the routing test split for workdir $2 (fits from pipe2.sh) at ROUTE_P_TEE=$1
set -u
FP=$(cd "$(dirname "$0")/.." && pwd)
W=$(cd "$2" && pwd)
export FP FASTPATH_CACHE=$FP/cache/v2root ROUTE_LEARN_VER=v2seg_d0+yall FASTPATH_TILE_CACHE=off FASTSCENE_UNET_MODEL=v2 ROUTE_P_TEE=$1
export ROUTE_BENCH_PROBS=d0+yall ROUTE_LEARN_KINDS=h,w,s,e ROUTE_LEARN_TRAIN=train+big
export ROUTE_BENCH_PREP=$W/prep_test ROUTE_LEARN_DIR=$W/learn_test
export ROUTE_LEARN_MODEL=$W/models/route_learn_model.pkl ROUTE_RERANK_MODEL=$W/models/route_rerank_model.pkl \
       ROUTE_TEE_MODEL=$W/models/route_tee_model.pkl ROUTE_GATE_PARAMS=$W/models/route_gate.json
cd $FP
EV() { python3 route_bench.py eval --scene fast --router v2 --card-only --prep --ver $ROUTE_LEARN_VER --split $1 --procs 4 --out $2 2>&1 | tail -1; }
ROUTE_RERANK=0 ROUTE_TEE=0 EV test $W/prep_test.json > /dev/null
python3 route_learn.py table --split test --procs 4 2>&1 | tail -1
python3 route_learn.py x3 --split test --procs 4 2>&1 | tail -1
python3 - <<'PY'
import os, pickle, route_learn as RL
W = os.environ["ROUTE_BENCH_PREP"][:-len("/prep_test")]
m = pickle.load(open(RL.MODEL, "rb")); out = W + "/sc/test"; os.makedirs(out, exist_ok=True)
n = 0
for t in RL.load_tables("test"):
    pickle.dump(RL.predict(m["models"], t), open(os.path.join(out, t["slug"] + ".pkl"), "wb")); n += 1
print("test sc", n)
PY
ROUTE_BENCH_SC=$W/sc/test EV test $W/test.json > /dev/null
python3 $FP/refit/summ3.py $W/oof.json $W/test.json
