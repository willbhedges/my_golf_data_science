# Landing-zone hazard edges: hand map vs independent evidence (Spirit Hollow)

QA of `spirit_hollow/course.py` (HOLES incl. AUDIT_FIXES and the OSM first-cut bands) in the tee-shot
landing corridor: 190-335 yds from the tee, +/-55 yds of the app's tee line. Nothing in `course.py`
was edited; every proposed fix is in `proposed_patches.py`.

Re-run after any map change (about 2 minutes, one process):

    python3 spirit_hollow/qa_landing/disagree.py --all        # rank + crops of the top 20 + EV impact
    python3 spirit_hollow/qa_landing/disagree.py --patched    # what would remain once the patches are in
    python3 spirit_hollow/qa_landing/disagree.py --zoom 18 340 830 600 1240   # photo | NAIP at full res
    pytest tests/test_qa_landing.py                           # fast offline test

## How it works

* **Grid.** 1-yd cells along/across the tee line, mapped to screenshot px (`tee_strategy.hole_frame`)
  and to the ground through the screenshot-to-NAIP registration in `hand_zones_ll.json`.
* **Evidence** (none of it uses the hand trace): trees = USGS 3DEP lidar canopy > 2.5 m (2019), kept only
  where NAIP 2023 shows canopy texture or the vision2 classifier sees trees (so trees cut down since 2019
  drop out); long grass = the vision_any NAIP layer AND vision2 agreeing; water = 2 of OSM / vision_any /
  a NAIP NDVI-NIR rule / vision2; sand = OSM bunker, or the NAIP brightness rule with vision2. vision2 = the
  out-of-sample (leave-one-hole-out) screenshot classifier, so it has never seen that hole's labels.
* **Disagreements** need more than 4 yds of edge position: *missing* (the evidence hazard reaches more than 4 yds
  past every hand hazard), *phantom* (the hand hazard reaches more than 4 yds past every evidence cell of that class) and
  *swap* (trees, long grass and water confused, weight 0.5). Connected cells form one finding, with the
  per-row edge shift (how far the evidence edge is from the hand edge).
* **Ranking by decision impact.** These are the simulated tee shots (`tee_strategy.simulate`, prior-median model: driver
  width 70, depth x1.25, roll 0.975, trees 0.8, lost ball 0.5, mishit 0.15, no map jitter). The weights are 2/3 for the
  `final_decision.json` pick at its aim plus 1/3 for the runner-up, and each shot counts half for its landing
  spot and half for where it stops. The shot share in a finding's cells is multiplied by exp(-d/12), where d is the
  distance in yds from the hand fairway or first cut. That way an edge error next to the short grass outranks one deep in the woods.
* **Review.** I looked at the 5-panel crop of each of the top ~30 findings (screenshot | NAIP | lidar + layers + OSM | vision2 |
  hand map), and at full-resolution photo/NAIP zooms where the call was close (18, 9B, 1, 4).
  Winter screenshots lean the canopies and throw long shadows, so the canopy position comes from NAIP and lidar, which look straight down.
  The shadow side is told apart from the crowns by texture: crowns are lumpy, shadow is smooth and dark.
* **Impact.** For each map-wrong finding I ran the hole with and without its patch, through `course_with_patches()`.
  That function re-executes `course.py` with the patch appended to `AUDIT_FIXES`, so the first-cut bands are rebuilt
  as they would be for real. The run uses N=3000 common-random-number swings, the same central model, and every club's best
  aim on a 2.5-yd grid (-25..+25, irons to +45). This is a point estimate. It is not the 128-draw Bayesian run
  in `final_decision.py`, so re-run that for the holes flagged below once patches are applied.

## Bug found on the way: two AUDIT_FIXES entries are silently dropped

`course.py`'s `AUDIT_FIXES` dict literal has **keys 5 and 8 twice** (lines ~283/339 and ~309/340). A dict literal
keeps only the last entry, so these earlier fixes are **not in the model today**:

* 5: `("sand", [(478, 843), (549, 843), (549, 925), (478, 925)])`, the "right bunker ~2x the trace" fix.
* 8: `("rough", ...)` "long grass ends 10-19 yds further left" and `("fairway", ...)` "L-shaped bunker:
  grass block".

The evidence independently flags both areas (findings 8-long-grass-left, 8-right-bunker-280 and 5-right-bunker-300).
The patches below restore the 8 rough strip verbatim and replace both bunkers by their OSM outlines. Merge the
duplicate keys when applying. `disagree.duplicate_keys()` checks for this, and `disagree.md` prints a warning while it persists.

## Ranked findings (top 20 by impact, plus the ones reviewed and rejected)

