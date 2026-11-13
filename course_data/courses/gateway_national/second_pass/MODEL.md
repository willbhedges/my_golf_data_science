# Gateway National: review of the decision model (statistics), Nov 13 2026

For Will, NCCGA Regional 3, Back tees. Scope set by Will on Nov 13: his carries as stated, one standard
DECADE-style pattern per club, the standard expected-strokes numbers kept as they are, and one club and one aim per
hole. This review asks whether that one answer is computed correctly.

**Checkpoint 3** (04:20 UTC Nov 13). The sensitivity runs are on a frozen copy of the engine and map at commit
`222f7ece4`, because the shared checkout changed under the first runs. Since then the map edges on 2, 3 and 5 moved
(`ca4480af1`): the clubs there are the same, with aims 2 +9 (was +14.5), 3 -5.5 (was -9) and 5 +3.5 (was 0).
The findings below are about the model and carry over; the aims quoted are the frozen state's. Code:
`second_pass/model/` (imports the engine, edits nothing); `run_all.sh <snapshot> <out>` repeats the tables.

## Findings, ranked by effect on a club or an aim

| # | finding | changes a pick? | which hole, how much |
|---|---|---|---|
| 1 | Which table "the standard numbers" means has to be settled (see below) | **yes, if it means the plain Tour table** | current map: 11: Driver +17.5 -> 4-wood +8 (by 0.004, a tie); 9: 4-wood +2, 2-wood +8 and Driver +12.5 within 0.0014. Every other club stays. With the engine's present table: no change |
| 2 | Hole 10 aim is Monte Carlo noise in the single-seed solve | **aim only** | 10: 2-wood aim -18, not -20.5; worth 0.007 |
| 3 | Second-shot rollout on the close holes | no | 9: margin 0.025 -> 0.025-0.030; 10: 0.060 -> 0.065-0.086; 16: 0.108 -> 0.088-0.107, aim 0.5-1 yd left |
| 4 | Lost ball in the fescue (25 % at the edge to 65 % ten yards in) | no | at 5-25 % or 40-90 %: aims within 1 yd, margins within 0.010 |
| 5 | Stroke-and-distance value on 3 (OB) and 10 | no | 3: Driver margin 0.051 -> 0.044, aim unchanged; 10: 0.060 -> 0.061 |
| 6 | Water drop geometry | no | applied correctly |
| 7 | Monte Carlo soundness, winner's curse | no | same club on 6 of 6 independent swing sets on all 13 holes; bias under 0.002 |
| 8 | Aim search (grid, bound, window, sideways shift) | no | within 1.25 yds of a 40,000-swing fine search on 12 of 13 holes (the 13th is finding 2) |
| 9 | Dispersion: size, shape, tilt, tails | no | fat tails: no club, aims within 2.5 yds; firm ground makes 10 a tie between 2-wood and 4-wood |
| 10 | Par-3 putting and short-game values | no | reviewed, not re-run |

Frozen-state picks the table refers to: 1 Driver -8.5; 2 Driver +14.5; 3 Driver -9; 5 Driver 0; 6 Driver +6;
8 Driver -44.5; 9 Driver +13; 10 2-wood; 11 Driver +17.5; 13 Driver +1; 15 Driver +14.5; 16 4-wood +6.5; 18 Driver
+14.5.

## 1. Which table is "the standard numbers"? Decision needed from the manager

Will's decision is to keep the standard near-PGA (Broadie) expected-strokes numbers. The engine's central world
does not use the plain Broadie table today. It uses `table="am"`: Broadie's Tour values + 0.36 + 0.0012 per yard
beyond 150, with the fairway-to-rough gap multiplied by 0.75 (`spirit_hollow/v2/model.py`, `central()`). The plain
Tour table is in the engine as `table="tour"`.

On the current map (`087baac94`, same map as `ca4480af1`; 32,000 common swings, SE 0.001-0.003) the two give the
same club on eleven holes and differ on two:

