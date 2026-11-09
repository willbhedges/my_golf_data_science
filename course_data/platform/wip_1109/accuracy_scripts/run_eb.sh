#!/bin/bash
# run_eb.sh NAME AUTO_PREFIX [extra error_budget args]  -> $A/NAME_v1.json / _v2.json (shared decision caches)
S=/tmp/claude-0/-home-user-my-golf-data-science/3c0900e1-ef71-58c8-8d72-7f70a9ca40ad/scratchpad; A=$S/acc
N=$1; P=$2; shift 2
cd /home/user/my_golf_data_science; export OMP_NUM_THREADS=1
for v in v1 v2; do
  [ -f $A/cache_$v.json ] || cp $S/eb_1109/cache_$v.json $A/cache_$v.json
  python3 course_data/platform/error_budget.py --set $v --n 4000 --workers ${W:-2} --auto-dir ${P}_$v --out $A/${N}_$v.json --cache $A/cache_$v.json "$@" > $A/${N}_$v.log 2>&1 &
done
wait
echo done > $A/${N}.done
