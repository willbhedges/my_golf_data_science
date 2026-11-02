#!/bin/bash
# chain.sh <variant name> <variant log>: wait for the variant build, then score it
export OMP_NUM_THREADS=1 PYTHONWARNINGS=ignore
WT=/home/user/my_golf_data_science
while pgrep -f "s2_variant.py .* var $1 " >/dev/null; do sleep 15; done
python3 s2_eb.py $WT $PWD/var/$1 $PWD/eb/eb_$1.json blue_hills,eagle_knoll,gateway_national,hot_springs_arlington,pine_dunes,veenker,coldwater,annbriar,amana_colonies,ellis,spirit_hollow > eb_$1.log 2>&1
echo DONE >> eb_$1.log
