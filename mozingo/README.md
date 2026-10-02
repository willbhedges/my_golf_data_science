# Mozingo Lake GC — tee-club strategy (Fawcett / DECADE method)

Clubs (carry / total on fairway / lateral dispersion):
**Driver 275 / 300 / 65**, **2-wood 265 / 280 / 60**, **4-wood 255 / 270 / 50**.

Run it: `python3 mozingo/tee_strategy.py` (needs `numpy`, `matplotlib`). Writes
`output/results_table.md` and one shot-pattern overlay per hole.
`python3 mozingo/scenarios.py` runs the what-if checks below.
`python3 mozingo/stats.py` writes `output/stats_report.md`: strokes gained off the tee,
paired club-vs-club confidence intervals, how often each pick survives 100 randomly
perturbed versions of the inputs, and a hole 13 deep dive.

## Recommendations (par 3s skipped; 8, 14–18 still to come)

| Hole | Play | Aim | Margin over next-best club |
|---|---|---|---|
| 1 (par 4) | **4-wood** (2-wood is equal) | ~2 yds right of app line | 0.006 vs 2-wood, 0.03 vs driver |
| 2 (par 4) | **4-wood** | ~5 yds left | 0.03 vs driver |
| 3 (par 5) | **Driver** | ~12 yds left (trees line the right side) | 0.11 vs 2-wood |
| 4 (par 4) | **Driver** | on the line | 0.05 vs 2-wood |
| 6 (par 5) | **Driver** | ~5 yds left | 0.13 vs 2-wood |
| 7 (par 4) | **4-wood** | ~7 yds right | 0.06 vs 2-wood, 0.08 vs driver — *only if the tree clumps at 260–310 really block you* (see below) |
| 9 (par 4) | **Driver** | ~2 yds right | 0.05 vs 2-wood |
| 10 (par 4) | **Driver** | ~5 yds left (trees right) | 0.03 vs 2-wood |
| 12 (par 5) | **Driver** | on the line | 0.12 vs 2-wood |
| 13 (par 4) | **Any** — dead heat | on the line | <0.01 between all three |

## What-if checks (`scenarios.py`)

- **Hole 1, 4-wood:** with the 255-carry 4-wood, it ties the 2-wood. Both beat
  driver because about 8% of drives finish in the trees at 270–320. Hitting
  the shorter 4-wood (240 carry / 260 total) costs about 0.01 strokes.
  The extra accuracy doesn't pay for the extra 10 yds.
- **Hole 2, driver carry:** with a 275 carry, the driver lands right on the
  bunker on the right (273–294 yds), and about 10% finish in sand. The
  4-wood stays short of it. Driver only wins again once it carries about
  290 (e.g. downwind), because then it flies the bunker.
- **Hole 4, left prairie:** traced, the prairie edge is ~40 yds left of the
  line at 300+. Driver reaches it <1% of the time. 2-wood only becomes
  correct if that edge is within ~17 yds of the line. Driver is the play
  unless the prairie is a lot closer than the satellite image shows.
- **Hole 7, tree clumps:** the model treats the trees left (260–310) and right
  (~280) as a blocked lie. About 23% of drives finish there, and the 4-wood
  stays mostly short of them. If they're thin enough that you usually have a
  shot, driver wins by 0.03 instead. Your local knowledge decides this hole.
- **Dispersion 30% wider than the app's:** same picks on every hole, and
  bigger margins for the 4-wood on holes 1 and 2.

## Method

1. **Shot pattern:** carry spot is a 2-D normal around the aim point. The
   app's dispersion width is treated as ±2σ (95% of shots), and the carry-depth
   window is ±2σ ≈ 24–28 yds. The ball then rolls out along its line: full roll
   on fairway, 30% in rough, and none once it is in a hazard.
2. **Course map:** fairway, trees, bunkers, native prairie and water polygons
   traced from the satellite screenshots in `screenshots/`. Yardage scale is
   calibrated from the app's own 270-yd dot on every hole.
3. **Scoring:** each landing spot gets expected strokes to hole out from that
   lie and distance (Broadie strokes-gained baselines). Trees = recovery
   shot. Native grass = 50% lost ball / 50% hack-out. Water = penalty stroke
   plus a drop in the rough.
4. **Aim search:** −20 to +20 yds in 2.5-yd steps; the best aim is kept for each club.

## Caveats

- Hazard edges are traced by eye from phone screenshots (accurate to roughly ±5 yds).
  Hole 4's imagery is cloud-shadowed, so its fairway edges are a best guess.
- Tour baselines make the absolute scores optimistic. The *differences*
  between clubs are what matter.
- Elevation, wind and slope-driven roll aren't modelled.
