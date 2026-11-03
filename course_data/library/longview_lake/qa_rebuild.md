# Fred Arbanas Golf Course (Longview Lake, Kansas City MO): card rebuild QA (2026-11-03)

**Verdict: PUBLISH.** The rebuild used the golfify Championship card (`card_golfify.json`). **Hole 11 is now 203**
from the Blue tee (plays 202), not 230. Blue 6,879 and White 6,299 are solved, page yardage equals the card on all 18
for both sets, the pars equal the card, and the routing chains 1→18.

Page checked: `course_data/library/longview_lake/page.html`, GitHub Actions run 41605206913 (built 2026-11-03T09:11Z).
`qa_page.js` phone + desktop, Blue: 18 holes, 0 problems. The White run had the same result (page = card 6,299, holes
4/5 = 147/444). I looked at all 18 hole pictures (montage in the QA scratch folder).

## Checks

- Card source: `card_golfify.json`. There is no "mixed card versions" flag. "Black" is not on the card, so the build
  substituted Blue, which is expected.
- Hole 11: Blue box on the hole line (tee_axis), 203 measured (the OSM line from the 230 back box is 226). Measured
  and card agree. The old OpenGolfAPI 230 does not appear on the golfify card.
- Chains run 48-99 yds, except 7→8 at 189. Split warning "#1 18, #2 9; kept the largest group" (the par-3 nine is
  dropped).
- The one CHECK is hole 5: the tee is 3 yds off an OSM box (trivial). White 6 (+37) and 9 (-34) aim wide into the
  doglegs, inside 40 and not flagged. Both look right on the photo.

## Holes (Blue; page yds = card on all 18)

| hole | par | page yds | measured | chain | pick | lie | note |
|---|---|---|---|---|---|---|---|
| 1 | 4 | 387 | 387 | - | Driver 13.5 L | fairway 42% |  |
| 2 | 4 | 376 | 376 | 53 | Driver 6.5 R | fairway 42%, trees 2% |  |
| 3 | 5 | 518 | 518 | 69 | Driver 5 R | fairway 45%, sand 6%, trees 1% |  |
| 4 | 3 | 222 | 222 | 53 | plays 221 |  |  |
| 5 | 5 | 511 | 511 | 65 | Driver 2 L | fairway 46%, sand 10%, trees 5% |  |
| 6 | 4 | 399 | 400 | 99 | Driver 25 R | fairway 55%, trees 3% |  |
| 7 | 3 | 182 | 182 | 72 | plays 175 |  |  |
| 8 | 4 | 388 | 387 | 189 | 4-wood 4 R | fairway 70%, water 3% |  |
| 9 | 4 | 369 | 369 | 92 | Driver 28.5 L | fairway 59% |  |
| 10 | 5 | 548 | 549 | 87 | Driver 6 R | fairway 62%, sand 3%, trees 3% |  |
| 11 | 3 | 203 | 203 | 48 | plays 202 |  |  |
| 12 | 4 | 403 | 404 | 54 | Driver | fairway 61%, sand 17%, trees 7% |  |
| 13 | 4 | 457 | 457 | 56 | Driver 2.5 R | fairway 53%, sand 14%, trees 4% |  |
| 14 | 5 | 519 | 519 | 49 | Driver 18.5 L | fairway 50%, trees 4%, water 4% |  |
| 15 | 4 | 400 | 400 | 77 | Driver 21.5 L | fairway 57%, trees 7% |  |
| 16 | 3 | 174 | 174 | 67 | plays 176 |  |  |
| 17 | 4 | 401 | 402 | 77 | Driver 14 R | fairway 36%, trees 4% |  |
| 18 | 4 | 422 | 422 | 72 | Driver 2 L | fairway 43%, trees 13% |  |

Nothing is off the course. The aims on 6 (+25), 9 (-28.5), 14 (-18.5) and 15 (-21.5) follow the dogleg on the photo.
