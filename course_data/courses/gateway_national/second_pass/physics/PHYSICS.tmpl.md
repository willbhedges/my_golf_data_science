# Gateway National second pass: ball-flight physics review (P), Nov 13 2026

Scope: the wind / temperature / pressure / elevation / carry / roll rules behind the Gateway page, checked against an
independent trajectory model built for this review (`second_pass/physics/`). Nothing in the engine or the Gateway
data was edited. Section 5 gives the corrections as values of the engine's own knobs, ranked by size, for the
integrator. Checkpoint 1 at 02:35Z Nov 13 (sections 0-6); section 2e and section 7 added 02:50Z.

## 0. Summary

The engine's physics has **no sign or unit error**. Its air-temperature rule, its driver head / tail wind rule and its
elevation rule agree with the reference model and with the published numbers to within ~1.5 yds. Four things are off
or missing, and together they move this weekend's numbers by 2-5 yds:

| # | finding | size at this weekend's forecast | size at 10-15 mph | fix |
|---|---|---|---|---|
| 1 | **The ball itself is cold.** The engine's 0.075 %/F is the AIR only (it matches TrackMan's air-density figures). A ball that has been out for a hole is at air temperature and comes off the face ~1 % slower at 45 F (Carlsson et al. 2019: 0.6-0.7 m/s, 3-4 m of carry between 4 C and 18 C balls). | **Driver -3.2 yds carry, mid iron -1.9; par 3s +2 yds** | same | temperature coefficient 0.00075 -> 0.00115 per F (ball at air temperature), or keep the ball warm (section 5) |
| 2 | **Barometric pressure is not in the model.** Sat / Sun sit under a 1027 / 1031 hPa high: the air is 1.2-1.5 % denser than the same temperature on an average day, worth another 6-8 F of cold. | **Driver -1.2 (Sat) / -1.5 (Sun) yds, irons -1; par 3s +1 yd** | same | feed the air term T - 6 F (Sat) / T - 8 F (Sun), or fold into the coefficient: 0.00135 per F in total |
| 3 | **Crosswind drift is too small, and falls off with club length when it should not.** Drift is (crosswind) x (flight time lost to drag), and every full shot from driver to 8-iron hangs 6.3-7.1 s. Engine: 1.14 yds per mph for the driver, 0.79 for the mid iron, 0.67 for the 8-iron. Reference: 1.5-1.7 for all of them. | **irons up to +2.4 yds of drift (par 3s: 5.5-6.5 yds on 7, 14, 17 Sat instead of 3-3.7), driver +1.4** | driver +4 to +5 yds, irons +6 to +9 | `DRIFT_PER_MPH_275` 1.14 -> 1.5 with the new sensitivities of #4 |
| 4 | **Irons and fairway woods lose / gain too little in a head / tail wind.** The driver rule is right (-15 at 10 mph: published -12 to -18). The per-club multiplier is too flat: TrackMan's own 6-iron figure is -39 / +23 yds at 20 mph; the engine gives -30 / +18. | par 3s **+0.5 to +1 yd** (winds are 2-4 mph along the line); 4-wood -1 yd | mid iron -6 yds at 10 mph into, 4-wood -4 | `SENSITIVITY`: 2-wood 1.2, 4-wood 1.3, hybrid 1.4, long iron 1.5, mid iron 1.65, 8-iron 2.0 (driver stays 1.0) |

Applied together (the "patched" columns of section 3): **every par-3 number goes up 1-4 yds (mean +2.8)**, the
**driver carries ~4 yds less than the page says on every hole** (2-wood / 4-wood -4, irons -3), and crosswind aims
move 1-2.5 yds further into the wind. `OPTIMIZE.md` 4b already shows what carry -5 does to the picks: **hole 10
flips from 4-wood to 2-wood (by 0.065)** and hole 9 becomes a 4-wood / Driver tie; nothing else changes club.

Not errors, but worth knowing:

* **The newest forecast is colder at the start** (fetched 02:27Z Nov 13): Sat 24 F at 7:00, 35 F at 9:00 (the page's
  Nov 12 file has 40 F), 46 F at noon; a hard freeze overnight, so expect a frost delay and frozen ground early.
  Sunday's wind has backed from SE to E (100-110 deg). 5 F is ~1 yd of carry. The integrator should refresh the
  forecast file once more.
* **Wind speed is the largest unknown of all.** Open-Meteo says 4-5 mph at 10 m, the NWS grid says 2-3. In light,
  cold, sunny weather that factor of two is real (calm pockets, puffs). Every wind number above scales with it.
* **Roll** cannot be improved from physics (section 4): the bounce model says the driver's 25 yds becomes ~11 on
  soft, thawed turf and ~43 on firm or frozen turf. The engine's stated totals are fine as a centre; the day's turf
  decides.
* Wind height profile (10 m forecast vs the ball's 0-31 m): the effect is +7-9 % on every wind number (0.6 yd at
  5 mph), not worth a change. Gusts: 1 mph of turbulence at this forecast; negligible (section 2e).
* If Will's 275 / 300 are on-course numbers from Lawrence (~900 ft), Gateway's 410 ft is another 1.8 % of air density
  (driver -1.6 yds, irons -1). Not applied: we do not know where the numbers were measured. Ask him.

## 1. The reference model

Code: `second_pass/physics/refmodel.py` (flight, air, wind profile, bounce and roll), `fit_aero.py` (coefficients),
`will.py` (Will's clubs), `compare.py` (engine vs reference; calls the engine's own functions), `report.py`
(the tables below). Results: `physics/results/reference.json`, `compare.json`. Run: `python3 fit_aero.py; python3
will.py; python3 compare.py; python3 report.py` (about a minute).

* **Flight.** 3-D point mass, drag and lift along the air-relative velocity, spin axis fixed in space (so a tilted
  axis curves the ball and a crosswind does not), midpoint integration at 10 ms.
* **Coefficients.** Cd = 0.137 + 0.283 (1 - exp(-S / 0.219)), Cl = 0.416 (1 - exp(-S / 0.188)), S = spin ratio.
  Fitted to the TrackMan PGA and LPGA Tour average tables (23 clubs, driver to wedge: ball speed, launch, spin ->
  carry, apex, landing angle): rms 2.8 yds of carry, 1.7 yds of apex, 4.1 deg of landing angle (the model lands irons
  3-6 deg shallower than TrackMan reports). Both coefficients rise with spin ratio and level off, as in Bearman &
  Harvey (1976) and Smits & Smith (1994). The Tour tables were typed from memory of the published sheets.
* **Independent check of the density response.** Not fitted to it, the model gives a driver +0.39 % of carry per
  1 % less air density; Titleist's altitude rule (+1.16 % per 1000 ft) is 0.40.
* **Model spread.** Every sensitivity is also run with two other coefficient sets: Smits & Smith's published 1994
  fit (a higher-drag ball) and the repo's own `elevation/adjust.py` linear fit (good for woods, wrong for short irons:
  it needs a 157 mph 8-iron). A fourth variant with a Reynolds-number drag term fits the Tour tables slightly better
  but predicts almost no carry change with air density, which the altitude rule contradicts; it is kept only to
  show that the Tour tables alone cannot pin the density response.
* **Spin decay** d(omega)/dt = -2e-5 omega V / r (Smits & Smith; ~4 % a second).
* **Air.** Density and viscosity from temperature, station pressure (sea-level pressure and 410 ft), humidity.
* **Wind.** The forecast is the 10 m wind. Neutral log profile u(z) = u10 ln(z / z0) / ln(10 / z0), z0 = 0.03 m (open
  flat grassland; 0.1 m also run), held below 0.2 m. A driver peaks at 31 m, where the wind is 1.19 x the 10 m
  value; it starts and lands in slower air.
* **Will's clubs.** Launch angle and spin are Tour-like for each carry; ball speed is solved so the 70 F calm carry
  at 410 ft is his number:

