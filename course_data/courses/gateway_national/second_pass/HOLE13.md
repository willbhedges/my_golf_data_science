# HOLE 13 (par 5, 533 Back): Driver or 2-wood, given the ditch on the left

Nov 13. Read-only study: no map, engine or page file changed. Single-hole runs with the C kernel, variants in memory.

## Verdict

**Driver.** Finish target is the page's: pattern centre 3 yds right of the tee line at about 286 (calm aim 3 R;
Saturday's 5 mph from the left moves the aim to about 4 L for the same finish). A ditch-shy line 2 yds further right
(calm 5 R) is free: it costs 0.001 strokes and takes the ditch from 1.9 % to 1.5 % of Drivers.

* **How much the ditch costs the Driver:** 0.4 % of Drivers in the central world, 1.9 % averaged over the 64 prior
  worlds (map shifted +/-2.5 yds, roll 0.8-1.2, pattern width, carry +/-5). Call it 1 ball in 50 to 1 in 250. A ball
  in the ditch costs 1.0 stroke more than a dry one, so the ditch is worth **0.004-0.019 strokes** on the Driver.
  The 2-wood takes that to 0.1 % but puts 1.2 % in the left pond (it has to aim 6-7 yds further left to stay out of
  the right sand), so its total penalty share is 1.7 % against the Driver's 4.0 %.
* **By how much:** 0.103 strokes (se 0.005) on the engine's scoring table, same on Saturday's and Sunday's wind.
  **That number is mostly the value of being 19 yds closer for a second shot at the green** (249 in against 268).
  If Will lays up from both spots, the edge is about zero: +0.02 to +0.03 if he goes for the green only from
  inside 240, -0.01 to +0.01 if he never goes (crude re-scoring, section 2). The 2-wood never beats the Driver by more
  than 0.01 in any of these.
* **Switch to the 2-wood when both are true:** the fairway is frozen and drives are running 40+ yds (not the usual
  25-30), and he is laying up with the second shot anyway. On roll alone the Driver holds to x1.75 (+0.04) and ties
  at x2.0 (+0.008, 12 % of Drivers in the ditch). With the 45 F noon forecast after a 24-28 F night, x1.25-x1.5 is the
  realistic worst case: Driver by 0.07-0.10 on the engine table.
* **Page note option (no banned words):** "Frozen and running 40+ yds, or laying up regardless: 2-wood, same line.
  Otherwise Driver; favour the right half."

## 1. Map check of the landing zone (looked at, not only computed)

Images (scratch, not committed):

* `/tmp/claude-0/-home-user-my-golf-data-science/3c0900e1-ef71-58c8-8d72-7f70a9ca40ad/scratchpad/hole13/h13_landing.jpg`
  : x -80..65, 232-372 yds, six panels: NAIP 2023; 2023 + zones + 6,000 Driver finishes; 2023 + zones + 2-wood
  finishes; colour infrared; 1 m lidar DEM relief; lidar height above ground.
* `/tmp/claude-0/-home-user-my-golf-data-science/3c0900e1-ef71-58c8-8d72-7f70a9ca40ad/scratchpad/hole13/h13_ditch.jpg`
  : close-up x -60..30, 275-365 with 20,000 Driver finishes.
* `/tmp/claude-0/-home-user-my-golf-data-science/3c0900e1-ef71-58c8-8d72-7f70a9ca40ad/scratchpad/hole13/h13_second.jpg`
  : 230-580 yds, the second-shot corridor and the green.

Rasters: `course_data/packages/gateway_national/imagery/naip_rgb.tif` and `naip_nir.tif` (2023, 0.3 m), `dem.tif`
(1 m), `course_data/vision_any/gateway_national/raw/hag.tif`.

Findings:

* **The mapped ditch is on the trench, full length.** The DEM trench (a clean 7-8 yd low band) lies inside the mapped
  strip from the pond corner (-42, 288) to past the footbridge (0, 343) and on to 370; the photo's pale stone channel
  runs down the middle of it. No offset larger than 1-2 yds anywhere.
* **Width, including the margin.** The photo shows a darker, longer-grass band 2-3 yds wide on each bank. The mapped
  strip (9-10 yds after the widening) covers the channel and both dark bands; its fairway-side edge sits on the outer
  edge of the dark band (at 300 yds: mapped edge x -21, channel centre x -27). The height raster shows no tall growth
  along the ditch (only the footbridge and a clump at the pond corner by the cart-path bridge), so there is no reed
  margin beyond what is mapped.
* **Top-left of the Driver pattern:** between the fairway edge (x -22 at 300) and the ditch there is 2-8 yds of rough,
  then the ditch. Nothing else is there. The cart path and its bridge (-45, 288) are left of the pattern.
* **No map error found.** Two things worth knowing, neither a ditch error:
  1. The page's "2.2 % in penalty ground" is mostly NOT the ditch. Central world, Driver at 3 R: ditch 0.35 %, left
     pond 0.53 %, right tall grass (x > 45, 240-345) 1.27 %.
  2. Right of the fairway past 345 the tall growth is unmapped (already noted in REVIEW_C). The Driver's 99th
     percentile finish is 321, so no tee ball reaches it.

