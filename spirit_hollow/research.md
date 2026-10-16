# Research: amateur baselines, driver dispersion, penalties, DECADE tee rules

Target player: about a 5 handicap who shoots 72-82 (average about 77) on a par-72 course.
Compiled 2026-10-16. Direct page fetches were blocked in this environment (DNS failures
on golf.com, golfdigest.com, mygolfspy.com, columbia.edu and others). Every number below
comes from search-engine extracts of the linked pages, not from reading the full pages.
Treat each one as "reported by the linked page" and spot-check it before relying on it.

Labels used: **[P]** = a number published directly by the source. **[I]** = my inference or
calculation from published numbers.

---

## 1. Recommended parameters for a ~5 handicap (summary)

| Parameter | Current model | Recommended | Basis | Confidence |
|---|---|---|---|---|
| Driver lateral SD (sigma) | 65/(2*1.96) = 16.6 yd | **20-22 yd** (use 21) | [I] fitted to the [P] stats below: about 49% fairways hit, about 7% of drives more than 40 yd from fairway centre, and about 90% of 0-5 players keeping at least 75% of drives within 30 yd | Medium |
| "Dispersion width" (95% lateral window) | 65 yd | **about 80-85 yd** | [I] = 2 x 1.96 x sigma | Medium |
| Lateral tail shape | Normal, optional t(nu=5) | **Normal (or t with nu >= 10)** once sigma is widened | [I] With sigma about 21, a normal fit already matches the published share of drives beyond 40 yd. A t5 scaled to the same 95% window gives too many fairway hits. | Low-medium |
| Driver total distance (average) | (app value) | **about 245 yd average total; about 260 on a solid strike** | [P] Arccos: men scratch-4.9 average 244 yd. [P] Shot Scope P-avg: 5 hcp 261, 10 hcp 259 | Medium-high |
| Fairway-hit % with driver (sanity check) | implied about 63% on a 30-yd fairway | **about 49%** | [P] Shot Scope: 5 hcp 49%, with 23% missed left and 24% right | High (as a target) |
| 5-hcp fairway expected strokes minus tour | +0.25 + 0.0012*(d-150), i.e. +0.19 at 100 yd and +0.25 at 150 yd | **about +0.35 at 100 yd, about +0.40 at 150 yd, about +0.45 at 200 yd**, i.e. +0.40 + 0.001*(d-150) | [I] from [P] scratch 3.04 at 100 yd (tour 2.80) plus [P] "a 5 index from 100 yd averages the same as scratch from 150 yd" | Low-medium |
| Rough penalty vs fairway (multiplier on tour gap) | 1.3x | **about 0.6-0.8x** at approach distances, and about 0 for long holes (2nd shots of 200+ yd) | [P] Stagner: 5 index, 80-89 yd, rough is +0.11 vs fairway (tour is about +0.2). [P] 10 index: 160 fw = 140 rough. [P] On holes of 450+ yd, essentially no fw/rough difference for 5+ index | Medium |
| Fairway/greenside sand penalty multiplier | 1.3x | **about 1.0-1.2x** | [P] Shot Scope: fairway bunker costs +0.19/hole for scratch and +0.45 for a 15 hcp (interpolated to about +0.28 for a 5 [I]). [P] Bunker is about 0.5 worse than grass for 50-150 yd approaches | Low-medium |
| Recovery (trees) penalty multiplier | 1.3x | **keep 1.3x; 1.5x is plausible** | [P] Arccos 10 index: 0 recovery shots = 81.0 avg, 2 = 83.9, 4+ = 87.4, i.e. about 1.45 strokes per recovery event, confounded with bad rounds. The tour recovery-vs-fairway gap is about 0.8 | Low |
| OB / lost (stroke and distance) | re-tee, +1 stroke | **cost about 2.0 strokes vs the starting tee value** | [P] Broadie: a stroke-and-distance penalty is SG of about -2 | High |
| Water (lateral/penalty-area drop) | (model value) | about 1 stroke + a rough/drop lie; **about 1.2-1.4 strokes vs fairway** [I] | Rules + baselines | Medium |
| Penalties per round (calibration target) | n/a | **about 1.0-1.4 per round** (all shots) | [P] Arccos: scratch-5 band 1.03, 6-10 band 1.39 | Medium |
| Tee-shot penalty rate with driver | n/a | **about 1-3% of drives** on typical courses. Recovery-or-penalty about 12% of drives | [P] Shot Scope 1% (5 hcp), 2% (10 hcp). [P] Arccos scratch-4.9: 12% penalty-or-recovery, 88% in play | Medium |
| Long grass / native lost-ball probability | 50% | **no published number. Keep 50% as an assumption and run a sensitivity sweep over 25-75%** | none found | Very low |
| Driver vs 3-wood decision | (DECADE corridor) | Driver by default. Club down only when "dead" hazards (OB/water/jail trees) are within about 65-70 yd of each other | [P] Fawcett 70-yd rule (Golf Digest), 65 yd (Golf.com) | Medium-high |

