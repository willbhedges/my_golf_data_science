#!/bin/bash
# The whole battery on one frozen engine / map state.  usage: run_all.sh <snapshot dir> <out dir>
# snapshot: git archive <commit> spirit_hollow/*.py spirit_hollow/v2/*.py mozingo/*.py course_data/courses/*.py \
#   course_data/courses/gateway_national/{config.json,truth/course.py,truth/meta.json,truth/package.json} \
#   course_data/weather/forecast_gateway_national.json course_data/imagery/*.py course_data/product/*.py | tar -x -C <dir>
export SNAP=$1
O=$2
cd "$(dirname "$0")"
V1="tour table|am level 0.20 (scratch)|am_slope 0|am_slope 0.0025|m_rough 0.4|m_rough 1.3|lost 0.05-0.25 (dormant, thin)|lost 0.40-0.90|trees 1.0|block_sev 0|m_sand 1.5"
V2="width 60|width 65 (stated)|width 76|width 82 (Arccos 0-5)|width 90|big miss 6% x2.2 added|big miss 10% x2.5 added|t5 same 95% width|t3 same 95% width|no mishits|heavy mishits 6%|rho 0.4 (push short)|rho -0.2|kappa 0.25|depth x0.8|depth x1.3|equal-angle woods (4w 63)|DECADE woods 70/65/60|roll x0.7 (soft Nov)|roll x1.3 (firm dormant)"
(python3 exp1_value.py $O/v_a.json 1,2,3,5,6,8,9,10,11,13,15,16,18 "$V1" > $O/v_a.log 2>&1; python3 exp5_sd.py $O/sd.json > $O/sd.log 2>&1; python3 exp4_mdp.py $O/m_all.json "" 1.6,1.0,2.2 > $O/m_all.log 2>&1) &
(python3 exp2_disp.py $O/d_a.json 8,10,9,16,3,11,2 "$V2" > $O/d_a.log 2>&1; python3 exp3_aim_mc.py $O/a_a.json 8,10,9,16,11,3,2 > $O/a_a.log 2>&1) &
(python3 exp2_disp.py $O/d_b.json 1,5,6,13,15,18 "$V2" > $O/d_b.log 2>&1; python3 exp3_aim_mc.py $O/a_b.json 1,5,6,13,15,18 > $O/a_b.log 2>&1) &
(python3 exp6_prior_vs_central.py $O/p_a.json 8,9,10,11,16,3 64 > $O/p_a.log 2>&1) &
wait
echo done > $O/DONE
