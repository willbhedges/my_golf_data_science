# Gateway National par 3s: aim box for an unknown pin, and the plays-like number (Nov 9 2026)

**Nov 13 update: the page target now obeys the DECADE edge rule (section 0). Sections 1-7 are the Nov 9 expected-strokes
study it was built on; where a box or a number there differs from section 0, section 0 is what the page shows.**

## 0. The DECADE rule as a constraint (Nov 13 2026, golfer's request)

Script `opt/par3_decade.py` (`solve`, `page`, `table`); results `opt/results/par3_decade.json`; page file
`par3_targets.json`; club ladder `par3_ladder.json` (re-run on the new targets, every set).

**Refresh, Nov 13 evening** (Friday-evening forecast, NWS; Saturday 10:36, Sunday 9:00). `opt/par3_target.py` reads
the day's own tee time (`TEE_HOURS` from config `tee_hours`; it had 9:00 hard-coded for both days).
`opt/results/par3_plays_forecast.json` (the D of the rule) rewritten from the rebuilt page: its Plays number to the
box in the four states, minus the box depth (D is 0-5 yds smaller than before: Sunday has no wind against now;
Back 4 187.5, 7 187.5, 12 135.5, 14 207, 17 203.5). `par3_decade.py solve` and `par3_ladder.py`, every set, both
tall-grass rule sets (1-2 min a set). Result: no Back target moves; Middle 4 (2, -2) -> (2.5, -2.5) and Forward 14
(1.5, -1.5) -> (1, -1.5), both under 1 yd; every target still meets the rule as before (4, 14, 17 from Back and
behind remain lesser-of-two-evils, short by 0.1-0.2 yds less). The ladder is identical step for step (it is a
calm 70-F table). No club changes on the page for Saturday or Sunday on any set. `par3_ladder.py` now sets
`P3_FEATURES=1` itself (a run without it gives a different ladder: the change-overs 1-2 yds later).

### 0.1 The rule, as checked

Source: the golfer's own statement of Scott Fawcett's DECADE approach rule (Nov 13). The 5 % base is also in the USGA
junior-development slide deck "Picking Targets Into Greens" (160 yds -> 8 yds from the edge). I could not find a
public page that gives the +3 / +1-2 modifiers, so those are the golfer's numbers; the repo's earlier DECADE book
(`mozingo/yardage_book.py`: distance / 20, +3 water or OB, +2 trees or tall grass, +1 bunker) agrees with them except
that it had tall grass at +2.

The target T is the centre of the blue box, which is the **landing spot** (the number on the page is the carry to it).
For every point b of the green edge:

    distance(T, b) >= 0.05 x D + modifier(b)

* **D** = the page's plays-like number to the target, the largest of the four forecast states (Sat / Sun x start 1 /
  10). It is a yard or two more than the card on these cold days, so the margin is on the safe side.
