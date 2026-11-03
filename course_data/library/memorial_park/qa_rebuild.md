# Memorial Park (Houston TX): card-order rebuild QA (2026-11-03)

**Verdict: NEEDS FIX (card only) → card added, rebuild pushed.** The card-order fix did its job. The OSM holes 1-18
walk as a round (longest green → next tee 198 yds), so they kept their order, and the golfify card was rejected
("par or length off on 6 holes"). That was right: golfify's is the **pre-2019 layout** (par 4 on 3 and 9, par 5 on 13).
The routing and every hole on the page are sound. The page has no card, though. The **OpenGolfAPI card** fetched in the
same build (`raw/scorecard_web.json`) is the current Doak layout, and it fits the OSM order. It is now
`card_review.json`.

Page checked: `course_data/library/memorial_park/page.html`, GitHub Actions run 41607398168 (built 2026-11-03T09:42Z,
on the card-order fix). One set (`osm_back`, 7,184 from the map). `qa_page.js` phone + desktop: 18 holes, 0 problems. I
looked at all 18 hole pictures (montage in the QA scratch folder). The gate passes (`regate` blocks nothing).

## The OpenGolfAPI card fits the OSM order

- Par 5 3 5 4 4 4 3 5 3 / 4 3 4 4 5 3 5 4 4 = 72. These are the OSM pars on **all 18**.
- The Blue hole yardages are 0-34 yds longer than each OSM back-box line, in OSM order (median ~16; the OSM back boxes
  sit slightly forward). No hole is out of place.
- I ran `sanity.card_order` locally with this card on the page's hole lines: action "none", no mapping, no bad
  holes. The build will keep the OSM order and use the card.
- The API's stated totals do not equal its hole rows: Blue 7,292 vs 7,464 summed, White 6,553/6,584, Gold 5,905/5,930,
  Red 4,826/4,851. `card_review.json` keeps the hole rows (totals = sums). Green is left out: stated 5,399 vs 5,595
  summed, and it copies Gold on 8 holes. The request's "Black" is not on the card, so the build will substitute Blue
  (the longest).

## Holes (page as built, from the map; Blue from the new card)

| hole | par (card) | page yds (map) | Blue (OpenGolfAPI) | chain | pick | lie | note |
|---|---|---|---|---|---|---|---|
| 1 | 5 (5) | 499 | 522 | - | Driver 9 L | fairway 41%, trees 2% |  |
| 2 | 3 (3) | 151 | 167 | 76 | plays 143 |  |  |
| 3 | 5 (5) | 580 | 587 | 52 | Driver 1.5 L | fairway 43%, trees 12% |  |
| 4 | 4 (4) | 483 | 490 | 83 | Driver 9 R | fairway 54%, trees 4% |  |
| 5 | 4 (4) | 440 | 440 | 102 | Driver 1.5 R | fairway 49%, trees 12% |  |
| 6 | 4 (4) | 441 | 443 | 96 | Driver 3.5 R | fairway 53%, trees 10% |  |
| 7 | 3 (3) | 206 | 216 | 54 | plays 212 |  |  |
| 8 | 5 (5) | 591 | 625 | 128 | Driver 11.5 R | fairway 35%, trees 1% |  |
| 9 | 3 (3) | 180 | 202 | 52 | plays 188 |  |  |
| 10 | 4 (4) | 433 | 456 | 198 | Driver 9 R | fairway 45%, trees 5% |  |
| 11 | 3 (3) | 217 | 237 | 49 | plays 209 |  |  |
| 12 | 4 (4) | 486 | 496 | 81 | Driver 5 R | fairway 48%, trees 6% |  |
| 13 | 4 (4) | 390 | 406 | 75 | Driver 10.5 R | fairway 49%, trees 10% |  |
| 14 | 5 (5) | 517 | 529 | 54 | Driver 7 L | fairway 44%, trees 19% |  |
| 15 | 3 (3) | 137 | 155 | 81 | plays 142 |  |  |
| 16 | 5 (5) | 545 | 576 | 99 | Driver 11 R | fairway 40%, water 9% |  |
| 17 | 4 (4) | 403 | 414 | 147 | 4-wood 10.5 L | fairway 60%, water 4% |  |
| 18 | 4 (4) | 485 | 503 | 65 | Driver 2.5 L | fairway 65%, trees 6% |  |

Every hole on the page also carries the no-card CHECK (yardage and par from the map). No aim is past 11.5 yds and
nothing is off the course. Water on 16 and 17 is on the right side in the photos, and the picks avoid it.

## Fix (pushed)

`course_data/library/memorial_park/card_review.json` (OpenGolfAPI, ODbL attribution kept);
`course_page_memorial_park.json` rev 3, in `course_batch_qa_cards.json`. Expect the card to be matched (source
file), Blue 7,464 + White solved, no renumber warning, and tee walkbacks or CHECKs where Blue is 20-34 yds behind the
OSM box (8, 9, 11, 16, 18, 10). Not verified: whether Blue's 7,464 or the stated 7,292 is the current tips length.
