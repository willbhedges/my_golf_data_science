# DECADE benchmark: Fawcett's corridor rule vs the Spirit Hollow model

Re-run with `python3 spirit_hollow/benchmark/corridor.py` (about 90 s; `--no-model` gives the corridors alone in under 1 s).
The raw numbers, including the width profile across each landing window and the model's lie shares, are in `results.json`. `table.md` is the table below as the script writes it.

## Method

**Corridor.** For each hole and wood, the landing window runs from total − 20 to total + 10 yds (Driver 280–310, 2-wood 260–290, 4-wood 250–280), sampled every 2 yds.
- At each step the script scans the lateral line from −60 to +60 yds every 0.5 yd, using the model's own `lie_at` (later zones override earlier ones, and unzoned ground counts as rough).
- It keeps the widest contiguous dead-free run that contains the tee line, or the nearest run if none does.
- "Dead" means water, OB and recovery (trees). A second pass also counts native long grass as dead.
- Width is the minimum over the window.
- Aim is the middle of the band that stays clear at every step of the window (the largest left edge to the smallest right edge).

The scan is clipped at ±60. A width near 120, or an edge at −60/+60, means that side is open. In those cases the true DECADE aim lies even further toward the open side than the number shown.

**DECADE pick.**
1. Driver if its corridor is at least 65 yds.
2. Otherwise the longer of 2-wood / 4-wood whose corridor is at least 65 yds.
3. If no club reaches 65, the club with the widest corridor (the longer club when they are within 2 yds).

Rough and bunkers are ignored, as the rule ignores them.

**Model pick.** `t.best_aim(h, club)` on the three woods with default settings (20k common-random-number shots, aims −40..+40 at 2.5 yds), taking the lowest-EV club. The Bayes column is the `pick` and `aim` from `spirit_hollow/output/decision.json` (the Bayesian engine).

Aims are in yds, + = right of the tee line. The EV gap is the model's margin over its runner-up club.

## Results

| Hole | Corridor D / 2W / 4W (yds, dead = water/OB/trees) | + native as dead | DECADE pick, aim | DECADE (native dead) | Model pick, aim (EV gap to next) | Bayes pick, aim | Agree? |
|---|---|---|---|---|---|---|---|
| 1 | 106 / 110 / 109 | 81 / 84 / 86 | D -4.0 | D +9.8 | D +5.0 (0.010) | 4W +2.5 | yes / Bayes no |
| 2 back tee | 107 / 90 / 85 | 62 / 64 / 62 | D +6.4 | 2W +0.0 | D -5.0 (0.036) | D -7.5 | yes |
| 2 forward tee | 88 / 84 / 83 | 74 / 70 / 68 | D -5.5 | D -10.2 | D -12.5 (0.077) | D -10.0 | yes |
| 4 | 118 / 116 / 116 | 37 / 37 / 37 | D -0.9 | D -2.8 | D -5.0 (0.032) | D -5.0 | yes |
| 5 | 94 / 94 / 94 | 77 / 76 / 76 | D -12.9 | D -4.0 | D -7.5 (0.017) | D -7.5 | yes |
| 6 | 113 / 107 / 104 | 63 / 63 / 63 | D +3.6 | D -2.0 | D -2.5 (0.021) | D -2.5 | yes |
| 8 | 97 / 103 / 107 | 59 / 66 / 71 | D -11.6 | 2W +10.0 | 4W +0.0 (0.080) | 4W +2.5 | **no** |
| 9 back tee | 73 / 73 / 71 | 73 / 73 / 65 | D -23.4 | D -23.4 | D -15.0 (0.010) | D -15.0 | yes |
| 9 forward tee | 77 / 78 / 81 | 56 / 78 / 81 | D -21.4 | 2W -21.1 | 2W -10.0 (0.002) | 2W -12.5 | **no** |
| 10 | 55 / 63 / 68 | 55 / 63 / 68 | 4W -0.2 | 4W -0.2 | D -7.5 (0.062) | D -7.5 | **no** |
| 11 | 0 / 0 / 71 | 0 / 0 / 71 | 4W -7.0 | 4W -7.0 | 4W -5.0 (0.196) | 4W -7.5 | yes |
| 13 | 68 / 68 / 68 | 68 / 68 / 68 | D -14.0 | D -14.0 | 4W -17.5 (0.022) | 4W -17.5 | **no** |
| 14 | 87 / 96 / 100 | 74 / 84 / 88 | D -7.8 | D -14.5 | D -10.0 (0.028) | D -10.0 | yes |
| 16 | 60 / 82 / 82 | 60 / 60 / 60 | 2W -19.1 | D -9.0 | D -7.5 (0.009) | 4W -5.0 | **no** |
| 17 | 92 / 90 / 90 | 86 / 86 / 87 | D -13.9 | D -8.8 | D -2.5 (0.073) | D -2.5 | yes |
| 18 | 96 / 86 / 82 | 50 / 48 / 48 | D -8.8 | D -6.8 | D -7.5 (0.047) | D -5.0 | yes |

**Score.** On club, DECADE and the model agree on **11 of 16** tees (1, 2B, 2F, 4, 5, 6, 9B, 11, 14, 17, 18) and disagree on 5 (8, 9F, 10, 13, 16). Against the Bayes engine:
- On 8, 9F, 10 and 13, Bayes sides with the model.
- On 16, Bayes picks the 4-wood, out of a three-way tie.
- On 1, Bayes picks the 4-wood while DECADE and the model pick driver. That is inside its noise.

When native counts as dead, DECADE matches the model's club on 12 of 16. 9F (2W) and 16 (D) flip into agreement. 2B moves to the 2W and now disagrees. 8 moves to the 2W but still disagrees with the 4-wood. 10 and 13 are unchanged.

