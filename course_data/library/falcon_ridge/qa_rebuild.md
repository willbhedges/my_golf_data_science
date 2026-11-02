# Falcon Ridge GC (Lenexa KS): rebuild QA, final pass (2026-11-02)

**Verdict: PUBLISH.** The mapper fairways on 6 / 8 / 9 / 13 / 15 are in, so the back-nine "fairway 0%" readings are
gone. The Blue 11 / 18 tee fixes hold, and every hole on both sets matches the card.

Page checked: `course_data/library/falcon_ridge/page.html`, GitHub Actions run 41479479995 (committed 19:24Z). Both
solved sets (Black 6,820, Blue 6,329, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page
problems. I looked at every phone hole picture.

## Checks

| check | result |
|---|---|
| Card | page yardage = golfify card on all 36 hole-sets; measured within 6 yds (Black 8: 507 / 513) |
| Mapper layers (`course_data/mapper/falcon_ridge/`) | in. Fairway adds on 6, 8, 9, 13, 15: Black landings now read fairway 59 / 50 / 37 / 53 / 56% (were 0%). Creek water added on 10 (330-345) and 11 (300-325); 11 Black lays up with a 4-wood (water 1%). Tree adds on 1 / 11, the 6 right-edge grow and the 18 tree erase show in the stats |
| Native check cards (`native.json`, Black) | 4 cards: 9, 8, 13, 4. No mapper native here, so priors are 0.25 each side. "Current" plans match the page (9 Driver +2 / +2; 8 +8 / +8.5; 13 -10 / -11; 4 +0 / -2.5). Re-plans are 4-wood near the line; sensible |
| Water filter | ran; no vision water on this course (OSM ponds only) |
| Aims past ±40 | none |

## Holes

| hole | Black | Blue | note |
|---|---|---|---|
| 1-5, 10, 11, 16-18 | OK | OK | tees on OSM boxes; Blue 11 / 18 on the review fix boxes (547 / 548, 375 / 373) |
| 6, 8, 9, 13, 15 | OK (CHECK) | OK (CHECK) | OSM maps no tees on these holes: lidar / texture pads and walkbacks, all within 6 yds of the card. Landings now on mapped fairway |
| 7, 12, 14 | OK (CHECK) | OK (CHECK) | par 3s without an OSM green: target box on a 24-yd estimated green; pictures show it on the green |

## Next fix

None. OSM tees and greens for the back nine would clear the CHECKs (data gap, not a page fault).
