# Gate v2: which auto-built holes and courses can skip the human tap

Built 2026-10-30 by `course_data/library/gate/gate_v2_eval.py` (numbers below) from `gate_v2.py` (the rules).
It reads only a page's `qa.json`, the output of `picture_checks.py`, and changes nothing upstream.

    python3 course_data/library/gate/gate_v2.py course_data/library/<slug>/qa.json [--json]
    python3 course_data/library/gate/gate_v2_eval.py [--target 0.95] [--csv rows.csv]   # about 90 s

## Data (small: treat every number as approximate)

* **Review labels.** `course_data/library/<slug>/review.json` from 23 courses. A verdict of OK counts as right. Anything else counts as wrong: wrong tee position, wrong yardage, wrong par, wrong routing, or bad pick.
  * A verdict covers the whole hole, so it is applied to every tee set of that hole. The exception is a `fix.tee_ll` keyed by some but not all of the page's sets: then only those sets count as wrong.
  * Holes marked `missing` have no page row. They make the course unsafe.
* **Truth labels.** The 10 hand-truth gate builds in `gate/gate_eval.json`. A row is wrong when the club is not the same or a tie, or when the routing or par is wrong. Only the blind `auto` set is used.
* **Size.** 843 labelled hole x tee-set rows from 33 courses, of which 192 (23%) are wrong. The errors cluster heavily by course: 8 courses hold about 75% of the wrong rows. So the effective sample size is closer to 33 than to 843.
* **Safe courses.** Only 4 of the 33 have no wrong hole at all (adams_pointe, blue_hills, eagle_knoll, hot_springs_arlington).

Wrong rate by failed check (a row counts once under each check it fails):

| failed check | rows | wrong |
|---|---|---|
| none (PASS) | 494 | 43 (9%) |
| tee: walk-back, yardage matches the card | 51 | 37 (73%) |
| tee: lidar / texture pad / tee axis, yardage matches, course has OSM tees | 66 | 24 (36%) |
| tee: lidar / texture pad / tee axis, yardage matches, OSM maps **no** tees | 31 | 0 (0%) |
| par / yardage: no card at all (osm_back) | 140 | 68 (49%) |
| yardage vs card off by more than 10 | 16 | 8 (50%) |
| aim: rough, no fairway mapped | 14 | 0 (0%) |
| aim: rough within 15 yds of fairway | 21 | 4 (19%) |
| aim: rough more than 15 yds out | 40 | 15 (38%) |
| aim: OB / sand / water / recovery | 14 | 9 |
| oval: over the hazard limit | 9 | 9 (100%) |
| par-3 box: no OSM green outline | 8 | 0 (0%) |

The pad rows are split by `osm_no_tees`. The 0/31 bucket is all Painted Hills, so this rule rests on one course. Where OSM does map tees, a pad tee means the build disagreed with OSM.

## Rule set (gate_v2.py)

**Course red flags.** Any one of these makes every hole CONFIRM.

