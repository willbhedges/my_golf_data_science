# Gateway National par 5s: the second shot (go for the green or lay up, and where)

Nov 13 2026. Golfer's request: "add a go-for-it-in-two versus lay-up simulation for the approach on the par 5s, and
where to aim on that ... a target for where Driver goes and a target for where the 2-wood goes." Holes 3, 6, 13, 18.
No tee-shot club, aim or table number on the page changed.

Code: `opt/par5_second.py` (solver; `solve` then `describe`), `opt/par5_page.py` (page text ->
`par5_second.json`, config `par5_second`), `opt/par5_render.py` (the check pictures). Results:
`opt/results/par5_second_<set>.json` (`_v_*` = sensitivity runs). Run time: 15 s a hole and day, 2 min with the
tee-pick re-check.

    OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/par5_second.py --which truth --sets Back
    OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/par5_second.py --which truth_middle --sets Middle
    ... --which truth --sets "The Tips,Champions" --no-two-stage ; --which truth_middle --sets Forward --no-two-stage
    python3 .../opt/par5_second.py describe --which truth --sets "Back,The Tips,Champions"   (and truth_middle: Middle,Forward)
    python3 course_data/courses/gateway_national/opt/par5_page.py
    python3 course_data/courses/v2_course.py page --slug gateway_national --which truth

## Answer in short (Back tees, Saturday's forecast; Sunday within 0.1 of it)

| hole | Driver finishes | to front / middle | go for it | lay up | go minus lay-up | 2-wood finishes | from there |
|---|---|---|---|---|---|---|---|
| 3 (630) | 299, 5 L | 316 / 330 | not reachable | 4-wood (248) to (545, 34 R), the middle of the fairway, leaves 80 | | 274, 5 L | 4-wood, leaves 105 |
| 6 (530) | 291, 6 R | 226 / 239 | 4-wood at the middle of the green, 66 % carry the front | mid iron (186) to the left fairway (476, 19 L), leaves 55; or 9-iron (149) to the right fairway (440, 14 R), leaves 90 (+0.13) | -0.41 | 270, 6 R | 247 to the front: 4-wood runs up short (1 % carry it); lay-up long iron leaves 50 |
| 13 (533) | 294, 1 R | 223 / 239 | 4-wood at the left edge of the green (12 L of centre), 76 % carry the front, 8 % penalty | mid iron (186) to (480, 1 R), leaves 55; or 9-iron (149) to (443, 4 L), leaves 90 (+0.13) | -0.35 | 273, 5 L | 244 to the front: not reachable (5 %); long iron leaves 50 |
| 18 (527) | 299, 13 R | 204 / 218 | long iron 8 R of centre, 63 % carry the front, 7 % penalty | 8-iron (167) to (461, 31 L), leaves 50; or GW (128) to (422, 23 L), leaves 90 (+0.16) | -0.44 | 280, 13 R | 223 to the front: 4-wood, 86 % carry it |

(Coordinates: yds from the Back tee along the tee line, yds left / right of it.)

* **Going beats laying up on 6, 13 and 18 by 0.35-0.45 strokes** on the model, from the Driver's spot in the
  fairway, and still by 0.15-0.25 when every second shot is made 50 % wider and the 4-wood off the deck a further
  30 % wider and 10 yds shorter (table at the end). From the rough at the same spot there is no 4-wood: the edge
  falls to 0.1-0.2 and on 6 and 13 the play is the long iron up short of the green.
