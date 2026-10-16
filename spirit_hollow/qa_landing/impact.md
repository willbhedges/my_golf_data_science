# Decision impact of the proposed patches

Central prior (driver width 70, 2w/4w 0.94/0.85 of it, depth x1.25, roll 0.975, rough roll 0.325, trees 0.8, lost 0.5, mishit 0.15), 3000 common-random-number swings, aims -25..+25 by 2.5 (irons to +45). EV = expected strokes for the hole at each club's best aim.

| finding | hole | club | aim before -> after | EV before -> after (change) | pick before -> after |
|---|---|---|---|---|---|
| 1-trees-right-305 | 1 | Driver | +2.5 -> +0.0 | 3.957 -> 4.073 (+0.116) | Driver -> 4-wood |
| 1-trees-right-305 | 1 | 2-wood | +5.0 -> +5.0 | 3.978 -> 4.003 (+0.025) | Driver -> 4-wood |
| 1-trees-right-305 | 1 | 4-wood | +7.5 -> +7.5 | 3.980 -> 3.982 (+0.001) | Driver -> 4-wood |
| 18-creek-bank-right | 18 | Driver | -2.5 -> +2.5 | 4.708 -> 4.596 (-0.112) | 2-wood -> 2-wood |
| 18-creek-bank-right | 18 | 2-wood | -7.5 -> -5.0 | 4.675 -> 4.591 (-0.084) | 2-wood -> 2-wood |
| 18-creek-bank-right | 18 | 4-wood | -12.5 -> -7.5 | 4.694 -> 4.619 (-0.075) | 2-wood -> 2-wood |
| 9F-trees-left-260 | 9F | Driver | -10.0 -> -5.0 | 3.928 -> 3.947 (+0.019) | 2-wood -> 4-wood |
| 9F-trees-left-260 | 9F | 2-wood | -20.0 -> -10.0 | 3.867 -> 3.907 (+0.041) | 2-wood -> 4-wood |
| 9F-trees-left-260 | 9F | 4-wood | -25.0 -> -22.5 | 3.868 -> 3.902 (+0.034) | 2-wood -> 4-wood |
| 9F-trees-long-300 | 9F | Driver | -10.0 -> -22.5 | 3.928 -> 4.125 (+0.197) | 2-wood -> 4-wood |
| 9F-trees-long-300 | 9F | 2-wood | -20.0 -> -25.0 | 3.867 -> 3.911 (+0.044) | 2-wood -> 4-wood |
| 9F-trees-long-300 | 9F | 4-wood | -25.0 -> -25.0 | 3.868 -> 3.889 (+0.021) | 2-wood -> 4-wood |
| 9B-9F-tree-clump-right | 9B | Driver | -25.0 -> -20.0 | 3.966 -> 3.946 (-0.020) | Driver -> Driver |
| 9B-9F-tree-clump-right | 9B | 2-wood | -25.0 -> -22.5 | 3.978 -> 3.961 (-0.017) | Driver -> Driver |
| 9B-9F-tree-clump-right | 9B | 4-wood | -22.5 -> -22.5 | 3.984 -> 3.977 (-0.008) | Driver -> Driver |
| 9F-tree-clump-right | 9F | Driver | -10.0 -> -10.0 | 3.928 -> 3.922 (-0.006) | 2-wood -> 4-wood |
| 9F-tree-clump-right | 9F | 2-wood | -20.0 -> -17.5 | 3.867 -> 3.854 (-0.012) | 2-wood -> 4-wood |
| 9F-tree-clump-right | 9F | 4-wood | -25.0 -> -22.5 | 3.868 -> 3.848 (-0.020) | 2-wood -> 4-wood |
| 13-pot-bunkers-left | 13 | Driver | -10.0 -> -15.0 | 4.024 -> 4.013 (-0.012) | Driver -> Driver |
| 13-pot-bunkers-left | 13 | 2-wood | -17.5 -> -17.5 | 4.045 -> 4.041 (-0.005) | Driver -> Driver |
| 13-pot-bunkers-left | 13 | 4-wood | -20.0 -> -20.0 | 4.033 -> 4.036 (+0.003) | Driver -> Driver |
| 13-pot-bunkers-left | 13 | Long iron | -20.0 -> -20.0 | 4.131 -> 4.131 (+0.000) | Driver -> Driver |
| 13-pot-bunkers-left | 13 | Mid iron | -17.5 -> -17.5 | 4.276 -> 4.276 (+0.000) | Driver -> Driver |
| 5-right-bunker-300 | 5 | Driver | -5.0 -> -5.0 | 3.904 -> 3.928 (+0.024) | Driver -> 2-wood |
| 5-right-bunker-300 | 5 | 2-wood | -5.0 -> -5.0 | 3.911 -> 3.912 (+0.001) | Driver -> 2-wood |
| 5-right-bunker-300 | 5 | 4-wood | -5.0 -> -5.0 | 3.917 -> 3.917 (+0.000) | Driver -> 2-wood |
| 17-lone-tree-right-310 | 17 | Driver | -5.0 -> -10.0 | 4.034 -> 4.051 (+0.018) | Driver -> Driver |
| 17-lone-tree-right-310 | 17 | 2-wood | -5.0 -> -7.5 | 4.087 -> 4.088 (+0.001) | Driver -> Driver |
| 17-lone-tree-right-310 | 17 | 4-wood | -10.0 -> -10.0 | 4.123 -> 4.123 (+0.000) | Driver -> Driver |
| 11-canopy-left-245 | 11 | Driver | -25.0 -> -25.0 | 4.669 -> 4.675 (+0.006) | 4-wood -> 4-wood |
| 11-canopy-left-245 | 11 | 2-wood | -2.5 -> -2.5 | 4.240 -> 4.249 (+0.009) | 4-wood -> 4-wood |
| 11-canopy-left-245 | 11 | 4-wood | -2.5 -> +0.0 | 3.840 -> 3.869 (+0.030) | 4-wood -> 4-wood |
| 11-canopy-left-245 | 11 | Long iron | +2.5 -> +2.5 | 3.916 -> 3.916 (-0.000) | 4-wood -> 4-wood |
| 11-canopy-left-245 | 11 | Mid iron | +7.5 -> +7.5 | 4.020 -> 4.020 (+0.000) | 4-wood -> 4-wood |
| 8-right-bunker-280 | 8 | Driver | +7.5 -> +7.5 | 4.175 -> 4.130 (-0.045) | 4-wood -> 4-wood |
| 8-right-bunker-280 | 8 | 2-wood | +5.0 -> +7.5 | 4.038 -> 4.008 (-0.030) | 4-wood -> 4-wood |
| 8-right-bunker-280 | 8 | 4-wood | +7.5 -> +10.0 | 3.945 -> 3.931 (-0.013) | 4-wood -> 4-wood |
| 8-long-grass-left | 8 | Driver | +7.5 -> -2.5 | 4.175 -> 4.037 (-0.138) | 4-wood -> 4-wood |
| 8-long-grass-left | 8 | 2-wood | +5.0 -> +5.0 | 4.038 -> 3.987 (-0.051) | 4-wood -> 4-wood |
| 8-long-grass-left | 8 | 4-wood | +7.5 -> +5.0 | 3.945 -> 3.930 (-0.015) | 4-wood -> 4-wood |
| 9B-trees-left-310 | 9B | Driver | -25.0 -> -20.0 | 3.966 -> 3.994 (+0.028) | Driver -> 2-wood |
| 9B-trees-left-310 | 9B | 2-wood | -25.0 -> -25.0 | 3.978 -> 3.979 (+0.001) | Driver -> 2-wood |
| 9B-trees-left-310 | 9B | 4-wood | -22.5 -> -22.5 | 3.984 -> 3.984 (+0.000) | Driver -> 2-wood |
| 5-right-strip | 5 | Driver | -5.0 -> -2.5 | 3.904 -> 3.895 (-0.008) | Driver -> Driver |
| 5-right-strip | 5 | 2-wood | -5.0 -> -2.5 | 3.911 -> 3.905 (-0.006) | Driver -> Driver |
| 5-right-strip | 5 | 4-wood | -5.0 -> -2.5 | 3.917 -> 3.914 (-0.003) | Driver -> Driver |
| 13-pond-corner | 13 | Driver | -10.0 -> -10.0 | 4.024 -> 4.008 (-0.016) | Driver -> Driver |
| 13-pond-corner | 13 | 2-wood | -17.5 -> -15.0 | 4.045 -> 4.037 (-0.008) | Driver -> Driver |
| 13-pond-corner | 13 | 4-wood | -20.0 -> -20.0 | 4.033 -> 4.030 (-0.003) | Driver -> Driver |
| 13-pond-corner | 13 | Long iron | -20.0 -> -20.0 | 4.131 -> 4.131 (+0.000) | Driver -> Driver |
| 13-pond-corner | 13 | Mid iron | -17.5 -> -17.5 | 4.276 -> 4.276 (+0.000) | Driver -> Driver |
| 16-woods-left-270 | 16 | Driver | -10.0 -> -12.5 | 4.001 -> 3.976 (-0.024) | Driver -> Driver |
| 16-woods-left-270 | 16 | 2-wood | -7.5 -> -10.0 | 4.002 -> 3.991 (-0.011) | Driver -> Driver |
| 16-woods-left-270 | 16 | 4-wood | -10.0 -> -10.0 | 4.048 -> 4.048 (-0.000) | Driver -> Driver |
| 13-tree-right-300 | 13 | Driver | -10.0 -> -10.0 | 4.024 -> 4.031 (+0.007) | Driver -> Driver |
| 13-tree-right-300 | 13 | 2-wood | -17.5 -> -17.5 | 4.045 -> 4.046 (+0.000) | Driver -> Driver |
| 13-tree-right-300 | 13 | 4-wood | -20.0 -> -20.0 | 4.033 -> 4.033 (+0.000) | Driver -> Driver |
| 13-tree-right-300 | 13 | Long iron | -20.0 -> -20.0 | 4.131 -> 4.131 (+0.000) | Driver -> Driver |
| 13-tree-right-300 | 13 | Mid iron | -17.5 -> -17.5 | 4.276 -> 4.276 (+0.000) | Driver -> Driver |
| 2B-trees-right-290 | 2B | Driver | -5.0 -> -5.0 | 4.906 -> 4.896 (-0.010) | Driver -> Driver |
| 2B-trees-right-290 | 2B | 2-wood | -5.0 -> -5.0 | 4.928 -> 4.920 (-0.008) | Driver -> Driver |
| 2B-trees-right-290 | 2B | 4-wood | +0.0 -> +0.0 | 4.970 -> 4.961 (-0.008) | Driver -> Driver |
| 2B-long-grass-left-320 | 2B | Driver | -5.0 -> -7.5 | 4.906 -> 4.873 (-0.033) | Driver -> Driver |
| 2B-long-grass-left-320 | 2B | 2-wood | -5.0 -> -5.0 | 4.928 -> 4.920 (-0.007) | Driver -> Driver |
| 2B-long-grass-left-320 | 2B | 4-wood | +0.0 -> +0.0 | 4.970 -> 4.970 (+0.000) | Driver -> Driver |
| 17-long-grass-left | 17 | Driver | -5.0 -> +0.0 | 4.034 -> 4.048 (+0.014) | Driver -> Driver |
| 17-long-grass-left | 17 | 2-wood | -5.0 -> -5.0 | 4.087 -> 4.090 (+0.003) | Driver -> Driver |
| 17-long-grass-left | 17 | 4-wood | -10.0 -> -10.0 | 4.123 -> 4.123 (+0.000) | Driver -> Driver |
| 9F-all | 9F | Driver | -10.0 -> +5.0 | 3.928 -> 4.155 (+0.227) | 2-wood -> 4-wood |
| 9F-all | 9F | 2-wood | -20.0 -> -12.5 | 3.867 -> 3.936 (+0.069) | 2-wood -> 4-wood |
| 9F-all | 9F | 4-wood | -25.0 -> -17.5 | 3.868 -> 3.888 (+0.020) | 2-wood -> 4-wood |
| 9B-all | 9B | Driver | -25.0 -> -20.0 | 3.966 -> 3.962 (-0.003) | Driver -> 2-wood |
| 9B-all | 9B | 2-wood | -25.0 -> -22.5 | 3.978 -> 3.961 (-0.017) | Driver -> 2-wood |
| 9B-all | 9B | 4-wood | -22.5 -> -22.5 | 3.984 -> 3.977 (-0.008) | Driver -> 2-wood |
| 13-all | 13 | Driver | -10.0 -> -10.0 | 4.024 -> 4.008 (-0.016) | Driver -> Driver |
| 13-all | 13 | 2-wood | -17.5 -> -15.0 | 4.045 -> 4.033 (-0.013) | Driver -> Driver |
| 13-all | 13 | 4-wood | -20.0 -> -20.0 | 4.033 -> 4.032 (-0.000) | Driver -> Driver |
| 13-all | 13 | Long iron | -20.0 -> -20.0 | 4.131 -> 4.131 (+0.000) | Driver -> Driver |
| 13-all | 13 | Mid iron | -17.5 -> -17.5 | 4.276 -> 4.276 (+0.000) | Driver -> Driver |
| 5-all | 5 | Driver | -5.0 -> -5.0 | 3.904 -> 3.922 (+0.018) | Driver -> 2-wood |
| 5-all | 5 | 2-wood | -5.0 -> -2.5 | 3.911 -> 3.907 (-0.004) | Driver -> 2-wood |
| 5-all | 5 | 4-wood | -5.0 -> -2.5 | 3.917 -> 3.914 (-0.003) | Driver -> 2-wood |
| 17-all | 17 | Driver | -5.0 -> -5.0 | 4.034 -> 4.071 (+0.037) | Driver -> Driver |
| 17-all | 17 | 2-wood | -5.0 -> -5.0 | 4.087 -> 4.091 (+0.004) | Driver -> Driver |
| 17-all | 17 | 4-wood | -10.0 -> -10.0 | 4.123 -> 4.123 (+0.000) | Driver -> Driver |
| 8-all | 8 | Driver | +7.5 -> +0.0 | 4.175 -> 4.006 (-0.169) | 4-wood -> 4-wood |
| 8-all | 8 | 2-wood | +5.0 -> +5.0 | 4.038 -> 3.960 (-0.077) | 4-wood -> 4-wood |
| 8-all | 8 | 4-wood | +7.5 -> +7.5 | 3.945 -> 3.918 (-0.027) | 4-wood -> 4-wood |
| 2B-all | 2B | Driver | -5.0 -> -7.5 | 4.906 -> 4.867 (-0.039) | Driver -> Driver |
| 2B-all | 2B | 2-wood | -5.0 -> -5.0 | 4.928 -> 4.913 (-0.015) | Driver -> Driver |
| 2B-all | 2B | 4-wood | +0.0 -> +0.0 | 4.970 -> 4.961 (-0.008) | Driver -> Driver |
