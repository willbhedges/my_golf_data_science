#!/bin/bash
# usage: run_eb.sh variant...   (waits for build_variant to finish)
WT=${WT:?set WT to the repo root}
cd "$(dirname "$0")"   # data dir: ds_*.npz, var/, eb2/ (not committed)
export OMP_NUM_THREADS=1 PYTHONWARNINGS=ignore
while pgrep -f "python3 build_variant.py" >/dev/null; do sleep 10; done
for v in "$@"; do
  cp shared_cache.json eb2/eb_$v.json.cache.json 2>/dev/null
  python3 $WT/course_data/platform/error_budget_variant.py "$WT" "$PWD/var/$v" "$PWD/eb2/eb_$v.json" blue_hills,eagle_knoll,gateway_national,hot_springs_arlington,pine_dunes,veenker,coldwater,ellis,spirit_hollow
  cp eb2/eb_$v.json.cache.json shared_cache.json
done
echo ALLDONE