| rank | finding | hole | where (along, lat) | kind | map says | evidence says | verdict | shots % | edge shift med/max | decision impact (central model, N=3000) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1-trees-right-305 | 1 | 311-335, +4..+40 | missing | playable | trees | map wrong | 5.17 | 26-29 | **Driver → 4-wood**; Driver EV +0.116; aim +2.5 → +7.5 |
| 2 | 18-creek-bank-right | 18 | 231-335, -8..+51 | phantom | long grass | playable | map wrong | 4.84 | 9-15 | 2-wood stays; 2-wood EV -0.084; aim -7.5 → -5.0 |
| 3 | 9F-trees-left-260 | 9F | 261-312, -55..-34 | missing | playable | trees | map wrong | 3.02 | 21-45 | **2-wood → 4-wood**; 2-wood EV +0.041; aim -20.0 → -22.5 |
| 4 | 9F-trees-long-300 | 9F | 294-318, -34..+15 | missing | playable | trees | map wrong | 1.59 | 14-19 | **2-wood → 4-wood**; 2-wood EV +0.044; aim -20.0 → -25.0 |
| 5,14,23 | 13-pot-bunkers-left | 13 | 294-322, -24..+4 | missing; phantom | sand | playable | map wrong | 2.55 | 7-9/6-8/7-8 | Driver stays; Driver EV -0.012; aim -10.0 → -15.0 |
| 6 | 9B-9F-tree-clump-right | 9B | 268-297, +14..+32 | phantom | trees | playable | map wrong | 1.82 | 13-18 | Driver stays; Driver EV -0.020; aim -25.0 → -20.0 |
| 7 | 5-right-bunker-300 | 5 | 291-304, +8..+25 | missing | playable | sand | map wrong | 1.43 | 6-11 | **Driver → 2-wood**; Driver EV +0.024; aim -5.0 → -5.0 |
| 8 | 9F-tree-clump-right | 9F | 231-270, +6..+25 | phantom | trees | playable | map wrong | 1.54 | 16-20 | **2-wood → 4-wood**; 2-wood EV -0.012; aim -20.0 → -22.5 |
| 9 | 17-lone-tree-right-310 | 17 | 295-320, +27..+46 | missing | playable | trees | map wrong | 1.18 | 19-21 | Driver stays; Driver EV +0.018; aim -5.0 → -10.0 |
| 10 | 4-long-grass-left | 4 | 260-283, -35..-27 | missing | playable | long grass | evidence wrong | 1.81 | 9-11 | — |
| 11,22 | 11-canopy-left-245 | 11 | 238-266, -32..-20 | missing | playable | trees | map wrong | 1.04 | 10-15/6-7 | 4-wood stays; 4-wood EV +0.030; aim -2.5 → +0.0 |
| 12 | 8-right-bunker-280 | 8 | 273-275, +5..+8 | phantom | sand | playable | map wrong | 0.68 | 5-6 | 4-wood stays; 4-wood EV -0.013; aim +7.5 → +10.0 |
| 13 | 9B-trees-left-310 | 9B | 309-335, -55..-19 | missing | playable | trees | map wrong | 0.55 | 64-76 | **Driver → 2-wood**; Driver EV +0.028; aim -25.0 → -25.0 |
| 15 | 5-right-strip | 5 | 209-303, +33..+51 | phantom | trees | playable | map wrong | 1.02 | 20-32 | Driver stays; Driver EV -0.008; aim -5.0 → -2.5 |
| 16 | 13-pond-corner | 13 | 279-286, +18..+23 | phantom | water | playable | map wrong | 0.51 | 6-7 | Driver stays; Driver EV -0.016; aim -10.0 → -10.0 |
| 17 | 16-woods-left-270 | 16 | 271-299, -55..-39 | swap | long grass | trees | map wrong | 1.62 | 19-33 | Driver stays; Driver EV -0.024; aim -10.0 → -12.5 |
| 18 | 13-tree-right-300 | 13 | 291-304, +25..+41 | missing | playable | trees | map wrong | 0.41 | 10-16 | Driver stays; Driver EV +0.007; aim -10.0 → -10.0 |
| 19,29 | 2B-trees-right-290 | 2B | 279-302, +22..+42 | missing; swap | playable | trees | map wrong | 1.28 | 6-7/71-76 | Driver stays; Driver EV -0.010; aim -5.0 → -5.0 |
| 20 | 16-trees-right-265 | 16 | 262-267, +22..+25 | phantom | trees | playable | unclear | 0.42 | 6-7 | — |
| 21 | 2B-long-grass-left-320 | 2B | 300-335, -47..-35 | phantom | long grass | playable | map wrong | 0.63 | 10-16 | Driver stays; Driver EV -0.033; aim -5.0 → -7.5 |
| 24 | 17-long-grass-left | 17 | 273-335, -51..-34 | missing | playable | long grass | map wrong | 0.65 | 12-15 | Driver stays; Driver EV +0.014; aim -5.0 → +0.0 |
| 25 | 2F-pond-corner | 2F | 281-285, -38..-36 | phantom | water | playable | unclear | 0.26 | 5-5 | — |
| 26 | 8-long-grass-left | 8 | 267-335, -42..-22 | phantom | long grass | playable | map wrong | 0.28 | 12-21 | 4-wood stays; 4-wood EV -0.015; aim +7.5 → +5.0 |
| 28 | 10-creek-bank-left | 10 | 283-306, -28..-22 | phantom | long grass | playable | unclear | 0.21 | 9-18 | — |

Not reviewed in detail: the findings ranked below about 30, each under 0.25% of shots once weighted by the edge distance.
`disagree.md` lists them, and the reviewed ones carry their verdict in the `reviewed` column. With all
patches applied (`--patched`), what remains is the rejected or unclear ones above plus slivers under 0.2% of shots.

## Decision impact per hole (all of the hole's map-wrong patches together)

| hole | final_decision pick (aim) | central model now: pick aim EV (margin) | with this hole's patches | change |
|---|---|---|---|---|
| 1 | Driver (+2.5) | Driver +2.5 3.957 (0.021) | 4-wood +7.5 3.982 (0.021) | **club flips**; best EV +0.025 |
| 18 | 2-wood (-7.5) | 2-wood -7.5 4.675 (0.020) | 2-wood -5.0 4.591 (0.005) | aim moves; best EV -0.084 |
| 11 | 4-wood (-2.5) | 4-wood -2.5 3.840 (0.077) | 4-wood +0.0 3.869 (0.047) | aim moves; best EV +0.030 |
| 16 | 2-wood (-7.5) | Driver -10.0 4.001 (0.001) | Driver -12.5 3.976 (0.015) | aim moves; best EV -0.024 |
| 9F | 4-wood (-25.0) | 2-wood -20.0 3.867 (0.002) | 4-wood -17.5 3.888 (0.048) | **club flips**; best EV +0.022 |
| 9B | Driver (-25.0) | Driver -25.0 3.966 (0.012) | 2-wood -22.5 3.961 (0.001) | **club flips**; best EV -0.005 |
| 13 | Driver (-10.0) | Driver -10.0 4.024 (0.009) | Driver -10.0 4.008 (0.025) | same; best EV -0.016 |
| 5 | Driver (-5.0) | Driver -5.0 3.904 (0.007) | 2-wood -2.5 3.907 (0.007) | **club flips**; best EV +0.003 |
| 17 | Driver (-5.0) | Driver -5.0 4.034 (0.054) | Driver -5.0 4.071 (0.020) | same; best EV +0.037 |
| 8 | 4-wood (+7.5) | 4-wood +7.5 3.945 (0.093) | 4-wood +7.5 3.918 (0.043) | same; best EV -0.027 |
| 2B | Driver (-5.0) | Driver -5.0 4.906 (0.022) | Driver -7.5 4.867 (0.046) | aim moves; best EV -0.039 |

