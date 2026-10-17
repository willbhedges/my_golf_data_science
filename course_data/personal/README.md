# Personalisation: the golfer's own shot pattern

The tee-shot plan (`mozingo/tee_strategy.py`, v2 in `spirit_hollow/v2/`) depends most on the golfer's
dispersion: driver pattern width, miss shape, carry and roll, mishit rate. Until now that came from the
golfer's stated numbers and a prior (driver width lognormal, median 70 yds, 90% 62-80;
`spirit_hollow/final_decision.py`, `review_stats/prior_patch.py`, `v2/decide.prior_draws`). The v2 report
leaves calibration open ("the golfer's own fairway and miss data would settle it"): a 70-yd pattern gives more
fairways and fewer big misses than published 0-5 handicap data, and at about 82 yds some picks flip.

This folder is the path from data a golfer already has to a **player profile** the app and the planner use:

```
exports (CSV / JSON / form) --parsers.py--> bayes.Data --bayes.Model.fit--> posterior --player_profile.py--> golf_player/1
                                                    ^ summary stats: emulator.py (v2 simulator on the home holes)
```

| File | What |
|---|---|
| `parsers.py` | launch-monitor CSV (Garmin R10/R50, TrackMan, FlightScope, Rapsodo, SkyTrak, ... through column aliases), on-course tee shots (generic GPS CSV, arccos-api JSON, Golf Pad shots CSV), summary stats (manual form, Golf Pad rounds CSV, Garmin Connect scorecard JSON) |
| `manual_stats.schema.json` | the manual stats form (fairways, misses L/R, tee penalties, average drive), read off any app's stats screen |
| `bayes.py` | the model: prior, likelihoods for the three data kinds, posterior (Laplace + importance sampling, Metropolis fallback) |
| `emulator.py` | summary-stat emulator: the v2 course simulator over a bank of 4,096 patterns on Spirit Hollow's 14 Black-tee driving holes, plus a polynomial response surface |
| `player_profile.py` | builds the `golf_player/1` JSON, `to_v2_params` (profile draw -> v2 model overrides), `picks_at_interval` (Spirit Hollow picks across the width interval) |
| `PROFILE.md` | **the profile contract** |
| `simulate.py`, `validate.py` | synthetic golfers and the recovery study |
| `examples/profile_example.json` | a profile fitted to the synthetic examples (R10 session + 30 logged tee shots + a manual form) |
| `test_personal.py` | unit tests (`python3 -m pytest -q course_data/personal`, ~45 s) |
| `examples/` | synthetic example files for each parser, a bag, a manual form |
| `output/` | `recovery.md` / `recovery.json` / `recovery_fits.jsonl`, `emulator_spirit_hollow.npz`, `emulator_check.json` (GitHub Actions) |

Heavy work runs on GitHub Actions: `.github/workflows/personal_validate.yml`, triggered by a change to
`course_data/requests/personal_validate.json` (bank in 6 shards, then the recovery study in 12 shards,
max-parallel 6; the merge job commits `course_data/personal/output/` only).

```
python3 course_data/personal/player_profile.py --bag course_data/personal/examples/bag.json \
    --lm course_data/personal/examples/garmin_r10_session.csv --shots course_data/personal/examples/tee_shots.csv \
    --manual course_data/personal/examples/manual_stats.json --out profile.json
```

## 1. What golfers can already export (October 2026; no paid sign-ups, no API keys)

Researched on the web this session. Vendor support pages for TrackMan, Golf Pad and 18Birdies could not be
fetched from here (blocked); their rows rest on search-engine extracts of those pages. Column names marked
"aliases" are matched by `parsers.ALIASES`; check one real file before relying on them.