**Most important change.** The 65-yd dispersion is a DECADE/tour-pattern number. Applied as a 95% window,
it makes a 5 handicap about 30% straighter (sigma 16.6) than the amateur tracking data shows (sigma about 21).
At 16.6 yd, the model predicts about 63% fairways on a 30-yd fairway and about 1.6% of drives beyond 40 yd.
The published values for 0-10 handicaps are about 49% and about 7%.

---

## 2. Expected strokes by distance and lie for amateurs

The Arccos, Shot Scope and Broadie amateur tables are mostly paywalled or app-only. No complete
5-hcp or 10-hcp table by distance and lie is publicly available. The published anchor points are:

- **Scratch, 100 yd fairway: about 3.04 strokes** [P]. Lou Stagner, X post:
  https://x.com/LouStagner/status/1464285564811816966 (tour baseline is about 2.80, so the gap is +0.24 [I]).
- **Scratch, 120 yd fairway: about 3.05 strokes** [P], from a secondary summary of Stagner's
  "seven stats for scratch players" thread:
  https://www.compleatgolfer.com/golf/scratch-golfer-stats-that-will-shock-you/ and
  https://x.com/LouStagner/status/1748076560110813190 (tour about 2.85, gap +0.20 [I]).
  The same thread gives scratch proximity of **about 37 ft from 150 yd fairway** [P]. Broadie's figure
  for tour pros is 23 ft from the same spot [P], and he puts 80-golfers at about 40 ft (50% GIR) and
  90-golfers at about 55 ft (just over 30% GIR):
  https://golf.com/instruction/analytics-expert-weekend-golfers-save-strokes/
- **Distance equivalence to scratch at 150 yd fairway** [P] (Stagner, Arccos data, Hack It Out
  Golf podcast "Handicap Skill Tiers by the Numbers"): a **5 index needs to be about 100 yd away**
  to average what scratch averages from 150. The transcript summary also gives 10 index = 53 yd,
  15 = 36 yd and 20 = 27 yd. The 10/15/20 figures may be mis-transcribed, so verify them.
  https://podcastrex.com/shows/hack-it-out-golf/handicap-skill-tiers-by-the-numbers/transcript
- **Arccos illustration:** "an average 5-handicap golfer takes 3.2 strokes to hole out from 150 yards" [P].
  This is offered as an example, not as a measured table value:
  https://www.arccosgolf.com/blogs/community/understanding-strokes-gained
- **Stagner fairway-vs-rough newsletters** (Arccos data):
  - #2: 5 index, 80-89 yd: **rough averages +0.11 strokes vs fairway**. About half the cells in his
    table are 0.10 or less [P].
    https://newsletter.loustagnergolf.com/p/newsletter-2-why-fairways-are-overrated-for-amateur-players
  - #58 and Golf Digest: **scratch 90 yd fw = 67 yd rough; 10 hcp 160 yd fw = 140 yd rough** [P],
    with the gap "basically disappearing" at longer distances for higher handicaps.
    https://newsletter.loustagnergolf.com/p/fairway-vs-rough ,
    https://www.golfdigest.com/story/how-hard-should-you-swing-test-explains-fairway-vs-rough-tradeoff-stats-golf-digest-mythbusters
  - #30: for a 5+ index on any hole of 450+ yd, there is **essentially no difference between rough and
    fairway** [P]. 10 index, 325-yd hole: about 174 yd drive in the fairway vs 196 in the rough to
    break even [P]. https://newsletter.loustagnergolf.com/p/how-far-is-a-good-drive
  - For comparison, the tour fw-to-rough gap is "30-80 yards depending on hole length" [P, secondhand]:
    https://forum.practical-golf.com/t/bomb-and-gouge/503?page=2
