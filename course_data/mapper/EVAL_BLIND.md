# Blind mapper evaluation: why the agent layers helped or hurt (evaluator's analysis)

**Truth-bearing. A mapper agent must never read this file** (it is excluded by the `EVAL_*` rule in BRIEF.md).
Written 2026-11-02 by the evaluator from the first five blind mapper runs (error budget v1, n = 4000, seed 31).
Scripts (not committed, scratchpad): an overlay of AUTO / AUTO + AGENT / truth effective lies in each mapper corridor
frame (`error_budget.truth_stack` + `effective`), per-edit precision, and re-scoring of mechanically modified agent
layers through `error_budget.score_course` (same machinery as `eval_mapper.py`).

## 1. Result of the blind runs

| course | style | match AUTO -> AGENT | regret AUTO -> AGENT | fixed | broken |
|---|---|---|---|---|---|
| gateway_national (Back) | open, prairie / fescue | 9 -> 11 / 13 | 0.424 -> 0.144 | 9, 11, 13 | 16 |
| ellis (Blue) | parkland, scattered trees | 11 -> 11 / 14 | 0.375 -> 0.325 | - | - |
| blue_hills (Black) | parkland, lidar trees | 14 -> 13 / 14 | 0.051 -> 0.071 | - | 10 (reference tie) |
| pine_dunes (Gold) | pine forest, waste sand | 11 -> 11 / 14 | 0.099 -> 0.104 | - | - |
| coldwater (Blue) | links / prairie | 10 -> 7 / 14 | 0.472 -> 0.483 | 2, 3 | 4, 7, 14, 15, 18 |
| pooled | | 55 -> 53 / 69 | 1.42 -> 1.13 | 5 | 7 |

Regret fell 21 %, but every course with long grass shows the same failure: native drawn hugging the fairway.

## 2. Biggest causes (ranked by decision impact)

### 2.1 Native drawn on mown rough next to the fairway (coldwater, gateway; 6 of 7 broken holes)

Long grass is priced almost like OB by the planner (`tee_strategy._lie_mixture`: half lost = stroke and distance,
half hacked out), so native inside the driver landing dispersion flips Driver to a 3/4-wood.

Measured in the corridor frames (180-330 yds along, both sides, every 5 yds):

| | coldwater | gateway_national |
|---|---|---|
| mown-rough width (fairway edge -> native) where both have native, median (IQR) | agent 5.3 (3.4-10) vs truth 8.7 (4-17) yds | agent 8.0 (6-14) vs truth 13.1 (3-19) yds |
| native where truth has none within 45 yds: median gap to the fairway | 4.3 yds (n = 244 samples) | 6.9 yds (n = 95) |
| agent native extra area (landing window 180-320, +/-50) | 27.6k sq yds, ~85 % on truth rough, ~7 % on truth fairway | 21.2k sq yds, ~97 % on truth rough |

