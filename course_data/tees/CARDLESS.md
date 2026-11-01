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
rows included), `test_cardless.py`.