* **modifier(b)**, from what lies beyond that part of the edge (the par-3 solve's map: truth map +
  `opt/par3_features.json`, checked on the 2023 photo):
  * **+3** penalty: water, OB, tall native (penalty area at Gateway: the golfer's rule), in full when it starts within
    5 yds of the edge, falling in a straight line to 0 at 10 yds;
  * **+2** trees, the same taper (the golfer's statement does not name trees; this is the old book's number);
  * **+2** a bunker within 5 yds of the edge, **+1** one 5-10 yds off;
  * **0** mown ground.
* **Every part of the edge** is checked, not four sides: the table gives left / right / short / long through the
  target and the tightest edge point in any direction.
* **Lesser of two evils**, when the margins do not all fit: the penalty margins are met first (two penalty edges that
  conflict share the shortfall); then the worst shortfall on the other edges is made as small as possible, with
  expected strokes allowed to buy shortfall back at 0.01 strokes a yard, so the leftover leans toward the cheaper miss.
* **Inside the rule, expected strokes decides** (the model of section 1 with the fixes of 0.4).
* One target for every wind class of the page (the forecast is 4-9 mph; the old book's +1 / +2 / +3 yds at 10 / 20 /
  30 mph do not fit these greens).
* The box drawn is the target +/- 2 yds.

The roll is not in the rule: the ball finishes one roll past the box (2-3 yds with a wedge, 6-8 with a mid iron, 10
with the 4-iron), so the finish is closer to the back edge than the "long" column by that much. Expected strokes
knows this, which is why it takes the short end of the allowed depth.

### 0.2 Green outlines against the 2023 photo

The margins are measured on `opt/par3_green_check.json`: the solve's outline cut back to the putting surface classified
on the 0.3 m 2023 photo (colour + infrared), the smaller of the two on every side. The page now draws this outline.

| hole | side that matters | photo (colour / infrared profile, 0.5-yd steps) | solve outline | outline the page drew before | check outline |
|---|---|---|---|---|---|
| 12 | left, at the centre's depth | putting surface ends 13-14.5 yds left of the centre; collar to 15.5; bank to 17.5; waterline 17.5-18 | 14.8 | 11.5 (OSM: 2-3 yds inside the true edge) | 14.5 |
| 12 | long, 4-8 yds left of the centre | surface ends 14.5-15.2 past the centre; water from 19-22 | 16.8-17.0 (takes in the collar) | 15-15.5 | 15.2 |
| 12 | short-left | surface edge 2-3 yds inside the waterline (the map's line is 1-2.5 yds on the dry side of the 2023 waterline) | within 0.5 | 1-2 inside | within 0.5 |
| 7 | front | surface ends 13-15.5 yds short of the centre; the tall growth starts 2-5 yds beyond it | 14.2-15.8 | the same polygon | 13.2-15.2 |
| 7 | right | surface runs 1.5-3 yds further right than the outline (as noted Nov 9) | 10 | 10 | 10 |
| 4, 14, 17 | all | within 1-2 yds; 14's left edge 1.5-2.5 yds inside the outline | | | the smaller |

So on 12 the old page picture made the target look 3 yds nearer the left edge than it is.

### 0.3 Result (wind class of the forecast; "have / need" in yds)

L2E = lesser of two evils. "Old target" = the box on the page at 2fede0ff8, checked against the same rule.

| set | hole | plays (max) | base | old target | old: tightest edge (have / need) | new model's free optimum | DECADE target | left | right | short | long | tightest | how | cost vs free optimum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Back | 4 | 184 | 9.2 | (+2.5, -4.0) | 7.8 / 10.2 bunker **FAIL 2.4** | (+2.0, -4.0) | **(+2.5, -3.5)** | 12 / 10.2 bunker | 13 / 9.2 mown | 11 / 10.2 bunker | 14 / 9.4 mown | 8.1 / 10.2 bunker | L2E: other edges 1.4 short | +0.000 +/- 0.001 |
| Back | 7 | 191 | 9.6 | (+0.0, -1.0) | 10.9 / 12.0 penalty **FAIL 1.2** | (+1.0, -1.5) | **(-1.0, +1.5)** | 11 / 9.6 mown | 11 / 10.6 bunker | 15 / 12.4 penalty | 13 / 11.9 penalty | 10.9 / 10.9 mown | fits | +0.015 +/- 0.002 |
| Back | 12 | 136 | 6.8 | (-0.5, -0.5) | 10.3 / 9.2 penalty ok | (-0.5, -0.5) | **(-0.5, -0.5)** | 14 / 9.8 penalty | 12 / 6.8 mown | 16 / 9.8 penalty | 15 / 9.8 penalty | 10.3 / 9.2 penalty | fits | +0.000 +/- 0.000 |
| Back | 14 | 207 | 10.4 | (+2.5, -5.0) | 8.6 / 11.3 bunker **FAIL 2.7** | (+2.5, -4.5) | **(+2.5, -4.0)** | 10 / 11.5 trees | 8 / 10.4 mown | 13 / 10.4 mown | 20 / 10.4 mown | 9.1 / 11.4 bunker | L2E: other edges 1.7 short | +0.001 +/- 0.001 |
| Back | 17 | 201 | 10.1 | (-0.5, -5.5) | 10.4 / 12.0 bunker (greenside) **FAIL 1.6** | (-0.5, -5.0) | **(-0.5, -4.5)** | 9 / 10.1 mown | 12 / 12.1 bunker (greenside) | 13 / 10.1 mown | 19 / 10.1 mown | 10.7 / 12.1 bunker (greenside) | L2E: other edges 0.3 short | +0.001 +/- 0.001 |
| The Tips | 4 | 200 | 10.1 | (+2.0, -7.0) | 5.1 / 10.9 bunker **FAIL 5.8** | (+2.5, -4.5) | **(+2.5, -4.5)** | 11 / 11.1 bunker | 13 / 10.1 mown | 10 / 11.1 bunker | 15 / 10.4 mown | 7.3 / 11.1 bunker | L2E: other edges 2.5 short | +0.000 +/- 0.000 |
| The Tips | 7 | 215 | 10.8 | (+0.5, -5.0) | 7.4 / 13.2 penalty **FAIL 5.7** | (+1.5, -1.0) | **(+0.0, +0.5)** | 12 / 10.8 mown | 10 / 11.8 bunker | 14 / 13.5 penalty | 14 / 13.7 penalty | 9.8 / 11.8 bunker | L2E: penalty 0.7 short, others 1.1 | +0.006 +/- 0.002 |
| The Tips | 12 | 160 | 8.0 | (+1.0, -2.5) | 11.7 / 10.9 penalty ok | (+0.5, -1.5) | **(+0.5, -1.5)** | 14 / 11.0 penalty | 11 / 9.0 bunker | 15 / 11.0 penalty | 13 / 11.0 penalty | 11.0 / 10.6 penalty | fits | +0.000 +/- 0.000 |
| The Tips | 14 | 247 | 12.3 | (+2.0, -11.5) | 4.0 / 13.1 bunker **FAIL 9.1** | (+4.5, -8.5) | **(+3.5, -6.5)** | 10 / 13.5 trees | 8 / 12.3 mown | 11 / 12.3 mown | 22 / 12.3 mown | 7.5 / 12.3 mown | L2E: other edges 3.7 short | +0.005 +/- 0.002 |
| The Tips | 17 | 237 | 11.8 | (-3.5, -10.0) | 6.3 / 12.7 bunker **FAIL 6.4** | (-1.5, -7.5) | **(-1.0, -6.5)** | 9 / 11.8 mown | 12 / 13.8 bunker (greenside) | 10 / 11.8 mown | 20 / 11.8 mown | 8.8 / 12.8 bunker | L2E: other edges 2.1 short | +0.004 +/- 0.001 |
| Champions | 4 | 198 | 9.9 | (+2.0, -6.5) | 5.5 / 10.8 bunker **FAIL 5.3** | (+2.5, -4.5) | **(+2.5, -4.0)** | 12 / 10.9 bunker | 13 / 9.9 mown | 10 / 10.9 bunker | 14 / 10.2 mown | 7.6 / 10.9 bunker | L2E: other edges 2.4 short | +0.001 +/- 0.001 |
| Champions | 7 | 211 | 10.6 | (+1.0, -5.0) | 7.9 / 13.1 penalty **FAIL 5.2** | (+0.5, -0.5) | **(+0.5, +0.5)** | 12 / 10.5 mown | 9 / 11.5 bunker | 14 / 13.3 penalty | 14 / 13.5 penalty | 9.4 / 11.5 bunker | L2E: penalty 0.3 short, others 1.7 | +0.007 +/- 0.001 |
| Champions | 12 | 153 | 7.6 | (+1.0, -2.0) | 11.5 / 10.2 penalty ok | (+0.0, -1.0) | **(+0.0, -1.0)** | 14 / 10.6 penalty | 12 / 7.6 mown | 16 / 10.6 penalty | 14 / 10.6 penalty | 10.6 / 10.0 penalty | fits | +0.000 +/- 0.000 |
| Champions | 14 | 244 | 12.2 | (+1.5, -11.0) | 4.0 / 12.9 bunker **FAIL 8.9** | (+4.0, -8.0) | **(+3.0, -5.5)** | 11 / 13.4 trees | 8 / 12.2 mown | 12 / 12.2 mown | 21 / 12.2 mown | 8.8 / 13.2 bunker | L2E: other edges 3.5 short | +0.007 +/- 0.002 |
| Champions | 17 | 231 | 11.5 | (-3.0, -9.5) | 6.8 / 12.4 bunker **FAIL 5.6** | (-1.5, -8.0) | **(-1.0, -6.5)** | 9 / 11.5 mown | 12 / 13.5 bunker (greenside) | 10 / 11.5 mown | 20 / 11.5 mown | 8.8 / 12.5 bunker | L2E: other edges 1.7 short | +0.002 +/- 0.001 |
| Middle | 4 | 158 | 7.9 | (+2.0, -2.5) | 8.6 / 8.9 bunker **FAIL 0.3** | (+2.0, -2.0) | **(+2.0, -2.0)** | 13 / 8.9 bunker | 13 / 8.3 mown | 13 / 8.9 bunker | 12 / 7.9 mown | 8.9 / 8.9 bunker | fits | +0.000 +/- 0.000 |
| Middle | 7 | 169 | 8.4 | (-0.5, -0.5) | 10.5 / 10.4 penalty ok | (-1.0, -0.5) | **(-0.5, -0.5)** | 11 / 8.4 mown | 10 / 9.4 bunker | 13 / 11.4 penalty | 15 / 11.0 penalty | 10.5 / 10.4 penalty | fits | +0.000 +/- 0.001 |
| Middle | 12 | 120 | 6.0 | (-1.0, -0.5) | 11.1 / 9.0 penalty ok | (-1.0, -0.5) | **(-1.0, -0.5)** | 13 / 9.0 penalty | 13 / 6.0 mown | 16 / 9.0 penalty | 15 / 9.0 penalty | 11.1 / 9.0 penalty | fits | +0.000 +/- 0.000 |
| Middle | 14 | 193 | 9.7 | (+1.5, -3.5) | 8.6 / 10.6 bunker **FAIL 2.0** | (+1.5, -3.5) | **(+2.0, -2.5)** | 10 / 10.9 trees | 9 / 9.7 mown | 15 / 10.7 bunker | 19 / 9.7 mown | 9.5 / 10.7 bunker | L2E: other edges 1.0 short | +0.003 +/- 0.001 |
| Middle | 17 | 180 | 9.0 | (+0.0, -4.0) | 10.5 / 10.9 bunker (greenside) **FAIL 0.5** | (+0.5, -3.5) | **(+0.0, -2.5)** | 9 / 9.0 mown | 12 / 11.0 bunker (greenside) | 15 / 9.0 mown | 17 / 9.0 mown | 11.1 / 11.0 bunker (greenside) | fits | +0.004 +/- 0.001 |
| Forward | 4 | 135 | 6.7 | (+1.5, -2.5) | 8.4 / 7.7 bunker ok | (+1.5, -1.0) | **(+1.5, -1.0)** | 12 / 7.7 bunker | 12 / 8.4 penalty | 14 / 6.7 mown | 12 / 6.7 mown | 10.7 / 9.7 penalty | fits | +0.000 +/- 0.000 |
| Forward | 7 | 153 | 7.6 | (-1.0, -2.0) | 9.5 / 10.0 penalty **FAIL 0.5** | (-0.5, +0.0) | **(-0.5, +0.0)** | 11 / 7.6 mown | 10 / 8.6 bunker | 13 / 10.4 penalty | 15 / 10.6 penalty | 10.6 / 9.4 penalty | fits | +0.000 +/- 0.000 |
| Forward | 12 | 95 | 4.8 | (-0.5, +0.0) | 9.9 / 7.2 penalty ok | (-2.0, +1.0) | **(-2.0, +1.0)** | 12 / 7.8 penalty | 13 / 4.8 mown | 18 / 7.8 penalty | 15 / 7.8 penalty | 10.1 / 7.3 penalty | fits | +0.000 +/- 0.000 |
| Forward | 14 | 162 | 8.1 | (+0.0, -3.5) | 7.4 / 9.0 trees **FAIL 1.6** | (+1.0, -1.5) | **(+1.5, -1.5)** | 10 / 9.4 trees | 9 / 8.1 mown | 16 / 8.1 mown | 19 / 8.9 mown | 9.8 / 9.4 trees | fits | +0.001 +/- 0.001 |
| Forward | 17 | 162 | 8.1 | (-1.0, -4.0) | 8.3 / 8.0 mown ok | (+0.5, -2.5) | **(+0.5, -2.5)** | 10 / 8.1 mown | 12 / 10.1 bunker (greenside) | 14 / 8.1 mown | 18 / 8.1 mown | 10.7 / 10.1 bunker (greenside) | fits | +0.000 +/- 0.000 |

Page targets and clubs, before -> now (plays-like number and club for each forecast state):

| set | hole | target on the page before -> now (yds right, yds past the centre) | moved | Sat, start 1 | Sat, start 10 | Sun, start 1 | Sun, start 10 | new target against the old one, strokes |
|---|---|---|---|---|---|---|---|---|
| Back | 4 | (+2.0, -4.0) -> (+2.5, -3.5) | 0.7 | 180 7-iron -> 181 7-iron | 178 7-iron -> 179 7-iron | 183 6-iron -> 184 6-iron | 182 6-iron (close) -> 183 6-iron (close) | -0.000 +/- 0.001 |
| Back | 7 | (+0.0, -1.0) -> (-1.0, +1.5) | 2.7 | 187 6-iron -> 190 6-iron | 184 6-iron -> 187 6-iron | 189 6-iron -> 191 6-iron | 187 6-iron -> 189 6-iron | +0.015 +/- 0.002 |
| Back | 12 | (-1.0, +0.0) -> (-0.5, -0.5) | 0.7 | 137 PW (same) | 137 PW -> 136 PW | 131 GW (same) | 132 GW (same) | +0.000 +/- 0.000 |
| Back | 14 | (+2.5, -4.5) -> (+2.5, -4.0) | 0.5 | 201 5-iron (same) | 203 5-iron -> 204 5-iron | 205 5-iron (same) | 207 5-iron (close) (same) | +0.000 +/- 0.001 |
| Back | 17 | (-0.5, -5.0) -> (-0.5, -4.5) | 0.5 | 197 5-iron -> 198 5-iron | 201 5-iron (same) | 196 5-iron -> 197 5-iron | 198 5-iron (same) | +0.001 +/- 0.001 |
| The Tips | 4 | (+2.0, -6.5) -> (+2.5, -4.5) | 2.1 | 195 5-iron -> 197 5-iron | 193 5-iron -> 195 5-iron | 198 5-iron -> 200 5-iron | 197 5-iron -> 199 5-iron | -0.018 +/- 0.002 |
| The Tips | 7 | (+0.5, -5.0) -> (+0.0, +0.5) | 5.5 | 208 4-iron -> 214 4-iron | 205 4-iron (close) -> 211 4-iron | 210 4-iron -> 215 4-iron | 208 4-iron -> 213 4-iron | -0.064 +/- 0.005 |
| The Tips | 12 | (+1.0, -2.5) -> (+0.5, -1.5) | 1.1 | 159 8-iron -> 160 8-iron | 158 8-iron -> 159 8-iron | 152 9-iron -> 153 9-iron | 153 9-iron -> 154 9-iron | -0.006 +/- 0.001 |
| The Tips | 14 | (+1.5, -11.0) -> (+3.5, -6.5) | 4.9 | 235 between clubs -> 240 between clubs | 238 between clubs -> 243 between clubs | 240 between clubs -> 245 between clubs | 242 between clubs -> 247 between clubs | -0.019 +/- 0.003 |
| The Tips | 17 | (-2.5, -10.0) -> (-1.0, -6.5) | 3.8 | 229 between clubs -> 233 between clubs | 233 between clubs -> 237 between clubs | 228 between clubs -> 232 between clubs | 230 between clubs -> 234 between clubs | -0.007 +/- 0.002 |
| Champions | 4 | (+2.0, -6.5) -> (+2.5, -4.0) | 2.5 | 192 6-iron (close) -> 194 6-iron (close) | 190 6-iron -> 192 6-iron | 195 5-iron -> 198 5-iron | 194 5-iron -> 197 5-iron | -0.011 +/- 0.002 |
| Champions | 7 | (+0.5, -4.5) -> (+0.5, +0.5) | 5.0 | 204 5-iron -> 210 4-iron | 202 5-iron -> 207 5-iron | 206 4-iron (close) -> 211 4-iron | 204 5-iron -> 209 4-iron | -0.061 +/- 0.004 |
| Champions | 12 | (+0.5, -2.0) -> (+0.0, -1.0) | 1.1 | 152 9-iron -> 153 9-iron | 151 9-iron -> 152 9-iron | 145 9-iron -> 146 9-iron | 146 9-iron -> 147 9-iron | -0.004 +/- 0.001 |
| Champions | 14 | (+1.5, -10.5) -> (+3.0, -5.5) | 5.2 | 231 between clubs -> 237 between clubs | 235 between clubs -> 240 between clubs | 236 between clubs -> 241 between clubs | 239 between clubs -> 244 between clubs | -0.017 +/- 0.003 |
| Champions | 17 | (-3.0, -9.5) -> (-1.0, -6.5) | 3.6 | 224 between clubs -> 227 between clubs | 228 between clubs -> 231 between clubs | 222 between clubs -> 226 between clubs | 224 between clubs -> 227 between clubs | -0.007 +/- 0.002 |
| Middle | 4 | (+2.0, -2.0) -> (+2.0, -2.0) | 0.0 | 155 9-iron (same) | 153 9-iron (same) | 158 9-iron (close) (same) | 157 9-iron (same) | -0.001 +/- 0.001 |
| Middle | 7 | (+0.0, -0.5) -> (-0.5, -0.5) | 0.5 | 167 8-iron (same) | 165 8-iron (same) | 169 8-iron (same) | 167 8-iron (same) | +0.000 +/- 0.000 |
| Middle | 12 | (-1.0, -0.5) -> (-1.0, -0.5) | 0.0 | 120 SW (same) | 119 SW (same) | 115 SW (same) | 116 SW (same) | +0.000 +/- 0.000 |
| Middle | 14 | (+2.0, -3.5) -> (+2.0, -2.5) | 1.0 | 187 6-iron -> 188 6-iron | 189 6-iron -> 190 6-iron | 190 6-iron -> 191 6-iron | 192 6-iron -> 193 6-iron | +0.003 +/- 0.001 |
| Middle | 17 | (+0.5, -4.0) -> (+0.0, -2.5) | 1.6 | 176 7-iron -> 177 7-iron | 179 7-iron -> 180 7-iron | 175 7-iron -> 176 7-iron | 176 7-iron -> 178 7-iron | +0.003 +/- 0.001 |
| Forward | 4 | (+1.5, -2.5) -> (+1.5, -1.0) | 1.5 | 131 GW -> 132 GW | 129 GW -> 131 GW | 133 PW -> 135 PW | 132 PW (close) -> 134 PW (close) | -0.007 +/- 0.001 |
| Forward | 7 | (-1.0, -2.0) -> (-0.5, +0.0) | 2.1 | 149 9-iron -> 152 9-iron | 147 9-iron -> 149 9-iron | 151 9-iron -> 153 9-iron | 149 9-iron -> 151 9-iron | -0.013 +/- 0.002 |
| Forward | 12 | (-0.5, +0.0) -> (-2.0, +1.0) | 1.8 | 94 LW -> 95 LW | 94 LW -> 95 LW | 90 between clubs -> 91 between clubs | 91 between clubs -> 92 between clubs | -0.006 +/- 0.001 |
| Forward | 14 | (+0.5, -3.0) -> (+1.5, -1.5) | 1.8 | 156 9-iron -> 157 9-iron (close) | 158 8-iron -> 160 8-iron | 159 8-iron -> 161 8-iron | 161 8-iron -> 162 8-iron | -0.011 +/- 0.002 |
| Forward | 17 | (-0.5, -3.5) -> (+0.5, -2.5) | 1.4 | 158 8-iron -> 159 8-iron | 161 8-iron -> 162 8-iron | 157 8-iron (close) -> 158 8-iron (close) | 158 8-iron -> 159 8-iron | -0.007 +/- 0.001 |

* **12 (all sets): the old target already met the rule.** Back: 14 yds from the left edge (9.8 needed), 16 from the
  front, 15 from the back. It moved 0-1.5 yds. The picture misled: the dashed outline was 2-3 yds inside the true left
  edge.
* **7: the old targets failed, by 1.2 (Back) to 5.7 yds (The Tips)**, tightest against the tall growth short and
  short-left. The Tips moves 5.5 yds deeper, Champions 5.5, Back 2.7, Forward 2.1; Middle already passed.
  The Tips and Champions cannot fit both the front (13.3-13.5) and the back-right long grass (13.5-13.7) on a 31-yd
  green: the two share a shortfall of 0.3-0.7 yd; the right-hand bunker edge gives way (9-10 yds against 11.5-11.8).
* **4, 14, 17 from Back and behind: the greens are narrower than twice the base** (4: 16 yds across its short axis
  against 2 x 9.2-10.1; 14 and 17: 20-23 yds wide against 2 x 10.1-12.3 plus the bunker / tree yards), so no point
  satisfies every edge. Penalty margins are met; the other edges are short by 0.3-3.7 yds at best and the table shows
  each side. The old targets were worse on the tightest edge on every one of them.
* **Cost of the constraint** (last column of the first table): at most 0.015 strokes (Back 7), 0.007 or less
  elsewhere. Against the old page target the new one is better by 0.06 on The Tips / Champions 7, 0.02 on The Tips 4
  and 14, and within 0.004 (noise) on Back, except Back 7 (+0.015: the rule, not the model, moves it).
* **Club**: only Champions 7 changes (5-iron -> 4-iron in three of the four states: the number rises 5-6 yds).
  Back 7 reads 187-191 between the 6-iron (185) and the 5-iron (198); the ladder keeps the 6-iron.

### 0.4 Why the old targets differed, and what was fixed in the model

Free optimum of the model for The Tips 7 as each piece is added (1-yd grid, 8,000 swings):

| model | The Tips 7 | Back 7 |
|---|---|---|
| page box at 2fede0ff8 | (+0.5, -5.0): the Nov 9 solve, never re-run for The Tips / Champions / Forward | (0, -1) |
| today's engine on the Nov 9 map | (+1, -3) | (0, -2) |
| + second-pass surrounds (`P3_FEATURES=1`: long grass short of 7) | (0, -2) | (-1, -1) |
| + the thicket short-left of 7 is penalty, not a punch-out from trees | (+1, -2) | (0, -1) |
| + the trees behind 7 cut back to where they stand on the 2023 photo | (0, -1) | (0, -1) |
| + penalty balls priced where they crossed the edge | (0, -1) | (+1, -1) |
| + the DECADE rule | (0, +0.5) | (-1, +1.5) |

1. **Stale boxes.** The Tips, Champions and Forward still had the Nov 9 boxes (first-pass physics, no second-pass
   surrounds): 2-5 yds too short on 4, 7, 14, 17. Every set is now solved on the same model.
2. **Penalty priced at the crossing point** (`opt/par3_target.py`, `GHole._strokes_field`; audit round 3's note). A
   ball in water or tall native cost 1 + a rough chip from the ball's own distance. It now costs 1 + the next shot
   from the last dry point on the tee-to-ball line, like the tee-shot engine. Short of 7 from The Tips that point is
   32-53 yds behind the ball: 4.12 strokes instead of about 3.4. `P3_PENALTY=ball` restores the old pricing.
3. **7 short-left**: the 2014-lidar tree block there is a regrown thicket; it was priced as a punch-out from trees.
   It is now tall native = penalty (`THICKET_SHORT`; `P3_THICKET=trees` restores).
4. **7 long**: the 2014 crown polygon reached 1-5 yds from the back edge; on the 2023 photo that strip is mown and
   the crowns start 8-9 yds behind the green. Cut back to that line (`STALE_TREES_LONG`; `P3_TREES7=lidar` restores).
5. **What the rule adds over expected strokes**: the model's free optimum lands 1-8 yds short of centre because the
   ball rolls; the rule asks for the landing spot itself to clear the front by 5 % + modifier, which is 1-2.5 yds
   deeper on 7 and 14 from the longer tees. The lateral differences are under 1.5 yds.

Not satisfied / open:
* The rule cannot be met in full on 4, 14, 17 (Back, The Tips, Champions), Middle 14, and The Tips / Champions 7, as
  above.
* The page text gives the four distances ("The middle of the box is 11 yds from the left edge, ...") without naming
  what is beyond them.
* The 10-yd "counts as beside the green" distance, the taper and the trees / bunker steps are my reading, not the
  golfer's words; `NEAR`, `FULL`, `ADD` in `opt/par3_decade.py`.
* The Card row (front / centre / back) still uses the package outline.
* `P3_FEATURES=1` is now the default of `opt/par3_decade.py`; `opt/par3_ladder.py` must be run with it set.


Holes 4, 7, 12, 14 and 17 (Back 180 / 180 / 131 / 200 / 195), every tee set. The page's par-3 box was the DECADE box
(`yardage_book.par3_plan`: cushions in from each edge, the worse side first). This page replaces it with the
**expected-strokes optimum for a pin anywhere on the green, on Will's own iron pattern**. It is the method of Eagle
Knoll (`eagle_knoll/OPTIMIZE.md` section 13). The model code is imported unchanged from
`eagle_knoll/opt/par3_target.py`. Only the course wiring, the two ends of the bag and the forecast are Gateway's.

* Script: `opt/par3_target.py` (`solve`, `robust`, `mapvar`, `numbers`, `page`).
* Results: `opt/results/par3_target_<set>.json` (surfaces (coarse grid for Back only), clubs, SEs), `opt/results/par3_robust.json` (sensitivity and
  map variants) and `opt/results/par3_numbers.json` (plays-like by temperature and wind).
* Page file: `par3_targets.json`. It is read by `course_data/courses/par3_targets.py` once the config has
  `"par3_targets": "course_data/courses/gateway_national/par3_targets.json"`. It is not wired yet, because the engine
  agent owns `config.json`.

## 1. Method

**Ball** (the engine's `model.shots` at the central world):
* Lateral sigma = 95 % width / 4 x 70/65. Carry sigma = depth window x 1.25 / 4. rho 0.1.
* Mishits: 12 % slight (92-95 % carry) and 2.5 % heavy (65-85 %).
* Temperature: carry x (1 - 0.00075 (70 - T)).
* Wind: `wind.adjust`, including gust scatter. The mean drift is aimed off.
* Clubs:
  * **Engine numbers:** Long iron 210, Mid iron 185 and 4-wood 255. These are Will's numbers (mid iron ~184).
  * **From the brief:** 8-iron 162, assumed.
  * **Assumed exactly as at Eagle Knoll:** 5-iron 198, 7-iron 174, 9-iron 150, PW 138 and GW 126. They come from the
    Spirit Hollow approach bag (~12-yd gaps), with width and depth window scaled with carry like the engine's 8-iron.
    This is where Eagle Knoll's PW 138 came from.
  * **Assumed for Forward / Middle 12:** SW 113 and LW 100.
  * Nothing sits between 210 and 255 (the engine's "Hybrid ~235" is marked not in the bag).
* The aim surface uses an ideal club for each depth: carry interpolated, with that carry's width, depth and roll. So
  the box does not depend on the gapping. The club table does.

**Terrain:**
* The truth package is loaded per tee set through the page's own loader, so each set has its own tee, line and frame.
* Each ball lands where its flight meets the 3DEP 1 m DEM (`packages/gateway_national/imagery/dem.tif`):
  x = flat carry + 0.839 x (tee height minus ground height). 0.839 = 1/tan 50 deg, the page's elevation factor.
* It then rolls the club's stated roll (+/-25 %): about 2.5 yds for a PW, 6 for a 7-iron, 8 for a 5-iron and 10 for a
  4-iron. Roll is x0.3 in rough, and the ball stops in sand, trees or water.
* **The box is the landing spot and the number is the carry.** The ball finishes about one roll past the box.

**Green and pins:**
* The green is the truth-map polygon.
* Pins are uniform over it, at least 4 yds inside the edge (222-288 pin spots per green on a 1-yd grid).
* Putting: Broadie by feet + 0.06, plus the slope term (an assumed size): 0.02 strokes per 1 % of downhill grade, from
  the DEM plane fit.

**After the shot:**
* Short game by lie + 0.15 within 40 yds; beyond that, the engine's table.
* Trees: Broadie recovery. Water: 1 + rough from the drop.

**Statistics:**
* Common random numbers throughout.
* Back: 6,000-swing 1-yd grid, then a 0.5-yd refine on 40,000 fresh swings. The other sets use 3,000 / 16,000.
* The centre and DECADE aims are scored on the refine swings. Margins are paired means +/- SE.
* Box = aims within 0.02 strokes of the best, at least 4 yds each way.
* One box per page wind class: calm, and 7 / 14 / 24 / 32 mph averaged over four directions. Back solves every class;
  the other sets copy classes 1-3 from class 0 (on Back they differ by 0.5 yd or less).

**Forecast** (`weather/forecast_gateway_national.json`, fetched Nov 7): conditions at each hole's time, with a 9:00
shotgun on 1 and 14 min a hole (4 at 9:42, 7 at 10:24, 12 at 11:34, 14 at 12:02, 17 at 12:44).
* Sat: NNW 8-9 mph, 41-49 F.
* Sun: SW 6.5-7.5 mph, 48-58 F.

## 2. Map and terrain check (imagery, lidar)

Each green and its surround was checked against these sources:
* NAIP 2023 RGB (0.6 m and the package's 0.3 m) and the 0.3 m NIR as CIR;
* NAIP 2022 CIR;
* the 2014 Madison Co. lidar HAG and DTM;
* the truth-map polygons overlaid, with 10-40 yd rings.

The renders were scratch only.

| hole | green outline | around it (in the tee frame) | verdict |
|---|---|---|---|
| 4 | matches the smooth putting surface; the green runs front-right to back-left | two bunkers short-left (match); mown rough left and long to the path at 195-200; trees and OB right from ~+40 | OK |
| 7 | matches (the surface may run ~1-2 yds further right than mapped; no effect) | bunker right, small bunker short-left; trees short-left (2014 canopy, thinner on NAIP 2023); native long-right from ~3 yds past the back-right edge (map fix of Nov 9), trees long-right; pond beyond | OK |
| 12 | matches | peninsula: water left (~3-5 yds off the edge), long (~22 yds past the centre at the line) and a creek 24-30 yds short; bunker long-right | OK, CIR water edges match the map |
| 14 | matches (NAIP 2023 is the reference; NAIP Plus is older and shadowed here) | bunker left; tree line 1-3 yds behind the back edge (canopy edge = map edge within ~2 yds); trees left beyond the bunker; native strip down the left of the corridor 0-185 yds (map fix of Nov 9), 30+ yds from the centre | OK |
| 17 | matches | three bunkers short-right, one left; trees right 5-8 yds off the edge; trees long beyond the cart path | OK; the "trees long" polygon takes in the path strip (3-5 yds, 25-30 yds past the centre), no effect |

No native or prairie lies within ~12 yds of any par-3 green. The par 3s were never hand-traced: their surrounds are
OSM bunker / water / fairway plus lidar canopy. Reviewer A (EYECHECK_A_1109.md) found the same for 4.

**Map revision.** Everything here is on the truth package as rebuilt on Nov 9 (commit 5403fb168). That revision added
native on 7 and 14. 4, 12 and 17 are unchanged in it (same zones, tees and green), so their results stand. 7 and 14
were re-solved for every set. Lies are painted in package order, as the page's `lie_at` does: later zones win, so where
the new native bands overlap the lidar trees, the trees stay. The Back boxes for 7 and 14 did not move; on the other
sets, the 14 boxes moved by 0.5-1 yd at most.

Three map questions were run as variants (`mapvar`). Each gives the regret of keeping the page aim:
* **4, if the smooth "fairway" lobe left of the green is putting surface** (reviewer A's note; pins there too): best
  (0, -5), regret 0.009 +/- 0.001.
* **4, reviewer A's C4** (native 24-54 yds past the centre): best (2, -5), regret 0.000.
* **7, if the 2014-lidar trees short-left are now rough:** best (-1, -4), regret 0.002 +/- 0.001.

**There is no map error near a par-3 green that changes a box, so no polygon edit is proposed.**

**Lidar.** The 3DEP DEM and the 2014 lidar DTM agree on the greens:
* plane-fit grades within 0.25 % and drops within 1 ft, with residual 0.1-0.2 ft;
* tee-to-green drops, Back: 4 -2.8 ft (uphill), 7 +0.8, 12 +2.3, 14 +2.5, 17 +2.5. That is under 1 yd of plays-like.

Green tilt (fall line, DEM):

| hole | tilt |
|---|---|
| 4 | 1.5 % up to the right, 1.0 % back-to-front |
| 7 | 1.6 % back-to-front, 0.8 % up to the right |
| **12** | **3.65 % right-to-left**, falling toward the water left |
| 14 | 0.45 % (flat) |
| 17 | 1.6 % back-to-front |

**Card vs map.** On 4 and 7 the map's tee-to-centre is 4-5 yds shorter than the card for every set:
* Back 176 / 176 against 180 / 180;
* Tips 192 / 199 against 197 / 204;
* Middle 7 155 against 160 (the Middle tees on 7 and 12 are estimated).

The page builds its number from the card, so on those two holes the page number is ~4 yds longer than the model's
carry to the same spot. **On the day, take the distance to the green centre from the tee plate or a laser, and add the
box depth.**

## 3. Result: Back

Depth is + long of the green centre, lateral is + right. Strokes are for the hole. The plays-like number is the carry
in 70 F, flat-ground yards.

| hole | best aim (lat, depth) | box lat / depth | EV | gain vs centre aim | gain vs old DECADE aim (its lat, depth) | plays like, 50 F calm: page (card) / model (map) [to centre] | 35 F / 65 F | 10 mph head / tail |
|---|---|---|---|---|---|---|---|---|
| 4 (180) | **+2.5, -5.5** | -1..5 / -8..-3 | 3.192 | **0.067 +/- 0.001** | 0.049 +/- 0.001 (1.8, -1.1) | **178** / 174 [180 / 179.5] | 180 / 176 | 191 / 170 |
| 7 (180) | **0, -3.5** | -3..2 / -6..-2 | 3.194 | **0.032 +/- 0.001** | 0.039 +/- 0.001 (-0.5, +0.4) | **179** / 175 [178.4] | 181 / 177 | 192 / 171 |
| 12 (131) | **+0.5, -1.5** | -2..2 / -3.5..0.5 | 3.069 | 0.007 +/- 0.001 | 0.007 +/- 0.001 (1.8, -1.6) | **131** / 131 [132] | 132 / 129 | 141 / 125 |
| 14 (200) | **+0.5, -6.5** | -3..3 / -10..-4 | 3.281 | **0.100 +/- 0.002** | 0.063 +/- 0.001 (1.0, -1.2) | **196** / 196 [202] | 198 / 194 | 210 / 187 |
| 17 (195) | **-1.5, -6.5** | -4..1 / -9..-4 | 3.244 | **0.090 +/- 0.001** | 0.049 +/- 0.001 (-1.8, -1.6) | **191** / 188.5 [195] | 193 / 188.5 | 205 / 182 |

How the numbers are built:
* Page = (card + aim depth + dz) / temperature factor. This is the template's formula and what the page will show.
* Model = the carry that lands a solid strike on the aim, at the map distance and the DEM height there.
* The wind column is the page's `wind_grid.plays_like` at 50 F. A crosswind does not change the number.

**Wind classes and the forecast days barely move the box:**
* 7-32 mph: within 1 yd of calm (14: -7..-7.5; 17: -7).
* Sat / Sun best aims:
  * 4: (2, -5.5) / (2.5, -6.5)
  * 7: (0.5, -3.5) / (0, -3)
  * 12: (0.5, -1.5) / (0.5, -2)
  * 14: (1, -6.5) / (1, -6.5)
  * 17: (-1.5, -7) / (-1, -6)
* Model carries to those aims, Sat / Sun:

  | hole | Sat | Sun |
  |---|---|---|
  | 4 | 169 (tail-ish, 41 F) | 179 (into, 48 F) |
  | 7 | 176 (across) | 170 (helping) |
  | 12 | 134 | 134 |
  | 14 | 194 | 189 |
  | 17 | 190.5 | 181.5 (helping) |

**Why the boxes sit short.** These are long par 3s, played with 5- to 7-irons that roll 6-8 yds. The model lands the
ball 3.5-6.5 yds short of the centre, so it **finishes at about the centre**. A centre landing finishes 6-8 yds long.
On 14 and 17 the trees are 1-8 yds behind the green, so that miss is expensive: 0.09-0.10 strokes a hole. Laterally:
* 4 aims 2.5 right, onto the wide front-right half of a diagonal green and away from the short-left bunkers.
* 17 aims 1.5 left, away from the trees right.
* 12 is the exception. It is a short club with little roll onto a peninsula, and the box is the centre (gain 0.007).
  Half a yard right, toward the high side and away from the water, is a wash.

**Club** (stock carries, lateral aim optimised; margin over the runner-up). This depends on the **assumed** 5- / 7- /
9-iron / wedge carries.

| hole | calm 50 F | Sat | Sun |
|---|---|---|---|
| 4 | 7-iron by 0.21 (lands -5.4) | 7-iron by 0.04 | 6-iron / 7-iron TIE |
| 7 | 7-iron by 0.29 | 7-iron by 0.21 | 7-iron by 0.07 |
| 12 | GW by 0.09 (lands -6) | PW by 0.15 | PW by 0.18 |
| 14 | 5-iron by 0.14 | 5-iron by 0.09 | 6-iron by 0.14 |
| 17 | 6-iron by 0.15 (lands -10) | 6-iron by 0.05 | 6-iron by 0.06 |

## 4. Sensitivity (Back; `robust`: 4,000-swing grid, 20,000 fresh swings)

Each cell gives the best aim under the variant, then the regret of keeping the page aim.

| variant | 4 | 7 | 12 | 14 | 17 |
|---|---|---|---|---|---|
| temp 35 F / 65 F | (3,-6) / (2,-5); 0.000 | (0,-4) / (0,-3); 0.000 | (0,-2) / (0,-1); 0.001 | (1,-7); 0.000 | (-1,-8) / (-1,-7); 0.000 |
| dispersion +/-15 % | (2..3,-6); <= 0.001 | (0..1,-4); 0.000 | (0..1,-1); 0.000 | (0..1,-6..-7); <= 0.002 | (-1..-2,-7); 0.001 |
| depth spread x2 | (3,-6); 0.001 | (1,-4); 0.006 | (0,-1); 0.000 | (3,-9); 0.010 | (-3,-8); 0.002 |
| 10 mph head / tail | (3,-7) / (2,-6); 0.005 / 0.000 | (0,-5) / (0,-3); 0.000 / 0.001 | (0,-2) / (0,-1); 0.001 | (1,-9) / (1,-6); 0.014 / 0.001 | (-2,-8) / (-1,-6); 0.006 / 0.001 |
| 10 mph from left / right | (2,-6); 0.000 | (0,-3); 0.000 | (0,-2); 0.000 | (1,-7); 0.000 | (-1,-7); 0.000 |
| 20 mph head | (3,-9); 0.023 | (2,-7); 0.022 | (2,-3); 0.010 | (2,-13); 0.055 | (-3,-12); 0.035 |
| **roll x0.5 (soft greens)** | (1,-3); **0.017** | (-1,-1); 0.011 | (0,0); 0.001 | (1,-3); 0.010 | (-1,-4); 0.014 |
| roll x1.5 (firm) | (3,-8); 0.020 | (-1,-5); 0.008 | (0,-2); 0.002 | (1,-9); 0.018 | (-2,-10); 0.020 |
| **carry +5 / -5** | (2,-10) / (2,-1); **0.064 / 0.048** | (0,-8) / (0,+1); 0.059 / 0.055 | (0,-6) / (0,+3); 0.074 / 0.080 | (1,-12) / (1,-2); 0.046 / 0.032 | (-1,-12) / (-1,-3); 0.044 / 0.031 |
| no slope / slope x2 | 0.000 | 0.000 | 0.001 | 0.000 | 0.000 |
| trees half the cost | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| no mishits | 0.003 | 0.005 | 0.004 | 0.001 | 0.003 |
| pins 3 / 6 yds in | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

* **The box is robust.** Temperature (35-65 F), dispersion (+/-15 %, depth x2), crosswind and wind to 10 mph, the
  slope term, tree cost, pin inset and mishits all leave the page aim within 0.015 strokes of the variant's best,
  usually within 0.005. The variant's best is within 1-1.5 yds (14 into 10 mph: 2.5 yds).
* **Into a strong wind, land it shorter.** At 20 mph into, 14 wants -13 (regret 0.055) and 17 wants -12 (0.035). The
  page's wind-class boxes average the four directions, so they do not know about this. Rule of thumb: into the wind,
  pick the short end of the box.
* **Green firmness is the main model uncertainty.** The box is a landing spot, so it moves with the roll: soft greens
  land 2-3 yds deeper, firm greens 2-3 yds shorter. The cost of not adjusting is 0.01-0.02. On soft November greens
  (dew, rain) take the long end of the box. If the ball is checking up, land it nearer the centre.
* **The number matters more than the box.** If Will's carry with the club is 5 yds off the model, he loses 0.03-0.08 a
  hole at the page aim. **Confirm the 5- / 7-iron and wedge carries with Will**; they are assumed.

## 5. Other tee sets (own tee, own frame; 3,000 / 16,000 swings)

Columns: best aim, box, gain vs centre, gain vs DECADE, plays like at 50 F calm (page from card / model from map).

| set | 4 | 7 | 12 | 14 | 17 |
|---|---|---|---|---|---|
| The Tips | (2,-6.5), -1..5 / -9..-5; 0.093; 0.083; 194 / 189 | (0.5,-5), -3..3 / -6.5..-2.5; 0.076; 0.113; 202 / 197 | (1,-2.5), -1..3 / -4.5..-0.5; 0.020; 0.006; 153 / 152.5 | (1.5,-11), -2..5 / -14..-8; 0.206; 0.125; 232 / 232 | (-2.5,-10), -6..0 / -13..-7; 0.161; 0.087; 224 / 219 |
| Champions | (2,-6.5), -1..5 / -9..-4; 0.092; 0.080; 191 / 187 | (0.5,-4.5), -3..3 / -7..-2; 0.059; 0.083; 198 / 193.5 | (0.5,-2), -1..3 / -4..0; 0.015; 0.006; 147 / 146 | (1.5,-10.5), -2..5 / -13..-8; 0.198; 0.120; 228 / 229 | (-3,-9.5), -6..0 / -12..-6; 0.152; 0.090; 218 / 215 |
| Middle | (2,-3.5), -1..4 / -6..-2; 0.031; 0.017; 153 / 150 | (0,-2.5), -3..1 / -5..0; 0.017; 0.021; 160 / 155 | (0,-1), -1.5..2.5 / -3..1; 0.005; 0.012; 115 / 114 | (0,-5.5), -3..3 / -8..-3; 0.067; 0.038; 181.5 / 182 | (-1,-5), -3..1 / -7..-3; 0.059; 0.033; 170 / 168 |
| Forward | (1.5,-2.5), -1..4 / -4..0; 0.011; 0.005; 130 / 129 | (-1,-2), -3..1 / -4..0; 0.014; 0.024; 145 / 142 | (-0.5,0), -2.5..1.5 / -2..2; 0.001; 0.035; 91 / 92 | (0.5,-3), -3..2 / -6..-1; 0.023; 0.010; 154 / 154 | (-0.5,-3.5), -3..1 / -6..-1; 0.035; 0.019; 154 / 153 |

The pattern is the same on every set: land short by about one roll. The longer the club, the shorter the landing,
because the roll and the long misses grow with it.

**Tips and Champions 14 (232 / 228 to play) and 17 (224 / 218).** These fall in Will's gap between the long iron
(210) and the 4-wood (255):
* The model's best real club is the long iron, landing 14-33 yds short. The 4-wood flies into the trees long.
* The page's number is the ideal carry, not one of his clubs.
* Back is the event set, so this is a note for the tee picker only.

**Forward 12 (90).** A partial lob wedge. The bag model has no partial shots, so the club margin there means nothing.

**Drawing.** The page draws every set's box in the Back frame, rotated by the tee-angle difference: 8.5 deg on Forward 4 and
12, and about 5 deg on Forward 14 and Tips 7. That moves a corner by at most ~1 yd. The depth used for the number is the
set's own.

## 6. Uncertainty / not verified

* The pins are uniform, not the day's sheet.
* The slope term's size is assumed (0 and x2 shown: no effect here).
* The DEM / lidar is 2014-15, so greens rebuilt since would not show.
* The roll is the club's fairway roll, applied to greens: see the roll rows.
* The short-iron and wedge carries are assumed. Card vs map is 4-5 yds on 4 and 7.
* Lateral wind drift is aimed off, not modelled as a miss. The wind classes are direction-averaged (see the 20 mph
  into row).
* Water banks are not modelled (12): a ball stopping on the rough bank stays dry.

## 7. To wire it (engine agent)

Add to `course_data/courses/gateway_national/config.json`:

```
"par3_targets": "course_data/courses/gateway_national/par3_targets.json"
```

The engine then calls `par3_targets.install(cfg, BW, meta["tee_set"])` (v2_course.py ~l.1193). No other key is needed.
The Middle alt-base page (`truth_middle`, tee_set Middle) takes the file's own Middle entries.
`par3_targets.json` covers all five sets. `d["p3club"]` names the club for the two forecast days. On Tips and
Champions 14 / 17 it reads "4-iron", which lands 14-33 yds short; a template showing p3club should not show it for
those sets.

## 8. Pattern check against published data, Nov 14 (the par-3 irons were Tour-level; now x 1.5)

The par-5 study (second_pass/FAIRWAY_WOOD_DATA.md) found the approach patterns Tour-accurate. Same test for the
par-3 tee irons (`E.shot_set`, mishits on; flat ground, nothing around, pin where a solid strike finishes, calm,
70 F, 40,000 swings; green = 15-yd-radius circle):

| from | club | pattern | 95 % width | proximity (mean) | on the green | good shot (>= 90 % of the distance, within 10 yds) |
|---|---|---|---|---|---|---|
| 135 | PW | as built | 28 | 25 ft | 92 % | 82 % |
| 135 | PW | x 1.5 | 42 | 36 ft | 75 % | 64 % |
| 135 | PW | x 1.75 | 49 | 41 ft | 65 % | 56 % |
| 180 | 7-iron / 6-iron | as built | 35 / 37 | 31 / 33 ft | 83 / 80 % | 73 / 70 % |
| 180 | 7-iron / 6-iron | x 1.5 | 52 / 55 | 44 / 47 ft | 60 / 56 % | 54 / 52 % |
| 180 | 7-iron / 6-iron | x 1.75 | 61 / 65 | 50 / 53 ft | 51 / 46 % | 47 / 45 % |
| 200 | 5-iron / 4-iron | as built | 40 / 43 | 36 / 39 ft | 75 / 70 % | 66 / 63 % |
| 200 | 5-iron / 4-iron | x 1.5 | 60 / 65 | 50 / 54 ft | 51 / 46 % | 48 / 45 % |
| 200 | 5-iron / 4-iron | x 1.75 | 70 / 76 | 57 / 62 ft | 41 / 37 % | 42 / 39 % |

Data: PGA Tour proximity 125-150 yds 24 ft, 175-200 34 ft, 200-225 42 ft; Tour hits 50 % of greens from 205; a
scratch amateur's pattern is about 1.5 x the Tour's (36 / 51 / 63 ft), scratch 80 ft and about 25 % of greens from
200-225 by distance (with a longer club than Will's), scratch "good shot" from 200: 39 %. So the patterns as built
were at or inside Tour level; x 1.5 gives Tour x 1.4-1.5 = the scratch level club for club. A tee is a perfect lie,
so x 1.5 (the low end; the deck shots use 1.75).

Applied: config `par3_pattern_mult` 1.5 (read by `opt/par3_target.py`; `P3_PATTERN_MULT=1.0` gives the run
before); `par3_decade.py solve` + `par3_ladder.py`, every set, both rule sets. The margins of section 0 are
geometric and unchanged; every target still meets them as before (the shortfalls on 4, 14, 17 are 0.1 smaller).
Inside the margins the best point moves away from the costly side, and the shorter club holds a little longer.
Back (plays number and club on the page, before -> after):

| hole | target (yds right, yds past the middle) | Sat, Drop | Sun, Drop | Sat, Lost ball | Sun, Lost ball |
|---|---|---|---|---|---|
| 4 | (2.5, -3.5) -> (3.5, -4.5) | 180 7-iron -> 179 7-iron | 184 6-iron -> 183 6-iron | 179 7-iron -> 179 7-iron | 184 6-iron -> 183 6-iron |
| 7 | (-1.0, 1.5) -> (-1.0, 1.5) | 189 6-iron -> 189 6-iron | 188 6-iron -> 188 6-iron | 189 6-iron -> 189 6-iron | 188 6-iron -> 188 6-iron |
| 12 | (-0.5, -0.5) -> (2.0, -0.5) | 134 PW -> 134 PW | 133 GW -> 133 GW | 134 PW -> 134 GW | 133 GW -> 133 GW |
| 14 | (2.5, -4.0) -> (3.5, -6.0) | 202 5-iron -> 200 5-iron | 201 5-iron -> 199 5-iron | 202 5-iron -> 200 5-iron | 201 5-iron -> 199 5-iron |
| 17 | (-0.5, -4.5) -> (-1.0, -5.0) | 198 5-iron -> 197 5-iron | 195 5-iron -> 195 6-iron | 198 5-iron -> 197 5-iron | 195 5-iron -> 195 6-iron |

Club changes on Back: 17 on Sunday 5-iron -> 6-iron (195, "5-iron close": the two are within a hundredth);
12 on Saturday under Lost ball PW -> GW ("PW close"; under Drop the PW stays, "GW a tie"). Saturday, Drop: no club
changes; 12's box moves 2.5 yds right, 14's 2 yds shorter and 1 right, 4's 1 yd shorter and 1 right. Other sets:
Forward 14 Saturday 8-iron -> 9-iron. No tee shot on a par 4 or 5 changed.

## 9. Sideways and distance apart, Nov 14 late (replaces the x 1.5 of section 8)

Golfer, on the par-5 page: "why is it saying 79 yards wide with like a 220-yard shot? Wouldn't that be a lot more
narrow?" The same single multiplier was on the par 3s (x 1.5 on width AND distance window: a 4-iron 64 yds wide
at 220, against 43 for the same club in the tee table). Proximity data cannot tell a sideways miss from a short
one; split now, as off the fairway (second_pass/FAIRWAY_WOOD_DATA.md, "Sideways and distance apart"), with less of
everything because a tee is a perfect lie. `config.json approach_pattern.par3_tee`, read by `opt/par3_target.py`
(wraps `E.opts` and `E.shot_set`); `P3_PATTERN_MULT=1.5` gives the run before:

* width x 1.1 (one sigma 3.0-3.2 deg; his Driver 3.6); distance window x 1.75;
* slightly-mishit share 12 % (sand wedge) rising to 22 % (4-wood), each going 85-95 % of the carry (was 12 % at
  92-95 %); bad mishits 2.5 % -> 4 %.

Same flat test as section 8 (200,000 swings; before = x 1.5 -> now):

| club, pin at | 95 % width | 95 % depth | proximity (mean) | on the green | good shot | 15+ yds short |
|---|---|---|---|---|---|---|
| PW 141 | 42 -> 31 | 25 -> 33 | 36 -> 34 ft | 74 -> 77 % | 63 -> 71 % | 4 -> 11 % |
| 8-iron 167 | 48 -> 36 | 29 -> 39 | 41 -> 40 ft | 65 -> 66 % | 56 -> 64 % | 5 -> 15 % |
| 6-iron 192 | 55 -> 41 | 33 -> 44 | 47 -> 46 ft | 56 -> 57 % | 51 -> 58 % | 7 -> 20 % |
| 4-iron 220 | 64 -> 48 | 37 -> 50 | 54 -> 53 ft | 46 -> 46 % | 44 -> 51 % | 11 -> 25 % |

Proximity and greens hit are unchanged (the scratch level of section 8); the misses moved from the sides to short.

Applied: `par3_decade.py solve` + `par3_ladder.py`, every set, both rule sets (4 and 8 min). The margins of section
0 are geometric: 7 and 12 fit; 4, 14 and 17 remain lesser-of-two-evils with the penalty margins met (other edges
short by 1.6, 1.5 and 0.3 yds at best). Back (target = yds right, yds past the middle; margins left / right / short /
long through the target):

| hole | target before -> now | margins now | Saturday (Drop) | Sunday (Drop) |
|---|---|---|---|---|
| 4 | (2.5, -3.5) -> (2.5, -3.5) | 12.0 / 13.0 / 11.0 / 13.8 | 7-iron, no change | 6-iron, no change |
| 7 | (-1.0, 1.5) -> (-1.0, 1.5) | 11.0 / 10.9 / 14.6 / 13.3 | 6-iron, no change | 6-iron, no change |
| 12 | (2.0, -0.5) -> (0.5, 0.0) | 15.2 / 11.3 / 16.8 / 11.9 | PW, plays 134 -> 135 | GW, no change |
| 14 | (3.5, -6.0) -> (3.0, -5.0) | 10.6 / 8.0 / 12.6 / 20.8 | 5-iron, plays 200 -> 201 | 5-iron, plays 203 -> 204 |
| 17 | (-1.0, -5.0) -> (-1.0, -5.0) | 8.8 / 12.2 / 12.1 / 19.1 | 5-iron, no change | 5-iron, no change |

No club changes on Back, either day, either rule set (Lost ball, 4 on Sunday: the 7-iron is now "a tie" with the
6-iron, was "close"). With less sideways scatter the box moves back toward the middle (12: 1.5 yds left; 14: 1 yd
deeper). Other sets, club changes on the page: The Tips 12 Saturday 9-iron -> 8-iron (both rule sets); Middle 7
Saturday 8-iron -> 7-iron (both rule sets, "8-iron a tie / close"), Sunday under Lost ball 8-iron -> 7-iron ("a
tie"). Expected strokes on Back: 4, 12, 14, 17 better by 0.02-0.09 (less ball in the trouble at the sides), 7 worse
by 0.06 (short is the costly miss there).

Tee table (par 4s and 5s), not changed: its iron rows (long iron 43 yds wide, mid iron 37; the 8-iron's 32 in the
hole 10 lay-up table) are the patterns as built = Tour-tight, and they feed the tee-shot solve (hole 16's long-iron
row, hole 10's lay-up table), so they were left alone. Consistent with this section they would be 48 / 41 / 36
wide (10 % more) with the distance window 75 % deeper (28 -> 50, 25 -> 44, 22 -> 39 yds) and more short misses.

