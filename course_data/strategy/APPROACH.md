# Approach-shot layer (`course_data/strategy/approach.py`)

The tee engine (`mozingo/tee_strategy.py`, run per course by `course_data/product/decide.py` / `wind_page.py`)
picks a tee club and aim. Its objective scores where the tee ball finishes with a Broadie table:
`1 + expected_strokes(lie, yds to the green centre)`. That table doesn't know where the green is, what is
around it, or where the pin is. This module adds the next shot. From any lie position it picks the club and
the **aim point on (or near) the green** that minimise the expected strokes to hole out. It can also value
every tee-ball finishing spot that way, so a tee pick can be scored on the whole hole. That second use is
offline only: no page output changes.

```python
from course_data.strategy import approach as A
hole = A.Hole.from_package("eagle_knoll", "5")          # package.json, read-only, yard frame
r = A.solve(hole, start=(x, y), lie="fairway")           # unknown pin (12-pin average)
r = A.solve(hole, start, "rough", pin=(px, py),          # a known pin, wind 12 mph from 200 deg true, 45 F
            cond=A.Conditions(12, 200, temp_f=45))
r["best"], r["centre"], r.get("flag"), r["top"]
A.tee_compare("blue_hills", "3")                         # tee-only vs whole-hole tee pick (offline)
```

`best`, `centre` and `flag` each hold the following: club, aim target (yard frame), EV, plays-like yds, the
aim relative to the green centre (+long / +right in the shot's frame), the wind aim-off, and P(green / sand /
water / OB).

## Model

**Frame and map.** The package's yard frame: x is yds right of the tee line, y is −yds along it, and the tee
is at (0, 0). The lies are rasterised on a 1-yd grid from the package's `zones`, in package order with later
zones winning (the same rule as `tee_strategy.lie_at`), plus `green_polygon_yd` on top. Unzoned ground is
rough. Tee-ball finishes from `tee_strategy.simulate` (pixel frame) map in exactly: `(px − tee_px) / ppy`.

**Bag.** The calm 70 °F carry and total are those of the tee model. The tee model's "Long iron" is the 4-iron
(210/220) and its "Mid iron" is the 6-iron (185/192); the 2-wood (265/280) and 4-wood (255/270) are the
golfer's numbers. The other irons use the usual 12-yd gaps:

| club | 2W | 4W | 4i | 5i | 6i | 7i | 8i | 9i | PW | GW | SW | LW |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| carry / total | 265/280 | 255/270 | 210/220 | 198/206 | 185/192 | 174/180 | 162/167 | 150/154 | 138/141 | 126/128 | 113/114 | 100/101 |

- Off the deck the woods lose 15 / 10 yds (no tee), as in `spirit_hollow/approach/shots.py`.
- A club covers [total − 12, total + 3], meaning a smooth or choked-down swing.
- The bag has a gap between 222 and ~245. The 4-wood swung smooth fills it, the same choice
  `approach/shots.py` makes. v2's ~235 hybrid is hypothetical and is not in the bag.
- Under 100 yds the shot is a partial lob wedge.
- The driver is never an approach club.
- Reach by lie: fairway 275, rough 235, sand 190, trees 140.

**Plays-like distance.** The aim point's horizontal distance, plus elevation: a green dh ft above the ball
plays dh·0.3048/tan 50°/0.9144 ≈ 0.28 yd per ft longer. This is the par-3 rule in
`course_data/elevation/adjust.py`, using heights from the package's DEM tee-line profile and green height.

- **Club choice.** The club is the one whose wind- and temperature-adjusted total is nearest that distance.
  It uses `spirit_hollow/wind.py`'s `temperature_adjust` and `adjust`, the same physics as the tee shots and
  the par-3 plays-like box, with that file's club sensitivities: 4-iron/5-iron = "Long iron", shorter clubs =
  "Mid iron".
- **Aim and drift.** The golfer is assumed to club and aim so that the mean ball finishes on the aim point.
  The cross-wind drift is aimed off and reported (`aim_off_drift`, + = start it right).
- **Wind and dispersion.** Wind widens or lengthens the pattern by wind.py's width and depth factors.

