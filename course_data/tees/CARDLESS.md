# Cardless scorecard (tees/cardless.py)

Goal: no web card and no paid API. From routed holes (tee complex + green per hole) and the tee boxes on the ground,
infer the **tee sets, the per-hole yardage of each set and the par**, so the tee-shot planner can run on any course.

```bash
python3 course_data/tees/eval_cardless.py --fit   # fit cardless_model.json on the zero_tap DEV split, score dev + test
python3 -m pytest -q course_data/tees/test_cardless.py
```
```python
import cardless as CL
card = CL.infer_card(holes, osm_tees, pads=lidar_pads)   # scorecard/1 shape: par, tee_sets {"Back", "2nd", ...}
```

## Method

1. **Tee complex per hole.** Each OSM `golf=tee` box goes to the hole whose first leg it sits beside
   (`place_tee.assign_tees_to_holes`). Lidar pads are used only on holes with no OSM box. Every box is measured
   the USGA way along the hole line through the dog-leg points to the green centre (`place_tee.LineOfPlay`):
   front, back and centroid yardage, and its length. Boxes whose centroid yardages are within 5 yds of each other
   are one position (side-by-side split boxes). The start of the routed line is also a tee position when it lies
   behind every box.
2. **Number of sets S.** Each box gives one marker slot, or two when it is 30 yds or longer (one near the back,
   one near the front). Take the 75th percentile of slots per hole and map it to S with a lookup table learned
   on dev (`s_table`). In practice S comes out 3 to 5. Sparse mapping falls back to the prior, which is 4.
3. **Joint assignment.** Each set s has a course-wide ratio r_s to the back set. It starts from the median ratio
   of card totals for that S on dev (e.g. S=4: 1, .94, .87, .78). Per hole, an exact DP (beam 60) places the sets
   back to front onto the box intervals. A set stands at r_s × B, clamped into its box, never longer than the set
   before it. Sets may share a box (at least 4 yds apart inside it) or the same marker. They may also stand off
   any box at r_s × B for a cost of 25, which covers forward tees on the fairway that OSM does not map. B is the
   back yardage: 0.9 of the way back in the farthest box, because cards measure from near the back of the back
   box (on dev, the farthest box's back edge is a median 1.9 yds from the card's back yardage and its centroid is
   8.7 yds short). Then r_s ← 0.5 × median(y_s / y_back) + 0.5 × prior, repeated 4 times.
4. **Par.** A softmax over (back yds, back², 2nd-set yds, green radius, dog-leg angle, line length), fitted on dev
   with the predicted yardages as inputs. A course DP then maximises Σ log p(par_h) + log prior(course par, number
   of par 3s, number of par 5s), with the prior taken from the dev cards' counts (18 holes mostly 70 to 72, about
   4 par 3s and 4 par 5s; 9 holes 34 to 36).
5. Sets are named `Back`, `2nd`, `3rd`, ... and each carries its total and its ratio.

## v2 (2026-11-01): box reassignment, hybrid anchoring, learned 2nd set

Three changes, all fitted on dev only (test run once with the final settings):

1. **Box -> hole assignment** (`reassign_far_boxes`). `place_tee.assign_tees_to_holes` scores a box by
   |offset| + 0.1 x behind, so a box far behind a hole's start could still be claimed by it. Now a box more than
   30 yds behind its hole's line start that lies **nearer another hole's line start** goes to that hole (if it
   fits there: |offset| <= 45, at most 150 behind) or is dropped. On dev such boxes matched the card back on 4
   holes and the line start on 20. A "another hole's line passes within 30 yds" rule (`corridor_yd`) was tried
   and left off (no gain on dev).
2. **Hybrid** (`infer_card(..., anchored=)`). On a hole whose line is an OSM golf=hole way, OSM boxes whose back
   edge is more than 45 yds behind the way's start, and lidar pads more than 10 yds behind it, are not tee
   positions; the rest of cardless (other boxes, sets, par) runs as before. Holes the router placed (no hole way)
   use cardless fully. On dev, lidar pads behind the line start matched the card back on 2 of 18 holes. The
   45-yd limit costs a little on the bench, where boxes 30-60 yds behind the way's start are often the real tips
   (anchoring at the line start alone: back within-10 56.5 % on dev; 15 yds: 62.1 %; 45 yds: 67.8 %; none:
   68.3 %), and it removes the overshoots seen in the card-blind eval (`platform/CARDBLIND.md`).
3. **2nd set** (`second_mode="gap"`). Back minus a learned gap by par and 50-yd back-length bin (dev-card
   medians, `cardless_model.json` `gap2`: par 4 from 12 yds at 250-299 to 30 at 450-499; par 5 17 -> 31), snapped
   to the nearest box position within 4-45 yds in front of Back when one is within 15 yds of that target. On
   dev this beat the joint DP's 2nd set (46.0 %) and a 0.94 x back ratio (41.4 %): 49.6 %. A ratio by par
   (0.905 / 0.947 / 0.955) was worse than the gap (43.6 % vs 44.4 % before snapping).

