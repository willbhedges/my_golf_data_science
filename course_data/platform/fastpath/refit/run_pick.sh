#!/bin/bash
# full routing refit under ROUTE_BENCH_CARD=pick with the shipped recipe: route_learn h/w/s/e + x3 (cv / fit),
# re-ranker rows (gen3) + bagged ranker (thr 0.5), tee rows (tgen2) + hybrid tee rule (0.93 / 12 / 0.5), out-of-fold
# bench, gate. usage: refit/run_pick.sh WORKDIR [PREP_DIR]  (resumable via done.* markers; refit/README.md)
# WORKDIR gets learn tables, scores, rows, picks, models/ (about 1.5 GB at the peak); PREP_DIR the bench's prepared
# solver inputs (default WORKDIR/prep; reused across refits of the same scenes + card convention).
set -u
FP=$(cd "$(dirname "$0")/.." && pwd)
RF=$FP/refit
V=$RF; R=$RF; T4=$RF; W=$(mkdir -p "$1" && cd "$1" && pwd); mkdir -p $W/models
PREP=${2:-$W/prep}
export FP FASTPATH_CACHE=$FP/cache/v2root ROUTE_LEARN_VER=v2seg_d0+yall FASTPATH_TILE_CACHE=off FASTSCENE_UNET_MODEL=v2 ROUTE_P_TEE=0.0
export ROUTE_TEE_PEAKS=0.1 ROUTE_TEE_PEAK_FILL=2 ROUTE_BENCH_CARD=pick
export ROUTE_BENCH_PROBS=d0+yall ROUTE_LEARN_KINDS=h,w,s,e ROUTE_LEARN_TRAIN=train+big
export ROUTE_BENCH_PREP=$PREP ROUTE_LEARN_DIR=$W/learn
export ROUTE_LEARN_MODEL=$W/models/route_learn_model.pkl ROUTE_RERANK_MODEL=$W/models/route_rerank_model.pkl \
       ROUTE_TEE_MODEL=$W/models/route_tee_model.pkl ROUTE_GATE_PARAMS=$W/models/route_gate.json
SC=$W/sc
cd $FP
st() { [ -f $W/done.$1 ]; }
mk() { touch $W/done.$1; echo "== $1 done $(date +%T) $(df -h / | tail -1 | awk '{print $4}')"; }
EV() { python3 route_bench.py eval --scene fast --router v2 --card-only --prep --ver $ROUTE_LEARN_VER --split $1 --procs 4 --out $2 2>&1 | tail -1; }
echo "== start $(date +%T) $*"
st prep || { ROUTE_RERANK=0 ROUTE_TEE=0 EV train+big $W/prep_tb.json; mk prep; }
st table || { python3 route_learn.py table --split train+big --procs 4 2>&1 | tail -1; mk table; }
st x3 || { python3 route_learn.py x3 --split train+big --procs 4 2>&1 | tail -1; mk x3; }
st cv || { python3 route_learn.py cv --out $SC 2>&1 | tail -1; python3 route_learn.py fit --out $SC 2>&1 | tail -1; find $ROUTE_LEARN_DIR -maxdepth 1 -name "*.pkl" -delete; mk cv; }
st gen || { ROUTE_BENCH_SC=$SC/cv python3 $R/gen3.py train+big $SC/cv $W/gen3_tb 4 > $W/gen3_tb.log 2>&1; mk gen; }
st rr || { (cd $R && X2=1 NC=${NC:-1} MODEL=rankbag KS=beam,renum,start,end python3 rr_fit.py $W/gen3_tb 0.5 $W/picks_tb.json $ROUTE_RERANK_MODEL > $W/rr.log 2>&1); tail -3 $W/rr.log; mk rr; }
st tgen || { ROUTE_RERANK=0 ROUTE_RERANK_PICKS=$W/picks_tb.json ROUTE_BENCH_SC=$SC/cv python3 $R/tgen2.py train+big $W/tg_tb 4 > $W/tg_tb.log 2>&1; mk tgen; }
st tl || { (cd $T4 && python3 tl_exp.py $W/tg_tb $W/tlc.pkl len:0:grid len:1:rank > $W/tl.log 2>&1 && python3 tl_fit.py $W/tg_tb $W/tlc.pkl 0.93 12 0.5 $W/tee_picks.json $ROUTE_TEE_MODEL > $W/tlfit.log 2>&1); tail -2 $W/tlfit.log; find $W/tg_tb -name "*.pkl" -delete; rm -f $W/tlc.pkl; mk tl; }
st oof || { ROUTE_TEE=0 ROUTE_RERANK=0 ROUTE_RERANK_PICKS=$W/picks_tb.json ROUTE_TEE_PICKS=$W/tee_picks.json ROUTE_BENCH_SC=$SC/cv EV train+big $W/oof.json; mk oof; }
st gate || { ROUTE_GATE_PARAMS=$W/models/route_gate.json python3 route_bench.py gate --train $W/oof.json --write 2>&1 | tail -1 | cut -c1-200; mk gate; }
python3 $V/summ3.py $W/oof.json
echo "== end $(date +%T)"