**Dispersion.** This is the repo's approach pattern from `spirit_hollow/approach/shots.py`, fitted to
5-handicap proximity (Broadie / Stagner / Arccos anchors).

- Lateral sigma: 7.0 yd at 100, 9.4 at 150, 13.4 at 200.
- Depth sigma: 1.5× lateral.
- Lie multipliers (lateral × depth): first cut 1.08/1.12, rough 1.2/1.35, sand 1.4/1.5, trees 1.6/1.8.
- Over 200 yds, 15% of shots are mishits that finish 75–92% of the distance.
- Test `test_proximity_matches_calibration` checks the mean proximity from 150 yds: 35–55 ft, about 45 ft.
- The tee model's narrower Long iron / Mid iron widths are teed-ball numbers. They stay in force off the tee;
  this module never changes a tee number.

**After-shot value** (`value_map`, averaged over the pins). These are PGA Tour tables (Broadie), the same
family the tee engine uses. `hcp=True` adds the ~5-handicap offsets from `research.md`.

- **On the green:** putts by feet to the pin.
- **Off the green, within 40 yds of the pin:** the short-game table by lie (fairway / first cut / rough /
  sand) at the distance to the pin, plus a **short-side** cost. The extra strokes are fairway 0.08, first cut
  0.12, rough 0.18 and sand 0.15. That full cost applies when no green lies between the ball and the pin; it
  fades to 0 at 10 yds of green to work with. Tour up-and-down rates are ~60% normally and ~40–45%
  short-sided from greenside rough; a 15–20 point drop is roughly 0.15–0.2 strokes.
- **Further out:** `tee_strategy.expected_strokes(lie, yds to the green centre)`.
- **Trees:** the recovery row. The `TREE_SEVERITY` mix is as in the tee model.
- **Water:** 1 + rough from near where the ball went in.
- **OB:** stroke and distance, 1 + the expected strokes from the spot the shot was played.
- **Pin:** unknown pins use 12 positions spread over the green, at least 4 yds from the edge
  (farthest-point sampling, fixed seed). You can also pass `pin=`.

**Search.**
- The candidate aims are a 2-yd grid over the green plus an 8-yd ring around it, for bail-out aims short or
  to the fat side. Water, OB, trees and native are excluded as aims.
- When the green is out of reach or nearly so, and on every par 5, lay-up spots are added: fairway cells on a
  6-yd grid within reach and at least 20 yds closer.
- Every aim and club uses the same swings: common random numbers, default n = 400.

**Whole-hole tee value** (`ValueGrid`, `tee_compare`).
- V(x, y, lie) is the optimal approach EV on a 10-yd grid over the tee-ball landing area, for fairway, rough,
  sand and trees, with bilinear interpolation between grid points.
- Penalty lies map exactly as in the tee model: water = 1 + V_rough, OB = 2 + V_rough, first cut = the
  `FIRST_CUT_COST` mix.
- `tee_compare` runs the tee engine's own `simulate` (same clubs, Driver to Mid iron, aims −30..+30 every
  5 yds, same swings). It scores each swing both ways and reports the two argmins and the *regret*: what the
  tee-only pick costs under the whole-hole objective.

## Assumptions and limits

- **Model mix.** Tour tables with a 5-handicap pattern. The absolute EVs therefore sit about 0.2–0.3 above
  the Broadie baseline on small public-course greens. Only the *differences* between aims and clubs drive the
  picks.
- **Green surface.** No green slope, firmness or green-specific roll-out: the ball finishes where the pattern
  says. Elevation comes only from the tee-line DEM profile (the ball's height is taken at its distance along
  that line).
- **Hazard maps.** Hazards are only as good as the package. OSM bunkers and water, and vision-mapped trees,
  are auto-built and not hand-checked.
- **Lay-ups.** A lay-up's value is the static table at its lie and distance, not a recursive solve.
- **Recovery.** Trees reduce reach and widen the pattern. There is no explicit punch-out-sideways option.

## Evaluation (Blue Hills, Eagle Knoll; `eval_approach.py` → `output/approach_eval.json`)

RESULTS_PLACEHOLDER
