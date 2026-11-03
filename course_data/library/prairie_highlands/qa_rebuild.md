# Prairie Highlands GC (Olathe KS): rebuild QA, wide-aim pass (2026-11-03)

**Verdict: PUBLISH.** Blue 10 now carries the wide-aim CHECK on its calm-day Driver line (60 yds right). With the
Driver row tapped, the oval sits on the upper fairway short of the green, inside the picture. The forecast pick is a
Long iron straight down the first fairway.

Page checked: `course_data/library/prairie_highlands/page.html`, GitHub Actions run 41537321619 (committed 2026-11-03
01:25Z). I ran both solved sets (Black, Blue) through `qa_page.js`, phone and desktop: 18 holes each, 0 page problems,
no console errors. I looked at every phone hole picture, plus the desktop picture of Blue 10 with the Driver row
tapped. Every landing oval was checked against the picture edge.

## Checks

| check | result |
|---|---|
| Card / pars | page yardage = card on all 36 hole-sets; measured within 6 yds |
| Wide-aim CHECK | Blue 10 (calm Driver +60; the CHECK text names the 2-wood row, +76) |
| Ovals | 0 of 72 pick ovals outside; 0 club-row ovals outside. Blue 10 calm Driver is 18 px inside |
| Native check cards | none asked |

## Holes

| hole | Black | Blue | note |
|---|---|---|---|
| 1-9, 12-16, 18 | OK | OK | |
| 10 | OK | **fixed** (CHECK) | calm Driver 60 right over the cart path and rough to the upper fairway (fairway 35%, water 12% for the pond right); forecast Long iron +0 |
| 11 | OK (tee CHECK) | OK | Black tee_axis 6 yds; Blue review tee 367 = card |
| 17 | OK (aim CHECK) | OK | Black Driver -5 ends by the greenside sand (sand 17%), flagged |

## Next fix

None.