- **Shot Scope lie effects (amateurs):** for 50-150 yd approaches, bunker is about 0.5 strokes worse than
  grass [P]. Proximity from 60-100 yd is about 40 ft from fairway, 46 ft from rough and 56 ft from bunker [P].
  https://shotscope.com/blog/practice-green/stats-and-data/such-a-thing-as-a-good-miss/ ,
  https://shotscope.com/blog/practice-green/stats-and-data/approach-shots-average-proximity/
- **Shot Scope bunker scoring cost per hole:** fairway bunker **+0.19 (0 hcp) and +0.45 (15 hcp)**;
  greenside bunker +0.43 and +0.50 [P].
  https://mygolfspy.com/news-opinion/instruction/fairway-vs-greenside-bunkers-which-hurts-your-score-more/
  Shot Scope also says the fairway bunker is "the worst place for an amateur to hit their tee shot",
  costing about 1.4 shots per round [P].
  https://shotscope.com/blog/practice-green/stats-and-data/analysing-driving-accuracy/
- **Shot Scope handicap benchmarks** (Strokes Gained ebook) [P]: score to par is +0.83 (0), +6.33 (5) and
  +10.88 (10). GIR is 61%, 44% and 36%. Penalty shots per round are about 0.56 at 0 and 4.67 at 25.
  https://shotscope.com/ebook/Strokes_Gained.pdf
- **Broadie (tour baseline the model already uses):** 140 yd is 2.91 from fairway, 3.15 from rough and 3.22
  from sand. 150 yd fairway is 2.98 [P]. https://columbia.edu/~mnb2/broadie/Assets/strokes_gained_pga_broadie_20110408.pdf .
  Broadie's book publishes tour tables (Table 5.2) but **no amateur-by-lie table**. A reader asked
  him for one and none was given:
  https://www.golfclubatlas.com/forum/index.php?topic=66559.75
- **Broadie, amateur gap sizes:** the 70-vs-80 shooter gap is about 1.5 strokes from putting vs about 6.5
  from shots of 100+ yd [P]. 90-golfers lose about 3 shots/round to "awful" drives and 80-golfers about
  1.8 [P]. https://golf.com/instruction/smart-players-guide-drop-10-shots/

**Inference for the 5-hcp fairway curve [I]:** scratch is about tour +0.24 at 100 yd. A 5 index at 100 yd
equals scratch at 150 yd. Scratch at 150 is likely about 3.15-3.20, because the gap widens with
distance as proximity grows from 23 to 37 ft. That puts a 5 index at 100 yd at about 3.15-3.20, i.e.
**tour +0.35-0.40**. Extrapolating, +0.40 at 150 and about +0.45 at 200. Round check: about 14 approach
shots x 0.4 + about 1.5 driving + about 2.5 short game/putting is roughly 9-10 strokes behind tour.
That is consistent with a 77 shooter vs a tour pro's roughly 67-68 on a member course. The model's
current +0.25 at 150 (and +0.19 at 100) looks about 0.15 stroke too generous to the player. A
uniform shift does not change tee-shot rankings much, but the lie multipliers do (see below).

**Inference for lie multipliers [I]:** amateur rough penalties are *smaller* than tour rough
penalties at approach distances. The likely reasons are that tour rough is thicker and amateurs gain
less from a fairway lie. The 1.3x rough multiplier therefore overstates the cost of missing the
fairway, and that pushes the model toward too-conservative tee clubs. Use about 0.7x for rough and
about 1.1x for sand. Keep 1.3-1.5x for recovery and trees.

---

## 3. Driver dispersion and distance for amateurs

