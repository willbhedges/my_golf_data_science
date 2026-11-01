# Approach-shot layer (`course_data/strategy/approach.py`)

The tee engine (`mozingo/tee_strategy.py`, run per course by `course_data/product/decide.py` / `wind_page.py`)
picks a tee club and aim. This module adds the next shot: from any lie it gives the **club and aim point
into the green by the DECADE edge rule**, the same rule as the par-3 blue box on the wind pages
(`mozingo/yardage_book.py` `par3_plan`) and Spirit Hollow's approach boxes (`spirit_hollow/approach/plan.py`
`decade_box`). It also scores those picks with an expected-strokes model, but **only as a check** (DECADE
pick vs aiming at the green centre); expected strokes never move the aim. Offline only: no page changes.

**Why (Nov 2026).** The first version (commit d00a2d3) chose the aim that minimised expected strokes over a
grid on and around the green. On most greens that was 4–7 yds *short* of the centre (the front was open,
the trouble long) with one club less, and the golfer found it consistently left him short. His rule:
"middle is probably ideal, then just use the DECADE logic: the percent of the distance in from the edge,
with the modifiers." That is what this version does.

```python
from course_data.strategy import approach as A
hole = A.Hole.from_package("eagle_knoll", "5")          # package.json, read-only, yard frame
r = A.solve(hole, start=(x, y), lie="fairway")           # unknown pin (12-pin average)
r = A.solve(hole, start, "rough", pin=(px, py),          # a known pin, wind 12 mph from 200 deg true, 45 F
            cond=A.Conditions(12, 200, temp_f=45))
r["best"], r["decade"], r["centre"], r["ev_check"], r.get("flag"), r.get("layup")
A.solve(hole, start, "fairway", opt=True)["ev_opt"]      # the old EV-optimal aim, for comparison only
A.tee_compare("blue_hills", "3")                         # tee-only vs whole-hole tee pick (offline)
```

