# Mozingo Lake GC — tee-club strategy (Fawcett / DECADE method)

Clubs (from the GPS app): **Driver 300 yds / 65 yd dispersion**, **2-wood 270 / 60**, **4-wood 240 / 50**.

Run it: `python3 mozingo/tee_strategy.py` (needs `numpy`, `matplotlib`). Writes
`output/results_table.md` and one shot-pattern overlay per hole.

## Recommendations (holes 1–6, par 3 #5 skipped)

| Hole | Par | Play | Aim | Strokes saved vs next-best club |
|---|---|---|---|---|
| 1 | 4 | **2-wood** | ~2 yds right of app line | 0.03 vs driver, 0.06 vs 4-wood |
| 2 | 4 | **Driver** | ~7 yds left (away from bunker / trees / prairie on the right) | 0.09 vs 2-wood |
| 3 | 5 | **Driver** | ~10 yds left (trees line the right side) | 0.19 vs 2-wood |
| 4 | 4 | **Driver** | on the line | 0.07 vs 2-wood |
| 6 | 5 | **Driver** | on the line (lake is ~100 yds left, out of play) | 0.19 vs 2-wood |

Hole 1 is the only lay-up. At 300 the driver pattern reaches the tree clump
on the left (270–320 yds) and the trees right of the cart path (~10–12% of
drives end up blocked). The 2-wood stays short of most of that and still
leaves only about 100 yds. It's close (0.03 strokes), so take driver if
the wind is helping and the pin is easy. Everywhere else the extra 30 yds is
worth more than the extra misses. That's Fawcett's usual result: lay up only
when a penalty or a blocked-out lie sits inside the driver pattern but
outside the shorter club's pattern.

The picks hold if your real dispersion is 30% wider than the app's numbers.
Hole 1 then favours the 2-wood by more (0.07).

## Method

1. **Shot pattern:** 2-D normal around the aim point. The app's dispersion
   width is treated as ±2σ (95% of shots), and the depth window is ±2σ ≈ 24–28 yds.
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
- Elevation, wind and rollout aren't modelled. The club distances are total yards.
