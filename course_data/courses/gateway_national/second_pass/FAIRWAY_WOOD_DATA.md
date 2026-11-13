# Fairway wood off the deck, long approaches and go-or-lay-up: what published data says, and the par-5 re-run

Nov 13 2026. Golfer: "Study and get real data." The par-5 Second shot menu (PAR5.md) said going for the green beats
laying up by 0.2-0.4 strokes on 6, 13 and 18. That rested on an assumed pattern off the deck. This note collects
published numbers, turns them into three parameter sets, shows the calibration check and re-runs holes 6, 13, 18.

Code: `opt/par5_second.py` (`DECK_SETS`: assumed / central / pessimistic; the page data is built on central),
re-run scripts kept in the session scratchpad (`rerun.py`, `calib3.py`; they call `par5_second.play` / `summarise`).

## How far each figure could be checked

The session could run web searches but could not open pages: `mygolfspy.com`, `pgatour.com` and `pluggedingolf.com`
did not resolve (outside the session's allowed network), so no page was read at the source. Status codes below:

* **S** = the figure appears in the search engine's extract of the named page itself (not opened, not cross-read).
* **2** = quoted by a secondary page, original not seen. Treat as unverified.
* **M** = from memory, not verified.

Nothing here is verified at the source page. Where two sources disagree both are given.

## (a) Fairway wood off the deck against off a tee

| figure | population | source | status | use for Will |
|---|---|---|---|---|
| Mini driver, same club and testers: off turf 226.2 carry, 143.5 mph ball speed, 10.7 deg launch, 3,345 rpm; off a tee 237.4 carry, 146.1 mph, 13.3 deg, 3,167 rpm. Tee minus turf = 11.2 yds carry (4.7 %), 2.6 mph | MyGolfSpy test panel (amateurs), six mini drivers | https://mygolfspy.com/buyers-guide/mini-driver-off-the-tee-vs-off-the-fairway-what-the-data-shows/ | S | The only measured tee-against-turf comparison found. A mini driver (11.5-13.5 deg, deep face) loses more off turf than a 4-wood should, so 15 yds off his 255 is on the careful side of this |
| Same test: every one of the six clubs dispersed MORE from the tee than from the turf; shot area 32 % larger from the tee | same | same (the 32 % from a second summary of the same test) | S | No support for "wider off the deck" on a flat lie. The deck penalty in the data is carry and launch, not width |
| TrackMan PGA Tour average 3-wood: 107 mph club, attack angle -2.9 deg, 158 mph ball, 9.2 deg launch, 3,655 rpm, 243 carry (older chart); newer chart 249 carry, -2.3 deg attack | PGA Tour | https://teeituprva.com/wp-content/uploads/2019/03/PGA-AVERAGES-INTERACTIVE.pdf ; https://golfingfocus.com/uncovering-how-far-pros-hit-their-woods-and-hybrids/ | S | The downward attack angle says ground or a very low tee, but no page seen states it. Will's assumed 240 carry off the deck is Tour 3-wood carry: plausible for his speed (275 Driver carry), not short |
| Off the fairway expect 1-2 deg less launch and 300-500 rpm more spin than off a tee | rule of thumb | https://www.upyourclub.com/3-wood-launch-angle-spin-rate/ | S (not a measurement) | Direction only |
| 3-wood off a tee is 1-2 % more accurate than Driver and about 24 yds shorter | Shot Scope users, all handicaps | https://shotscope.com/ebook/The_Ultimate_Golfers_Guide_Shot_Scope.pdf | S | Tee shots only |
| Strike quality / mishit rate of a fairway wood off turf against off a tee, amateurs | - | none found | - | No published number. The mishit rate stays an assumption |

## (b) Long approaches: proximity and greens hit

| figure | population | source | status | use for Will |
|---|---|---|---|---|
| Proximity from the fairway: 100-125 yds 20 ft; 125-150 23 ft 8; 150-175 27 ft 8; 175-200 34 ft 1; 200-225 42 ft 5 | PGA Tour | https://x.com/practicalgolf/status/1527261534816292865 | S | The Tour ladder. The first build's patterns reproduce it almost exactly (table below): they were Tour patterns |
| 200-225 yds: 42 ft 0 (2021 season page); 41 ft 3 (Golf Digest); 41 ft 4 (Today's Golfer) | PGA Tour | https://www.pgatour.com/stats/stat.02358.y2021.html ; https://www.golfdigest.com/story/statistics-pros-better-than-scratch-golfers-how-do-you-compare ; https://www.todays-golfer.com/news-and-events/general-news/pga-tour-v-scratch-golfer-stats/ | S | same |
| 225-250 yds: about 54 ft | PGA Tour | https://theleftrough.com/why-greens-in-regulation-matter/ | 2 | Tour 4-wood band |
| 250-275 yds: Tour average not found (the season leader 48 ft 10); 225-250 from rough: leader 29 ft 4 only | PGA Tour | https://www.pgatour.com/stats/approach-green | S (leaders only) | none |
| Tour pros hit the green 50 % of the time from about 205 yds | PGA Tour | https://x.com/LouStagner/status/1984730930259345912 | S | Green-hit anchor |
| 200+ yds: 40 % of greens | PGA Tour | https://theleftrough.com/why-greens-in-regulation-matter/ | 2 | same |
| Proximity from 200-225: scratch 80 ft 2 against Tour 41 ft 3 (Arccos); another page gives scratch 102 ft | scratch amateurs | Golf Digest and Today's Golfer pages above | S (the two disagree) | The amateur number BY DISTANCE. Average scratch players hit a hybrid or wood from here; Will hits a long iron |
| Scratch hits about 25 % of greens from 200-225 | scratch | https://ejsgolf.com/post/scratch-vs-professional (citing MyGolfSpy) | 2 | same |
| "Good" approach = at least 90 % of the distance and within 10 yds left / right of the flag, fairway only: from 200 yds scratch 39 %, 20-index 8 %; from 100 yds scratch 78 % | Arccos, by handicap | https://newsletter.loustagnergolf.com/p/good-approach-shot-benchmarks | S | The cleanest dispersion benchmark for his level |
| A Tour player's 30-ft circle is a scratch player's 45-ft circle, 100-200 yds (pattern 1.5 x) | Tour against scratch | https://forums.golfwrx.com/topic/1859153-approach-tour-and-scratch-data/ (Stagner's chart) | S | Club for club, a scratch pattern = Tour x 1.5 |
| Tour from 200 in the fairway = scratch from 156 in the fairway, in strokes | Tour against scratch | Stagner, as quoted in search extracts | 2 | Checks the engine's amateur table (3.33 at 156 against the Tour's 3.19 at 200: the table is a 2-3 handicap, a touch worse than scratch) |
| Scratch: proximity from 90 yds in the fairway about 26 ft | scratch | https://x.com/LouStagner/status/1748076560110813190 | S | Wedge band |
| Greens hit from 100 yds in the fairway: scratch 74 %, 5-handicap 65 %; from 75-125 scratch 66 % | Shot Scope | https://golfity.com/blog/approach-proximity-benchmarks-how-close-should-you-be ; https://pluggedingolf.com/right-size-your-golf-expectations-part-2/ | S / 2 | Wedge band |
| Par 3s of 225-250 yds: Tour 3.18, 1-5 handicap 3.96 | Arccos | https://mygolfspy.com/labs/pros-vs-joes-par-3-scoring-average/ | S | The engine's table gives 3.90 at 237 from the fairway: in line |
| Tour strokes to hole out, fairway 200 / 220 / 240 / 260 = 3.19 / 3.32 / 3.45 / 3.58; rough 3.42 / 3.53 / 3.64 / 3.74; fairway 40 / 100 = 2.60 / 2.80; rough 2.78 / 3.02 | PGA Tour 2004-12 (Broadie) | https://whygolf.com/pages/strokes-gained-calculator | S (and identical to the table already in the engine) | Rough costs the Tour 0.2 at these distances |

## (c) Go or lay up; is closer better for amateurs

| figure | population | source | status | use for Will |
|---|---|---|---|---|
| 1.34 million par-5 holes, 18,285 golfers, one year: going for it more than doubles birdie-or-better and cuts bogey-or-worse by nearly a third against laying back, at every handicap band; a scratch player averages +0.12 on par 5s | Arccos, all handicaps | https://mygolfspy.com/news-opinion/the-par-5-lay-up-debate-is-over-we-have-the-data/ | S | Direction agrees with the model. Not controlled for lie or trouble (the article says so) |
| Same study: strokes to hole out get worse in a straight line the farther back the lay-up, about 0.22 from 60 to 100 yds; fairway beats rough by 0.09-0.18 at every yardage; "lay up to a spot, not a number" | same | https://dormied.com/news/arccos-golf-every-coachs-lay-number/ | S | Closer is better. The engine's table has 0.15 from 60 to 100 (Tour 0.10), rough 0.14-0.16: inside the data |
| After the drive: 4.2 strokes to finish when going, 4.8 when laying up | Shot Scope users | https://pluggedingolf.com/should-you-ever-lay-up-golf-myths-unplugged/ | 2 (confounded: bad drives lay up) | Direction only |
| Laying up costs on average half a shot a hole | Shot Scope users | https://shotscope.com/blog/practice-green/stats-and-data/par-5-go-for-it-in-2-vs-a-lay-up/ | S | Direction only |
| Proximity 0-5 handicap: 41.4 ft from 60-80 yds, 48.8 ft from 100-120 | Arccos (older study) | https://www.arccosgolf.com/blogs/community/course-management-101-what-layup-yardage-is-your-sweet-spot | S | Closer is closer, by 7 ft |
| 110 yds from the fairway 64 ft, 50 yds 35 ft | Shot Scope users | https://theleftrough.com/golf-lay-up/ | 2 | same |
| Scratch: 2.98 strokes from 100 yds; up and down about half the time inside 50 | Shot Scope | search extract of golfity.com pages | 2 | Engine table: 3.10 at 100 |
| "No evidence for a comfortable yardage; the best lay-up is as close to the green as you can get it" (Broadie, Fawcett) | Tour and amateur shot data | https://www.golfdigest.com/story/tpc-sawgrass-tour-pro-par-5-strategy-golf-digest-game-plan-explained | S | Rule |

## (d) Cold

| figure | source | status | use |
|---|---|---|---|
| About 2 yds of carry per club for every 10 F below 75 (1.3 for a pitching wedge), TrackMan tests | https://golf.com/instruction/cold-weather-golf-ball-formula-yardages/ (Andrew Rice) | S | The engine takes 0.135 % a degree: 9 yds off a 240 carry at 42 F, more than this rule. Stands |
| Colder: lower ball speed, launch, spin and height | https://www.milesofgolf.com/does-temperature-effect-the-golf-ball/ | S | Direction: the low-launch 4-wood off turf suffers most, which the pessimistic set carries as 8 yds |
| Fairway wood off cold turf specifically | none found | - | The engine's cold rule stands |

## Driver pattern (research note only; no tee-shot input changed)

Scott Fawcett's figure for the Driver pattern is 65-70 yds wide, quoted both for Tour players ("every ounce of
70 yards") and for scratch-or-better amateurs (https://practical-golf.com/golf-ball-control ;
https://www.golfdigest.com/story/scott-fawcett-golf-cheat-code ; both S). The page's Driver, 70 yds at 95 %, is that
number, so the tee-shot width is not Tour-only. The tee shot is also scored on the amateur table for everything
after it, so it does not have the mismatch found here. The par-3 club ladder and targets do simulate iron shots with
the same Tour-tight iron patterns (a 210 long iron 43 yds wide); the mismatch would matter there. Not changed.

## From the data to model inputs

**Distance: the golfer's own number.** During this pass Will said: "4-wood same as off tee". So the 4-wood off the
fairway is 255 carry / 270 total at 70 F (about 245 carry in Saturday's cold), not the first build's 240. That
overrides both the old assumption and the 11-15 yds the data would take off. It says nothing about accuracy: the
patterns below are where the data decides.

**What the first build was.** Its patterns off the deck were the tee-shot patterns. On a flat, calm hole with a
15-yd-radius green they leave 21 / 25 / 29 / 33 / 38 ft from 115 / 141 / 167 / 192 / 220 yds, against the PGA
Tour's 20 / 24 / 28 / 34 / 42 ft, and hit 70 % of greens from 220 (Tour: 50 % from 205). So every second shot was
a Tour-level strike, then scored on the engine's amateur table. Played out that way a shot scores 0.25-0.7 strokes
better than the same table says a shot from there is worth (last column of the table below). This is the whole
approach game, not the 4-wood alone.

**Three sets** (`DECK_SETS` in `opt/par5_second.py`; every club off the deck, fairway and rough):

| | assumed (first build) | data central (the page now) | pessimistic |
|---|---|---|---|
| basis of the patterns | tee patterns kept | Tour proximity x 1.5 club for club (scratch pattern = 1.5 x Tour); gives the scratch good-shot rate | scratch proximity BY DISTANCE (80 ft from 200-225), a poor strike day in 40 F |
| width and distance window, every club | x 1.0 | x 1.75 | x 2.0 |
| 95 % width: 4-wood / long iron / mid iron / SW | 54 / 44 / 37 / 24 yds | 95 / 76 / 65 / 42 | 113 / 90 / 77 / 50 |
| as an angle (one sigma), 4-wood / long iron | 3.0 / 2.8 deg | 5.0 / 4.9 deg | 5.7 / 5.6 deg |
| mishits (slightly thin or heavy / bad) | 12 % / 2.5 % | 12 % / 2.5 % (no data to move it) | 20 % / 6 % |
| 4-wood off the deck at 70 F, carry / total | 240 / 255 | 255 / 270 (his number) | 255 / 270 (his number) |
| rough | 4 % shorter, 25 % wider, no 4-wood | the same | 8 % shorter, 50 % wider, no 4-wood |
| Driver, 2-wood off the deck | none | none | none |

Why x 1.75 and not x 1.5: the engine adds its mishits on top of the width, and x 1.75 is what brings the simulated
proximity to Tour x 1.5 in the long clubs and the good-shot rate to the scratch figure. Why central is not the
scratch number by distance: the average scratch player is 20-30 yds shorter than Will and hits a hybrid or wood
from 210; Will hits a long iron, as a Tour player does. Club for club is the fair comparison for him; by distance
is the unfavourable end, and is the pessimistic set.

### Calibration check (flat hole, calm, 70 F, pin at the club's own stock distance, 15-yd-radius green)

"1 + value after" = the shot, then the engine's own values where the ball finishes (putts on the green; off it the
engine's short-game and table values, 25 % fairway / 75 % rough). "engine table" = the amateur table's strokes from
the starting spot. If the pattern and the table describe the same player, the last column is about zero.

| club | pin at | set | lie | 95 % width | proximity (mean, ft) | on a 15-yd green | good shot (>= 90 % of the distance, within 10 yds) | 15+ yds short | 1 + value after | engine table | sim - table |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SW | 115 | assumed | fairway | 24 | 21 | 96 % | 88 % | 2 % | 2.90 | 3.16 | -0.25 |
| SW | 110 | assumed | rough | 30 | 25 | 91 % | 79 % | 3 % | 2.99 | 3.31 | -0.32 |
| SW | 115 | central | fairway | 42 | 35 | 76 % | 62 % | 3 % | 3.16 | 3.16 | -0.00 |
| SW | 110 | central | rough | 52 | 42 | 62 % | 50 % | 5 % | 3.27 | 3.31 | -0.04 |
| SW | 115 | pessimistic | fairway | 50 | 42 | 64 % | 53 % | 8 % | 3.26 | 3.16 | +0.10 |
| SW | 106 | pessimistic | rough | 74 | 57 | 42 % | 35 % | 12 % | 3.45 | 3.29 | +0.16 |
| PW | 141 | assumed | fairway | 28 | 25 | 92 % | 82 % | 2 % | 2.97 | 3.26 | -0.29 |
| PW | 135 | assumed | rough | 35 | 30 | 85 % | 72 % | 3 % | 3.07 | 3.42 | -0.35 |
| PW | 141 | central | fairway | 50 | 41 | 65 % | 55 % | 5 % | 3.25 | 3.26 | -0.01 |
| PW | 135 | central | rough | 62 | 49 | 52 % | 44 % | 7 % | 3.37 | 3.42 | -0.05 |
| PW | 141 | pessimistic | fairway | 59 | 49 | 54 % | 46 % | 9 % | 3.36 | 3.26 | +0.09 |
| PW | 130 | pessimistic | rough | 88 | 68 | 33 % | 30 % | 14 % | 3.54 | 3.39 | +0.15 |
| 8-iron | 167 | assumed | fairway | 33 | 29 | 87 % | 76 % | 3 % | 3.04 | 3.40 | -0.35 |
| 8-iron | 161 | assumed | rough | 41 | 35 | 77 % | 65 % | 3 % | 3.14 | 3.54 | -0.40 |
| 8-iron | 167 | central | fairway | 57 | 47 | 55 % | 49 % | 6 % | 3.34 | 3.40 | -0.06 |
| 8-iron | 161 | central | rough | 71 | 57 | 43 % | 39 % | 9 % | 3.45 | 3.54 | -0.09 |
| 8-iron | 167 | pessimistic | fairway | 68 | 57 | 44 % | 41 % | 11 % | 3.44 | 3.40 | +0.04 |
| 8-iron | 154 | pessimistic | rough | 101 | 78 | 27 % | 27 % | 16 % | 3.61 | 3.51 | +0.10 |
| Mid iron | 192 | assumed | fairway | 37 | 33 | 80 % | 70 % | 4 % | 3.11 | 3.56 | -0.44 |
| Mid iron | 185 | assumed | rough | 46 | 39 | 69 % | 59 % | 4 % | 3.22 | 3.68 | -0.46 |
| Mid iron | 192 | central | fairway | 65 | 53 | 46 % | 44 % | 9 % | 3.41 | 3.56 | -0.14 |
| Mid iron | 185 | central | rough | 81 | 64 | 35 % | 35 % | 12 % | 3.52 | 3.68 | -0.16 |
| Mid iron | 192 | pessimistic | fairway | 77 | 65 | 36 % | 37 % | 14 % | 3.51 | 3.56 | -0.04 |
| Mid iron | 177 | pessimistic | rough | 115 | 89 | 22 % | 24 % | 19 % | 3.68 | 3.63 | +0.04 |
| Long iron | 220 | assumed | fairway | 44 | 38 | 70 % | 62 % | 7 % | 3.20 | 3.76 | -0.56 |
| Long iron | 212 | assumed | rough | 54 | 45 | 58 % | 52 % | 7 % | 3.31 | 3.86 | -0.56 |
| Long iron | 220 | central | fairway | 76 | 62 | 37 % | 38 % | 13 % | 3.49 | 3.76 | -0.27 |
| Long iron | 212 | central | rough | 95 | 74 | 27 % | 30 % | 16 % | 3.59 | 3.86 | -0.27 |
| Long iron | 220 | pessimistic | fairway | 90 | 75 | 28 % | 32 % | 20 % | 3.59 | 3.76 | -0.17 |
| Long iron | 203 | pessimistic | rough | 135 | 103 | 16 % | 21 % | 23 % | 3.74 | 3.80 | -0.06 |
| 4-wood | 255 | assumed | fairway | 54 | 47 | 56 % | 52 % | 12 % | 3.32 | 4.03 | -0.71 |
| 4-wood | 270 | central | fairway | 95 | 76 | 26 % | 31 % | 22 % | 3.61 | 4.14 | -0.53 |
| 4-wood | 270 | pessimistic | fairway | 113 | 92 | 19 % | 26 % | 32 % | 3.70 | 4.14 | -0.44 |

Against the data:

| band | data | assumed | central | pessimistic |
|---|---|---|---|---|
| 100-125 yds, proximity | Tour 20 ft; scratch about 26 ft from 90; 0-5 handicap 49 ft from 100-120 | 21 | 35 | 42 |
| 100 yds, green hit | scratch 74 % (66 % for 75-125) | 96 % | 76 % | 64 % |
| 125-150 | Tour 24 ft (x 1.5 = 36) | 25 | 41 | 49 |
| 150-175 | Tour 28 ft (x 1.5 = 42) | 29 | 47 | 57 |
| 175-200 | Tour 34 ft (x 1.5 = 51) | 33 | 53 | 65 |
| 200-225, proximity | Tour 42 ft (x 1.5 = 63); scratch 80 ft (one page: 102) | 38 | 62 | 75 |
| 200-225, green hit | Tour 50 % from 205; scratch about 25 % (unverified) | 70 % | 37 % | 28 % |
| 200, good shot | scratch 39 % | 62 % (at 220) | 38 % (at 220) | 32 % |
| 4-wood | Tour about 54 ft from 225-250 (x 1.5 = 81); 250-275 not found | 47 (at 255) | 76 (at 270) | 92 (at 270) |

* Central reproduces the engine's own table within 0.00-0.06 from 115 to 167 yds, fairway and rough. So below
  170 yds the table and the central pattern are the same player.
* From 190 out a gap remains even on central (0.14 at 192, 0.27 at 220, 0.53 at 270) and on pessimistic (0.04,
  0.17, 0.44). Part of that is the flat hole with nothing around the green; the real holes below price what is
  there. Part may be that the long clubs are still too kind. So read the central edges as the favourable side of
  the truth and the pessimistic ones as the unfavourable side.
* One multiplier for every band is enough: by band the fit asks for about x 1.5 in the wedges, x 1.7 in the
  irons and x 1.75-1.9 in the long clubs. The wedges come out slightly wide on x 1.75; that only touches lay-up
  shots, which are aimed at wide ground.

## Re-run: holes 6, 13, 18

From the middle of the fairway on the hole's line of play at each distance to the middle of the green (the menu's
spots), fairway and rough, Saturday and Sunday forecast, Back map (a first run on the Middle map gave the same
numbers within 0.01). 3,000 swings a cell, one hole a process, 35-50 s. "Go" = the best club that finishes within
20 yds of the front edge or beyond; "lay-up" = the best club stopping 20+ yds short. Cells: go minus lay-up in
strokes (negative = go is better), the go club (4w, LI = long iron), then (share on the green / share carrying the
front edge / share in trouble = penalty or trees). Differences under 0.03 are ties. "assumed" = the first build
(240-carry 4-wood, Tour patterns); central and pessimistic have his 255-carry 4-wood.

| hole | day | lie | set | 220 | 230 | 240 | 250 | 260 | 270 |
|---|---|---|---|---|---|---|---|---|---|
| 6 | sat | fairway | assumed | -0.34 LI (35/23/1) | -0.28 LI (20/1/0) | -0.43 4w (27/64/7) | -0.32 4w (28/27/3) | -0.32 4w (23/3/2) | -0.26 4w (9/0/3) |
| 6 | sat | fairway | central | -0.19 LI (18/31/9) | -0.19 LI (12/10/8) | -0.15 LI (5/1/10) | -0.08 4w (12/69/25) | -0.21 4w (14/47/18) | -0.26 4w (12/23/14) |
| 6 | sat | fairway | pessimistic | -0.16 LI (13/28/12) | -0.16 LI (9/12/12) | -0.11 LI (4/2/14) | -0.09 4w (10/57/24) | -0.18 4w (12/40/20) | -0.20 4w (8/21/19) |
| 6 | sat | rough | assumed | -0.25 LI (19/5/2) | -0.20 LI (6/0/3) | lay Long 3.91 | lay Long 3.99 | lay Long 4.07 | lay Long 4.13 |
| 6 | sat | rough | central | -0.15 LI (10/18/13) | -0.12 LI (6/5/15) | lay Long 4.08 | lay Long 4.14 | lay Long 4.19 | lay Long 4.23 |
| 6 | sat | rough | pessimistic | -0.05 LI (4/12/26) | -0.06 LI (2/4/24) | lay Long 4.26 | lay Long 4.30 | lay Long 4.35 | lay Long 4.39 |
| 6 | sun | fairway | assumed | -0.55 LI (38/42/2) | -0.31 LI (29/5/0) | -0.36 4w (24/77/8) | -0.48 4w (29/45/5) | -0.33 4w (25/10/2) | -0.28 4w (15/1/3) |
| 6 | sun | fairway | central | -0.34 LI (20/43/10) | -0.20 LI (15/18/8) | -0.17 LI (8/3/9) | -0.15 LI (3/1/9) | -0.16 4w (13/57/20) | -0.25 4w (13/32/15) |
| 6 | sun | fairway | pessimistic | -0.27 LI (15/37/13) | -0.16 LI (11/18/12) | -0.13 LI (6/4/14) | -0.13 4w (9/69/28) | -0.15 4w (11/47/21) | -0.20 4w (10/29/20) |
| 6 | sun | rough | assumed | -0.27 LI (24/13/2) | -0.23 LI (11/1/2) | -0.18 LI (2/0/3) | lay Long 3.95 | lay Long 4.03 | lay Long 4.11 |
| 6 | sun | rough | central | -0.15 LI (12/24/13) | -0.14 LI (7/9/14) | -0.11 LI (3/2/16) | lay Long 4.11 | lay Long 4.17 | lay Long 4.22 |
| 6 | sun | rough | pessimistic | -0.06 LI (5/15/26) | -0.06 LI (2/6/25) | lay Long 4.24 | lay Long 4.28 | lay Long 4.34 | lay Long 4.37 |
| 13 | sat | fairway | assumed | -0.34 LI (30/34/9) | -0.24 4w (18/95/5) | -0.35 4w (30/74/8) | -0.17 4w (23/32/11) | -0.10 4w (8/4/6) | -0.12 4w (2/0/3) |
| 13 | sat | fairway | central | -0.25 LI (18/39/8) | -0.08 LI (7/14/8) | -0.19 4w (9/94/4) | -0.19 4w (13/71/6) | -0.19 4w (13/48/8) | -0.15 4w (11/25/10) |
| 13 | sat | fairway | pessimistic | -0.21 LI (12/34/7) | -0.10 4w (3/93/4) | -0.18 4w (9/89/6) | -0.18 4w (11/59/5) | -0.18 4w (10/41/7) | -0.14 4w (7/23/10) |
| 13 | sat | rough | assumed | -0.08 LI (10/10/7) | -0.08 LI (2/1/4) | -0.11 LI (0/0/1) | lay Long 3.94 | lay Long 4.00 | lay Long 4.03 |
| 13 | sat | rough | central | -0.10 LI (9/22/9) | -0.06 LI (3/7/7) | -0.05 LI (1/1/7) | lay Long 4.05 | lay Long 4.08 | lay Long 4.11 |
| 13 | sat | rough | pessimistic | -0.09 LI (4/14/10) | -0.05 LI (1/5/9) | lay Long 4.13 | lay Long 4.18 | lay Long 4.20 | lay Long 4.23 |
| 13 | sun | fairway | assumed | -0.16 LI (25/24/11) | -0.29 4w (24/91/6) | -0.36 4w (30/69/8) | -0.14 4w (18/24/9) | -0.09 4w (6/2/6) | -0.13 4w (1/0/2) |
| 13 | sun | fairway | central | -0.15 LI (15/32/9) | -0.11 4w (5/97/4) | -0.22 4w (11/93/5) | -0.20 4w (14/67/7) | -0.19 4w (13/43/9) | -0.14 4w (7/20/8) |
| 13 | sun | fairway | pessimistic | -0.13 LI (11/28/8) | -0.13 4w (6/93/4) | -0.21 4w (10/88/6) | -0.19 4w (10/56/7) | -0.17 4w (9/37/8) | -0.13 4w (7/19/9) |
| 13 | sun | rough | assumed | -0.07 LI (6/6/6) | -0.08 LI (1/0/3) | lay Long 3.90 | lay Long 3.96 | lay Long 4.01 | lay Long 4.04 |
| 13 | sun | rough | central | -0.09 LI (8/18/10) | -0.06 LI (2/5/6) | lay Long 4.02 | lay Long 4.06 | lay Long 4.09 | lay Long 4.12 |
| 13 | sun | rough | pessimistic | -0.08 LI (4/12/10) | lay Long 4.10 | lay Long 4.16 | lay Long 4.19 | lay Long 4.21 | lay Long 4.24 |
| 18 | sat | fairway | assumed | -0.40 LI (47/49/10) | -0.15 4w (13/98/3) | -0.26 4w (23/81/5) | -0.26 4w (29/44/9) | -0.07 4w (18/9/9) | -0.06 4w (10/1/4) |
| 18 | sat | fairway | central | -0.14 LI (19/47/9) | -0.03 LI (14/21/12) | -0.06 4w (6/96/4) | -0.12 4w (10/79/6) | -0.06 4w (12/55/8) | -0.03 4w (10/36/8) |
| 18 | sat | fairway | pessimistic | -0.07 LI (14/40/9) | -0.01 LI (7/19/8) | -0.05 4w (7/91/6) | -0.09 4w (10/68/7) | -0.03 4w (9/46/9) | -0.00 4w (7/32/9) |
| 18 | sat | rough | assumed | -0.08 LI (22/17/11) | -0.05 LI (9/1/6) | -0.07 LI (2/0/3) | lay Long 3.90 | lay Long 3.93 | lay Long 3.97 |
| 18 | sat | rough | central | -0.02 LI (10/26/10) | +0.00 LI (6/10/9) | +0.00 LI (3/3/5) | lay Long 4.01 | lay Long 4.01 | lay Long 4.03 |
| 18 | sat | rough | pessimistic | +0.03 LI (4/17/10) | +0.02 LI (3/7/9) | lay Mid 4.08 | lay Long 4.11 | lay Long 4.12 | lay Long 4.13 |
| 18 | sun | fairway | assumed | -0.14 4w (11/98/2) | -0.29 4w (28/87/5) | -0.32 4w (32/65/7) | -0.09 4w (21/18/11) | -0.06 4w (10/1/6) | -0.08 4w (3/0/3) |
| 18 | sun | fairway | central | -0.04 LI (13/25/10) | -0.06 4w (6/97/3) | -0.12 4w (10/92/6) | -0.08 4w (13/63/9) | -0.04 4w (11/38/10) | -0.02 4w (9/21/11) |
| 18 | sun | fairway | pessimistic | -0.01 LI (8/23/8) | -0.06 4w (8/92/6) | -0.10 4w (10/87/7) | -0.05 4w (9/52/8) | -0.01 4w (8/33/11) | +0.00 4w (5/19/8) |
| 18 | sun | rough | assumed | -0.04 LI (9/3/6) | -0.06 LI (2/0/3) | lay Long 3.90 | lay Long 3.93 | lay Long 3.97 | lay Long 4.00 |
| 18 | sun | rough | central | +0.00 LI (7/14/9) | +0.01 LI (3/4/5) | lay Long 4.01 | lay Long 4.02 | lay Long 4.03 | lay Long 4.05 |
| 18 | sun | rough | pessimistic | +0.03 LI (3/9/10) | lay Mid 4.08 | lay Mid 4.10 | lay Long 4.13 | lay Long 4.14 | lay Long 4.16 |

### Crossover (fairway; distance to the middle of the green where laying up becomes as good as going)

| hole | assumed (first build) | his distance + central patterns | his distance + pessimistic patterns |
|---|---|---|---|
| 6 | none to 270 (go by 0.26-0.55) | none to 270: go by 0.15-0.34, except 0.08 at 250 on Saturday | none to 270: go by 0.09-0.27 |
| 13 | none to 270 (0.09-0.36) | none to 270: go by 0.15-0.25, except 0.08-0.11 at 230 | none to 270: go by 0.13-0.21, 0.10 at 230 |
| 18 | none to 270 (0.06-0.41) | about 270: go by 0.03-0.14 all the way, a tie from 265 | about 260: go by 0.05-0.10 at 240-250, a tie at 220-230 and from 260 |

From the rough there is no 4-wood, so his distance changes nothing: on central, 6 is the long iron run up from
inside 230 by 0.12-0.15 and a lay-up beyond; 13 the same by 0.05-0.10; 18 level. On pessimistic those shrink to
0.05-0.09 on 6 and 13, and on 18 the lay-up is ahead by 0.03.

The dip at 230-250: he has no club between the long iron (about 212 in the cold) and the 4-wood (about 260), and the
solver plays full swings only. From 240-250 on 6 the long iron is short and the full 4-wood is long (25 % find
trouble from 250 on Saturday), so the edge is smallest exactly there. An eased 4-wood would fill that gap; it is
not modelled.

### Which side the wider patterns hurt (fairway, mean of 220-260, both days, against the first build)

| hole | set | go gets worse by | closest lay-up gets worse by | lay-up to 80-100 gets worse by |
|---|---|---|---|---|
| 6 | central | 0.28 | 0.10 | 0.09 |
| 6 | pessimistic | 0.37 | 0.15 | 0.12 |
| 13 | central | 0.12 | 0.07 | 0.02 |
| 13 | pessimistic | 0.17 | 0.11 | 0.05 |
| 18 | central | 0.18 | 0.05 | 0.01 |
| 18 | pessimistic | 0.24 | 0.08 | 0.02 |

The go side is hurt two to four times as much, even with 15 more yards on the 4-wood. The wedge that follows a
lay-up was never simulated: it is the amateur table's value, which the central pattern reproduces, so that side was
already his level. Only the lay-up shot itself is wider now (it misses its strip more often).

### 2-wood off the deck

Tested before his distance came in (4-wood at 240, 2-wood at 252 carry): worth 0.00-0.05, only from 250-270 on 13.
With his 4-wood at 255 the same ground is covered. Not added.

## Plain answers

1. **Is "go" still right on 6, 13 and 18 with real data?** Yes on 6 and 13 from the fairway, at any distance from
   220 to 270 to the middle, by about half of what the page said: 0.15-0.25 a time (was 0.3-0.45). On 18 it is
   a small edge, 0.03-0.14, largest at 240-250, and a tie from about 265.
2. **Where does it flip on the pessimistic set?** Nowhere on 6 (still 0.09-0.27) or 13 (0.10-0.21). On 18 at about
   260; inside that the edge is 0.05-0.10 at best. So the answer on 6 and 13 does not depend on which reading of
   the data is right; on 18 either play is fine.
3. **What going looks like now.** On central the green is hit 10-20 % of the time from 220-260, not 25-45 %. From
   250 on 6 in Saturday's cold: 12 % on the green, 69 % carry the front edge, 25 % in trouble (long and wide). The
   edge survives because most of the rest finish within 40 yds of the hole, closer than any lay-up leaves him.
4. **"Get as close as you can" or "lay up to 90"?** As close as is safe. The closest lay-up beats the best lay-up
   to 80-100 yds by 0.06-0.24 on all three holes on central (0.05-0.20 on pessimistic), and the Arccos study of
   1.34 million par 5s puts 60 against 100 yds at 0.22 for amateurs. The condition in the data is the lie: fairway
   beats rough by 0.09-0.18, so "close" means the closest piece of fairway, not the closest yard.
5. **What still is not known.** How often he mis-hits a 4-wood off cold turf. No published number exists; the
   pessimistic set (one thin or bad strike in four) is the stand-in.

## What changed on the page

The par-5 Second shot block and menu are now built on his 4-wood distance and the central patterns, in both
tall-grass modes (`par5_second.json`, `par5_menu.json`, `*_lost.json`; Drop stays the default). The tee-pick
re-check under "always lay up" (the pill) was re-run for Back and Middle in Drop mode; for the Lost ball mode it is
kept from the first build (it compares tee clubs when every second shot is a lay-up, which the wider pattern moves
by the same 0.05-0.10 for all three woods). The hole 10 lay-up table is not re-solved and still uses the first
pattern and the 240-carry 4-wood (`DECK_SETS["assumed"]`, what a plain import of `par5_second` gives). No tee-shot
club, aim or number changed.

Pills that moved with the re-check (Drop): Back 3 gains "the 2-wood and 4-wood are just as good off the tee"; Back 6
loses its pill (laying up regardless, the 2-wood is now 0.032 behind the Driver, the line is 0.03); Back 13 names
the 2-wood only; Middle 6 and Middle 18 (Sunday) gain one. With the best second shot played out on 6, the 2-wood
and 4-wood come out level with the Driver off the tee (within 0.006): the Driver leaves 240, between his long iron
and his 4-wood.

QA of the rebuilt page: The Tips, Champions, Back, Middle, Forward, each in Drop and Lost ball: 18 holes, 0
problems; the Second shot and Lay up tables fit at 375 and 430 px in both modes; none of the ten words kept off the
page in 5,580 rendered texts or in the par-5 data. Against the page of commit ce04a9172 (same ten runs): the only
fields that differ are the Second shot text and the pill on 3, 6, 13, 18, and hole 10, which another change
(commits 0061ee7b2, 281442149: hole 10 map and re-solve) altered. Every other hole's club, aim, table and notes
are identical.

## Appendix: every cell, Back map

Columns: distance to the middle / to the front edge; the go club at its best line with its strokes and shares; the closest lay-up (what it leaves) and its strokes; the best lay-up leaving 80-100 yds.

### Hole 6 sat fairway  (40.7 F)
| to middle / front | set | go: club | go strokes | green | carry front | trouble | best lay-up (leaves) | strokes | lay-up to 80-100 | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|
| 220 / 207 | assumed | Long iron | 3.49 | 35 % | 23 % | 1 % | Mid iron (36) | 3.83 | PW (87) 4.09 | -0.34 |
| 220 / 207 | central | Long iron | 3.74 | 18 % | 31 % | 9 % | Mid iron (36) | 3.93 | PW (85) 4.17 | -0.19 |
| 220 / 207 | pessimistic | Long iron | 3.84 | 13 % | 28 % | 12 % | Mid iron (36) | 4.00 | PW (85) 4.19 | -0.16 |
| 230 / 216 | assumed | Long iron | 3.64 | 20 % | 1 % | 0 % | Mid iron (45) | 3.92 | 9-iron (84) 4.09 | -0.28 |
| 230 / 216 | central | Long iron | 3.81 | 12 % | 10 % | 8 % | Mid iron (45) | 4.01 | 9-iron (82) 4.18 | -0.19 |
| 230 / 216 | pessimistic | Long iron | 3.91 | 9 % | 12 % | 12 % | Mid iron (45) | 4.06 | 9-iron (81) 4.20 | -0.16 |
| 240 / 227 | assumed | 4-wood | 3.57 | 27 % | 64 % | 7 % | Mid iron (57) | 4.00 | 8-iron (82) 4.10 | -0.43 |
| 240 / 227 | central | Long iron | 3.93 | 5 % | 1 % | 10 % | Mid iron (55) | 4.08 | 9-iron (93) 4.20 | -0.15 |
| 240 / 227 | pessimistic | Long iron | 4.02 | 4 % | 2 % | 14 % | Mid iron (55) | 4.12 | 9-iron (93) 4.24 | -0.11 |
| 250 / 236 | assumed | 4-wood | 3.56 | 28 % | 27 % | 3 % | Long iron (38) | 3.88 | 8-iron (90) 4.12 | -0.32 |
| 250 / 236 | central | 4-wood | 3.93 | 12 % | 69 % | 25 % | Long iron (38) | 4.01 | 8-iron (89) 4.21 | -0.08 |
| 250 / 236 | pessimistic | 4-wood | 3.99 | 10 % | 57 % | 24 % | Long iron (38) | 4.08 | 8-iron (89) 4.25 | -0.09 |
| 260 / 245 | assumed | 4-wood | 3.65 | 23 % | 3 % | 2 % | Long iron (47) | 3.97 | 8-iron (99) 4.14 | -0.32 |
| 260 / 245 | central | 4-wood | 3.87 | 14 % | 47 % | 18 % | Long iron (47) | 4.08 | 8-iron (99) 4.23 | -0.21 |
| 260 / 245 | pessimistic | 4-wood | 3.96 | 12 % | 40 % | 20 % | Long iron (47) | 4.14 | 8-iron (99) 4.28 | -0.18 |
| 270 / 255 | assumed | 4-wood | 3.79 | 9 % | 0 % | 3 % | Long iron (59) | 4.04 | Mid iron (86) 4.13 | -0.26 |
| 270 / 255 | central | 4-wood | 3.88 | 12 % | 23 % | 14 % | Long iron (56) | 4.14 | Mid iron (84) 4.23 | -0.26 |
| 270 / 255 | pessimistic | 4-wood | 3.99 | 8 % | 21 % | 19 % | Long iron (57) | 4.20 | Mid iron (84) 4.28 | -0.20 |

### Hole 6 sat rough  (40.7 F)
| to middle / front | set | go: club | go strokes | green | carry front | trouble | best lay-up (leaves) | strokes | lay-up to 80-100 | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|
| 220 / 207 | assumed | Long iron | 3.67 | 19 % | 5 % | 2 % | Mid iron (43) | 3.92 | 9-iron (80) 4.12 | -0.25 |
| 220 / 207 | central | Long iron | 3.90 | 10 % | 18 % | 13 % | Mid iron (44) | 4.05 | PW (90) 4.21 | -0.15 |
| 220 / 207 | pessimistic | Long iron | 4.16 | 4 % | 12 % | 26 % | Mid iron (51) | 4.21 | 9-iron (83) 4.30 | -0.05 |
| 230 / 216 | assumed | Long iron | 3.80 | 6 % | 0 % | 3 % | Mid iron (53) | 4.00 | 9-iron (89) 4.14 | -0.20 |
| 230 / 216 | central | Long iron | 3.99 | 6 % | 5 % | 15 % | Mid iron (53) | 4.11 | 9-iron (87) 4.22 | -0.12 |
| 230 / 216 | pessimistic | Long iron | 4.20 | 2 % | 4 % | 24 % | Mid iron (60) | 4.27 | 8-iron (80) 4.32 | -0.06 |
| 240 / 227 | assumed | none | | | |  | Long iron (37) | 3.91 | 8-iron (87) 4.15 |  |
| 240 / 227 | central | none | | | |  | Long iron (37) | 4.08 | 8-iron (85) 4.24 |  |
| 240 / 227 | pessimistic | none | | | |  | Long iron (47) | 4.26 | 8-iron (92) 4.40 |  |
| 250 / 236 | assumed | none | | | |  | Long iron (46) | 3.99 | 8-iron (96) 4.17 |  |
| 250 / 236 | central | none | | | |  | Long iron (46) | 4.14 | 8-iron (95) 4.28 |  |
| 250 / 236 | pessimistic | none | | | |  | Long iron (54) | 4.30 |  |  |
| 260 / 245 | assumed | none | | | |  | Long iron (56) | 4.07 | Mid iron (83) 4.16 |  |
| 260 / 245 | central | none | | | |  | Long iron (55) | 4.19 | Mid iron (80) 4.26 |  |
| 260 / 245 | pessimistic | none | | | |  | Long iron (64) | 4.35 | Mid iron (87) 4.44 |  |
| 270 / 255 | assumed | none | | | |  | Long iron (66) | 4.13 | Mid iron (92) 4.18 |  |
| 270 / 255 | central | none | | | |  | Long iron (64) | 4.23 | Mid iron (91) 4.32 |  |
| 270 / 255 | pessimistic | none | | | |  | Long iron (74) | 4.39 | Mid iron (98) 4.48 |  |

### Hole 13 sat fairway  (45.2 F)
| to middle / front | set | go: club | go strokes | green | carry front | trouble | best lay-up (leaves) | strokes | lay-up to 80-100 | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|
| 220 / 204 | assumed | Long iron | 3.62 | 30 % | 34 % | 9 % | 8-iron (59) | 3.96 | PW (84) 4.05 | -0.34 |
| 220 / 204 | central | Long iron | 3.75 | 18 % | 39 % | 8 % | 8-iron (59) | 4.00 | PW (86) 4.07 | -0.25 |
| 220 / 204 | pessimistic | Long iron | 3.82 | 12 % | 34 % | 7 % | 8-iron (61) | 4.03 | PW (86) 4.09 | -0.21 |
| 230 / 214 | assumed | 4-wood | 3.65 | 18 % | 95 % | 5 % | Mid iron (46) | 3.90 | 9-iron (82) 4.04 | -0.24 |
| 230 / 214 | central | Long iron | 3.88 | 7 % | 14 % | 8 % | Mid iron (48) | 3.96 | 9-iron (83) 4.06 | -0.08 |
| 230 / 214 | pessimistic | 4-wood | 3.91 | 3 % | 93 % | 4 % | Mid iron (51) | 4.00 | 9-iron (84) 4.09 | -0.10 |
| 240 / 224 | assumed | 4-wood | 3.60 | 30 % | 74 % | 8 % | Mid iron (54) | 3.95 | 9-iron (91) 4.08 | -0.35 |
| 240 / 224 | central | 4-wood | 3.81 | 9 % | 94 % | 4 % | Mid iron (57) | 4.00 | 8-iron (80) 4.06 | -0.19 |
| 240 / 224 | pessimistic | 4-wood | 3.85 | 9 % | 89 % | 6 % | Mid iron (57) | 4.04 | 8-iron (81) 4.09 | -0.18 |
| 250 / 234 | assumed | 4-wood | 3.71 | 23 % | 32 % | 11 % | Long iron (40) | 3.87 | 8-iron (89) 4.07 | -0.17 |
| 250 / 234 | central | 4-wood | 3.78 | 13 % | 71 % | 6 % | Long iron (44) | 3.97 | 8-iron (91) 4.10 | -0.19 |
| 250 / 234 | pessimistic | 4-wood | 3.84 | 11 % | 59 % | 5 % | Long iron (44) | 4.02 | 8-iron (92) 4.13 | -0.18 |
| 260 / 244 | assumed | 4-wood | 3.83 | 8 % | 4 % | 6 % | Long iron (49) | 3.93 | 8-iron (100) 4.11 | -0.10 |
| 260 / 244 | central | 4-wood | 3.81 | 13 % | 48 % | 8 % | Long iron (51) | 4.00 |  | -0.19 |
| 260 / 244 | pessimistic | 4-wood | 3.88 | 10 % | 41 % | 7 % | Long iron (53) | 4.06 |  | -0.18 |
| 270 / 254 | assumed | 4-wood | 3.86 | 2 % | 0 % | 3 % | Long iron (58) | 3.98 | Mid iron (85) 4.06 | -0.12 |
| 270 / 254 | central | 4-wood | 3.88 | 11 % | 25 % | 10 % | Long iron (59) | 4.04 | Mid iron (87) 4.10 | -0.15 |
| 270 / 254 | pessimistic | 4-wood | 3.94 | 7 % | 23 % | 10 % | Long iron (61) | 4.08 | Mid iron (88) 4.14 | -0.14 |

### Hole 13 sat rough  (45.2 F)
| to middle / front | set | go: club | go strokes | green | carry front | trouble | best lay-up (leaves) | strokes | lay-up to 80-100 | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|
| 220 / 204 | assumed | Long iron | 3.81 | 10 % | 10 % | 7 % | Mid iron (44) | 3.90 | PW (90) 4.08 | -0.08 |
| 220 / 204 | central | Long iron | 3.89 | 9 % | 22 % | 9 % | Mid iron (48) | 3.99 | PW (92) 4.11 | -0.10 |
| 220 / 204 | pessimistic | Long iron | 4.03 | 4 % | 14 % | 10 % | Mid iron (59) | 4.11 | 9-iron (90) 4.17 | -0.09 |
| 230 / 214 | assumed | Long iron | 3.87 | 2 % | 1 % | 4 % | Mid iron (52) | 3.95 | 9-iron (88) 4.07 | -0.08 |
| 230 / 214 | central | Long iron | 3.96 | 3 % | 7 % | 7 % | Mid iron (56) | 4.03 | 9-iron (90) 4.11 | -0.06 |
| 230 / 214 | pessimistic | Long iron | 4.08 | 1 % | 5 % | 9 % | Mid iron (68) | 4.14 | 8-iron (90) 4.18 | -0.05 |
| 240 / 224 | assumed | Long iron | 3.89 | 0 % | 0 % | 1 % | Mid iron (61) | 4.00 | 8-iron (86) 4.06 | -0.11 |
| 240 / 224 | central | Long iron | 4.01 | 1 % | 1 % | 7 % | Mid iron (65) | 4.06 | 8-iron (88) 4.11 | -0.05 |
| 240 / 224 | pessimistic | none | | | |  | Long iron (55) | 4.13 | 8-iron (98) 4.22 |  |
| 250 / 234 | assumed | none | | | |  | Long iron (48) | 3.94 | 8-iron (97) 4.10 |  |
| 250 / 234 | central | none | | | |  | Long iron (53) | 4.05 | 8-iron (99) 4.16 |  |
| 250 / 234 | pessimistic | none | | | |  | Long iron (64) | 4.18 | Mid iron (88) 4.20 |  |
| 260 / 244 | assumed | none | | | |  | Long iron (56) | 4.00 | Mid iron (83) 4.06 |  |
| 260 / 244 | central | none | | | |  | Long iron (62) | 4.08 | Mid iron (86) 4.13 |  |
| 260 / 244 | pessimistic | none | | | |  | Long iron (75) | 4.20 | Mid iron (99) 4.25 |  |
| 270 / 254 | assumed | none | | | |  | Long iron (66) | 4.03 | Mid iron (93) 4.09 |  |
| 270 / 254 | central | none | | | |  | Long iron (69) | 4.11 | Mid iron (96) 4.17 |  |
| 270 / 254 | pessimistic | none | | | |  | Long iron (84) | 4.23 | Long iron (84) 4.23 |  |

### Hole 18 sat fairway  (47.2 F)
| to middle / front | set | go: club | go strokes | green | carry front | trouble | best lay-up (leaves) | strokes | lay-up to 80-100 | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|
| 220 / 207 | assumed | Long iron | 3.53 | 47 % | 49 % | 10 % | 8-iron (54) | 3.93 | GW (93) 4.08 | -0.40 |
| 220 / 207 | central | Long iron | 3.81 | 19 % | 47 % | 9 % | 8-iron (55) | 3.95 | GW (93) 4.09 | -0.14 |
| 220 / 207 | pessimistic | Long iron | 3.90 | 14 % | 40 % | 9 % | 8-iron (57) | 3.97 | PW (80) 4.05 | -0.07 |
| 230 / 216 | assumed | 4-wood | 3.71 | 13 % | 98 % | 3 % | Mid iron (42) | 3.87 | PW (90) 4.07 | -0.15 |
| 230 / 216 | central | Long iron | 3.90 | 14 % | 21 % | 12 % | Mid iron (45) | 3.93 | PW (90) 4.08 | -0.03 |
| 230 / 216 | pessimistic | Long iron | 3.95 | 7 % | 19 % | 8 % | Mid iron (45) | 3.96 | PW (90) 4.09 | -0.01 |
| 240 / 225 | assumed | 4-wood | 3.65 | 23 % | 81 % | 5 % | Mid iron (48) | 3.91 | 9-iron (85) 4.05 | -0.26 |
| 240 / 225 | central | 4-wood | 3.88 | 6 % | 96 % | 4 % | Mid iron (51) | 3.94 | 9-iron (85) 4.06 | -0.06 |
| 240 / 225 | pessimistic | 4-wood | 3.92 | 7 % | 91 % | 6 % | Mid iron (53) | 3.97 | 9-iron (86) 4.08 | -0.05 |
| 250 / 237 | assumed | 4-wood | 3.70 | 29 % | 44 % | 9 % | Mid iron (60) | 3.96 | 8-iron (84) 4.05 | -0.26 |
| 250 / 237 | central | 4-wood | 3.86 | 10 % | 79 % | 6 % | Mid iron (61) | 3.98 | 8-iron (84) 4.06 | -0.12 |
| 250 / 237 | pessimistic | 4-wood | 3.92 | 10 % | 68 % | 7 % | Mid iron (62) | 4.00 | 8-iron (85) 4.08 | -0.09 |
| 260 / 247 | assumed | 4-wood | 3.81 | 18 % | 9 % | 9 % | Long iron (44) | 3.89 | 8-iron (96) 4.10 | -0.07 |
| 260 / 247 | central | 4-wood | 3.89 | 12 % | 55 % | 8 % | Long iron (47) | 3.96 | 8-iron (97) 4.12 | -0.06 |
| 260 / 247 | pessimistic | 4-wood | 3.97 | 9 % | 46 % | 9 % | Long iron (49) | 4.00 | 8-iron (97) 4.14 | -0.03 |
| 270 / 255 | assumed | 4-wood | 3.86 | 10 % | 1 % | 4 % | Long iron (51) | 3.92 |  | -0.06 |
| 270 / 255 | central | 4-wood | 3.94 | 10 % | 36 % | 8 % | Long iron (54) | 3.97 |  | -0.03 |
| 270 / 255 | pessimistic | 4-wood | 4.00 | 7 % | 32 % | 9 % | Long iron (54) | 4.01 |  | -0.00 |

### Hole 18 sat rough  (47.2 F)
| to middle / front | set | go: club | go strokes | green | carry front | trouble | best lay-up (leaves) | strokes | lay-up to 80-100 | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|
| 220 / 207 | assumed | Long iron | 3.79 | 22 % | 17 % | 11 % | Mid iron (42) | 3.87 | PW (85) 4.06 | -0.08 |
| 220 / 207 | central | Long iron | 3.95 | 10 % | 26 % | 10 % | Mid iron (44) | 3.97 | PW (86) 4.07 | -0.02 |
| 220 / 207 | pessimistic | Long iron | 4.08 | 4 % | 17 % | 10 % | Mid iron (54) | 4.05 | 9-iron (81) 4.08 | +0.03 |
| 230 / 216 | assumed | Long iron | 3.86 | 9 % | 1 % | 6 % | Mid iron (48) | 3.91 | 9-iron (83) 4.05 | -0.05 |
| 230 / 216 | central | Long iron | 3.98 | 6 % | 10 % | 9 % | Mid iron (52) | 3.98 | 9-iron (83) 4.06 | +0.00 |
| 230 / 216 | pessimistic | Long iron | 4.09 | 3 % | 7 % | 9 % | Mid iron (60) | 4.07 | 9-iron (91) 4.12 | +0.02 |
| 240 / 225 | assumed | Long iron | 3.88 | 2 % | 0 % | 3 % | Mid iron (56) | 3.95 | 9-iron (92) 4.08 | -0.07 |
| 240 / 225 | central | Long iron | 4.00 | 3 % | 3 % | 5 % | Mid iron (59) | 3.99 | 9-iron (92) 4.10 | +0.00 |
| 240 / 225 | pessimistic | none | | | |  | Mid iron (67) | 4.08 | 8-iron (87) 4.12 |  |
| 250 / 237 | assumed | none | | | |  | Long iron (45) | 3.90 | 8-iron (91) 4.08 |  |
| 250 / 237 | central | none | | | |  | Long iron (49) | 4.01 | 8-iron (92) 4.10 |  |
| 250 / 237 | pessimistic | none | | | |  | Long iron (58) | 4.11 |  |  |
| 260 / 247 | assumed | none | | | |  | Long iron (52) | 3.93 |  |  |
| 260 / 247 | central | none | | | |  | Long iron (56) | 4.01 |  |  |
| 260 / 247 | pessimistic | none | | | |  | Long iron (65) | 4.12 | Mid iron (87) 4.15 |  |
| 270 / 255 | assumed | none | | | |  | Long iron (59) | 3.97 | Mid iron (86) 4.06 |  |
| 270 / 255 | central | none | | | |  | Long iron (62) | 4.03 | Mid iron (87) 4.09 |  |
| 270 / 255 | pessimistic | none | | | |  | Long iron (71) | 4.13 | Mid iron (95) 4.20 |  |

### Hole 6 sun fairway  (46.6 F)
| to middle / front | set | go: club | go strokes | green | carry front | trouble | best lay-up (leaves) | strokes | lay-up to 80-100 | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|
| 220 / 207 | assumed | Long iron | 3.43 | 38 % | 42 % | 2 % | 8-iron (57) | 3.98 | PW (84) 4.08 | -0.55 |
| 220 / 207 | central | Long iron | 3.71 | 20 % | 43 % | 10 % | 8-iron (57) | 4.05 | PW (83) 4.16 | -0.34 |
| 220 / 207 | pessimistic | Long iron | 3.82 | 15 % | 37 % | 13 % | 8-iron (56) | 4.09 | PW (82) 4.19 | -0.27 |
| 230 / 216 | assumed | Long iron | 3.57 | 29 % | 5 % | 0 % | Mid iron (41) | 3.88 | 9-iron (81) 4.09 | -0.31 |
| 230 / 216 | central | Long iron | 3.77 | 15 % | 18 % | 8 % | Mid iron (41) | 3.97 | PW (92) 4.18 | -0.20 |
| 230 / 216 | pessimistic | Long iron | 3.87 | 11 % | 18 % | 12 % | Mid iron (41) | 4.03 | PW (92) 4.22 | -0.16 |
| 240 / 227 | assumed | 4-wood | 3.61 | 24 % | 77 % | 8 % | Mid iron (53) | 3.97 | 9-iron (90) 4.11 | -0.36 |
| 240 / 227 | central | Long iron | 3.88 | 8 % | 3 % | 9 % | Mid iron (52) | 4.05 | 9-iron (89) 4.20 | -0.17 |
| 240 / 227 | pessimistic | Long iron | 3.97 | 6 % | 4 % | 14 % | Mid iron (52) | 4.10 | 9-iron (89) 4.23 | -0.13 |
| 250 / 236 | assumed | 4-wood | 3.55 | 29 % | 45 % | 5 % | Mid iron (62) | 4.03 | 8-iron (86) 4.11 | -0.48 |
| 250 / 236 | central | Long iron | 3.97 | 3 % | 1 % | 9 % | Mid iron (60) | 4.12 | 8-iron (85) 4.20 | -0.15 |
| 250 / 236 | pessimistic | 4-wood | 4.03 | 9 % | 69 % | 28 % | Mid iron (60) | 4.16 | 8-iron (84) 4.24 | -0.13 |
| 260 / 245 | assumed | 4-wood | 3.60 | 25 % | 10 % | 2 % | Long iron (43) | 3.93 | 8-iron (96) 4.14 | -0.33 |
| 260 / 245 | central | 4-wood | 3.89 | 13 % | 57 % | 20 % | Long iron (43) | 4.05 | 8-iron (94) 4.22 | -0.16 |
| 260 / 245 | pessimistic | 4-wood | 3.97 | 11 % | 47 % | 21 % | Long iron (43) | 4.12 | 8-iron (94) 4.27 | -0.15 |
| 270 / 255 | assumed | 4-wood | 3.73 | 15 % | 1 % | 3 % | Long iron (54) | 4.01 | Mid iron (82) 4.12 | -0.28 |
| 270 / 255 | central | 4-wood | 3.86 | 13 % | 32 % | 15 % | Long iron (53) | 4.11 |  | -0.25 |
| 270 / 255 | pessimistic | 4-wood | 3.98 | 10 % | 29 % | 20 % | Long iron (53) | 4.18 |  | -0.20 |

### Hole 6 sun rough  (46.6 F)
| to middle / front | set | go: club | go strokes | green | carry front | trouble | best lay-up (leaves) | strokes | lay-up to 80-100 | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|
| 220 / 207 | assumed | Long iron | 3.62 | 24 % | 13 % | 2 % | Mid iron (39) | 3.89 | PW (89) 4.12 | -0.27 |
| 220 / 207 | central | Long iron | 3.87 | 12 % | 24 % | 13 % | Mid iron (40) | 4.02 | PW (87) 4.21 | -0.15 |
| 220 / 207 | pessimistic | Long iron | 4.14 | 5 % | 15 % | 26 % | Mid iron (47) | 4.19 | PW (92) 4.34 | -0.06 |
| 230 / 216 | assumed | Long iron | 3.75 | 11 % | 1 % | 2 % | Mid iron (49) | 3.97 | 9-iron (86) 4.13 | -0.23 |
| 230 / 216 | central | Long iron | 3.95 | 7 % | 9 % | 14 % | Mid iron (48) | 4.09 | 9-iron (84) 4.21 | -0.14 |
| 230 / 216 | pessimistic | Long iron | 4.19 | 2 % | 6 % | 25 % | Mid iron (56) | 4.25 | 9-iron (90) 4.36 | -0.06 |
| 240 / 227 | assumed | Long iron | 3.87 | 2 % | 0 % | 3 % | Mid iron (61) | 4.05 | 8-iron (84) 4.14 | -0.18 |
| 240 / 227 | central | Long iron | 4.04 | 3 % | 2 % | 16 % | Mid iron (59) | 4.15 | 8-iron (81) 4.23 | -0.11 |
| 240 / 227 | pessimistic | none | | | |  | Long iron (44) | 4.24 | 8-iron (88) 4.39 |  |
| 250 / 236 | assumed | none | | | |  | Long iron (42) | 3.95 | 8-iron (92) 4.16 |  |
| 250 / 236 | central | none | | | |  | Long iron (42) | 4.11 | 8-iron (91) 4.27 |  |
| 250 / 236 | pessimistic | none | | | |  | Long iron (51) | 4.28 | 8-iron (97) 4.42 |  |
| 260 / 245 | assumed | none | | | |  | Long iron (51) | 4.03 |  |  |
| 260 / 245 | central | none | | | |  | Long iron (51) | 4.17 |  |  |
| 260 / 245 | pessimistic | none | | | |  | Long iron (60) | 4.34 | Mid iron (84) 4.43 |  |
| 270 / 255 | assumed | none | | | |  | Long iron (62) | 4.11 | Mid iron (88) 4.17 |  |
| 270 / 255 | central | none | | | |  | Long iron (60) | 4.22 | Mid iron (87) 4.31 |  |
| 270 / 255 | pessimistic | none | | | |  | Long iron (69) | 4.37 | Mid iron (94) 4.47 |  |

### Hole 13 sun fairway  (50.8 F)
| to middle / front | set | go: club | go strokes | green | carry front | trouble | best lay-up (leaves) | strokes | lay-up to 80-100 | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|
| 220 / 204 | assumed | Long iron | 3.69 | 25 % | 24 % | 11 % | Mid iron (40) | 3.86 | PW (87) 4.06 | -0.16 |
| 220 / 204 | central | Long iron | 3.79 | 15 % | 32 % | 9 % | Mid iron (44) | 3.93 | PW (88) 4.08 | -0.15 |
| 220 / 204 | pessimistic | Long iron | 3.85 | 11 % | 28 % | 8 % | Mid iron (44) | 3.97 | PW (89) 4.10 | -0.13 |
| 230 / 214 | assumed | 4-wood | 3.62 | 24 % | 91 % | 6 % | Mid iron (48) | 3.91 | 9-iron (85) 4.06 | -0.29 |
| 230 / 214 | central | 4-wood | 3.86 | 5 % | 97 % | 4 % | Mid iron (50) | 3.97 | 9-iron (86) 4.08 | -0.11 |
| 230 / 214 | pessimistic | 4-wood | 3.88 | 6 % | 93 % | 4 % | Mid iron (52) | 4.01 | 9-iron (87) 4.10 | -0.13 |
| 240 / 224 | assumed | 4-wood | 3.60 | 30 % | 69 % | 8 % | Mid iron (57) | 3.96 | 8-iron (82) 4.05 | -0.36 |
| 240 / 224 | central | 4-wood | 3.79 | 11 % | 93 % | 5 % | Mid iron (58) | 4.01 | 8-iron (84) 4.07 | -0.22 |
| 240 / 224 | pessimistic | 4-wood | 3.84 | 10 % | 88 % | 6 % | Mid iron (60) | 4.05 | 8-iron (85) 4.10 | -0.21 |
| 250 / 234 | assumed | 4-wood | 3.75 | 18 % | 24 % | 9 % | Long iron (43) | 3.89 | 8-iron (93) 4.09 | -0.14 |
| 250 / 234 | central | 4-wood | 3.78 | 14 % | 67 % | 7 % | Long iron (47) | 3.98 | 8-iron (95) 4.12 | -0.20 |
| 250 / 234 | pessimistic | 4-wood | 3.85 | 10 % | 56 % | 7 % | Long iron (49) | 4.04 | 8-iron (96) 4.15 | -0.19 |
| 260 / 244 | assumed | 4-wood | 3.85 | 6 % | 2 % | 6 % | Long iron (51) | 3.95 |  | -0.09 |
| 260 / 244 | central | 4-wood | 3.83 | 13 % | 43 % | 9 % | Long iron (54) | 4.02 |  | -0.19 |
| 260 / 244 | pessimistic | 4-wood | 3.89 | 9 % | 37 % | 8 % | Long iron (56) | 4.07 | Mid iron (80) 4.12 | -0.17 |
| 270 / 254 | assumed | 4-wood | 3.87 | 1 % | 0 % | 2 % | Long iron (62) | 4.00 | Mid iron (89) 4.07 | -0.13 |
| 270 / 254 | central | 4-wood | 3.91 | 7 % | 20 % | 8 % | Long iron (63) | 4.05 | Mid iron (90) 4.12 | -0.14 |
| 270 / 254 | pessimistic | 4-wood | 3.96 | 7 % | 19 % | 9 % | Long iron (65) | 4.09 | Mid iron (91) 4.15 | -0.13 |

### Hole 13 sun rough  (50.8 F)
| to middle / front | set | go: club | go strokes | green | carry front | trouble | best lay-up (leaves) | strokes | lay-up to 80-100 | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|
| 220 / 204 | assumed | Long iron | 3.84 | 6 % | 6 % | 6 % | Mid iron (46) | 3.91 | 9-iron (81) 4.04 | -0.07 |
| 220 / 204 | central | Long iron | 3.91 | 8 % | 18 % | 10 % | Mid iron (50) | 4.00 | 9-iron (82) 4.08 | -0.09 |
| 220 / 204 | pessimistic | Long iron | 4.04 | 4 % | 12 % | 10 % | Mid iron (63) | 4.13 | 9-iron (92) 4.18 | -0.08 |
| 230 / 214 | assumed | Long iron | 3.88 | 1 % | 0 % | 3 % | Mid iron (55) | 3.97 | 9-iron (91) 4.08 | -0.08 |
| 230 / 214 | central | Long iron | 3.98 | 2 % | 5 % | 6 % | Mid iron (58) | 4.04 | 8-iron (81) 4.09 | -0.06 |
| 230 / 214 | pessimistic | none | | | |  | Long iron (49) | 4.10 | 8-iron (92) 4.20 |  |
| 240 / 224 | assumed | none | | | |  | Long iron (42) | 3.90 | 8-iron (89) 4.07 |  |
| 240 / 224 | central | none | | | |  | Long iron (44) | 4.02 | 8-iron (91) 4.13 |  |
| 240 / 224 | pessimistic | none | | | |  | Long iron (54) | 4.16 |  |  |
| 250 / 234 | assumed | none | | | |  | Long iron (50) | 3.96 | 8-iron (100) 4.12 |  |
| 250 / 234 | central | none | | | |  | Long iron (55) | 4.06 |  |  |
| 250 / 234 | pessimistic | none | | | |  | Long iron (68) | 4.19 | Mid iron (92) 4.22 |  |
| 260 / 244 | assumed | none | | | |  | Long iron (59) | 4.01 | Mid iron (86) 4.07 |  |
| 260 / 244 | central | none | | | |  | Long iron (64) | 4.09 | Mid iron (89) 4.14 |  |
| 260 / 244 | pessimistic | none | | | |  | Long iron (79) | 4.21 | Mid iron (100) 4.26 |  |
| 270 / 254 | assumed | none | | | |  | Long iron (70) | 4.04 | Mid iron (97) 4.11 |  |
| 270 / 254 | central | none | | | |  | Long iron (72) | 4.12 | Mid iron (99) 4.19 |  |
| 270 / 254 | pessimistic | none | | | |  | Long iron (87) | 4.24 | Long iron (87) 4.24 |  |

### Hole 18 sun fairway  (52.8 F)
| to middle / front | set | go: club | go strokes | green | carry front | trouble | best lay-up (leaves) | strokes | lay-up to 80-100 | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|
| 220 / 207 | assumed | 4-wood | 3.72 | 11 % | 98 % | 2 % | Mid iron (42) | 3.86 | PW (87) 4.06 | -0.14 |
| 220 / 207 | central | Long iron | 3.89 | 13 % | 25 % | 10 % | Mid iron (45) | 3.93 | PW (87) 4.07 | -0.04 |
| 220 / 207 | pessimistic | Long iron | 3.95 | 8 % | 23 % | 8 % | Mid iron (45) | 3.96 | PW (88) 4.08 | -0.01 |
| 230 / 216 | assumed | 4-wood | 3.61 | 28 % | 87 % | 5 % | Mid iron (49) | 3.91 | 9-iron (85) 4.05 | -0.29 |
| 230 / 216 | central | 4-wood | 3.88 | 6 % | 97 % | 3 % | Mid iron (52) | 3.95 | 9-iron (85) 4.06 | -0.06 |
| 230 / 216 | pessimistic | 4-wood | 3.92 | 8 % | 92 % | 6 % | Mid iron (52) | 3.98 | 9-iron (86) 4.08 | -0.06 |
| 240 / 225 | assumed | 4-wood | 3.63 | 32 % | 65 % | 7 % | Mid iron (57) | 3.95 | 8-iron (81) 4.04 | -0.32 |
| 240 / 225 | central | 4-wood | 3.85 | 10 % | 92 % | 6 % | Mid iron (59) | 3.97 | 8-iron (81) 4.05 | -0.12 |
| 240 / 225 | pessimistic | 4-wood | 3.90 | 10 % | 87 % | 7 % | Mid iron (60) | 4.00 | 8-iron (82) 4.07 | -0.10 |
| 250 / 237 | assumed | 4-wood | 3.80 | 21 % | 18 % | 11 % | Long iron (44) | 3.89 | 8-iron (94) 4.10 | -0.09 |
| 250 / 237 | central | 4-wood | 3.88 | 13 % | 63 % | 9 % | Long iron (47) | 3.97 | 8-iron (94) 4.11 | -0.08 |
| 250 / 237 | pessimistic | 4-wood | 3.96 | 9 % | 52 % | 8 % | Long iron (49) | 4.01 | 8-iron (95) 4.13 | -0.05 |
| 260 / 247 | assumed | 4-wood | 3.87 | 10 % | 1 % | 6 % | Long iron (52) | 3.93 |  | -0.06 |
| 260 / 247 | central | 4-wood | 3.94 | 11 % | 38 % | 10 % | Long iron (54) | 3.98 |  | -0.04 |
| 260 / 247 | pessimistic | 4-wood | 4.01 | 8 % | 33 % | 11 % | Long iron (56) | 4.02 |  | -0.01 |
| 270 / 255 | assumed | 4-wood | 3.88 | 3 % | 0 % | 3 % | Long iron (60) | 3.96 | Mid iron (87) 4.06 | -0.08 |
| 270 / 255 | central | 4-wood | 3.98 | 9 % | 21 % | 11 % | Long iron (63) | 4.00 | Mid iron (88) 4.08 | -0.02 |
| 270 / 255 | pessimistic | 4-wood | 4.03 | 5 % | 19 % | 8 % | Long iron (63) | 4.03 | Mid iron (88) 4.10 | +0.00 |

### Hole 18 sun rough  (52.8 F)
| to middle / front | set | go: club | go strokes | green | carry front | trouble | best lay-up (leaves) | strokes | lay-up to 80-100 | go - lay-up |
|---|---|---|---|---|---|---|---|---|---|---|
| 220 / 207 | assumed | Long iron | 3.86 | 9 % | 3 % | 6 % | Mid iron (48) | 3.90 | 9-iron (81) 4.04 | -0.04 |
| 220 / 207 | central | Long iron | 3.99 | 7 % | 14 % | 9 % | Mid iron (51) | 3.98 | 9-iron (82) 4.05 | +0.00 |
| 220 / 207 | pessimistic | Long iron | 4.10 | 3 % | 9 % | 10 % | Mid iron (60) | 4.07 | 9-iron (88) 4.11 | +0.03 |
| 230 / 216 | assumed | Long iron | 3.89 | 2 % | 0 % | 3 % | Mid iron (56) | 3.95 | 9-iron (91) 4.08 | -0.06 |
| 230 / 216 | central | Long iron | 4.01 | 3 % | 4 % | 5 % | Mid iron (59) | 4.00 | 9-iron (92) 4.09 | +0.01 |
| 230 / 216 | pessimistic | none | | | |  | Mid iron (66) | 4.08 | 8-iron (88) 4.12 |  |
| 240 / 225 | assumed | none | | | |  | Long iron (43) | 3.90 | 8-iron (87) 4.06 |  |
| 240 / 225 | central | none | | | |  | Long iron (48) | 4.01 | 8-iron (88) 4.08 |  |
| 240 / 225 | pessimistic | none | | | |  | Mid iron (73) | 4.10 | 8-iron (97) 4.17 |  |
| 250 / 237 | assumed | none | | | |  | Long iron (51) | 3.93 |  |  |
| 250 / 237 | central | none | | | |  | Long iron (56) | 4.02 |  |  |
| 250 / 237 | pessimistic | none | | | |  | Long iron (64) | 4.13 | Mid iron (86) 4.14 |  |
| 260 / 247 | assumed | none | | | |  | Long iron (60) | 3.97 | Mid iron (85) 4.06 |  |
| 260 / 247 | central | none | | | |  | Long iron (63) | 4.03 | Mid iron (87) 4.09 |  |
| 260 / 247 | pessimistic | none | | | |  | Long iron (72) | 4.14 | Mid iron (95) 4.20 |  |
| 270 / 255 | assumed | none | | | |  | Long iron (68) | 4.00 | Mid iron (96) 4.11 |  |
| 270 / 255 | central | none | | | |  | Long iron (70) | 4.05 | Mid iron (95) 4.14 |  |
| 270 / 255 | pessimistic | none | | | |  | Long iron (78) | 4.16 |  |  |
