# Routing refit recipe (moved from the scratch dirs, 2026-11-20)

These scripts are taken as they were used, with only path fixes; refit/never_used.txt replaces scratch
slugs_new1.txt. Results and history are in ../NOTES_ROUTING.md.

| script | step | was (scratch) |
|---|---|---|
| run_pick.sh WORKDIR [PREP_DIR] | the whole shipped refit, resumable (done.* markers) | t4/run_pick.sh |
| gen3.py SPLIT SC_DIR OUT_DIR [procs] [slug file] | re-ranker rows: alternatives per course + route_struct labels | rsel/gen3.py |
| rr_exp.py / rr_fit.py GEN_DIR THR PICKS.json MODEL.pkl | bagged lambdarank re-ranker: out-of-fold picks + final fit (rr_fit execs rr_exp's head) | rsel/ |
| tgen2.py SPLIT OUT_DIR [procs] [slugs] | tee-candidate rows under the re-ranker's picks | rsel/tgen2.py |
| tl_exp.py / tl_fit.py | hybrid tee rule (classifier + ranker): rows -> tee picks + route_tee_model.pkl | t4/ (the version reading the bench's card) |
| foldfit.py OUT_DIR | route_learn fold models (folds.json + fold_<i>.pkl, state folds) for out-of-fold rescoring | rsel/foldfit.py |
| summ3.py OOF.json [TEST.json] | holes right / all-right per split (643 / choice 443 / never-used 200 / test) | segv2/summ3.py |
| testeval.sh P_TEE WORKDIR | the ONE read of test 28 on a workdir's fits (production path) | teerec/testeval.sh |
| link_benchdata.sh | on a fresh checkout, links cache/big/{courses,manifest.json,status} to ../benchdata/big | new |
| smoke_bench.sh OUT [INPUT_DIR] / smoke_compare.py REF RUN | the Actions smoke (.github/workflows/routing_bench.yml): the default's out-of-fold protocol on benchdata/smoke's 5 courses; identical per-hole results to benchdata/smoke/ref_oof.json; SMOKE_MODE=fold: fold-model scores + live re-ranker / tee, vs ref_fold.json | new |
| smoke_scenes.py REF_DIR RUN_DIR | rebuilt vs committed scenes (greens / tees matched) | new |
| build_inputs.py OUT_DIR SLUGS | rebuild TRAIN-BIG scenes / probs / maps from free imagery (route_big's stages without the card search) | new |

## The shipped recipe (pick refit, 2026-11-20)

```
FP=course_data/platform/fastpath
export FASTPATH_CACHE=$FP/cache/v2root ROUTE_LEARN_VER=v2seg_d0+yall FASTPATH_TILE_CACHE=off FASTSCENE_UNET_MODEL=v2
export ROUTE_P_TEE=0.0 ROUTE_TEE_PEAKS=0.1 ROUTE_TEE_PEAK_FILL=2 ROUTE_BENCH_CARD=pick
export ROUTE_BENCH_PROBS=d0+yall ROUTE_LEARN_KINDS=h,w,s,e ROUTE_LEARN_TRAIN=train+big
refit/run_pick.sh /path/to/workdir [/path/to/prep]
```

Steps (all on split train+big, 643 courses, `--ver v2seg_d0+yall`):
1. **prep:** route_bench eval --prep with ROUTE_RERANK=0 ROUTE_TEE=0 (prepared solver inputs per course).
2. **route_learn table + x3, then cv + fit:** hole / walk / start / end models. cv writes the out-of-fold scores
   (WORKDIR/sc/cv), fit writes route_learn_model.pkl.
3. **gen3.py:** re-ranker rows, with ROUTE_BENCH_SC=sc/cv.
4. **rr_fit.py:** with `X2=1 NC=1 MODEL=rankbag KS=beam,renum,start,end` and threshold 0.5. Writes picks_tb.json
   (out-of-fold picks) and route_rerank_model.pkl.
5. **tgen2.py, then tl_exp.py + tl_fit.py:** tgen2 runs with ROUTE_RERANK=0, ROUTE_RERANK_PICKS=picks_tb.json and
   ROUTE_BENCH_SC=sc/cv. The tee fit uses `tl_exp len:0:grid len:1:rank` then `tl_fit 0.93 12 0.5`, writing
   tee_picks.json and route_tee_model.pkl.
6. **out-of-fold bench:** ROUTE_TEE=0 ROUTE_RERANK=0 ROUTE_RERANK_PICKS=picks_tb.json ROUTE_TEE_PICKS=tee_picks.json
   ROUTE_BENCH_SC=sc/cv, giving WORKDIR/oof.json.
7. **route_bench gate --train oof.json --write:** route_gate.json. summ3.py prints the per-split table.
8. **Ship:** copy WORKDIR/models/* to route_models/<name>/. Read test 28 once with testeval.sh 0.0 WORKDIR, and only
   after the variant is chosen.

## Bench pitfalls

* **Scores (the trap the v3 refit hit):** a bench eval routes on the learned route_learn scores only when one of these
  is set:
  * ROUTE_BENCH_SC=<dir> (cached out-of-fold scores, e.g. WORKDIR/sc/cv, made with the bench's card);
  * ROUTE_BENCH_FOLD_RESCORE=1 + ROUTE_BENCH_FOLDS=<foldfit dir> (each course rescored by its state-fold model on
    its own card).

  Without either, `route_bench.py eval --prep` routes on the solver's built-in scores from prepare(), not the learned
  ones, and gives a different and much worse number. ROUTE_LEARN_MODEL alone does not change this.
* Out-of-fold re-ranker / tee picks (ROUTE_RERANK_PICKS / ROUTE_TEE_PICKS, with ROUTE_RERANK=0 ROUTE_TEE=0) belong to
  the card and scenes they were made with. A course whose card changes needs its picks dropped (route_bench does this
  for ROUTE_CARD_PICKS) or regenerated.
* Prep pickles (ROUTE_BENCH_PREP) keep the card they were prepared with. Use a new prep dir when ROUTE_BENCH_CARD or
  the scenes change.
* Always pass `--ver v2seg_d0+yall`. Without it, route_bench names the scene cache after the last commit touching the
  detector files (fastscene.py among them) and rebuilds scenes under a new hash.
* The scripts call route_bench / route_learn / route_struct / route_rerank / route_tee / route_scene from ../ and read
  the bench caches (cache/v2root/big/{scenes,probs,maps}, cache/v2root/val/*, cache/heldout/probs). Those caches are
  not in git (1.3 GB; see the Actions design in NOTES_ROUTING.md). TRAIN-BIG truth + cards are in ../benchdata/big.
* Library versions: requirements.txt.

## Scratch dependencies left

None of the scripts read scratch files any more (never_used.txt is the copy of slugs_new1.txt). The env file
scratch rsel/env.sh only set FP / FASTPATH_CACHE / FASTSCENE_UNET_MODEL, which run_pick.sh sets itself. The
experiment scripts behind the variant choices (rr_exp variants, tl_hyb / tl_pen*, cardalt, etc.) are not moved;
NOTES_ROUTING.md names them under each "Reproduce".