{{calib}}

  Driver 168 mph at 11.5 deg / 2550 rpm is a ~113 mph swing: consistent with 275 carry. The 4-wood needs 161 mph
  (teed, 10.5 deg / 3500): fast for a 4-wood, so his 255 is probably a low-spin strong 3-wood flight. It does not
  matter for the sensitivities.
* **Bounce and roll.** Haake's turf-impact model as used by Penner ("The run of a golf ball", Can. J. Phys. 2002):
  the ball rebounds from a crater tilted back by 15.4 deg x (v / 18.6 m/s) x (angle / 44.4 deg), restitution falling
  with impact speed, friction 0.40 that either slides or grips, repeated bounces, then rolling at the stimpmeter
  deceleration. The fairway's crater scale is calibrated so the driver runs Will's 25 yds at 70 F.

Limits: a point-mass model with one ball's coefficients; no dimple-pattern or ball-model differences; the wind is a
steady mean profile; launch conditions are assumed, not measured.

## 2. Engine vs reference, club by club

### 2a. Temperature (carry change from 70 F, yds)

{{temp}}

* **Air only.** Engine -5.2 (driver) / -3.5 (mid iron) at 45 F. Reference -5.7 / -5.0; the linear set -4.9 / -8.0;
  Smits -9.1 / -6.3. Published TrackMan (their model, via Rice / Bubany): 9 yds for a driver and "almost 8" for a
  6-iron between 40 F and 100 F, i.e. -3.8 / -3.3 at 45 F; Rice's coach-camp test: ~2 yds per 10 F for a driver (-5).
  The engine sits inside the published range for every club. **No change to the air coefficient.**
* **The ball.** Carlsson, Nilsson, Hellstrom, Tinmark & Carlsson (2019, Proc. IMechE Part P, doi 10.1177/1754337118812618): balls stored 24 h
  at 4 C launched 0.6-0.7 m/s slower and carried 2.9-3.9 m less than balls at 18 C or 32 C, with a driver. That is
  0.04 % of ball speed per F. The model turns it into -3.2 yds (driver) and -1.9 (mid iron) at 45 F, on top of the
  air. Magazine robot tests give larger numbers (frozen balls); the range used is 0.02-0.07 % per F.
* A ball carried in a trouser pocket starts a hole near 70-80 F and cools toward the air with a time constant of
  roughly 12-23 minutes (a conduction estimate, section 7, not a measurement), so over a 14-minute hole it loses
  half to two thirds of its warmth. Swapping to a pocket-warm ball of the same model on each tee recovers most of item 1. That is allowed
  between holes (Rule 6.3a; with the one-ball local rule it must be the same model). Warming a ball with a hand
  warmer or heater during the round is not (Rule 4.2a).
* **Pressure and humidity.** At the hole times Saturday's sea-level pressure is 1027-1028 hPa and Sunday's
  1030-1031 (Open-Meteo, 02:27Z Nov 13), humidity 30-55 %. Against 1015 hPa and 50 % that is +1.2 % and +1.5 % of
  density: the same as 5.8 F (Sat) and 7.6 F (Sun) colder. Humidity alone is under 0.2 yd.

### 2b. Wind: carry and drift at 70 F (yds)

Engine: `spirit_hollow/wind.adjust` with the page's sensitivities (8-iron 1.3). Reference: 10 m forecast wind with
the log profile, and the same speed uniform with height (how launch-monitor "wind" settings and rules of thumb are
quoted).

{{wind}}

* **Head / tail, driver.** Engine -15.1 / +10.7 at 10 mph. Reference -17.4 / +14.1 (uniform), linear set -14.4 /
  +11.2. Published for a driver: -13 / +9 on a 250 drive (Thomas), -12 / +9 (Foresight), -18 (Golf Australia),
  300 -> 259 / 333 at 20 mph (Golf.com). The engine is in the middle. Keep.