| Source | What you get | Format and fields | How to get it | Shot level? | Parser |
|---|---|---|---|---|---|
| **Garmin Approach R10 / R50** (launch monitor) | every range/sim shot | CSV, one row per shot. Header (EN, confirmed from the R10Progress project's types): `Date, Player, Club Name, Club Type, Club Speed, Ball Speed, Smash Factor, Launch Angle, Launch Direction, Backspin, Sidespin, Spin Rate, Spin Rate Type, Spin Axis, Apex Height, Carry Distance, Carry Deviation Angle, Carry Deviation Distance, Total Distance, Total Deviation Angle, Total Deviation Distance, Note, Tag, Air Density, Temperature, Air Pressure, Relative Humidity`; a second row gives units (`[mph]`, `[yds]` or `[m]`); German/Spanish headers in other locales | Garmin Golf app (2.10+): open the session, share -> CSV. Free with the device. Known issues: a comma in a club name breaks the CSV; range targets are not exported | yes (carry, side) | `parse_launch_monitor` |
| **TrackMan** (TPS, Range) | shots of a session | "Trackman CSV". Parameters Carry, Total, Side (carry side), Side Total (perpendicular to the target line); exact headers aliased; metadata lines before the header and a units row are handled | TPS: All Activities -> Shot History -> Table View -> export icon -> "Trackman CSV". Free where you already use TrackMan | yes | `parse_launch_monitor` |
| **FlightScope Mevo / Mevo+** | session shots | CSV (`stats.csv`, no date in the name). Basic: ball/club speed, smash, **carry**, launch angle, spin, height, club. Lateral landing, total and roll need the **Pro Package (paid)** | myflightscope.com -> session -> export | carry only without Pro | `parse_launch_monitor` (side optional) |
| **Rapsodo MLM2PRO, SkyTrak, Foresight, Uneekor** | session shots | CSV from the vendor app/portal; carry / total / side ("Side Carry", "Offline", "Lateral") aliased, not verified | vendor app export | yes | `parse_launch_monitor` |
| **Arccos** (on-course sensors) | every tracked shot | No official export (the web dashboard is view-only). The unofficial, read-only `arccos-api` (pip; your own login; GET requests only) returns round detail JSON: `holes[].shots[]` with `shotId, clubId, clubType, startLat, startLong, endLat, endLong, distance, noOfPenalties, shotTime`, `holes[].isFairWay`; `arccos clubs --json` maps clubIds; also smart distances and `/clubs/dispersion`. `arccos export -f csv` is round-level only; use `arccos export --detail -f json` | `pip install arccos-api; arccos login; arccos export --detail -f json -o rounds.json` (Arccos membership the golfer already has) | **yes** (GPS start/end) | `parse_arccos_json` |
| **Garmin Golf** (watch, CT10) | scorecards; CT10 shots | No official export ("scorecards cannot be exported", Garmin forum). Community bookmarklet (github.com/gsingers/garmin_golf) pulls Connect's scorecard JSON (per-hole fairway outcome, penalties; CT10 shot data); users report the endpoint is unreliable. Some watches keep scorecard `.FIT` files reachable over USB | browser console script on Garmin Connect | CT10 only | `parse_garmin_scorecards` (summary) |
| **Golf Pad** | rounds; holes and shots | Free: rounds CSV (score, putts, penalties, fairways hit), emailed link valid 3 days. Premium "comprehensive" export adds holes (fairway hit / miss direction) and shots (club, lie, shot length, distance from the fairway centre, - = left) | app -> export history | Premium (paid) | `parse_golfpad_rounds`, `parse_golfpad_shots` |
| **18Birdies** | stats screens | "Playing data can not be exported to a CSV, Excel, or other spreadsheet" (18Birdies help); a GDPR/CCPA data request exists | read the stats screen | no | manual form |
| **Shot Scope** | stats screens, web dashboard | No official export found (dashboard: rounds, club distances, analysis). A third-party site asks for your Shot Scope password: not recommended. GDPR request: support@shotscope.com | read the stats screen | no | manual form |
| **TheGrint** | stats screens | No export found. Fairway hit / missed, PRO "Advanced Score Selector" logs far left / far right | read the stats screen | no | manual form |
| **Golfshot** | stats screens | Nothing found on an export | read the stats screen | no | manual form |
| **Manual** (any app, or a paper card) | fairways, misses L/R, tee penalties, average drive | `manual_stats.schema.json` (counts or percentages) | type it in | no | `parse_manual` |
| **This app** (prototype logger) | tee shots with the plan's aim | generic shot CSV: `club, start_lat, start_lon, end_lat, end_lon, aim_lat, aim_lon, aim_source, penalty, penalty_side` | the app writes it when the golfer marks where the ball finished | yes, aim known | `parse_shot_csv` |

The best cheap data, in order: (1) the app logs each tee shot against **the aim it recommended** (aim known to
~3 yds); (2) Arccos via arccos-api (GPS start/end; aim unknown, measured against the tee -> hole line, so
doglegs need a target); (3) a launch-monitor session (carry, side, mishits, ratios between clubs, but range
!= course); (4) the manual form.

## 2. The model (`bayes.py`)

The pattern is v2's shot model with its unknowns made explicit, plus a Student-t lateral tail:

* good strike, club *k* (stated carry C_k, total T_k): carry ~ N(C_k + c_common + c_k, sd_k), sd_k =
  depth95_k x depth_mult / 4; lateral = b_k + s_k t_nu, with s_k = width95_k / (2 t_nu^-1(0.97725)), so
  **width95 = the central 95.45 % interval** (4 sigma for a normal: v2's `sig_lat = width / 4`).
* width95_k = W r_k: W is the driver's on-course width, r_k the club's ratio (65/70, 54/70, irons x the 4-wood,
  or interpolated by carry for any other club).
* bias b_k = beta C_k / C_driver + delta_k (a common aim/shape bias in angle, plus a club part).
* mishits as in v2: slight (rate p_s) carry x U(0.92, 0.95), lateral x 1.15; heavy (p_h) carry x U(0.65, 0.85),
  lateral x 1.5.
* roll on the home fairways = (T_k - C_k) x roll_mult, +/-25 % per swing.
* launch monitor: the range width = on-course width / f (f > 1: the range is tighter), a carry offset per
  session (ball, mat, air; range balls -5 % +/- 3 %), 1.5 yd measurement error.

**Prior** (`Prior.v2()`, the current one): W ~ LN(70, 90% 62-80), r_2w ~ LN(65/70, .04), r_4w ~ LN(54/70, .06),
others sd .08; c_common ~ N(0, 5), c_k ~ N(0, 3); depth_mult ~ LN(1.25, .2); beta ~ N(0, 2), delta ~ N(0, 1.5);
p_s ~ Beta(23.8, 174.8) (mean .12, = v2's U(.08, .16) moments), p_h ~ Beta(8, 313) (mean .025);
roll_mult ~ N(1, .115) (U(0.8, 1.2)); nu ~ LN(30, .75) (90% 9-100: near-normal, as v2); f ~ LN(1.05, .08)
(an assumption: no published range-vs-course dispersion figure was found). `Prior.generic()` is for a new user
we know nothing about: W ~ LN(82, 90% 67-100) (the published 0-5 hcp fit), bias ~ N(0, 6), carry ~ N(0, 10),
weak mishit priors. The v2 prior is **tight**: its width sd (8 % in log) is what ~75 normal shots would give.

**Likelihoods**

* (a) launch monitor: each shot's (carry, side) is a 3-component mixture (good / slight / heavy).
* (b) on-course tee shot from GPS start/end: total = carry + roll + conditions N(0, 8) (wind, slope, lie,
  temperature) + GPS N(0, 5); lateral of the resting ball = the pattern convolved with aim noise (3 yds when
  the app logged its plan, 6 for the fairway centre, 10 for the tee -> hole line) and GPS noise (Gauss-Hermite).
  Penalty / lost balls have no usable end point: they enter as **censored** laterals, P(|lat| > 35 yds) on the
  side they went (or either side).
* (c) summary stats only: fairways hit and misses L/R (binomials), tee-shot penalties (Poisson), average
  drive (normal, se = 16/sqrt(n) + 6 yds systematic for app definitions and firmness). The rates come from
  `emulator.py`: the v2 simulator (lie raster, roll-out, water/OB/lost-ball rules) run for 4,096 Sobol
  patterns over (W, bias, nu, carry, roll, mishit rates, depth) with nuisance rho, kappa and lost-ball rates
  from v2's prior, on Spirit Hollow's 14 Black-tee driving holes, 1,500 swings each, the golfer aiming at the
  fairway centre at his expected landing distance. A polynomial surface (65 terms) on the bank gives smooth,
  cheap rates; `output/emulator_check.json` has its held-out error.

All three enter one posterior: MAP (L-BFGS) + numerical Hessian, then 4,000 importance draws from a
multivariate t (df 5) around the MAP, weights truncated at mean x sqrt(n); if the ESS is below 300, an
adaptive Metropolis chain from the MAP takes over. A fit takes 4-10 s.

## 3. Recovery study: how much data is enough

Full tables: `output/recovery.md` (GitHub Actions run 39019293550: 2,726 fits, 2 failed fits dropped).
Simulated golfers: 24 drawn from each prior + 5 off-prior scenarios (book 70; published 82; wide 95 with
nu = 4 tails; fader bias +8; mishits 25 %) x 4 replicates. Bag: Driver + 4-wood. Each golfer's data are
simulated, fitted, and the posterior compared with the truth. W sd = posterior sd / median of the driver's
on-course width; for scale, **the v2 prior is 8.1 % (90 % 62-80)** and the generic prior 12 %.

| Data | v2 prior: W sd (±yds 90 % at 76) | generic prior: W sd | bias sd (yds) | 90 % coverage (prior golfers) |
|---|---|---|---|---|
| none (prior) | 8.1 % (±10) | 12 % (±15) | 2.0 / 6.0 | — |
| Launch monitor, 50 shots/club, range factor f uncertain | 6.6 % (±8.3) | 8.6 % | 1.3 / 2.1 | 92 % / 79 % |
| Launch monitor, 200 shots/club, f uncertain | **6.1 % (±7.6): the floor** | 7.4 % | 0.9 / 1.3 | 100 % / 79 % |
| Launch monitor, 200 shots/club, range = course (f = 1) | 4.0 % (±4.9) | 4.5 % | 0.9 / 1.3 | 92 % / 83 % |
| On course, aim logged, 5 rounds (50 drives + 15 4-woods) | 6.5 % (±8.1) | 8.2 % | 1.5 / 2.4 | 92 % / 92 % |
| On course, aim logged, 10 rounds | 5.6 % (±7.0) | 6.7 % | 1.3 / 1.8 | 88 % / 92 % |
| On course, aim logged, 20 rounds | 4.6 % (±5.7) | 5.3 % | 1.0 / 1.4 | 92 % / 96 % |
| On course, aim logged, 40 rounds | **3.6 % (±4.5)** | 4.1 % | 0.8 / 1.0 | 92 % / 83 % |
| On course, tee -> pin line (aim sd 10), 40 rounds | 3.8 % (±4.8) | 4.3 % | 0.9 / 1.1 | 83 % / 96 % |
| 50 LM shots/club + 10 rounds on course | 5.1 % (±6.3) | 6.0 % | 1.1 / 1.5 | 92 % / 88 % |
| Summary stats only, 20 rounds | 6.7 % (±8.4) | 8.6 % | 1.1 / 1.6 | 88 % / 92 % |
| Summary stats only, 80 rounds | 5.6 % (±7.0) | 7.3 % | 0.7 / 0.8 | 75 % / 83 % |

What this says:

1. **The current prior is already worth ~75 shots.** Driver width is only learned at the rate of 1/sqrt(2n)
   per shot (8 % = 75 normal shots), so small samples barely move it. Carry (sd 2.5-3 yds after 25 shots or
   3 rounds) and bias (1-1.5 yds after ~10 rounds) are learned much faster than width.
2. **On-course tee shots are the data that count.** About **20 rounds** of logged tee shots take the width
   from ±10 to ±6 yds, **40 rounds** to ±4.5 yds (the spacing of Spirit Hollow's break-evens), with ~90 %
   coverage. Logging the aim helps less than expected (aim sd 3 vs 10: 3.6 % vs 3.8 % at 40 rounds), because the
   aim noise adds in quadrature to a ~18-yd sigma; it matters more for bias.
3. **A launch monitor alone can't pin the on-course width**, because range-to-course is unknown: with
   f ~ 1.05 ± 8 % the posterior stops at ~6 % however many shots. If the golfer trusts the range/sim as the course
   (f = 1), 200 shots/club reach 4 %. Launch-monitor data are still the cheap way to get **carry, ratios between
   clubs, bias and mishit rate**, and they make f learnable once some on-course shots exist.
4. **Summary stats (fairway %, L/R, penalties, average drive) are weak for width** (80 rounds ~ 5.6 %, coverage
   75-83 %: the emulator's lost-ball nuisance and the fairway-centre aim assumption leak in) but good for
   **bias** (L/R split: 0.7 yds at 80 rounds) and average carry. Use them to check the profile's calibration,
   not to set the width.
5. **Prior matters for off-prior golfers.** Under the tight v2 prior a published-82 golfer is recovered at 82
   only from 40 logged rounds (LM 200 shots: 75); a fader's +8 is shrunk to +5.5-6.0 even with lots of data
   (bias prior sd 2). For new app users use `Prior.generic()` (recovers 82 and +8 at 20-40 rounds).
6. **Heavy tails are the hard part.** A 95-yd golfer with nu = 4 is read as ~80-85 everywhere: most of the tail
   is beyond the 35-yd penalty line (censored, so only its frequency is seen) and it trades off against the
   mishit rate. Tail weight needs penalty counts over many rounds; report `nu` with its wide interval.
7. **Decisions:** with on-course data, the posterior is on the right side of a break-even (>= 5 yds from the
   truth) 96-98 % of the time at 40 rounds and confident (> 90 %) 89-92 %; with the prior alone 68-74 % confident.
   With break-evens at 70.5 / 71.5 / 73.6 yds (v2 holes 18, 16, 13), a golfer near 70 is never settled; one at
   <= 66 or >= 78 is after ~20 rounds.

Emulator accuracy (`output/emulator_check.json`, held-out 20 % of the 4,096-pattern bank): fairway rate RMSE
0.015 (spread 0.11), miss-left share 0.023 (0.24), average drive 0.46 yds (30); tee-penalty rate 0.010 (0.023),
the residual being the lost-ball-rate nuisance the surface averages over.

## 4. How picks change across the profile's interval

`player_profile.picks_at_interval(profile)` re-uses the width break-evens the planner already computes
(`final_decision.py` / `decide.width_sweep`: every club's width scaled with the driver's, picks re-solved at
55-90 yds, the crossing interpolated). For each Spirit Hollow hole it reports the pick at the posterior
median and at both ends of the 90 % interval, and **P(other club right)** = the posterior mass on the far side
of a break-even.

v2 break-evens (`spirit_hollow/v2/output/v2_decisions.json`, roll-to-stated-totals run, Actions 39011577014):
18 (2-wood -> 4-wood) 70.5, 16 (Driver -> 4-wood) 71.5, 13 (Driver -> 4-wood) 73.6, 5 (Driver -> 2-wood 58.5,
2-wood -> 4-wood 64.6), 14 84.3, 6 86.6, 17 86.9; the other holes do not change between 55 and 90 yds.
**Three break-evens sit within 4 yds of the prior's 70-yd median**, so with the current prior 13, 16 and 18
are decided by the prior, not by evidence. P(other club right) at a few profiles (central-world sweeps;
`picks_at_interval` with lognormal draws):

| Profile driver width (90%) | Holes where the other club has > 5 % | Picks that differ from the plan's |
|---|---|---|
| 70 (62-80), the prior itself | 18 (46 %), 16 (39 %), 13 (26 %), 5 (15 %) | none (6 is a 0.003 tie) |
| 65 (61-69) | 5 (45 %: 2-wood vs 4-wood) | none |
| 70 (66-74), +/-4 yds | 18 (41 %), 16 (27 %), 13 (8 %) | none |
| 76 (72-80) | 13 (17 %) | 13, 16 -> 4-wood; 18 -> 4-wood |
| 82 (78-86), published 0-5 hcp | 14 (17 %) | 13, 16, 18 -> 4-wood |

The live page (v1, `final_decision.json`) has its own break-evens: 6, 14, 18 at 68-69 (2-wood/Driver -> 4-wood),
10 at 61, 17 at 77; at the prior's 70 those are 34-46 % coin flips. Ties in the plan (6 in v2) stay ties: their
margins are not about width.

Rule of thumb from the break-even spacing (70.5, 71.5, 73.6 sit 1-3 yds apart): a golfer near 70-74 never gets
all three settled; a golfer at <= 66 or >= 78 does once the 90 % interval is about **+/-4 yds** (sd ~ 3 %).
Section 3 says how much data that takes. Being wrong on a near-break-even hole costs little (the two clubs are
within a few hundredths of a stroke there); the profile matters most for golfers far from 70.

## 5. Limits

* The fitting model ignores v2's push-slice correlation (rho) and curvature loss (kappa); the profile carries
  their prior. The recovery study's summary-stat arm simulates truth *with* them.
* nu is not in the v2 engine (normal lateral + mishit scale mixture). `to_v2_params` passes width, carry,
  bias, mishit rates and roll; for a heavy-tailed golfer (nu < 10) the plan should be re-run with t laterals
  (`emulator.HoleSim` has them).
* On-course distances are not corrected for wind/elevation per shot (an 8-yd conditions term instead); with the
  course's DEM and the forecast at the time of the shot they could be.
* The emulator exists for Spirit Hollow only; another home course needs its own bank (one Actions run).
* Golfers aim where they like: summary stats assume the fairway centre; GPS shots assume the logged target or
  the tee -> hole line (10-yd aim noise). Doglegs without a target should be dropped.
* Range -> course factor f is an assumption (1.05 +/- 8 %) until a golfer has both kinds of data.
