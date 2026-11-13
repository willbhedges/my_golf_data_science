# Gateway National: variance, lay-ups and hole 6 (Nov 13 2026)

For Will, Back tees, 36 holes of stroke play. A read-only study: the engine, the map and the page are untouched.
Everything here is the engine's central world (prior means, forecast temperature per hole) at the book's aims, 60,000
swings per club and hole; its means are within 0.015 of the book's prior-averaged values on every Driver hole.
Scripts and the hole-6 picture are in the session scratch folder (`variance/`), not in the repo.

## The three answers

**Q1. Hole 6, Driver: are we sure?** Yes. The mapped corridor between the native edges is 78 yds wide where the
Driver finishes (270-310), against a 70-yd Driver pattern, and on the 2023 photo the right-hand edge is drawn 10-15
yds tighter than the ground (the real tall grass starts beyond the cart path, at about +62, not +48). Driver is
ahead by 0.115 strokes over the 2-wood with 3 % of balls in penalty; it is still ahead with both native edges 6 yds
closer AND a 30 % wider pattern (by 0.05), and only loses (to the 4-wood, not the 2-wood) when the edges are about
10 yds closer on both sides together with a 30 % wider pattern, or 15 yds closer with a 15 % wider one. It is the
sixth most fragile of the eleven Driver holes, well behind 11, 9, 3, 1 and 2. One condition (section E): the
Driver's edge on 6 is the chance to go for the green in two (40-70 % of Drivers leave 225-240 or less to the front,
almost no 2-woods do). If he will lay up to a number whatever happens, the three woods score the same on 6.

**Q2. Does expected strokes flatten inside wedge range, and do we account for it?** We do, and it does not flatten
enough. In the table the engine uses, 140 to 110 yds from the fairway is worth 0.12 strokes (0.085 on the Tour
table); amateurs lose more per yard than pros, not less, so the amateur slope is the steeper one. One penalty ball
costs about 1.1 strokes, so 30 yds of wedge distance pays for about 10 extra penalty balls per 100 drives, and on
the Driver holes the Driver adds 1-4 per 100 over the 4-wood. The intuition is right on exactly two holes, 9 and 11,
where the distance gain is smallest relative to the risk (half to 70 % of it is given back): both are within 0.03,
and on the Tour slope 11 is a tie. The sharper form of the question is on the par 5s (section E): with a
lay-up-regardless second shot, Driver's 0.12 on 6, 13 and 18 becomes a coin flip (never a clear loss); with a plan
to go from 240 or less to the front it stays +0.06 to +0.17. Hole 3 is Driver under any plan.

**Q3. Is lower expected score simply correct, or does the lay-up buy consistency?** For a 36-hole total, lower
expected score per decision is correct, and here the lay-up does not buy consistency: the variance is nearly the
same, just shifted worse. A round's score SD is about 3.15 strokes with the page picks and 3.08 with one club less
on every tee; the tee shot's outcome is only 13 % of a round's variance. Over 36 holes "one club less" costs 2.5
strokes of mean for 0.10 strokes of SD and posts the lower total 32 % of the time (page 63 %, tie 6 %); the page's
total is better at every cut number, high or low. The legitimate part of the intuition is model risk and bad
driver days, and that also points at 11 and 9 only.

**Would I change a pick?** No club changes on expected strokes. Two things to add to the page: (a) show 11 as
"Driver or 4-wood" (0.027 apart; 4-wood has 1.7 % penalty balls against 6.0 % and 4.9 % doubles-or-worse against
7.5 %, and it wins if his pattern is 16 % wider than modelled or a native ball costs 1.7 strokes instead of 1);
(b) an on-the-day rule: if two of the first three drives (holes 1-3) finish more than 25 yds off the line, hit
4-wood on 11 and 2-wood on 9 that day. Keep Driver on 5, 6, 8, 13, 15, 18 whatever the day. (c) On 6 and 13 say that the Driver is
the pick for a player who goes for the green from 240 or less to the front, and that the three woods are level
for one who lays up regardless (section E, with wording).

## A. The table at wedge range (Q2)

Engine (`table="am"`): Tour (Broadie) fairway value + 0.36 + 0.0012 x (yds - 150), the term applied at every
distance, so the slope is steeper than Tour everywhere; rough = fairway + 0.75 x Tour's rough-fairway gap.

| yds | fairway, engine | fairway, Tour | rough, engine | rough, Tour | rough - fairway, engine | rough - fairway, Tour |
|---|---|---|---|---|---|---|
| 60 | 2.95 | 2.70 | 3.11 | 2.91 | 0.16 | 0.21 |
| 80 | 3.03 | 2.75 | 3.18 | 2.96 | 0.16 | 0.21 |
| 100 | 3.10 | 2.80 | 3.26 | 3.02 | 0.17 | 0.22 |
| 110 | 3.14 | 2.83 | 3.31 | 3.05 | 0.17 | 0.22 |
| 120 | 3.17 | 2.85 | 3.35 | 3.08 | 0.17 | 0.23 |
| 140 | 3.26 | 2.91 | 3.44 | 3.15 | 0.18 | 0.24 |
| 160 | 3.35 | 2.98 | 3.54 | 3.23 | 0.19 | 0.25 |
| 180 | 3.48 | 3.08 | 3.65 | 3.31 | 0.17 | 0.23 |
| 200 | 3.61 | 3.19 | 3.78 | 3.42 | 0.17 | 0.23 |

| 30 yds is worth | fairway | rough |
|---|---|---|
| 110 vs 140, engine | 0.121 (0.0040 / yd) | 0.132 |
| 110 vs 140, Tour | 0.085 (0.0028 / yd) | 0.100 |
| 170 vs 200, engine | 0.20 | 0.20 |
| 170 vs 200, Tour | 0.165 | 0.165 |