| hole | engine as it is (`am`) | plain Tour table (`tour`) |
|---|---|---|
| 9 | Driver +13.5 by 0.027 over 2-wood | 4-wood +2 (3.9940), 2-wood +8 (3.9947), Driver +12.5 (3.9954): a three-way tie |
| 11 | Driver +17.5 by 0.033 over 4-wood | **4-wood +8 by 0.004 over Driver +17.5: a tie** |
| 3 | Driver -5 by 0.059 | Driver -5 by 0.033 |
| 8 | Driver -45.5 by 0.057 | Driver -41.5 by 0.029 |
| 10 | 2-wood -18.5 by 0.060 | 2-wood -19 by 0.046 |
| 16 | 4-wood +6.5 by 0.110 | 4-wood +6.5 by 0.054 |
| 1, 2, 5, 6, 13, 15, 18 | Driver | Driver, aims within 0.5 yd, margins 0.02-0.03 smaller |

(On the frozen state `222f7ece4`, before the edge fix on 3, the Tour table had 3 at Driver by only 0.007.)

What separates them is one term: the 0.0012 per yard, which makes each extra yard off the tee worth about 30 %
more than on Tour. The 0.36 level does nothing (set to 0.20: every club and aim identical). The rough multiplier
does little (x0.4 to x1.3: no club changes; 9's margin 0.036 to 0.011).

* If "as they are" means the engine as it is: nothing changes, and 9 and 11 should be shown as close calls
  (0.025 and 0.031).
* If it means the plain Tour table: set `table="tour"` in the central world and re-solve. 11 becomes a tie that
  leans 4-wood, 9 a three-way tie, and every other club stays.
* Either way 9 and 11 are within 0.03, so either club is defensible on both. I am not proposing a rescaling;
  this is only which of the two existing tables the page should be solved on.
* A third reading agrees that 11 is a coin flip: with the second-shot rollout's own values in place of the table
  (section 3, "raw"), 11 is Driver by 0.003 or 4-wood by 0.019 depending on the approach spread, and 9 is Driver
  by 0.007 to 0.026.

## 2. Hole 10: aim 18 left

The 2-wood's best aim from a 0.25-yd grid on 40,000 swings is -17.25. Six other swing sets give -17, -18, -18.5,
-19, -19, -19. The average over 64 prior draws gives -17.5. The default-seed two-stage solve gives -20.5, which
costs 0.007; the same solve on 32,000 swings on the current map gives -18.5. The 10th has the bumpiest aim curve (green, sand and pond in the landing area). If the re-solved book
shows -17 to -19, nothing to do. Either way the club is the 2-wood (by 0.060 +/- 0.003; six of six swing sets).

## 3. Second shot: does the finish position change the next shot's value correctly?

The engine scores a tee ball from a table of distance and lie. It does not know the angle, the water by 16's
green, or whether a par 5 can be reached. To check it I played the next shot explicitly (`mdp.py`): from every
playable cell between 120 yds and the green, the engine's own swing model hits the best next shot toward the green
(an ideal club for the distance up to a 250-yd carry, or a lay-up; 7 lateral aims; wider and shorter from rough
and sand), and the finish is scored on the engine's own per-cell strokes (putts on the green, short game by lie,
water, sand). Cells more than 235 yds out are solved after the nearer ones on the improved values, so a par-5
second shot chooses between going for the green and laying up. The same rollout on a featureless hole is
subtracted, so the table keeps its level and its value of distance and only this hole's geometry is added.

Frozen state, next-shot spread 1.0 / 1.6 / 2.2 times the stated iron pattern (`exp4_mdp.py`):