* **Will's call on 13 (he would not go).** The model disagrees by 0.35 with its own dispersion, but the hole gives
  him the reason: the channel is 3-6 yds off the right edge of the green and crosses in front of its right half, so
  the go line is at the LEFT EDGE of the green and 8 % of 4-woods still take a penalty. If he lays up: **mid iron,
  186 total, to the upper fairway at about 480 yds from the tee on the tee line (fairway there runs from 35 left to
  20 right; the pond's edge is at 28 right), leaving 55**; or, for a full wedge, **9-iron (149) to the gap between
  the two fairway sand patches at 443, 4 left, leaving 90** (0.13 more on the engine's table, which prices every
  yard closer as better). Both spots were looked at on the 2023 photo (below).
* **Tee pick, re-checked with the second shot played out: Driver on all four from Back and Middle; no change.**
  If he lays up whatever happens, the three woods are level on 6, 13 and 18 (Driver ahead by 0.01-0.03), and on 3
  the Driver keeps 0.04. The page says so in a pill on those holes.

## Assumptions (stated; none of them is measured)

**Clubs off the deck** (`DECK` in `par5_second.py`; carry at 70 F, total, 95 % width, 95 % carry window):

| club | carry | total | width | depth | note |
|---|---|---|---|---|---|
| Driver, 2-wood | - | - | - | - | not hit off the deck |
| 4-wood | 240 | 255 | 50 | 24 | 255 off a tee less 15; the tee width kept in yards (6 % wider as an angle) |
| Long iron | 210 | 220 | 40 | 20 | engine's club |
| Mid iron | 185 | 192 | 34 | 18 | engine's club |
| 8-iron | 162 | 167 | 30 | 16 | engine's extra club |
| 9-iron / PW / GW / SW | 150 / 138 / 126 / 113 | 154 / 141 / 128 / 115 | 28 / 26 / 24 / 22 | 15 / 14 / 13 / 12 | the par-3 bag, 12-yd gaps |

* Widths x 70 / 65 and depths x 1.25 as the engine's central world; the engine's mishits (12 % carry 92-95 %,
  2.5 % carry 65-85 %), tilt and roll noise; full swings only (no eased 4-wood, no club between 210 and 240).
* Cold: carry x (1 - 0.00135 per F below 70), the page's rule. Saturday 38-47 F on these holes: the 4-wood off the
  deck carries 230-232, the long iron 201-204.
* Wind: the forecast at the hole's time (9:00 start on 1, 14 min a hole), turned onto the SHOT's line (18's second
  shot is 15 deg left of the tee line), the engine's `wind.adjust`.
* Lie rules (from the model review's rollout, `second_pass/model/mdp.py`): rough = 4 % shorter, 25 % wider, no
  4-wood; fairway sand (re-check only) = 7 % shorter, 50 % wider, mid iron at most.
* No elevation on the second shot. Trees are priced where the ball finishes, not in flight.

**Scoring.** The ball after the second shot is valued by the engine's own per-cell strokes on the hole's map
(`Raster.strokes`: the am table by lie and distance, short game inside 20 yds, putts on the green, punch-out from
trees), rastered out past the green. Penalty areas (water and tall native, as the engine has them at Gateway): one
stroke, then the engine's rough value at the point where the ball last crossed the edge on the shot's own line.
Out of bounds (3, right): stroke and distance from the second-shot spot.

**Search.** Every club x every direction within 28 deg of the line to the middle of the green (1-deg steps), 4,000
common swings. An option is a LAY-UP when a solid shot stops 20+ yds short of the front edge, otherwise a GO. The
"target" is where a solid shot finishes. "Carry the front" = share of swings whose carry reaches the front edge on
the line to the middle.

**What the model does not know.** It has one pattern per club and treats the 4-wood off a cold fairway as a
tee-quality strike made 15 yds shorter. It lays up to the closest safe spot because the table says closer is
better; it knows nothing of a favourite wedge number, which is why the page also gives the full-wedge lay-up.

## Results

### Back, Saturday

| hole | from | spot (yds from tee, side) | to front / middle | GO: club, aim | strokes | green / around / sand / pen. / trees | carry the front | LAY-UP: club (total), target, leaves | strokes | pen. | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | Driver, fairway | 299, 5 L | 316 / 330 | none reaches | | |  | 4-wood (248), (545, 34 R), 81 | 4.09 | 0.1 % |  |
| 3 | Driver, rough | 299, 5 L | 316 / 330 | none reaches | | |  | Long iron (206), (503, 30 R), 123 | 4.27 | 0.2 % |  |
| 3 | 2-wood, fairway | 274, 5 L | 341 / 355 | none reaches | | |  | 4-wood (248), (520, 31 R), 106 | 4.18 | 0.1 % |  |
| 6 | Driver, fairway | 291, 6 R | 226 / 239 | 4-wood, 4 R of centre | 3.58 | 27 % / 55 % / 8 % / 2 % / 7 % | 66 % | Mid iron (186), (476, 19 L), 56 | 3.99 | 0.0 % | -0.41 |
| 6 | Driver, rough | 291, 6 R | 226 / 239 | none reaches | | |  | Long iron (205), (495, 14 L), 35 | 3.91 | 0.5 % |  |
| 6 | 2-wood, fairway | 270, 6 R | 247 / 261 | 4-wood, 0 R of centre | 3.69 | 19 % / 65 % / 6 % / 1 % / 1 % | 1 % | Long iron (213), (481, 18 L), 50 | 3.98 | 0.0 % | -0.30 |
| 13 | Driver, fairway | 294, 1 R | 223 / 239 | 4-wood, 12 L of centre | 3.59 | 31 % / 54 % / 5 % / 8 % / 0 % | 76 % | Mid iron (186), (480, 1 R), 53 | 3.94 | 0.1 % | -0.35 |
| 13 | Driver, rough | 294, 1 R | 223 / 239 | Long iron, 29 L of centre | 3.89 | 0 % / 37 % / 0 % / 1 % / 0 % | 0 % | Mid iron (178), (473, 1 R), 61 | 4.00 | 0.4 % | -0.11 |
| 13 | 2-wood, fairway | 273, 5 L | 244 / 260 | 4-wood, 23 L of centre | 3.83 | 10 % / 70 % / 0 % / 8 % / 0 % | 5 % | Long iron (213), (486, 1 L), 48 | 3.93 | 0.3 % | -0.10 |
| 18 | Driver, fairway | 299, 13 R | 204 / 218 | Long iron, 8 R of centre | 3.47 | 50 % / 36 % / 5 % / 7 % / 0 % | 63 % | 8-iron (167), (461, 31 L), 51 | 3.92 | 0.0 % | -0.44 |
| 18 | Driver, rough | 299, 13 R | 204 / 218 | Long iron, 15 R of centre | 3.75 | 24 % / 53 % / 4 % / 9 % / 0 % | 25 % | 8-iron (160), (455, 30 L), 57 | 3.95 | 0.0 % | -0.20 |
| 18 | 2-wood, fairway | 280, 13 R | 223 / 237 | 4-wood, 4 R of centre | 3.65 | 24 % / 63 % / 5 % / 6 % / 0 % | 86 % | Mid iron (191), (467, 27 L), 47 | 3.90 | 0.1 % | -0.25 |

### Back, Sunday (from the Driver, fairway)

| hole | spot | to front / middle | GO | strokes | carry the front | LAY-UP | strokes | go - lay-up |
|---|---|---|---|---|---|---|---|---|
| 3 | 299, -5 | 316 / 330 | - |  |  | 4-wood to (546, +35), leaves 79 | 4.08 |  |
| 6 | 297, +6 | 220 / 234 | Long iron | 3.64 | 1 % | Mid iron to (485, -17), leaves 46 | 3.92 | -0.28 |
| 13 | 291, +0 | 226 / 242 | 4-wood | 3.61 | 58 % | Mid iron to (474, +4), leaves 59 | 3.98 | -0.37 |
| 18 | 292, +13 | 211 / 226 | 4-wood | 3.65 | 97 % | Mid iron to (470, -25), leaves 45 | 3.89 | -0.23 |

### Back: lay-up by club from the Driver spot, Saturday (strokes; target; leaves)

| hole | 4-wood | Long iron | Mid iron | 8-iron | 9-iron | PW | GW | SW |
|---|---|---|---|---|---|---|---|---|
| 3 | 4.09; (545, +34); 81 | 4.19; (511, +32); 115 | 4.31; (483, +33); 143 | 4.41; (461, +22); 166 | 4.49; (448, +17); 179 | 4.57; (436, +16); 192 | 4.66; (423, +14); 205 | 4.76; (410, +14); 217 |
| 6 | 3.58; (538, -9); 7 (go) | 3.78; (503, -15); 28 (go) | 3.99; (476, -19); 56 | 4.10; (453, +17); 81 | 4.12; (440, +14); 92 | 4.14; (428, +11); 104 | 4.17; (415, +9); 116 | 4.22; (403, +7); 128 |
| 13 | 3.59; (541, +4); 9 (go) | 3.83; (507, -11); 33 (go) | 3.94; (480, +1); 53 | 4.03; (456, -1); 78 | 4.08; (443, -4); 91 | 4.12; (431, -4); 103 | 4.17; (418, -6); 116 | 4.22; (406, -1); 128 |
| 18 | 3.84; (544, -54); 35 (go) | 3.47; (512, -42); 8 (go) | 3.82; (487, -25); 32 (go) | 3.92; (461, -31); 51 | 3.98; (447, -30); 64 | 4.03; (435, -24); 77 | 4.08; (422, -23); 90 | 4.14; (414, +0); 107 |

### Back: tee pick with the second shot played out (Saturday)

| hole | valuation | Driver | 2-wood (vs Driver) | 4-wood (vs Driver) |
|---|---|---|---|---|
| 3 | engine table | 5.606, aim -1.0 | 5.666 (+0.059, se 0.001) | 5.683 (+0.076, se 0.002) |
| 3 | best second shot | 5.265, aim +0.0 | 5.301 (+0.037, se 0.002) | 5.314 (+0.049, se 0.002) |
| 3 | always lay up | 5.265, aim +0.0 | 5.301 (+0.037, se 0.002) | 5.314 (+0.049, se 0.002) |
| 6 | engine table | 5.038, aim +12.0 | 5.154 (+0.116, se 0.002) | 5.195 (+0.158, se 0.002) |
| 6 | best second shot | 4.745, aim +11.0 | 4.814 (+0.069, se 0.002) | 4.880 (+0.135, se 0.003) |
| 6 | always lay up | 5.028, aim +13.0 | 5.047 (+0.019, se 0.002) | 5.061 (+0.033, se 0.002) |
| 13 | engine table | 5.083, aim -6.0 | 5.202 (+0.118, se 0.002) | 5.227 (+0.144, se 0.002) |
| 13 | best second shot | 4.819, aim -6.0 | 4.925 (+0.105, se 0.002) | 4.934 (+0.115, se 0.002) |
| 13 | always lay up | 4.994, aim -8.0 | 5.012 (+0.018, se 0.002) | 5.011 (+0.017, se 0.002) |
| 18 | engine table | 4.871, aim +14.5 | 4.991 (+0.120, se 0.001) | 5.060 (+0.189, se 0.002) |
| 18 | best second shot | 4.657, aim +14.5 | 4.750 (+0.093, se 0.001) | 4.775 (+0.119, se 0.002) |
| 18 | always lay up | 4.922, aim +12.5 | 4.931 (+0.009, se 0.001) | 4.937 (+0.015, se 0.001) |

### Middle, Saturday

| hole | from | spot (yds from tee, side) | to front / middle | GO: club, aim | strokes | green / around / sand / pen. / trees | carry the front | LAY-UP: club (total), target, leaves | strokes | pen. | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | Driver, fairway | 295, 3 L | 256 / 270 | 4-wood, 5 L of centre | 3.83 | 3 % / 67 % / 4 % / 0 % / 0 % | 0 % | Long iron (214), (507, 31 R), 56 | 3.97 | 0.0 % | -0.14 |
| 3 | Driver, rough | 295, 3 L | 256 / 270 | none reaches | | |  | Long iron (206), (499, 30 R), 64 | 4.02 | 0.1 % |  |
| 3 | 2-wood, fairway | 274, 4 L | 277 / 291 | none reaches | | |  | 4-wood (248), (520, 30 R), 44 | 3.95 | 0.0 % |  |
| 6 | Driver, fairway | 292, 7 R | 195 / 208 | Long iron, 7 R of centre | 3.42 | 40 % / 47 % / 8 % / 1 % / 2 % | 77 % | 8-iron (162), (453, 11 L), 48 | 3.92 | 0.0 % | -0.50 |
| 6 | Driver, rough | 292, 7 R | 195 / 208 | Long iron, 4 R of centre | 3.54 | 31 % / 56 % / 7 % / 2 % / 2 % | 42 % | 8-iron (155), (446, 16 L), 55 | 3.99 | 0.0 % | -0.45 |
| 6 | 2-wood, fairway | 272, 6 R | 215 / 229 | Long iron, 0 R of centre | 3.63 | 22 % / 70 % / 4 % / 0 % / 0 % | 2 % | Mid iron (186), (457, 10 L), 43 | 3.91 | 0.0 % | -0.28 |
| 13 | Driver, fairway | 295, 9 R | 210 / 225 | 4-wood, 12 L of centre | 3.69 | 13 % / 73 % / 7 % / 4 % / 0 % | 97 % | Mid iron (185), (480, 4 L), 42 | 3.87 | 0.3 % | -0.18 |
| 13 | Driver, rough | 295, 9 R | 210 / 225 | Long iron, 28 L of centre | 3.85 | 4 % / 68 % / 0 % / 4 % / 0 % | 2 % | Mid iron (178), (473, 0 L), 48 | 3.93 | 0.5 % | -0.08 |
| 13 | 2-wood, fairway | 273, 2 R | 231 / 247 | 4-wood, 17 L of centre | 3.65 | 27 % / 59 % / 1 % / 8 % / 0 % | 47 % | Mid iron (185), (459, 4 R), 61 | 3.99 | 0.3 % | -0.34 |
| 18 | Driver, fairway | 299, 5 R | 169 / 184 | Mid iron, 0 R of centre | 3.27 | 69 % / 25 % / 1 % / 3 % / 0 % | 95 % | PW (141), (437, 25 L), 44 | 3.87 | 0.1 % | -0.60 |
| 18 | Driver, rough | 299, 5 R | 169 / 184 | Mid iron, 6 R of centre | 3.45 | 52 % / 34 % / 5 % / 7 % / 0 % | 70 % | 9-iron (148), (445, 19 L), 40 | 3.85 | 0.5 % | -0.41 |
| 18 | 2-wood, fairway | 279, 9 R | 190 / 204 | Long iron, 4 R of centre | 3.50 | 35 % / 59 % / 3 % / 2 % / 0 % | 97 % | 8-iron (167), (444, 23 L), 39 | 3.85 | 0.4 % | -0.35 |

### Middle, Sunday (from the Driver, fairway)

| hole | spot | to front / middle | GO | strokes | carry the front | LAY-UP | strokes | go - lay-up |
|---|---|---|---|---|---|---|---|---|
| 3 | 296, -3 | 256 / 269 | 4-wood | 3.81 | 0 % | Long iron to (510, +30), leaves 54 | 3.96 | -0.16 |
| 6 | 297, +8 | 189 / 203 | Mid iron | 3.54 | 9 % | 8-iron to (462, -12), leaves 39 | 3.85 | -0.31 |
| 13 | 292, +8 | 213 / 228 | 4-wood | 3.63 | 93 % | Mid iron to (474, +0), leaves 47 | 3.90 | -0.28 |
| 18 | 291, +6 | 178 / 192 | Long iron | 3.57 | 98 % | 9-iron to (434, -25), leaves 47 | 3.89 | -0.32 |

### Middle: lay-up by club from the Driver spot, Saturday (strokes; target; leaves)

| hole | 4-wood | Long iron | Mid iron | 8-iron | 9-iron | PW | GW | SW |
|---|---|---|---|---|---|---|---|---|
| 3 | 3.83; (541, +33); 24 (go) | 3.97; (507, +31); 56 | 4.05; (480, +30); 83 | 4.14; (456, +28); 106 | 4.19; (443, +28); 119 | 4.24; (429, +30); 133 | 4.30; (416, +29); 146 | 4.35; (406, +18); 157 |
| 6 | 4.16; (539, -6); 38 (go) | 3.42; (505, -1); 4 (go) | 3.71; (477, -10); 24 (go) | 3.92; (453, -11); 48 | 4.00; (439, -18); 62 | 4.06; (427, -18); 75 | 4.08; (416, +17); 87 | 4.12; (403, +14); 98 |
| 13 | 3.69; (542, +4); 21 (go) | 3.76; (507, -2); 17 (go) | 3.87; (480, -4); 42 | 3.99; (456, +4); 64 | 4.03; (444, +2); 77 | 4.07; (431, +0); 90 | 4.12; (418, -2); 103 | 4.17; (405, -3); 115 |
| 18 | 4.08; (545, -58); 69 (go) | 3.84; (512, -49); 35 (go) | 3.27; (484, -45); 7 (go) | 3.71; (463, -28); 21 (go) | 3.81; (451, -20); 35 (go) | 3.87; (437, -25); 44 | 3.94; (423, -29); 56 | 3.99; (410, -25); 69 |

### Middle: tee pick with the second shot played out (Saturday)

| hole | valuation | Driver | 2-wood (vs Driver) | 4-wood (vs Driver) |
|---|---|---|---|---|
| 3 | engine table | 5.266, aim +1.0 | 5.350 (+0.084, se 0.001) | 5.373 (+0.107, se 0.002) |
| 3 | best second shot | 4.956, aim +1.0 | 5.035 (+0.080, se 0.002) | 5.037 (+0.082, se 0.002) |
| 3 | always lay up | 5.056, aim -1.0 | 5.046 (-0.010, se 0.001) | 5.038 (-0.018, se 0.002) |
| 6 | engine table | 4.877, aim +13.0 | 4.929 (+0.052, se 0.002) | 4.960 (+0.083, se 0.002) |
| 6 | best second shot | 4.621, aim +12.0 | 4.668 (+0.047, se 0.002) | 4.650 (+0.029, se 0.002) |
| 6 | always lay up | 4.977, aim +13.0 | 4.980 (+0.004, se 0.001) | 4.973 (-0.004, se 0.002) |
| 13 | engine table | 4.968, aim +2.0 | 5.087 (+0.119, se 0.003) | 5.152 (+0.184, se 0.003) |
| 13 | best second shot | 4.764, aim +1.0 | 4.801 (+0.037, se 0.003) | 4.872 (+0.108, se 0.003) |
| 13 | always lay up | 4.993, aim +1.0 | 4.975 (-0.018, se 0.002) | 4.976 (-0.017, se 0.002) |
| 18 | engine table | 4.584, aim +6.0 | 4.719 (+0.135, se 0.001) | 4.785 (+0.201, se 0.001) |
| 18 | best second shot | 4.416, aim +6.0 | 4.532 (+0.116, se 0.001) | 4.572 (+0.156, se 0.001) |
| 18 | always lay up | 4.879, aim +7.0 | 4.890 (+0.011, se 0.001) | 4.898 (+0.019, se 0.001) |

### Sensitivity (Back, Saturday, from the Driver, fairway)

| case | hole | GO club | strokes | pen. | carry the front | lay-up strokes | go - lay-up |
|---|---|---|---|---|---|---|---|
| base | 6 | 4-wood | 3.58 | 2 % | 66 % | 3.99 | -0.41 |
| base | 13 | 4-wood | 3.59 | 8 % | 76 % | 3.94 | -0.35 |
| base | 18 | Long iron | 3.47 | 7 % | 63 % | 3.92 | -0.44 |
| 4-wood 30 % wider and 10 yds shorter | 6 | 4-wood | 3.67 | 3 % | 25 % | 3.99 | -0.32 |
| 4-wood 30 % wider and 10 yds shorter | 13 | 4-wood | 3.72 | 9 % | 40 % | 3.94 | -0.22 |
| 4-wood 30 % wider and 10 yds shorter | 18 | Long iron | 3.47 | 7 % | 63 % | 3.92 | -0.44 |
| every second shot 50 % wider | 6 | 4-wood | 3.81 | 6 % | 58 % | 4.05 | -0.24 |
| every second shot 50 % wider | 13 | 4-wood | 3.73 | 6 % | 67 % | 3.98 | -0.25 |
| every second shot 50 % wider | 18 | Long iron | 3.70 | 10 % | 56 % | 3.93 | -0.23 |
| both | 6 | Long iron | 3.87 | 1 % | 1 % | 4.05 | -0.18 |
| both | 13 | 4-wood | 3.83 | 7 % | 41 % | 3.98 | -0.15 |
| both | 18 | Long iron | 3.70 | 10 % | 56 % | 3.93 | -0.23 |
## Reach, by arithmetic

| hole (Back) | front edge from the Driver's spot | cold solid carry | solid carry minus front | simulated share carrying the front |
|---|---|---|---|---|
| 6 | 226 | 4-wood 231 (41 F, 4 mph across) | +5 | 66 % |
| 13 | 223 | 4-wood 232 (45 F) | +9 | 76 % |
| 18 | 204 | long iron 207 (47 F, 3 mph behind) | +3 | 63 % |
| 13, after a 2-wood | 244 | 4-wood 232 | -12 | 5 % |
| 3 | 316 | 4-wood 231 | -85 | 0 |

One standard deviation of carry is 7.5 yds for the 4-wood and 14.5 % of swings are mishits that carry 5 % or more
short, so +9 gives 0.855 x 88 % = 76 %, +5 gives 0.855 x 75 % = 64 %: the simulation agrees.
18's 527 is from the second pad (the tee moved 17 yds forward on Nov 13): the Driver's spot is 218 from the middle
and 204 from the front, the page's "To green" is 218.

## Pictures looked at

`par5_img/second_h<hole>_<set>_sat.jpg`: the 2023 photo, plain and with the map's zones; white = where the Driver
and the 2-wood finish; cyan square = lay-up target; red star = go target; magenta + = each club's best target.
`par5_img/sheet_Back_maps.jpg`, `sheet_Middle_maps.jpg`, `sheet_h13.jpg`: the page's own pictures.

* **3:** the 4-wood's target (545, 34 R) is in the middle of the mown fairway (15 R to 58 R there), 35 yds from
  the tree line on the right, past the three sand patches at 470-490. Fine.
* **6:** the mid-iron target (476, 19 L) is on the upper-left fairway (34 L to 3 L), the chain of sand on its right,
  tree crowns 12+ yds left of the line at 400-440 (flight not priced). The shorter lay-ups (9-iron and less) go to
  the right-hand fairway at 400-450, 10-17 R. The go line runs up the left fairway to the green's mouth.
* **13:** the mid-iron target (480, 1 R) is on mown fairway beyond the centre sand patch (458-472, 13 L), 19 yds
  from the fairway's right edge and 27 from the pond; the 9-iron target (443, 4 L) is between the two sand
  patches with the pond 35 yds right. The go target is the green's left edge; the channel on the right is mapped.
* **18:** the 8-iron target (461, 31 L) is on mown fairway, 19-20 yds right of the pond's edge (the pond is at
  about 50 L there): no penalty balls in 4,000 swings, but it is the lay-up nearest to trouble; the GW target
  (422, 23 L) has 25+ yds. The go line is right of centre, away from the pond on the green's left.

## The page

Each par 5 card has a "Second shot" block under the club table (Gateway only: `page_text`-style data in
`par5_second.json`, the shared template shows it only where a hole carries it), for the tee set and day picked:
the better of go / lay up first, the other with its cost, a full-wedge lay-up when the best one leaves under 70,
one line from the rough, one line after a 2-wood. On the Whole hole picture: a hollow square "2ND" at the lay-up
target, a ring "GO" at the aim point beside the green, a small blue ring "2-WOOD" where the 2-wood would finish.
The block is for the solved club at the solved tee: it hides when another club row is tapped, the tee is moved, or
the wind model picks a different club. Pills (Back and Middle, from the re-check): "Laying up regardless: the
2-wood ... just as good off the tee". No hazard words.

QA (qa_page.js, five sets): 18 holes, 0 problems each; against the version-15 page (cadbcaf2c) every recorded
field is identical except the new `second` text and the added pill on 3, 6, 13, 18; all 360 states of the page's
own solver (set x day x start x hole: headline, aim, table) identical apart from those pills.

## Not done / crude

* Forward tees: solved (results file), not shown on the page: the block is keyed to the base set a hole is drawn from and Forward's did not match; from there the second shot is an ordinary iron in any case.
* The block uses a 9:00 start on hole 1; a start on 10 moves these holes' clock by two hours (2-5 F).
* The re-check values penalty and tree balls off the tee with the engine's table (not the rollout), a 6-yd value
  lattice and 500 swings a node: margins good to about 0.01.
* 6's right tall-grass band is drawn 10-15 yds tighter than the ground at 260-300 (noted by the manager; not fixed).