* The curve does flatten at wedge range, as Will says: 30 yds is worth 0.12 there against 0.20 at 170-200. It does
  not go flat.
* Rough at 110 (3.31) is worse than fairway at 140 (3.26) by 0.05 in the engine and by 0.14 on Tour. So a certain
  fairway at 140 does beat a certain rough at 110. The decision is not that trade, because the shorter club only
  moves 5-15 balls in 100 from rough to fairway (table below).
* Is the amateur slope sensible? Direction yes. The source (`spirit_hollow/research.md`, quoted in MODEL.md) is
  scratch 3.04 from 100 yds (Tour 2.80) and "a 5 index from 100 averages what scratch does from 150": the gap to
  Tour grows with distance, so each yard is worth more to an amateur. The size (0.0012 / yd) is rated low-medium
  confidence there. Nothing was fetched for this study.
* How flat would it have to be? Re-pricing every ball inside 150 yds with a fraction of the engine's slope (aims
  fixed; 1 = engine, 0.70 = Tour, 0 = dead flat inside 150), the Driver stops being the pick at:

  | hole | Driver leaves | break-even slope inside 150 | reading |
  |---|---|---|---|
  | 11 | 127 | 0.67 of the engine's | a tie on the Tour slope |
  | 9 | 108 | 0.54 | lay-up wins only if wedge yards are worth less than on Tour |
  | 1 | 91 | 0.34 | needs a third of the engine's slope |
  | 8 | 111 | 0.19 | needs an almost flat table |
  | 2, 15 | 132, 144 | none | Driver even with a dead-flat table inside 150 (the shorter club is left outside 150) |

### Driver against the next club down, split into distance, lie and penalty

Per ball: distance term = the fairway-table value at the ball's distance (the drop point for a penalty ball), as if
every ball were on the fairway; lie term = what the lie adds for balls in play (rough, sand, trees, blocked line);
penalty term = what a penalty ball adds over a fairway ball at its drop. The three sum to the margin exactly.
Positive = favours the Driver. Shares are fairway / rough / sand / trees / penalty in %. "Given back" = (lie +
penalty) / distance gain.

Driver vs 2-wood:

| hole | median left, Driver / 2-wood | Driver shares | 2-wood shares | distance | lie mix | penalty | margin | book margin | given back |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 91 / 111 | 76/18/ 3/ 0/ 2.9 | 79/14/ 5/ 0/ 1.7 | +0.066 | +0.000 | -0.015 | **0.052** | 0.051 | 0.22 |
| 2 | 132 / 152 | 76/20/ 0/ 0/ 4.1 | 76/19/ 1/ 0/ 2.6 | +0.081 | +0.003 | -0.017 | **0.067** | 0.062 | 0.17 |
| 3 | 345 / 364 | 62/31/ 3/ 2/ 2.5 | 73/24/ 0/ 1/ 1.5 | +0.090 | -0.020 | -0.012 | **0.058** | 0.061 | 0.35 |
| 5 | 170 / 189 | 67/28/ 2/ 0/ 2.1 | 72/24/ 4/ 0/ 1.0 | +0.108 | -0.004 | -0.012 | **0.092** | 0.091 | 0.15 |
| 6 | 246 / 266 | 80/17/ 0/ 1/ 3.0 | 85/12/ 2/ 0/ 1.5 | +0.139 | -0.005 | -0.017 | **0.117** | 0.114 | 0.15 |
| 8 | 111 / 130 | 66/32/ 1/ 1/ 0.0 | 76/22/ 0/ 1/ 0.0 | +0.074 | -0.017 | -0.000 | **0.057** | 0.046 | 0.23 |
| 9 | 108 / 125 | 51/42/ 1/ 3/ 2.7 | 62/32/ 4/ 2/ 1.4 | +0.063 | -0.018 | -0.015 | **0.029** | 0.024 | 0.53 |
| 11 | 127 / 144 | 58/35/ 0/ 0/ 6.0 | 65/30/ 0/ 0/ 4.3 | +0.059 | -0.008 | -0.021 | **0.031** | 0.031 | 0.48 |
| 13 | 249 / 268 | 70/20/ 8/ 0/ 2.2 | 61/31/ 6/ 0/ 1.3 | +0.125 | +0.004 | -0.011 | **0.119** | 0.102 | 0.05 |
| 15 | 144 / 165 | 77/18/ 3/ 0/ 1.2 | 77/14/ 8/ 0/ 0.5 | +0.105 | +0.012 | -0.008 | **0.109** | 0.102 | -0.03 |
| 18 | 230 / 247 | 79/15/ 4/ 1/ 0.6 | 79/16/ 4/ 1/ 0.4 | +0.129 | -0.007 | -0.002 | **0.121** | 0.124 | 0.07 |

Driver vs 4-wood:

| hole | median left, Driver / 4-wood | Driver shares | 4-wood shares | distance | lie mix | penalty | margin | book margin | given back |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 91 / 122 | 76/18/ 3/ 0/ 2.9 | 83/14/ 3/ 0/ 0.5 | +0.105 | -0.007 | -0.028 | **0.069** | 0.067 | 0.34 |
| 2 | 132 / 161 | 76/20/ 0/ 0/ 4.1 | 79/17/ 3/ 0/ 1.3 | +0.128 | +0.002 | -0.033 | **0.098** | 0.088 | 0.24 |
| 3 | 345 / 374 | 62/31/ 3/ 2/ 2.5 | 83/16/ 0/ 1/ 0.4 | +0.135 | -0.035 | -0.024 | **0.076** | 0.075 | 0.44 |
| 5 | 170 / 199 | 67/28/ 2/ 0/ 2.1 | 77/20/ 3/ 0/ 0.2 | +0.172 | -0.014 | -0.021 | **0.137** | 0.131 | 0.20 |
| 6 | 246 / 275 | 80/17/ 0/ 1/ 3.0 | 89/ 9/ 2/ 0/ 0.3 | +0.199 | -0.010 | -0.030 | **0.160** | 0.155 | 0.20 |
| 8 | 111 / 142 | 66/32/ 1/ 1/ 0.0 | 80/20/ 0/ 0/ 0.0 | +0.128 | -0.026 | -0.000 | **0.102** | 0.094 | 0.20 |
| 9 | 108 / 134 | 51/42/ 1/ 3/ 2.7 | 66/28/ 5/ 0/ 0.6 | +0.098 | -0.029 | -0.025 | **0.044** | 0.036 | 0.55 |
| 11 | 127 / 153 | 58/35/ 0/ 0/ 6.0 | 72/26/ 0/ 0/ 1.7 | +0.093 | -0.015 | -0.051 | **0.027** | 0.024 | 0.71 |
| 13 | 249 / 276 | 70/20/ 8/ 0/ 2.2 | 72/26/ 2/ 0/ 0.5 | +0.180 | -0.017 | -0.020 | **0.143** | 0.125 | 0.20 |
| 15 | 144 / 180 | 77/18/ 3/ 0/ 1.2 | 76/14/ 9/ 0/ 0.1 | +0.181 | +0.018 | -0.012 | **0.187** | 0.172 | -0.03 |
| 18 | 230 / 260 | 79/15/ 4/ 1/ 0.6 | 80/14/ 4/ 1/ 0.1 | +0.211 | -0.010 | -0.006 | **0.196** | 0.196 | 0.07 |

* The distance gain is smallest on the wedge holes, as Will expected: 0.06-0.07 for 17-20 yds on 1, 9, 11 against
  0.11-0.14 on 5, 6, 13, 18. That is the flattening, and it is in the numbers.
* The risk given back is largest on 9 (53-55 %) and 11 (48-71 %), then 3 (35-44 %). Everywhere else the Driver
  keeps 65-100 % of its distance gain. On 13 and 15 the Driver's lie mix is no worse than the shorter club's.
* The temperature matters to the leave: at the forecast 40s the Driver finishes about 285, not 300.

## B. Score distributions (Q3)

What is modelled and what is assumed:

* Modelled (engine): where each of 60,000 tee balls finishes, its lie, and the expected strokes from there.
* Assumed (mine): the spread of the strokes still to play. For each ball, an integer distribution whose mean is the
  engine's value and whose SD is 0.62 + 0.115 x (mean - 3): 0.62 strokes for a wedge approach, 0.74 with 4 to play,
  right-skewed (a two-point floor / ceiling split, plus a symmetric +/-1 and a -1 / +2 component). No published
  strokes-to-hole-out variance was fetched; the level is set so that a par 4 comes out at about 0.7 a hole, a
  low-handicap figure. A penalty ball adds one stroke and plays on from its drop with the same rule. The same rule
  is used for every club, so differences between clubs come from the engine's tee-shot outcomes, not from this
  assumption. Tested at x0.8 and x1.25.
* Par 3s: held fixed at mean 3.25, SD 0.73 each (12 % birdie, 56 % par, 27 % bogey, 5 % double): a placeholder that
  is the same in every strategy.
* Holes are treated as independent (relaxed in C-ii).

Per hole, club at its own best aim. "pen" = tee balls in a penalty area, %.