## Disagreements

| Hole | DECADE | Model | Why the simulation differs | Model/map concern? |
|---|---|---|---|---|
| 8 | Driver (97-yd corridor; OB/water right) | **4-wood** by 0.080 (Bayes 4W, p=1.0) | **Bunker the rule ignores.** The right-side fairway bunker at ~270–290 catches 32% of drives (25% of 2-wood, 11% of 4-wood). The 4-wood stops short of it, which is worth more than 19 yds of approach on a short par 4 (89 vs 108 yds in). With native counted as dead, DECADE goes to the 2W (59-yd driver corridor). | No. A robust pick that only a bunker-aware model can see. |
| 9 forward | Driver (77 / 78 / 81, all past 65) | **2-wood** by 0.002 over 4W; driver 0.04 behind (Bayes 2W) | **Long grass and little approach value.** With native counted as dead, the driver corridor drops to 56 (long grass left at the end of the driver window), and DECADE also picks the 2W. On a ~373-yd hole, driver gains only ~8 yds of approach (100 vs 108) but brings in the creek/trees right at ~280–320 (4% trees, 2% native). | No |
| 10 | 4-wood (driver 55, 2W 63, 4W 68) | **Driver** by 0.062 (Bayes D) | **Approach-distance value on a par 5.** The pond right and the creek/woods left pinch to 55 yds at 300–310, so DECADE drops two clubs. The model accepts ~7% dead (4% trees, 3% water) for 24 yds closer (225 vs 249 in). Trees play as a recovery lie (~+0.5–0.8), not a full stroke-and-distance penalty, so a "dead" miss costs less in the model than the rule assumes. The corridor is also widest at 280 (68) and narrows only at the long end of the window. | **Watch.** Driver into a sub-65 corridor (55 yds). It is still above the 50-yd red line, and 7% dead matches a 65-yd dispersion through a ~58-yd gap, so it is consistent. The pick does lean on trees being "recovery", not "jail". |
| 13 | Driver (68 / 68 / 68: pond right; borderline, at the 65–70 threshold) | **4-wood** by 0.022 (Bayes 4W, p=1.0) | **Bunkers the rule ignores.** The two pot bunkers left at ~280–300 catch 23% of drives aimed away from the pond. The 4-wood stops short of them (96% fairway). All three corridors are the same 68 yds, so the rule can't tell the clubs apart and defaults to driver. The aims agree (DECADE −14, model −17.5). | No |
| 16 | 2-wood (driver 60 vs 82: trees right at ~300 pinch only the end of the window) | **Driver** by 0.009 (Bayes **4W**, p_best D 0.5) | **Window edge and a near-tie.** The driver corridor is 83 yds until ~300 and drops to 60 only at 304–310, where few drives finish (carry 275, mishits shorter). The model sees 3% trees + 3% native and takes the 20–30 yds closer (92 vs 111–121 in). With native counted as dead, all three clubs share a 60-yd corridor and DECADE also picks driver. All three EVs sit within 0.013 of each other. | No. This is a statistical tie; the model and Bayes engines even disagree with each other. |

Aim differences on tees where the clubs agree:
- On 9B (−23 vs −15), 17 (−14 vs −2.5) and 5 (−13 vs −7.5), DECADE aims further left than the model. These holes are open on the left (the corridor's left edge is clipped at −60), so the rule's "centre of the safe corridor" sits out in the rough or long grass. The model keeps the ball on the fairway and nearer the green, which the rule cannot value.
- On 2B (+6 vs −5), the corridor is open to the right but long grass sits right of the cart path. With native counted as dead, the DECADE aim moves to 0, matching the model.

## Flags (possible model or map issues)

- **No tee has the model hitting driver into a corridor under 50 yds** when dead means water/OB/trees. The narrowest corridor the model hits driver into is **10 (55 yds)**, then **16 (60 yds)**. Both are explained above and are not errors.
- **When native counts as dead:**
  - **4 (37 yds)** and **18 (50 / 48 / 48)**: the model hits driver into very narrow long-grass corridors (29% and 24% of drives finish in native). Every club faces the same band, so DECADE's "widest corridor, longer club on ties" also lands on driver.
  - The result depends on `NATIVE_LOST = 0.5`. If the native on 4 and 18 is really lost-ball grass (Fawcett's "dead"), the driver edge (0.03–0.05) is the number to re-check. Re-check the traced width of the native on 4 too: the native polygons sit right against the ~37-yd fairway on both sides.
- **Hole 11 driver aim +40.** All three engines agree on the 4-wood. But the model's best *driver* aim sits on the `aim_max` limit (67% trees, 19% water): it is trying to bail away from the creek that crosses at ~286–292. That is harmless because driver is never picked, but the book should not quote that aim. The corridor for driver and 2-wood is 0, since the creek crosses the whole window.
- **Hole 1:** the model (D by 0.010) and Bayes (4W, margin 0.004 ± 0.013) differ. That is noise, not a model fault; DECADE agrees with the model (106-yd corridor).

## Caveats

- Widths come from the traced polygons and inherit any tracing error. Trees are traced at the trunks, so "recovery" corridors are wider than the canopy suggests on 1, 14 and 18.
- The landing window uses nominal totals with no `extra_roll`, and ignores the model's mishit and rough-roll physics. Corridors that pinch only at total + 10 (10, 16) overstate how often the pinch is reached.
- The 65-yd threshold sits at the low end of Fawcett's 65–70. With 70 as the threshold, the DECADE picks don't change:
  - 13 has three equal 68-yd corridors, so the tie-break still gives driver.
  - 10 still goes to the 4-wood as the widest corridor.
  - 9B (73) still passes.