| hole | table | with the rollout |
|---|---|---|
| 9 | Driver +13, 0.025 | Driver +13, 0.025 / 0.025 / 0.030 |
| 10 | 2-wood, 0.060 | 2-wood, same aim, 0.065 / 0.077 / 0.086 |
| 16 | 4-wood +6.5, 0.108 | 4-wood +6 / +5.5 / +5.5, 0.107 / 0.098 / 0.088 |
| 11 | Driver +17.5, 0.031 | Driver +17.5, 0.037 / 0.031 / 0.037 |
| 3 | Driver -9, 0.051 | Driver -9, 0.056 / 0.063 / 0.061 |
| 8 | Driver -44.5, 0.057 | Driver -46.5 / -45.5 / -46, 0.075 / 0.072 / 0.066 |
| 13 | Driver +1, 0.122 | Driver -3.5 / -1.5 / +0.5, 0.066 / 0.112 / 0.137 |
| 18 | Driver +14.5, 0.132 | Driver +10 / +14.5 / +15.5, 0.023 / 0.060 / 0.094 over 4-wood |
| 1, 2, 5, 6, 15 | Driver | same club, aims within 1 yd, margins within 0.035 |

* **No club changes on any hole.** On the three close holes the aim moves by at most 1 yd.
* On 16 the approach over the water costs 0.2-0.3 more than the table says from anywhere in the fairway, so the
  hole is harder than the table thinks, but the order of the clubs is the same.
* 13 and 18 (par 5s) lose part of the Driver's margin. Part of that is the method: the featureless hole rewards
  a 240-yd second shot onto an open green more than the table does, and 18's green has water beside it. The Driver
  still wins in every variant.
