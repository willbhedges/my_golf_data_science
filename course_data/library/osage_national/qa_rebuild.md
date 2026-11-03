# Osage National: rebuild QA, wide-aim pass (2026-11-03)

**Verdict: PUBLISH** (the renovation caveat from earlier passes still stands). The hole-15 native card is gone:
`native.json` drops it with "planner's no-answer plan Driver +60 is not the page's Long iron -1.0". The two cards left,
5 and 11, match the page's picks exactly.

Page checked: `course_data/library/osage_national/page.html`, GitHub Actions run 41537321619 (committed 2026-11-03
01:42Z). I ran both solved sets (Palmer, Tournament) through `qa_page.js`, phone and desktop: 18 holes each, 0 page
problems, no console errors. I looked at every Palmer phone hole picture, and checked every landing oval against the
picture edge on both sets.

## Checks

| check | result |
|---|---|
| Card / pars | page yardage = card on all 36 hole-sets; measured within 7 yds (Palmer 1: 370 / 377) |
| Native check cards (Palmer) | 5 (Driver -18) and 11 (Driver -7). "current" equals the page pick. 15 dropped, which is consistent with the page (Long iron -1) |
| Wide-aim CHECK | none needed: no pick or club row past ±40 on either set |
| Ovals | all picks inside. Tapping the Driver / 2-wood row on 15 draws an oval 80-90 px off the picture: that is the planner's +60 line, which the page never picks. Tournament 6 Driver row is 3-7 px off |

## Holes

| hole | Palmer | Tournament | note |
|---|---|---|---|
| 1, 4, 5, 8-14, 16-18 | OK | OK | |
| 2 | OK (tee CHECK) | OK | Palmer walked back 22 yds, 456 / 455 |
| 3 | OK (tee CHECK) | OK | Palmer lidar pad behind the pond, 376 / 370 |
| 6, 7 | OK (tee CHECK) | OK | Palmer lidar pads, yardage = card ±3 |
| 15 | **fixed** (card gone) | OK | Long iron to the fairway, 83-88% |

## Next fix

None blocking. As before: a post-renovation card and newer imagery.