| hole | club | mean | SD | pen % | birdie or better % | par % | bogey % | double or worse % |
|---|---|---|---|---|---|---|---|---|
| 1 | Driver (pick) | 4.168 | 0.70 | 2.9 | 10.5 | 67.2 | 17.7 | 4.6 |
| 1 | 2-wood | 4.220 | 0.68 | 1.7 | 8.6 | 65.4 | 21.8 | 4.2 |
| 1 | 4-wood | 4.237 | 0.67 | 0.5 | 7.8 | 64.8 | 23.8 | 3.6 |
| 2 | Driver (pick) | 4.339 | 0.73 | 4.1 | 6.6 | 59.6 | 27.8 | 5.9 |
| 2 | 2-wood | 4.406 | 0.72 | 2.6 | 5.5 | 55.0 | 34.0 | 5.5 |
| 2 | 4-wood | 4.437 | 0.70 | 1.3 | 5.0 | 52.4 | 37.7 | 5.0 |
| 3 | Driver (pick) | 5.628 | 0.85 | 2.5 | 6.5 | 38.2 | 44.2 | 11.2 |
| 3 | 2-wood | 5.686 | 0.84 | 1.5 | 5.9 | 34.1 | 48.5 | 11.6 |
| 3 | 4-wood | 5.704 | 0.83 | 0.4 | 5.6 | 32.5 | 50.5 | 11.4 |
| 5 | Driver (pick) | 4.532 | 0.74 | 2.1 | 4.4 | 46.4 | 42.5 | 6.7 |
| 5 | 2-wood | 4.624 | 0.73 | 1.0 | 3.7 | 39.1 | 50.0 | 7.2 |
| 5 | 4-wood | 4.669 | 0.72 | 0.2 | 3.5 | 35.2 | 54.0 | 7.3 |
| 6 | Driver (pick) | 5.043 | 0.79 | 3.0 | 19.2 | 61.2 | 14.8 | 4.8 |
| 6 | 2-wood | 5.161 | 0.78 | 1.5 | 14.6 | 60.3 | 19.8 | 5.3 |
| 6 | 4-wood | 5.203 | 0.77 | 0.3 | 12.9 | 59.4 | 22.4 | 5.2 |
| 8 | Driver (pick) | 4.217 | 0.66 | 0.0 | 8.2 | 65.7 | 22.7 | 3.4 |
| 8 | 2-wood | 4.273 | 0.67 | 0.0 | 7.0 | 62.6 | 26.9 | 3.5 |
| 8 | 4-wood | 4.318 | 0.67 | 0.0 | 6.2 | 59.9 | 30.4 | 3.6 |
| 9 | Driver (pick) | 4.277 | 0.71 | 2.7 | 7.8 | 62.3 | 24.8 | 5.0 |
| 9 | 2-wood | 4.306 | 0.69 | 1.4 | 7.0 | 60.6 | 27.9 | 4.5 |
| 9 | 4-wood | 4.321 | 0.68 | 0.6 | 6.5 | 59.5 | 30.0 | 4.0 |
| 10 | Driver | 3.975 | 0.83 | 23.7 | 27.5 | 49.4 | 19.9 | 3.2 |
| 10 | 2-wood | 3.753 | 0.89 | 19.2 | 42.4 | 38.8 | 16.0 | 2.7 |
| 10 | 4-wood (pick) | 3.761 | 0.84 | 14.7 | 39.2 | 45.0 | 13.3 | 2.6 |
| 10 | Long iron | 4.037 | 0.65 | 0.5 | 14.3 | 70.1 | 12.6 | 2.9 |
| 11 | Driver (pick) | 4.377 | 0.77 | 6.0 | 6.6 | 58.1 | 27.8 | 7.5 |
| 11 | 2-wood | 4.408 | 0.74 | 4.3 | 5.7 | 55.7 | 32.1 | 6.6 |
| 11 | 4-wood | 4.404 | 0.70 | 1.7 | 5.3 | 54.8 | 35.0 | 4.9 |
| 13 | Driver (pick) | 5.081 | 0.80 | 2.2 | 18.2 | 59.9 | 16.9 | 5.0 |
| 13 | 2-wood | 5.200 | 0.79 | 1.3 | 13.6 | 58.7 | 22.0 | 5.6 |
| 13 | 4-wood | 5.224 | 0.77 | 0.5 | 12.4 | 58.6 | 23.5 | 5.4 |
| 15 | Driver (pick) | 4.363 | 0.70 | 1.2 | 6.0 | 57.3 | 31.9 | 4.7 |
| 15 | 2-wood | 4.472 | 0.71 | 0.5 | 4.7 | 49.6 | 40.5 | 5.1 |
| 15 | 4-wood | 4.550 | 0.71 | 0.1 | 4.1 | 43.8 | 46.3 | 5.7 |
| 16 | Driver | 4.420 | 0.76 | 11.7 | 7.4 | 50.4 | 35.9 | 6.4 |
| 16 | 2-wood | 4.262 | 0.73 | 5.1 | 9.2 | 60.9 | 24.7 | 5.2 |
| 16 | 4-wood (pick) | 4.165 | 0.68 | 2.2 | 10.1 | 67.4 | 18.5 | 4.0 |
| 16 | Long iron | 4.280 | 0.66 | 0.1 | 6.6 | 62.7 | 27.2 | 3.4 |
| 18 | Driver (pick) | 4.917 | 0.76 | 0.6 | 24.5 | 60.9 | 11.3 | 3.4 |
| 18 | 2-wood | 5.038 | 0.77 | 0.4 | 18.8 | 62.0 | 14.9 | 4.3 |
| 18 | 4-wood | 5.113 | 0.77 | 0.1 | 16.0 | 61.4 | 17.9 | 4.7 |

* The SD barely moves with the club: 0.70 / 0.68 / 0.67 on hole 1, 0.79 / 0.78 / 0.77 on hole 6. The lay-up removes
  some penalty doubles and adds bogeys from a longer approach.
* On six of the eleven Driver holes the Driver has no more doubles-or-worse than the 2-wood (3, 5, 6, 13, 15, 18)
  and on 8 it is level. The 2-wood has fewer doubles only on 1, 2, 9 and 11, by 0.4-0.9 points. The 4-wood has
  clearly fewer on 11 (4.9 against 7.5) and 9 (4.0 against 5.0).
* The Driver has more birdies on every Driver hole (hole 6: 19 % against 15 % and 13 %).

### Round strategies (13 tee-shot holes + 5 fixed par 3s)