* **Head / tail, irons.** TrackMan's 6-iron (183 carry): -39 / +23 yds at 20 mph. Reference mid iron (185), uniform
  20 mph: -43 / +24; Smits set -40 / +19. Engine: -30 / +18. The engine's iron multiplier (1.25) is too small.
  Scaling the reference by the TrackMan 6-iron ratio (x0.91 head, x0.96 tail) and dividing by the engine's driver
  curve gives the multipliers of section 5: long iron 1.5, mid iron 1.65, 8-iron 2.0, 4-wood 1.3, 2-wood 1.2. They
  match the old rule "1 % per mph into, a bit over 0.5 % per mph down" for irons.
* **Drift.** For a drag-dominated flight in a steady crosswind w, drift = w x (T - R / v0x): flight time minus the
  time the ball would need at its launch speed. Driver: 6.9 s - 3.4 s = 3.5 s; 8-iron: 6.3 - 3.0 = 3.3 s. So a
  10 mph crosswind (4.5 m/s) moves every full shot 15-17 yds. The trajectory integration agrees (14.4-17.6 uniform,
  15.4-18.9 on the profile), and so do the two other coefficient sets for the woods. Backspin lift has no sideways
  component in a crosswind, so this is a drag result and does not depend on the lift model. The engine's 11.4 yds
  for a driver is at the low end of the rules of thumb (10-15 yds on a 250-yd drive, which hangs a second less);
  its 7.9 for a mid iron and 6.7 for an 8-iron are about half of the physics. Section 5 uses 1.5 yds per mph, a
  little under the model, because the forecast 10 m wind is an open-terrain number and tree lines take some off.
* **Wind height.** Profile vs uniform: +8 % on the head-wind loss, +2 % on the tail-wind gain, +7 % on drift
  (z0 0.03 m); +10 % / +9 % with z0 0.1 m. The engine's note says under 3 %. At 5 mph this is 0.6 yd. No change.

### 2c. Elevation

{{misc}}

* Engine tee shots: carry delta from its own 2-D flight onto the DEM profile, e.g. hole 2 driver, landing 8.0 ft
  below: +3.4 yds. Reference: 0.41 yd per ft for the driver, 0.36 for the 4-wood, 0.32 for the mid iron: +3.3. Hole
  15 (7 ft up): engine -4.0, reference -3.0 (the engine flies the real profile, which rises before the landing
  spot). Agreement within 1 yd on every Gateway hole.
* Par 3s: the page uses 1 / tan 50 deg = 0.28 yd per ft. Reference irons land at 46-50 deg (TrackMan: 50): 0.28-0.32.
  Gateway's greens are within 3 ft of their tees: the difference is under 0.1 yd.
* A head wind steepens the landing by almost 1 deg per mph (mid iron: 46 deg calm, 52 at 5 mph into, 41 at 5 mph
  down), which matters for roll and for the green (section 4), not for these flat holes' carry.

### 2d. Lateral dispersion in wind

The engine widens the pattern x1.07 per 10 mph of head wind and narrows it x0.94 down wind (Ping). The reference
(a 3-deg tilted spin axis flown in the wind) gives x1.11 / x0.89 for the driver and x1.17 / x0.84 for the mid iron.
At this weekend's 2-4 mph along the line that is 1-2 % of a 65-yd pattern: under 1 yd. No change now; for a 15 mph
day the iron value should be about double the engine's.

### 2e. Gusts and the scatter they add

A forecast gust is a ~3-second peak, about mean + 3 sigma of the turbulence, so sigma = (gust - mean) / 3 (the
engine's rule; the neutral surface-layer value for open ground is 0.17 x the mean, gust 1.5 x the mean). A ball does
not feel a point gust: it averages the gust field over 6.5 s and ~230 yds of path. With a 100 m turbulence length
scale that keeps 0.73 of sigma (0.58 with 50 m). Extra scatter, in quadrature with the swing's own (driver 17.5 yds
lateral, 8.8 carry; mid iron 9.2 / 5.6):

