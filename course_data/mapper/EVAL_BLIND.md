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