"Tee SD" = the part of the round SD that comes from where the tee balls finish (the engine's part).
"Lower total" = chance the strategy's 36-hole total is lower / equal / higher than the page's, two independent
36-hole totals. "Trade rate" = strokes of 36-hole mean given up per stroke of 36-hole SD removed.

| strategy | round mean | round SD | tee SD | 36-hole mean | 36-hole SD | mean given up | SD removed | lower / tie / higher than page | trade rate |
|---|---|---|---|---|---|---|---|---|---|
| page picks | 75.12 | 3.15 | 1.15 | 150.23 | 4.46 | | | | |
| one club less on all 13 (2-wood for Driver; long iron on 10, 16) | 76.36 | 3.08 | 0.80 | 152.72 | 4.36 | 2.49 | 0.10 | 31.5 % / 5.9 % / 62.6 % | 25 to 1 |
| 2-wood on the 11 Driver holes, 10 and 16 as the page | 75.97 | 3.13 | 1.01 | 151.94 | 4.43 | 1.71 | 0.03 | 36.2 % / 6.1 % / 57.6 % | 52 to 1 |
| 4-wood on the 11 Driver holes | 76.36 | 3.10 | 0.87 | 152.71 | 4.39 | 2.48 | 0.07 | 31.6 % / 5.9 % / 62.5 % | 34 to 1 |
| lowest-SD club within 0.05 of the best (= 4-wood on 9 and 11, nothing else) | 75.19 | 3.13 | 1.08 | 150.38 | 4.43 | 0.14 | 0.03 | 45.9 % / 6.4 % / 47.7 % | 4.7 to 1 |

(The round mean of 75.1 includes the placeholder par 3s; only differences between rows mean anything.)

With the assumed remainder SD x0.8 / x1.25: page round SD 2.79 / 3.65; "one club less" removes 0.14 / 0.06 of
36-hole SD and is lower 29 % / 34 % of the time; the 9-and-11 strategy is lower 45 % / 47 %. The conclusion does
not depend on the assumption.

Why the SD hardly moves: Var(score) = E[Var(rest | where the ball finished)] + Var(E[rest | where it finished)].
The second term is the tee shot's and is 1.15^2 = 1.3 of a round variance of 9.9 (13 %). Laying up everywhere cuts
it to 0.64, and the first term rises a little because every approach is longer. MODEL.md's line ("tee-shot SD
1.16 to 0.46, cost 4.4 strokes") is the same finding for the lowest-variance club on every tee.

## C. The theory, and where the intuition is right

**Linear objective.** If the payoff is the 36-hole total, the total is a sum and the expectation of a sum is the sum
of expectations, so the club with the lower expected score on each tee is optimal whatever its variance. Variance
enters only when the payoff is not linear in the total.

**What a nonlinear payoff would need.** For a cut number T the criterion is P(total <= T). With a normal
approximation, giving up mean m to remove SD s helps only if T sits more than m / s standard deviations ABOVE his
mean (protecting against a blow-up); it always hurts when he needs a score below his mean. Here m / s is 25 for
"one club less" and 4.7 for the 9-and-11 version: the cut would have to be 21 strokes (9-and-11) or 110 strokes
(one less) above his expected total. Checked on the full distributions without the normal approximation: the
page's P(total <= T) is at least the conservative strategy's at every T (examples: T = 144: 9.6 % against 2.7 %;
T = 152: 70 % against 49 %; T = 160: 98.7 % against 96.0 %; T = 164: 99.9 % against 99.5 %). The page strategy
dominates; there is no top-N or cut shape that prefers the lay-up across 36 holes.

Where variance does matter is the end-game, when the remaining holes are few and the payoff is a step: one or two
holes to play with a lead that only a double loses, or a deficit that only a birdie closes. Then use the hole
table above directly: protecting on 11, the 4-wood (4.9 % doubles against 7.5 %); chasing on 18, the Driver (24.5 %
birdies against 18.8 %, and fewer doubles too). In a team best-ball the opposite holds: variance is good, take the
Driver.

### (i) Model risk: how wrong would the model have to be?

For each Driver hole, every club re-aimed at each setting (12,000 swings): the multiple of ALL clubs' lateral
dispersion at which the best of 2-wood / 4-wood draws level, and the multiple of the penalty stroke (1 = one stroke
plus the drop; 2 = two strokes plus the drop, roughly a lost ball or a bad drop) at which it does.

| rank | hole | margin now | dispersion multiple to draw level | penalty-cost multiple to draw level | dispersion x1.3 and penalty x2 together |
|---|---|---|---|---|---|
| 1 | 11 | 0.030 | **1.16** (4-wood) | **1.7** | 4-wood by 0.10 |
| 2 | 9 | 0.029 | 1.31 | 4.3 | 4-wood by 0.03 |
| 3 | 3 | 0.059 | 1.39 | 5.2 | 4-wood by 0.03 |
| 4 | 1 | 0.052 | 1.45 | 3.9 | 4-wood by 0.03 |
| 5 | 2 | 0.070 | 1.66 | 4.4 | 4-wood by 0.02 |
| 6 | 6 | 0.118 | 2.26 | none up to 6 | Driver by 0.035 |
| 7 | 8 | 0.057 | none up to 3 | none (no penalty area in range) | Driver by 0.05 |
| 8 | 5 | 0.090 | none up to 3 (lowest margin 0.03) | none up to 6 | Driver by 0.04 |
| 9 | 15 | 0.107 | none up to 3 (lowest 0.02 at x2.5) | none up to 6 | Driver by 0.06 |
| 10 | 18 | 0.117 | none up to 3 | none up to 6 | Driver by 0.09 |
| 11 | 13 | 0.123 | none up to 3 | none up to 6 | Driver by 0.07 |

* The conservative club is the robust one on 11, and to a lesser degree on 9, 3 and 1: a pattern 30-45 % wider than
  Will's stated 65 : 60 : 50 flips those. A 30 % wider pattern AND a doubled penalty cost flips 1, 2, 3, 9 and 11,
  all to the 4-wood rather than the 2-wood (the 2-wood is nearly as wide as the Driver and 20 yds shorter, so it
  is rarely the right hedge).
* 5, 6, 8, 13, 15, 18 are Driver holes under any plausible error.

### (ii) Bad driver days: holes are not independent

A shared day factor: 20 % of days every wood is 1.4x as wide, aims as on the page (he does not know in advance).

| | page picks | one club less | 4-wood on 9 and 11 |
|---|---|---|---|
| round mean, independent / with wild days | 75.12 / 75.44 | 76.36 / 76.59 | 75.19 / 75.49 |
| round SD, independent / with wild days | 3.15 / 3.27 | 3.08 / 3.16 | 3.13 / 3.23 |
| 36-hole mean given up, with wild days | | 2.31 | 0.10 |
| 36-hole SD removed, with wild days | | 0.16 | 0.04 |
| lower / tie / higher than page, with wild days | | 33.0 % / 5.8 % / 61.2 % | 46.3 % / 6.2 % / 47.6 % |

The correlation raises the page's round SD by 0.12 and helps the lay-up strategy a little (trade rate 15 to 1
instead of 25 to 1). It does not change the comparison.