Per-edit precision (share of an edit's visible added area that truth has as native):

| edit kind | coldwater | gateway |
|---|---|---|
| `beyond_fairway`, w <= 5 | 0.37 (13 edits) | 0.47 (3) |
| `beyond_fairway`, w > 5 | 0.41 (3) | 0.55 (18) |
| `poly` / `ell` (traced patches) | 0.66 (10) | 0.76 (4) |
| confidence high | 0.80 | 0.78 |
| confidence medium | 0.33 | 0.54 |

The coldwater agent (20 minutes) laid `beyond_fairway` strips with w = 3-5 yds over the full window (120-400) on
most holes; every one of them sits on mown rough on its fairway side. The traced high-confidence blocks were right.

Broken holes, checked against the photo myself (0.3 m NAIP + the other year):

| hole | agent edit | photo | truth | verdict |
|---|---|---|---|---|
| coldwater 7 | native strip w = 4 left, between fairway and tree line | dark mottled band = tree shade / leaf litter on mown rough | rough | agent wrong vs photo |
| coldwater 15 | native strip w = 4 right, fairway -> cart path | smooth, paler mown rough, mower texture | rough (truth notes: "wide tan mown rough" is the judgement call on 6, 15, 18) | agent wrong vs photo |
| coldwater 14 | native strip w = 3 left whole length + w = 10 right between paths | left: mown rough with one cut-hay strip near the trees (230-350); right: mottled, partly tall | native only as the hay strip and a strip between the paths | agent wrong (template strip) |
| coldwater 4 | high-confidence triangle at the fairway end 285-400 drawn to x = -5 | tall grass starts ~10-15 yds right of a ditch / mown strip | native from x ~ +15 | agent edge 10-15 yds too far in (high confidence, survives the keep-out) |
| coldwater 18 | native w = 8 left (truth: rough to the ditch), w = 5 right (truth: native ~10 yds beyond the path) | left band is green-mottled rough in both years | rough / water | partly convention (tan mown rough), partly agent too close |
| gateway 16 | native w ~ 2-3 on both sides 140-340 | 5-8 yds of mown rough, then tufted native | native from ~8-10 yds | agent wrong vs photo |

The brief encouraged this: "long grass may be drawn generously: it never covers a fairway, trees or water". Precedence
does not protect mown rough, and `beyond_fairway` makes a whole-window strip one line of JSON.

### 2.2 Tree crowns: noise, not a cause

* Inner tree edge, agent minus truth (median yds, + = agent farther from the line): coldwater -1.6, gateway -1.1,
  ellis 0.0 (IQR -5..+5), blue_hills +1.5, pine_dunes +2.7. The lidar-course truth trees (point-cloud canopy) reach
  1.5-3 yds closer to the fairway than the auto / agent trees.
* Growing every auto tree edge mechanically does not help: pine_dunes +2 yds 11 -> 13 matches (regret 0.099 -> 0.095),
  +4 yds 12; blue_hills +2 yds 14 -> 11 (regret 0.051 -> 0.053), +4 yds 10 (0.065). Plans move by a few yds of aim,
  regret barely changes. No blanket growth rule.
* blue_hills: 132 single-crown polygons, precision 0.32; most sit 15-25+ yds from the fairway. Hole 10 "broke" on a
  reference tie (2-wood vs 4-wood within the tie margin). Effect within noise.
* ellis: crowns of scattered trees drawn as stand polygons (hole 9: two polygons, 2.1k sq yds extra; truth = single
  crowns with grass between). Precision of tree adds 0.33. Neutral on the plan.

### 2.3 Pine Dunes waste sand: mostly a truth convention, no decision effect

The truth (truth/pine_dunes/trace.py docstring) takes sand only from OSM and the canopy from the point cloud, so the
waste strips along tree edges that are not in OSM are trees or rough in the truth. On the photo several agent sand
edits are right (hole 11 right 120-240, hole 2 right tree edge: open tan sand in both years); some are wrong (tan
strips at a shaded tree edge, 11 left; sand drawn 5 yds inside the visible strip on 2). Precision vs truth 0.02, but
dropping all agent sand leaves the plan identical to AUTO (11 / 14, 0.099 vs agent 0.104): the planner prices sand
like a fairway bunker, so it barely matters. Rule kept: waste = `sand`, only open sand outside the crowns.

### 2.4 Truth-convention differences (not agent errors)

* Coldwater / Veenker-style corridor truths are coarse: rectangular native strips and boxy fairway polygons in places
  (e.g. coldwater 12, 14, 18); ~7 % of the coldwater agent's extra native lies on truth "fairway" that is mown rough
  on the photo. Some apparent native "misses" are the truth's straight-edged boxes.
* Dry mown rough vs fescue is the truth author's main stated judgement call on coldwater (6, 15, 18): rough where
  mower stripes / smooth texture are visible. The new long-grass rule 1 matches that convention.

## 3. Rule experiments (agent layers modified mechanically, re-scored; coldwater + gateway, 27 tee shots)

| variant | match | regret |
|---|---|---|
| AUTO | 19 | 0.896 |
| AUTO + AGENT (as run) | 18 | 0.627 |
| clip all native within 8 yds of the package fairway | 20 | 0.575 |
| clip all native within 12 yds | 20 | 0.638 |
| drop thin strips (`beyond_fairway` w <= 5) | 21 | 0.730 |
| drop every native that is not confidence high | 21 | 0.892 |
| **clip native that is not confidence high within 10 yds (kept: high)** | **21** | **0.467** |
| same, 8 yds | 20 | 0.582 |

Clipping everything (incl. high confidence) loses coldwater 3, where truth native does come to the fairway; dropping
all unsure native loses gateway's real fescue (gateway 9 -> 0.632). The confidence-aware 10-yd keep-out is the best
and is now enforced by `write_layers.py`. Small sample: two courses, one agent each.

## 4. Changes made (BRIEF.md, write_layers.py)

* BRIEF step 2: "generously" removed; precedence does not protect rough; new sections "How the planner uses your map",
  "Long-grass rules" (two-year texture test, mown-rough width, enforced keep-out, no template strips, check the gap
  table) and "Trees, sand, OB rules" (single crowns for scattered trees, skip far isolated crowns, waste = sand only
  outside the canopy, no low-confidence OB).
* `write_layers.py`: `NATIVE_KEEPOUT = 10` yds (non-high native clipped, logged with the area), checks in `review.md`
  (high-confidence native near the fairway, beyond_fairway w < 10, sand on the canopy, big tree polygon over open
  ground) and a per-hole "Native gap to the fairway" table. Test `test_write_layers_native_keepout_and_checks`.
  Replaying the coldwater run through the new `write_layers.py`: 15 of its native edits are clipped (the strips),
  the high-confidence blocks are kept and flagged.

## 5. Validation (fresh blind mappers with the new brief; not yet run)

| course | set | set file | why |
|---|---|---|---|
| annbriar | Black | v2 | the only other truth course with much long grass (16 native zones) + trees + sand |
| veenker | Blue | v1 | parkland, same corridor-truth author as coldwater; tests tree edges and restraint |
| buffalo_ridge | Buffalo | v2 | open, lots of sand / water, no native in truth: tests the keep-out / restraint |
| eagle_knoll | Back | v1 | lake / trees with a little native |
| coldwater (re-run) | Blue | v1 | the failing course, fresh agent: remove the old `coldwater/edits.json` + layers first (git history keeps them) so the new agent cannot read the previous run |

All have a package with NAIP and `vision_any/<slug>/raw` (hag + two NAIP years). Score with
`python3 course_data/mapper/eval_mapper.py --set all --courses <slugs>`; success = no course loses matches and pooled
regret falls, with native extra area per hole well below the first runs (coldwater 27.6k sq yds).

## 6. Not verified

* The keep-out was tested by modifying finished layers, not by an agent working under the new brief.
* Two native courses only; the 10-yd threshold may be wrong for courses with very narrow mown rough (links with
  fescue at the fairway edge); high confidence is the escape hatch.
* Tree findings rest on two lidar courses; the photo check of crowns was by eye on a few holes (blue_hills 10, 17;
  ellis 9; pine_dunes 2, 11).

## Round 2 (revised brief: 10-yd native keep-out, two-year texture rule) — coordinator, 2026-11-02

Fresh blind mappers, error budget n=4000 seed 31. AUTO → AUTO + AGENT.

| course | set | match | regret | fixed / broken |
|---|---|---|---|---|
| coldwater (redo) | Blue | 10 → 10 /14 | 0.472 → 0.420 | 3 / 4 (round 1: 10 → 7, 0.472 → 0.483) |
| veenker | Blue | 9 → 9 /13 | 0.193 → 0.119 | 12 / 14 |
| eagle_knoll | Back | 14 → 14 /14 | 0.026 → 0.054 | – |
| buffalo_ridge | Buffalo | 12 → 12 /13 | 0.076 → 0.110 | – |
| annbriar | Black | 8 → 8 /14 | 0.293 → 0.293 | – |
| **round 2 pooled** | | **53 → 53** | **1.060 → 0.996 (−6 %)** | |

Coldwater native in the landing corridors: round 1 extra 27,600 sq yds / precision ~0.40; round 2 extra 4,372 /
precision ~0.70, recall ~0.36. Round-2 native recall stays low on Annbriar (agent erased auto native; missing area
grew 23.8k → 25.2k) — conservative, no plan effect.

Both rounds, 9 courses (round 1 Coldwater replaced by round 2): matches 98 → 99, regret 2.009 → 1.640 (−18 %).
Gains concentrate on native/prairie courses (Gateway −0.28, Coldwater −0.05, Veenker −0.07 via a highway-mislabelled
water fix); well-mapped parkland courses move ±0.03 (aim nudges, within seed noise at n=4000).

Decision: the mapper becomes a standard build step (cheap, never broke a course in round 2), with highest priority
on courses with prairie/links character; long-grass recall is the open item (big tufted blocks found, thin native
bands mostly left out by design).

## Round 3 plan: S2 native suggestions as a mapper input (evaluator, 2026-11-02)

Coordinator decision: the Sentinel-2 native P (s2_longgrass.md, 23-course model) is not an automatic layer; the
mapper sees it as a suggestion and confirms / rejects it on the photos. The mapper's native recall was ~0.36 (round
2), S2's LOCO recall on the KS native courses 0.62 but with parkland false native (Ellis 2 / 9, Spirit Hollow 17).

Tooling (commit "Mapper: S2 native suggestions"):
* `vision_any/s2/native_model.py` + `native_model/`: `loco/<slug>.npz` = the LOCO grids of the 23-course run (fold
  model without that course; copied from `pred_s2_23.npz`, uint8 P x 200), `full_model.txt` = the same LightGBM on
  all 23 courses for new courses (features from the stack + `g10_blind`, the package masks at 10 m; checked identical
  to `prep_grid10.py` on Sand Creek Station).
* `render_inputs.py`: `hNN_corridor_s2.png` [P heat over the photo | candidates on the photo | candidates on the 2nd
  year], an S2 column in `inputs.md`, `edits.template.json` `holes.<n>.s2_suggested.{L,R}` (P >= 0.5 clusters minus
  the package fairway / first cut / green / water / sand / trees, >= 150 sq yds, empty `decision`).
* `write_layers.py`: `accept` -> `add native` (agent confidence + evidence, keep-out applies), `reject` / `replace`
  -> nothing (evidence required); undecided candidates listed under Checks; "S2 suggestions" table in review.md;
  decisions recorded in `agent_zones.geojson` `properties.reviewed.<n>.s2` (for the accept-rate analysis).
* Imagery fallback `course_data/imagery/<slug>/` (Spirit Hollow's package predates package imagery); the brief's
  sparse checkout adds the S2 stack, the native model and those 4 imagery files, and excludes
  `course_data/spirit_hollow/**` (its hand map).

Round-3 courses (no mapper folder exists; the round-1 Ellis run was removed, git history keeps it):

| slug | set | why |
|---|---|---|
| prairie_dunes | Blue | native both sides of every hole; S2 LOCO IoU 0.78, auto 1 / 14 matches |
| buffalo_dunes | Blue | sandhill prairie between fairways; S2 IoU 0.67 |
| sand_creek_station | Championship | native beyond ~12 yds of mown rough |
| mariah_hills | Blue | native islands; S2 broke 6 / 13 as a layer |
| eagle_bend | Gold | S2 misses its green mottled native (IoU 0.03): tests the photo-only path |
| ellis | Blue | parkland control: S2 false native on 2 / 9 (drought tan rough 2023, green 2021) |
| spirit_hollow | Black | parkland control: S2 broke 17 |

Score: `python3 course_data/mapper/eval_mapper.py --set all --courses <slugs>` (the 5 KS courses are truth_sets_v2,
Ellis / Spirit Hollow v1). Success = the KS courses gain most of S2's error-budget gain (Prairie Dunes 1 -> 12,
Buffalo Dunes 7 -> 12 as a layer) while Ellis 2 / 9 and Spirit Hollow 17 do not break.


