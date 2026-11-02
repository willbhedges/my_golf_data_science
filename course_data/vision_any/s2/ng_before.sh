C13=gateway_national,spirit_hollow,coldwater,ellis,mozingo,eagle_knoll,veenker,pine_dunes,hot_springs_arlington,blue_hills,national_kc,annbriar,amana_colonies
python3 s2_apply.py $C13 tomahawk_hills,la_nickell,gustin,rivercut,osage_national,sand_creek_station,eagle_bend,prairie_dunes,mariah_hills,buffalo_dunes pred_s2_13.npz pred_s2_before23.npz 2>&1 | tail -1
python3 s2_eval.py pred_s2_before23.npz 0.3,0.4,0.5,0.6 -v --json ev_pred_s2_before23.json 2>&1 | grep -v -i warn
echo BEFORE_DONE