| wind (mean, gust) | turbulence felt by a flight | driver lateral sigma (wind across) | driver carry sigma (wind along) | mid iron lateral | mid iron carry |
|---|---|---|---|---|---|
| Sat 4.5, gust 8 | 0.85 mph | 17.5 -> 17.6 | 8.8 -> 8.9 | 9.2 -> 9.3 | 5.6 -> 5.9 |
| Sun 3.5, gust 6 | 0.6 mph | 17.5 -> 17.5 | 8.8 -> 8.8 | 9.2 -> 9.2 | 5.6 -> 5.75 |
| 10, gust 17 | 1.7 mph | 17.5 -> 17.7 | 8.8 -> 9.5 | 9.2 -> 9.6 | 5.6 -> 7.0 |
| 15, gust 25 | 2.4 mph | 17.5 -> 18.0 | 8.8 -> 10.4 | 9.2 -> 10.0 | 5.6 -> 8.8 |

* This weekend gusts add under 0.3 yd to any sigma. Nothing to change.
* Gusts widen DEPTH far more than width, and irons far more than the driver: at 15 gusting 25 a mid iron's carry
  sigma grows by half. The tee-shot wind grid calls `wind.adjust` without `gust_mph`, so it has no gust scatter at
  all; the par-3 solve passes it. On a windy weekend the grid should pass the gust too.
* The engine's rule uses the point sigma, not the flight average, so where it is used it over-states the added
  scatter by about a third (10.9 vs 8.8 for the mid iron at 15 gusting 25). Scale `sig_w` by 0.75 when it matters.
* A fade or a draw does not ride or fight a crosswind differently in the model: the drift of a 4-deg fade, a
  straight ball and a 4-deg draw in a 10 mph crosswind is the same to 0.1 yd (the wind adds to the curve). The
  engine's "curvature riding / fighting the wind is not modelled" loses nothing.

## 3. Gateway, this weekend

Forecast rows: the page's file (fetched Nov 12 14:05Z), 9:00 start on hole 1, 14 minutes a hole, as the page
interpolates. Pressure and humidity from the 02:27Z Nov 13 fetch (`physics/results/open_meteo_1113_0227Z.json`).
"Patched" = the engine's own functions with the section 5 values swapped in (`compare.py`, class `patched`); the
reference columns are the independent model and are there to show the patch lands in the right place, not to be
copied.

### 3a. Par 3s (Back): the plays-like number

Target = card + the box's best depth (4: 174.5, 7: 176.5, 12: 129.5, 14: 193.5, 17: 188.5). Page now = my
re-computation of the template's formula on the stored 5-mph grid (it reproduces PAR3.md's 50 F calm column:
178 / 179 / 131 / 196 / 191). Head + = into the face; cross + = from the right; drift + = ball moves right.

{{par3}}

* The arithmetic is right end to end: target + elevation + wind + temperature, each with the correct sign (4 on
  Saturday is down wind and plays shorter; 12 on Saturday is into it). The grid interpolation (0 -> 5 mph, 30-deg
  steps) is within 0.2 yd of the direct formula.
* What moves: the temperature chip (+3 -> +5 or +6: ball and pressure) and a larger wind chip on the holes with
  2-4 mph along the line. **New numbers: 4: 178 Sat / 184 Sun; 7: 183 / 185; 12: 136 / 130; 14: 198 / 203;
  17: 196 / 194** (page now: 176 / 181; 180 / 181; 133 / 129; 195 / 199; 193 / 191). With a pocket-warm ball take
  2 yds off each.
* The page gives no crosswind allowance on a par 3 (only the arrow). On Saturday 7, 14 and 17 have 4-4.5 mph
  straight across: **5.5-6.5 yds of drift to the right** at 1.5 yds per mph (reference 7). That is a third of a
  green. If the wind is the NWS's 2-3 mph instead, halve it.

### 3b. Tee shots (Back), Driver

{{tee}}

All clubs, the 13 tee shots x 2 days:

{{tee_summary}}

* The patch moves the engine about four fifths of the way to the reference; the rest is the reference's larger
  air-density response for fairway woods and irons, which the published TrackMan figures do not support, so it is
  left out.
* Totals move with the carries (the roll rule is unchanged).

## 4. Roll and the turf (fairways and greens)

The engine does not compute roll. It takes Will's totals (driver 25 yds, 2-wood and 4-wood 15, long iron 10, mid iron
7, 8-iron 5), scales them for landing slope (DEM) and for a head / tail wind, and leaves them alone for temperature.
The Haake / Penner model, calibrated to the driver's 25:

* **Other clubs at 70 F:** 2-wood 17, 4-wood 11, long iron 7, mid iron 1, 8-iron about 0 (it checks). Will's 2-wood
  number fits; his 4-wood and iron rolls are a few yards more than a mid-firm fairway gives a ball landing at
  42-48 deg with 2800-6800 rpm left. It is 3-6 yds on clubs that are rarely the pick. No change.
* **Turf:** firm (dry, dormant, or frozen underneath) 43 yds for the driver; soft (thawed surface, dew) 11. The
  model is very sensitive here, as real turf is. The engine's prior of x0.8-1.2 on roll is narrower than a November
  day's range of roughly x0.5-1.7. Saturday starts on frozen ground (24 F at 7:00, soil surface 22 F, 48 F by 9:00
  in the sun) and will be wet on top once it thaws: long bounces first, then little run.
* **Cold:** a 45 F ball lands ~1.5 % slower and 0.5 deg steeper: the model takes 4 yds (15 %) off the driver's roll.
  The engine has no such term; it is inside the turf uncertainty.
* **Wind:** engine x0.89 at 5 mph into, x1.11 at 5 mph down. The bounce model reacts far more strongly (the landing
  angle moves ~1 deg per mph), which I do not trust beyond the direction. No change.

**Greens (PAR3.md's "land 3.5-6.5 yds short").** PAR3.md lets each iron roll its fairway figure on the green: 6 yds
for a 7-iron, 7 for the 6-iron, 8 for a 5-iron, 10 for the 4-iron. Reference landings at the forecast (45-50 F air,
cold ball): 53-55 mph, 44-49 deg, 4200-5900 rpm left. The bounce model on a normal green (stimp ~9.5): 7-iron 2 yds,
6-iron 5, 5-iron 8-12, 4-iron 15+; soft green 0-4 for all of them; firm green 8 (7-iron) to 25+ (5-iron). So:

* For a 6-iron PAR3.md's 7 yds is in line. For a 7-iron it is ~3 yds too much: a 7-iron shot (PAR3.md's club on
  4 and 7) would do better landing 1-3 yds short than 3.5-5.5. With the new plays-like numbers (183-185) those
  holes become 6-irons anyway. For a 5-iron on 14 it is fair to slightly low.
* The spread between soft and firm is larger than any of that. PAR3.md's own roll rows are the right hedge. One
  cheap observation settles it on the day: watch the first full iron land on the practice green or on 4. If balls
  are plugging or checking within 2 yds, play the page number + 3; if they release 10, the box is right or a
  touch long.
* Down-wind par 3s release more: 4 on Saturday (3.7 mph behind) lands at 44 deg instead of 48, which doubles the
  model's roll.

## 5. Corrections for the integrator, ranked

Values of existing engine knobs. None of them is applied here. `compare.py`'s `PATCH` dict and `patched` context
manager show the exact swap; `results/compare.json` has every number before and after.

1. **Temperature coefficient: 0.00075 -> 0.00115 per F** (ball at air temperature). Page effect: par 3s +2 yds;
   driver carry -3.2 yds at 45 F (-4.5 at 35 F), irons -2. Where: `model.central()["temp_k"]` (tee shots: needs the
   wind grids and the calm-day run re-solved) and the page's `temp_k` (par 3s: a page rebuild only; `v2_course.py`
   line 1359 passes `M.central()["temp_k"]` to the template, which uses it only in `solvePar3`).
   If the re-solve is not possible, the par-3 change alone is safe and is the larger part for the scorecard, and the
   page text should say "driver carries ~4 yds less than shown once the ball is cold".
