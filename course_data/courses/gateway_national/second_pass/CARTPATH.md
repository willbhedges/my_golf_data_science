# Gateway National: cart paths in the tee-shot pattern (study, 2026-11-13)

Question (Will): "if there's a cart path in the dispersion, a ball that lands there is going to hit it and bounce."
Read-only study on the published state (2fede0ff8), run in a sparse worktree; nothing in the engine or the page was
changed. Scripts and images stay in the session scratchpad (`cartpath/`: geo.py, snap.py, xs2.py, eng.py, shares.py,
bounce.py, img/).

## Verdict

**Note for later, not a change before Saturday.** No club changes and no aim moves by 2 yds on any of the 13 tee
shots, Back or Middle, with a cart-path bounce added (central and a deliberately strong version). The most a path
does to the picked club is +0.008 strokes (1 Middle) and -0.007 (11 Middle, where the bounce helps). The reason is
simple geometry: every path is 24-57 yds from the picked landing point, a path is 3 yds wide, so only 0-2 % of tee
balls land on one, and those balls were already headed for the rough or the tall grass beyond it.

- Is the premise true? Yes. The engine has no cart-path lie. Lies are rough, fairway, first cut, sand, trees,
  tall grass, water, OB, unverified (`spirit_hollow/v2/model.py` LIES); the truth map (`truth/course.py`,
  `truth/package.json`) has no path zone; `course_data/truth/gateway_national/trace.py` only uses the paths as
  landmarks in comments ("prairie left of the cart path"). A ball on a path today is scored as the zone around it
  (rough, or the tall-grass block the path runs along).
- Holes where a path is inside the pattern at all (>= 0.5 % of balls land on it): **1, 2, 3, 8, 11** (1-2 %), 5, 9,
  13 (0.5-0.8 %). Under 0.4 %: 6, 15, 16, 18. None: 10.
- Reverse framing (shade the aim away from the path): never pays. 3 yds away costs 0.001-0.008, 5 yds away costs
  0.003-0.023, with the bounce switched on, on every hole.
- No page change recommended. If a line is wanted anyway, the only two holes where it is worth a glance:
  - 1 (both tees): "Cart path runs down the left edge 45 yds left of centre; a ball on it kicks on left. Keep the line."
  - 11 (both tees): "Cart path right is a friendly kick: a ball on it runs on down the right side."

## 1. What was mapped and how each feature was identified

Source: cached OSM (`course_data/packages/gateway_national/raw/osm.geojson`: 23 `golf=cartpath` ways, 53 service
ways). OSM was used only as a first guess. Every segment was then (a) snapped to the pale strip on the NAIP 2023
photo (0.3 m) by a cross-section every 2 yds (peak of min(R,G,B) within 5 yds, width at half height), (b) checked on
the 2019/2020 lidar ground (lowest point within 3 yds of the centre line against the lower shoulder 5-8 yds out), and
(c) looked at: one photo / OSM / lidar-relief panel per hole (150-350 yds) and one zoomed crop per hole with the
traced edges drawn on it. OSM was 0-1.4 yds off the photo strip (median per segment); the snapped line is used.

What separates a path from a ditch here, measured:

| | cart path (22 segments) | ditch / creek (10 creek, 13 two ditches, 9 left) |
|---|---|---|
| photo colour (mean R,G,B) | pale grey 185-203 / 182-198 / 171-191 (9 under trees: 159/156/139) | dark or brown-green 133-157 / 140-156 / 96-122 |
| width | 3.0-3.2 yds at half height, p10-p90 2.8-3.8 (true width about 2.5-3: the 0.3 m pixel blurs the edge) | 2.5-5 yds, variable |
| lidar: lowest point below the lower shoulder | median -0.5 to +0.2 m (at or above grade); two in a shallow swale, see 1 and 18 left | 10: 1.2 m (max 1.5); 13 south of the pond 0.9 m; 13 north-east 0.5-0.6 m; 9 left up to 0.9 m |
| shape | constant width, smooth curves, joins tees / greens / other paths | follows the low ground, ends in a pond |

### Linear features near each landing zone (Back frame: x = yds right of the tee line, y = yds from the Back tee)