Reading it:

* **1**: the right trees really do reach the fairway edge from ~305 out, which costs the driver 0.12. The 4-wood
  becomes best by 0.021. This is the biggest decision change. Re-run the Bayesian pick: the driver's
  current edge is 0.022.
* **9F**: adds the left clump and the tree line across at ~300, and moves the right clump. The 4-wood (the current
  final pick, a tie with the 2-wood) wins clearly (margin 0.048), and the driver drops 0.23.
* **9B**: Driver, 2-wood and 4-wood stay within 0.02 of each other. The point estimate flips Driver to 2-wood by 0.001,
  which is a tie, as before.
* **5**: Driver to 2-wood by 0.007 once the full bunker is in. This was already a tie (0.010 in final_decision).
* **18**: every club gains 0.07-0.11 because the long-grass bank is moved back. The 2-wood stays best, but its edge over the driver
  shrinks to 0.005.
* **8**: the driver gains 0.17 once the left long grass is back to where the audit put it. The 4-wood still wins by 0.04.
* Others (13, 17, 11, 2B, 16): aim shifts of 2.5-5 yds and EV changes of 0.04 or less. The pick does not change.

## Findings in detail

Coordinates are yds along the tee line and yds right (+) or left (-) of it. "Edge shift" is how far the evidence
edge sits beyond the hand edge, per along-row (median/max). Crops are in `spirit_hollow/qa_landing/crops/`, one per rank:
screenshot | NAIP 2023 | lidar canopy (green, by height) + long-grass layer (orange) + water (blue) + OSM (cyan dashed) |
vision2 | hand map. The disputed cells are in red and the auto-drafted patch is yellow dotted.

Caveats that apply throughout:
* Canopy patches make the whole canopy footprint "recovery" (TREE_SEVERITY applies). Under a big tree the ball is
  often playable, so for the canopy-overhang findings (11, 2B, 17, 1) the EV change is an upper bound.
* For the sand fixes, `REPLACE` in `proposed_patches.py` (edit the traced boxes in place) is cleaner than appending.
  Appended 'fairway' pieces move course.py's first-cut insertion point, which affects ~25 yd2 of the other hole-8 boxes.

### 1-trees-right-305 — hole 1 (map wrong)