2. **Pressure: air term at T - 6 F (Sat) and T - 8 F (Sun).** Page effect: par 3s +0.8 / +1.1 yds; driver -1.2 / -1.6.
   Where: no knob exists. Simplest equivalent for this weekend: use **0.00135 per F** instead of 0.00115 in item 1
   (it reproduces "ball + pressure" within 0.6 yd of driver carry between 38 F and 52 F on both days). Warm-ball equivalent: 0.00095.
3. **Crosswind drift: `wind.DRIFT_PER_MPH_275` 1.14 -> 1.5**, together with item 4 (the two multiply). Resulting yds
   per mph: driver 1.50, 2-wood 1.70, 4-wood 1.74, long iron 1.50, mid iron 1.37, 8-iron 1.36 (reference 1.5-1.9).
   Page effect at the forecast: aims 1-2.5 yds further up wind on the tee shots; needs the wind grids re-solved.
   For the par 3s a line of text is enough: "Sat 7, 14, 17: wind across, allow 5-6 yds".
4. **Head / tail multipliers: `wind.SENSITIVITY` = Driver 1.0, 2-wood 1.2, 4-wood 1.3, Hybrid 1.4, Long iron 1.5,
   Mid iron 1.65, 8-iron 2.0** (now 1.0 / 1.0 / 1.05 / 1.1 / 1.15 / 1.25 / 1.3). Page effect at the forecast: par 3s
   up to +1 yd into the wind and -1 down wind (`wind_grid.plays_like` uses "Mid iron"; set at page build); 4-wood
   -1 yd into 4 mph. At 10 mph: mid iron -6 yds, 4-wood -4.
5. **Refresh the forecast** (colder Saturday start, Sunday wind from the E). ~1 yd.
6. Not recommended to change: air-temperature coefficient, driver wind curve, elevation rule, roll rule, wind
   height profile, gust model.

Safety of 1-4: all four are multiplicative coefficients read at call time (`W.SENSITIVITY`, `W.DRIFT_PER_MPH_275`
are module globals used inside `adjust`; `temp_k` is a `central()` keyword). They can be set from
`v2_course.install_engine` behind a config key (e.g. `"engine": {"wind": {"sensitivity": {...},
"drift_per_mph_275": 1.5}, "temp_k": 0.00135}`) so other courses keep their numbers. The Bayesian prior draws
`temp_k` from U(0.0005, 0.0009) in `decide.py` line 59: for a cold-ball world that should be U(0.0010, 0.0016).

## 6. What would make this exact

* Will's launch-monitor numbers (ball speed, launch, spin, landing angle) for driver, 4-wood and a 6-iron: replaces
  the assumed launch conditions; the sensitivities would move by ~10 %.
* Where and in what weather his 275 / 300 were measured (altitude, temperature, launch-monitor "normalised" or
  on-course): settles the pressure / altitude baseline (1-2 yds).
