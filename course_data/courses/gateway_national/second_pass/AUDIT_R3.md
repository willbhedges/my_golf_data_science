# Gateway National: independent audit, round 3 (Nov 13, page = commit 632c4927c)

**Verdict: NO.** Nothing found that puts a wrong club on the page or moves an aim by 3+ yds, on any tee set, either
day, either start. The engine change (native = penalty area) is priced as described and is the same in the Python
engine, the C kernel and the wind grids. Six findings below; the top two are wording on hole 10, the rest are small.

Scope: code diff 7668a5896..632c4927c (v2_course.py, wind_page_template_course.html, config.json, trace.py,
holes_truth.py, par3_target.py; nothing changed in spirit_hollow/v2 or fastsolve); 360 page states driven with
Playwright (5 tee sets x Sat / Sun x start on 1 / 10 x 18 holes); all 36 Back and Middle phone screenshots read, plus
Sunday 4, 9, 10, 11, 12, 18. Single-hole solves only.

## Findings, by consequence

### 1. Back 10, Saturday: three statements on one card disagree about the two woods (wording, no club or aim change)
Back, Sat, start on 1 (11:06, 44 F, 5 mph) and start on 10 (9:00, 35 F): headline and star = 4-wood, aim 20 / 21 L.
- pill: "4-wood and 2-wood are level here: the 4-wood misses the green complex less often"
- table row: `2-wood | 256 | 271 | 8 | 65 | better by 0.020 here`
- note: "Calm-day book (no wind, 44 F): 2-wood by 0.012 ... With 2-wood at 44 F: fairway 47%."

Cause: `wind_page_template_course.html` line 450 (the `lost` column) has no branch for `r.pref`, so the true best
club prints "better by"; the note keeps the book's club. Fix: in that line, when `r.pref` and the club is within
`h.prefer.within` of the pick, print "level" (as the pill says); and when `r.pref`, drop the "With <book club> at
T: fairway N%" sentence. Middle 11 is fine as it is (Driver row reads "≈ tie", gap 0.003-0.005).

The rule sits near its edge on Saturday: page gap 0.020-0.021 against the 0.03 band, and the calm 35 F grid cell
has the 4-wood 0.050 behind (exact engine: 2-wood 3.772, 4-wood 3.822). A dead-calm 9:00 start on 10 would show the
2-wood instead. Both woods aim within 2 yds of each other, so the line does not move.

### 2. Middle 10, Sunday: the 4-wood is shown finishing 19 yds past the middle of the green
Middle, Sun 11:06, 49 F, 3 mph behind: `4-wood | carry 253 | total 269 | To green 21` on a 251-yd hole (Sat: 261
total, 13). The engine still has it 0.144 ahead of the long iron and says a 235 hybrid "would gain 0.163", so the
pick is right among full swings; a golfer reads "269 total, 251 hole" and will not swing full. Hole 10 from Middle
is accepted; this is only the Sunday number. Fix (text): a Middle `set_notes` pill on 10, e.g. "A full 4-wood
finishes past the middle today: a smooth one is enough". Back is fine (Sun 270 total on 271, To green 8).

### 3. Penalty-area reference point: two approximations, tested, no effect on any pick
`model.Raster._water_entry` (unchanged code, now applied to every native band) walks back along the straight line
from the tee: (a) a ball deep in a band that runs along the hole is dropped where that straight line entered it,
up to 120 yds back (hole 11: median 20 yds back, 90th percentile 68); (b) past 120 yds the walk gives up and the
ball is priced at its own distance, the cheapest case (Back: 1,438 such cells in reach on 11, 10,422 on 15, 9,231
on 2). Real curving balls cross later than (a) assumes. I re-solved all 26 Back / Middle tee holes in the central
world with the drop capped 25 yds back and with the drop level with the ball: same club on 26 of 26; largest aim
moves 11 Back +16.5 -> +18.0 and 11 Middle +18.5 -> +19.0, every other hole within 0.5 yd. No action before the
event. Afterwards: make the 120 a clean cap (`min(entry, dist + cap)`) so (b) is not a cliff.

### 4. "N on the card" pill repeats the header
Shown whenever plays-like differs from the card by 3+ (template line ~494), e.g. Back 12 Sat: header "Par 3 · 131
yds", target 131, pill "131 on the card"; also 7 Sat / Sun, 4 Sun, 14 Sun, Middle 7, 12. Not wrong, adds nothing in
simple mode. Fix: skip it when `D.simple`.

### 5. Why sentence against the note, Back 1
Why: "75% fairway"; note under it on Saturday: "With driver at 35 F: fairway 76%". One point. Fix: write 76, or
"about three in four".

### 6. Middle 8, Sunday, start on 10 only: one 65 F grid cell sits on the aim limit
The calm 65 F cell for the 4-wood is -60 (the search bound) against -34 at 50 F; at 52 F it carries about 5 % of
the weight and pulls the shown aim (30 L) about 1 yd. Under the 3-yd bar; re-solve that cell after the event.