## Round 3 results (S2-assisted brief, 7 blind mappers) — coordinator, 2026-11-02

Pooled over 98 tee shots: match 50 → 66, same club 63 → 73, regret 6.165 → 2.253 strokes; 18 fixed, 2 broken.
Native long-grass corridor area missing 296k → 151k sq yds (extra 13k → 33k).

Takeaways:
- Prairie/links courses (Prairie Dunes, Buffalo Dunes) are where the mapper pays: −0.9 and −1.4 strokes per course.
- Parkland controls held: Ellis rejected 56/59 S2 hints (drought-tan rough), no breaks; Spirit Hollow +1 match, no breaks.
- Eagle Bend (mixed): mapper rejected all 13 S2 hints and added no native; Will's notes say native on 2 L+R, 3 L, 5 L, 6 L.
  Hole 2 got worse (0.097 → 0.155). Too strict on mixed courses — brief fix needed.
- Mariah Hills: 2 broken (6, 10); hole 7 negative regret means the reference plan is not optimal there (truth tie); hole 9 unscored.
- Tee moves: 2 total (Sand Creek 1 Championship, Spirit Hollow 18 Gold); tee errors unchanged.

### Full table (generated)

## Pooled

| | tee shots | match | same club | same club or tie | regret (strokes) |
|---|---|---|---|---|---|
| AUTO | 98 | 50/98 (51%) | 63 | 68 | 6.165 |
| AUTO + AGENT | 98 | 66/98 (67%) | 73 | 82 | 2.253 |

Holes fixed by the agent: 18; broken: 2. Reference ties among all holes: 12.

Landing-corridor area vs truth (sq yds, 180-320 yds along the truth tee line, +/-50; summed over holes):

| layer | truth | AUTO missing / extra | AUTO + AGENT missing / extra |
|---|---|---|---|
| bunkers | 13206 | 1739 / 1424 | 1739 / 1649 |
| fairway | 475627 | 72368 / 8582 | 72368 / 8582 |
| long_grass | 305799 | 296477 / 13084 | 150926 / 33230 |
| ob | 5380 | 2397 / 10283 | 2397 / 8657 |
| trees | 129294 | 56115 / 13642 | 48998 / 17344 |
| water | 28177 | 2139 / 10494 | 2565 / 8433 |

## Per course

| course | set | mapper | tee shots | match AUTO -> AGENT | same club | regret | fixed | broken | tee err median (measured truth tees) |
|---|---|---|---|---|---|---|---|---|---|
| ellis | Blue | mapper-ellis (blind) | 14 | 11 -> 11 | 12 -> 12 | 0.375 -> 0.293 | - | - | 0.8 (14, 0 > 10) -> 0.8 (14, 0 > 10) |
| spirit_hollow | Black | mapper-spirit_hollow-3 | 14 | 7 -> 8 | 10 -> 11 | 0.892 -> 0.729 | 6 | - | 10.5 (14, 7 > 10) -> 10.5 (14, 7 > 10) |
| sand_creek_station | Championship | mapper-agent sand_creek_station (map3) | 14 | 12 -> 12 | 13 -> 13 | 0.259 -> 0.258 | - | - | 2.7 (3, 0 > 10) -> 2.7 (3, 0 > 10) |
| eagle_bend | Gold | mapper-eagle_bend | 14 | 7 -> 8 | 9 -> 9 | 0.515 -> 0.565 | 7 | - | 4.1 (7, 1 > 10) -> 4.1 (7, 1 > 10) |
| prairie_dunes | Blue | mapper-prairie_dunes-3 | 14 | 1 -> 7 | 2 -> 7 | 1.649 -> 0.720 | 7, 8, 12, 13, 16, 18 | - | 5.8 (4, 0 > 10) -> 5.8 (4, 0 > 10) |
| buffalo_dunes | Blue | mapper-buffalo_dunes-blue | 14 | 7 -> 13 | 7 -> 13 | 1.623 -> 0.208 | 7, 10, 13, 14, 15, 16 | - | 12.1 (2, 1 > 10) -> 12.1 (2, 1 > 10) |
| mariah_hills | Blue | mapper-mariah_hills-blue | 14 | 5 -> 7 | 10 -> 8 | 0.852 -> -0.520 | 1, 3, 14, 18 | 6, 10 | 2.3 (9, 0 > 10) -> 2.3 (9, 0 > 10) |

## Holes whose plan the agent changed

