# TPC Deere Run: rebuild QA (2026-11-02)

**Verdict: PUBLISH.** The page now carries the yard card (Gold 7,267 / Black 6,984, par 71). On every hole of both sets
the tee localizer put the tee on a mapped teeing ground (or, on 7, a lidar pad) at the card yardage. Pars, routing and
greens are as reviewed.

Page checked: `course_data/library/tpc_deere_run/page.html`, built 2026-11-02T05:06Z (GitHub Actions run 41388450661).
Both solved sets (Gold, Black) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I
looked at every phone hole picture. No build warnings. The request has no per-hole fixes (the metre-based ones stay
withdrawn).

## Tee vs card, every hole

Page yardage = card on all 36 hole-sets, and the measured length equals the card within 3 yds on every hole of
both sets (largest: 17 Gold 566 / 569).

| hole | Gold card / measured | Black card / measured | tee |
|---|---|---|---|
| 1 | 395 / 395 | 386 / 386 | OSM 680459607 (shared box, axis) |
| 2 | 561 / 561 | 546 / 547 | OSM 680716217 |
| 3 | 186 / 186 | 182 / 182 | OSM 680257926 |
| 4 | 454 / 453 | 443 / 443 | OSM 680461909 |
| 5 | 433 / 433 | 424 / 424 | OSM 680732161 |
| 6 | 367 / 367 | 357 / 357 | OSM 680747611 |
| 7 | 226 / 226 | 221 / 221 | **lidar pad** (21-26 yds from the nearest OSM box; CHECK) |
| 8 | 428 / 428 | 377 / 377 | OSM 681502371 / 681502369 (separate boxes) |
| 9 | 503 / 503 | 480 / 480 | Gold OSM 681505893 (p 0.57 vs a lidar pad); Black lidar pad |
| 10 | 596 / 596 | 576 / 576 | OSM 681507345 (Gold p 0.52 vs a lidar pad) |
| 11-18 | = card | = card | OSM boxes (one shared teeing ground per hole) |

Uncertain: 7 (both sets on a lidar pad) and 9 / 10 Gold (the localizer is close to 50/50 between the OSM ground and
a lidar pad just behind). In both cases the yardage is right either way.

## Holes

| hole | Gold | Black | note |
|---|---|---|---|
| 1-3, 5, 9-14, 16, 18 | OK | OK | |
| 4 | OK (marginal) | OK (marginal) | Driver aim 23-27 right, trees 22-31%. Model choice |
| 6 | OK | **pick doubtful** | Black Driver aim 34 right over the dogleg corner, fairway 1%, trees 21%, 74 yds in (Gold plays 4-wood). Not on the aim bound; model choice, not blocking |
| 7 | OK (uncertain tee) | OK (uncertain tee) | |
| 8 | OK (marginal) | OK | Gold 4-wood, trees 15% |
| 15, 17 | OK (marginal) | OK | Driver near the tree lines (trees 16-17%) |

## Remaining (optional)

Black 6 Driver pick (fairway 1%) is worth a look in the decide step. It is the only pick on this page that lands almost
entirely off the fairway.
