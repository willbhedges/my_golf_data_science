# Gateway National: review of the decision model (statistics), Nov 13 2026

For Will, NCCGA Regional 3, Back tees. Scope set by Will on Nov 13: his stated carries are taken as given, one
standard pattern per club (a DECADE-style oval) is the model of a normal swing, and the output is one club and one
aim per hole. So this review asks whether that one answer is right. It does not give answers by form or by mood.

**Checkpoint 1** (03:45 UTC Nov 13). Everything below was run on a frozen copy of the engine and map at commit
`222f7ece4` ("final map under the 3-yd rule"), because the shared checkout changed four times while the first runs
were going. Code: `second_pass/model/` (it imports the engine and edits nothing). `run_all.sh <snapshot> <out>`
repeats every table.

## 0. Verdict in one table

Central-world picks on the frozen state (two-stage solve, 16,000 common swings; forecast 35-47 F). "Honest margin"
is the range over the three golfers whose pattern and scoring table belong together (section 1a).

| hole | club and aim (yds, + = right) | margin as the engine reports it | honest margin | what could change it |
|---|---|---|---|---|
| 1 | Driver -8.5 | 0.054 over 2-wood | 0.03 to 0.04 | nothing tested |
| 2 | Driver +14.5 | 0.082 | 0.06 to 0.07 | nothing tested |
| 3 | Driver -9 | 0.051 | **0.007 to 0.016** over 4-wood | driver pattern over ~85 yds wide |
| 5 | Driver 0 | 0.098 | 0.07 to 0.08 | nothing tested |
| 6 | Driver +6 | 0.118 | 0.09 to 0.10 | nothing tested |
| 8 | Driver -44.5 | 0.057 | 0.03 to 0.05 | nothing tested |
| 9 | Driver +13 | 0.025 | **0.00 to 0.01: a tie with 4-wood +2** | see 1a |
| 10 | 2-wood, aim **-18** (the stored -20.5 is Monte Carlo noise, section 3) | 0.060 over 4-wood | 0.04 to 0.05 | firm ground (roll x1.3): tie with 4-wood |
| 11 | Driver +17.5 | 0.031 | **0.00: a tie with 4-wood +9** | see 1a |
| 13 | Driver +1 | 0.122 | 0.10 to 0.12 | nothing tested |
| 15 | Driver +14.5 | 0.109 | 0.08 to 0.09 | nothing tested |
| 16 | 4-wood +6.5 | 0.108 | 0.05 to 0.08 | nothing tested |
| 18 | Driver +14.5 | 0.132 | 0.11 to 0.13 | nothing tested |

**No club changes.** Of about 60 model variants per hole, the club changes only on 3, 9 and 11, and only to a
4-wood that is level with the Driver. The aims are stable to about 2 yds, except 10.

What to do before the tournament, in order of effect on Will's decisions:

1. **Label 9 and 11 as ties between Driver and 4-wood**, and 3 as close. The engine's 0.025 / 0.031 / 0.051
   overstate the Driver by 0.02 to 0.04 (section 1a). Page text only. If Will wants a rule for a tie: take the
   Driver, because on 3, 9 and 11 it loses at most 0.012 in any golfer tested and the 4-wood loses 0.033 to 0.052 in the engine's central one.
2. **Hole 10: aim 18 left, not 20.5.** A 40,000-swing curve puts the 2-wood's best aim at -17.25, six other seeds
   give -17 to -19, and the prior average gives -17.5. Aiming at -20.5 costs 0.007. If the re-solve's book already
   shows -17 to -19, nothing to do.
3. **Drop "better in X % of what-if golfers" from the page.** It is not a confidence level (section 4). Show the
   margin and a close-call label.
4. Nothing else needs to change before Saturday. Three engine corrections are right in principle and are measured
   below, but none changes a club or moves an aim by more than 1.5 yds: the stroke-and-distance value (1b), the aim
   as a rotation (3), and the hole-specific next-shot value (1d).

## 1. Objective

### 1a. The value function: right in kind, and one inconsistency that matters on three holes

The engine minimises expected strokes to hole out. After the tee shot it reads a table V(lie, distance): the PGA
Tour baseline (Broadie) plus an amateur offset, 0.36 + 0.0012 per yard beyond 150, with the rough gap x0.75.

* **A level shift changes nothing.** With the offset at 0.20 instead of 0.36 every club and aim is the same and the
  margins move by 0.000 to 0.008. Only stroke-and-distance and the putts on the 10th green see the level. So "is
  the baseline 0.2 too high for a scratch player" is not a decision question.