| course | hole | truth | AUTO | AUTO + AGENT | match | regret |
|---|---|---|---|---|---|---|
| ellis | 5 | Driver -2 | Driver +5 | Driver +2 | True -> True | 0.018 -> 0.0086 |
| ellis | 9 | Driver -2 | Driver +5 | Driver +0 | True -> True | 0.029 -> 0.0066 |
| ellis | 10 | Driver +2 | Driver +2 | Driver +5 | True -> True | 0.0 -> 0.0009 |
| ellis | 12 | Driver -5 | Driver -8 | Driver -5 | True -> True | 0.0044 -> -0.0 |
| ellis | 15 | 4-wood +12 | Driver +2 | Driver +10 | False -> False | 0.1044 -> 0.0575 |
| spirit_hollow | 4 | Driver -12 | Driver -5 | Driver -18 | False -> False | 0.0579 -> 0.0183 |
| spirit_hollow | 5 | 4-wood -8 | 4-wood -5 | 4-wood -2 | True -> True | 0.0001 -> 0.0013 |
| spirit_hollow | 6 | 4-wood -22 (tie) | Driver -40 | 4-wood -20 | False -> True | 0.1289 -> -0.0002 |
| spirit_hollow | 17 | Driver +12 (tie) | Driver +0 | Driver +2 | True -> True | 0.0007 -> 0.0051 |
| sand_creek_station | 1 | Driver -2 | Driver +10 | Driver -5 | True -> True | 0.0004 -> -0.0016 |
| sand_creek_station | 5 | Driver -8 | Driver -5 | Driver -8 | True -> True | -0.0002 -> -0.0 |
| sand_creek_station | 12 | Driver -2 | Driver -5 | Driver +0 | True -> True | 0.0018 -> 0.011 |
| sand_creek_station | 18 | 4-wood -2 | 4-wood -22 | 4-wood -20 | True -> True | 0.0257 -> 0.0135 |
| eagle_bend | 2 | 4-wood +0 | Driver +5 | Driver +10 | False -> False | 0.0973 -> 0.1549 |
| eagle_bend | 7 | Driver +5 | Driver -40 | Driver +5 | False -> True | 0.0072 -> 0.0 |
| eagle_bend | 9 | 4-wood +0 (tie) | Driver +0 | Driver -2 | False -> False | 0.0245 -> 0.0233 |
| prairie_dunes | 1 | 4-wood +32 | Driver +22 | Driver +20 | False -> False | 0.1643 -> 0.2064 |
| prairie_dunes | 3 | Driver -2 | Driver -12 | 4-wood +8 | False -> False | -0.0064 -> 0.0591 |
| prairie_dunes | 6 | 4-wood +15 | Driver +15 | Driver +10 | False -> False | 0.1183 -> 0.1333 |
| prairie_dunes | 7 | 4-wood -2 | Driver +5 | 4-wood -2 | False -> True | 0.0989 -> 0.0037 |
| prairie_dunes | 8 | 4-wood -32 | Driver -22 | 4-wood -32 | False -> True | 0.2014 -> 0.0035 |
| prairie_dunes | 11 | Driver +32 | Driver +28 | Driver +32 | True -> True | 0.0433 -> 0.0045 |
| prairie_dunes | 12 | 4-wood -2 | Driver +0 | 4-wood +0 | False -> True | 0.2271 -> 0.0162 |
| prairie_dunes | 13 | 4-wood +22 | Driver +2 | 4-wood +20 | False -> True | 0.1891 -> 0.013 |
| prairie_dunes | 14 | 4-wood +22 | Driver +0 | 2-wood +12 | False -> False | 0.1034 -> 0.0423 |
| prairie_dunes | 16 | 4-wood -28 | Driver -20 | 4-wood -28 | False -> True | 0.0934 -> -0.0005 |
| prairie_dunes | 17 | 4-wood +12 (tie) | Driver +10 | Driver +8 | False -> False | 0.004 -> 0.0171 |
| prairie_dunes | 18 | 4-wood -8 | Driver +2 | 4-wood -10 | False -> True | 0.2403 -> 0.0476 |
| buffalo_dunes | 1 | Driver -2 (tie) | Driver -5 | Driver -8 | True -> True | 0.0026 -> 0.0176 |
| buffalo_dunes | 2 | 4-wood +10 | 4-wood +10 | 4-wood +12 | True -> True | -0.0022 -> 0.0194 |
| buffalo_dunes | 3 | 4-wood +5 | 4-wood +5 | 4-wood +8 | True -> True | -0.005 -> 0.0024 |
| buffalo_dunes | 7 | 4-wood +18 (tie) | 2-wood +10 | 4-wood +18 | False -> True | 0.005 -> 0.0013 |
| buffalo_dunes | 10 | 4-wood -20 | Driver +8 | 4-wood -15 | False -> True | 0.5084 -> 0.0252 |
| buffalo_dunes | 13 | 4-wood -10 | Driver -5 | 4-wood -10 | False -> True | 0.1404 -> 0.0025 |
| buffalo_dunes | 14 | 4-wood -10 | Driver +12 | 4-wood -8 | False -> True | 0.4031 -> -0.0003 |
| buffalo_dunes | 15 | 4-wood +0 | Driver -8 | 4-wood +0 | False -> True | 0.2428 -> 0.0012 |
| buffalo_dunes | 16 | 4-wood -10 | Driver +5 | 4-wood -10 | False -> True | 0.1882 -> -0.001 |
| mariah_hills | 1 | Driver +20 | Driver +8 | Driver +12 | False -> True | 0.0197 -> 0.002 |
| mariah_hills | 2 | 4-wood +18 (tie) | Driver +12 | Driver +20 | False -> False | 0.0183 -> 0.0889 |
| mariah_hills | 3 | Driver +0 | Driver +10 | Driver +2 | False -> True | 0.0297 -> 0.0 |
| mariah_hills | 4 | 4-wood +2 | Driver +2 | Driver -2 | False -> False | 0.0313 -> 0.054 |
| mariah_hills | 6 | Driver -18 | Driver -18 | Driver -28 | True -> False | -0.0008 -> 0.0287 |
| mariah_hills | 7 | Driver +40 (tie) | Driver +0 | 4-wood +80 | False -> False | 0.6083 -> -0.7362 |
| mariah_hills | 9 | Driver -38 | Driver +28 | 4-wood +30 | False -> False | None -> None |
| mariah_hills | 10 | Driver -2 (tie) | Driver +5 | 4-wood +0 | True -> False | 0.0382 -> 0.0041 |
| mariah_hills | 12 | Driver +0 | Driver +0 | Driver +5 | True -> True | 0.0005 -> 0.0094 |
| mariah_hills | 13 | Driver +15 | Driver +0 | Driver -5 | True -> True | 0.0257 -> 0.0 |
| mariah_hills | 14 | 4-wood -5 | Driver -10 | 4-wood -5 | False -> True | 0.0301 -> 0.0032 |
| mariah_hills | 15 | 4-wood +20 | 4-wood +15 | 4-wood +18 | True -> True | 0.0046 -> -0.0002 |
| mariah_hills | 18 | Driver +15 | Driver +8 | Driver +10 | False -> True | 0.0435 -> 0.0224 |

## Round 3 follow-up: Eagle Bend native, Mariah Hills breaks (evaluator, 2026-11-02)

Method: truth native / trees overlaid on the mapper's own panels (NAIP 2021 / 2023, corridor frame), and the agent
layers modified mechanically and re-scored with `eval_mapper.py` (n=4000, seed 31; one change per variant).

### Eagle Bend (Gold): why no native

* **S2 did not point at the golfer's areas.** On 3, 5, 6 there was no candidate at all (P < 0.5 everywhere left);
  on 2 the only one was a 350 sq yd strip right at 138-172 yds, outside the landing zone. All 13 hints were on other
  holes (7, 9, 11, 13, 15, 18). So the mapper's only path to this native was the photos, and it took none.
* **The brief's texture rules read this native as mown rough.** Here native is green and mottled in NAIP 2021 and
  tan / streaky in 2023 (dry year), with a mowing line (often the cart path) in the same place in both years and
  smooth, striped turf inside it. The round-2 rules said native is "tan / textured / tufted", "if it is green and
  smooth in the other year it is mown rough" and "a dark, mottled band along a tree line is shade": the green year
  became the reason to reject. The S2 section added a course-level prior ("on a parkland course expect to reject
  most"), and the mapper pasted one rejection text ("mown parkland rough ... green, smooth or mowing stripes") on
  11 of 13 candidates and wrote "no native seen (parkland mown rough)" on holes it never marked per side.
* **Hole 2 got worse because of a correct tree.** The one hole-2 edit is a lidar crown at x -38, 260-290; the truth
  has the same crown. With native missing on both sides, the crown pushes the aim right (Driver +5 -> +10).
  Dropping it: 0.097 (as AUTO). The fix is the native, not the tree.
* Truth convention: native = everything beyond 10 yds of the OSM fairway on the golfer's sides (`native_beyond`,
  w 10 +/-5). The photos show the mowing line 12-20 yds out on these holes; the score does not care:

| variant (eagle_bend, 14 tee shots) | match | regret |
|---|---|---|
| AUTO | 7 | 0.515 |
| AGENT as run | 8 | 0.565 |
| AGENT without the hole-2 crown | 8 | 0.507 |
| AGENT + native drawn at the photo mowing line (2 L w20 / R w15, 3 L w15, 5 L w12, 6 L w12; 150-345) | **10** | **0.306** |
| same, with truth's w 10 | 10 | 0.302 |

  (fixes 2 and 5; 3 and 6 stay matched with lower regret.) A mapper that marks these four sides at its own measured
  edge gets the whole gain; the edge position is not the issue, the yes / no per side is.

### Mariah Hills (Blue): 6 and 10

| variant | hole 6 | hole 10 | course match / regret |
|---|---|---|---|
| AGENT as run | Driver -28, broken (0.029) | 4-wood +0, broken (0.004) | 7 / -0.520 |
| without hole 6 native edit 0 | fixed | broken | 8 / -0.550 |
| without hole 10 crown (edit 1) | broken | Driver -2, match (0.005) | 8 / -0.520 |
| without hole 10 native oval (edit 0) | broken | Driver +8 (0.058) | 7 / -0.466 |

* **Hole 6 = agent edit (mostly agent error).** Edit 0 is one native polygon on the right from 262 to 400 yds whose
  fairway-side edge runs at x 3-5 (7 yds off the fairway after the keep-out clip, `review.md` gap 7 / 7). At 262-330
  the photo shows smooth mown rough between the fairway and the native island (the island starts ~25-30 yds out,
  where the truth box starts); the polygon was drawn as one block instead of following the island. Above ~330 the
  2023 photo does show native nearer the fairway that the truth's coarse boxes (+/-10 yds, "islands only") leave
  out: that part is a truth-convention difference, but the club change comes from the 262-330 part.
