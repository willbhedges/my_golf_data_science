# Drumm Farm GC: rebuild QA, wide-aim pass (2026-11-03)

**Verdict: PUBLISH.** The agent mapper layers are in, as `course_data/mapper/drumm_farm/review.md` describes. The
wide-aim CHECK fires on Championship 8, and the native card is consistent with the page.

Page checked: `course_data/library/drumm_farm/page.html`, GitHub Actions run 41537321619 (committed 2026-11-03
00:58Z). I ran both solved sets (Tour, Championship) through `qa_page.js`, phone and desktop: 18 holes each, 0 page
problems, no console errors. I looked at every Championship phone hole picture, plus Championship 8 with the Driver
row tapped. Every landing oval was checked against the picture edge on both sets.

## Checks

| check | result |
|---|---|
| Mapper layers | applied 2026-11-02T22:46Z, 14 ops. The package carries agent native zones on 2 (2), 4, 7 (2), 8 (3), 12, 13 (2), 15 and 16, matching the review. The 10 OB erase took: no OB in the 10 landing. Landings now read "long grass 1-5%" on 4, 7, 8, 12, 13 and 15. 0 tees moved |
| Native check cards (Tour) | 11: "current" Driver +26 = page. 2 dropped ("no answer changes the page's Driver +1.5") |
| Wide-aim CHECK | Championship 8: calm Driver 60 left over the corner to the fairway. The forecast pick 4-wood is near the line |
| Ovals | all picks inside. Only the Championship 11 Driver row goes off the picture (-19 to -31 px); the pick there is 2-wood +40 |
| Card / pars | page yardage = card on all 36 hole-sets; measured within 7 yds (Tour 7: 591 / 598) |

## Holes

| hole | Tour | Championship | note |
|---|---|---|---|
| 1-4, 6, 7, 9, 10, 12, 14, 15, 17, 18 | OK | OK | |
| 5 | OK (tee CHECK) | OK | tee_axis 4 yds |
| 8 | OK (tee CHECK) | OK (CHECK) | Tour on a lidar pad 28 yds behind the box (not photo-verified, as reviewed). Championship calm Driver -60, flagged |
| 11 | OK | OK (marginal) | Championship 2-wood 40 right on the bound, fairway 71%; Tour Driver +26 |
| 13 | OK (tee CHECK) | OK | Tour walked back 27 yds |
| 16 | OK | OK (marginal) | Championship 4-wood (calm Driver) to the fairway start, fairway 2%, trees 7%, as before |

## Next fix

None.