| hole | feature | class | evidence | confidence |
|---|---|---|---|---|
| 1 | left, x -60 (y 200) -> -45 (260) -> -38 (300) -> -34 (340) | **cart path** | pale 3.0-yd strip, 100 % of sections on the photo; lies in a 0.3-0.5 m swale at the foot of the tall-grass berm (one side higher, not a trench); Will's reference case | high |
| 1 | right, pale strip x 57-65 and another x 85+ | road / gravel shoulder outside the course | 8 yds wide, straight, OSM `unclassified` road at x 66; lidar flat | high (not a path; not modelled; 65+ yds right of the aim) |
| 2 | right, x 49 (200) -> 52 (235), then two branches: main path x 46 (240) -> 41 (260) -> 43 (280) -> 54 (320); spur x 60 (260) -> 75 (280) to the buildings | **cart path** (main) / gravel spur | pale 3.0 yds, 92-100 % confirmed, at grade (-0.1 m) | high |
| 3 | left, x -46 (200) -> -47 (240) -> -40 (280) -> -35 (340) | **cart path** | grey 3.0 yds, 99 %, at grade | high |
| 3 | left, faint two-track joining at (-48, 250) from the west | maintenance track (dirt) | brown, not uniform | medium; not modelled |
| 3 | right, brown line x 31-40 along the tree line | berm / bare strip, not a path | lidar: on the side of a 1 m ridge, no channel (max 0.37 m); brown, B 89 | medium (not a path: high; what it is: unsure) |
| 3 | right, x 45+ | service road in the yard beyond the trees | OSM service; off the course | high |
| 5 | right, x 62 (200) -> 53 (240) -> 43 (280) -> 35 (320) | **cart path** | pale 3.2 yds, 100 %, at grade | high |
| 5 | right, x 84 (200) -> 73 (260) -> 61 (320), with two cross links | cart path of the next hole | same look | high |
| 6 | right, x 41 (200) -> 51 (240) -> 63 (275) then turning left across the hole: 55 (300), 40 (320), 22 (340) | **cart path** | pale 3.2 yds, 100 %, at grade | high |
| 6 | right, second strip x 63 (200) -> 90 (260) | cart path of the next hole | same | high |
| 6 | right, brown curved strip x 73-79, y 280-315 | bare ground on the berm | no channel (0.14 m max); brown | medium; unsure what it is, 70 yds right of the aim |
| 8 | left, x -58 (200) -> -62 (230) -> -75 (260) -> -90 (270), and across the hole at y 155-165 (x -30..+50) | **cart path** | pale 3.0 yds, 100 %, at grade | high |
| 8 | far right, pale track x 80-92 with a channel beyond it | farm / levee track + ditch | track on a ridge; the ditch beyond is in the truth map as water | high |
| 9 | right, x 44 (200) -> 49 (240) -> 54 (280) -> 52 (320) | **cart path** | 73 % confirmed (y 200-235 under the tree edge), 2.8 yds, at grade (+0.2 m) | medium-high (line under the trees is interpolated) |
| 9 | left, (-88, 228) -> (-45, 300) -> (-35, 340) | ditch (with a footbridge at -88, 228) | channel up to 0.9 m, green-brown, feeds the pond | high; already water in the truth map |
| 10 | right, x 40 (200) -> 48 (260) -> 46 (280), then left over the bridge at (-8, 308) and on to (-62, 340) | **cart path** | pale 3.0 yds, 96-100 %, at grade; bridge visible | high |
| 10 | dark line x -12 (230) -> -6 (305) right of the green | **creek, not a path** | 1.2 m channel (max 1.5), dark, 2.5-5 yds; Will's reference case | high; already water in the truth map (correct) |
| 10 | right, second strip x 65-76 | cart path of the next hole | same look | high |
| 10 | right, faint track (35..50, 290..310) | worn dirt track | not uniform | low importance |
| 11 | right, x 35 (200) -> 43 (240) -> 55 (280) -> 72 (320) | **cart path** | pale 3.2 yds, 100 %; in a slight swale (median 0.15 m, max 0.6 at one spot) | high |
| 13 | left, x -44 (200) -> -40 (240) -> -37 (260) -> -40 (280), bridge at (-45, 288), then -48 (300) -> -62 (340) | **cart path** | pale 3.0 yds, 100 %, slightly ABOVE grade (+0.2 to +0.4 m) | high |
| 13 | grey-brown strip (-42, 290) -> (0, 345) | **ditch, not a path** (looks like a path on the photo) | lidar channel 0.5-0.6 m, ends in the pond, bridge at (0, 343) | high; already water in the truth map (correct) |
| 13 | channel x -47..-50, y 150-215, into the pond | ditch | 0.9-1.0 m channel | high; already water |
| 13 | right, x 63 (200) -> 75 (260) -> 78 (320) | cart path | 100 % | high (60+ yds right of the aim) |
| 15 | right, x 81 (200) -> 68 (240) -> 55 (280) -> 44 (300) -> 38 (340) | **cart path** | pale 3.2 yds, 100 %, at grade | high |
| 15 | left, x -80..-65 | cart path | 100 % | high (80 yds left of the aim) |
| 16 | right, x 50 (200) -> 55 (240) -> 50 (280) -> 45 (320) | **cart path** | 83 % (y 245-270 dull), 3.2 yds, at grade | high |
| 18 | left, x -46 (200) -> -48 (240) -> -58 (260) -> -73 (280) -> -89 (300) | **cart path** | pale 3.0 yds, 100 %; shallow swale at the foot of the berm (0.3-0.5 m, one-sided) | high |
| 18 | right, x 46 (200) -> 54 (240) -> 60 (260) -> 55 (300) -> 61 (340) | **cart path** | 69 % confirmed (rest under the tree edge); +0.3 m above grade | medium (OSM here is one straight line; the snapped line follows the visible strip, the hidden part is interpolated) |