* **The slope with distance is the decision.** It sets what 20 more yards are worth. Broadie's published figures
  (Every Shot Counts; quoted from memory, not re-read here) are about 0.75 strokes a round for a Tour player and
  1.3 for an 80-shooter for 20 yards, so a scratch-to-5 player is near 1.0 to 1.1: about 1.4 times the Tour value.
  The engine's 0.0012 per yard on top of the Tour slope (0.0039 per yard at 100-200 yds) is 1.3 times. That is the
  right size.
* **The inconsistency.** The engine pairs that scratch-to-5 table with a Tour-width pattern (driver 95 % width 70
  yds). Played forward on a featureless hole, the engine's own iron pattern with Tour putting scores the Tour table
  within 0.02 to 0.09 (`exp4_calib.py`: 2.76 against 2.80 from 100, 2.93 against 2.95 from 150, 3.10 against 3.19
  from 200). To score the amateur table at 150 yds the irons would have to be 1.6 times as wide. Both halves favour
  the longer club: the narrow pattern makes the Driver safe, and the amateur slope makes its yards worth more. A
  real golfer is one or the other.

Re-solved for golfers whose two halves belong together (`exp8_coherent.py`, 32,000 swings, SE 0.001-0.002):

| golfer | 3 | 9 | 11 | other ten holes |
|---|---|---|---|---|
| engine central (width 70, 5-handicap table) | Driver by 0.050 | Driver by 0.027 | Driver by 0.033 | as the table in section 0 |
| elite (width 70, Tour table) | Driver by 0.007 | 4-wood, 2-wood and Driver within 0.0014 | 4-wood by 0.004 | same clubs; 8 aims 4 yds less left |
| scratch (width 76, Tour + 0.22 + 0.0006 / yd) | Driver by 0.012 | Driver by 0.008 | Driver by 0.001 | same clubs, aims within 1.5 |
| 5 handicap (width 82, engine table) | Driver by 0.016 | Driver by 0.011 | Driver by 0.002 | same clubs, aims within 2.5 |
| width 70, scratch table (Will's scope: DECADE oval) | Driver by 0.032 | Driver by 0.017 | Driver by 0.017 | same |
| width 82, scratch table | 4-wood by 0.005 | 4-wood by 0.002 | 4-wood by 0.012 | same |

* Under Will's scope (the 70-yd oval), the Driver holds on all three for any amateur table from scratch to 5.
* The published on-course figure for 0-5 handicaps is nearer 82 yds (`spirit_hollow/research.md`: Arccos / Stagner,
  7 % of drives more than 40 yds off centre). At 82 with a scratch table the three holes go to the 4-wood by 0.002
  to 0.012.
* So 9 and 11 are ties and 3 is close. Either club costs under 0.02 a hole. The other ten holes do not move.

**Recommendation.** Keep the table. Print the honest margins for 3, 9 and 11. Optional, not needed for Saturday: a
config `player` block that sets the central table to the scratch one (am_off 0.22, am_slope 0.0006, am_tee_off
0.25) gives the "width 70, scratch table" row and changes no club.

Other table parameters (`exp1_value.py`; no club changes, aims within 1 yd unless noted):

| variant | largest effect |
|---|---|
| rough gap x0.4 / x1.3 | 9: margin 0.036 / 0.011; 8: aim 3.5 yds further left when rough is cheap |
| sand gap x1.5 | margins within 0.007 |
| trees always a chip-out | margins within 0.003 |
| no line-of-sight cost | no change |

### 1b. Penalties

* **Stroke and distance is mispriced on two holes, without effect.** The engine charges 1 + (Tour tee baseline for
  the hole's length + 0.40). That table is clipped at 300 and 600 yds. The exact cost is 1 + the hole's own
  expected score, a fixed point (`exp5_sd.py`):

  | hole | engine's replay value | hole's own value | effect of the exact value |
  |---|---|---|---|
  | 3 (630) | 5.22 | 5.68 | OB and lost balls cost 0.46 more; Driver margin 0.051 -> 0.044 (runner becomes the 4-wood); aim unchanged |
  | 10 (271) | 4.11 | 3.58 | lost balls cost 0.53 less; margin 0.060 -> 0.061; aim unchanged |
  | other eleven | within 0.19 | | aims within 0.5, margins within 0.002 |

  Patch if wanted (4 lines, `model.tee_value`: return the hole's own solved value when the config carries one).
  Not needed for Saturday.
* **Lost ball in the fescue.** The engine assumes 25 % lost at the edge of the long grass, rising to 65 % ten yards
  in, stroke and distance when lost, a punch-out when found. For dormant November fescue 65 % is probably high, and
  nobody has measured it here. It does not matter: at 5-25 % or at 40-90 % no club changes, aims move 1 yd at most
  (9: 1 yd), and margins move by up to 0.010 (11: 0.040 / 0.022). The tee balls finish in the long grass 0-6.7 %
  of the time (3: 6.7 %, 11: 5.9 %, 5: 5.3 %).
* **Water.** One stroke plus a rough lie at the point where the ball crossed the margin (walked back along the
  flight line). That is the lateral-relief rule and it is applied correctly. A pond that must be carried again
  after the drop is not priced by the table; the rollout in 1d prices it and changes nothing.

### 1c. Risk

Expected score is the right target for 36 holes of stroke play: the total is a sum of about 36 nearly independent
holes, so the lower mean wins more often unless one is several strokes behind with a few holes left. The numbers
(`exp7_risk.py`): the 13 tee shots carry an SD of 1.16 strokes a round at the best clubs. Taking the lowest-variance
club on every hole cuts that to 0.46 and costs 4.4 strokes a round.

### 1d. Is a one-shot table enough? A hole-specific rollout says yes here

The table knows distance and lie. It does not know that 16's green has water short and left, or that a par 5 is
reachable. So I built the next shot explicitly (`mdp.py`): from every playable cell between 120 yds and the green,
the engine's own swing model plays the best next shot (an ideal club for the distance, up to a 250-yd carry, or a
lay-up; 7 lateral aims), scored on the engine's per-cell strokes (putts on the green, short game by lie, water,
sand). Cells more than 235 yds out are solved after the nearer ones, on the improved values, so a par-5 second
shot chooses between going for the green and laying up. The same rollout on a featureless hole is subtracted, so
the table keeps its level and its value of distance and only the hole's own geometry is added.

Results on the map states of 03:00-03:10 UTC (the frozen-state run is listed in section 6 when finished):

* No club changes on any hole, for an approach spread of 1.0, 1.6 or 2.2 times the stated iron pattern.
* Aims move 0 to 2.5 yds (13: 2.5 left; the others 1 or less).
* Margins: 16 grows (the approach over the water from further back costs 0.15 to 0.30 more than the table says, so
  laying back with an iron is worse than it looked); 8 and 10 grow by 0.01 to 0.02; 13 and 18 shrink by 0.01 to
  0.04 at 1.6.

Limits: the ground beyond 345 yds from the tee was not hand-checked (greens, greenside sand and water are OSM and
lidar), so I would not adopt these values for picks. As a check they say the one-shot table is adequate at Gateway.

### 1e. Is there something better than strokes gained?

Expected strokes to go, minimised shot by shot, is the Bellman-optimal objective for stroke play. "Strokes gained"
is that same quantity with a constant subtracted, so it picks the same shot. The weak point is not the objective
but the table: one average over all holes. The improvement that is real is the course-specific value in 1d, and
at Gateway it does not change a decision. Optimising for the worst case over unknown dispersion was dropped under
Will's scope; for the record, on 3, 9 and 11 the Driver is also the choice with the smallest worst-case loss
(0.012 against 0.033 to 0.052 for the 4-wood) over the six golfers of 1a.

## 2. Dispersion

What the engine's central pattern is, measured on 200,000 swings at 70 F (`exp2_disp.py stats`):

| club | 95 % width (yds) | lateral SD | as an angle | carry SD, good swings | 95 % carry window, all swings | beyond 40 yds off line |
|---|---|---|---|---|---|---|
| Driver | 70.9 | 18.1 | 3.47 deg | 8.8 | 59 | 2.8 % |
| 2-wood | 65.5 | 16.7 | 3.43 deg | 8.2 | 57 | 1.7 % |
| 4-wood | 54.6 | 13.9 | 2.97 deg | 7.5 | 54 | 0.5 % |
| Long iron | 43.6 | 11.1 | 2.91 deg | 6.3 | 44 | 0.1 % |
| Mid iron | 37.1 | 9.5 | 2.84 deg | 5.7 | 39 | 0 |
| 8-iron | 32.7 | 8.3 | 2.88 deg | 5.0 | 35 | 0 |

* **Size.** 70 yds is DECADE's number for elite players' good swings (Fawcett: "every ounce of 70 yards"). As an
  angle it is the Tour's (about 3.4 deg in Broadie's data, from memory). For a scratch-to-5 golfer over all
  on-course drives the published figure is nearer 82. Under Will's scope 70 stands. At 76 and 82 no club changes
  with the engine's table (9: margin 0.016 / 0.010; 11: 0.017 / 0.004; 3: 0.036 / 0.021). At 90 the 4-wood ties on
  3, 9 and 11.