- `1-mrec-324R20` (rank 1, missing): evidence trees, map playable; along 311-335, lat +4..+40 (centre 324, +21); edge shift 26 median / 29 max yds; 5.17% of shots; evidence means: lidar canopy 1.00, NAIP canopy 0.74, long-grass layer 0.00, vision2 trees/native/water/sand 0.83/0.06/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/01_1.png`
- What I saw: Woods right: from ~305 out the canopy (lidar 2019, NAIP 2023, and the dark tree texture in the screenshot) comes right to the fairway's right edge; the map leaves a 15-29 yd wedge of rough before its tree line.
- Proposed patch (append to `AUDIT_FIXES[1]`):

```python
('recovery', [(702, 1089), (687, 1104), (643, 1104), (619, 1084), (633, 1064), (629, 1054), (614, 1054), (594, 1084), (569, 1093), (540, 1078), (510, 1029), (511, 994), (491, 945), (501, 935), (624, 936), (639, 951)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | +2.5 → +0.0 | 3.957 → 4.073 (+0.116) |
| 2-wood | +5.0 → +5.0 | 3.978 → 4.003 (+0.025) |
| 4-wood | +7.5 → +7.5 | 3.980 → 3.982 (+0.001) |

Pick: Driver → 4-wood (margin 0.021 → 0.021).

### 18-creek-bank-right — hole 18 (map wrong)

- `18-pnat-292R22` (rank 2, phantom): map long grass, evidence playable; along 231-335, lat -8..+51 (centre 292, +22); edge shift 9 median / 15 max yds; 4.84% of shots; evidence means: lidar canopy 0.00, NAIP canopy -0.00, long-grass layer 0.00, vision2 trees/native/water/sand 0.08/0.04/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/02_18.png`
- What I saw: Creek bank right, 231-335: the long-grass polygon's fairway-side edge sits 9-15 yds inside where the tan bank starts in the screenshot zoom and where NAIP shows the unmown strip; vision2 (screenshot, LOHO) agrees (p(native) 0.04 on the strip). A 4-yd fringe of long grass is kept next to the evidence edge. NB this partly reverses the earlier landing-zone check's hole-18 fix (the 'tan bank starts right at the fairway edge' native polygon): see crops/zoom_18_340_830.png (photo | NAIP) before accepting.
- Proposed patch (append to `AUDIT_FIXES[18]`):

```python
('rough', [(371, 1228), (364, 1221), (387, 1171), (439, 1008), (476, 926), (496, 907), (529, 836), (540, 825), (564, 825), (579, 838), (572, 863), (559, 888), (487, 964), (481, 992), (464, 1011), (461, 1046), (441, 1064), (449, 1099), (429, 1131), (429, 1145), (409, 1174), (409, 1185)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -2.5 → +2.5 | 4.708 → 4.596 (-0.112) |
| 2-wood | -7.5 → -5.0 | 4.675 → 4.591 (-0.084) |
| 4-wood | -12.5 → -7.5 | 4.694 → 4.619 (-0.075) |

Pick: 2-wood → 2-wood (margin 0.020 → 0.005).

### 9F-trees-left-260 — hole 9F (map wrong)

- `9F-mrec-288L48` (rank 3, missing): evidence trees, map playable; along 261-312, lat -55..-34 (centre 288, -49); edge shift 21 median / 45 max yds; 3.02% of shots; evidence means: lidar canopy 1.00, NAIP canopy 0.77, long-grass layer 0.00, vision2 trees/native/water/sand 0.29/0.15/0.01/0.00, OSM water/bunker 0.00/0.00; crop `crops/03_9F.png`
- What I saw: Tree clump left at 261-312, -34..-55 (same clump as 9B 310-335 left): canopy in lidar, NAIP and the screenshot; the map has rough / first cut there.
- Proposed patch (append to `AUDIT_FIXES['9F']`):

```python
('recovery', [(303, 833), (290, 808), (300, 778), (308, 773), (305, 762), (313, 738), (338, 722), (324, 701), (333, 673), (341, 669), (352, 679), (377, 673), (385, 703), (395, 703), (399, 711), (388, 724), (402, 735), (407, 751), (389, 765), (371, 766), (366, 761), (354, 768), (345, 795), (321, 798), (324, 809), (338, 807), (343, 812), (334, 840)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -10.0 → -5.0 | 3.928 → 3.947 (+0.019) |
| 2-wood | -20.0 → -10.0 | 3.867 → 3.907 (+0.041) |
| 4-wood | -25.0 → -22.5 | 3.868 → 3.902 (+0.034) |

Pick: 2-wood → 4-wood (margin 0.002 → 0.005).

### 9F-trees-long-300 — hole 9F (map wrong)

- `9F-mrec-306L1` (rank 4, missing): evidence trees, map playable; along 294-318, lat -34..+15 (centre 307, -1); edge shift 14 median / 19 max yds; 1.59% of shots; evidence means: lidar canopy 1.00, NAIP canopy 0.78, long-grass layer 0.00, vision2 trees/native/water/sand 0.55/0.09/0.03/0.00, OSM water/bunker 0.00/0.00; crop `crops/04_9F.png`
- What I saw: Tree line across the hole at 294-318 (-34..+15): the traced fairway runs ~15 yds into the trees before the long-grass band.
- Proposed patch (append to `AUDIT_FIXES['9F']`):

```python
('recovery', [(580, 718), (562, 776), (532, 794), (520, 780), (505, 741), (470, 744), (457, 722), (422, 735), (405, 713), (415, 702), (573, 709)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -10.0 → -22.5 | 3.928 → 4.125 (+0.197) |
| 2-wood | -20.0 → -25.0 | 3.867 → 3.911 (+0.044) |
| 4-wood | -25.0 → -25.0 | 3.868 → 3.889 (+0.021) |

Pick: 2-wood → 4-wood (margin 0.002 → 0.022).

### 13-pot-bunkers-left — hole 13 (map wrong)

- `13-psan-297L19` (rank 5, phantom): map sand, evidence playable; along 294-300, lat -24..-14 (centre 298, -19); edge shift 7 median / 9 max yds; 1.77% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.00, long-grass layer 0.00, vision2 trees/native/water/sand 0.04/0.02/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/05_13.png`
- `13-msan-304L4` (rank 14, missing): evidence sand, map playable; along 302-307, lat -7..-1 (centre 304, -4); edge shift 6 median / 8 max yds; 0.51% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.06, long-grass layer 0.00, vision2 trees/native/water/sand 0.27/0.06/0.01/0.00, OSM water/bunker 0.00/1.00; crop `crops/14_13.png`
- `13-msan-317R2` (rank 23, missing): evidence sand, map playable; along 313-322, lat +0..+4 (centre 318, +2); edge shift 7 median / 8 max yds; 0.27% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.04, long-grass layer 0.00, vision2 trees/native/water/sand 0.04/0.04/0.06/0.00, OSM water/bunker 0.00/1.00; crop `crops/23_13.png`
- What I saw: Pot bunkers left: the photo and NAIP show two bunkers (a figure-8 at 270-292, -32..-15 and a larger one at 305-325, -14..+4). The map's top box at 294-300 is grass, and the upper bunker is ~2.5x the traced square. Boxes replaced by the OSM outlines (which sit on the NAIP sand).
- Proposed patch (append to `AUDIT_FIXES[13]`):

```python
('first_cut', [(418, 798), (410, 798), (417, 806), (418, 806)]),
('first_cut', [(402, 798), (402, 808), (404, 801), (410, 798)]),
('fairway', [(377, 894), (380, 894), (382, 891), (375, 886), (371, 880), (373, 876), (381, 871), (391, 870), (393, 872), (395, 889), (393, 894), (395, 894), (395, 890), (397, 890), (395, 848), (365, 848), (372, 892), (377, 892)]),
('fairway', [(358, 896), (358, 898), (361, 897), (370, 903), (374, 903), (379, 896)]),
('first_cut', [(358, 922), (362, 922), (360, 915), (358, 914)]),
('sand', [(382, 914), (390, 904), (395, 889), (393, 872), (391, 870), (381, 871), (373, 876), (371, 880), (375, 886), (382, 891), (374, 903), (370, 903), (361, 897), (357, 899), (355, 903), (354, 910), (356, 913), (360, 915), (363, 927), (366, 929), (372, 928), (380, 923), (382, 918)]),
('sand', [(415, 844), (420, 842), (426, 835), (427, 826), (423, 819), (423, 817), (433, 812), (437, 805), (436, 796), (434, 792), (431, 789), (427, 790), (424, 793), (422, 803), (419, 805), (417, 806), (410, 798), (404, 801), (402, 808), (403, 817), (410, 826), (408, 836), (409, 841)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -10.0 → -15.0 | 4.024 → 4.013 (-0.012) |
| 2-wood | -17.5 → -17.5 | 4.045 → 4.041 (-0.005) |
| 4-wood | -20.0 → -20.0 | 4.033 → 4.036 (+0.003) |
| Long iron | -20.0 → -20.0 | 4.131 → 4.131 (+0.000) |
| Mid iron | -17.5 → -17.5 | 4.276 → 4.276 (+0.000) |

Pick: Driver → Driver (margin 0.009 → 0.023).

### 9B-9F-tree-clump-right — hole 9B (map wrong)

- `9B-prec-285R20` (rank 6, phantom): map trees, evidence playable; along 268-297, lat +14..+32 (centre 286, +21); edge shift 13 median / 18 max yds; 1.82% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.04, long-grass layer 0.00, vision2 trees/native/water/sand 0.11/0.04/0.01/0.00, OSM water/bunker 0.00/0.00; crop `crops/06_9B.png`
- What I saw: Tree clump right of the fairway at 268-297 (9B) / 231-262 (9F): the map's clump starts at +14 (9B) / +6 (9F) but in NAIP the dark area there is the clump's shadow; the crowns (and the 2019 lidar canopy) start ~+30 (9B) / ~+25 (9F). The winter screenshot shows the shadow and leaning branches. The canopy edge is moved out 13-18 yds.
- Proposed patch (append to `AUDIT_FIXES['9B']`):

```python
('rough', [(479, 882), (469, 860), (476, 779), (483, 772), (557, 767), (564, 775), (541, 796), (545, 803), (537, 811), (530, 807), (511, 828), (518, 843), (502, 857), (506, 872)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -25.0 → -20.0 | 3.966 → 3.946 (-0.020) |
| 2-wood | -25.0 → -22.5 | 3.978 → 3.961 (-0.017) |
| 4-wood | -22.5 → -22.5 | 3.984 → 3.977 (-0.008) |

Pick: Driver → Driver (margin 0.012 → 0.015).

### 5-right-bunker-300 — hole 5 (map wrong)

- `5-msan-295R15` (rank 7, missing): evidence sand, map playable; along 291-304, lat +8..+25 (centre 295, +16); edge shift 6 median / 11 max yds; 1.43% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.00, long-grass layer 0.00, vision2 trees/native/water/sand 0.03/0.51/0.00/0.07, OSM water/bunker 0.00/1.00; crop `crops/07_5.png`
- What I saw: Right bunker ~300 out is a hook shape reaching 291-304, +8..+25 (photo, NAIP, OSM); the map's box stops at ~302. NOTE course.py AUDIT_FIXES has key 5 twice: the earlier '~2x the trace' box is silently dropped. Replaced by the OSM outline.
- Proposed patch (append to `AUDIT_FIXES[5]`):

```python
('fairway', [(535, 835), (501, 835), (510, 842), (512, 852), (505, 861), (505, 868), (525, 880), (528, 873), (527, 865), (531, 859), (535, 859)]),
('sand', [(482, 835), (476, 845), (475, 862), (483, 873), (490, 881), (493, 907), (501, 916), (509, 921), (524, 922), (529, 917), (532, 907), (542, 899), (551, 889), (554, 876), (547, 863), (539, 859), (531, 859), (527, 865), (528, 873), (526, 881), (505, 868), (505, 861), (512, 852), (510, 842), (504, 836), (496, 833)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -5.0 → -5.0 | 3.904 → 3.928 (+0.024) |
| 2-wood | -5.0 → -5.0 | 3.911 → 3.912 (+0.001) |
| 4-wood | -5.0 → -5.0 | 3.917 → 3.917 (+0.000) |

Pick: Driver → 2-wood (margin 0.007 → 0.005).

### 9F-tree-clump-right — hole 9F (map wrong)

- `9F-prec-252R16` (rank 8, phantom): map trees, evidence playable; along 231-270, lat +6..+25 (centre 252, +17); edge shift 16 median / 20 max yds; 1.54% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.04, long-grass layer 0.00, vision2 trees/native/water/sand 0.07/0.07/0.02/0.00, OSM water/bunker 0.00/0.00; crop `crops/08_9F.png`
- What I saw: Same clump from the 9F tee (see 9B-9F-tree-clump-right).
- Proposed patch (append to `AUDIT_FIXES['9F']`):

```python
('rough', [(504, 999), (493, 961), (493, 887), (547, 877), (569, 880), (573, 889), (537, 918), (534, 927), (540, 939), (528, 979), (537, 982), (540, 993), (528, 1000)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -10.0 → -10.0 | 3.928 → 3.922 (-0.006) |
| 2-wood | -20.0 → -17.5 | 3.867 → 3.854 (-0.012) |
| 4-wood | -25.0 → -22.5 | 3.868 → 3.848 (-0.020) |

Pick: 2-wood → 4-wood (margin 0.002 → 0.006).

### 17-lone-tree-right-310 — hole 17 (map wrong)

- `17-mrec-308R36` (rank 9, missing): evidence trees, map playable; along 295-320, lat +27..+46 (centre 308, +36); edge shift 19 median / 21 max yds; 1.18% of shots; evidence means: lidar canopy 1.00, NAIP canopy 0.81, long-grass layer 0.00, vision2 trees/native/water/sand 0.27/0.42/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/09_17.png`
- What I saw: A single large tree in the right rough at 298-320, +25..+45 (NAIP crown ~20 yds across, lidar canopy; visible in the screenshot); the map has rough there.
- Proposed patch (append to `AUDIT_FIXES[17]`):

```python
('recovery', [(497, 958), (498, 950), (488, 934), (497, 903), (516, 890), (548, 894), (557, 912), (548, 946), (520, 966), (514, 960)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -5.0 → -10.0 | 4.034 → 4.051 (+0.018) |
| 2-wood | -5.0 → -7.5 | 4.087 → 4.088 (+0.001) |
| 4-wood | -10.0 → -10.0 | 4.123 → 4.123 (+0.000) |

Pick: Driver → Driver (margin 0.054 → 0.037).

### 4-long-grass-left — hole 4 (evidence wrong)

- `4-mnat-273L31` (rank 10, missing): evidence long grass, map playable; along 260-283, lat -35..-27 (centre 273, -31); edge shift 9 median / 11 max yds; 1.81% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.00, long-grass layer 1.00, vision2 trees/native/water/sand 0.04/0.64/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/10_4.png`
- What I saw: vision_any's long-grass layer bleeds ~8 yds over the cart path; the photo zoom and NAIP show mown rough between the path and the fairway, as the audit's rough strip says.

### 11-canopy-left-245 — hole 11 (map wrong)

- `11-mrec-245L26` (rank 11, missing): evidence trees, map playable; along 238-253, lat -32..-20 (centre 245, -27); edge shift 10 median / 15 max yds; 0.77% of shots; evidence means: lidar canopy 1.00, NAIP canopy 0.82, long-grass layer 0.00, vision2 trees/native/water/sand 0.16/0.03/0.01/0.00, OSM water/bunker 0.00/0.00; crop `crops/11_11.png`
- `11-mrec-261L30` (rank 22, missing): evidence trees, map playable; along 256-266, lat -31..-29 (centre 262, -30); edge shift 6 median / 7 max yds; 0.27% of shots; evidence means: lidar canopy 1.00, NAIP canopy 0.53, long-grass layer 0.00, vision2 trees/native/water/sand 0.07/0.01/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/22_11.png`
- What I saw: Left of the fairway at 238-277: the canopy of the trees on the far side of the cart path overhangs the path and the left rough to ~-20 (lidar + NAIP crowns); the map stops the trees at ~-38 (trunks). Under-canopy lies are often playable, so this is the upper bound of the effect.
- Proposed patch (append to `AUDIT_FIXES[11]`):

```python
('recovery', [(373, 884), (349, 876), (329, 843), (333, 807), (350, 791), (362, 803), (353, 811), (365, 827), (401, 848), (401, 860)]),
('recovery', [(353, 835), (333, 815), (333, 787), (346, 775), (338, 759), (346, 751), (366, 771), (366, 787), (358, 795), (362, 803), (353, 811), (365, 823)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -25.0 → -25.0 | 4.669 → 4.675 (+0.006) |
| 2-wood | -2.5 → -2.5 | 4.240 → 4.249 (+0.009) |
| 4-wood | -2.5 → +0.0 | 3.840 → 3.869 (+0.030) |
| Long iron | +2.5 → +2.5 | 3.916 → 3.916 (-0.000) |
| Mid iron | +7.5 → +7.5 | 4.020 → 4.020 (+0.000) |

Pick: 4-wood → 4-wood (margin 0.077 → 0.047).

### 8-right-bunker-280 — hole 8 (map wrong)

- `8-psan-273R6` (rank 12, phantom): map sand, evidence playable; along 273-275, lat +5..+8 (centre 274, +6); edge shift 5 median / 6 max yds; 0.68% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.00, long-grass layer 0.00, vision2 trees/native/water/sand 0.14/0.05/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/12_8.png`
- What I saw: The kidney bunker at 272-295 right is drawn as a 75x70 px box, twice the sand area (photo, NAIP, OSM); the corners are fairway. NOTE AUDIT_FIXES has key 8 twice: the earlier grass-block fix for this bunker is silently dropped. Replaced by the OSM outline.
- Proposed patch (append to `AUDIT_FIXES[8]`):

```python
('fairway', [(520, 875), (520, 805), (445, 805), (447, 875), (480, 875), (472, 857), (459, 853), (453, 848), (448, 840), (448, 822), (452, 814), (467, 809), (476, 810), (483, 816), (486, 822), (484, 831), (488, 840), (514, 844), (518, 851), (517, 861), (513, 865), (496, 868), (486, 875)]),
('sand', [(518, 851), (514, 844), (505, 842), (495, 842), (488, 840), (484, 831), (486, 822), (483, 816), (476, 810), (467, 809), (458, 811), (452, 814), (448, 822), (448, 840), (453, 848), (459, 853), (472, 857), (476, 864), (478, 873), (482, 878), (496, 868), (506, 867), (513, 865), (517, 861)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | +7.5 → +7.5 | 4.175 → 4.130 (-0.045) |
| 2-wood | +5.0 → +7.5 | 4.038 → 4.008 (-0.030) |
| 4-wood | +7.5 → +10.0 | 3.945 → 3.931 (-0.013) |

Pick: 4-wood → 4-wood (margin 0.093 → 0.076).

### 9B-trees-left-310 — hole 9B (map wrong)

- `9B-mrec-325L41` (rank 13, missing): evidence trees, map playable; along 309-335, lat -55..-19 (centre 326, -42); edge shift 64 median / 76 max yds; 0.55% of shots; evidence means: lidar canopy 1.00, NAIP canopy 0.75, long-grass layer 0.00, vision2 trees/native/water/sand 0.35/0.14/0.02/0.00, OSM water/bunker 0.00/0.00; crop `crops/13_9B.png`
- What I saw: 9B left at 309-335 (-55..-19): the tree clump that 9F also shows; unmapped from the Gold tee.
- Proposed patch (append to `AUDIT_FIXES['9B']`):

```python
('recovery', [(257, 712), (236, 686), (237, 664), (223, 649), (223, 638), (276, 599), (361, 602), (375, 621), (356, 639), (323, 634), (311, 644), (314, 659), (299, 673), (285, 666), (277, 673), (277, 680), (295, 695), (298, 718), (286, 724)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -25.0 → -20.0 | 3.966 → 3.994 (+0.028) |
| 2-wood | -25.0 → -25.0 | 3.978 → 3.979 (+0.001) |
| 4-wood | -22.5 → -22.5 | 3.984 → 3.984 (+0.000) |

Pick: Driver → 2-wood (margin 0.012 → 0.006).

### 5-right-strip — hole 5 (map wrong)

- `5-prec-251R41` (rank 15, phantom): map trees, evidence playable; along 209-303, lat +33..+51 (centre 251, +42); edge shift 20 median / 32 max yds; 1.02% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.00, long-grass layer 0.00, vision2 trees/native/water/sand 0.04/0.44/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/15_5.png`
- What I saw: The 'trees' strip right (+33..+45, 209-303) is rough and the cart path in the screenshot and NAIP, no canopy in lidar; only a couple of small trees at ~200. OB (houses) beyond is unchanged.
- Proposed patch (append to `AUDIT_FIXES[5]`):

```python
('rough', [(605, 1224), (591, 1214), (597, 1207), (590, 1201), (585, 996), (591, 989), (609, 991), (615, 974), (614, 956), (586, 947), (582, 864), (592, 857), (625, 886), (647, 920), (651, 1000), (649, 1201), (636, 1209), (628, 1202), (635, 1195), (617, 1189), (618, 1199), (608, 1207), (615, 1217)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -5.0 → -2.5 | 3.904 → 3.895 (-0.008) |
| 2-wood | -5.0 → -2.5 | 3.911 → 3.905 (-0.006) |
| 4-wood | -5.0 → -2.5 | 3.917 → 3.914 (-0.003) |

Pick: Driver → Driver (margin 0.007 → 0.010).

### 13-pond-corner — hole 13 (map wrong)

- `13-pwat-283R20` (rank 16, phantom): map water, evidence playable; along 279-286, lat +18..+23 (centre 283, +20); edge shift 6 median / 7 max yds; 0.51% of shots; evidence means: lidar canopy 0.05, NAIP canopy -0.00, long-grass layer 0.00, vision2 trees/native/water/sand 0.04/0.11/0.01/0.00, OSM water/bunker 0.00/0.00; crop `crops/16_13.png`
- What I saw: The pond's top-left corner (279-286, +18..+23) is drawn square; the shore is rounded (photo, NAIP, OSM). Small.
- Proposed patch (append to `AUDIT_FIXES[13]`):

```python
('rough', [(482, 904), (476, 900), (478, 882), (493, 875), (498, 880)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -10.0 → -10.0 | 4.024 → 4.008 (-0.016) |
| 2-wood | -17.5 → -15.0 | 4.045 → 4.037 (-0.008) |
| 4-wood | -20.0 → -20.0 | 4.033 → 4.030 (-0.003) |
| Long iron | -20.0 → -20.0 | 4.131 → 4.131 (+0.000) |
| Mid iron | -17.5 → -17.5 | 4.276 → 4.276 (+0.000) |

Pick: Driver → Driver (margin 0.009 → 0.022).

### 16-woods-left-270 — hole 16 (map wrong)

- `16-snat-286L47` (rank 17, swap): map long grass, evidence trees; along 271-299, lat -55..-39 (centre 286, -47); edge shift 19 median / 33 max yds; 1.62% of shots; evidence means: lidar canopy 1.00, NAIP canopy 0.75, long-grass layer 0.00, vision2 trees/native/water/sand 0.85/0.04/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/17_16.png`
- What I saw: Left: the woods reach down to ~271 (canopy in lidar/NAIP and dark trees in the photo); the map switches from trees to the long-grass field at 300 (a straight line at y=900).
- Proposed patch (append to `AUDIT_FIXES[16]`):

```python
('recovery', [(275, 1016), (255, 1016), (244, 1009), (231, 971), (206, 953), (207, 915), (224, 898), (280, 898), (287, 905), (286, 940), (279, 954), (286, 961), (289, 992)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -10.0 → -12.5 | 4.001 → 3.976 (-0.024) |
| 2-wood | -7.5 → -10.0 | 4.002 → 3.991 (-0.011) |
| 4-wood | -10.0 → -10.0 | 4.048 → 4.048 (-0.000) |

Pick: Driver → Driver (margin 0.001 → 0.015).

### 13-tree-right-300 — hole 13 (map wrong)

- `13-mrec-296R33` (rank 18, missing): evidence trees, map playable; along 291-304, lat +25..+41 (centre 297, +34); edge shift 10 median / 16 max yds; 0.41% of shots; evidence means: lidar canopy 1.00, NAIP canopy 0.69, long-grass layer 0.00, vision2 trees/native/water/sand 0.11/0.28/0.01/0.00, OSM water/bunker 0.00/0.00; crop `crops/18_13.png`
- What I saw: Tree(s) right of the fairway above the pond at 291-317, +21..+43 (grey winter crown in the photo, NAIP crown, lidar); the map has fairway / first cut.
- Proposed patch (append to `AUDIT_FIXES[13]`):

```python
('recovery', [(500, 878), (492, 865), (499, 860), (496, 855), (506, 844), (505, 836), (520, 827), (531, 834), (526, 842), (534, 847), (538, 860), (528, 871)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -10.0 → -10.0 | 4.024 → 4.031 (+0.007) |
| 2-wood | -17.5 → -17.5 | 4.045 → 4.046 (+0.000) |
| 4-wood | -20.0 → -20.0 | 4.033 → 4.033 (+0.000) |
| Long iron | -20.0 → -20.0 | 4.131 → 4.131 (+0.000) |
| Mid iron | -17.5 → -17.5 | 4.276 → 4.276 (+0.000) |

Pick: Driver → Driver (margin 0.009 → 0.002).

### 2B-trees-right-290 — hole 2B (map wrong)

- `2B-mrec-298R23` (rank 19, missing): evidence trees, map playable; along 294-302, lat +22..+24 (centre 298, +23); edge shift 6 median / 7 max yds; 0.42% of shots; evidence means: lidar canopy 1.00, NAIP canopy 0.68, long-grass layer 0.00, vision2 trees/native/water/sand 0.06/0.23/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/19_2B.png`
- `2B-snat-288R35` (rank 29, swap): map long grass, evidence trees; along 279-298, lat +30..+42 (centre 289, +35); edge shift 71 median / 76 max yds; 0.86% of shots; evidence means: lidar canopy 1.00, NAIP canopy 0.86, long-grass layer 0.00, vision2 trees/native/water/sand 0.64/0.14/0.00/0.00, OSM water/bunker 0.00/0.00
- What I saw: Right at 279-302: a tree clump inside the long-grass band (+25..+42) whose canopy overhangs the cart path to +22 (photo, NAIP, lidar).
- Proposed patch (append to `AUDIT_FIXES['2B']`):

```python
('recovery', [(529, 818), (509, 792), (508, 773), (515, 765), (527, 765), (539, 776), (544, 802)]),
('recovery', [(581, 877), (545, 833), (531, 772), (538, 764), (546, 764), (582, 797), (583, 824), (614, 838)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -5.0 → -5.0 | 4.906 → 4.896 (-0.010) |
| 2-wood | -5.0 → -5.0 | 4.928 → 4.920 (-0.008) |
| 4-wood | +0.0 → +0.0 | 4.970 → 4.961 (-0.008) |

Pick: Driver → Driver (margin 0.022 → 0.023).

### 16-trees-right-265 — hole 16 (unclear)

- `16-prec-264R23` (rank 20, phantom): map trees, evidence playable; along 262-267, lat +22..+25 (centre 264, +24); edge shift 6 median / 7 max yds; 0.42% of shots; evidence means: lidar canopy 0.00, NAIP canopy -0.00, long-grass layer 0.00, vision2 trees/native/water/sand 0.08/0.04/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/20_16.png`
- What I saw: NAIP shows a dark patch (shadow or low shrubs) at +20..+28; lidar has no canopy until +30. 0.4% of shots; left as is.

### 2B-long-grass-left-320 — hole 2B (map wrong)

- `2B-pnat-322L39` (rank 21, phantom): map long grass, evidence playable; along 300-335, lat -47..-35 (centre 322, -39); edge shift 10 median / 16 max yds; 0.63% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.02, long-grass layer 0.00, vision2 trees/native/water/sand 0.09/0.09/0.01/0.00, OSM water/bunker 0.00/0.00; crop `crops/21_2B.png`
- What I saw: Left at 300-335: mown rough runs to the bank of the water at ~-47 (photo, NAIP); the long-grass band is drawn 10-16 yds further in (to -35).
- Proposed patch (append to `AUDIT_FIXES['2B']`):

```python
('rough', [(284, 806), (263, 765), (262, 742), (238, 712), (225, 663), (231, 644), (247, 658), (255, 658), (266, 638), (285, 638), (293, 645), (295, 794)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -5.0 → -7.5 | 4.906 → 4.873 (-0.033) |
| 2-wood | -5.0 → -5.0 | 4.928 → 4.920 (-0.007) |
| 4-wood | +0.0 → +0.0 | 4.970 → 4.970 (+0.000) |

Pick: Driver → Driver (margin 0.022 → 0.047).

### 17-long-grass-left — hole 17 (map wrong)

- `17-mnat-303L42` (rank 24, missing): evidence long grass, map playable; along 273-335, lat -51..-34 (centre 304, -42); edge shift 12 median / 15 max yds; 0.65% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.00, long-grass layer 1.00, vision2 trees/native/water/sand 0.07/0.67/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/24_17.png`
- What I saw: Left at 273-335: the field's long grass starts at the cart path (~-38) in NAIP, the photo and both classifiers; the map starts it 12-15 yds further left.
- Proposed patch (append to `AUDIT_FIXES[17]`):

```python
('native', [(248, 1005), (243, 999), (290, 823), (307, 804), (327, 807), (334, 816), (316, 849), (308, 930), (274, 1002), (254, 1000)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | -5.0 → +0.0 | 4.034 → 4.048 (+0.014) |
| 2-wood | -5.0 → -5.0 | 4.087 → 4.090 (+0.003) |
| 4-wood | -10.0 → -10.0 | 4.123 → 4.123 (+0.000) |

Pick: Driver → Driver (margin 0.054 → 0.042).

### 2F-pond-corner — hole 2F (unclear)

- `2F-pwat-283L36` (rank 25, phantom): map water, evidence playable; along 281-285, lat -38..-36 (centre 283, -37); edge shift 5 median / 5 max yds; 0.26% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.04, long-grass layer 0.00, vision2 trees/native/water/sand 0.07/0.65/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/25_2F.png`
- What I saw: 5 yds at one corner of the creek polygon: at the tolerance; not worth a patch.

### 8-long-grass-left — hole 8 (map wrong)

- `8-pnat-312L29` (rank 26, phantom): map long grass, evidence playable; along 267-335, lat -42..-22 (centre 312, -30); edge shift 12 median / 21 max yds; 0.28% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.02, long-grass layer 0.00, vision2 trees/native/water/sand 0.02/0.03/0.00/0.00, OSM water/bunker 0.00/0.00; crop `crops/26_8.png`
- What I saw: Long grass left at 267-335 ends 12-21 yds further left than drawn (screenshot and NAIP: mown to ~-38). This is exactly the earlier audit's rough patch that is lost to the duplicate key 8 in AUDIT_FIXES; restored verbatim.
- Proposed patch (append to `AUDIT_FIXES[8]`):

```python
('rough', [(245, 650), (325, 650), (330, 700), (340, 900), (333, 975), (330, 975), (310, 900), (278, 800), (250, 700)]),
```

| club | aim before → after | EV before → after |
|---|---|---|
| Driver | +7.5 → -2.5 | 4.175 → 4.037 (-0.138) |
| 2-wood | +5.0 → +5.0 | 4.038 → 3.987 (-0.051) |
| 4-wood | +7.5 → +5.0 | 3.945 → 3.930 (-0.015) |

Pick: 4-wood → 4-wood (margin 0.093 → 0.057).

### 10-creek-bank-left — hole 10 (unclear)

- `10-pnat-298L24` (rank 28, phantom): map long grass, evidence playable; along 283-306, lat -28..-22 (centre 298, -25); edge shift 9 median / 18 max yds; 0.21% of shots; evidence means: lidar canopy 0.00, NAIP canopy 0.00, long-grass layer 0.00, vision2 trees/native/water/sand 0.07/0.08/0.00/0.00, OSM water/bunker 0.00/0.00
- What I saw: Tan creek-bank strip at 283-306 may be ~5-9 yds narrower than drawn; 0.2% of shots.