Unsure, listed rather than guessed: the brown strips right of 3 and right of 6 (not paths, not channels; bare berm
ground or an old track), and the exact line of the 9 and 18 right-hand paths where the tree edge hides them
(position good to about 3 yds).

### Truth-map classification errors found

- **18, far left: a cart path is mapped as water.** The "water" strip at x -92..-110, y 297-372 lies exactly on the
  paved path (pale 3-yd strip, lowest point 0.10 m below the shoulder, no channel). This is reviewer C's 18-B. The
  real channel there is further on, at y 380-392 (1 m+ trench, mapped). 60+ yds left of every Driver pattern, so no
  pick depends on it. Recommend removing that strip when the map is next touched.
- No ditch was found missing inside a landing zone. All the channels above (9 left, 10, 13 x 2, 8 far right) are
  already water. Outside the checked width: 6 has a deep channel at x -95..-35, y 150-200 (only its x -70..-40 part
  is mapped; the rest is under trees, 60+ yds left of the line).
- No ditch is mapped as a path anywhere (the map has no path class), and OSM's cartpath tags were all real paths on
  the photo; OSM did not tag either ditch as a path.

### Par 3s: paths within 25 yds of the green edge

| hole | nearest path | |
|---|---|---|
| 4 | 13 yds over the back (path wraps behind and round the right side, 17-20 yds right) | in reach only of a ball 20+ yds long |
| 7 | none (41 yds) | |
| 12 | 21 yds short-right at (+29, 113) | |
| 14 | 28 yds right (x 39); also an unpaved pale stub crossing 25-30 yds short-left (y 163-167), not in OSM | |
| 17 | 17 yds left (x -22 at y 209) | |

Not simulated (the par-3 solver was being edited by another agent). With an iron pattern of about 8 yds lateral and
6-7 yds depth (1 sd), a strip 13-17 yds off the green EDGE is 3 sd or more from a centre-green target: well under
1 % of balls. No change.

## 2. Share of tee balls on a path (picked club and aim, Saturday calm book)

40,000 swings in the central world at each hole's Saturday temperature; path = snapped centre line, 3.0 yds wide.
"Lands" = the carry point is on the path. "Rolls" = lands off it and the roll-out touches or crosses it.

