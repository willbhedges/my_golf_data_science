# A. L. Gustin GC: rebuild QA, wide-aim pass (2026-11-03)

**Verdict: PUBLISH.** The wide-aim CHECK now reaches the library page. Gold 6 (4-wood 59.5 yds left) carries a CHECK,
and its landing oval sits fully inside the wider hole picture, on the fairway past the corner. Card, tees and mapper
layers are unchanged from the last pass.

Page checked: `course_data/library/gustin/page.html`, GitHub Actions run 41537321619 (committed 2026-11-03 01:13Z).
I ran both solved sets (Black, Gold) through `qa_page.js`, phone and desktop: 18 holes each, 0 page problems, no
console errors. I looked at every phone hole picture. I also checked every landing oval against the picture edge, for
the forecast pick, the calm pick and every club row (see "Ovals").

## Checks

| check | result |
|---|---|
| Card / pars | page yardage = card on all 36 hole-sets. Measured within 5 yds except Gold 15 (340 / 350, review box, as before) and Black 11 (416 / 424, capped lidar pad) |
| Wide-aim CHECK | present on Black 6, Black 16, Gold 3, Gold 6, Gold 7 and Gold 16. The page text reads "Auto-map CHECK: wide_aim ..." |
| Ovals | the forecast and calm picks are inside the picture on all 36 hole-sets. Only taps on non-picked rows go outside: Black 6 2-wood (-6 px), Black 15 Driver (-13 px), Gold 3 Driver (-16 px), Gold 6 calm Driver (-2 px) |
| Native check cards (Black) | 9, 1, 3, 12: each "current" plan equals the page pick (Driver +3 / +4 / +19 / +6) |
| Mapper layers | in (tree adds/erases); landings on fairway, tree readings as in the last pass |

## Holes

| hole | Black | Gold | note |
|---|---|---|---|
| 1, 2, 5, 8-10, 12, 13, 15, 17, 18 | OK | OK | |
| 3 | OK | OK (CHECK) | Gold 2-wood 52 right over the right-hand trees at the dogleg; oval inside the picture |
| 4, 11 | OK (tee CHECK) | OK | tee_axis 5 yds / capped lidar pad 11 yds |
| 6 | OK (CHECK) | **fixed** (CHECK) | Gold 4-wood 59.5 left (calm) over the tree corner onto the fairway, trees 18%; oval fully in the picture. Black 4-wood 40 left; its CHECK is for the 2-wood row (-52) |
| 7 | OK (tee CHECK) | OK (CHECK) | Gold 2-wood 39.5 left into the corner; the CHECK is for the 2-wood row at -62 |
| 14 | OK (tee CHECK) | OK (tee CHECK) | lidar pads 150-183 yds from any mapped box; yardage = card |
| 16 | OK (CHECK) | OK (CHECK) | Black 4-wood / calm 2-wood 58 right, flagged. Gold plays 4-wood +12; its CHECK is for the 2-wood row (+74) |

## Notes (not blocking)

- The CHECK text can quote a different number than the page. Gold 6: the CHECK says "4-wood aim -67", the page says
  59.5 left. The auto-QA and the page seem to measure the aim differently.
- The wide-aim rule fires on any club row, not only the pick (Gold 16, Gold 7, Black 6). That is defensible, since a
  tapped row prints its aim. But it makes the CHECK list longer than the "pick" wording suggests.

## Next fix

None.