Per hole on a wild day (expected strokes, Driver / 2-wood / 4-wood; "best shorter - Driver", positive = Driver
still ahead):

| hole | normal day | wild day, all woods x1.4 | Driver penalty %, normal -> wild | normal day | wild, all woods | wild Driver only (shorter club normal) |
|---|---|---|---|---|---|---|
| 1 | 4.168 / 4.220 / 4.237 | 4.307 / 4.331 / 4.316 | 2.9 -> 10.5 | +0.052 | +0.009 | -0.087 |
| 2 | 4.339 / 4.406 / 4.437 | 4.486 / 4.526 / 4.522 | 4.1 -> 12.5 | +0.067 | +0.036 | -0.080 |
| 3 | 5.628 / 5.686 / 5.704 | 5.776 / 5.802 / 5.777 | 2.5 -> 8.9 | +0.058 | +0.001 | -0.090 |
| 5 | 4.532 / 4.624 / 4.669 | 4.668 / 4.729 / 4.742 | 2.1 -> 8.4 | +0.092 | +0.061 | -0.044 |
| 6 | 5.043 / 5.161 / 5.203 | 5.177 / 5.255 / 5.259 | 3.0 -> 9.2 | +0.117 | +0.078 | -0.016 |
| 8 | 4.217 / 4.273 / 4.318 | 4.260 / 4.309 / 4.345 | 0.0 -> 0.2 | +0.057 | +0.048 | +0.013 |
| 9 | 4.277 / 4.306 / 4.321 | 4.412 / 4.412 / 4.401 | 2.7 -> 7.8 | +0.029 | -0.011 | -0.106 |
| 11 | 4.377 / 4.408 / 4.404 | 4.540 / 4.561 / 4.516 | 6.0 -> 14.9 | +0.027 | -0.024 | -0.136 |
| 13 | 5.081 / 5.200 / 5.224 | 5.186 / 5.290 / 5.293 | 2.2 -> 8.6 | +0.119 | +0.104 | +0.014 |
| 15 | 4.363 / 4.472 / 4.550 | 4.474 / 4.548 / 4.599 | 1.2 -> 6.5 | +0.109 | +0.075 | -0.002 |
| 18 | 4.917 / 5.038 / 5.113 | 5.020 / 5.114 / 5.171 | 0.6 -> 2.9 | +0.121 | +0.094 | +0.018 |

* If the whole long game is wild, the Driver is still the club on 2, 5, 6, 8, 13, 15, 18; 1 and 3 become ties; the
  4-wood wins 11 (by 0.024) and 9 (by 0.011). A rule that switches 9 and 11 to the 4-wood on such days, with perfect
  knowledge of the day, is worth 0.007 strokes a round: nothing.
* If it is the Driver alone that is wild and the shorter woods are behaving, switching pays on 11 (0.14), 9 (0.11),
  3 (0.09), 1 (0.09), 2 (0.08), 5 (0.04), and not on 6, 8, 13, 15, 18.
* Can he tell after three holes? Weakly. With a 17.5-yd lateral SD (24.5 on a wild day), two of the first three
  drives more than 25 yds off line happens on 6 % of normal days and 23 % of wild days: the chance the day is wild
  goes from 20 % to 45 %. Three of three: 67 %.
* The rule that this supports: **after two of three drives on holes 1-3 more than 25 yds off line, hit the 4-wood
  on 11 and the 2-wood (or 4-wood) on 9.** Being wrong costs 0.03 a hole; being right gains 0.02-0.14 a hole. At a
  45 % chance of a wild day that is about +0.02 to +0.08 strokes for the two holes together, depending on whether
  the shorter woods are wild too. On 5 the switch would need a 68 % chance of a Driver-only wild day; on 6, 8, 13,
  15, 18 it never pays. Holes 1, 2 and 3 are played before he can know.

## D. Hole 6 (Q1)

Looked at: the 2023 NAIP photo, 215-350 yds, with the mapped zones outlined and 2,500 finishing spots per club
(`variance/h6_landing.jpg` in the session scratch folder).

What the photo shows against the map:

* Fairway: -22 to +30 at 270-300 (52 yds), narrowing to 47 at 310 and 37 at 320. Mapped correctly.
* Left: mown rough from the fairway edge to about -30, then a row of trees from -33 to -60 (250-340) with rough
  textured ground behind. The mapped native strip (-48 to -30, from 255) starts where the trees start. The left
  edge at -30 is right to within 2-3 yds.
* Right: mown rough from +30 out to the cart path, which bows from +47 at 230 to +62 at 280 and back to +50 at
  310. The tall brown bank is beyond the path, +58 to +75 at 240-300. The mapped native band starts at +48 for the
  whole length, so at 260-300 it is 10-15 yds inside the real edge; from 310 on it is about right (the path and
  the cut field beyond it come in to +50). This agrees with REVIEW_A ("harsher than the ground on both sides").
* From the tee the left trees and the right bank frame the fairway and foreshorten it; from above the ground
  between the penalty edges is 78 yds as mapped and about 90 as photographed at Driver distance. The photo is
  from 2023; it cannot say how far the tall grass has been let in this November.