| hole | tee | club, aim | carry / total | path from the carry point | lands on path | rolls onto / across |
|---|---|---|---|---|---|---|
| 1 | Back | Driver 8.5 L | 260 / 286 | 34 | 1.03 % | 1.18 % |
| 1 | Middle | Driver 6.5 L | 260 / 282 | 31 | 1.36 % | 1.15 % |
| 2 | Back | Driver 9.5 R | 264 / 286 | 30 | 1.91 % | 0.69 % |
| 2 | Middle | Driver 11 R | 264 / 284 | 29 | 1.76 % | 0.39 % |
| 3 | Back | Driver 6 L | 263 / 286 | 35 | 0.98 % | 0.98 % |
| 3 | Middle | Driver 4.5 L | 263 / 285 | 32 | 1.37 % | 0.76 % |
| 5 | Back | Driver 4.5 R | 261 / 284 | 39 | 0.48 % | 0.60 % |
| 5 | Middle | Driver 0 | 261 / 282 | 37 | 0.58 % | 0.63 % |
| 6 | Back | Driver 5.5 R | 262 / 286 | 49 | 0.19 % | 0.00 % |
| 6 | Middle | Driver 7.5 R | 262 / 285 | 41 | 0.22 % | 0.14 % |
| 8 | Back | Driver 44.5 L | 264 / 288 | 24 | 1.83 % | 1.27 % |
| 8 | Middle | 4-wood 33.5 L | 245 / 261 | 29 | 0.59 % | 0.20 % |
| 9 | Back | Driver 12.5 R | 264 / 283 | 37 | 0.80 % | 0.01 % |
| 9 | Middle | 4-wood 11 R | 245 / 258 | 38 | 0.21 % | 0.01 % |
| 10 | Back | 2-wood 26 L | 255 / 268 | 57 | 0.00 % | 0.00 % |
| 10 | Middle | 4-wood 23 L | 245 / 258 | 48 | 0.00 % | 0.00 % |
| 11 | Back | Driver 16 R | 263 / 284 | 31 | 1.60 % | 0.09 % |
| 11 | Middle | Driver 18.5 R | 263 / 280 | 28 | 1.97 % | 0.07 % |
| 13 | Back | Driver 3 R | 265 / 286 | 38 | 0.61 % | 0.24 % |
| 13 | Middle | Driver 11 R | 265 / 292 | 47 | 0.22 % | 0.06 % |
| 15 | Back | Driver 13.5 R | 260 / 288 | 44 | 0.24 % | 0.63 % |
| 15 | Middle | Driver 7 R | 261 / 284 | 40 | 0.30 % | 0.65 % |
| 16 | Back | 4-wood 5.5 R | 248 / 261 | 47 | 0.03 % | 0.01 % |
| 16 | Middle | Long iron 7 R | 204 / 214 | 48 | 0.03 % | 0.00 % |
| 18 | Back | Driver 13 R | 267 / 289 | 45 | 0.34 % | 0.06 % |
| 18 | Middle | Driver 5.5 R | 267 / 291 | 48 | 0.22 % | 0.11 % |

Why so small: a strip 3 yds wide, 1.2-1.6 sd off the centre line of a pattern whose lateral sd is about 20 yds,
catches roughly 3 / 20 x the density there (0.1-0.2), i.e. 1.5-3 % at most, and less where the path angles away.
Wind page: a 10-15 mph crosswind moves the aim and the pattern together by design, so these shares hold to within
a factor of about 2 either way; nothing here approaches a share that could matter.

## 3. Bounce model and its effect

No measured data on cart-path bounces was found or used; this is a physics estimate and it is crude.