* **Shape.** Wider than long for good swings: 71 wide by 35 deep (4 x 8.8) for the Driver, the DECADE shape. All
  swings together are 59 deep because the mishits are short: 12 % carry 92-95 %, 2.5 % carry 65-85 %. Depth x0.8 or
  x1.3: no club changes, aims within 1 yd.
* **Per-club scaling.** The woods follow Will's own 65 : 60 : 50. As angles the 4-wood (2.97 deg) is straighter
  than the Driver (3.47), and the irons are near 2.9. If the 4-wood were as wide as DECADE's usual fairway wood (60,
  or the same angle as the Driver, 63): 16 stays 4-wood by 0.07-0.08, 10 becomes 2-wood by 0.09-0.10, and nothing
  else moves. No current pick depends on the 4-wood being that straight.
* **Tilt.** A push finishes short and a pull long (correlation 0.1), plus a carry loss with curvature. At
  correlation 0.4 or -0.2: no club changes, aims within 3.5 yds on 10 and within 1.5 elsewhere.
* **Tails.** The lateral miss is Gaussian apart from the mishits (kurtosis 3.1). Tested: a 6 % big-miss mode at
  2.2x and a 10 % mode at 2.5x added on top, and Student-t with 5 and 3 degrees of freedom at the same 95 % width.
  No club changes. Margins move by up to 0.012 for the added modes (16: 0.108 -> 0.096). Aims move 0-2.5 yds
  (t3 on 9: 3 yds). On the
  three holes named in the brief:

  | hole | central | + 6 % big misses | + 10 % big misses | t5, same width |
  |---|---|---|---|---|
  | 3 (OB right) | Driver -9, 0.051; OB 0.3 % | -9, 0.049; OB 0.6 % | -9, 0.047; OB 0.8 % | -8.5, 0.068; OB 0.5 % |
  | 10 (pond) | 2-wood -20.5, 0.060; water 5.7 % | -20.5, 0.057; 5.5 % | -20.5, 0.053; 5.4 % | -20, 0.069; 5.8 % |
  | 2 (pond) | Driver +14.5, 0.082; water 1.0 % | +15, 0.082; 1.6 % | +14.5, 0.079; 2.2 % | +13.5, 0.084; 1.3 % |

  A fat tail at a fixed 95 % width pulls weight into the middle, so it helps the longer club; an added tail hurts
  it slightly. Neither changes a decision: the OB on 3 starts 53 yds right of the aim, so even the 10 % big-miss
  mode puts 0.8 % of drives there, and on 10 the water is taken by ordinary swings, not by the tail.
