# HOLE 10: if he lays up, with what, and short of the fairway sand or over it?

Nov 13 2026. Golfer's questions: "what is the best lay-up on strokes gained? What would a 4-wood lay-up be, a mid
iron, a long iron? Should I carry the bunker? Should I go short of it with the mid iron?" Back (271) and Middle
(251), Saturday, Sunday and calm. Code: `opt/layup10.py` (`study`, `grid`), `opt/layup10_picture.py`. Results:
`opt/results/layup10_<set>.json`. No tee-shot number of the normal page changed.

## Answer

**Back tee (271).** The fairway sand is one patch, 194-200 yds out, 4-11 yds right of the tee line, with a collar of
rough round it (190-205).

| lay-up | finishes | leaves | what happens | strokes (Sat), table / next shot played out |
|---|---|---|---|---|
| **Long iron: carry it** | 211-212 out, 8 R | 65 | carries 202 cold, so a solid one pitches just past the sand: 86 % fairway, **10 % in the sand** (the 12 % of swings that come up 5-8 % short), 1 % lost | 4.05 / **3.86** |
| **Mid iron: stay short** | 183-184 out, on the tee line | 88 | carries 178, stops 10 short of the sand: 98 % fairway, nothing in the sand, nothing lost | 4.07 / 3.94 |
| 8-iron: well short | 160 out, 3 L | 111 | 99 % fairway | 4.15 / 4.06 |
| 4-wood: past everything | 258-260 out, 22 R | 45 | the fairway ends at 270-275 on that line (260 at 40 R, 247 on the tee line): 73 % fairway, 13 % rough, **13 % lost** (long-left over the channel, or right) | **4.02** / 3.95 |
| 2-wood / Driver to the right fairway | 266 / 276 out | 45-48 | 25 % / 35 % lost; the Driver runs through the end of the fairway half the time | 4.15 / 4.31 |

* **Carry it or stay short?** Carry it with the long iron if he is laying up: it is the best lay-up or level with
  the best in every case run (Saturday, Sunday, calm, firm ground) and the best by 0.08 when the wedge shot is
  played out. Staying short with the mid iron costs 0.03 on the engine's table on Saturday (0.07 on Sunday) and
  takes the sand and the lost ball out of it completely: a fair choice, not a mistake.
* **The 4-wood lay-up** is 0.03 better than the long iron on the table in the cold (35-45 F) because it leaves 45,
  but 1 ball in 8 is lost and with the wedge played out it drops to third. With firm ground (roll x1.25 / x1.5)
  it goes to 4.05 / 4.10 and the long iron (4.04 / 4.03) passes it; on Sunday's helping wind it is 0.09 worse than
  the long iron. Not the lay-up.
* **Sunday (49 F, 4 mph helping):** long iron 3.99 (carries 208, only 4 % in the sand), mid iron 4.06 (it now
  finishes at 190, right at the front of the sand: aim 4 yds left of the tee line, 2 % in it), 8-iron 4.13.
* **Against going at the green:** the best lay-up is 0.27-0.32 worse than the best go on the table (Sat 4.05
  against 3.75; Sun 3.99 against 3.67), 0.12-0.17 with the wedge played out. Laying up is the lower-variance play,
  not the lower score.

**Middle tee (251).** The same sand is 174-180 out, 6-12 right. The fairway ends at 245-254.

| lay-up | finishes | leaves | what happens | strokes (Sat), table / played out |
|---|---|---|---|---|
| **Long iron: carry it by 20** | 211 out, 17 R | 50 | 93 % fairway, 0 in the sand, 3-4 % lost (left, over the channel) | **3.95 / 3.83** |
| Mid iron | 183 out, 2 L | 69 | **lands at the sand: 9 % in it**, 81 % fairway | 4.07 / 3.88 |
| 8-iron: short of it | 160 out, 1 L | 92 | 99 % fairway | 4.08 / 3.95 |
| 4-wood | 254 out, 31 R | 49 | runs out of fairway: 17 % fairway, 62 % rough, 21 % lost | 4.19 / 4.07 |