**Fairways hit and miss split (Shot Scope, driver only)** [P]:
- 0 hcp 48%; 5 hcp **49% fw, 23% left, 24% right, 1% penalty**; 10 hcp **49% fw, 24% left, 25% right, 2% penalty**;
  15 and 20 hcp 2-3% penalty. Fairway % is nearly flat from scratch to 25 hcp.
  https://mygolfspy.com/news-opinion/driver-distance-chart-2026-update-how-far-golfers-hit-it-by-handicap/ ,
  https://www.nationalclubgolfer.com/equipment/drivers/is-it-better-to-hit-your-driver-straighter-or-further/
  (an older version gives 46/49/50% for 0/5/10).
- Tour driver fairway % is about 57-61% [P]. 3-wood hits only about 1.5% more fairways than driver
  for amateurs [P]: https://shotscope.com/blog/practice-green/stats-and-data/analysing-driving-accuracy/

**Distance from centre (Lou Stagner / Arccos)** [P]:
- "Big miss" (more than 40 yd from fairway centre): **7.0% of drives for 0-5 index, 7.3% for 5-10**,
  7.7% for 10-15 and 7.8% for 15-20. Only about 1-2.5% of golfers keep 99%+ within 40 yd.
  https://newsletter.loustagnergolf.com/p/big-miss-with-driver
- Within 30 yd of fairway centre: only **about 10% of 0-5 players keep fewer than 75%** of drives inside
  30 yd. 18% of 0-5 players are in the 75-79% bin. The minimum sample was 250 drives/year. The target
  is unknown, so this is "directional" [P].
  https://newsletter.loustagnergolf.com/p/shots-in-play-with-driver
- One 6.1-index player on a GC Quad: 17.5% of drives more than 30 yd offline with a 45.5-in driver and
  12.4% with a 42.75-in driver [P]: https://x.com/LouStagner/status/1774806517780226504
- 3-wood is 20+ yd narrower than driver for 28% of players and 30+ yd narrower for 9%, but driver is
  usually 25+ yd longer [P]: https://newsletter.loustagnergolf.com/p/should-you-always-hit-driver

**Fit to a normal distribution [I]** (centred aim; fractions within +/- x yd):

| sigma (yd) | 30-yd fw | 35-yd fw | within 30 yd | beyond 40 yd | 95% window |
|---|---|---|---|---|---|
| 16.6 (current) | 63% | 71% | 93% | 1.6% | 65 |
| 20 | 55% | 62% | 87% | 4.6% | 78 |
| **22** | **50%** | 57% | **83%** | **6.9%** | 86 |
| 24 | 47% | 53% | 79% | 9.6% | 94 |

sigma of about 21-22 matches all three published 0-10 handicap stats at once (49% fw on roughly 30-35 yd
fairways, about 7% beyond 40, and a typical player at about 80-85% within 30). A Student-t(5) scaled to
the same 95% window concentrates more mass in the middle: an 80-yd window gives 62% fw and 89%
within 30, with only 5% beyond 40. **The published amateur data does not call for extra tail weight
out to 40 yd.** No dataset was found for the extreme tail (more than 60 yd, i.e. shanks/tops/hooks into
the next fairway). Aim error and lateral/carry correlation are absorbed in these "from centre"
numbers. The published L/R split is close to symmetric (23/24) for a 5 hcp, so a small or zero
mean bias is appropriate unless the player's own data says otherwise.

**Fairway width reference:** the USGA rating guidance is 32 yd for scratch and 40 yd for a 20-hcp
"to regularly hit fairways". Typical widths are 30-45 yd [P]:
https://www.golfcourseindustry.com/article/design-concepts-debating-fairway-widths