- Driver lands at about 28 m/s, 38 degrees down (the repo's own LAND_DEG): 17 m/s into the ground, 22 m/s along.
  On turf the ball keeps little of the vertical speed. On concrete / asphalt it keeps roughly 0.6-0.75 of it and
  about 0.8 of the forward speed: a second flight of about 2.3 s and 35-45 yds without drag, 25-40 with.
- Model, central: a ball whose carry point is on the path flies a further U(20, 45) yds along its line (irons
  U(10, 30)), with sideways scatter N(0, 8 yds); it then rolls half its normal roll from the new spot under the
  usual rules (stops in sand, trees, tall grass, water; slows in rough). A ball that rolls onto or across a path
  gets 4 yds of extra run.
- Model, strong: U(35, 60) yds further, scatter 15 yds, 8 yds extra on a roll-over.
- Not modelled: the path's edge or crown kicking the ball the other way, bounces back towards the fairway from a
  path running across the line, scuffed ball, free relief (the ball rarely stays on the path), frozen turf beside
  the path (the page already has a firm-ground pill; firm turf shrinks the gap between path and grass).
- Applied in memory by wrapping `model.finish`; the path mask is not jittered with the map draws. Each hole: 16
  prior draws x 4,096 swings, top three clubs, aim re-optimised (the engine's `robust_aim`) with the bounce off,
  central and strong. Common random numbers, so the differences are far tighter than the levels. The 16-draw
  "off" run reproduces the page's pick and aim (128 draws) within 1 yd on every hole except 10 Back, which the page
  itself shows as a near tie (2-wood by 0.012 +- 0.010; here 4-wood by 0.008); the bounce does not touch 10.

| hole | tee | change in expected strokes, picked club at its aim: central (strong) | best aim: off -> central (strong) | pick off / central / strong | margin to the next club: off -> central (strong) | cost of shading 3 / 5 yds away from the path (bounce on) |
|---|---|---|---|---|---|---|
| 1 | Back | +0.0057 (+0.0051) | 8.5 L -> 8 L (8 L) | Driver all | 0.052 -> 0.050 (0.050) | +0.0030 / +0.0089 |
| 1 | Middle | +0.0083 (+0.0065) | 6.5 L -> 6 L (6 L) | Driver all | 0.025 -> 0.019 (0.020) | +0.0033 / +0.0103 |
| 2 | Back | +0.0027 (+0.0012) | 9.5 R -> 9.5 R (9.5 R) | Driver all | 0.062 -> 0.064 (0.064) | +0.0049 / +0.0124 |
| 2 | Middle | +0.0013 (+0.0007) | 11 R -> 11.5 R (11.5 R) | Driver all | 0.028 -> 0.029 (0.028) | +0.0051 / +0.0131 |
| 3 | Back | +0.0028 (+0.0027) | 5.5 L -> 5 L (5.5 L) | Driver all | 0.061 -> 0.060 (0.060) | +0.0038 / +0.0126 |
| 3 | Middle | +0.0003 (+0.0008) | 4.5 L -> 4 L (4 L) | Driver all | 0.082 -> 0.083 (0.083) | +0.0035 / +0.0114 |
| 5 | Back | +0.0029 (+0.0023) | 4.5 R -> 4 R (4 R) | Driver all | 0.092 -> 0.092 (0.092) | +0.0032 / +0.0092 |
| 5 | Middle | +0.0038 (+0.0022) | 0 -> 0.5 L (0.5 L) | Driver all | 0.056 -> 0.055 (0.055) | +0.0029 / +0.0086 |
| 6 | Back | -0.0002 (-0.0007) | 6 R -> 6 R (6 R) | Driver all | 0.114 -> 0.114 (0.114) | +0.0036 / +0.0103 |
| 6 | Middle | -0.0005 (-0.0010) | 7.5 R -> 7.5 R (7.5 R) | Driver all | 0.047 -> 0.048 (0.048) | +0.0050 / +0.0131 |
| 8 | Back | -0.0038 (-0.0001) | 45.5 L -> 47.5 L (45.5 L) | Driver all | 0.049 -> 0.049 (0.047) | +0.0026 / +0.0054 |
| 8 | Middle | -0.0013 (-0.0002) | 34 L -> 34.5 L (34 L) | 4-wood all | 0.035 -> 0.027 (0.027) | +0.0012 / +0.0031 |
| 9 | Back | -0.0015 (-0.0024) | 12.5 R -> 13 R (13 R) | Driver all | 0.024 -> 0.023 (0.024) | +0.0059 / +0.0142 |
| 9 | Middle | -0.0003 (-0.0005) | 11 R -> 11 R (11 R) | 4-wood all | 0.035 -> 0.035 (0.034) | +0.0050 / +0.0139 |
| 10 | Back | +0.0001 (+0.0000) | 26 L -> 26 L (26 L) | unchanged (see note) | unchanged | +0.0083 / +0.0231 |
| 10 | Middle | 0.0000 (0.0000) | 23 L -> 23 L (23 L) | 4-wood all | 0.217 -> 0.219 (0.218) | +0.0129 / +0.0319 |
| 11 | Back | -0.0037 (-0.0058) | 17 R -> 17 R (17.5 R) | Driver all | 0.023 -> 0.027 (0.029) | +0.0054 / +0.0148 |
| 11 | Middle | -0.0052 (-0.0069) | 19.5 R -> 20 R (20 R) | Driver all | 0.006 -> 0.010 (0.010) | +0.0054 / +0.0122 |
| 13 | Back | +0.0004 (-0.0005) | 3.5 R -> 3.5 R (3.5 R) | Driver all | 0.101 -> 0.104 (0.103) | +0.0047 / +0.0101 |
| 13 | Middle | +0.0001 (-0.0001) | 11.5 R -> 11.5 R (11.5 R) | Driver all | 0.089 -> 0.089 (0.089) | +0.0060 / +0.0167 |
| 15 | Back | +0.0025 (+0.0044) | 13 R -> 12.5 R (12.5 R) | Driver all | 0.105 -> 0.104 (0.103) | +0.0027 / +0.0087 |
| 15 | Middle | +0.0021 (+0.0032) | 7 R -> 6.5 R (6.5 R) | Driver all | 0.048 -> 0.048 (0.047) | +0.0023 / +0.0072 |
| 16 | Back | +0.0002 (+0.0002) | 5 R -> 5 R (5 R) | 4-wood all | 0.081 -> 0.082 (0.082) | +0.0049 / +0.0156 |
| 16 | Middle | 0.0000 (0.0000) | 6.5 R -> 6.5 R (6.5 R) | Long iron all | 0.097 -> 0.098 (0.098) | +0.0031 / +0.0093 |
| 18 | Back | -0.0006 (-0.0010) | 13 R -> 13.5 R (13.5 R) | Driver all | 0.124 -> 0.124 (0.123) | +0.0025 / +0.0078 |
| 18 | Middle | -0.0003 (-0.0006) | 6 R -> 6 R (6 R) | Driver all | 0.138 -> 0.138 (0.138) | +0.0018 / +0.0050 |

Reading it:

- **Sign depends on where the kicked ball ends up.** 1, 2, 3, 5, 15: the path runs along the tall grass, so a kick
  forward and sideways loses some balls that would otherwise have stopped in the rough beside it: a cost, up to
  +0.008. 8, 9, 11, 18: the kicked ball mostly stays on mown ground (on 11 the path angles away to the right, so a
  ball running on along its own line ends on the fairway side of it): 30 free yards, a gain of up to -0.007. This
  split is my reading of the photos and the sign of the result, not a separate measurement.
- **Aim.** Largest moves: 8 Back 2 yds further LEFT (towards the path) in the central version only, 0 in the strong
  version; that hole's curve is flat (the two aims differ by 0.0001 strokes, and the page's own draw-to-draw aim
  spread on 8 is 6 yds), so it is noise, not a finding. Everything else is 0-1 yd, mostly 0.5.
- **Club.** No pick changes. The two thin margins move the safe way or trivially: 11 Middle (page: Driver / 4-wood
  tie, 0.004) goes 0.006 -> 0.010 for the Driver; 1 Middle 0.025 -> 0.019, still Driver. 8 Middle's margin column
  falls 0.035 -> 0.027 only because the 2-wood's far-left line gains from the path; the 4-wood stays the pick.
- **Shading away from the path** costs more than it saves on every hole (last column, all positive).

## 4. What is crude

- The bounce numbers are an estimate from landing speed and angle, not data. The strong version (35-60 yds further,
  15 yds scatter) is meant to bracket it; it changes nothing either.
- Frozen ground was not rerun with the bounce. With turf rolling x1.25-1.5 the path's advantage over turf shrinks,
  and the shares do not change (they depend on the carry point), so the effect can only get smaller.
- Path lines under the tree edge on 9 and 18 right are interpolated (about 3 yds uncertain). Both holes have
  under 1 % on the path.
- 16 prior draws against the page's 128; the "off" aims match the page within 1 yd, and the conclusions rest on
  paired differences 10-50 times smaller than any margin.
- Par 3s were sized by hand, not simulated.

## 5. If a path term is added later

Cheapest honest form: a `path` overlay raster (not a lie: the lie underneath still scores a ball that stops there)
from the snapped OSM lines, and in `finish()` a second-flight step for carry points on it. Worth doing for
completeness and for courses where a path runs inside the fairway line or along a hard edge; at Gateway it is
worth at most 0.008 strokes on any tee shot and changes no decision.