* **Soft or firm ground.** Roll x0.7: no change (10: 2-wood by 0.110). Roll x1.3: 10 becomes a tie (2-wood by
  0.011), 9 thins to 0.010.
* **Recommendation.** Keep the pattern. One central pattern and the average over 64 "what-if golfers" give the
  same club and the same aim within 0.5 yd on the holes compared so far (8, 9, 10; `exp6_prior_vs_central.py`), so
  the single pattern loses nothing.

## 3. Aim search

Checked against a 0.25-yd grid on 40,000 swings with no smoothing (`exp3_aim_mc.py`):

* **The search is fine.** The engine's aim is within 1.25 yds of the fine optimum on 12 of 13 holes, and the loss
  from the difference is 0.000-0.001. The exception is **10: -20.5 against -17.25, loss 0.007**. Its curve is the
  bumpiest (green, sand and pond in the landing area). Use -18.
* **How sharp is the optimum?** Curvature 0.0003-0.0007 strokes per yd squared (8: 0.00014). Aiming 3 yds off costs
  0.001-0.010, 5 yds off 0.003-0.022, 10 yds off 0.014-0.075. The 0.005 window is 5-8 yds wide (8: 11.5), which is
  what the page's bar shows. It is a fair description: inside the bar the aim does not matter.
* **Which side to err on**, from the cost of 5 yds either way: err right on 1, 2, 3 and 6 (left costs about twice
  as much); err left on 10, 11, 15 and 18; even on 5, 8, 9, 13 and 16.
