# Gateway National, hole 10: where the drop is (Nov 13 2026, after Will played it)

Will's question: "are you simulating where the drops would be? Say you hit the left native grass and you cross over
the bunker - you're dropping in the bunker ... I either need to go for it or hit 8-iron ... if it's 0.3 that's
obviously enough that you have to go for it, but make sure we're accounting for the right things."

Read-only study. Nothing in the map, config, engine, solved outputs or page was changed. Scripts and pictures in the
scratch folder `h10drops/` (`drops.py` the drop model, `trace.py` the traced balls, `run.py` the tables;
`trace_b.jpg`, `trace_a.jpg`). Central world, 16,000 swings a club, aims every 0.5 yd; Monte Carlo noise on a margin
about 0.01. Calm 43.6 F; Saturday 44 F, 5 mph from the right; Sunday 49 F, 4 mph helping from the left.
Frame: yds from the Back tee, minus = left of the tee line. Green centre (270, -18.5).

## Answers

1. **Are sand drops a material cost? No.** In the rules-correct drop model 0.0-0.1 % of tee balls end up dropping in
   sand (ball flies straight from the tee: the tall grass on the left is entered from the front, short of the left
   greenside sand, not over it). If instead EVERY ball that finishes in the tall grass beside or behind the green is
   made to drop in the nearest greenside sand, that is 0.8-3.5 % of tee balls, and with sand shots priced 0.2 worse
   and two more hostile assumptions on top the go costs 0.02-0.06 more. The go's lead over the 8-iron stays 0.34 or
   more from the Back tee.
2. **Is the 0.3 real?** Yes, and against his real alternative it is bigger. 0.3 was the lead over the long iron (the
   best lay-up on paper). Over the **8-iron** the go leads by **0.41-0.47 (Back, published map), 0.51-0.54 (Back,
   band mown), 0.25-0.40 (Middle, published map), 0.32-0.48 (Middle, band mown)**. The drop model moves these by
   +0.00 to +0.02 (it is slightly kinder than the engine, below); sand +0.2 by -0.01; the hostile case by -0.02 to
   -0.06. Lowest figure anywhere: Middle tee, Sunday, published map, hostile: 0.22.
3. **Aim if he goes:** unchanged by the drop pricing (the pick within 1 yd in every case; the hostile sand case too).
   Back: 2-wood at the left half of the green, 25.5 L calm / 17 L Saturday on the published map; 22.5 L / 12 L if
   the band is mown. Sunday: 4-wood, 29 L (25 L band mown). Middle: 4-wood both days.
4. **Go or 8-iron: go.** Back tee, Saturday: 3.73 against 4.15. Break-even: every dropped ball would have to cost
   about 2.2 strokes MORE than priced (19 % of balls are dropped on the published map), or about half of all tee
   balls would have to be dropped. Honest uncertainty: the level depends on his real sideways spread with the woods
   (red team: woods 1.5 times wider than modelled takes about 0.18 off) and on how the 40-yd pitch back to the
   green goes; neither gets near 0.4.
5. **What the engine did and did not count.** It does simulate the drop point: one stroke, then a shot from the point
   where the ball's straight line from the tee last entered the dead ground. It prices that shot as ROUGH at that
   distance whatever is there (it never drops in sand, never credits fairway), and it does not look at what the
   pitch must carry. Both errors are small here and mostly cancel (section 2).

Page line for 10 (no banned words): **"Go at the green, left half. A ball that has to be dropped is already
counted, sand drops included: going still beats the 8-iron by about 0.4."**

## 1. How the engine prices a dropped ball on 10 today

Every dead area on 10 (the two on the right, the short-left one, the tall grass left and behind) is one class. A
ball that lands in it, or rolls into it, stops there. The value given to it is `1 + rough(d)`, d = distance to the
hole from the first dry cell found walking BACK from the ball along the straight tee-to-ball line (1-yd steps, up to
120 yds). The ball flies straight in the model, so that line is its flight line and the point is where it last
crossed the edge. The lie at the drop is always rough; the short-game table is not applied (inside 20 yds the value
is the 20-yd rough value, 2.75).