* **Hole 10 = a lidar crown at the fairway edge (x -24, 283), not in the truth; reference tie.** The truth plan is a
  tie (Driver -2 vs 4-wood), the agent picks 4-wood with lower regret than AUTO (0.038 -> 0.004). Not a real break.
  The agent's native oval matches the truth island and helps (removing it costs 0.054).
* **Hole 7 negative regret (-0.74)**: regret = EV on the truth map of the agent's (club, aim point) minus EV of the
  truth map's own plan. Negative means the truth plan is not the optimum of its own map: the truth pick, Driver
  +40, sits exactly on the planner's +/-40 aim bound of the round-3 scoring, and the agent plan (4-wood aimed +80,
  round the dog-leg past the large native island) is evaluated on the truth map at an aim point that search never
  reached. A reference artefact (search bound on a dog-leg; the truth pick is also a tie), not an agent gain to
  bank. The adaptive aim bound now on the branch (d8b4b41e / d7447e68: widen to 60 where the best aim sits on the
  bound) should shrink it; re-score Mariah Hills after it. **Hole 9 None**: truth aims Driver -38 (left of the island), AUTO and AGENT aim +28 / +30
  (right of it); the aim points are > 80 yds apart (`SAME_PLACE`), so regret is undefined for both. Not agent-related.

### Changes (BRIEF.md brief, write_layers.py, render_inputs.py)

* Long-grass rule 1 rewritten: **the mowing line first, then texture** — native sits behind a second mowing line
  in the same place in both years with coarser grass outside, *whatever its colour* (green-mottled in a wet year,
  tan in a dry one); mown rough has no such line (smooth to the trees, or tan one year / smooth green the other); an
  irrigation edge seen in one year only is not a mowing line; "shade" limited to ~10 yds of the canopy; courses mix
  parkland and native holes, decide each side on its own (no "parkland course" verdict). Step 2 item 1 and the
  second-year check say the same; "leaving unsure unmarked" is the safe default *near the fairway*, and a whole
  missed side in the landing zone is named as the other common miss.
* S2 section: the course-level prior removed; rejections from each candidate's own panel; **S2 is often silent on
  green-in-summer native and narrow bands**, so a side with no candidate still needs a verdict.
* Per-side verdicts (tooling): `edits.template.json` holes get `long_grass: {"L": "", "R": ""}`
  (`"native: <edits>"` / `"none: <what both years show>"`); `write_layers.py` lists under Checks an empty /
  missing verdict, a "native" verdict with no native edit on that side, a "none" verdict with one, and the same S2
  rejection text on > 3 candidates; `review.md` gets a "Long grass per side" table and `agent_zones.geojson`
  `reviewed.<n>.long_grass`. Layers are unchanged (no new auto-native). Test
  `test_long_grass_verdicts_and_same_evidence`.

### Parkland controls

The new tooling does not change any layer, so re-scoring Ellis / Spirit Hollow with it is identical by construction.
The risk is behavioural: a mapper that now accepts what it used to reject. Bound (mechanical): accept every S2
candidate the round-3 mapper rejected (Ellis 56, Spirit Hollow 36; medium confidence, so the keep-out applies):

| course | AUTO | AGENT as run | AGENT + every rejected S2 hint accepted |
|---|---|---|---|
| ellis (56 accepted) | 11 / 0.375 | 11 / 0.293 | 10 / 0.398 (breaks 2: Driver +40 -> 4-wood +10, +0.096) |
| spirit_hollow (36 accepted) | 7 / 0.892 | 8 / 0.729 | 7 / 0.733 (breaks 17, the S2 hint known from round 3: +0.026) |

Even the worst case (every hint accepted) costs ~0.1 stroke per parkland course, because the 10-yd keep-out
removes the near-fairway part of unsure native; the KS gain from marking the right sides is ~0.26 on Eagle Bend
alone. Spirit Hollow 4 / 6 keep their round-3 fixes in this variant.

On the photos the Ellis false hints (2 / 9) are tan rough in 2023 with an irrigation edge and one smooth green sheet
in 2021, with no mowing line in either year: rule 1 rejects them explicitly. Not verified: an agent working under
the new brief (only a blind re-run tests that).


## Round 4 results (mowing-line brief 47fd3e0e; eagle_bend, mariah_hills, ellis) — coordinator, 2026-11-02

Scored with DECIDE_ADAPTIVE_AIM=0 V2_ADAPTIVE_AIM=0 so it compares with round 3.

| course | round 3 match / regret | round 4 match / regret | broken r3 -> r4 |
|---|---|---|---|
| eagle_bend | 8 / 0.565 | 8 / 0.586 | 0 -> 0 |
| mariah_hills | 7 / -0.520 | 8 / -0.323 | 2 -> 1 (13) |
| ellis (control) | 11 / 0.293 | 11 / 0.334 | 0 -> 0 |

Native corridor missing 66.0k -> 41.0k sq yds (extra 11.3k) over the three.

Takeaways:
- The brief change did not unlock Eagle Bend: the mapper found native only on hole 2 LEFT (owner: 2 L+R, 3 L, 5 L, 6 L).
  One-sided native is worse than none on a hole that has both sides: hole 2 aim moved further right (0.097 -> 0.200).
- Mariah: hugging fixed on 6; 13 now breaks (4-wood -2 vs Driver +15); hole 7 / 9 remain reference artefacts.
- Ellis: still no breaks; slight regret rise (h17 high-confidence strips 0-9 yds off the fairway).
- Decision: keep the round-4 brief (no parkland breaks, fewer Mariah breaks). Photo-only native recall on mixed
  courses is the ceiling -> product path is a per-side native confirm tap for low-confidence / one-sided holes
  (and golfer local knowledge), not more brief tuning.

### Full table (generated)

## Pooled

| | tee shots | match | same club | same club or tie | regret (strokes) |
|---|---|---|---|---|---|
| AUTO | 42 | 23/42 (55%) | 31 | 33 | 1.742 |
| AUTO + AGENT | 42 | 27/42 (64%) | 30 | 34 | 0.597 |

Holes fixed by the agent: 5; broken: 1. Reference ties among all holes: 6.

Landing-corridor area vs truth (sq yds, 180-320 yds along the truth tee line, +/-50; summed over holes):

| layer | truth | AUTO missing / extra | AUTO + AGENT missing / extra |
|---|---|---|---|
| bunkers | 2228 | 345 / 1009 | 345 / 1009 |
| fairway | 192104 | 26902 / 4386 | 26902 / 4386 |
| long_grass | 66002 | 66002 / 0 | 41037 / 11262 |
| ob | 3024 | 1376 / 6345 | 1376 / 6198 |
| trees | 57933 | 26596 / 8073 | 19184 / 11849 |
| water | 6769 | 3 / 421 | 813 / 421 |

## Per course

| course | set | mapper | tee shots | match AUTO -> AGENT | same club | regret | fixed | broken | tee err median (measured truth tees) |
|---|---|---|---|---|---|---|---|---|---|
| ellis | Blue | map4_ellis | 14 | 11 -> 11 | 12 -> 12 | 0.375 -> 0.334 | - | - | 0.8 (14, 0 > 10) -> 0.8 (14, 0 > 10) |
| eagle_bend | Gold | mapper-eagle_bend-4 | 14 | 7 -> 8 | 9 -> 9 | 0.515 -> 0.586 | 7 | - | 4.1 (7, 1 > 10) -> 4.1 (7, 1 > 10) |
| mariah_hills | Blue | mapper-mariah_hills-blue | 14 | 5 -> 8 | 10 -> 9 | 0.852 -> -0.323 | 1, 3, 17, 18 | 13 | 2.3 (9, 0 > 10) -> 2.3 (9, 0 > 10) |