* **Raw rollout** (current map, `exp4_mdp.py ... raw`: the rollout's value replaces the table, so the value of
  distance is the rollout's own, which is flatter than the table beyond 200 yds). Spread 1.6 / 1.0: every club
  stays except 11 (Driver by 0.003 / 4-wood +9 by 0.019). 9: Driver by 0.026 / 0.007. 10: 2-wood by 0.052 / 0.054,
  aim -20 / -19.5. 16: 4-wood by 0.052 / 0.055, aim +7 / +8.5. 18: Driver by 0.032 / 0.056. So the second shot
  does not change 9, 10 or 16, and it confirms that 11 depends on how much a yard is worth.
* Limit: the ground beyond 345 yds from the tee was not hand-checked (greens, greenside sand and water are OSM
  and lidar). This is a check, not a replacement for the table.

## 4. Lost ball in the fescue

* What the engine assumes: a ball in the long grass is lost 25 % of the time at the edge, rising linearly to 65 %
  ten yards in. Lost is stroke and distance. Found is a punch-out (one stroke, about 35 yds of progress, a 10 %
  chance of another).
* Reasonable? For dormant November fescue with a three-minute search I would put the deep figure lower than 65 %.
  Nobody has measured it here.
* Does it matter? No. At 5-25 % and at 40-90 %: no club changes, aims move 1 yd at most (9), margins move by up
  to 0.010 (11: 0.040 / 0.022; 16: 0.098 / 0.108). The picks finish in the long grass on 0-6.7 % of swings
  (3: 6.7 %, 11: 5.9 %, 5: 5.3 %).
* If the fescue is staked as a penalty area, the cost is lower than stroke and distance; that is inside the range
  tested.

## 5. Stroke and distance (OB on 3)

The engine charges 1 + (Tour tee value for the hole's length + 0.40). The tee table is clipped at 300 and 600 yds.
The exact cost is 1 + the hole's own expected score under the same model, a fixed point (`exp5_sd.py`):

| hole | engine's replay value | hole's own value | effect of using the exact value |
|---|---|---|---|
| 3 (630 yds) | 5.22 | 5.68 | OB and lost balls cost 0.46 more; Driver margin 0.051 -> 0.044 (runner-up becomes the 4-wood); aim unchanged |
| 10 (271 yds) | 4.11 | 3.58 | lost balls cost 0.53 less; margin 0.060 -> 0.061; aim unchanged |
| other eleven | within 0.19 of their own value | | aims within 0.5 yd, margins within 0.002 |

On 3 the Driver finishes OB on 0.3 % of swings at the chosen aim (the yard starts 53 yds right of it), which is why
0.46 strokes on the penalty moves so little. Patch if wanted: `model.tee_value` returns the hole's solved value when
the config carries one. Not needed for Saturday.

## 6. Water

One stroke, then a rough lie at the point where the ball crossed the margin, found by walking back along the flight
line from the tee. That is lateral relief and it is applied correctly. A pond that has to be carried again after
the drop is not in the table; the rollout in section 3 prices it and changes nothing (2, 10, 16).

## 7. Monte Carlo and winner's curse

* Every club and aim sees the same swings (common random numbers), and margins carry paired SEs of 0.001-0.003.
  That is sound.
* Six independent swing sets per hole (`exp3_aim_mc.py`): the same club 6 of 6 times on all 13 holes; aim SD
  0.2-0.8 yds; the chosen club's value on fresh swings differs from its in-sample value by -0.002 to +0.002; the
  in-sample and fresh margins agree within 0.002. With the smallest margin at 0.025 and SEs of 0.002, choosing the
  best of 7 clubs does not bias anything.
* One pattern against the average over 64 prior draws (`exp6_prior_vs_central.py`; 3, 8, 9, 10, 11, 16): the same
  club on all six, aims within 0.5 yd (10: 3 yds, finding 2), margins within 0.015.
* "Better in X % of what-if golfers" is the share of prior draws in which the pick wins. On 10 it reads 0.59 for a
  pick that wins by 0.056 on average. It is not a confidence level, and with one golfer in scope it should come
  off the page.
* The SE is not the uncertainty of the decision. 0.031 +/- 0.002 on 11 is 15 standard errors, and the choice of
  table (section 1) moves it by 0.036.

## 8. Aim search

Against a 0.25-yd grid on 40,000 swings with no smoothing:

* The engine's aim (0.5-yd grid, 1-yd smoothing, spline) is within 1.25 yds of the fine optimum on 12 of 13 holes,
  and the loss is 0.000-0.001. The exception is 10 (finding 2).
* The optimum is a shallow bowl: curvature 0.0003-0.0007 strokes per yd squared (8: 0.00014). Aiming 3 yds off
  costs 0.001-0.010, 5 yds 0.003-0.022, 10 yds 0.014-0.075. The 0.005 window is 5-8 yds wide (8: 11.5), which is
  what the page's bar shows.
* Which side is cheaper to miss the aim on (cost of 5 yds either way): right on 1, 2, 3 and 6 (left costs about
  twice as much); left on 10, 11, 15 and 18; even on 5, 8, 9, 13 and 16.
* The 60-yd bound binds nowhere (8's best aim is -45).
* The engine slides the pattern sideways; a real aim turns it about the tee. On 8 (9 degrees) both clubs score
  0.02 worse than the engine says, the best aim moves from -45.75 to -44, and the margin is unchanged (0.057 ->
  0.059). Elsewhere under 0.013 strokes and 1.25 yds. No change needed.

## 9. Dispersion: is the one oval right?

The central pattern, measured on 200,000 swings at 70 F (`exp2_disp.py stats`):

| club | 95 % width (yds) | lateral SD | as an angle | carry SD, good swings | 95 % carry window, all swings | beyond 40 yds off line |
|---|---|---|---|---|---|---|
| Driver | 70.9 | 18.1 | 3.47 deg | 8.8 | 59 | 2.8 % |
| 2-wood | 65.5 | 16.7 | 3.43 deg | 8.2 | 57 | 1.7 % |
| 4-wood | 54.6 | 13.9 | 2.97 deg | 7.5 | 54 | 0.5 % |
| Long iron | 43.6 | 11.1 | 2.91 deg | 6.3 | 44 | 0.1 % |
| Mid iron | 37.1 | 9.5 | 2.84 deg | 5.7 | 39 | 0 |
| 8-iron | 32.7 | 8.3 | 2.88 deg | 5.0 | 35 | 0 |

* **Size.** 70 yds is the DECADE figure for a good player's driver (Fawcett: "every ounce of 70 yards"; quoted
  from `spirit_hollow/research.md`). Right by that standard. At 60, 65, 76 and 82: no club changes; 9 and 11 thin
  to 0.010 and 0.004 at 82. At 90 the 4-wood ties the Driver on 3, 9 and 11.
* **Shape.** Good swings are 71 wide by 35 deep for the Driver (4 x 8.8): wider than long, the DECADE shape. All
  swings together are 59 deep because mishits finish short (12 % carry 92-95 %, 2.5 % carry 65-85 %). Depth x0.8
  or x1.3: no club changes, aims within 1 yd.
* **Per-club scaling.** The woods follow Will's own 65 : 60 : 50. If the 4-wood were 60 (DECADE's usual fairway
  wood) or 63 (the Driver's angle): 16 stays 4-wood by 0.07-0.08, 10 stays 2-wood by 0.09-0.10, nothing else moves.
* **Tilt.** A push finishes short and a pull long (correlation 0.1), plus a carry loss with curvature. At 0.4 or
  -0.2: no club changes, aims within 3.5 yds on 10 and 1.5 elsewhere.
* **Tails.** Gaussian apart from the mishits. Tested: a big-miss mode added on top (6 % of swings at 2.2x, 10 % at
  2.5x) and Student-t with 5 and 3 degrees of freedom at the same 95 % width. No club changes; margins move by up
  to 0.012; aims by 0-2.5 yds (t3 on 9: 3 yds).

  | hole | central | + 6 % big misses | + 10 % big misses | t5, same width |
  |---|---|---|---|---|
  | 3 (OB right) | Driver -9, 0.051; OB 0.3 % | -9, 0.049; OB 0.6 % | -9, 0.047; OB 0.8 % | -8.5, 0.068; OB 0.5 % |
  | 10 (pond) | 2-wood -20.5, 0.060; water 5.7 % | -20.5, 0.057; 5.5 % | -20.5, 0.053; 5.4 % | -20, 0.069; 5.8 % |
  | 2 (pond) | Driver +14.5, 0.082; water 1.0 % | +15, 0.082; 1.6 % | +14.5, 0.079; 2.2 % | +13.5, 0.084; 1.3 % |

* **Ground.** Roll x0.7: no change. Roll x1.3 (frozen or firm): 10 becomes a tie (2-wood by 0.011 over 4-wood)
  and 9 thins to 0.010.

## 10. Par-3 aim boxes: putting and short-game values (PAR3.md)

Reviewed from the method and the committed sensitivity table; not re-run, and not checked against the par-3
re-solve of `ca4480af1`.

* Putting: Broadie's Tour putts by distance (1.50 from 8 ft, 1.87 from 20, 1.98 from 30) + 0.06. Short game by
  lie + 0.15. These are the standard values with small offsets. A level offset cannot move a box, because it adds
  the same amount to every outcome of the same kind.
* "Aim short by 3.5-6.5 yds" is a statement about roll. The box is the landing spot; each iron rolls its stated
  fairway roll (7-iron about 6 yds, 5-iron 8), so the ball finishes at about the centre. That is the right target
  for an unknown pin.
* Robust within the stated limits: half the roll puts the best landing spot 2.5-3.5 yds deeper and keeping the
  page's box costs 0.010-0.017; 1.5x the roll, 2-3 yds shorter, 0.008-0.020. Dispersion +/-15 %, depth x2 and
  temperature: under 0.01.
* The carry matters more: 5 yds wrong on a club's number costs 0.03-0.08. The 5-, 7-, 9-iron and wedge carries are
  assumed.

## Risk, in one line

Expected score is the right target for 36 holes of stroke play. Taking the lowest-variance club on every tee would
cut the tee-shot SD from 1.16 to 0.46 strokes a round and cost 4.4 strokes (`exp7_risk.py`).

## Not verified

* Which table Will means (section 1).
* The lost-ball rate in November fescue: a guess that does not matter.
* The rollout rests on ground near the greens that was not hand-checked.
* Fawcett's and Broadie's figures are quoted from `spirit_hollow/research.md` or from memory; nothing was fetched.
* The sensitivity tables are on `222f7ece4`. On `ca4480af1` only the base picks were re-solved (same clubs; aims on
  2, 3 and 5 as in the header).
