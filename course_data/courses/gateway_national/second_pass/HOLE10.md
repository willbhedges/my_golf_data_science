# Gateway National, hole 10: the ditch beside the green (Nov 13 2026)

Will's question on the page photo of 10 (Back, 271 yds, 2-wood at the green): "this decision can't be right as there's
a creek there, and that would be a lot of penalties".

**Short answer.** The dark line is a real ditch with water in it, and it was already in the map as a penalty area, but
as a strip 2.3-2.8 yds wide; the trench is 3.5-5 yds wide. The map is now corrected (commit with this file). With the
ditch at its true width the play does not change: **2-wood at the green, aim 20 yds left of the tee line (was 17.5),
about 11.5 left in Saturday's 5 mph wind from the right (was 10)**. About 1 ball in 10 finishes in the ditch (was
priced as 1 in 15). Laying up is 0.35-0.45 strokes worse; the 4-wood at the green is 0.045 worse.

Frame: x = yds right of the Back tee line (negative = left), along = yds from the Back tee. Green centre (-18.5, 270).

## 1. What the line is (pictures looked at)

Renders, all in the hole frame with the map zones drawn on top (scratch, not committed):
`look_plain.png` / `look_zones.png` (195-335 yds, x -60..+40: NAIP 2023 RGB 0.3 m, NAIP 2023 colour-infrared, NAIP
2022, lidar), `zoom_plain.png` / `zoom_zones.png` / `zoom_after.png` (225-315 yds, x -30..+15 at 13 px / yd: RGB, CIR,
Dec 2020 lidar ground), cross-sections every 5 yds (`prof.py`) and a wall / bank trace every 2 yds (`trace_ditch.py`).

* **NAIP 2023 RGB / CIR, NAIP 2022:** a straight dark line leaves the pond's corner at the footbridge (x -14, 234 yds),
  runs up the right edge of the green and goes under the cart path at 308 yds. It is the same line in 2022 and 2023,
  black in colour-infrared (water or deep shadow), about 1 yd wide at x -9.5..-8.5 from 255 to 300 yds. Right of it a
  2-3 yd olive band (the ditch floor and bank face), then a tufted lip at x -6..-5, then plain rough up to the fairway
  that passes right of the green.
* **Lidar ground (USGS 3DEP, flown 2 Dec 2020, 0.5 m grid):** a trench. The green side is a vertical wall: the ground
  drops 4.0-4.8 ft within 1 yd. The floor is 1.5-3 yds wide. The right bank climbs 2.5-3 ft in the first 1.5-2 yds
  (40-50 % slope), then eases to 10-20 % for about 10 more yds. **There are no lidar returns on the floor** (near-infrared
  laser absorbed): standing water in December 2020. So: a wet drainage ditch from the pond to the culvert, not a shadow
  and not a path edge.
* **Size and place** (lidar wall to the top of the steep bank, every 2 yds, 238-308):

| along | wall (green side) x | bank top x | width | depth below the green side |
|---|---|---|---|---|
| 240 | -13.1 | -8.4 | 4.8 | 4.1 ft |
| 250 | -9.1 | -5.9 | 3.2 | 4.4 |
| 260 | -8.9 | -5.1 | 3.8 | 4.4 |
| 270 | -7.6 | -4.9 | 2.8 | 4.3 |
| 280 | -8.4 | -4.9 | 3.5 | 4.2 |
| 290 | -8.6 | -4.6 | 4.0 | 4.6 |
| 300 | -8.9 | -3.9 | 5.0 | 5.8 |

  Median 3.8 yds (2.5-5.0). On the photo the wall's dark line sits 0-2 yds (median 0.6) left of the lidar wall, i.e.
  at x -9.5; the two sources agree to about 1 yd. The mapped green's right edge is x -9.2..-9.9 and the photo green ends
  at about -10.5 (F2: "the ditch is 1-2 yds off the right edge"): the wall is 1-2 yds from the putting surface.
* **Relative to the shots.** The green centre is 9-11 yds left of the wall. The ditch runs the whole length of the
  2-wood and 4-wood finishing zones (2-wood finishes 247 / 266 / 279 yds at the 10th / 50th / 90th percentile, 4-wood
  238 / 254 / 270). The fairway that the lay-up uses passes right of the ditch (its left edge is 8-12 yds right of
  the bank top at 240-265) and ends at 277; a ball right of the ditch must pitch back over it.

## 2. How it was mapped