## Holes whose plan the agent changed

| course | hole | truth | AUTO | AUTO + AGENT | match | regret |
|---|---|---|---|---|---|---|
| ellis | 5 | Driver -2 | Driver +5 | Driver +0 | True -> True | 0.018 -> 0.003 |
| ellis | 9 | Driver -2 | Driver +5 | Driver +0 | True -> True | 0.029 -> 0.0066 |
| ellis | 10 | Driver +2 | Driver +2 | Driver +5 | True -> True | 0.0 -> 0.0009 |
| ellis | 12 | Driver -5 | Driver -8 | Driver -5 | True -> True | 0.0044 -> -0.0 |
| eagle_bend | 2 | 4-wood +0 | Driver +5 | Driver +12 | False -> False | 0.0973 -> 0.2 |
| eagle_bend | 7 | Driver +5 | Driver -40 | Driver +5 | False -> True | 0.0072 -> 0.0 |
| eagle_bend | 9 | 4-wood +0 (tie) | Driver +0 | 2-wood +0 | False -> False | 0.0245 -> 0.0054 |
| eagle_bend | 13 | Driver -2 | Driver +2 | Driver -2 | True -> True | 0.0142 -> -0.0008 |
| eagle_bend | 14 | Driver -2 | Driver -2 | Driver +2 | True -> True | -0.0003 -> 0.0096 |
| mariah_hills | 1 | Driver +20 | Driver +8 | Driver +18 | False -> True | 0.0197 -> -0.0008 |
| mariah_hills | 2 | 4-wood +18 (tie) | Driver +12 | Driver +20 | False -> False | 0.0183 -> 0.0889 |
| mariah_hills | 3 | Driver +0 | Driver +10 | Driver +8 | False -> True | 0.0297 -> 0.0171 |
| mariah_hills | 4 | 4-wood +2 | Driver +2 | Driver +0 | False -> False | 0.0313 -> 0.0385 |
| mariah_hills | 7 | Driver +40 (tie) | Driver +0 | 4-wood +80 | False -> False | 0.6083 -> -0.7362 |
| mariah_hills | 9 | Driver -38 | Driver +28 | Driver -40 | False -> False | None -> 0.1671 |
| mariah_hills | 12 | Driver +0 | Driver +0 | Driver +5 | True -> True | 0.0005 -> 0.0094 |
| mariah_hills | 13 | Driver +15 | Driver +0 | 4-wood -2 | True -> False | 0.0257 -> 0.0253 |
| mariah_hills | 14 | 4-wood -5 | Driver -10 | Driver +5 | False -> False | 0.0301 -> 0.0274 |
| mariah_hills | 15 | 4-wood +20 | 4-wood +15 | 4-wood +18 | True -> True | 0.0046 -> -0.0002 |
| mariah_hills | 17 | 4-wood -40 (tie) | Driver -35 | 4-wood -40 | False -> True | 0.0033 -> 0.0024 |
| mariah_hills | 18 | Driver +15 | Driver +8 | Driver +15 | False -> True | 0.0435 -> 0.001 |

## Native-side confirm tap, offline (2026-11-02)

`product/native_confirm.py` asks "native grass along hole n?" (L / R / both / none) on the holes where an answer
changes the club or moves the aim > 10 yds (re-decided per answer state), ranked by expected regret avoided under
priors from the mapper's per-side verdicts; "yes" inserts native beyond max(10, mapped rough width) of the fairway,
130-400 along; "no" cuts native on that side. Answers simulated from the truth (native >= 300 sq yds within 30 yds
of the fairway, 150-345 along). Full table: `EVAL_native_confirm.md` (truth-bearing).

| | AUTO | AGENT | ASK <= 2 | ASK <= 4 | ASK <= 6 | ASK all 14 |
|---|---|---|---|---|---|---|
| 7 courses, 98 tee shots: match / regret | 50 / 6.06 | 66 / 2.51 | 69 / 1.91 (14 q) | 70 / 1.65 (26 q) | 69 / 1.30 (38 q) | 71 / 1.06 (98 q) |

Eagle Bend 8 / 0.588 -> 9 / 0.299 (4 q) -> 10 / 0.196 (6 q). Mariah Hills loses (8 -> 7 at 4 q): its native is
islands 25+ yds out; "yes" inserts at 10 yds and the 30-yd "near" answer rule says "no" on sides whose islands the
mapper drew. Next: on "yes", keep the mapper's own native edge on that side when it has one (insert only where
it drew none); a second tap for "starts near / far" on island courses.

### Island fix (2026-11-02, follow-up)

Tried on a "yes" side: keep the mapper / auto native as drawn and add the band only on 10-yd along slices with
nothing native within 40 yds of the fairway (`native_confirm.covered_along`, `set_side(islands=True)`). Same
eval (DECIDE_ADAPTIVE_AIM=0 V2_ADAPTIVE_AIM=0, n = 4000, seed 31), match / regret at ASK <= 4 and <= 6:

| course | plain band (committed) <= 4 / <= 6 | island rule on every yes <= 4 / <= 6 | env B plain <= 4 / <= 6 | env B plain + "well out" 2nd tap <= 4 / <= 6 |
|---|---|---|---|---|
| ellis | 11 / 0.335 · 11 / 0.335 | 11 / 0.335 · 11 / 0.335 | 11 / 0.334 · 11 / 0.334 | same |
| spirit_hollow | 8 / 0.617 · 8 / 0.305 | (not run: checkout lacked spirit_hollow/) | 9 / 0.670 · 10 / 0.343 | same |
| sand_creek_station | 13 / 0.233 · 13 / 0.233 | 13 / 0.228 · 13 / 0.228 | 13 / 0.257 · 13 / 0.257 | same |
| eagle_bend | 9 / 0.299 · 10 / 0.196 | 9 / 0.299 · 10 / 0.196 | 9 / 0.297 · 10 / 0.194 | same |
| prairie_dunes | 9 / 0.514 · 9 / 0.510 | **7 / 0.847 · 7 / 0.847** | 9 / 0.438 · 9 / 0.435 | same |
| buffalo_dunes | 13 / 0.152 · 13 / 0.138 | 13 / 0.175 · 13 / 0.175 | 13 / 0.148 · 13 / 0.133 | same |
| mariah_hills (AGENT 8 / -0.317; env B 8 / -0.323) | 7 / -0.505 · 5 / -0.420 | **8 / -0.516** · 6 / -0.431 | 8 / -0.509 · 6 / -0.426 | same |
| pooled, 6 courses without Spirit Hollow | 62 / 1.028 · 61 / 0.992 | 61 / 1.368 · 60 / 1.350 | 63 / 0.965 · 62 / 0.927 | same |
| pooled, 7 courses (AGENT: 66 / 2.51 committed, 67 / 2.51 env B) | 70 / 1.645 · 69 / 1.297 | - | 72 / 1.635 · 72 / 1.270 | same (ASK all 74 / 1.015 -> 74 / 0.989) |

- The island rule on every "yes" fixes Mariah Hills (7 -> 8 at <= 4, back to AGENT) but breaks Prairie Dunes
  (9 -> 7): its mapped native is near the fairway but patchy, so the slices it touches keep their mown gaps and
  the "yes" no longer changes holes 1 and 5 (they drop out of the selection). Pooled <= 4 is worse (62 / 1.03 ->
  61 / 1.37 on the six comparable courses): **gate failed, not shipped as the default.** A "fill outward from the
  island's inner edge" variant was worse on the first three courses (ellis 11 -> 10, sand creek 13 -> 12) and was
  stopped.