Also noted, no action: `V2_NATIVE_PENALTY` is read for every course, so exporting it in a shell changes any
course solved in that shell; no test covers the relabel (a two-line test that Eagle Knoll keeps `native` zones and
Gateway has none after `activate` would pin it). The par-3 solver prices native as 1 + rough at the ball's own
distance (par3_target.py), not at the crossing point: stated in its comment, and the difference is a few yards.

## Checked and found correct

**Native = penalty area (A1).**
- `activate` relabels `native` -> `water` on every hole; zone order kept; no other lie changes (11: 37,200 cells,
  10: 41,418, all water; every other cell identical). Roll is unaffected (native already stopped the ball).
- Price = 1 + rough at the crossing point: max |S - (1 + rough(entry))| over all ex-native cells 2e-7 on 10 and 11.
  Eight points on 11 by hand (walk back in 0.25-yd steps): e.g. ball (302.0, -13.0) crossed at (292.5, -12.6),
  rough there 3.416, cell 4.418; ball (306.5, -24.5) crossed 46.5 yds back, 3.573 -> 4.574; all eight within 0.003
  (the engine steps 1 yd). Old model on the same points: 4.52-4.98.
- Python engine against the C kernel on 10 and 11: lie, entry distance and strokes rasters identical (max diff 0.0).
- The committed book and card grid of 10 and 11 are reproduced bit for bit by today's code and config (1,281 club
  cells each, 0 aim differences, max EV difference 0), so the page numbers come from the rule as committed.
- `--exact` (256 draws, 3,000 / 12,000 swings, 16,000-swing grid) against the page: 10 2-wood 26.0 L, 3.7909 vs
  3.7932, margin 0.011 vs 0.012; 11 Driver 16.5 R vs 16.0 R, 4.3830 vs 4.3805, margin 0.025 vs 0.024. Grids, 183
  cells a hole: pick differs in 1 (10) and 3 (11) cells, none by more than 0.01; aims of the pick within 1.5 yds.
- Off elsewhere: only Gateway's config has the key; the default path does nothing.

**Tie rules (A2).** In all 360 states the headline club, the Play line, the table star, the line's end and the
oval use the same club and aim (one variable in the template; checked from the DOM and the SVG). The rule fires
exactly when the preferred club is inside its band: Back 10 Sat (gap 0.020), Middle 11 both days (0.003-0.005);
not on Back 11 (0.024-0.027 > 0.015), nor on Back 10 Sunday, where the 4-wood wins outright by 0.053-0.090. No
"Calm-day pick" or "models split" pill appears beside the rule's pill.

**Par 3s (A3).** 100 states (5 sets x 2 days x 2 starts x 5 holes): the parts shown add up to the plays-like
number in all 100; the club equals an independent reading of the ladder in all 100; every change-over pill equals
my recomputation, and none is missing. Back: Sat 4 176+1-5+8 = 180, 7-iron, change-over at page number 181.6 ->
"182 or more: 6-iron"; Sun 4 183, 6-iron, "178 or less: 7-iron"; Sat 7 187 / Sun 189, 6-iron; Sat 12 137 PW, Sun
131 GW with "134 or more: PW"; Sat 14 201, Sun 205 5-iron with "203 or more: 4-iron"; Sat 17 197, Sun 196 5-iron
with "192 or less: 6-iron". The ladder leans to the shorter club by 1.5-3.7 yds past the midpoint between two
carries (14: 5-iron until 207.7, midpoint 204), which is carry plus release, not an error.

**18 (A4).** Between da3938fda and 632c4927c only hole 18 differs in both course modules (HOLES[18], FRAMES;
BEARINGS only Middle 18, 153.71 -> 153.72); green moved 57.8 px = 17.0 yds (Back) and 26.2 px = 7.7 yds (Middle).
Book and all 11 Back grids + the Middle grid: only hole 18 changed, at all three temperatures, with 0 cells left
identical. The page offers 18 at 0, +20 and -140; "Move this tee" +17 lands on +20.

**Pictures (A5).** Green centre drawn against the photo on Back 1, 3, 8, 10, 11, 16, 18 and Middle 3, 9, 18: on
the putting surface within about 3 yds each time; tee markers on a tee pad on all ten. Photos reach the green on
3, 8 and 18.

**Page read (B).** No page errors; no hazard word in any of the 360 states' text; "To green" equals the straight
line from the finishing spot to the green centre on every tee shot (within 1.5); totals above carries everywhere.
Ovals: 13, 16, 18 and 1 have a fairway bunker inside the oval's edge, none at its centre; 8's line crosses the
unmown inside of the bend as intended. Saturday and Sunday aims differ by up to 11 yds on the same hole (9: 5 R
and 16 R) while the finishing spot is the same within 2 yds: that is the crosswind allowance and the Aim line says
so.