## 2. Outcomes at each club's best aim

64 prior worlds x 2,048 swings, 45 F at the hole (11:50 Saturday). Saturday = 4.9 mph from 336 on a hole playing 65:
straight across from the left, 7 yds of drift; the aim moves 7 left and every number below stays within 0.1 points.
Cold numbers: Driver 267 carry + 27 roll, 2-wood 257 + 16, 4-wood 248 + 15.

| | Driver | 2-wood | 4-wood |
|---|---|---|---|
| best aim, calm / Saturday | 2.5 R / 4.5 L | 4 L / 12 L | 6 L / 14 L |
| expected strokes (engine table) | 5.094 | 5.197 | 5.225 |
| fairway | 67.6 % | 62.7 % | 71.4 % |
| rough | 21.2 % | 29.4 % | 24.7 % |
| sand | 7.2 % | 6.2 % | 3.2 % |
| ditch | 1.90 % | 0.08 % | 0.00 % |
| left pond | 0.71 % | 1.17 % | 0.55 % |
| right tall grass | 1.42 % | 0.45 % | 0.11 % |
| all penalty | 4.0 % | 1.7 % | 0.7 % |
| finish, median (10-90 %; 99 %) | 286 (260-308; 321) | 267 (250-285; 298) | 259 (243-274; 285) |
| finish 300+ / 310+ | 24 % / 7.3 % | 0.6 % / 0 % | 0 % |
| 310+ and left of the tee line | 2.7 % | 0.02 % | 0 % |
| to the pin, median (quartiles) | 249 (235-265) | 268 (258-277) | 276 (268-284) |
| leaves 240 or less / 255 or less | 35 % / 60 % | 2 % / 19 % | 0 % / 3 % |

Sunday (3.7 mph from 105, about 50 F): Driver 4.5 R, +0.104 over the 2-wood, ditch 1.3 %.

**The second shot.** Green x 0..21, 515-550. The same ditch leaves the big right pond at (22, 490), crosses in front
of the green's right half at 505-515 and runs up the green's right side at x 15-22. The pond is right of x 25 from
395 to 490. Second fairway x -40..+5 from 360 to 510, open to the green's front-left.

* From the Driver (x +3, 286): 229 to the front edge, 249 to the middle, ditch carry on the direct line about 225.
  A cold 4-wood off the deck (246 carry at best, about 260 total) reaches. So the good half of his Drivers give a
  real go, with the ditch front-right and right and the pond short-right as the miss to avoid; the safe go is at the
  front-left. This risk is NOT in the engine (it scores the second shot from a table by distance and lie).
* From the 2-wood (x -4, 267): 248 to the front, 268 to the middle. Not reachable in the cold except by 1 ball in 5.
  A three-shot hole.
* Lay-up from either spot: 150-170 yds to x -20..-5 at 430-450 leaves 90-100. The crossing ditch is 55-75 yds ahead
  of the ball (no factor); the pond edge is 25+ yds right of that target; one fairway sand patch at (-18, 468).