From Middle the long iron is the lay-up by 0.12 on the table; the mid iron is the wrong club (its number is the
sand's); to stay short it is the 8-iron, 0.13 behind the long iron.

## What a lay-up is here (the aim window)

A lay-up = an aim whose finishing line (aim + wind drift, yds right of the tee line) is inside the window:
**irons 5 left to 45 right; woods 5 right to 45 right.** From the map: the green is 9-29 yds left of the tee line at
249-290 yds from the Back tee, the channel beside it at 5-15 left, the right fairway runs from 28 left (150 out) to
40 right (270 out), tall growth starts at 45-50 right. The irons cannot reach the green, so their window only has
to keep them right of the channel; the woods' window starts at 5 right so that a "lay-up" is never a ball meant to
spill onto the green (their strokes curve has a second, separate low point at 20-22 right: that is the lay-up).
The Driver from Middle (and both long woods in the page grid at some cells) sit on the window's left edge: there is
no real lay-up line for them, and the page table leaves them out.

## Sand and fairway, measured on the map (yds from each tee; map checked on the 2023 photo, pictures below)

| | Back tee | Middle tee |
|---|---|---|
| fairway sand (the only patch in the right fairway) | 194-200 out, 4-11 R | 174-180 out, 6-12 R |
| its rough collar | 190-205 | 170-185 |
| right fairway ends, on the tee line / 10 R / 20 R / 30 R / 40 R | 247 / 270 / 275 / 274 / 260 | 219 / 245 / 254 / (path side) / 248 |
| beyond the end | 10-15 yds of rough, the cart path, then tall growth; the channel on the left from 230 on | same |
| red team's figures (HOLE10_REDTEAM.md) | "sand around 198": yes. Long iron 3-10 R leaves 64-67 with 9 % in it: **confirmed** (8.5 R, 65, 9-10 %). Mid iron 0-4 L leaves 88, 97 % fairway: **confirmed** (1 L, 88, 98 %). 8-iron leaves about 110: **confirmed** (111) | |

## Explicit pricing of the next shot

Engine table = strokes from the lie and the distance left. "Played out" = from where each lay-up ball finishes
(30+ yds from the middle of the green), the next shot is simulated on the map with the par-5 solver's machinery
(`par5_second.play`: club x direction, penalty at the crossing point, putts on the green), with part swings every
10 yds from 30 to 100 (ASSUMED: width and depth in proportion to a full sand wedge's 22 / 12 yds, floors 10 / 8).

* It lowers every lay-up by 0.08-0.19 (a pitch with this pattern does better than the table's value for that
  distance) and the go clubs by 0.01, so the gap to going shrinks to 0.12-0.17. The red team's cruder version went
  the other way (lay-up 0.16 worse): the level of this number depends on how good the 50-90 yd shot is taken to be
  and should not be read as "laying up is nearly as good". The engine-table figure is the one on the page.
* **It does change the ranking among lay-ups:** the long iron becomes clearly best (by 0.08 Back, 0.05 Middle),
  the 4-wood falls from first to third on Back. That is why the page stars the long iron whenever it is within
  0.04 of the table's best lay-up.

## Tables

### Back (271), calm, 45 F

| club | aim (finishing line) | carry / total | finishes (yds out, side) | leaves | fairway / rough / fairway sand / lost | strokes | vs best lay-up | vs going | next shot played out | vs best lay-up | vs going |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 4-wood | 22 R (22 R) | 247 / 262 | 259, 23 R | 44 | 70 / 14 / 0 / 14 % | 4.03 | +0.00 | +0.28 | 3.95 | +0.09 | +0.21 |
| Long iron | 8 R (8 R) | 203 / 213 | 211, 9 R | 65 | 87 / 3 / 8 / 0 % | 4.04 | +0.01 | +0.29 | 3.86 | +0.00 | +0.12 |
| Mid iron | 1 L (1 L) | 179 / 185 | 184, 1 L | 88 | 97 / 1 / 0 / 0 % | 4.07 | +0.04 | +0.32 | 3.93 | +0.08 | +0.20 |
| 8-iron | 4 L (4 L) | 157 / 161 | 160, 4 L | 110 | 99 / 0 / 0 / 0 % | 4.15 | +0.12 | +0.40 | 4.06 | +0.20 | +0.32 |
| 2-wood | 22 R (22 R) | 256 / 272 | 267, 23 R | 45 | 38 / 33 / 0 / 25 % | 4.17 | +0.14 | +0.42 | 4.08 | +0.22 | +0.35 |
| Driver | 21 R (21 R) | 266 / 292 | 276, 22 R | 47 | 4 / 57 / 0 / 35 % | 4.32 | +0.29 | +0.57 | 4.21 | +0.35 | +0.48 |
| GO: 2-wood | 26 L (26 L) | 256 / 272 | 267, 28 L | 18 | 18 / 28 / 0 / 18 % | 3.75 |  | +0.00 | 3.73 |  | +0.00 |
| GO: 4-wood | 28 L (28 L) | 247 / 262 | 254, 29 L | 22 | 31 / 19 / 0 / 14 % | 3.75 |  | +0.01 | 3.74 |  | +0.00 |
| GO: Driver | 28 L (28 L) | 266 / 292 | 279, 30 L | 21 | 2 / 57 / 0 / 22 % | 3.98 |  | +0.23 | 3.96 |  | +0.23 |

### Back (271), Saturday (44 F, 5 mph from the left and a touch against)

| club | aim (finishing line) | carry / total | finishes (yds out, side) | leaves | fairway / rough / fairway sand / lost | strokes | vs best lay-up | vs going | next shot played out | vs best lay-up | vs going |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 4-wood | 30 R (21 R) | 245 / 261 | 258, 23 R | 44 | 72 / 13 / 0 / 13 % | 4.02 | +0.00 | +0.27 | 3.95 | +0.09 | +0.21 |
| Long iron | 14 R (8 R) | 202 / 212 | 210, 8 R | 66 | 85 / 3 / 10 / 0 % | 4.05 | +0.03 | +0.30 | 3.86 | +0.00 | +0.12 |
| Mid iron | 6 R (1 L) | 178 / 184 | 183, 1 L | 89 | 98 / 1 / 0 / 0 % | 4.07 | +0.05 | +0.32 | 3.94 | +0.08 | +0.20 |
| 8-iron | 3 R (3 L) | 156 / 160 | 159, 3 L | 112 | 99 / 0 / 0 / 0 % | 4.15 | +0.13 | +0.40 | 4.06 | +0.20 | +0.32 |
| 2-wood | 29 R (21 R) | 255 / 271 | 266, 22 R | 45 | 43 / 29 / 0 / 24 % | 4.15 | +0.13 | +0.40 | 4.08 | +0.22 | +0.34 |
| Driver | 28 R (21 R) | 265 / 291 | 275, 22 R | 47 | 5 / 56 / 0 / 35 % | 4.31 | +0.29 | +0.56 | 4.21 | +0.35 | +0.48 |
| GO: 2-wood | 18 L (26 L) | 255 / 271 | 265, 28 L | 18 | 20 / 26 / 0 / 18 % | 3.75 |  | +0.00 | 3.74 |  | +0.00 |
| GO: 4-wood | 20 L (28 L) | 245 / 261 | 253, 29 L | 23 | 34 / 18 / 0 / 14 % | 3.78 |  | +0.03 | 3.76 |  | +0.02 |
| GO: Driver | 21 L (28 L) | 265 / 291 | 278, 30 L | 21 | 2 / 56 / 0 / 22 % | 3.96 |  | +0.21 | 3.95 |  | +0.22 |

### Back (271), Sunday (49 F, 4 mph helping from the right)

| club | aim (finishing line) | carry / total | finishes (yds out, side) | leaves | fairway / rough / fairway sand / lost | strokes | vs best lay-up | vs going | next shot played out | vs best lay-up | vs going |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Long iron | 6 R (10 R) | 208 / 219 | 218, 10 R | 60 | 90 / 3 / 4 / 0 % | 3.99 | +0.00 | +0.32 | 3.83 | +0.00 | +0.17 |
| Mid iron | 6 L (4 L) | 184 / 191 | 189, 4 L | 82 | 93 / 3 / 2 / 0 % | 4.06 | +0.07 | +0.39 | 3.89 | +0.06 | +0.23 |
| 4-wood | 20 R (24 R) | 252 / 270 | 266, 25 R | 46 | 51 / 31 / 0 / 16 % | 4.08 | +0.09 | +0.41 | 3.99 | +0.16 | +0.33 |
| 8-iron | 6 L (4 L) | 162 / 167 | 166, 4 L | 105 | 99 / 0 / 0 / 0 % | 4.13 | +0.13 | +0.45 | 4.01 | +0.18 | +0.35 |
| 2-wood | 19 R (23 R) | 262 / 279 | 272, 24 R | 47 | 21 / 48 / 0 / 27 % | 4.22 | +0.23 | +0.55 | 4.12 | +0.29 | +0.46 |
| Driver | 18 R (22 R) | 271 / 299 | 279, 23 R | 48 | 1 / 59 / 0 / 36 % | 4.35 | +0.36 | +0.67 | 4.24 | +0.41 | +0.58 |
| GO: 4-wood | 30 L (26 L) | 252 / 270 | 265, 28 L | 18 | 21 / 23 / 0 / 14 % | 3.67 |  | +0.00 | 3.66 |  | +0.00 |
| GO: 2-wood | 30 L (26 L) | 262 / 279 | 273, 28 L | 18 | 10 / 38 / 0 / 18 % | 3.77 |  | +0.10 | 3.76 |  | +0.10 |
| GO: Driver | 31 L (28 L) | 271 / 299 | 283, 29 L | 22 | 0 / 61 / 0 / 25 % | 4.04 |  | +0.37 | 4.03 |  | +0.37 |

### Back: firm ground (engine table; lay-up strokes, best go in the last column)

| case | 4-wood | Long iron | Mid iron | 8-iron | best go |
|---|---|---|---|---|---|
| Saturday (44 F, 5 mph from the left and a touch against) | 4.02 (13 % lost, 0 % sand) | 4.05 (0 % lost, 10 % sand) | 4.07 (0 % lost, 0 % sand) | 4.15 (0 % lost, 0 % sand) | 2-wood 3.75 |
| Saturday, roll x1.25 | 4.05 (15 % lost, 0 % sand) | 4.04 (0 % lost, 10 % sand) | 4.07 (0 % lost, 0 % sand) | 4.15 (0 % lost, 0 % sand) | 4-wood 3.77 |
| Saturday, roll x1.5 | 4.10 (17 % lost, 0 % sand) | 4.03 (0 % lost, 10 % sand) | 4.07 (0 % lost, 1 % sand) | 4.14 (0 % lost, 0 % sand) | 4-wood 3.78 |
| Sunday (49 F, 4 mph helping from the right) | 4.08 (16 % lost, 0 % sand) | 3.99 (0 % lost, 4 % sand) | 4.06 (0 % lost, 2 % sand) | 4.13 (0 % lost, 0 % sand) | 4-wood 3.67 |
| Sunday, roll x1.25 | 4.13 (18 % lost, 0 % sand) | 3.98 (1 % lost, 4 % sand) | 4.06 (0 % lost, 2 % sand) | 4.12 (0 % lost, 0 % sand) | 4-wood 3.70 |

### Middle (251), calm, 45 F

| club | aim (finishing line) | carry / total | finishes (yds out, side) | leaves | fairway / rough / fairway sand / lost | strokes | vs best lay-up | vs going | next shot played out | vs best lay-up | vs going |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Long iron | 16 R (16 R) | 203 / 214 | 212, 17 R | 51 | 92 / 3 / 0 / 3 % | 3.95 | +0.00 | +0.26 | 3.83 | +0.00 | +0.14 |
| Mid iron | 2 L (2 L) | 178 / 185 | 183, 2 L | 68 | 81 / 8 / 9 / 1 % | 4.07 | +0.12 | +0.38 | 3.87 | +0.05 | +0.19 |
| 8-iron | 1 L (1 L) | 156 / 161 | 160, 1 L | 91 | 99 / 0 / 0 / 0 % | 4.07 | +0.13 | +0.39 | 3.95 | +0.12 | +0.26 |
| 4-wood | 30 R (30 R) | 246 / 262 | 254, 31 R | 49 | 14 / 63 / 0 / 20 % | 4.19 | +0.25 | +0.50 | 4.07 | +0.24 | +0.38 |
| 2-wood | 5 R (5 R) at the window edge | 256 / 271 | 259, 5 R | 26 | 3 / 36 / 0 / 51 % | 4.32 | +0.37 | +0.63 | 4.28 | +0.46 | +0.60 |
| Driver | 5 R (5 R) at the window edge | 266 / 291 | 270, 5 R | 36 | 1 / 37 / 0 / 60 % | 4.48 | +0.53 | +0.79 | 4.44 | +0.62 | +0.76 |
| GO: 4-wood | 23 L (23 L) | 246 / 262 | 256, 24 L | 17 | 8 / 43 / 0 / 14 % | 3.69 |  | +0.00 | 3.68 |  | +0.00 |
| GO: 2-wood | 24 L (24 L) | 256 / 271 | 262, 24 L | 20 | 3 / 55 / 0 / 22 % | 3.93 |  | +0.24 | 3.92 |  | +0.24 |
| GO: Driver | 24 L (24 L) | 266 / 291 | 272, 24 L | 25 | 0 / 45 / 0 / 45 % | 4.30 |  | +0.61 | 4.28 |  | +0.60 |

### Middle (251), Saturday (44 F, 5 mph from the left and a touch against)

| club | aim (finishing line) | carry / total | finishes (yds out, side) | leaves | fairway / rough / fairway sand / lost | strokes | vs best lay-up | vs going | next shot played out | vs best lay-up | vs going |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Long iron | 23 R (16 R) | 202 / 213 | 211, 17 R | 51 | 92 / 3 / 0 / 3 % | 3.95 | +0.00 | +0.27 | 3.83 | +0.00 | +0.16 |
| Mid iron | 4 R (2 L) | 178 / 184 | 182, 2 L | 69 | 81 / 8 / 9 / 1 % | 4.07 | +0.12 | +0.39 | 3.88 | +0.05 | +0.21 |
| 8-iron | 6 R (1 L) | 155 / 160 | 159, 1 L | 92 | 99 / 0 / 0 / 0 % | 4.08 | +0.13 | +0.40 | 3.95 | +0.12 | +0.28 |
| 4-wood | 38 R (30 R) | 245 / 260 | 253, 31 R | 48 | 17 / 61 / 0 / 20 % | 4.19 | +0.24 | +0.51 | 4.07 | +0.24 | +0.40 |
| 2-wood | 34 R (26 R) | 255 / 270 | 258, 27 R | 47 | 4 / 59 / 0 / 33 % | 4.31 | +0.36 | +0.63 | 4.20 | +0.37 | +0.53 |
| Driver | 12 R (5 R) at the window edge | 265 / 290 | 269, 5 R | 36 | 1 / 38 / 0 / 58 % | 4.46 | +0.52 | +0.79 | 4.43 | +0.60 | +0.76 |
| GO: 4-wood | 15 L (23 L) | 245 / 260 | 255, 24 L | 17 | 9 / 41 / 0 / 13 % | 3.68 |  | +0.00 | 3.67 |  | +0.00 |
| GO: 2-wood | 15 L (23 L) | 255 / 270 | 261, 24 L | 20 | 4 / 54 / 0 / 21 % | 3.91 |  | +0.23 | 3.90 |  | +0.23 |
| GO: Driver | 17 L (24 L) | 265 / 290 | 272, 25 L | 25 | 0 / 47 / 0 / 42 % | 4.27 |  | +0.59 | 4.26 |  | +0.59 |

### Middle (251), Sunday (49 F, 4 mph helping from the right)

| club | aim (finishing line) | carry / total | finishes (yds out, side) | leaves | fairway / rough / fairway sand / lost | strokes | vs best lay-up | vs going | next shot played out | vs best lay-up | vs going |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Long iron | 16 R (19 R) | 208 / 220 | 218, 20 R | 48 | 91 / 3 / 0 / 4 % | 3.93 | +0.00 | +0.15 | 3.83 | +0.00 | +0.05 |
| Mid iron | 4 R (6 R) | 183 / 191 | 190, 7 R | 64 | 87 / 2 / 9 / 0 % | 4.03 | +0.10 | +0.25 | 3.84 | +0.01 | +0.06 |
| 8-iron | 5 L (2 L) | 161 / 167 | 166, 2 L | 85 | 97 / 1 / 0 / 0 % | 4.06 | +0.12 | +0.27 | 3.90 | +0.07 | +0.13 |
| 4-wood | 26 R (30 R) | 252 / 269 | 257, 31 R | 49 | 6 / 70 / 0 / 23 % | 4.23 | +0.30 | +0.45 | 4.09 | +0.26 | +0.32 |
| 2-wood | 20 R (24 R) | 262 / 278 | 264, 25 R | 47 | 1 / 55 / 0 / 41 % | 4.39 | +0.45 | +0.60 | 4.28 | +0.45 | +0.51 |
| Driver | 2 R (5 R) at the window edge | 271 / 298 | 274, 5 R | 40 | 1 / 28 / 0 / 70 % | 4.59 | +0.66 | +0.81 | 4.56 | +0.73 | +0.78 |
| GO: 4-wood | 28 L (24 L) | 252 / 269 | 261, 25 L | 19 | 4 / 59 / 0 / 13 % | 3.78 |  | +0.00 | 3.78 |  | +0.00 |
| GO: 2-wood | 28 L (24 L) | 262 / 278 | 267, 24 L | 22 | 1 / 57 / 0 / 27 % | 4.06 |  | +0.27 | 4.05 |  | +0.27 |
| GO: Driver | 29 L (26 L) | 271 / 298 | 275, 26 L | 26 | 0 / 31 / 0 / 59 % | 4.46 |  | +0.67 | 4.44 |  | +0.67 |

### Middle: firm ground (engine table; lay-up strokes, best go in the last column)

| case | 4-wood | Long iron | Mid iron | 8-iron | best go |
|---|---|---|---|---|---|
| Saturday (44 F, 5 mph from the left and a touch against) | 4.19 (20 % lost, 0 % sand) | 3.95 (3 % lost, 0 % sand) | 4.07 (1 % lost, 9 % sand) | 4.08 (0 % lost, 0 % sand) | 4-wood 3.68 |
| Saturday, roll x1.25 | 4.21 (21 % lost, 0 % sand) | 3.95 (3 % lost, 0 % sand) | 4.07 (1 % lost, 9 % sand) | 4.07 (0 % lost, 0 % sand) | 4-wood 3.74 |
| Saturday, roll x1.5 | 4.23 (22 % lost, 0 % sand) | 3.94 (4 % lost, 0 % sand) | 4.07 (1 % lost, 10 % sand) | 4.07 (0 % lost, 0 % sand) | 4-wood 3.80 |
| Sunday (49 F, 4 mph helping from the right) | 4.23 (23 % lost, 0 % sand) | 3.93 (4 % lost, 0 % sand) | 4.03 (0 % lost, 9 % sand) | 4.06 (0 % lost, 0 % sand) | 4-wood 3.78 |
| Sunday, roll x1.25 | 4.25 (23 % lost, 0 % sand) | 3.93 (4 % lost, 0 % sand) | 4.02 (0 % lost, 9 % sand) | 4.06 (0 % lost, 0 % sand) | 4-wood 3.85 |
(Aim: yds left / right of the tee line, in brackets the finishing line with the wind. "vs going": against the best
go club of that case. GO rows are the woods at their unrestricted best aim, for reference.)

## Pictures looked at

* `second_pass/img_h10/h10_layup_Back.jpg`, `h10_layup_Middle.jpg`: the 2023 photo with the map's zones and the
  window, then 3,000 Saturday swings of the 8-iron, mid iron, long iron, 4-wood and 2-wood at their lay-up aims
  (white fairway, orange rough, yellow sand, red lost). Back: the mid iron's cloud sits short of the sand, the long
  iron's sits on and beyond it, the 4-wood's fills the top of the fairway with a red fringe left and long. Middle:
  the mid iron's cloud is centred on the sand; the long iron's is clear beyond it; the 2-wood has no lay-up (its
  balls are at the green).
* `second_pass/img_h10/lay_Back_d0.jpg`, `lay_Middle_d0.jpg`: the page in Lay up mode.

## The page

Hole 10, Back and Middle, "Lay up" on: the table becomes a lay-up table (4-wood, long iron, mid iron, 8-iron, each
at its best lay-up aim for the wind, temperature and tee: carry / total / leaves / width / strokes against the best
lay-up), the best one starred and drawn; tapping a row shows that club's lay-up line and oval; one pill gives the
cost against going at the green, one answers carry-or-short. Data: `layup10.json` (config `layup_grid`; 172 KB;
the wind grid's 183 cells x 3 temperatures per tee, 8,192 common swings; `opt/layup10.py grid`, 20 min). Off =
the same page as before (panel HTML compared before / after on Back and Middle, Sat and Sun).

## Crude / not done

* The page's lay-up strokes are the engine table's; the played-out pricing is in this file only.
* Roll x1.25 / x1.5 only on the table. Part-swing dispersion is assumed.
* The Tips / Champions have no Lay up mode (their pick is already the fairway shot).
