#!/bin/bash
# run_var.sh <name> <pred|none> <thr> <slugs comma>: build variant packages then score them
export OMP_NUM_THREADS=1 PYTHONWARNINGS=ignore
cd "$(dirname "$0")"; WT=${WT:?set WT=<repo>}
python3 ng_variant.py $WT var $1 $2 $3 ${4//,/ } 2>&1 | grep -v -i warn | grep -E "native m2|Error|Trace" 
python3 ng_eb.py $WT $PWD/var/$1 $PWD/eb/eb_$1.json $4 2>&1 | grep -E "auto match|Error|Trace|skip"
echo "DONE $1"