| distance | fairway | native / tree edge left to native edge right (mapped) | Driver 95 % (70) | 2-wood (65) | 4-wood (54) |
|---|---|---|---|---|---|
| 250 | -21 to +33 (54) | -54 to +48 (102) | fits, 32 spare | 37 spare | 48 spare |
| 270 | -22 to +30 (52) | -30 to +48 (78) | fits, 8 spare | 13 spare | 24 spare |
| 290 | -22 to +29 (52) | -30 to +48 (78) | fits, 8 spare | 13 spare | 24 spare |
| 310 | -19 to +28 (47) | -30 to +48 (78) | fits, 8 spare | 13 spare | 24 spare |

The corridor's centre is +9; the book aims the Driver at +5.5, toward the wider-open short grass and slightly away
from the right band.

| club (own best aim) | expected | fairway % | rough % | sand % | trees % | penalty % (left / right) | median left to the green |
|---|---|---|---|---|---|---|---|
| Driver +5 | 5.046 | 80 | 16 | 0 | 1 | 3.1 (1.9 / 1.2) | 246 |
| 2-wood +6 | 5.160 | 85 | 12 | 2 | 0 | 1.5 (0.7 / 0.8) | 266 |
| 4-wood +7.5 | 5.203 | 89 | 9 | 2 | 0 | 0.3 (0.1 / 0.3) | 275 |

The Driver buys 20 yds over the 2-wood on a par 5 where every club leaves a long second (0.139 strokes of distance
gain, the largest of any hole) for 1.6 more penalty balls in 100 (0.017) and 5 fewer fairways (0.005).

Stress, every club re-aimed each time. Cells: Driver's margin over the 2-wood / over the 4-wood (negative = Driver
loses), and the Driver's penalty share.

| native edges, both sides | pattern as stated | 15 % wider | 30 % wider | 50 % wider |
|---|---|---|---|---|
| as mapped (78 yds) | +0.115 / +0.158, 3 % | +0.100 / +0.128, 5 % | +0.082 / +0.098, 8 % | +0.067 / +0.062, 11 % |
| 3 yds closer (72) | +0.109 / +0.146, 4 % | +0.091 / +0.111, 7 % | +0.076 / +0.079, 10 % | +0.058 / +0.043, 14 % |
| 6 yds closer (66) | +0.101 / +0.127, 6 % | +0.080 / +0.087, 10 % | +0.060 / +0.051, 13 % | +0.046 / +0.012, 17 % |
| 9 yds closer (60) | +0.082 / +0.094, 10 % | +0.060 / +0.050, 14 % | +0.040 / +0.009, 18 % | +0.025 / -0.033, 22 % |
| 12 yds closer (54) | +0.066 / +0.060, 14 % | +0.041 / +0.012, 19 % | +0.025 / -0.032, 23 % | +0.012 / -0.067, 27 % |
| 15 yds closer (48) | +0.048 / +0.021, 18 % | +0.026 / -0.030, 24 % | +0.011 / -0.067, 28 % | -0.002 / -0.104, 33 % |

Break-even:

* Edges alone: none within 15 yds a side. With the corridor cut from 78 to 48 yds the Driver is still 0.02 ahead.
* Pattern alone: 2.26 times the stated width.
* Together: 13 yds closer a side with a 15 % wider pattern; 10 yds with 30 %; 7 yds with 50 %.
* The Driver never loses to the 2-wood before it loses to the 4-wood. If hole 6 looks too tight on the day, the
  hedge is the 4-wood, and it costs 0.16 strokes if the model is right.

**Verdict for hole 6: Driver, aim as on the page.** The requested stresses (3 and 6 yds, 15 and 30 %, and both)
leave it 0.05-0.11 ahead. The map's right edge is already drawn tighter than the photo shows.

## E. The par 5s under an explicit second-shot plan (the sharp version of Q2)

Prompted by `HOLE13.md`: on a par 5 the table's value of 20 yds at 250-270 out is mostly the value of going for
the green. If he would lay up anyway, that value is not there. Re-scored, same tee balls as above (central world,
book aims, 60,000 swings), Back and Middle.

Plans for the second shot:

* **(a)** the engine's table as it is.
* **(b)** he goes only from the fairway or first cut, with a clear line, and 240 (or 225) or less to the FRONT of
  the green (front = centre - 18 yds). Those balls keep the engine's value. Every other ball lays up.
  Assumption on reach: a cold 4-wood off the deck carries about 235 and totals about 250 (246-248 carry off a tee),
  so 240 to the front is his limit with a good strike and 225 is comfortable.
* **(c)** he never goes: lay up to 90 yds, or as close to that as a 230-yd shot gets him.
* **(c2)** he never goes but advances as far as he sensibly can: to 40 yds short, or 230 yds, whichever is less.

Lay-up value (mine, stated so it can be argued with): 1 + the engine's table at the leftover distance, fairway or
rough by the lay-up's own accuracy. Lay-up lateral SD = 5 % of the shot's length (the engine's irons: 95 % width
about 19 % of carry), x1.3 from rough; lay-up fairway 35 yds wide; 12 % of lay-ups finish 6.5 % short. From sand
+0.1. For trees and penalty balls the engine's value with its rough-table part swapped for the lay-up value. This
gives a lay-up slope that is small but not zero: 4.069 from 230 in the fairway, 4.077 from 270, 4.088 from 310
(0.0002 a yard: a 140-yd lay-up finds the short grass 99 % of the time, a 200-yd one 92 %), against the engine
table's 0.007 a yard over the same range. Once he cannot reach the 90 number (more than 320 out) the slope is the
wedge slope again, 0.004 a yard. Levels differ between plans; only the margins within a plan are comparable.
Hazards around the greens and in the lay-up zones are not priced in any plan.

Driver's margin over the 2-wood / over the 4-wood (positive = Driver ahead):