**DECADE / tour pattern sizes:** Fawcett says a tour player's driver pattern is "every ounce of 70 yards"
[P]. He also says 10-handicaps who hit it 200 yd can be more offline in degrees and still have the same
70-yd pattern [P]. https://www.golfdigest.com/story/course-management-expert-scott-fawcett-tips-smarter-golf .
A launch-monitor test of near-scratch players gave about 65-70 yd ("what Fawcett usually sees with
scratch or better") [P]: https://practical-golf.com/golf-ball-control . Three single-digit players on GC Quad
gave about 70 yd "after discounting the occasional off-the-planet outlier" [P]:
https://www.australiangolfdigest.com.au/?p=96385 .
[I] These are pattern widths for **good** swings with outliers trimmed, and often range-measured.
They are not 95% windows of on-course drives. Tour sigma inferred from about 60% fairways on about 30-yd
fairways is about 18 yd (95% window about 70 yd), so "70 yd" is roughly a tour 95% window. A 5 hcp is wider.

**Broadie research:** tour players are "about twice as straight" in degrees as amateurs and much
longer. Longer hitters tend to be straighter [P]. Direction is measured as the SD of angle; 4 deg is
about 14 yd at 200 and 21 yd at 300 [P].
http://www.columbia.edu/~mnb2/broadie/Assets/broadie_wscg_v_200804.pdf (could not fetch; the per-group
SD table was not in the extracts). [I] At 250 yd, sigma = 21 yd is about 4.8 deg.

**Driver distance by handicap:**
- Shot Scope P-avg (solid strikes, mishits filtered): 0 = 285, **5 = 261, 10 = 259**, 15 = 236, 20 = 225 [P].
  https://mygolfspy.com/news-opinion/driver-distance-chart-2026-update-how-far-golfers-hit-it-by-handicap/
- Arccos (all driver tee shots on par 4/5, men): **scratch-4.9 = 244 yd**, 30+ = 181, all men 224 [P].
  https://www.arccosgolf.com/blogs/community/arccos-golf-releases-largest-ever-annual-driving-distance-report-leveraging-data-from-25-million-rounds-to-deliver-eight-year-trend-analysis-across-age-gender-and-skill-level ,
  https://sports.yahoo.com/articles/arccos-data-shows-amateur-driving-180026276.html
- Stagner: scratch amateurs average about 260 yd [P]. A 10-index's average is about 220 at sea level [P, via MyGolfSpy].
- [I] For a 5 who averages 77, use a **mean of about 240-250 yd total** with a long-tail mishit component
  (P-avg 260 = good strike). If the model uses a symmetric carry SD, about 15-20 yd plus a short-miss
  skew is reasonable. Distance error is not well documented for amateurs.

---

## 4. Penalty, lost-ball and recovery rates and costs

- **Penalties per round (Arccos):** scratch-5 band **1.03**, 6-10 band **1.39**, 11-15 band 1.66, 16-20 band 1.94, 20+ band 2.43.
  Rounds with 2+ penalties: 27% (scratch-5), 36% (6-10) [P].
  https://mygolfspy.com/news-opinion/the-secret-weapon-every-tour-pro-uses-and-most-amateurs-ignore/
- **Penalty or forced recovery per driver tee shot (Arccos 2026 report):** **12% for scratch-4.9** (88% in play);
  45% for 30+ [P]. Arccos (older): 10-15 hcp hit "almost 7%" of drives into a penalty situation [P]:
  https://www.golfdigest.com/story/golf-digest-arccos-data-driving-stats-amateur-golfer-distance-report
- **Shot Scope tee-shot penalty rate:** 1% (0 and 5 hcp), 2% (10, 15), 3% (20, 25) [P] (link above).
  [I] The large difference from Arccos (about 7% at 10-15) is about definition and course mix: penalty
  only vs penalty-area situation. For a course with OB/water/native, calibrate so that a 5 hcp
  takes about 1.0-1.4 penalty strokes per round in total.
- **Recovery shots:** Arccos 10 index, no penalties: **0 recoveries = 81.0, 2 = 83.9, 4+ = 87.4** [P]. That is
  about 1.45 strokes per recovery event [I], but it is confounded because bad rounds have both more
  recoveries and worse play elsewhere.
  https://podcastrex.com/shows/hack-it-out-golf/sms-10-index-scoring-with-no-penalties-but-recovery-shots
  Best-round recovery counts (Golf Monthly / Shot Scope): 0.39 (scratch), 0.71 (5), 1.18 (10) [P].
  https://www.golfmonthly.com/features/how-many-strokes-do-amateur-golfers-lose-each-round-due-to-wayward-shots-the-numbers-paint-an-interesting-picture
  Illustrative SG of a punch-out drive vs a fairway drive is about -0.57 vs +0.18 (tour baseline) [P]:
  https://golfity.com/blog/strokes-gained-off-the-tee-calculator