- "Near the fairway / well out" second tap (simulated: a "yes" side with < 300 sq yds of truth native within 15
  yds of the fairway is "well out", island rule there only): identical to the plain band at <= 2 / 4 / 6 (the
  asked holes' plans do not move), a hair better only when every hole is asked (regret 1.015 -> 0.989). Not
  asked on the pages; `apply_answers.py` and `native_confirm.apply_answer` take an optional `out`.
- Env B = the full scorer: the first sparse checkout (the committed numbers' environment, which its AGENT row
  reproduced exactly) lacked `course_data/elevation/*.py`, `library/*.py`, `vision_any/s2/*.py` and the top-level
  `spirit_hollow/`; with them AUTO / AGENT move (Spirit Hollow AUTO 6 -> 7, Prairie Dunes AGENT 0.789 -> 0.720), so
  before / after is compared within one environment. In env B the plain band no longer costs Mariah Hills a match
  at <= 4 (8 / -0.509 vs AGENT 8 / -0.323); it still does at <= 6 (holes 18, 12: 4-wood / aim shifts the truth does
  not make). `EVAL_native_confirm.md` / `.json` are the env B plain-band run.

## Automatic native sides: a classifier with no agent and no taps (2026-11-03)

`product/native_auto.py` classifies hole **sides** (not pixels): per par-4/5 hole and side of the tee line, 150-345
yds along, label-free features from the cached rasters and the package -> logistic regression -> on a "yes" side
the same band the golfer's "yes" tap draws (`native_confirm.set_side`, beyond 10 yds of the fairway, 130-400 along).
Nothing is erased. Scored by `mapper/eval_native_auto.py` (error_budget.score_course, n = 4000, seed 31,
DECIDE_ADAPTIVE_AIM=0 V2_ADAPTIVE_AIM=0 as rounds 3-4; two `--score` halves merged, full checkout). Full table:
`EVAL_native_auto.md` / `eval_native_auto.json` (truth-bearing).

**Set-up.** 18 truth courses with mapper frames (Colbert Hills and Buffalo Ridge left out: their truth has no
long grass traced), 500 sides, 193 with native (eval_native_confirm.truth_answers: >= 300 sq yds of truth native
within 30 yds of the package fairway). Leave one course out: the held-out course's p comes from the fit on the
other 17; its threshold is chosen on those 17 only (lowest t with inner LOCO side precision >= 0.9: 0.65-0.75).
The S2 input is itself the LOCO grid of the 23-course S2 model (`native_model/loco/<slug>.npz`), so no truth of the
held-out course enters anywhere.

**Features and what carried the signal** (side AUC, LOCO, 500 sides):

| feature group | what | AUC alone |
|---|---|---|
| S2 | mean P / share P >= 0.5 of the S2 native model, open ground 10-40 yds off the fairway (6-20, 20-50) | 0.88 |
| geo | share of that band that is open (not trees, water, sand, OB, any fairway) | 0.86 |
| HAG | 3DEP HAG >= 0.25 / 0.5 m share, band minus fairway / mown-rough reference | 0.61 |
| NAIP / CIR | 3x3 m / 5x5 m texture of grey and NIR, NDVI, ExG, band minus the 1-6 yd mown rough, two years | 0.64 |
| all + course context (course means of the side features, within-course z) | | **0.93** |

* **Lidar height does not separate native from mown rough here.** Within a course the HAG excess of the band over
  the fairway points the *wrong* way on most native courses (side AUC Gateway 0.12, Eagle Bend 0.16, Mariah Hills
  0.32, Sand Creek 0.35) and the right way only on Ellis (0.95). The 3DEP product is 2 m, leaf-off / winter
  (Sand Creek 2011-02, Mariah 2014-01, Eagle Bend 2006-05; Prairie Dunes / Spirit Hollow / Pine Dunes are a
  DSM - DTM fallback), stored in 0.25 m steps: dormant or snow-flattened grass rarely lands above the first step, and
  the steps that do fire are shrubs / tree edges, which sit on the parkland sides. The 0.3-1 m vs < 0.1 m contrast
  needs leaf-on point statistics (`raw2`, Actions only) or a newer flight, not this raster.
* NAIP texture is weak and course-dependent (Mariah 0.93 on NIR texture, Gateway 0.19); single-date summer NAIP
  does not see the mowing line reliably.
* The model leans on the course-level S2 share (coefficient +1.85: "is this a prairie course"), then open ground
  (+1.19). Cart-path mowing lines were not used (no path layer in the packages).

**Side level at the held-out threshold:** 145 TP / 13 FP / 48 FN (precision 0.92, recall 0.75). Misses are
concentrated: Eagle Bend 0 / 12 (green-in-summer native, S2 silent; its native sides do rank highest on the
course, p 0.21-0.37), Annbriar 2 / 16 (green prairie), Spirit Hollow 11 / 18. False sides: Ellis 2 (2 R, 7 R:
drought-tan rough, the known S2 false hint), Spirit Hollow 4, Mariah Hills 4 (islands 25+ yds out: the 30-yd
"near" label says no), Sand Creek 2, Gateway 1.

**Course gate (added after the first held-out pass broke Ellis 2 and 7).** The classifier alone (CLS) broke Ellis
2 (Driver +40 -> 4-wood +2, +0.17) and 7: two confident sides on a course whose other 26 sides are quiet. Rule:
a course gets automatic native only when >= 25 % of its sides reach the threshold. Shares on the 18 courses are
0-0.07 (all no-native and parkland courses, Annbriar, Eagle Bend) or 0.54-1.0 (the native courses), so every gate
between 0.08 and 0.53 makes the same decisions, and a gate chosen inside the folds (lowest g giving inner precision
>= 0.92) does too. Honest caveat: the gate's existence was prompted by the Ellis result; it has not yet met a course
that played no part in its design (the 7 courses being traced are the test).

**Plans, held out, per course (match / regret; AUTO = the package the mapper reviewed; GATED = the zero-tap
product rule; +TAP2 = then <= 2 native-confirm taps ranked by the classifier p, answers simulated from the truth;
ORACLE = the band on every truth "yes" side):**

| course | AUTO | GATED (0 taps) | GATED + TAP2 | ORACLE | mapper AGENT (round 3) |
|---|---|---|---|---|---|
| sand_creek_station | 12 / 0.259 | 12 / 0.293 | 13 / 0.187 (2) | 14 / 0.095 | 12 / 0.258 |
| prairie_dunes | 1 / 1.649 | **12 / 0.116** | 12 / 0.116 (0) | 12 / 0.116 | 7 / 0.720 |
| mariah_hills | 5 / 0.852 | 7 / -0.380 | 7 / -0.380 (2) | 8 / -0.464 | 7 / -0.520 |
| buffalo_dunes | 7 / 1.623 | **13 / 0.088** | 13 / 0.088 (2) | 13 / 0.062 | 13 / 0.208 |
| eagle_bend | 7 / 0.515 | 7 / 0.515 (gate shut) | **9 / 0.254** (2) | 10 / 0.136 | 8 / 0.565 |
| ellis (control) | 11 / 0.375 | 11 / 0.375 (gate shut) | 11 / 0.375 (2) | 11 / 0.428 | 11 / 0.293 |
| spirit_hollow (control) | 7 / 0.892 | 7 / 0.886 | **9 / 0.290** (2) | 9 / 0.379 | 8 / 0.729 |
| blue_hills (control) | 14 / 0.051 | 14 / 0.051 | 14 / 0.051 (0) | 14 / 0.051 | (round 1) |
| gateway_national | 9 / 0.424 | 9 / 0.303 | 10 / 0.169 (1) | 10 / 0.158 | |
| coldwater | 10 / 0.472 | 10 / 0.416 | 10 / 0.416 (2) | 9 / 0.383 | |
| annbriar | 8 / 0.293 | 8 / 0.293 (gate shut) | 9 / 0.286 (2) | 10 / 0.180 | |
| 7 no-native courses (eagle_knoll, pine_dunes, veenker, la_nickell, rivercut, gustin, osage_national) | 76 / 1.380 | 76 / 1.380 (unchanged, gate shut on all) | 76 / 1.380 (4) | 76 / 1.384 | |
| **pooled, 18 courses, 250 tee shots** | **167 / 8.785** | **186 / 4.336** | **193 / 3.232** (21 taps) | 196 / 2.908 | |
| the 7 round-3 courses (98 tee shots) | 50 / 6.165 | 69 / 1.893 | 74 / 0.930 (12) | 77 / 0.752 | 66 / 2.253; + ASK <= 4: 72 / 1.635 |

* **Mariah Hills hole 7** is the reference artefact of round 3 (truth Driver +40 on the +/-40 aim bound; any
  4-wood-round-the-island plan scores -0.73). Without it: AUTO 0.244 -> GATED 0.353 on Mariah, 18-course pooled
  AUTO 8.18 -> GATED 5.07 -> GATED + TAP2 3.97 (ORACLE 3.64), per 14-tee-shot round 0.46 -> 0.28 -> 0.22 (ORACLE
  0.20). The band at 10 yds is too close for Mariah's islands (12, 13 break); that is the band geometry, the ORACLE
  has it too.
* **Fixed / broken vs AUTO.** GATED fixes 26 holes and breaks 7: Sand Creek 8, Mariah Hills 10 (reference tie), 12,
  13, Spirit Hollow 17 (reference tie, the S2-known hint), Gateway 3, Coldwater 18 (each 0.03-0.05 strokes).
  GATED + TAP2 fixes 33, breaks the same 7.
* **Parkland controls hold:** Ellis and Blue Hills identical to AUTO (gate shut), Spirit Hollow 7 -> 7 matches with
  regret 0.892 -> 0.886 (fixes 6, flips the tie on 17), and all 7 no-native courses unchanged. Without the gate
  Ellis loses 2 matches (11 -> 9, 0.375 -> 0.562).
* **Against the agent path** on the same 7 courses: the zero-tap layer (69 / 1.893) beats the blind mapper
  (66 / 2.253) and the classifier + 2 taps (74 / 0.930, 12 taps) beats mapper + <= 4 taps (72 / 1.635, 26 taps).
  Classifier priors alone with 2 taps on AUTO (PRI + TAP2, no automatic native) reach only 176 / 5.777 pooled:
  the automatic band is what moves the prairie courses (Prairie Dunes 2 / 1.492 with taps only).
* Eagle Bend is the remaining native miss the layer cannot see (gate shut, S2 silent); the 2 taps recover most
  of it (7 -> 9, 0.515 -> 0.254) because its native sides still rank highest on the course.

**Decision: adopted behind the course gate** (`native_auto.ENABLED = True`, `COURSE_GATE = 0.25`,
`native_auto_model.json` = the fit on all 18 courses, thr 0.675). It beats "no layer" held out on matches and
regret without breaking a parkland control. Wired into the package build the same day (see "Shipping" below). With the shipped model a rebuild would
add native on Sand Creek, Prairie Dunes, Mariah Hills, Buffalo Dunes, Gateway, Coldwater, Annbriar (in-sample: held
out its gate stayed shut), Spirit Hollow (package only) and Tournament Club of Iowa (non-truth, share 0.46); National
KC, Amana (the S2 drought false positive: share 0), Tomahawk Hills, Hot Springs (no fairway reference) and 12 other
S2 courses stay unchanged.
the build step is `native_auto.build_layer(slug, pkg)` after tees / vision, and the confirm-tap priors are its
`info["p"]` (`native_auto.confirm_priors`).

**Not verified.**
* The gate was introduced after seeing Ellis; the threshold rule and features were chosen at side level on these
  18 courses (5 feature sets compared), plans were scored once. Fresh truth courses are the real test.
* Only courses with an S2 stack and `vision_any/<slug>/raw` can use it (`course_usable`; Buffalo Ridge and Falcon
  Ridge have no S2 stack and get nothing). The S2 stack is an Actions fetch (`s2_stack.yml`), not part of the build.
* Taps are simulated from the truth; the band geometry (10 yds) is the confirm tap's, not tuned for islands.
* Native outside the hand footprint is not penalised (eval_mapper caveat); approach shots and the app map are not
  scored.

### Shipping: wired into the build; held-out test on truth courses outside the training set (2026-11-03)

**Wiring.** `platform/package.py` stage S4n (`call_native_auto`, after vision + OB, before the mapper layer):
`native_auto.build_layer` adds the band when the course has an S2 stack + `vision_any/<slug>/raw` and the gate
fires; `package.native_auto` keeps thr / share / sides / p. With request `agent_layers` the stage is skipped (the
mapper layer wins: its native edits and per-side verdicts are the layer, and the confirm taps keep its priors), and
`"native_auto": false` turns it off. Confirm taps on a course with no mapper layer: `course_page.py native` ->
`verify.native_auto_for` (priors = the classifier p, <= 2 cards, the GATED + TAP2 rule above); a "no" answer erases
that side's native, the automatic band included, so a page never counts both. S2 stack: a step in
`course_page_one.yml` after the vision layer fetches it when none is committed (~30-90 s and 4-12 MB per course;
s2_stack.yml run 41619576831 did 18 courses in one 16-min job) and the finish job commits it.

**Held-out test of the frozen model** (`eval_native_auto_frozen.py`, the shipped fit on the 18, n = 4000, seed 31,
adaptive aim off). The "7 courses being traced" of the roadmap all landed on 11-02 (L.A. Nickell, Buffalo Ridge,
Rivercut, Gustin, Amana, Osage National, Annbriar) and 5 of them are already among the 18 training courses, so the
only truth courses the model has never seen are these five, none with truth native in its landing corridors:

| course | tee shots | S2 stack | gate share | AUTO | GATED | GATED + TAP2 (taps) | ORACLE |
|---|---|---|---|---|---|---|---|
| amana_colonies (drought-tan rough: the S2 false positive) | 14 | yes | 0.00 (max side p 0.64) | 12 / 0.031 | 12 / 0.031 | 12 / 0.031 (2) | 12 / 0.031 |
| tomahawk_hills | 12 | yes | 0.00 | 9 / 0.081 | 9 / 0.081 | 9 / 0.081 (2) | 9 / 0.081 |
| national_kc (no card: numbering 1 / 14) | 14 | yes | 0.00 | 1 / 0.000 | 1 / 0.000 | 1 / 0.000 (1) | 1 / 0.000 |
| hot_springs_arlington (no OSM fairway: S2 P undefined) | 14 | no P | - | 8 / 0.130 | 8 / 0.130 | - | 8 / 0.130 |
| wakonda | 14 | no | - | 11 / 0.312 | 11 / 0.312 | - | 11 / 0.312 |

The gate stays shut on all five and every plan is AUTO's: no false native, including Amana, which broke hole 14 as
an S2 pixel layer. The 5 taps it would ask (answers "none") change nothing. **This tests restraint only:** no truth
course with native has been held out from the shipped model, so the gate's yes side (and whether 25 % is right) is
still untested. The next native truth course (any prairie / links course traced blind) is the test; until then the
18-course leave-one-course-out numbers above are the evidence.

**Rebuild.** Only one library course would change: annbriar (no mapper layer; in-sample: held out its gate
stayed shut). Tournament Club of Iowa does not change because its request has `agent_layers` and the mapper layer
wins. Amana and Tomahawk Hills are unchanged (gate shut). The ~80 library courses with no S2 stack and no committed
raw cannot be judged offline (the features need the build's raw rasters); the S2 step decides on their next build.