* `no_card`: no web card matched (`card_holes` 0, or the set is `osm_back`). Of the 7 such courses, 3 are fine (Adams Pointe, Sycamore Ridge 17/18, Hot Springs) and 4 are bad (TPC Deere Run 17/18 wrong, Tournament Club of Iowa 18/18, Dub's Dread 8/18, National KC). Nothing in qa.json separates them.
* `holes_vs_card`: the number of holes built differs from the card's.
* `par_sum`: the pars do not sum to the card total, after taking out holes whose own par check already fails. Painted Hills' broken hole 17 ("par 17") therefore makes only hole 17 CONFIRM, not the whole course.
* `page_errors`: the page smoke test failed.
* `tee_fits`: more than 6 hole x set rows needed a walk-back, or are off the card yardage. This catches the scrambled or wrong-version cards: Eagle Bend has 16 rows with 16/18 holes wrong, Harvester has 7/18 wrong, and they are PASS holes the strict gate would trust.

**Hole x set.** On a course with no red flag, a hole x set is AUTO if it PASSes, or if every check it fails is benign:

* `tee`: OSM maps no tee boxes on the course, the tee is on a lidar pad, texture pad or the tee axis (not a walk-back), and the yardage is within 10 of the card.
* `aim`: no fairway is mapped and the pick lands in rough.
* `par3_box`: no OSM green outline.
* Everything else is CONFIRM: walk-backs, yardage or par off the card, aim in OB, water or sand, and oval over the limit.

A course is AUTO only when it has no red flag and zero CONFIRM holes. Otherwise the CONFIRM holes are the golfer's tap list.

## Results

| gate | AUTO hole x set | coverage | wrong among AUTO | precision |
|---|---|---|---|---|
| strict (PASS only) | 494 / 843 | 59% | 43 | 91.3% |
| v2 defaults, all 33 courses | 479 / 843 | 57% | 23 | 95.2% |
| v2 leave-one-course-out, params tuned to 95% on the other 32 | 443 / 843 | 53% | 27 | 93.9% |
| v2 leave-one-course-out, tuned to 92% (picks pads always benign, aim 50) | 571 / 843 | 68% | 57 | 90.0% |
| **holdout: 7 reviews that arrived after the rules were written** (strict) | 173 / 234 | 74% | 8 | 95.4% |
| **holdout: same 7, v2** | 150 / 234 | 64% | 4 | 97.3% |

* The holdout courses are amana_colonies, annbriar, finkbine, harvester, prairie_highlands, the_falls_ofallon and tournament_club_iowa.
* A course bootstrap (2000 resamples, in-sample defaults) puts the precision gain of v2 over strict at +0.1 to +10.8 points (90% interval). P(gain ≤ 0) = 1.5%. Strict is 83 to 97%; v2 is 90 to 98.5%.
* At about the same coverage, v2 roughly halves the wrong picks among auto-trusted holes (5% wrong instead of 9%). It does this by:
  * moving whole bad-card courses (Eagle Bend, Harvester) to CONFIRM;
  * trusting pad tees where OSM has none, plus harmless aim and green-outline CHECKs (Painted Hills goes from 18 taps to 4).
* The permissive tuning shows the risk of over-fitting the benign list. Trusting lidar pads where OSM has tees, or rough landings far from the fairway, does worse out of sample than the strict gate.

**Ablations** (in-sample, one change at a time):

| change | coverage | precision |
|---|---|---|
| no course red flags | 63% | 91.8% |
| `tee_fits` off | 62% | 91.9% |
| pad tees never benign | 53% | 94.9% |
| pad tees always benign | 63% | 93.0% |
| aim rough ≤15 yds benign | 59% | 95.2% |

The course flags carry most of the gain.

## Courses

**Whole-course AUTO: 0 of 33** under both strict and v2.

* The irreducible problem is PASS holes that are wrong because the card is a different version, the tee set labels are swapped, or the pick is bad. Weaver Ridge alone has 11 such rows. qa.json cannot see these. About 5% of v2-AUTO rows are still wrong.
* Getting a course to auto-OK would need a second card source to agree, which is a card check rather than a picture check.

**Tap-list mode** (no red flag, at most K CONFIRM holes; "clean" = every wrong hole is on the tap list):

| K | strict: courses / clean | v2: courses / clean |
|---|---|---|
| 2 | 6 / 3 | 6 / 3 |
| 4 | 11 / 5 | 12 / 6 |
| 6 | 15 / 6 | 16 / 7 |

* With K = 2, the courses are annbriar (tap 9, 13), old_kinderhook (tap 9; misses 15, a PASS with the wrong yardage), prairie_highlands (tap 11, 17; both wrong, both caught), blue_hills (tap 2), eagle_knoll (tap 1) and gateway_national (tap 8; misses the 9 and 11 clubs).
* Today's library (36 qa.json files): no course is AUTO. The shortest tap lists are old_kinderhook (1), annbriar (2), prairie_highlands (2), then buffalo_ridge, rivercut, shoal_creek and tiffany_greens / tomahawk_hills (3 each).

## Recommendation

* Use v2 per hole: auto-trust AUTO holes, ask the golfer to confirm the CONFIRM holes, and never auto-publish a course with a red flag.
* Do not auto-publish whole courses yet. No course passed with zero taps, and only half of the short-tap-list courses were fully clean.
* Re-run `gate_v2_eval.py` as more review.json files land. With about 10 more clean-card courses, the `no_card` flag and the "pad tee where OSM has tees" rule can be revisited.