Table values near the green (strokes to hole out; the engine's amateur table with the short-game correction):

| yds from the hole | 10 | 15 | 20 | 30 | 40 | 60 | 90 | 110 |
|---|---|---|---|---|---|---|---|---|
| short grass | 2.39 | 2.49 | 2.60 | 2.72 | 2.83 | 2.95 | 3.06 | 3.14 |
| rough | 2.51 | 2.63 | 2.75 | 2.85 | 2.96 | 3.11 | 3.22 | 3.31 |
| sand | 2.66 | 2.70 | 2.75 | 2.91 | 3.07 | 3.45 | 3.57 | 3.57 |

Sand is 0.15 worse than rough at 10 yds, the same at 20, 0.06 worse at 30, 0.11 at 40. If his 30-yd sand shot is
worse than that, it is the "+0.2" row below.

Where the page pick's dropped balls are (Back, calm, 26 L, published map; 20,000 swings):

| where the ball finished | 2-wood | 4-wood | engine: drop distance, value after the tee shot | drop model: distance, lie, value |
|---|---|---|---|---|
| right of the green (channel and band) | 13.9 % | 12.1 % | 35-37 yds, rough, 3.91-3.94 | 36-40 yds, short grass 87-93 %, 3.80-3.84; every one pitches back across |
| tall grass on the left | 3.7 % | 2.9 % | 50-53 yds (many 100: see ball 1), rough, 4.01-4.03 | 60 yds, rough / short grass, 3.97-4.01 |
| short-left, level with the water | 1.2 % | 1.3 % | 96-101 yds, rough, 4.27-4.29 | 99-103 yds, 4.29-4.31 |
| all | 18.9 % | 16.3 % | 3.95 | 3.86 |

Band mown (map a): right side 6.4 % / 6.0 % at 29-32 yds (3.85-3.88, drop model 3.84-3.87: half go back on the line
to the right fairway and pitch from 36-40); the rest as above. A dry ball averages 2.46.

Traced balls (`trace_b.jpg`: left the 2023 photo with the map's edges, right the engine map; x = ball, circle = the
engine's pricing point, star = the drop in the rules model):

| # | club | finishes | engine's point, value | what is really at that point (map and photo) | rules model |
|---|---|---|---|---|---|
| 1, 3 | 2-wood | (253, -69) tall grass, far left | (171, -46), **102 yds out**, rough, 4.27 | the line from the tee runs over the water and stays in dead ground all the way: the map joins the water and the tall grass, so the last crossing is the water's front edge. Mown rough there | same point, 4.27 |
| 9 | 4-wood | (252, -65) | (173, -45), 101 yds, 4.33 | same | same, 4.27 |
| 10 | 4-wood | (233, -60) left, short of the left sand | (229, -59), 58 yds, 4.27 | rough bank above the water; photo: mown, 30 yds short of the nearest left sand | back on the line to (208, -81), 88 yds, short grass, 4.06 |
| 2, 8 | 2-wood, 4-wood | (238-243, -13) start of the channel by the footbridge | (232-236, -12), 35-39 yds, 3.91-3.95 | rough between the water's corner and the channel, 2-3 yds wide; the pitch crosses the channel | (235, -15) rough 36 yds 3.85, or back to (216, -10) 55 yds 3.94 |
| 12, 13 | 4-wood | (238-241, -10) channel | (237, -10), 34 yds, 3.90 | same strip | (235, -11) rough, 36 yds, 3.90 |
| 6 | 2-wood | (241, -13) channel | (232, -12), 39 yds, 3.95 | same | back on the line (216, -10), 55 yds, 3.94 |
| 7 | 2-wood | (258, -5) band, level with the front of the green | (236, -5), 37 yds, 3.93 | the band's near end: photo shows mown ground, right fairway edge 1-2 yds right | (235, -4) short grass, 38 yds, 3.83; pitch crosses the channel |
| 14 | 4-wood | (249, -9) | (227, -8), 44 yds, 4.00 | same, on the fairway's left edge | (227, -6) short grass, 45 yds, 3.87 |
| 5 | 2-wood | (254, +1) band's right edge (rolled in from the fairway) | (253, +1), 26 yds, 3.82 | right fairway edge | (251, +1) short grass, 28 yds, 3.67; pitch crosses band and channel |

Looked at on the photo: no traced ball's reference point is in sand. With the band mown (`trace_a.jpg`) balls 5-7
are in the channel itself at (242-263, -5..-11); the engine's point is on the right bank 2-10 yds back (24-30 yds
out) and the rules model either drops there or goes back on the line to the right fairway at 235-246 (36-40 yds).

What the picture shows that the map does not: the map has a 3-5 yd collar of rough between the left greenside sand
(272-284 and 289-296 out, 38-52 left) and the tall grass; on the photo the tall grass comes up to the sand's outer
lip. A ball that really crosses there (a hook still moving left, which the straight-flight model does not have)
would have only sand inside two club-lengths: Will's case. That is what the hostile row forces for every such ball.

## 2. The rules model (red-staked area, Rule 17.1d)

Per dead cell: reference point = last crossing of the edge on the ball's own line (0.5-yd steps). Options, best one
taken: (a) lateral, any dry cell within 2.5 yds (two club-lengths) not nearer the hole, grass or sand, on the green
allowed; if only sand is there he is in sand; (b) back on the line from the hole through the point, up to 100 yds;
(c) re-tee, 1 + 3.85. Drop valued with the lie that is there (table above) plus the red team's explicit next-shot
surcharge at that spot (what the pitch must carry: its `S2 - S`, 0.00-0.10). Dry balls keep the engine's value, so
only the drop changes.

* **drop model**: as above. **sand +0.2**: every sand shot on the hole 0.2 worse (tee balls in sand as well).
* **hostile**: sand +0.2; no drop valued better than rough; +0.15 on every drop on the right (stance on the bank);
  every ball in tall grass within 25 yds of a greenside sand patch drops in that sand.
* Not modelled: curving flight (which side of the channel a ball enters from). Bounds: if every channel ball came in
  from the green side (drop on the 1-2 yd strip by the green, a 10-15 yd chip, about 3.55) the go gains 0.02; the
  engine already takes the costly side (drop on the far bank, pitch back across).

Why the engine's shortcut barely matters here: it calls the drop rough when most right-side drops are on short grass
(-0.11 a ball), it ignores the carry back across (+0.02 to +0.10), and it never puts a drop in sand (0.0-0.1 % of
balls). Net: dropped ball 3.95 -> 3.86, the go 0.01-0.02 better under the rules model.

## 3. Re-priced tables

Strokes for the hole. "dropped" = share of tee balls that take a drop. Bold = the go club. Last column: the go
club's dropped balls by where the drop is (the three add to its dropped share; re-tee is never the best option).
Map (b) = published (band between the channel and the right fairway dead); map (a) = lidar reading (band mown).
Middle = Back tee moved 20 yds up the line; aims are from that tee's line.

### Back tee, map (b)

| day | pricing | 2-wood: aim, strokes, dropped | 4-wood: aim, strokes, dropped | 8-iron | mid iron (in sand) | long iron (in sand) | go minus 8-iron | minus mid iron | minus long iron | go ball dropped: on grass same side / in sand / pitching back across |
|---|---|---|---|---|---|---|---|---|---|---|
| calm | engine | **25.5 L, 3.744, 19 %** | 27.0 L, 3.757, 15 % | 4.149 | 4.070 (1 %) | 4.038 (9 %) | **0.41** | 0.33 | 0.29 | - |
| calm | drop model | **25.5 L, 3.728, 19 %** | 27.0 L, 3.746, 15 % | 4.149 | 4.070 (1 %) | 4.038 (9 %) | **0.42** | 0.34 | 0.31 | 1.7 / 0.0 / 17.2 % |
| calm | drop model, sand +0.2 | **25.5 L, 3.738, 19 %** | 26.5 L, 3.770, 15 % | 4.149 | 4.071 (0 %) | 4.055 (8 %) | **0.41** | 0.33 | 0.32 | 1.7 / 0.0 / 17.2 % |
| calm | hostile | **25.5 L, 3.791, 19 %** | 27.0 L, 3.805, 15 % | 4.149 | 4.071 (0 %) | 4.055 (8 %) | **0.36** | 0.28 | 0.26 | 0.1 / 3.0 / 15.8 % |
| Sat | engine | **17.5 L, 3.746, 19 %** | 19.0 L, 3.772, 15 % | 4.152 | 4.072 (0 %) | 4.044 (9 %) | **0.41** | 0.33 | 0.30 | - |
| Sat | drop model | **17.0 L, 3.731, 19 %** | 18.5 L, 3.760, 15 % | 4.152 | 4.072 (0 %) | 4.045 (9 %) | **0.42** | 0.34 | 0.31 | 1.6 / 0.0 / 17.8 % |
| Sat | drop model, sand +0.2 | **17.0 L, 3.741, 19 %** | 18.5 L, 3.784, 15 % | 4.152 | 4.073 (0 %) | 4.062 (9 %) | **0.41** | 0.33 | 0.32 | 1.7 / 0.0 / 17.8 % |
| Sat | hostile | **17.5 L, 3.794, 19 %** | 20.0 L, 3.819, 14 % | 4.152 | 4.073 (0 %) | 4.062 (9 %) | **0.36** | 0.28 | 0.27 | 0.1 / 3.0 / 15.8 % |
| Sun | engine | 29.5 L, 3.770, 18 % | **29.5 L, 3.667, 15 %** | 4.126 | 4.064 (2 %) | 3.988 (4 %) | **0.46** | 0.40 | 0.32 | - |
| Sun | drop model | 29.0 L, 3.754, 19 % | **29.0 L, 3.655, 15 %** | 4.126 | 4.064 (2 %) | 3.988 (4 %) | **0.47** | 0.41 | 0.33 | 1.0 / 0.0 / 14.0 % |
| Sun | drop model, sand +0.2 | 29.0 L, 3.762, 19 % | **29.0 L, 3.671, 15 %** | 4.126 | 4.068 (2 %) | 3.997 (4 %) | **0.45** | 0.40 | 0.33 | 1.0 / 0.0 / 14.0 % |
| Sun | hostile | 29.5 L, 3.815, 18 % | **29.5 L, 3.709, 15 %** | 4.126 | 4.068 (2 %) | 3.997 (4 %) | **0.42** | 0.36 | 0.29 | 0.5 / 1.2 / 12.9 % |

### Back tee, map (a)

| day | pricing | 2-wood: aim, strokes, dropped | 4-wood: aim, strokes, dropped | 8-iron | mid iron (in sand) | long iron (in sand) | go minus 8-iron | minus mid iron | minus long iron | go ball dropped: on grass same side / in sand / pitching back across |
|---|---|---|---|---|---|---|---|---|---|---|
| calm | engine | **22.5 L, 3.635, 11 %** | 22.0 L, 3.685, 12 % | 4.149 | 4.070 (1 %) | 4.037 (9 %) | **0.51** | 0.43 | 0.40 | - |
| calm | drop model | **22.5 L, 3.634, 11 %** | 22.0 L, 3.683, 12 % | 4.149 | 4.070 (1 %) | 4.038 (9 %) | **0.52** | 0.44 | 0.40 | 1.6 / 0.0 / 9.8 % |
| calm | drop model, sand +0.2 | **22.5 L, 3.643, 11 %** | 21.5 L, 3.702, 12 % | 4.149 | 4.071 (0 %) | 4.055 (8 %) | **0.51** | 0.43 | 0.41 | 1.6 / 0.0 / 9.8 % |
| calm | hostile | **22.5 L, 3.670, 11 %** | 21.5 L, 3.726, 12 % | 4.149 | 4.071 (0 %) | 4.055 (8 %) | **0.48** | 0.40 | 0.38 | 0.3 / 2.0 / 9.0 % |
| Sat | engine | **12.0 L, 3.636, 12 %** | 14.0 L, 3.699, 12 % | 4.152 | 4.072 (0 %) | 4.044 (9 %) | **0.52** | 0.44 | 0.41 | - |
| Sat | drop model | **12.0 L, 3.635, 12 %** | 14.0 L, 3.697, 12 % | 4.152 | 4.072 (0 %) | 4.044 (9 %) | **0.52** | 0.44 | 0.41 | 1.1 / 0.0 / 10.8 % |
| Sat | drop model, sand +0.2 | **12.0 L, 3.644, 12 %** | 14.0 L, 3.717, 12 % | 4.152 | 4.073 (0 %) | 4.061 (9 %) | **0.51** | 0.43 | 0.42 | 1.1 / 0.0 / 10.8 % |
| Sat | hostile | **12.0 L, 3.671, 12 %** | 16.5 L, 3.741, 10 % | 4.152 | 4.073 (0 %) | 4.062 (9 %) | **0.48** | 0.40 | 0.39 | 0.3 / 1.4 / 10.2 % |
| Sun | engine | 25.0 L, 3.659, 11 % | **26.0 L, 3.589, 11 %** | 4.126 | 4.064 (2 %) | 3.987 (4 %) | **0.54** | 0.47 | 0.40 | - |
| Sun | drop model | 25.0 L, 3.656, 11 % | **25.0 L, 3.587, 11 %** | 4.126 | 4.064 (2 %) | 3.987 (4 %) | **0.54** | 0.48 | 0.40 | 1.1 / 0.0 / 10.1 % |
| Sun | drop model, sand +0.2 | 25.0 L, 3.663, 11 % | **24.5 L, 3.602, 12 %** | 4.126 | 4.068 (2 %) | 3.995 (4 %) | **0.52** | 0.47 | 0.39 | 1.0 / 0.0 / 10.5 % |
| Sun | hostile | 25.0 L, 3.689, 11 % | **26.5 L, 3.624, 10 %** | 4.126 | 4.068 (2 %) | 3.995 (4 %) | **0.50** | 0.44 | 0.37 | 0.5 / 0.8 / 9.2 % |

### Middle tee, map (b)

| day | pricing | 2-wood: aim, strokes, dropped | 4-wood: aim, strokes, dropped | 8-iron | mid iron (in sand) | long iron (in sand) | go minus 8-iron | minus mid iron | minus long iron | go ball dropped: on grass same side / in sand / pitching back across |
|---|---|---|---|---|---|---|---|---|---|---|
| calm | engine | 27.0 L, 3.943, 22 % | **25.5 L, 3.696, 14 %** | 4.076 | 4.059 (8 %) | 3.942 (0 %) | **0.38** | 0.36 | 0.25 | - |
| calm | drop model | 26.5 L, 3.927, 23 % | **25.5 L, 3.683, 14 %** | 4.076 | 4.059 (8 %) | 3.939 (0 %) | **0.39** | 0.38 | 0.26 | 1.9 / 0.0 / 12.5 % |
| calm | drop model, sand +0.2 | 26.5 L, 3.936, 23 % | **25.5 L, 3.689, 14 %** | 4.076 | 4.076 (8 %) | 3.939 (0 %) | **0.39** | 0.39 | 0.25 | 1.9 / 0.0 / 12.5 % |
| calm | hostile | 26.5 L, 4.004, 23 % | **25.5 L, 3.728, 14 %** | 4.076 | 4.076 (8 %) | 3.946 (0 %) | **0.35** | 0.35 | 0.22 | 0.1 / 2.4 / 11.9 % |
| Sat | engine | 19.0 L, 3.931, 22 % | **17.5 L, 3.686, 14 %** | 4.079 | 4.062 (8 %) | 3.943 (0 %) | **0.39** | 0.38 | 0.26 | - |
| Sat | drop model | 19.0 L, 3.915, 22 % | **17.5 L, 3.674, 14 %** | 4.079 | 4.062 (8 %) | 3.941 (0 %) | **0.40** | 0.39 | 0.27 | 1.8 / 0.0 / 12.4 % |
| Sat | drop model, sand +0.2 | 18.5 L, 3.922, 22 % | **17.5 L, 3.679, 14 %** | 4.079 | 4.077 (7 %) | 3.941 (0 %) | **0.40** | 0.40 | 0.26 | 1.8 / 0.0 / 12.4 % |
| Sat | hostile | 18.5 L, 3.989, 22 % | **17.5 L, 3.718, 14 %** | 4.079 | 4.077 (7 %) | 3.947 (0 %) | **0.36** | 0.36 | 0.23 | 0.1 / 2.4 / 11.8 % |
| Sun | engine | 30.5 L, 4.092, 30 % | **30.0 L, 3.804, 14 %** | 4.057 | 4.024 (7 %) | 3.927 (0 %) | **0.25** | 0.22 | 0.12 | - |
| Sun | drop model | 30.5 L, 4.075, 30 % | **29.5 L, 3.792, 14 %** | 4.057 | 4.024 (7 %) | 3.924 (0 %) | **0.27** | 0.23 | 0.13 | 3.2 / 0.1 / 11.0 % |
| Sun | drop model, sand +0.2 | 27.5 L, 4.086, 32 % | **29.0 L, 3.797, 15 %** | 4.058 | 4.038 (7 %) | 3.925 (0 %) | **0.26** | 0.24 | 0.13 | 3.1 / 0.0 / 11.6 % |
| Sun | hostile | 27.5 L, 4.180, 32 % | **29.5 L, 3.837, 14 %** | 4.058 | 4.038 (7 %) | 3.932 (0 %) | **0.22** | 0.20 | 0.09 | 0.3 / 3.5 / 10.5 % |

### Middle tee, map (a)

| day | pricing | 2-wood: aim, strokes, dropped | 4-wood: aim, strokes, dropped | 8-iron | mid iron (in sand) | long iron (in sand) | go minus 8-iron | minus mid iron | minus long iron | go ball dropped: on grass same side / in sand / pitching back across |
|---|---|---|---|---|---|---|---|---|---|---|
| calm | engine | 17.5 L, 3.820, 13 % | **22.5 L, 3.616, 9 %** | 4.076 | 4.059 (8 %) | 3.915 (0 %) | **0.46** | 0.44 | 0.30 | - |
| calm | drop model | 17.5 L, 3.815, 13 % | **20.0 L, 3.613, 10 %** | 4.076 | 4.059 (8 %) | 3.915 (0 %) | **0.46** | 0.45 | 0.30 | 0.8 / 0.0 / 9.4 % |
| calm | drop model, sand +0.2 | 17.5 L, 3.819, 13 % | **20.0 L, 3.617, 10 %** | 4.076 | 4.076 (8 %) | 3.915 (0 %) | **0.46** | 0.46 | 0.30 | 0.8 / 0.0 / 9.4 % |
| calm | hostile | 17.0 L, 3.849, 13 % | **20.0 L, 3.637, 10 %** | 4.076 | 4.076 (8 %) | 3.916 (0 %) | **0.44** | 0.44 | 0.28 | 0.2 / 0.9 / 9.2 % |
| Sat | engine | 9.5 L, 3.808, 13 % | **14.5 L, 3.605, 9 %** | 4.079 | 4.062 (8 %) | 3.919 (0 %) | **0.47** | 0.46 | 0.31 | - |
| Sat | drop model | 9.5 L, 3.803, 13 % | **14.5 L, 3.604, 9 %** | 4.079 | 4.062 (9 %) | 3.919 (0 %) | **0.47** | 0.46 | 0.32 | 1.2 / 0.0 / 8.2 % |
| Sat | drop model, sand +0.2 | 9.5 L, 3.806, 13 % | **12.0 L, 3.608, 10 %** | 4.079 | 4.077 (7 %) | 3.919 (0 %) | **0.47** | 0.47 | 0.31 | 0.8 / 0.0 / 9.4 % |
| Sat | hostile | 9.0 L, 3.835, 13 % | **14.5 L, 3.628, 9 %** | 4.079 | 4.077 (7 %) | 3.920 (0 %) | **0.45** | 0.45 | 0.29 | 0.1 / 1.4 / 7.9 % |
| Sun | engine | 16.5 L, 3.968, 20 % | **26.5 L, 3.733, 10 %** | 4.057 | 4.024 (7 %) | 3.889 (0 %) | **0.32** | 0.29 | 0.16 | - |
| Sun | drop model | 16.5 L, 3.962, 20 % | **26.5 L, 3.730, 10 %** | 4.057 | 4.024 (7 %) | 3.888 (0 %) | **0.33** | 0.29 | 0.16 | 2.4 / 0.0 / 7.4 % |
| Sun | drop model, sand +0.2 | 16.0 L, 3.965, 20 % | **26.0 L, 3.734, 10 %** | 4.058 | 4.038 (7 %) | 3.889 (0 %) | **0.32** | 0.30 | 0.15 | 2.3 / 0.0 / 7.6 % |
| Sun | hostile | 7.0 L, 3.997, 17 % | **26.5 L, 3.755, 10 %** | 4.058 | 4.038 (7 %) | 3.891 (0 %) | **0.30** | 0.28 | 0.14 | 0.4 / 2.3 / 7.0 % |

### Tall grass not staked (lost ball, re-tee hitting 3), drop model for the rest

| tee, map, day | go | strokes | go minus 8-iron | minus long iron |
|---|---|---|---|---|
| Back (b) calm | 2-wood 23.5 L | 3.752 | 0.40 | 0.29 |
| Back (b) Sat | 2-wood 15.5 L | 3.753 | 0.40 | 0.29 |
| Back (b) Sun | 4-wood 28.5 L | 3.667 | 0.46 | 0.32 |
| Back (a) calm | 2-wood 19.5 L | 3.646 | 0.50 | 0.39 |
| Back (a) Sat | 2-wood 11.5 L | 3.647 | 0.50 | 0.40 |
| Back (a) Sun | 4-wood 24.5 L | 3.594 | 0.53 | 0.39 |
| Middle (b) calm | 4-wood 25.0 L | 3.706 | 0.37 | 0.23 |
| Middle (b) Sat | 4-wood 17.0 L | 3.698 | 0.38 | 0.24 |
| Middle (b) Sun | 4-wood 28.5 L | 3.827 | 0.23 | 0.10 |
| Middle (a) calm | 4-wood 20.0 L | 3.623 | 0.45 | 0.29 |
| Middle (a) Sat | 4-wood 11.5 L | 3.615 | 0.46 | 0.31 |
| Middle (a) Sun | 4-wood 25.0 L | 3.752 | 0.31 | 0.14 |
Checks asked for: **mid iron from the Back tee** is sand-free in the calm and on Saturday (0.4-0.5 % in the fairway
sand), 2.0-2.5 % on Sunday's helping wind; from Middle it is the wrong club (7-8 % in the sand) and the 8-iron is the
stay-short club. The 8-iron is 0 % sand from both tees, every day. The long iron from Back has 8-10 % in the fairway
sand (4 % Sunday); with sand +0.2 it loses 0.02 and the mid iron is level with it.

Does the aim move away from the left? No. Largest move under any pricing 2.5 yds (Middle, map a, calm 4-wood
22.5 L -> 20 L, a flat curve), Back within 1 yd for the pick.

## 4. Map (a) or (b)

Will: "it matches what the LiDAR says". The lidar reading is map (a): the band is mown. Under (a), drop model:
Back 2-wood 22.5 L calm, 12 L Saturday, 0.05-0.06 over the 4-wood; Sunday 4-wood 25 L by 0.07; go over the 8-iron
0.51-0.54, over the long iron 0.40. Under (b): 2-wood 25.5 L / 17 L by 0.02-0.03 over the 4-wood, Sunday 4-wood 29 L
by 0.10; go over the 8-iron 0.42-0.47. The club and the go decision are the same on both; the aim is 3-5 yds
further right on (a). Not applied; the manager decides.

## 5. Elsewhere on the course

The drop is priced the same way on every hole: rough at the last-crossing point, no look at sand. AUDIT_R3 moved
the drop point two ways on all 26 Back / Middle tee holes and kept the same club on 26 of 26; a sand drop needs sand
lying against a dead area inside the tee shot's oval, a 0.1-0.3 stroke change on a few per cent of balls, so nothing
worth changing before tomorrow.