`truth/package.json`, hole 10: one OSM `water` polygon = the pond (50-222 yds, left) plus a thin tail up the ditch to
330 yds. Zone order: fairway, then water, then sand, so nothing paints over it; the green's putting value only applies
to fairway / rough cells, so water cells inside the green outline stay water. In the engine's 0.5-yd raster the cells
along it were `water` at x -7.0..-5.0 (245-295 yds: 2-3 yds), with `rough` on both sides (the 1.5-2 yds between the
mapped green and the strip, and the right bank).

So: right kind (penalty: 1 stroke + a shot from rough at the point the ball crossed in), right place (inside the
trench, on its right half), **too thin**: 2.3-2.8 yds against 3.5-5. The missing part is the 1-2 yds on the green
side, which were priced as greenside rough.

F2's note "narrow ditches (10 beside the green ...) not detectable; mapped lines kept" was about its vegetation-height
method; the lidar ground shows this one plainly.

## 3. What the engine does with it (Back, calm, 43.6 F)

Harness: the engine's `decide.bayes` (64 prior draws x 1,024 swings, fast kernel) for the pick, aim and margin; shares
at each club's best aim in the central world (20,000 swings). Ditch variants were painted in memory.

| ditch in the map | pick, aim | margin over 4-wood | in the ditch / pond: 2-wood | 4-wood | Driver | 2-wood strokes |
|---|---|---|---|---|---|---|
| true width - 1 yd each side (~2 yds) | 2-wood 17.5 L | 0.056 | 5.1 % | 6.9 % | 4.5 % | 3.607 |
| **before: OSM strip 2.3-2.8 yds** | 2-wood 17.5 L | 0.053 | 6.5 % | 8.2 % | 6.7 % | 3.624 |
| lidar wall to bank top (median 3.8 yds) | 2-wood 19.5 L | 0.045 | 8.2 % | 8.9 % | 8.1 % | 3.682 |
| the same, moved 1 yd left (photo line) | 2-wood 19 L | 0.050 | 8.7 % | 9.7 % | 8.4 % | 3.658 |
| **after (committed): photo wall to lidar bank top, 3.5-5.5 yds** | 2-wood 20.5 L | 0.046 | 9.7 % | 10.8 % | 9.6 % | 3.701 |
| true + 1 yd each side (~6 yds) | 2-wood 20.5 L | 0.037 | 11.3 % | 11.2 % | 11.1 % | 3.713 |
| true + 2 yds each side (~8 yds: every ball on the steep bank rolls in) | 2-wood 21.5 L | 0.026 | 14.2 % | 12.3 % | 13.6 % | 3.749 |

"With bank rough" is the default in every row: the ground beside the ditch is rough. One more run priced a 3-yd strip
along the right lip as a penal lie (the engine's "sand", as on 16's mound) on top of the +1 row: 2-wood 20 L, margin
0.044, strokes 3.690 (a penal lie stops the ball, so fewer run into the water; not a worse case than the +2 row).

The other clubs, on the corrected map (they do not change with the ditch width):