- **Stroke and distance (OB/lost):** SG of about **-2** [P]. Broadie, https://golf.com/instruction/smart-players-guide-drop-10-shots/
  Broadie's 80-shooter example has about 7% of drives OB on a tight hole, motivating aiming away from OB [P, secondhand].
- **Long grass / native lost-ball rate:** **no published figure found.** [I] Lost-ball probability depends on
  depth of native, distance past the mowed edge and spotter quality. Keep 50% as an explicit
  assumption, perhaps graded: about 20-30% within 5-10 yd of the rough line, about 60-80% deep in native.
  Show a sensitivity sweep.
- Stagner's practical rule: if driver sends more than about 5% of tee shots OB on a hole, consider clubbing down [P, secondhand]:
  https://newsletter.loustagnergolf.com/p/what-club-off-the-tee

---

## 5. DECADE tee-shot rules and rationale

- **70-yard rule** [P]: "If there are at least 70 yards between areas that would leave a player totally
  dead (a water hazard, an out of bounds, a waist-high clump of cabbage), Fawcett will always instruct his
  players to hit driver." If there is less space, consider the width where a 3-wood would finish, and if
  that is much wider, 3-wood is the play.
  https://www.golfdigest.com/story/course-management-expert-scott-fawcett-tips-smarter-golf
- Golf.com version [P]: driver unless "penalty hazards are within 65 yards of each other on either side".
  https://golf.com/instruction/driving/when-to-hit-driver-golf/ . Forum paraphrases say "about 60 yd".
- **Default is driver** [P]: "there needs to be a very good reason not to hit it". For a tour player,
  driver over a shorter club gains about **0.07 strokes per hole**, so 6-7 more drivers a round is worth
  about half a stroke [P] (Golf Digest, above). The philosophy is "aggressive off the tee, conservative into greens" [P].
  https://golf.com/news/decade-stats-course-strategy-changing-how-pros-play/
- **What counts as a hazard:** only "dead" outcomes (OB, water, jail/trees that force a chip-out).
  Rough and sand are *not* treated as hazards for tee-shot corridor purposes [P, forum paraphrase of DECADE]:
  https://forums.golfwrx.com/topic/1830284-decade-question/
- **Aim** at the centre of the safe corridor between the dead zones, not the fairway centre [P]:
  https://www.globalgolfpost.com/more/golf-becoming-strictly-a-numbers-game/ . Stagner adds that picking a
  side of the fairway is "fool's gold" because dispersion is too big: shift the aim away from trouble,
  not toward a side, to minimise penalties [P]. Aiming at the whole fairway beat aiming at a small target
  (67% vs 50% fairways in a 32-golfer study) [P]: https://newsletter.loustagnergolf.com/p/does-aim-small-miss-small-really-work
- Rationale [I]: the corridor width (about 65-70 yd) is roughly the tour driver 95% window. When dead zones
  are farther apart than the pattern, the expected cost of a dead miss is small relative to the value of
  distance (tour: 10 yd is about 0.6-0.7 strokes/round [P], Stagner via golf.com). For a 5 hcp with sigma about 21 yd,
  the equivalent corridor is about **80-85 yd**. Under 65 yd, a 3-wood/hybrid needs checking via the model.

---

## 6. Caveats

- All amateur numbers are from Arccos/Shot Scope users: self-selected, sensor-tracked, mixed courses,
  with lie classifications that differ from ShotLink.
- "From fairway centre" metrics mix aim error, course shape and true dispersion. Using them to set
  sigma is appropriate for an on-course model, but not as a pure swing-dispersion estimate.
- No full public 5-hcp expected-strokes table exists. The +0.40 offset curve is an inference anchored
  on three published points and should be replaced by the player's own Arccos/Shot Scope baseline if available.