**What the 0.10 is made of (crude).** Same balls, non-penalty lies re-scored with a table that goes flat beyond a
"can't reach" distance (my assumption: 0.001-0.002 strokes a yard for a longer lay-up, against the engine's 0.0054):

| second-shot world | Driver over 2-wood | Driver over 4-wood |
|---|---|---|
| engine table | +0.103 | +0.131 |
| goes for it from 240 or less, lays up otherwise | +0.019 to +0.033 | -0.008 to +0.015 |
| goes from 225 or less | -0.002 | -0.030 |
| never goes | -0.007 to +0.012 | -0.037 to -0.009 |

So Driver is right if he will take the green on from about 240 and in. If the plan is three shots whatever happens,
the three woods are level and the 4-wood (71 % fairway, 0.7 % penalty) is the quiet choice.

## 3. Stress of the Driver pick (engine table, all clubs re-aimed in each case)

| case | Driver over 2-wood | Driver ditch share | best Driver aim | 2-wood ditch |
|---|---|---|---|---|
| base | +0.103 | 1.9 % | 2.5 R | 0.1 % |
| a. ditch 5 yds closer | +0.080 | 3.2 % | 6 R | 0.2 % |
| a. ditch 10 yds closer | +0.057 | 4.6 % | 8.5 R | 0.5 % |
| a. ditch 15 yds wide | +0.077 | 3.5 % | 6 R | 0.2 % |
| a. 10 closer and 15 wide | +0.033 | 5.9 % | 11.5 R | 1.0 % |
| ditch 20 / 30 / 40 closer | +0.022 / +0.005 / -0.007 | 6.7 / 7.7 / 8.4 % | 13 / 17 / 20.5 R | 1.4-1.7 % |
| b. roll x1.25 | +0.097 | 3.2 % | 5 R | 0.1 % |
| b. roll x1.5 | +0.080 | 5.2 % | 7 R | 0.3 % |
| b. roll x1.5, rough holds half as well | +0.071 | 6.6 % | 9.5 R | 0.7 % |
| b. roll x1.75, same rough | +0.042 | 9.2 % | 11.5 R | 1.3 % |
| b. roll x2.0, same rough | **+0.008** | 11.7 % | 13.5 R | 2.0 % |
| b. roll x2.5, same rough | -0.060 | 16.3 % | 17 R | 4.4 % |
| c. 65 F, full distance | +0.109 | 2.8 % | 7.5 R | 0.3 % |
| d. pattern 15 % wider | +0.097 | 2.0 % | 3.5 R | 0.1 % |
| e. miss centre 5 left, known (he re-aims) | +0.103 | 1.9 % | 7.5 R | 0.1 % |
| e. centre 5 left, NOT known (plays the page aims) | +0.102 | 2.8 % | (page aim) | 0.15 %, pond 2.3 % |
| e. centre 10 left, not known | +0.103 | 3.8 % | (page aim) | 0.2 %, pond 4.2 % |
| f. roll x1.5 (rough half) + 65 F | +0.064 | 8.1 % | 13 R | 1.5 % |
| f. roll x1.5 (rough half) + ditch 10 closer | +0.023 | 9.9 % | 13.5 R | 2.1 % |
| f. roll x1.5 (rough half) + 15 % wider + 5 left | +0.053 | 8.2 % | 14 R | 0.8 % |
| f. roll x1.5 (rough half) + ditch 10 closer and 15 wide | **+0.002** | 11.0 % | 16 R | 2.9 % |
| f. roll x2.0 (rough half) + 65 F | **+0.002** | 13.0 % | 16.5 R | 3.0 % |
| f. roll x1.5 + 65 F + ditch 10 closer and 15 wide | **+0.003** | 12.9 % | 18.5 R | 3.8 % |
| f. everything at once (roll x2, 65 F, 10 closer, 15 wide, 15 % wider, 5 left) | -0.076 | 20.3 % | 26 R | 7.6 % |

A left miss he does not know about leaves the margin where it is because the 2-wood's line is already 6-7 yds further
left and it finds the pond.

**Break-even.** A ditch ball costs 0.98-1.07 strokes more than a dry one. The 2-wood draws level when the Driver
puts **about 11-13 % in the ditch** (now 0.4-1.9 %), in every route to it: roll x2.0 on its own; roll x1.5 with a map
that is wrong by 10 yds AND 6 yds of width; roll x2.0 at full summer distance. A map error alone needs the ditch 30+
yds closer than the photo and the lidar put it. On the "lays up anyway" scoring the starting margin is about zero,
so there any extra run (x1.25 and up) tips it to the 2-wood or 4-wood.

## 4. A better Driver aim? And is the 2-wood short of the trouble?

Driver, calm, fixed aims (prior-averaged):

| aim | strokes | ditch | left pond | right tall grass | sand | fairway |
|---|---|---|---|---|---|---|
| 0 | 5.097 | 2.3 % | 1.0 % | 1.1 % | 6.5 % | 66.5 % |
| 3 R (page) | 5.094 | 1.8 % | 0.7 % | 1.5 % | 7.3 % | 67.8 % |
| 5 R | 5.095 | 1.5 % | 0.5 % | 1.9 % | 7.8 % | 68.1 % |
| 6 R | 5.097 | 1.4 % | 0.5 % | 2.1 % | 8.0 % | 68.2 % |
| 8 R | 5.102 | 1.1 % | 0.4 % | 2.7 % | 8.3 % | 68.1 % |
| 10 R | 5.110 | 0.9 % | 0.3 % | 3.3 % | 8.6 % | 67.7 % |
| 15 R | 5.144 | 0.6 % | 0.1 % | 5.7 % | 9.0 % | 65.2 % |

The curve is flat from 0 to 6 R (0.003). 5 R is the ditch-shy line at no cost; past 8 R every ditch ball saved is paid
for with two in the right tall grass, which is also a penalty.

The 2-wood: he is right about the sand. On the Driver's line (3 R) the 2-wood finishes in sand 9.7 % of the time
against the Driver's 7.3 % (10.4 % against 7.6 % in the central world): its 257 carry lands beside the last two
patches (238-268), which the Driver's 267 flies. To get away from them its best aim is 4 L, and from there 1.2 % go
in the left pond. It is short of the ditch (0.1 %), not short of trouble.

## What is crude

* Ditch share: 0.35 % (central world, fixed map) to 1.9 % (prior average with the map jittered 2.5 yds). The truth
  is in that range; the stress table uses the high end.
* Roll is a fixed number per swing +/-25 %, cut to 0.3 in rough; no bounce or slope model. "Rough holds half as well"
  is rough roll 0.6, my stand-in for frozen ground.
* The lay-up re-scoring in section 2 is a post-hoc change of the table for fairway / rough / sand balls at the
  engine's aims; penalty balls keep the engine's cost. The second-shot hazards by the green are described from the
  photo, not simulated.
* Regions: "ditch" = penalty ball at 281+ yds with x between -47.5 and +33; "right tall grass" = x > 33; the rest is
  the left pond.