| tee | hole | Driver leaves to the front (fairway median) | Drivers with a go at 240 / 225 | 2-woods with a go at 240 / 225 | (a) table | (b) go from 240 | (b) go from 225 | (c) lay up to 90 | (c2) advance to 40 |
|---|---|---|---|---|---|---|---|---|---|
| Back | 3 (630) | 319 | 0 % / 0 % | 0 % / 0 % | +0.058 / +0.076 | +0.059 / +0.083 | +0.059 / +0.083 | +0.059 / +0.083 | +0.059 / +0.084 |
| Back | 6 (530) | 225 | 70 % / 40 % | 22 % / 1 % | +0.117 / +0.160 | +0.078 / +0.079 | +0.064 / +0.055 | -0.012 / -0.022 | +0.004 / +0.019 |
| Back | 13 (533) | 224 | 58 % / 37 % | 21 % / 1 % | +0.119 / +0.143 | +0.072 / +0.071 | +0.067 / +0.056 | -0.006 / -0.018 | +0.010 / +0.021 |
| Back | 18 (527) | 209 | 77 % / 69 % | 67 % / 34 % | +0.121 / +0.196 | +0.103 / +0.156 | +0.122 / +0.172 | -0.001 / -0.003 | +0.002 / +0.005 |
| Middle | 3 (566) | 259 | 2 % / 0 % | 0 % / 0 % | +0.079 / +0.100 | -0.009 / -0.023 | -0.010 / -0.024 | -0.010 / -0.024 | +0.066 / +0.083 |
| Middle | 6 (500) | 196 | 58 % / 58 % | 81 % / 67 % | +0.058 / +0.091 | +0.018 / +0.050 | +0.032 / +0.078 | -0.011 / -0.026 | -0.010 / -0.024 |
| Middle | 13 (520) | 210 | 73 % / 65 % | 58 % / 23 % | +0.116 / +0.183 | +0.078 / +0.119 | +0.100 / +0.130 | -0.032 / -0.037 | -0.027 / -0.025 |
| Middle | 18 (494) | 175 | 89 % / 89 % | 88 % / 87 % | +0.138 / +0.202 | +0.129 / +0.190 | +0.129 / +0.192 | -0.001 / -0.004 | +0.002 / -0.001 |

(Hole 18 Back is the map as it stands in the checkout, 527; whether that already includes the tee moved 17 yds
forward was not checked. 17 yds closer only strengthens "reachable".)

Reachable in the cold from the Driver position?

* **3 Back: no** (319 to the front). **3 Middle: no** (259).
* **6 Back: marginal.** 225 to the front from the median fairway Driver, 243 to the middle; 40 % of Drivers have
  225 or less, 70 % have 240 or less. From the 2-wood it is 246: out of reach. Same picture as 13.
* **13 Back: marginal**, 224 by this measure (HOLE13.md: 229 on the direct line).
* **18 Back: yes.** 209 to the front; two Drivers in three have 225 or less. From the 2-wood 227, one in three.
* Middle 6, 13, 18: yes from the Driver (196, 210, 175); on Middle 6 and 18 the shorter woods reach as well.

Verdict:

* **Back 3: Driver whatever the plan** (+0.06 / +0.08 in every column). It is a three-shot hole: he cannot reach a
  wedge number in two, so every yard off the tee comes off the third shot.
* **Back 6 and 13: Driver if he will go when he has 240 or less to the front from the fairway** (+0.06 to +0.08).
  **If he is laying up to a number regardless, the three woods are level** (within 0.02, the shorter clubs a hair
  ahead), and the choice is his. The Driver's whole edge on these two holes is the 40-70 % of drives that earn a go.
* **Back 18: Driver.** With a go plan it is +0.10 to +0.17 because the green is in range from most Drivers and
  from few 2-woods. Only a firm decision never to go makes it level, and then the shorter clubs are not ahead
  either (0.000 to -0.004): they are not safer there (penalty 0.6 % against 0.4 % and 0.1 %).
* **Middle 3:** level if he lays up to 90 (he can from every club), Driver by 0.07-0.08 if he advances as far as
  he can. **Middle 6:** Driver by 0.02-0.08 with a go plan, level without. **Middle 13 and 18:** Driver with a go
  plan (+0.08 to +0.19), level without (13: shorter clubs by 0.03).
* On no par 5 does a lay-up plan make the shorter club clearly right (the largest edge is 0.037). It turns the
  Driver's 0.12 into a coin flip; it does not reverse it.

Suggested page notes (wording only):

* 3: "Three-shot hole. Every yard off the tee comes off your third. Driver."
* 6 and 13: "Driver is the pick if you will go for the green in two with 240 or less to the front from the
  fairway. If you are playing it as a three-shot hole whatever happens, Driver, 2-wood and 4-wood score the same:
  hit the one you like."
* 18: "Driver puts the green in range: about 210 to the front."

## What is modelled, what is assumed, what was not done

* Modelled by the engine: dispersion, mishits, roll, lies, penalty drops, expected strokes by lie and distance.
* Assumed here: the spread of strokes after the tee shot (section B); the par-3 placeholder; independence of holes
  except in C-ii; "wild day" = 20 % of days at 1.4x width (an illustration, not a measurement of Will).
* Central world, not the book's 64-draw prior average: margins differ from the page by up to 0.015.
* Hole 10 is taken as the 4-wood (the committed book file has 2-wood by 0.012, a tie); either way it is not a
  Driver hole and plays no part in the fragility ranking.
* No published strokes-to-hole-out variance and no amateur slope data were fetched; the Tour values are the
  engine's table, the amateur source is as quoted in `spirit_hollow/research.md`.
* The hole-6 edges were moved as straight offsets of the mapped bands, not re-traced.