`best` (kind `decade` or `layup`), `go`, `layup`, `centre` and `flag` each hold: club, aim target (yard frame),
EV, plays-like yds, the aim relative to the green centre (+long / +right in the shot's frame), the wind
aim-off, and P(green / sand / water / OB). `decade` holds the box: card number, hazard per edge, cushion per
edge, what was given up, the region's lateral / depth extent and the aim (lateral, depth) from the centre.

## The aim: DECADE box

Ported line for line from `spirit_hollow/approach/plan.py` (`decade_base`, `side_hazards`, `decade_box`), with
the card and modifiers read from `mozingo/yardage_book.py` so the numbers cannot drift apart:

1. **Card number** for the distance to the green centre: yds in from an edge, `yardage_book.TARGET`
   (60 → 3, 100 → 5, 150 → 8, 200 → 10, 250 → 13, roughly 5% of the distance); 3 inside 60; distance/20
   past 250.
2. **Lie multiplier** (the pattern widens): first cut ×1.08 sideways / ×1.12 in depth, rough ×1.2 / ×1.35,
   sand ×1.4 / ×1.5 (`approach/shots.py` `LIE_MULT`).
3. **Edge modifier** for what is off each edge (left, right, short, long, seen from the ball): water/OB +3,
   trees/native +2, bunker +1, rough 0 (`yardage_book.ADD`). A category counts for an edge when 2+ of 11
   rays across the green hit it within 12 yds of that edge (20 for water/OB); the worst one wins.
4. **Wind modifier** on every edge, as on the wind pages (`windMod`): under 5 mph −1, 5–10 0, 10–20 +1,
   20–30 +2, 30+ +3. `Conditions(wind_mph=…)` sets it; calm is −1.
5. **Box** = every point of the green at least those cushions inside each edge (sideways for left/right,
   along the line of play for short/long; checked at the cushion and half of it, so a kidney's waist
   counts). **Aim at its centroid.** With no trouble anywhere that is the middle of the green, so there is
   no built-in short (or long) bias; it moves only away from a worse edge.
6. **No box** (small green / long shot): the lesser trouble gives up room 0.5 yd at a time while the worst
   side keeps its full cushion; equal trouble on both sides gives up equally and ends in the middle
   (yardage_book's "lesser of evils").
7. **Known pin** (`pin=`): the pin if it is inside the box, else the box point nearest it.

**Club.** The club is the one whose plays-like total (elevation + wind + temperature, below) is nearest the
distance to the aim point: `club_for` takes the smallest |total − plays-like| over the bag. Nothing is
shaded short; the old one-club-less pattern came only from the short aim.

**Lay-ups.** When the DECADE aim is out of reach (no club for its plays-like distance from this lie), or on a
par 5 when laying up scores better than going (the one place the EV model decides, as before):
- target a **full-wedge number**: short grass 101–141 yds from the green centre (the bag's full LW..PW
  totals), at least 20 yds closer and within the lie's reach;
- on the **widest fairway** there: most short grass around the spot (half-width, capped at 15 yds), ties
  to the shorter wedge in;
- none in that window → 60–160 yds, then any short grass 20+ yds closer, then straight at the green as far as
  the lie allows.

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

**EV check.** Every pick is scored with the swings below (common random numbers, n = 400 by default): the
DECADE aim, the green centre with the same club logic (`ev_check` = EV(centre) − EV(DECADE), + means the box
beats the middle), the flag if given, and with `opt=True` the old search over a 2-yd grid on the green plus
an 8-yd ring (`ev_opt`), so the cost of following DECADE instead of the optimiser can be reported.

**Whole-hole tee value** (`ValueGrid`, `tee_compare`).
- V(x, y, lie) is the EV of the DECADE approach (or lay-up) on a 10-yd grid over the tee-ball landing area, for fairway, rough,
  sand, with bilinear interpolation between grid points. Trees = V_rough + the Broadie recovery-minus-rough gap (x
  `TREE_SEVERITY`), because a geometric solve from the trees cannot see a blocked line to the green.
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

Run: `python3 course_data/strategy/eval_approach.py`, about 6 min on 4 cores. All 28 par 4s and par 5s on
Blue Hills (Black tees) and Eagle Knoll (Back tees, the package's set). Approach starts are 40 finishing spots
of each hole's tee-only pick, from the fairway, first cut, rough or sand. Unknown pin (12-pin average for the
EVs), calm (wind modifier −1), 70 °F. The old numbers are the d00a2d3 run of the EV-optimiser.

**Depth bias is gone.**
- Mean aim depth vs the green centre over all 1,011 DECADE go-shots: **−0.4 yds** (par 4s alone: **+0.15**),
  vs **−5.5** before (par 4s −5.7). The −0.4 is par-5 / long shots that hit the limit of reach (front of the
  box) and hazard-driven holes.
- Club: on the same spots the new pick is **one club more than the old one half the time and never less**
  (same 50%, more 50%, less 0.1%). It is the club for the middle, not for 5 yds short.
- Offsets are hazard-driven only: BH 1 −6 (OB long, bunker short), EK 7 −3.3 (trees long), EK 13 +2.6 and
  EK 9 +1.8 (bunkers short), EK 17 +3.6 right (water left and short).

**EV check (DECADE vs aiming at the centre, same club logic).** Mean **+0.002** strokes per approach (DECADE
slightly better); per spot −0.055 to +0.08; DECADE ≥ centre on 46% of spots. Biggest wins where the box
moves away from OB/water/trees (BH 1 +0.08, EK 7 +0.036, EK 1 +0.023); biggest cost EK 13 (−0.029: the box
sits 2.6 long of a bunkered front where the EV model likes a run-up). Against the old EV-optimal aim the DECADE
pick gives up 0.033 strokes per approach on average in this model, the price of not aiming short; the model
has no green slope or firmness and is the thing the golfer's experience contradicts.

**Picks, median fairway finish of each hole's tee pick** (club, plays-like, aim vs centre long/right yds;
edges L/R/S/Lg as DECADE sees them):

| hole | old (EV-optimal) | new (DECADE) | edges L / R / S / Lg, card |
|---|---|---|---|
| EK 1 (P4) | GW 127, −4.4 / −1.5 | PW 136, −1.3 / −1.7 | rough / trees / rough / bunker, 7 |
| EK 3 (P4) | LW 100, −2.9 / +1.2 | LW 103, +0.3 / −0.1 | open, 5 |
| EK 4 (P4) | SW 114, −4.0 / −1.0 | GW 117, −0.7 / +0.1 | trees long, 6 |
| EK 5 (P4) | 9-iron 155, −4.8 / +1.0 | 8-iron 164, +0.4 / −0.5 | bunker right, 9 |
| EK 7 (P5, 2nd) | 8-iron 168, −6.5 / −3.0 | 7-iron 171, −3.3 / −0.2 | trees L / R / long, 9 |
| EK 8 (P4) | SW 111, −1.6 / +0.5 | SW 114, +1.3 / −0.2 | bunkers L / R / short, 6 |
| EK 9 (P5, 2nd) | 5-iron 199, −16.4 / −3.0 | 4-iron 218, +1.8 / +1.6 | bunkers left / short, 11 |
| EK 10 (P4) | PW 133, −2.8 / −0.2 | PW 137, +0.4 / +0.7 | bunker left, 7 |
| EK 11 (P4) | 8-iron 169, −3.5 / −0.3 | 7-iron 173, −0.5 / +0.5 | bunkers left / short, 9 |
| EK 13 (P5, 2nd) | 4-wood 232, −9.4 / +2.3 | 4-wood 244, +2.6 / −2.4 | bunkers right / short, 13 |
| EK 14 (P4) | LW 70, −1.0 / −0.2 | LW 72, +0.4 / −0.4 | trees / water / water / trees, 4 |
| EK 15 (P4) | 8-iron 159, −5.8 / +0.7 | 8-iron 169, −0.6 / +1.2 | trees left, 9 |
| EK 17 (P5, 2nd) | lay-up LW 102 | 4-wood 234, +0.8 / +3.6 | water L / short, trees R, 12 |
| EK 18 (P4) | PW 138, −3.4 / 0.0 | PW 142, +1.3 / −0.5 | open, 7 |
| BH 1 (P5, 2nd) | 4-iron 220 lay-up, −13.7 / −4.1 | 4-wood 228, −6.0 / −3.2 | bunker short, OB long, 12 |
| BH 4 (P4) | 9-iron 156, −4.9 / +0.3 | 8-iron 161, −0.8 / +0.1 | open, 8 |
| BH 17 (P4) | 8-iron 163, −6.7 / +0.3 | 8-iron 170, −0.8 / −0.8 | trees / water / bunker / trees, 9 |
| BH 18 (P5, 2nd) | 2-wood 264 to 79 short of centre | lay-up 4-iron 211 to a full wedge | out of reach |

**Lay-ups.** 109 of 1,120 starts lay up (BH 18 always: out of reach; BH 6 / BH 13 / EK 13 / EK 17 / BH 1 from
the longer or rough finishes), each to 101–141 yds on the widest short grass. EK 17's median finish now goes
(4-wood at a box 3.6 right of centre, away from the water) where the old search laid up; from 7 of its 40
spots it lays up.

**Whole-hole tee choice** (tee clubs × aims scored by 1 + V, V now the DECADE approach value): the tee club
changes on 2 of 28 holes (BH 10 and EK 11, 4-wood → Driver) and the club or aim on 6; mean regret of keeping
the tee-only pick 0.001, max 0.010 (EK 11). The tee-shot table is still a good proxy; the pages are not
changed.

Tests: `python3 -m pytest course_data/strategy/test_approach.py` (19 pass, ~3 s). They cover:
- table monotonicity, and bag gapping / consistency with the tee clubs;
- the card numbers and wind modifier match `yardage_book.TARGET` and `windMod`; edge cushions for water,
  rough lie and wind;
- an open green aims at the centre (within 0.5 yd) with the club whose total is nearest the plays-like yds;
  water right moves the aim left; OB long moves it 1–3 yds short; a small green splits to the middle; water
  on one side of a small green keeps its full cushion;
- a tucked pin over a bunker aims inside the flag; a pin inside the box is aimed at; short-side cost;
- uphill plays longer; head wind, cold, and the cross-wind aim-off sign;
- out of reach lays up to a full-wedge number in the middle of the fairway; at the limit of reach the aim
  moves to the nearest reachable box point; rough worse than fairway;
- the proximity calibration; ValueGrid penalty mapping; a Blue Hills package hole solves.