Per-hole |predicted - card| within 10 yds (median yds), zero_tap bench, all lines are OSM hole ways:

| | dev back | dev 2nd | dev par | **test back** | **test 2nd** | **test par** |
|---|---|---|---|---|---|---|
| fallback (back = line, 2nd = 0.94 x line, par from length) | 54.9 % (8.6) | 34.5 % (15.3) | 93.5 % | 57.2 % (7.9) | 35.7 % (14.4) | 94.5 % |
| cardless v1 | 67.1 % (6) | 44.7 % (12) | 94.6 % | 70.1 % (5) | 47.0 % (11) | 96.4 % |
| cardless v2, no anchoring (router lines) | 68.1 % (6) | 49.9 % (11) | 95.2 % | 70.6 % (5) | 51.9 % (10) | 96.5 % |
| **hybrid** (v2 anchored on hole ways) | 67.8 % (6) | **50.6 % (10)** | 95.3 % | 69.6 % (5) | **52.0 % (10)** | 96.4 % |

(v1 rows are scored with the refitted par model; v1's own par model gave 94.8 / 96.8 %.) On the bench the
hybrid's anchoring costs 0.3-1.0 points of back-set accuracy against unanchored v2; the 2nd set gains 5-6 points
over v1. `python3 course_data/tees/eval_cardless.py [--fit] [--test]` prints all four rows.

## Evaluation (zero_tap benchmark, courses with a fitting web card)

The truth is the web card, cleaned. Sets with missing holes are dropped. So are duplicates and combo sets (every
hole equal to some other set, e.g. opengolfapi's "Web" set). Sets under 55 % of the back total are dropped too
(junior / family tees). One card listed its nines the other way round from the OSM refs and was re-aligned. The
method sees the truth hole lines as the routing, the OSM green centre and radius, all OSM tee boxes, and lidar
pads. It never sees the card, the hole ways' par or dist tags, or the tee colour tags. 18- and 9-hole courses
only. Dev: 124 courses / 2,106 holes. Test: 118 / 2,016 holes. Everything was fitted and tuned on dev, and test
was run once with the final settings.

Per-hole yardage error |predicted − card|, yds (median / p90 / share within 10 yds):

| | dev | **test** |
|---|---|---|
| **Back set** (cardless) | 6 / 40 / 67 % | **5 / 34 / 70 %** |
| Back, baseline: routed line length | 8.6 / 45 / 55 % | 7.9 / 40 / 57 % |
| **2nd set** (cardless) | 12 / 47 / 45 % | **11 / 39 / 47 %** |
| 2nd, baseline: line length | 14.8 / 47 / 37 % | 15.5 / 42 / 36 % |
| All sets, matched by total (DP) | 11 / 51 / 48 % | 10 / 44 / 52 % |
| Same with the true S given (oracle) | 12 / 54 / 47 % | 10 / 46 / 51 % |
| OSM `dist` tags on hole ways | 0 % of holes | 2.7 % of holes: median 0, p90 422 (some tags are metres or wrong) |

| | dev | **test** |
|---|---|---|
| Par per hole | 94.8 % | **96.8 %** |
| Par per hole, baseline (line ≤ 250 → 3, ≥ 470 → 5) | 93.5 % | 94.5 % |
| All pars right, per course (18-hole only) | 61 % (60 %) | **64 % (66 %)** |
| S exactly right / within 1 | 44 % / 82 % | **47 % / 83 %** |

Course totals are much less accurate than single holes. The back-set total is off by a median of 86 yds on dev
and 81 on test (p90 350 / 270). The 2nd set is off by about 120. Per-hole errors are not symmetric. On dev the
back set's signed error has a median of −2 but a 10th percentile of −29: some card back tees are not mapped at
all, and those are always too short.

## Failure modes (dev)

- **Unmapped back tees.** About 30 % of card back yardages fall in no mapped box (±5 yds). Without lidar or
  imagery pads the back set falls back to the farthest mapped box or the line start, and comes out short. These
  holes make up the p90.
- **Sparse OSM.** A course with only one box per hole (e.g. pezhekee_national_mn, back total 6,328 vs 7,263)
  collapses onto the forward box. The prior ratios then give plausible but uninformed forward sets.
- **S.** With 2 to 3 mapped boxes per hole, which is the median, the box count cannot tell a 4-set course from a
  5-set one. The table predicts 3 or 4 and misses 5 and 6. The 2nd set lands in the **same box as the back set**
  on a majority of holes. That is why the DP puts sets inside box intervals rather than on one point per box
  (point mode gave 2nd-set within-10 of 40 % vs 45 %).
- **Card / OSM mismatch (truth noise).** Some cards do not describe the mapped course (windham_nh, whistling_straits_wi:
  per-hole medians over 60 yds while the totals agree, i.e. another routing or another course of the facility).
  Some list a single set (19 courses with S = 1 after cleaning). These rows are kept in the numbers.
- **Par.** Most misses are 470 to 520-yd par-4/5 and 230 to 260-yd par-3/4 holes. All 18 must be right, so even
  97 % per hole gives about 65 % of courses fully right.

## Not done / next

- The 36 reviewed library courses (`course_data/library/<slug>`) were not scored here. Their `package.json`
  `tee_options` plus card can be fed to `infer_card` the same way.
- Texture pads (`localize.texture_pads`) and NAIP segment tees are not used yet. The back-tee shortfall is the
  biggest error, so they are the obvious next source.
- The routing used here is the OSM hole line. In a full zero-tap run the router's tee and green replace it. The
  line-start slot then means the router's chosen tee.

Files: `cardless.py`, `cardless_model.json` (fitted on dev), `eval_cardless.py`, `eval_cardless.json` (per-course
rows included), `test_cardless.py`, `fixtures_cardless_backbox.json` (the five card-blind back-box holes).

## Unmapped tips: candidate search (tip_candidates.py, eval_tips.py)

Tried feeding back-tee candidates that OSM does not map into `infer_card` (`extra_boxes=`, per hole, source
`tip:<src>`). Sources with local data: lidar flat pads (`pads.json`), NAIP segment-model tees (`segment.geojson`)
and blind perception scene tee boxes (`scene.json.gz`). Only **50 of the 262 bench courses** have these files
(dev 33 with OSM boxes / test 16), so everything below is on that imagery subset; texture pads need the DEM + NAIP
rasters, which are not local. The hole-line start is already a cardless slot.

Every candidate whose back edge reaches 4 to 80 yds behind the farthest OSM box (it may overlap the box: a lidar pad
often covers the whole levelled complex) is scored by a logistic model fitted on dev (label: the card back yardage
is inside it +-5 and beyond the back box +5). Features: reach behind, offset, source, detector p, area, sources
agreeing, distance to the nearest green, line start on it, OSM boxes on the hole, length. Per hole the best one is
added when p >= thr; thr was chosen on dev by the cardless back-set within-10 share.

| imagery subset | back within-10 / p90 | back total err med / p90 | S exact | tips accepted (precision) |
|---|---|---|---|---|
| dev before | 71.7 % / 34 | 102 / 341 | 45.5 % | - |
| dev after (thr 0.4, chosen) | 71.7 % / 34 | 102 / 341 | 45.5 % | 0 |
| dev, thr 0.2 | 69.4 % / 41 | 141 / 390 | 42.4 % | 39 (31 %; 17 too long by > 10 yds) |
| **test before** | 70.1 % / 32 | 56 / 203 | 56.2 % | - |
| **test after** (thr 0.4) | 70.1 % / 31 | 56 / 203 | 56.2 % | 1 (0 %) |
| test, thr 0.2 (diagnostic only) | 69.4 % / 35 | 113 / 259 | 50.0 % | 20 (40 %; 7 too long) |

Full dev / test (124 / 118 courses) are unchanged: 67.1 % / 70.1 % within 10.

Why it does not pay:
- About 17 % of holes (dev subset 98 / 556) have the card back > 5 yds beyond every OSM box; half of those gaps are
  5 to 17 yds (measuring convention, not a missing box). 59 of the 98 have no candidate at all behind the box.
- Candidates are informative but not enough: on unmapped holes a candidate covers the card yardage 70 % (scene
  boxes 38 %), vs 45 % (19 %) for a fake tip yardage drawn from the same gap distribution on mapped holes. But most
  holes with a candidate behind the back box are *correctly* mapped (245 of 280 on dev), so the posterior that a
  candidate is the real tips stays around 15 to 35 %; leave-one-course-out AUC 0.70, top-20 precision 10 %.
  Break-even is about 50 %, because a fake tip moves an otherwise-right back yardage 10 to 40 yds long.
- Nothing in the OSM geometry alone predicts which holes have unmapped tips (box count, back-box length and
  separation, line start, course length: 5-fold CV AUC 0.53 on 1,995 dev holes), and the course-level share of
  holes with strong candidates does not correlate with the course's unmapped share (r = -0.11 dev, 0.06 test).

Next: a per-hole elevation / mown-texture check on the candidate (needs the rasters), or the tee-sign / plaque
positions from street-level imagery; a better source than these three is needed before tips can be added safely.