| option | aim | expected strokes | vs the 2-wood | where it finishes |
|---|---|---|---|---|
| 2-wood at the green | 20.5 L | 3.701 | - | 32 % on the green, 20 % inside 10 yds of the hole; 9.9 % wet (9.3 % in the ditch, 0.6 % in the pond); 16 % dry but right of the ditch; 5 % sand; 1.6 % long grass |
| 4-wood at the green | 23 L | 3.748 | +0.046 | 26 % on the green; 10.5 % wet (8.2 % ditch, 2.3 % pond: it is shorter, so more balls stop level with the pond's end); 10 % sand |
| Driver | 17 L | 3.884 | +0.18 | runs through: 69 % rough, 9.6 % wet, 2.7 % long grass |
| Long iron lay-up | 8.5 R | 4.045 | +0.34 | fairway right of the ditch, 66 yds left; 8.9 % in the 198-yd bunker |
| Mid iron lay-up | 2.5 L | 4.080 | +0.38 | fairway, 88 yds left (97 % fairway, 0.2 % wet) |
| 8-iron lay-up | 4.5 L | 4.153 | +0.45 | fairway, 111 yds left |

Why going for it still wins: a ball in the ditch costs 1.37 strokes more than a dry one (3.87 against 2.50 strokes
after the tee shot). One ball in ten wet is 0.14 strokes per round. The lay-up gives up 0.38: from 88 yds on the
fairway a 5-handicap takes about 3.08; from where the 2-wood finishes (median 19 yds from the hole, a third of them
putting) he takes about 2.50 when dry. For the mid-iron lay-up to break even, close to 4 balls in 10 would have to
find the ditch.

Wind line (the page picture Will saw): with 5 mph from the right the ball drifts about 8 yds left, so the aim line is
drawn 8 yds right of the calm aim, which puts the line itself on the green's right edge, 1-2 yds from the ditch. If
the wind is not there and he still aims there, the calm cost is +0.04 strokes (2-wood 3.742 at 11.5 L against 3.703
at 20 L); if it blows 10 instead of 5, about +0.03. The line looks worse than it is.

## 4. The fix

`course_data/truth/gateway_national/trace.py`: `LATE["10"]`, one `water` polygon, 236-308 yds, left edge = the lidar
wall moved 1 yd left to the photo's wall line (clipped at the mapped green's edge, x -9.9), right edge = the lidar
bank top. 3.5-5.5 yds wide. The OSM strip stays (union). Applied with `opt/map_edits.py <old trace.py> --holes 10`
(`hand_zones_ll.json`: hole 10 13 -> 14 zones; `truth/package.json`: only hole 10's `zones_ll` differs), then
`truth/course.py` and `truth_middle/course.py` rewritten with `product.load` + `write_module` (no screenshots).
Checked on `zoom_after.png`: the polygon covers the photo's dark line and the lidar trench from the footbridge to the
culvert; raster water at 250 / 260 / 270 / 280 / 290 / 300 yds: x -10.0..-6.5, -9.5..-5.5, -8.5..-4.5, -8.5..-5.0,
-9.0..-4.5, -9.5..-4.0.

Not changed: the green outline (F2: 1.5-2 yds narrower on the right; its right edge now touches the water zone), the
right bank (rough).

## 5. Before / after (fast solver, `--holes 10 --card-only`, 64 draws; wind cells 8,192 swings)

| case | before | after |
|---|---|---|
| **Back, calm book (43.6 F)** | 2-wood 17.5 L, 0.057 over 4-wood (book 256 draws: 17.5 L, 0.053) | **2-wood 20 L, 0.045 over 4-wood** (se 0.015) |
| Back, share in water at the pick | 6.7 % | 10.0 % |
| Back, 5 mph from the right (Saturday: NNW, 84 deg off the line), 50 F cell | 2-wood 10 L, 0.018 | **2-wood 11.5 L, 0.013 over 4-wood (14 L)** |
| the same, 35 F cell | 2-wood 10.5 L, 0.107 | 2-wood 11.5 L, 0.095 |
| Back, calm cells 35 / 50 F | 2-wood 18.5 L / 18.5 L (0.109 / 0.019) | 2-wood 19.5 L / 20 L (0.102 / 0.013) |
| Back, firm ground roll x1.25 (central world, 16,000 swings) | 2-wood (0.019) | 2-wood 19 L, 0.014 over 4-wood |
| Back, frozen ground roll x1.5 | 4-wood 21.5 L (0.015) | **4-wood 22 L, 0.018 over 2-wood** (pill still right) |
| **Middle, calm book** | 4-wood 16 L, 0.215 over 2-wood | **4-wood 18.5 L, 0.207 over 2-wood** |
| Middle, share in water at the pick | 5.5 % | 8.3 % |
| Middle, 5 mph from the right, 35 / 50 F cells | 4-wood 8 L / 8.5 L | 4-wood 10.5 L / 10 L (0.171 / 0.214) |
| Middle, roll x1.25 / x1.5 | 4-wood | 4-wood 17.5 L / 18 L (0.189 / 0.161) |

Saturday 11:06 (44 F, 5 mph NNW) sits between the 35 and 50 F cells: Back 2-wood about 11.5-12 L, margin over the
4-wood about 0.05; at 50 F and warmer the two clubs are a toss-up, as before.

## 6. Left for the manager

* The committed `truth/v2` and `truth_middle/v2` decisions, wind grids and the page for hole 10 are from the old map:
  re-solve hole 10 (Back and Middle; the fast solver's `--holes 10` merges into an output folder) and rebuild the page.
  No whole-course solve was run here and the page was not rebuilt.
* OPTIMIZE.md's check table says "10: 2-wood, 17-21 L, 0.060": now 20 L, 0.045.
* The other tee sets' grids for 10 (offsets) were not re-solved here.
* Not done: the ditch continues past the cart path (310-330, OSM strip kept); the green outline's right edge.

## 7. Strategy pass, Nov 13: Will's drawings, the evidence per area, three solves (strategy lead)

Will marked the page picture of 10 twice (uploads `7323133a-image.jpg`: the band between the ditch and the right
fairway, "this is all penalty area in that native as well"; `01e42326-image.jpg`: every dead area round the green:
behind it to the cart path, left / back-left behind the bunkers, the whole right side to the cart path, the ditch
line down to the pond and the pond block). He then said of the right side "there might not be native grass on that
right side ... use the lidar ... I could be wrong" and of the band "double check some of this too". His standing
rule: tall native in which a ball cannot be found is penalty area (config `engine.native_penalty_area: relief`:
one stroke + a shot from rough where the ball crossed the edge).

Evidence per area (Dec 2020 lidar standing-grass height on the 0.5 m grid: median, share of cells over 0.10 m;
Sentinel-2 NDVI of 8 / 10 Nov 2026; NAIP Aug 2023 texture. References on this hole: fairway 0.01 m, 0 %, NDVI 0.86,
texture 2.5; mapped tall grass far left 0.07-0.11 m, 44-51 %, NDVI 0.55-0.59, texture 8-9):

| area of his drawing | lidar grass | NDVI Nov 2026 | call | sure | map |
|---|---|---|---|---|---|
| behind the green, 299-305 to the cart path | 0.14 m, 56 % | 0.61 | penalty native | 90 % | was mapped (from 298-300); the 293-298 strip is mown (0.01 m): surround |
| left / back-left behind the greenside bunkers | 0.11 m, 51 % | 0.56-0.64 | penalty native | 85 % | the 6-8-yd rough gap between the bunkers and the tall grass at 255-296 is closed (`EXTRA["10"]`, new strip) |
| ditch line short-right, down to the pond | trench, no ground returns | - | water | 95 % | mapped (section 4) |
| bottom-left block | pond; brush left of it 0.13 m at p75, 31 % | 0.58 | water / penalty native | 95 % | was mapped |
| band between the ditch and the right fairway, 226-272 | 0.01 m, 0 % | 0.86-0.87 | reads as mown rough | 80 % | kept as penalty (his first drawing; low-regret, below) |
| right of the green past the fairway's end to the cart path, 276-300 | 0.01 m, 0 % | 0.85-0.88 | reads as mown rough | 80 % | not mapped as penalty; changes nothing (outside both ovals) |

Three solves (Back; book = 64 prior draws, the rest the central world on 16,000 swings):

| map | calm pick | strokes | penalty share 2-wood / 4-wood | go over the best lay-up (long iron, right fairway) | dispersion +15 % | frozen ground | both |
|---|---|---|---|---|---|---|---|
| (a) ditch only on the right; tall grass left / behind | 2-wood 19.5 L, 0.045 over 4-wood | 3.69 | 12 % / 12 % | 0.41 | 0.38 | 4-wood 22 L, 0.33 | 0.31 |
| (b) his first band + (a) elsewhere (**published**) | 2-wood 25.5 L, 0.010 over 4-wood (27 L): a coin flip | 3.79 | 20 % / 16 % | 0.29 | 4-wood 26 L, 0.23 | 4-wood 27.5 L, 0.26 | 0.20 |
| (c) his full drawing | 2-wood 26 L, 0.005 over 4-wood | 3.80 | 20 % / 16 % | 0.29 | 0.23 | 0.25 | 0.20 |

Middle: 4-wood in all three: (a) 18 L, 3.65, go by 0.31; (b) 21 L, 3.72, go by 0.24 (frozen 0.10); (c) 23 L, 3.73,
go by 0.25 (frozen 0.13).

Why going at the green survives even the worst-case map: a ball in a penalty area costs 3.95 strokes after the tee
shot, a dry one 2.48 (44 % putting or chipping from short grass 2.19, 20 % greenside rough 2.76, 6 % sand 2.87), the
lay-up's wedge from 66-88 yds 3.03-3.07. **Break-even: about 40 % of tee balls in the penalty area; he is at
12-20 %.** There is no lay-up left: left of the fairway is the pond (160-222), then the green complex.

Aim regret (2-wood): aiming 26 L when the band is really mown costs 0.025 strokes; aiming 19.5 L when the band is
really dead costs 0.05; 24 L costs at most 0.011 either way. Hence map (b) on the page: aim at the left half of
the green, and the 4-wood when the two woods are within the tie band (4 points fewer penalty balls).

## 8. Nov 13 afternoon: played the hole

Will, after a practice round: "It matches what the LiDAR says as far as all the data stuff", then "Hole 10 it is clear
on the right, just some brush around the creek, but sort of accounted for." So the right side is section 7's map (a).

Map (commit 0061ee7b2; only hole 10's zones differ in `hand_zones_ll.json`, `truth/package.json`, both course modules):
* the band between the ditch and the right fairway (his first drawing) is removed: mown rough. Right of the green to
  the cart path was never mapped dead. The ditch polygon (photo wall to lidar bank top, 3.5-5.5 yds) is kept as it is:
  on NAIP 2023 it covers the dark line, the olive bank and the tufted lip; no brush shows outside it.
* the tall grass on the left now comes up to the outer lip of the two upper left greenside bunkers (edge moved 2-6 yds
  toward the green at 266-297; the map had a 1-2 yd strip of rough between sand and tall grass there, the photo none).
* config: `engine.tall_grass_alt.also_ll` (the band counted as tall grass for the Lost ball switch) removed.

Re-solve (commit 281442149): hole 10 only, book + card grid + every offset grid, 128 draws, both rule sets, merged
into `truth/v2`, `truth/v2_lost`, `truth_middle/v2`, `truth_middle/v2_lost` (every other hole's records identical).
Lay-up grid (`opt/layup10.py grid --kernel`, both rule sets) re-run.

| calm book | before | after |
|---|---|---|
| Back, Drop | 2-wood 26 L, 0.012 over 4-wood, 3.79, 19 % dropped, best iron +0.25 | **2-wood 20 L, 0.042 over 4-wood, 3.71, 12 % dropped, long iron +0.34, 8-iron +0.45** |
| Back, Lost ball | 4-wood 29 L, 0.034 over 2-wood, 3.88 | 2-wood 18.5 L, 0.033 over 4-wood, 3.72, long iron +0.32, 8-iron +0.43 |
| Middle, Drop | 4-wood 23 L, 0.229 over long iron, 3.73, 14 % | 4-wood 18.5 L, 0.205 over 2-wood, 3.66, 10 %, long iron +0.27, 8-iron +0.41 |
| Middle, Lost ball | 4-wood 23.5 L, 0.167 over long iron | 4-wood 17 L, 0.251 over long iron, 3.68 |

On the page (forecast cells, 9:00 start, hole 10 at 11:06), Drop / Lost ball:

| tee | Saturday | Sunday | calm 44 F |
|---|---|---|---|
| Back | 2-wood 12 L, 4-wood +0.059 / 2-wood 11 L, +0.053 (was 4-wood 20 L on the level rule) | 4-wood 25 L, 2-wood +0.063 / +0.064 (was 30 L) | 2-wood 20 L, +0.046 / 18 L, +0.042 |
| Middle | 4-wood 10 L / 9 L (was 15 L) | 4-wood 22 L / 20 L (was 27 L) | 4-wood 19 L / 17 L |
| The Tips, Champions | Driver 17 R, 2-wood +0.028, 4-wood +0.031 / 4-wood 17 R on the level rule | 4-wood 7 R / 6 R, Driver level | 4-wood 9 R, Driver level |
| Forward | long iron 15 L (was 17 L) | 25 L (was 28 L) | 22 L |

Going at the green over the best iron to the right fairway: Back 0.38-0.39 (was 0.26-0.31), Middle 0.31 Saturday and
0.17 Sunday (was 0.26 / 0.14).

Page words: the level rule on 10 (4-wood shown when within 0.03) no longer fires for Back at the forecast (the
2-wood leads by 0.05-0.06 Saturday, the 4-wood wins Sunday outright); it is kept for warmer cells and for the back
tees, where the three woods to the right fairway are within 0.03, with a general text ("The woods are level here:
the 4-wood is the straighter one"). Why line: "about 7 balls in 8 ... about 0.4 strokes" (Middle: 9 in 10, 0.3), the
same in both rule sets. The Tips / Champions pill names no club ("a wood at the right fairway"). Lay up mode now
stars the 4-wood to the right fairway (15 R Saturday, leaves 27, about 0.2 behind going at the green): with the right
side mown a wood there loses nothing; the irons follow (long iron +0.18, mid iron +0.21, 8-iron +0.29 behind it).
