# holesolve: a full-hole value solver, built and checked on Gateway National (Nov 13 2026)

Research build. Nothing in any course's data, config, solved outputs or page was changed, and the engine and
fastsolve behave as before. Code: `course_data/courses/holesolve/` (README there). Results:
`course_data/courses/holesolve/results/`. Calm, 45 F, central world, Back tees unless stated.

The checkout moved while this ran (hole 10's map changed at 22:13 UTC, commits `0061ee7b2` and `281442149`), so every
number below is from a frozen copy of the engine and the course inputs: **`281442149`** (the map now published)
for everything, and **`ae810a91d`** (the map the three hole-10 studies were made on) for the comparison with those
studies. Each results file carries its state. The "published book" column in section 5 is the book at `281442149`; the
page was re-solved afterwards for a 10:36 Saturday start (`8e4eb175d`, 42-48 F instead of 35-47 F; maps unchanged):
the same 13 clubs, aims within 0.5 yd, hole 10's margin 0.026 instead of 0.042.

## Answer in short

* **It works and it is fast.** One hole takes 4-13 s on 4 threads (C kernel, 5,000-10,000 states, 2-3 sweeps), plus
  2-4 s to paint the raster and 3 s for the engine's own tee solve on its values. All 13 holes: 1 min 42 s of DP.
* **Raw, the DP player is much better than the table says he is:** 0.18-0.25 strokes per shot inside 150 yds, 0.37 at
  200, 0.56 at 250 (the 4-wood reaches), 0.5-0.67 from 300-450. The stated patterns are Tour-accurate; the table is
  Tour + 0.36 and more with distance. A per-shot calibration term closes it: on a flat hole with no trouble the
  calibrated DP returns the table (fairway states within 0.003 sd, every state within 0.03).
* **It reproduces today's one-off studies.** Hole 10 dropped balls: 19.0 % of 2-woods, engine 3.95, DP 3.87
  (HOLE10_DROPS: 18.9 %, 3.95, 3.86). Hole 10 lay-ups with the wedge played out: raw DP 3.85 / 3.92 / 4.05 for long
  iron / mid iron / 8-iron (HOLE10_LAYUP: 3.86 / 3.94 / 4.06). Par 5 go shots from the Driver's spot: raw DP 3.56 on
  6 and 3.57 on 13 (PAR5.md: 3.58 and 3.59, same share on the green and in the penalty area).
* **No tee pick changes.** All 13 Back tee-shot holes keep their club under the calibrated DP and under the raw DP;
  calibrated aims move by 1.5 yds or less except 13 (3.5 yds left). Margins move by more than 0.01 on four holes:
  6 (0.118 to
  0.100), 11 (0.029 to 0.018), 13 (0.120 to 0.098), 18 (0.120 to 0.143). Under a third, level-only calibration 11
  goes to the 4-wood by 0.010: a tie, the same coin flip MODEL.md found.
* **What it adds that the table cannot see:** 16 plays 0.05 harder than the table says and the long iron falls 0.05
  further behind the 4-wood (the longer approach over the pond); the par 5s play 0.11-0.15 harder (trouble by the
  greens at 220-250 out); on 10 an 8-iron lay-up to 111 yds costs 0.10 more than its table value, a long iron to 64
  only 0.03; a dropped ball on 10 costs 1.41 strokes more than a dry one, not 1.49.
* **What it does not settle:** how much a yard is worth on a par 5. The calibration makes the DP inherit the table's
  value of distance on trouble-free ground, by construction. The Driver's edge over the 2-wood on 6 / 13 / 18 is
  0.12 on the table, 0.10 / 0.11 / 0.14 calibrated, 0.05 / 0.07 / 0.05 raw. The truth is between and only data on
  his approach shots can place it.
* **Recommendation:** not yet a replacement for the table valuation. Ready now as the standing second opinion (it
  replaces the one-off scripts). To go into the engine after the tournament: the calibration target has to be
  settled, the second-shot patterns confirmed, and the inside-30-yds anchor given a short-game model; the wiring
  itself is small (a per-hole correction raster added to the engine's value raster). Details at the end.

## 1. What was built

`V(s) = c(lie, d) + min over (club, direction) of E[1 + V(finish)]`, solved by value iteration on the hole's lie
raster (the engine's 0.5-yd raster in the tee frame, extended past the green).

| piece | what it is |
|---|---|
| state | a ball at rest on a 4-yd grid, lie class of the start = fairway, rough or sand (5,000-10,000 states a hole). First cut = the engine's blend |
| anchor | on the green, and inside 30 yds of the middle of it: the engine's own value (putts by distance; short game by lie and distance). No putting model |
| shot | the engine's `model.shots()` (sideways and carry spread, tilt, slight and heavy mishits, roll noise), roll as the engine's `finish()`. 256 scrambled-Sobol swings per club and lie, the same swings from every state: the DP solves one fixed swing distribution exactly, so there is no Monte Carlo noise between states or directions |
| clubs (config block `solver.CONFIG`) | PAR5.md's deck clubs: 4-wood 240 / 255 (no Driver or 2-wood off the deck), long iron, mid iron, 8-iron, 9-iron, PW, GW, SW; the par-3 bag's 5-iron and 7-iron; part swings 30-100 yds every 10 (layup10.py's, assumed). Rough: 4 % shorter, 25 % wider, long iron at most. Sand: 7 % shorter, 50 % wider, mid iron at most. Full swings only for the long clubs |
| directions | every degree within 40 deg of the line to the middle of the green (coarse every 4, then every degree round the best) |
| fairway, rough, sand finish | the DP's value for that lie at that point |
| trees | the engine's finish-lie rule kept as a premium over rough at the same spot, on the DP's rough value there; the "tree line in the way" charge kept the same way. Flight-path trees not priced |
| red penalty area (water; tall native under the drop rule) | one stroke + the better of (a) the DP's value at the point where the ball last crossed the edge on its own line, in that point's own lie, sand included, and (b) back on the line from the hole through that point (best dry spot, 17 distances out to 150 yds) |
| out of bounds; tall grass as a lost ball (`--tall lost`) | stroke and distance from the same spot in closed form, E = (n + sum of found values + n_gone (1 + c)) / (n - n_gone), fastsolve's arithmetic |
| stored as | DP minus table, per lie class, on the grid. A cell's value = the engine's value of the cell + the interpolated difference. The difference is smooth where the value is steep, which is why 4 yds is enough (check below) |
| sweep | 20-yd bands of distance to the hole, nearest first, each band using the bands in front of it. 2-3 sweeps to a change under 0.002 |
| tee shot | the engine's own two-stage central-world solve (3,000 swings on the whole aim grid, 16,000 on aim +/-10, `opt/solve2.py`) on a value raster that carries the DP's values. Same swings, roll, elevation and aim search as the table solve; only the value of the finishing spot differs |

Free by-products, from any spot (`HoleSolve.query`): every club's best line, strokes, target, share on the green /
in the penalty area / in sand; so go or lay up, the lay-up club and where it finishes, and the cost of a drop.

Tests (`test_holesolve.py`): the C kernel against a numpy copy of its swing loop on hole 10 (30 club-directions, 204
dropped balls among them: worst difference 0.0001); the flat hole returns the table; gone balls in closed form on a
flat hole with an OB strip (46 % gone on the tested line: kernel and numpy agree to 0.0001).

## 2. Validation 1: the flat hole, and the calibration

Flat hole: 640 yds, fairway 36 wide, rough either side, a round green of 14-yd radius, nothing else. 9,984 states.

**Raw DP against the engine's table (strokes to hole out; gap = DP - table):**

| yds | fairway: table | DP | gap | rough: table | DP | gap | sand: table | DP | gap |
|---|---|---|---|---|---|---|---|---|---|
| 40 | 2.83 | 2.65 | -0.18 | 2.96 | 2.77 | -0.19 | 3.07 | 2.86 | -0.21 |
| 60 | 2.95 | 2.70 | -0.25 | 3.11 | 2.84 | -0.27 | 3.45 | 3.17 | -0.28 |
| 80 | 3.03 | 2.79 | -0.24 | 3.18 | 2.94 | -0.25 | 3.56 | 3.32 | -0.24 |
| 100 | 3.10 | 2.88 | -0.22 | 3.27 | 3.05 | -0.21 | 3.57 | 3.40 | -0.18 |
| 125 | 3.19 | 2.99 | -0.21 | 3.37 | 3.13 | -0.24 | 3.58 | 3.36 | -0.22 |
| 150 | 3.31 | 3.08 | -0.23 | 3.49 | 3.23 | -0.26 | 3.64 | 3.39 | -0.25 |
| 175 | 3.44 | 3.16 | -0.29 | 3.62 | 3.30 | -0.32 | 3.79 | 3.47 | -0.32 |
| 200 | 3.61 | 3.24 | -0.37 | 3.78 | 3.40 | -0.39 | 4.01 | 3.61 | -0.39 |
| 225 | 3.80 | 3.50 | -0.30 | 3.96 | 3.65 | -0.31 | 4.22 | 3.92 | -0.31 |
| 250 | 4.00 | 3.43 | -0.56 | 4.13 | 3.76 | -0.37 | 4.40 | 4.04 | -0.37 |
| 275 | 4.17 | 3.71 | -0.46 | 4.28 | 3.84 | -0.44 | 4.52 | 4.08 | -0.44 |
| 300 | 4.32 | 3.79 | -0.53 | 4.41 | 3.95 | -0.46 | 4.61 | 4.14 | -0.47 |
| 350 | 4.55 | 3.98 | -0.57 | 4.64 | 4.12 | -0.52 | 4.84 | 4.32 | -0.53 |
| 400 | 4.79 | 4.15 | -0.64 | 4.88 | 4.30 | -0.58 | 5.08 | 4.50 | -0.58 |
| 450 | 5.03 | 4.35 | -0.67 | 5.12 | 4.54 | -0.57 | 5.31 | 4.74 | -0.57 |
| 500 | 5.20 | 4.59 | -0.61 | 5.29 | 4.83 | -0.46 | 5.49 | 5.02 | -0.47 |

Why:

* **The DP player hits it like a Tour player and the table says he scores 0.36 worse.** With the stated patterns a
  90-yd pitch finishes on hole 10's narrow green 93 % of the time. One shot from 150 plus the table's own putts
  and short game from where it finishes comes to the Tour table + 0.12; the engine's table is Tour + 0.36 there.
  The 0.2-0.25 per shot inside 150 is that difference. It compounds: two shots from 300 give 0.5.
* **The gap is not smooth.** At 225 it is -0.30 and at 250 -0.56: from 250 a full 4-wood (247 total at 45 F) is the
  perfect club, from 225 he is between the long iron (213) and the 4-wood. The raw model says 250 from the fairway
  is BETTER than 225 (3.43 against 3.50). That is the bag's 213-to-247 gap and "full swings only", not golf.
* The table beyond 450 yds is an extrapolation (tee shots have their own table); no tee ball here is valued there.

**The calibration.** Every state pays a per-shot term

    c(lie, d) = table(lie, d) - min over shots of E[1 + table(finish)]        on the flat hole

tabulated every yard from 30 to 620 for the three lie classes (fairway on the centre line, rough 25 yds off it, a
sand lie on the centre line). It is the amount by which the table disagrees with its own one-shot look-ahead under
the model's swings. With c in the Bellman step the table is the DP's fixed point on the flat hole, so **on
trouble-free ground DP = table**, and on a real hole what is left is what the hole's own trouble does. c is charged
to the state, not to the shot: it never changes which shot is best from a spot; it sets the level of the values the
previous shot chooses between.

| yds | c fairway | c rough | c sand |
|---|---|---|---|
| 40 | +0.18 | +0.21 | +0.23 |
| 60 | +0.25 | +0.28 | +0.52 |
| 100 | +0.22 | +0.18 | +0.45 |
| 150 | +0.24 | +0.25 | +0.33 |
| 200 | +0.37 | +0.38 | +0.24 |
| 225 | +0.28 | +0.26 | +0.26 |
| 250 | +0.55 | +0.20 | +0.34 |
| 300 | +0.35 | +0.27 | +0.35 |
| 400 | +0.39 | +0.23 | +0.20 |

**Calibrated DP on the flat hole:** centre-line fairway 30-600 yds within 0.001 of the table, rough within 0.003,
sand within 0.006. All 6,216 states within 60 yds of the line: mean +0.002, sd 0.006, 95 % within 0.017, worst 0.030
(rough states beside the fairway edge, where the ground differs from the calibration spot). The first version
tabulated c every 5 yds and left 0.04 inside 100 yds (c has club-gap structure at the part-swing distances); every
yard removes it.

What the calibration is and is not:

* It is exact for "trouble-free = the table". The table is an average over real holes, which have trouble, so every
  real hole comes out at or above its table value: Gateway's own fairways average +0.00 to +0.02 on six holes and
  +0.05 to +0.15 on 6, 13, 15, 16 and 18 (table in section 5). A fairer target is the course average or real shot
  data, not a flat hole.
* It imports the table's value of distance. Where the raw model's value of distance differs from the table's
  (above all at 220-260, the par-5 second shot), the calibrated DP sides with the table by construction.
* Two alternatives are kept for that reason: **raw** (`cal=None`) and **level-only** (`run.level_cal`: one constant
  per lie class, the mean of c between 40 and 200 yds: fairway +0.21, rough +0.27, sand +0.40; the table's level
  per shot without its value of distance, bag gap and all).

## 3. Validation 2: hole 10

### Against the three studies (their map, `ae810a91d`)

Tee solve (16,000 swings), strokes:

| tee | valuation | go | long iron | mid iron | 8-iron | go minus best lay-up |
|---|---|---|---|---|---|---|
| Back | engine table | 2-wood 25.5 L, 3.744 | 4.035 | 4.069 | 4.148 | -0.29 |
| Back | DP calibrated | 2-wood 25.0 L, 3.731 | 4.068 | 4.116 | 4.232 | -0.34 |
| Back | DP raw | 2-wood 25.5 L, 3.691 | 3.845 | 3.920 | 4.049 | -0.15 |
| Middle | engine table | 4-wood 23.0 L, 3.689 | 3.942 | 4.062 | 4.075 | -0.25 |
| Middle | DP calibrated | 4-wood 22.5 L, 3.676 | 3.965 | 4.091 | 4.127 | -0.29 |
| Middle | DP raw | 4-wood 22.5 L, 3.652 | 3.814 | 3.861 | 3.932 | -0.16 |

| study figure | study | here |
|---|---|---|
| HOLE10_LAYUP, lay-ups with the wedge played out, Back (Saturday there, calm here) | long iron 3.86, mid iron 3.94, 8-iron 4.06 | raw DP 3.85, 3.92, 4.05 |
| HOLE10_LAYUP, go minus best lay-up, wedge played out | 0.12-0.17 | raw DP 0.15 (Back), 0.16 (Middle) |
| HOLE10_LAYUP, best lay-up club | long iron on both tees; Back by 0.08 played out, Middle by 0.05 | long iron on both; Back by 0.05 calibrated / 0.08 raw, Middle by 0.13 / 0.05 |
| HOLE10_REDTEAM, go minus best lay-up, engine value | 0.30 | 0.29 |
| HOLE10_REDTEAM, explicit next shot for both options | 0.43, "makes the lay-up worse, not the go" | calibrated DP 0.34, same direction: the go moves 0.01, the lay-ups 0.03-0.08 |
| HOLE10_DROPS, 2-wood balls that are dropped | 18.9 % | 19.0 % |
| HOLE10_DROPS, a dropped ball (strokes after the tee shot, penalty included): engine / rules-correct drop | 3.95 / 3.86 | 3.95 / 3.87 |
| ... right of the green | 3.91-3.94 / 3.80-3.84 | 3.91 / 3.80 |
| ... tall grass left | 4.01-4.03 / 3.97-4.01 | 4.04 / 4.06 |
| ... short-left | 4.27-4.29 / 4.29-4.31 | 4.28 / 4.35 |
| HOLE10_DROPS, a dry ball | 2.46 | 2.46 (table and DP) |

* The raw DP is the studies' "played out" method and matches it to 0.02. The calibrated DP is the coherent version
  of the same thing: both the go's finish (green and greenside, the anchor) and the lay-up's wedge are at the
  table's level. HOLE10_LAYUP's 0.12-0.17 compared a go finishing on table values with a wedge played 0.2 better
  than the table; that is why it looked close.
* The true cost of a drop on 10: 3.87 - 2.46 = **1.41 strokes** against a dry ball (engine 1.49). The engine
  overprices drops right of the green by 0.11 (they are on short grass, 36-40 yds) and underprices the left and the
  short-left ones by 0.02-0.07 (the pitch back has trouble to cross).
* Left and short-left differ from HOLE10_DROPS by 0.05 in the other direction. Its drop model moved the ball to the
  best lie within reach of the reference point; this one drops in the reference cell's own lie.

Where the lay-up balls finish (the spots of HOLE10_LAYUP.md), strokes to hole out from the fairway:

| tee | ball at (yds from tee, side) | to the hole | table | DP calibrated | DP raw | best club | on the green | penalty |
|---|---|---|---|---|---|---|---|---|
| Back | long iron (212, 8 R) | 64 | 2.966 | 3.000 | 2.881 | pitch 60 | 97 % | 2.0 % |
| Back | mid iron (184, line) | 88 | 3.055 | 3.090 | 2.864 | pitch 90 | 93 % | 1.2 % |
| Back | 8-iron (160, 3 L) | 111 | 3.141 | 3.238 | 3.012 | SW | 79 % | 2.0 % |
| Back | 4-wood (259, 22 R) | 42 | 2.840 | 2.884 | 2.730 | pitch 40 | 96 % | 2.7 % |
| Middle | long iron (211, 17 R) | 51 | 2.895 | 2.921 | 2.694 | pitch 50 | 98 % | 2.0 % |
| Middle | mid iron (183, 2 L) | 68 | 2.983 | 2.993 | 2.752 | pitch 70 | 98 % | 0.8 % |
| Middle | 8-iron (160, 1 L) | 91 | 3.068 | 3.133 | 2.934 | pitch 90 | 90 % | 0.8 % |
| Middle | 4-wood (254, 31 R) | 46 | 2.867 | 2.886 | 2.799 | pitch 50 | 98 % | 1.2 % |

The wedge that must cross trouble to a narrow green costs 0.01-0.04 from 42-88 yds, 0.07 from 91 and **0.10 from
111**: the further back he lays up on 10, the more the table flatters it. That is the opposite of a "favourite
number" effect.

### On the published map (`281442149`)

| tee | valuation | go | long iron | mid iron | 8-iron | go minus best lay-up |
|---|---|---|---|---|---|---|
| Back | engine table | 2-wood 20.5 L, 3.635 | 4.035 | 4.069 | 4.148 | -0.40 |
| Back | DP calibrated | 2-wood 20.5 L, 3.635 | 4.062 | 4.113 | 4.225 | -0.43 |
| Back | DP raw | 2-wood 21.5 L, 3.607 | 3.841 | 3.917 | 4.044 | -0.23 |
| Middle | engine table | 4-wood 17.5 L, 3.608 | 3.911 | 4.062 | 4.075 | -0.30 |
| Middle | DP calibrated | 4-wood 17.5 L, 3.606 | 3.929 | 4.087 | 4.124 | -0.32 |
| Middle | DP raw | 4-wood 17.5 L, 3.589 | 3.783 | 3.857 | 3.929 | -0.19 |
| Back, tall grass = lost ball | engine table | 2-wood 19.5 L, 3.645 | 4.036 | 4.070 | 4.148 | -0.39 |
| Back, tall grass = lost ball | DP calibrated | 2-wood 19.5 L, 3.644 | 4.063 | 4.113 | 4.226 | -0.42 |

Dropped balls are now 11.8 % of 2-woods (engine 3.91, DP 3.89). Same club, same aim, on both rule sets; the
published book has 2-wood 20 L by 0.042 (drop) and 18.5 L (lost ball).

## 4. Validation 3: par 5s 6, 13, 18 (Back)

PAR5.md is at Saturday's forecast (41-47 F, 3-5 mph); this is calm 45 F. On 18 that matters: PAR5.md's long iron
carried 207 with 3 mph behind against a 205 front edge, here 203.

### Tee club (strokes; Driver's edge over the 2-wood / the 4-wood)

| hole | engine table | DP calibrated | DP level-only | DP raw | PAR5.md: table / best second shot / always lay up |
|---|---|---|---|---|---|
| 6 | 5.033; +0.118 / +0.162 | 5.147; +0.100 / +0.138 | +0.096 / +0.180 | 4.684; +0.051 / +0.098 | +0.116 / +0.069 / +0.019 |
| 13 | 5.081; +0.120 / +0.144 | 5.211; +0.107 / +0.098 | +0.125 / +0.139 | 4.754; +0.068 / +0.067 | +0.118 / +0.105 / +0.018 |
| 18 | 4.925; +0.120 / +0.196 | 5.073; +0.143 / +0.226 | +0.074 / +0.161 | 4.667; +0.052 / +0.101 | +0.120 / +0.093 / +0.009 |

Driver on all three in every valuation, as in PAR5.md, HOLE13.md and VARIANCE.md section E. How big the edge is
depends on the valuation, as VARIANCE.md said it would: 0.10-0.14 where the table's value of distance is kept
(calibrated), 0.05-0.07 on the model's own (raw; VARIANCE.md's "go from 240" plan gave 0.07-0.10).

### From the Driver's spot (PAR5.md's spots), fairway

| hole | spot; to front / middle | table | DP calibrated: V | go | lay-up | go minus lay-up: calibrated / raw | PAR5.md |
|---|---|---|---|---|---|---|---|
| 6 | (291, 6 R); 227 / 240 | 3.92 | 4.06 | 4-wood at the middle: 29 % on the green, 3 % penalty | 5-iron, leaves 42 | -0.34 / -0.21 | 4-wood 3.58, 27 %, 2 %; lay-up mid iron leaves 56; -0.41 |
| 13 | (294, 1 R); 224 / 240 | 3.92 | 4.06 | 4-wood 1 deg left: 32 %, 8 % | 5-iron, leaves 44 | -0.30 / -0.18 | 4-wood 3.59, 31 %, 8 %; mid iron leaves 53; -0.35 |
| 18 | (299, 13 R); 205 / 219 | 3.76 | 4.01 | long iron 3 deg right: 36 %, 10 % | 7-iron, leaves 46 | -0.25 / -0.14 | long iron 3.47, 50 %, 7 %; 8-iron leaves 51; -0.44 |

* Raw go values: 3.56 (6), 3.57 (13), 3.60 (18) against PAR5.md's 3.58, 3.59, 3.47 (18: the wind and 2 F).
* PAR5.md's 0.35-0.45 put a go finishing on table values against a lay-up valued by the table at its leftover
  distance; it did not charge the go for being a model shot. Calibrated, both are at table level: **going is worth
  0.25-0.34**. Raw (the lay-up's wedge played 0.2 better than the table): 0.14-0.21.
* From the rough at the same spot (no 4-wood): 6 no go, long iron up short; 13 the long iron up short by 0.05; 18
  a toss-up (0.05). PAR5.md: 6 none, 13 by 0.11, 18 by 0.20.
* Every non-tee shot 50 % wider (`--spread 1.5`, calibration redone): go minus lay-up -0.20 (6), -0.22 (13), -0.11
  (18); PAR5.md -0.24, -0.25, -0.23. The Driver's edge over the 2-wood: 0.115, 0.120, 0.129.

### Go / lay-up crossover (fairway's middle every 10 yds; calibrated; going's edge over the best lay-up)

| yds to the middle | 6 | 13 | 18 |
|---|---|---|---|
| 200 | 5-iron, 0.52 | 5-iron, 0.44 | 5-iron, 0.46 |
| 210 | long iron, 0.44 | long iron, 0.40 | long iron, 0.41 |
| 220 | long iron, 0.36 | long iron, 0.28 | long iron, 0.23 |
| 230 | long iron, 0.28 | 4-wood, 0.25 | 4-wood, 0.25 |
| 240 | 4-wood, 0.34 | 4-wood, 0.29 | 4-wood, 0.24 |
| 250 | 4-wood, 0.33 | 4-wood, 0.18 | 4-wood, 0.11 |
| 260 | 4-wood, 0.32 | 4-wood, 0.11 | 4-wood, 0.06 |
| 270 | 4-wood, 0.28 | 4-wood, 0.12 | 4-wood, 0.09 |
| 280 | 4-wood, 0.24 | 4-wood, 0.13 | 4-wood, 0.12 |
| 290 on | nothing gets within 20 of the front: 4-wood as far as it goes | same | same |

* **There is no distance at which laying up beats a club that can get there**, on any of the three: the same
  conclusion as PAR5.md's menu. (Raw, the two are level within 0.02 at 260 on 18 and from the rough at 220-230.)
  PAR5.md's edges (Saturday): 13: 0.23 at 240, 0.18 at 250; 6: 0.21 at
  240, 0.31 at 250-260; 18: 0.19 at 240, 0.16 at 250, 0.07 at 260.
* Where going stops being worth much: 13 beyond 250, 18 beyond 240 (0.11 at 250, 0.06 at 260). 6 stays worth 0.24+
  out to 280 (the 4-wood runs up an open front).
* From the rough (long iron at most): a go exists out to 230 on all three; its edge is under 0.11 from 220 on 13
  and 18 and at 230 on 6 (PAR5.md: out to 220 / 210 / 220).
* **Best lay-up distance: still the closest one.** From 240 on 13 the lay-ups rank 5-iron leaving 44 (best), mid
  iron 54 (+0.07), 7-iron 66 (+0.12), 8-iron 79 (+0.17), 9-iron 92 (+0.23). The table's own difference between 44
  and 92 yds is 0.22. Nothing in the lay-up zones of 6, 13 or 18 punishes the 40-50 yd pitch, so the DP agrees with
  the table that closer is better there, and with the calibration it could not say otherwise on clean ground. Hole
  10 is where the answer is not "closest": the long iron to 64 beats the 4-wood to 42 by trouble, not by distance.
* **A wrinkle the DP exposes: 220-230 out.** On 18 the fairway value is 4.03 at 220 and 3.90 at 230; on 13 4.00 and
  3.91. He is between the long iron (213, cannot carry the front) and a full 4-wood (247, through the green into
  trouble). With an eased 4-wood in the bag (226 / 240, `--eased`) the kink goes (13: 3.98, 4.03, 4.09 at 220, 230,
  240) and nothing else moves: the Driver's edge over the 2-wood is 0.092 / 0.099 / 0.145 on 6 / 13 / 18.

## 5. Validation 4: all 13 Back tee-shot holes

Published book = the page's calm pick (128 prior draws, forecast temperature at the hole). Table and DP columns: the
same two-stage central-world solve at 45 F on the two value rasters, the same 16,000 swings. Margin = over the
runner-up club. Strokes are from the tee.

| hole | published book | table: pick, strokes | margin | DP calibrated: pick, strokes | margin | DP - table | margin change | DP raw: pick | margin | DP level-only: pick | margin |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 (376) | Driver 8.5 L, 0.051 | Driver 9.0 L, 4.151 | 0.053 | Driver 9.0 L, 4.153 | 0.054 | +0.002 | +0.001 | Driver 9.0 L | 0.060 | Driver 9.0 L | 0.063 |
| 2 (422) | Driver 9.5 R, 0.062 | Driver 9.5 R, 4.325 | 0.062 | Driver 9.0 R, 4.332 | 0.059 | +0.008 | -0.002 | Driver 9.0 R | 0.040 | Driver 9.0 R | 0.041 |
| 3 (630) | Driver 6.0 L, 0.061 | Driver 5.5 L, 5.619 | 0.058 | Driver 5.5 L, 5.623 | 0.065 | +0.005 | +0.007 | Driver 5.5 L | 0.046 | Driver 5.5 L | 0.039 |
| 5 (452) | Driver 4.5 R, 0.091 | Driver 3.5 R, 4.521 | 0.091 | Driver 3.5 R, 4.526 | 0.092 | +0.005 | +0.001 | Driver 4.5 R | 0.046 | Driver 4.5 R | 0.052 |
| 6 (530) | Driver 5.5 R, 0.114 | Driver 6.0 R, 5.033 | 0.118 | Driver 6.0 R, 5.147 | 0.100 | +0.114 | -0.018 | Driver 6.0 R | 0.051 | Driver 5.5 R | 0.096 |
| 8 (408) | Driver 44.5 L, 0.046 | Driver 45.5 L, 4.215 | 0.053 | Driver 45.5 L, 4.251 | 0.058 | +0.036 | +0.004 | Driver 48.5 L | 0.062 | Driver 46.0 L | 0.053 |
| 9 (390) | Driver 12.5 R, 0.024 | Driver 12.5 R, 4.275 | 0.026 | Driver 12.5 R, 4.272 | 0.022 | -0.004 | -0.004 | Driver 13.5 R | 0.029 | Driver 12.5 R | 0.025 |
| 10 (271) | 2-wood 20.0 L, 0.042 | 2-wood 20.5 L, 3.635 | 0.041 | 2-wood 20.5 L, 3.635 | 0.041 | +0.000 | +0.000 | 2-wood 21.5 L | 0.032 | 2-wood 20.0 L | 0.050 |
| 11 (416) | Driver 16.0 R, 0.024 | Driver 16.5 R, 4.373 | 0.029 | Driver 16.0 R, 4.364 | 0.018 | -0.009 | -0.011 | Driver 15.5 R | 0.001 | **4-wood 8.0 R** | 0.010 |
| 13 (533) | Driver 3.0 R, 0.102 | Driver 1.5 R, 5.081 | 0.120 | Driver 2.0 L, 5.211 | 0.098 | +0.129 | -0.022 | Driver 1.0 L | 0.067 | Driver 1.0 R | 0.125 |
| 15 (428) | Driver 13.5 R, 0.102 | Driver 14.5 R, 4.367 | 0.110 | Driver 14.5 R, 4.425 | 0.112 | +0.058 | +0.002 | Driver 15.0 R | 0.075 | Driver 15.0 R | 0.086 |
| 16 (354) | 4-wood 5.5 R, 0.086 | 4-wood 6.0 R, 4.163 | 0.097 | 4-wood 5.5 R, 4.210 | 0.100 | +0.047 | +0.003 | 4-wood 7.5 R | 0.035 | 4-wood 6.0 R | 0.072 |
| 18 (527) | Driver 13.0 R, 0.124 | Driver 13.0 R, 4.925 | 0.120 | Driver 14.5 R, 5.073 | 0.143 | +0.147 | +0.023 | Driver 14.0 R | 0.052 | Driver 15.5 R | 0.074 |

Runner-up: the 2-wood everywhere except 10 (4-wood), 11 (4-wood; Driver under level-only), 13 under the calibrated
and raw DP (4-wood) and 16 (2-wood). Paired SE of a margin 0.001-0.003.

**Picks that change: none under the calibrated DP, none under the raw DP, one under level-only (11, by 0.010).**

Every club, strokes behind the valuation's best (table / calibrated / raw):

| hole | Driver | 2-wood | 4-wood | long iron | mid iron | 8-iron |
|---|---|---|---|---|---|---|
| 1 | 0 / 0 / 0 | 0.053 / 0.054 / 0.060 | 0.073 / 0.072 / 0.083 | 0.249 / 0.244 / 0.204 | 0.409 / 0.412 / 0.298 | 0.580 / 0.598 / 0.416 |
| 2 | 0 / 0 / 0 | 0.062 / 0.059 / 0.040 | 0.094 / 0.091 / 0.054 | 0.348 / 0.344 / 0.188 | 0.561 / 0.564 / 0.425 | 0.763 / 0.777 / 0.484 |
| 3 | 0 / 0 / 0 | 0.058 / 0.065 / 0.046 | 0.074 / 0.095 / 0.054 | 0.304 / 0.308 / 0.252 | 0.494 / 0.551 / 0.532 | 0.577 / 0.642 / 0.678 |
| 5 | 0 / 0 / 0 | 0.091 / 0.092 / 0.046 | 0.138 / 0.140 / 0.069 | 0.455 / 0.466 / 0.253 | 0.653 / 0.686 / 0.483 | 0.874 / 0.887 / 0.697 |
| 6 | 0 / 0 / 0 | 0.118 / 0.100 / 0.051 | 0.162 / 0.138 / 0.098 | 0.410 / 0.479 / 0.340 | 0.517 / 0.558 / 0.434 | 0.639 / 0.659 / 0.524 |
| 8 | 0 / 0 / 0 | 0.053 / 0.058 / 0.062 | 0.098 / 0.108 / 0.103 | 0.342 / 0.378 / 0.274 | 0.610 / 0.636 / 0.453 | 0.770 / 0.803 / 0.681 |
| 9 | 0 / 0 / 0 | 0.026 / 0.022 / 0.029 | 0.042 / 0.034 / 0.036 | 0.209 / 0.174 / 0.107 | 0.391 / 0.347 / 0.192 | 0.575 / 0.580 / 0.452 |
| 10 | 0.208 / 0.207 / 0.206 | 0 / 0 / 0 | 0.041 / 0.041 / 0.032 | 0.400 / 0.427 / 0.233 | 0.435 / 0.478 / 0.310 | 0.513 / 0.591 / 0.437 |
| 11 | 0 / 0 / 0 | 0.032 / 0.025 / 0.015 | 0.029 / 0.018 / 0.001 | 0.280 / 0.261 / 0.119 | 0.470 / 0.466 / 0.337 | 0.652 / 0.654 / 0.344 |
| 13 | 0 / 0 / 0 | 0.120 / 0.107 / 0.068 | 0.144 / 0.098 / 0.067 | 0.362 / 0.260 / 0.163 | 0.485 / 0.423 / 0.312 | 0.602 / 0.609 / 0.462 |
| 15 | 0 / 0 / 0 | 0.110 / 0.112 / 0.075 | 0.185 / 0.189 / 0.120 | 0.427 / 0.415 / 0.277 | 0.612 / 0.605 / 0.322 | 0.791 / 0.809 / 0.541 |
| 16 | 0.254 / 0.256 / 0.093 | 0.097 / 0.100 / 0.035 | 0 / 0 / 0 | 0.119 / 0.165 / 0.178 | 0.252 / 0.340 / 0.298 | 0.409 / 0.530 / 0.412 |
| 18 | 0 / 0 / 0 | 0.120 / 0.143 / 0.052 | 0.196 / 0.226 / 0.101 | 0.429 / 0.274 / 0.161 | 0.580 / 0.438 / 0.307 | 0.695 / 0.612 / 0.494 |

Where the DP and the table differ (the table's pick at the table's aim, the same swings scored on both; and the DP
minus the table on the hole's own fairway by distance to the hole):

| hole | penalty balls | dry balls, DP - table (left third / middle / right third of the pattern) | penalty balls, DP - table | fairway, DP - table: 75-125 / 125-175 / 175-225 / 225-275 yds out |
|---|---|---|---|---|
| 1 | 3.0 % | +0.002 (+0.001 / +0.004 / +0.002) | +0.011 | +0.00 / -0.00 / +0.01 / +0.04 |
| 2 | 4.0 % | +0.008 (+0.006 / +0.011 / +0.008) | +0.020 | +0.01 / +0.01 / +0.00 / +0.02 |
| 3 | 2.5 % | +0.005 (+0.005 / +0.001 / +0.010) | +0.001 | +0.01 / +0.01 / +0.02 / +0.08 |
| 5 | 2.2 % | +0.005 (+0.002 / +0.007 / +0.006) | +0.018 | +0.01 / +0.01 / +0.01 / +0.02 |
| 6 | 3.0 % | +0.111 (+0.099 / +0.106 / +0.128) | +0.213 | +0.06 / +0.09 / +0.09 / +0.09 |
| 8 | 0.0 % | +0.036 (+0.035 / +0.034 / +0.039) | - | +0.03 / +0.05 / +0.09 / - |
| 9 | 2.8 % | -0.003 (-0.001 / +0.002 / -0.013) | -0.016 | +0.00 / -0.02 / -0.05 / +0.01 |
| 10 | 11.8 % | +0.002 (+0.002 / +0.000 / +0.007) | -0.015 | +0.06 / +0.09 / +0.08 / - |
| 11 | 5.8 % | -0.011 (-0.018 / -0.006 / -0.009) | +0.012 | +0.00 / -0.01 / -0.02 / +0.02 |
| 13 | 2.1 % | +0.132 (+0.101 / +0.154 / +0.134) | +0.100 | +0.04 / +0.09 / +0.15 / +0.18 |
| 15 | 1.3 % | +0.058 (+0.055 / +0.059 / +0.060) | +0.046 | +0.05 / +0.06 / +0.07 / +0.06 |
| 16 | 2.0 % | +0.046 (+0.055 / +0.032 / +0.066) | +0.119 | +0.05 / +0.11 / +0.19 / +0.24 |
| 18 | 0.7 % | +0.148 (+0.140 / +0.175 / +0.121) | +0.023 | +0.02 / +0.03 / +0.13 / +0.23 |

### Reading, hole by hole

| hole | what moved | which to believe |
|---|---|---|
| 1, 2, 3, 5, 9 | nothing: values within 0.01 of the table, margins within 0.007, aims within 0.5 yd | the same answer twice. On these holes the table is a fair value of the finishing spots |
| 10 | nothing at the tee: the go's balls finish on or by the green, where both use the same anchor. The lay-up clubs fall 0.03-0.08 further behind | DP for the lay-ups (it plays the wedge over the trouble); neither for the go: what separates go balls is inside 30 yds, which the DP does not model |
| 8 | +0.04 on the whole hole, Driver's margin 0.053 to 0.058, aim the same | DP, mildly: the approach is harder than a clean one from every distance, a little more so from further back |
| 15 | +0.06 on the whole hole, the same from every distance; margin and aim unchanged | DP for the level; the tee decision is untouched because the charge does not depend on where the tee ball finishes |
| 16 | +0.05; the approach costs +0.05 from 100, +0.11 from 150, +0.19 from 200 (the pond). 4-wood margin 0.097 to 0.100; the long iron goes from 0.12 to 0.17 behind, the mid iron from 0.25 to 0.34 | DP. This is MODEL.md section 3's finding (approach 0.2-0.3 harder than the table, clubs in the same order) with the size by distance. It strengthens the 4-wood against anything shorter |
| 11 | Driver over 4-wood 0.029 to 0.018; raw 0.001; level-only 4-wood by 0.010 | neither: MODEL.md section 1 called 11 a coin flip that turns on how much a yard is worth, and three valuations of a yard give three answers within 0.03. Either club |
| 6 | Driver's margin 0.118 to 0.100; the hole +0.11 | DP for the direction: the extra yards buy a go that is harder here than on clean ground. The size turns on the calibration (raw 0.05) |
| 13 | margin 0.120 to 0.098, the runner-up becomes the 4-wood, aim 3.5 yds left (2 L instead of 1.5 R) | DP for the margin's direction. The aim: the DP charges balls in the middle and right of the pattern 0.03-0.05 more than balls on the left (the go line is at the green's left edge, away from the channel), so it shades left; HOLE13.md shades right for the ditch, worth 0.004-0.019. The two are the same size and opposite: leave the page's aim |
| 18 | margin 0.120 to 0.143, aim 1.5 yds right | weakest of the DP's changes. It comes from 250-260 out being charged +0.25-0.31 (a full 4-wood at a green with water) against +0.05-0.26 at 220-240; level-only says 0.074 and raw 0.052. Believe "Driver"; do not believe that the margin grew |

In one line: where the DP differs from the table it is because of ground the table cannot see (16, 15, 8, the par-5
greens, 10's lay-up), and none of it is large enough at the tee to move a club.

## 6. Resolution checks and timings

| check (calibrated DP, then the tee solve): pick, strokes, margin | hole 10 | hole 13 | hole 16 |
|---|---|---|---|
| as run: 256 swings, 4-yd grid | 2-wood 20.5 L, 3.635, 0.041 | Driver 2.0 L, 5.211, 0.098 | 4-wood 5.5 R, 4.210, 0.100 |
| 1,024 swings | 2-wood 20.5 L, 3.635, 0.041 | Driver 2.0 L, 5.217, 0.094 | 4-wood 5.5 R, 4.214, 0.099 |
| 2-yd grid (4 x the states) | 2-wood 20.5 L, 3.635, 0.041 | Driver 1.5 L, 5.210, 0.098 | 4-wood 5.5 R, 4.211, 0.100 |

Any club's strokes move by at most 0.009 with four times the swings and 0.0014 with four times the states. The
4-yd grid is not a limit; 256 swings are good to about 0.005 on a margin.

**Timings** (`run.py timing`, 4 threads, the box shared with other jobs at a load of 2.7; calibration 1.7 s once
per process):

| hole | states | sweeps | paint the long raster, s | DP, s | engine tee solve on the DP's values (6 clubs, 16,000 swings), s |
|---|---|---|---|---|---|
| 1 | 5,933 | 3 | 2.0 | 7.0 | 3.2 |
| 2 | 6,984 | 2 | 3.1 | 6.3 | 3.2 |
| 3 | 10,252 | 2 | 3.5 | 8.3 | 3.2 |
| 5 | 7,731 | 2 | 2.2 | 5.8 | 3.1 |
| 6 | 8,697 | 3 | 3.4 | 13.4 | 3.0 |
| 8 | 6,810 | 2 | 2.3 | 4.6 | 2.9 |
| 9 | 6,424 | 2 | 2.8 | 5.2 | 3.2 |
| 10 | 4,877 | 2 | 2.8 | 4.3 | 3.3 |
| 11 | 8,066 | 2 | 2.5 | 7.5 | 3.4 |
| 13 | 9,705 | 3 | 4.0 | 11.3 | 3.1 |
| 15 | 7,053 | 2 | 2.4 | 6.9 | 3.3 |
| 16 | 6,438 | 3 | 2.8 | 10.3 | 3.4 |
| 18 | 9,216 | 3 | 3.3 | 11.9 | 3.1 |
| all 13 | | | 37 | **103** | 41 |

* The flat hole (9,984 states): 4.4 s raw, 6.6 s calibrated.
* The first C version took 13 s for hole 10 and 40 s for a par 5. Two changes brought it to these figures:
  only the cells that use a band's nodes are refreshed after the band (the refresh was a third of the time), and
  sweeps after the first re-search only the clubs that were within 0.15 of the best from each state.
* The hot loop was in C from the start (one swing = land, roll in 2-yd steps, look up the value, walk back on a
  penalty ball: about 45 ns). A numpy copy of the same loop is kept for the tests and the outcome shares; it was
  never fast enough to be the solver (about 3 x 10^8 swings a sweep).
* Under 60 s a hole was the target; every hole is under 15 s. On a busy box (load 10) the same solves took 20-40 s.


## 7. Known simplifications

1. **Inside 30 yds and on the green the value is the table's.** No pin, no short side, no slope, no "chip that has
   to carry the sand". A drop or a miss beside the green is priced by lie and distance to the middle. This is the
   largest thing the DP still does not see, and it is exactly where hole 10's go balls differ from each other.
2. **Every shot that is not a tee shot is assumed:** the deck clubs, the part swings (a 90-yd pitch with a 19-yd
   wide pattern), the rough and sand rules, full swings only for the long clubs. None is measured. The bag has no
   club between 213 and 247 yds at 45 F, which shows as a kink at 220-230 out (section 4); `--eased` removes it.
3. **No wind and no elevation on shots that are not tee shots;** one temperature. The tee shot keeps the engine's.
4. **Trees** are the engine's finish-lie premium on top of the DP's rough value: a punch-out is not played as a
   real shot, trees in the flight path are not priced, and the engine's "tree line in the way" charge is for the
   line to the green even where the DP plays away from it.
5. **Relief:** the drop is in the reference cell's own lie (no choice within two club-lengths, so never out of
   sand onto grass a yard away); back-on-the-line is the best of 17 distances; stroke and distance is not offered
   for a ball in a penalty area unless the walk back reaches the start.
6. **Ground beyond 65 yds of the tee line** is rough on the DP's raster; the engine's half-trees rule for it is kept
   in the tee-shot values. **OB off the tee** keeps the engine's 1 + tee-table value (hole 3, 0.3 % of Drivers).
7. **Central world only.** No prior draws and no map jitter; the published book averages 128. The comparison is
   central world against central world.
8. **One fixed set of 256 swings per club.** Deterministic, so states and directions are compared without noise;
   the discretisation is checked in section 6.
9. **The calibration's premise** (flat = table) and its side effect (the table's value of distance is imported):
   section 2.

## 8. Recommendation

**Is it ready to replace the table valuation in the engine? No. Use it as the second opinion now, and decide after
the tournament.**

Why not yet:

* The decision it would most plausibly change, how much the Driver's extra yards are worth on a par 5 and on 11,
  is the one it cannot answer on its own: 0.10-0.14 with the table's value of distance, 0.05-0.07 with the model's.
  Putting the calibrated DP on the page would look like new information on those holes and would mostly be the
  table again.
* Where it does add information (16, 15, 8, the par-5 greens, 10's lay-up), it changes levels by 0.04-0.15 and no
  club. The page loses nothing by waiting.
* Its inputs for the second shot are assumptions, and its picture stops 30 yds from the hole.

What it is good for today, as it stands: any "what about the next shot" question on any hole in 10-20 s, with the
drop rules, the lost-ball rule and the go / lay-up menu, in place of a one-off script. It agreed with all three of
today's scripts.

What it would take to put it into the engine:

1. **Settle what the DP is calibrated to.** Options, in order of preference: (a) Will's own or a 5-handicap's
   strokes-to-hole-out by distance and lie for approach shots (Arccos / Shot Scope style), which would replace both
   the table and c; (b) the course average (c shifted so the DP averages the table over the course's fairways
   rather than on a flat hole); (c) as now. Until then, run calibrated, level-only and raw together and treat a hole
   where they disagree on the club (today only 11) as a tie.
2. **Confirm the second-shot patterns** with Will: the 4-wood off the deck, whether he has an eased one, his wedge
   distances and how wide a 60-100 yd shot really is. The lay-up conclusions on 10 rest on the 90-yd pitch.
3. **Give the last 30 yds a model**, even a crude one: a pitch or chip whose error grows with its length, a pin
   position (or an average over front / middle / back), short side charged by what is between the ball and the
   pin. Without it the DP is blind to short-siding and to the difference between go balls on a drivable hole.
4. **Wire it as a correction, not as a new engine.** The DP's output is a smooth "DP minus table" field per lie
   class on a 4-yd grid (three small arrays a hole). Add it to `Raster.strokes` behind a per-course config option
   (as `green_putting` is), with penalty cells taking 1 + the DP's drop value. Then the engine, fastsolve's kernel,
   the prior draws, the wind grids and the page all run unchanged on the corrected value raster, at 10-20 s extra
   per hole and rule set. With the option off the engine must reproduce today's numbers bit for bit (a test).
5. **Decide how the correction moves with conditions.** It was solved at one temperature, calm, central world. Check
   how much it changes at 35 and 55 F, with 10 mph, and on jittered maps before reusing one field for all of them.
6. **Check it against scores.** After the weekend: the field's and Will's hole-by-hole scoring against V at the tee.
   If 13, 16 and 18 really play 0.05-0.15 harder than their table values and 1, 2, 5 and 9 do not, the DP has earned
   its place.

## 9. Reproduce

    S=<scratch>/snap_281442149      (git archive of the engine + Gateway inputs at 281442149: holesolve/README.md)
    export HOLESOLVE_SNAP=$S HOLESOLVE_STATE=281442149
    R="python3 course_data/courses/holesolve/run.py"
    $R flat
    $R tee --holes 9,10,11 --tag _9_10_11      (and 13,15 / 16,18 / 1,2 / 3,5 / 6,8)
    $R tee --holes 9,10,11 --vals dp_level --tag _level_9_10_11      (and the other holes)
    $R par5 --holes 13 --tag _h13      (6, 18; --eased --tag _h13_eased; --spread 1.5 --tag _h13_spread15)
    $R hole10 ; $R hole10 --which truth_middle ; $R hole10 --tall lost
    $R timing ; $R tee --holes 10,13,16 --vals dp --swings 1024 --tag _check_swings1024 ; ... --grid 2 --tag _check_grid2
    HOLESOLVE_SNAP=<scratch>/snap_ae810a91d HOLESOLVE_STATE=ae810a91d $R hole10 --tag _map_ae810a91d   (and truth_middle)
    python3 course_data/courses/holesolve/report.py tee ; python3 course_data/courses/holesolve/report.py flat
    python3 course_data/courses/holesolve/test_holesolve.py

Every run is under 2 minutes on 4 CPUs. Results: `course_data/courses/holesolve/results/*.json`, each with its
`state`.