* Ten drives with a pocket-warm ball and ten with a ball left out for 20 minutes, on a launch monitor on a cold day:
  settles item 1 for his ball (the study's range is 0.02-0.07 % per F).
* An anemometer reading at 2 m on the first tee: the forecast models differ by a factor of two.
* Turf: how far the practice-range and first-fairway balls run.

## 7. Validation of the reference model against published numbers

Tour launch conditions (driver 167 mph / 10.9 deg / 2686 rpm; 6-iron 127 / 14.1 / 6231), sea level, 77 F, wind
uniform with height. `physics/validate.py`, `results/validate.json`.

| check | published | reference (fit) | linear set | Smits set | engine rule |
|---|---|---|---|---|---|
| 6-iron, 20 mph head / tail | -39 / +23 (TrackMan) | **-41 / +22** | -51 / +33 | -47 / +26 | -30 / +18 |
| driver, 10 mph head / tail | -12 to -18 / +9 to +11 | -17 / +14 | -15 / +12 | -22 / +19 | -15 / +11 |
| driver, 20 mph head / tail | -41 / +33 on a 300 carry (Golf.com) | -38 / +24 | -34 / +20 | -48 / +35 | -36 / +21 |
| driver, 40 F -> 100 F air | +9 (TrackMan), ~+12 (Rice) | +13.6 | +12.4 | +20.6 | +12.4 |
| 6-iron, 40 F -> 100 F air | ~+8 (TrackMan) | +11.5 | +15.6 | +17.8 | +8.2 |
| driver at 5,280 ft | +6.1 % (Titleist) | +6.5 % | +5.5 % | +10.7 % | none |
| driver, 10 mph crosswind | 10-15 yds on a 250-yd drive (rules of thumb) | 16.1 (lag-time formula 17.0) | 15.2 | 17.4 | 11.4 |
| 6-iron, 10 mph crosswind | ~5 (Hole19) to ~12 (aim-off charts) | 14.9 | 20.2 | 15.5 | 7.9 |
| ball speed -> carry | ~2 yds per mph (driver) | 2.0 driver, 1.6 6-iron | 2.2 / 1.3 | 1.5 / 1.6 | |

* The reference reproduces TrackMan's 6-iron wind figure to 2 yds and Titleist's altitude rule to 0.4 %, neither of
  which it was fitted to. It over-predicts TrackMan's own temperature figures by about half (13.6 vs 9-12 for the
  driver, 11.5 vs 8 for the 6-iron); that is why section 5 leaves the engine's air coefficient alone and does not
  use the reference's larger air response.
* The crosswind rows are where the published material is weakest: I found no measured drift table, only rules of
  thumb that are quoted for shorter, lower flights and for the wind a golfer feels at 2 m (about 0.7 of the 10 m
  wind over open grass). 1.5 yds per mph of FORECAST wind is the physics for a 6.5-7 s flight; if Will knows from
  experience that a 10 mph crosswind moves his 6-iron 10 yds, that is 1.0 per mph of felt wind and the two agree.
* Launch assumptions: re-solving Will's driver at 13.5 deg / 2200 rpm or 10 deg / 2900 rpm, or his mid iron at
  16 deg / 5400 or 13 deg / 6800, moves every sensitivity above by under 6 % (cold: -8.6 to -9.3 yds for the
  driver at 45 F with a cold ball; 10 mph head: -18.1 to -19.9; drift 16.6 to 18.2).
* Wind profile check against the forecast itself: Open-Meteo's 80 m wind is 1.15-1.2 x its 10 m wind at the playing
  hours on both days (the neutral log law gives 1.36), so by day the profile correction is about half of the 7-9 %
  in section 2b. At 7-8 am Saturday the layers are decoupled (2 mph at 10 m, 8 mph at 80 m): a high ball will find
  wind that cannot be felt on the tee.
* How fast a ball cools (first conduction mode of a 42.7 mm rubber sphere, surface coefficient 12-30 W/m2/K): time
  constant 12-23 minutes; 72-84 % of the pocket warmth is left after 4 minutes, 31-54 % after a 14-minute hole.
  A ball that sat in a car overnight starts Saturday at 25-35 F, colder than the air at 9:00.

Sources: Bearman & Harvey, Aeronautical Quarterly 27 (1976) 112; Smits & Smith, Science and Golf II (1994) 340;
Penner, Can. J. Phys. 80 (2002) 931 and Rep. Prog. Phys. 66 (2003) 131; Haake, Science and Golf (1991); Carlsson et
al., Proc. IMechE Part P (2019), doi 10.1177/1754337118812618; TrackMan Tour averages and normalisation notes (6-iron -39 / +23 yds at
20 mph; 40 F -> 100 F: driver +9, 6-iron +8 yds); Titleist altitude rule; Open-Meteo forecast API.
