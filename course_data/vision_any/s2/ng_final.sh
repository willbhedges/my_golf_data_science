#!/bin/bash
# after raw/ for the 5 KS courses is in the worktree: hand corridors with lidar trees, datasets, LOCO, eval
export OMP_NUM_THREADS=1 PYTHONWARNINGS=ignore
cd "$(dirname "$0")"; WT=${WT:?set WT=<repo>}
NEW="sand_creek_station eagle_bend prairie_dunes mariah_hills buffalo_dunes"
for s in $NEW; do (cd $WT && python3 course_data/truth/corridor.py build --slug $s && python3 course_data/truth_sets_v2/truth_sets.py build $s) 2>&1 | tail -1; done
python3 build_ds_13.py $WT . $NEW 2>&1 | grep -E "cells [0-9]|Error|Trace"
python3 prep_grid10.py $WT . $NEW 2>&1 | grep -E "fairway cells|Error|Trace"
C23=gateway_national,spirit_hollow,coldwater,ellis,mozingo,eagle_knoll,veenker,pine_dunes,hot_springs_arlington,blue_hills,national_kc,annbriar,amana_colonies,tomahawk_hills,la_nickell,gustin,rivercut,osage_national,sand_creek_station,eagle_bend,prairie_dunes,mariah_hills,buffalo_dunes
python3 s2_loco.py s2 $C23 2>&1 | grep -E "top gain|Error"; mv pred_s2.npz pred_s2_23.npz
python3 s2y_loco.py $C23 --tag y23 2>&1 | grep -E "drought|Error"
export NAT=gateway_national,spirit_hollow,coldwater,ellis,mozingo,annbriar,sand_creek_station,eagle_bend,prairie_dunes,mariah_hills,buffalo_dunes
for f in pred_s2_23 pred_y23_mean pred_y23_min pred_y23_gated; do python3 s2_eval.py $f.npz 0.3,0.4,0.5,0.6 -v --json ev_$f.json 2>&1 | grep -v -i warn; done
bash before.sh
echo FINAL_DONE
