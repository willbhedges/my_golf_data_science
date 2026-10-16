# NAIP hazard classifier: leave-one-hole-out vs the hand-traced maps

Grid 1.2 m, 30 features (NAIP RGB+NIR, NDVI, texture, 3DEP slope / relative elevation). Labels = spirit_hollow/course.py zones georeferenced by traced_align.py. Excluded (registration failed): 2B.

Pooled pixel accuracy **0.588**; any-penal-class (trees/native/water) precision 0.84, recall 0.83, IoU 0.72.

| class | IoU | precision | recall | labelled px |
|---|---|---|---|---|
| fairway | 0.49 | 0.70 | 0.63 | 88790 |
| rough | 0.19 | 0.30 | 0.33 | 52433 |
| trees | 0.59 | 0.73 | 0.75 | 135676 |
| native | 0.24 | 0.42 | 0.36 | 46321 |
| water | 0.32 | 0.47 | 0.49 | 17131 |
| sand | 0.18 | 0.20 | 0.67 | 1601 |

Per hole (held out): accuracy and IoU

| hole | reg corr | acc | fairway | rough | trees | native | water | sand |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.21 | 0.55 | 0.41 | 0.17 | 0.55 | 0.06 | 0.00 | 0.00 |
| 2F | 0.38 | 0.55 | 0.43 | 0.09 | 0.53 | 0.02 | 0.12 | 0.40 |
| 4 | 0.34 | 0.56 | 0.52 | 0.14 | 0.60 | 0.18 | 0.00 | 0.00 |
| 5 | 0.45 | 0.52 | 0.66 | 0.11 | 0.07 | 0.28 | 0.00 | 0.49 |
| 6 | 0.31 | 0.53 | 0.61 | 0.19 | 0.23 | 0.11 | 0.65 | 0.00 |
| 8 | 0.26 | 0.47 | 0.51 | 0.33 | 0.00 | 0.19 | 0.00 | 0.47 |
| 9B | 0.36 | 0.57 | 0.51 | 0.24 | 0.09 | 0.30 | 0.80 | 0.00 |
| 9F | 0.42 | 0.59 | 0.60 | 0.33 | 0.41 | 0.00 | 0.56 | 0.00 |
| 10 | 0.39 | 0.70 | 0.58 | 0.35 | 0.66 | 0.00 | 0.54 | 0.23 |
| 11 | 0.35 | 0.67 | 0.55 | 0.16 | 0.72 | 0.01 | 0.12 | 0.00 |
| 13 | 0.27 | 0.65 | 0.40 | 0.20 | 0.69 | 0.00 | 0.54 | 0.11 |
| 14 | 0.33 | 0.52 | 0.16 | 0.15 | 0.63 | 0.18 | 0.47 | 0.00 |
| 16 | 0.31 | 0.75 | 0.64 | 0.17 | 0.71 | 0.60 | 0.03 | 0.12 |
| 17 | 0.44 | 0.63 | 0.58 | 0.17 | 0.66 | 0.38 | 0.00 | 0.09 |
| 18 | 0.26 | 0.49 | 0.40 | 0.14 | 0.46 | 0.20 | 0.24 | 0.07 |

Confusion (rows = traced, cols = predicted): fairway, rough, trees, native, water, sand

```
 fairway    55683    18766     8447     4061     1087      746
   rough    15469    17447    10140     6517     1182     1678
   trees     5475    10472   101832    10963     6056      878
  native     3094    11359    13104    16664     1078     1022
   water      102      642     6562     1388     8388       49
    sand        6      380       96       49        1     1069
```

Caveats: the screenshots are winter imagery with tilted canopies and trees traced at the trunks; NAIP is leaf-on (September) and orthorectified, so tree canopies are legitimately wider than the traced 'recovery'. Footprints of neighbouring holes overlap, so LOHO is somewhat optimistic.