* **The 60-yd bound** binds nowhere (8's best aim is -45).
* **Aim as a sideways shift.** The engine slides the pattern sideways; a real aim turns it about the tee. At 45 yds
  left on 8 that is 9 degrees: both clubs score 0.02 worse than the engine says, the best aim moves from -45.75 to
  -44, and the margin is unchanged (0.057 -> 0.059). Elsewhere the effect is under 0.013 strokes and 1.25 yds (10: the 4-wood scores 0.012 worse, so the 2-wood's
  margin grows). No change
  needed.
* **One aim for the average golfer or an aim per golfer** is outside the scope now. For the record the per-golfer
  best aims have an SD of 2.6-4.9 yds in the stored book, about the half-width of the bar.

## 4. Monte Carlo and inference

* **Common random numbers and paired SEs: sound.** Every club and aim sees the same swings. The central margins
  have paired SEs of 0.001-0.003.
* **Winner's curse: none measurable.** Six independent swing sets per hole: the same club 6 of 6 times on all 13
  holes; aim SD 0.2-0.8 yds; the chosen club's value on fresh swings differs from its in-sample value by
  -0.002 to +0.002 (SD 0.002-0.003); in-sample and fresh margins agree within 0.002. With margins of 0.025 or more
  and SEs of 0.002, picking the best of 7 clubs does not bias the result.
* **The real error is model error, not Monte Carlo error.** 0.031 +/- 0.002 on 11 looks like 15 standard errors.
  The honest statement is 0.00 to 0.03 depending on the scoring table and width (1a). The page's SE should not be
  read as the uncertainty of the decision.
* **"Better in X % of what-if golfers"** is the share of prior draws in which the pick beats the runner-up. It
  mixes real differences between hypothetical golfers with noise, and on 10 it reads 0.59 for a pick that wins by
  0.056 on average. Under Will's scope there is one golfer. Drop the line.
* **Close-call label.** Suggested rule: "tie" when the honest margin is under 0.01, "close" under 0.02. On this map:
  tie on 9 and 11, close on 3.

## 5. Par-3 targets (PAR3.md)

Not re-run; reviewed from the method and the committed sensitivity table.

* **Putting and short game.** Broadie's Tour putts by distance (1.50 from 8 ft, 1.87 from 20, 1.98 from 30) + 0.06,
  short game by lie + 0.15. Those are the right tables and reasonable offsets for a scratch-to-5 player. As in 1a a
  level shift cannot move the box.
* **"Aim short by 3.5-6.5 yds" is a statement about roll, not about caution.** The box is the landing spot. The
  model rolls each iron its stated fairway roll (7-iron about 6 yds, 5-iron 8), so a ball that lands 3.5-6.5 short
  finishes at about the centre. That is the right target for an unknown pin: the finish at the centre, moved off
  the expensive side.
* **Robust?** Yes within the stated limits. With half the roll the best landing spot is 2.5-3.5 yds deeper and
  keeping the page's box costs 0.010-0.017; with 1.5x the roll it is 2-3 yds shorter and costs 0.008-0.020. Dispersion
  +/-15 %, depth x2 and temperature cost under 0.01.
* **What matters more** is the carry: 5 yds wrong on the club's number costs 0.03-0.08. The 5-, 7-, 9-iron and
  wedge carries are assumed, not Will's.
* **Not tested:** the box for a visible pin (uniform pins only).

## 6. Results log (frozen state `222f7ece4`)

Filled by `run_all.sh`; numbers quoted above come from these files' logs.

| file | what | status |
|---|---|---|
| `exp1_value.py` | scoring table and penalty variants, 13 holes x 12 | done |
| `exp2_disp.py` | pattern variants, 13 holes x 21 | done |
| `exp3_aim_mc.py` | fine aim curves, rotation, 6 independent swing sets | done |
| `exp5_sd.py` | stroke-and-distance fixed point | done |
| `exp7_risk.py` | mean and SD by club | done |
| `exp8_coherent.py` | coherent golfers | done |
| `exp4_mdp.py` | hole-specific rollout, spreads 1.0 / 1.6 / 2.2 | running on the frozen state; earlier-state results in 1d |
| `exp6_prior_vs_central.py` | one pattern against the prior average | 8, 9, 10 done; 11, 16, 3 running |

## 7. Not verified

* Will's handicap, his real pattern and his 8-iron and wedge carries. Under the scope they are assumptions.
* Broadie's and Fawcett's figures are quoted from memory or from `spirit_hollow/research.md`; nothing was fetched.
* The lost-ball rate in November fescue is a guess that turns out not to matter.
* The rollout in 1d rests on ground near the greens that was not hand-checked.
* The frozen state is `222f7ece4`. If the map or the physics change again, the picks in section 0 move with them
  (they moved on 8, 9, 10 and 16 between 02:10 and 03:05 UTC); the findings about the model should not.
