# Memorial Park (Houston TX): rebuild QA, OpenGolfAPI card (2026-11-03, run 41620964363)

**Verdict: PUBLISH (after the normal confirm of the 5 CHECK holes).** The card-order fix kept the OSM order. The holes
walk as a round, with chains of 48-175 yds. The OpenGolfAPI current-layout card from `card_review.json` is matched
(kind "file"): pars 5 3 5 4 4 4 3 5 3 / 4 3 4 4 5 3 5 4 4 = 72, the same as OSM on all 18 holes. Both page sets equal
the card's hole rows hole by hole: Blue 7,464 and White 6,584. The request's "Black" is not on the card, so the build
used Blue (allow_substitute warning), as expected.

Page checked: `course_data/library/memorial_park/page.html`, built 2026-11-03T11:06Z. `qa_page.js` ran on phone and
desktop, for Blue (the opening set) and White: 18 holes each, 0 problems. I looked at all 36 hole pictures. Status
"needs confirm", CHECKs on 8, 13, 14, 16 and 17. `regate` blocks nothing.

## Blue 7,464 (hole rows) vs 7,292 (stated total)

The page uses the hole rows (7,464), and that is the better number for the page:
- Each Blue row is at or just behind the hole's OSM back box: 0-34 yds behind the back-box line (the earlier pass),
  and within ~35 yds of a mapped box in the table below. So each row fits the ground. The OSM back boxes alone sum to
  about 7,184, and a 7,292 tips set would have to be about 170 yds shorter than the rows, with no hole showing where.
- 7,292 / 74.2 / 128 is the figure the listings repeat (GolfNow, GolfPass, OpenGolfAPI's tee table). The same sites
  also list 7,164 / 73.0 / 122 for "Blue", and golfify lists 7,305 / 75.0 / 130, so the stated totals are not
  consistent either. The PGA Tour (Houston Open) card is 7,435 at par 70.

Not verified: I could not reach the club's own card. golfpass.com and thegolfnewsnet.com are outside this session's
network, and the club site was "no parsable scorecard" in the build. The only thing the stated-vs-sum question changes
is the subtitle total ("Blue 7,464"). The holes are the rows either way.

## Holes (page as built)

| hole | par page (card Blue/White) | Blue page / card | White page / card | OSM tee boxes (yds to green) | chain | Blue pick, lie | White pick, lie | CHECKs |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 (5/5) | 522 / 522 | 512 / 512 | 426, 470, 499, 531 | - | Driver 8.5L (fairway 41%, trees 5%) | Driver 9.5L (fairway 39%, trees 3%) |  |
| 2 | 3 (3/3) | 167 / 167 | 147 / 147 | 127, 151, 169 | 71 | plays 159 | plays 140 |  |
| 3 | 5 (5/5) | 587 / 587 | 566 / 566 | 357, 410, 453, 580 | 57 | Driver (fairway 45%, trees 10%) | Driver 2L (fairway 38%, sand 3%, trees 12%) |  |
| 4 | 4 (4/4) | 490 / 490 | 457 / 457 | 356, 398, 458, 483, 528 | 85 | Driver 10.5R (fairway 54%, trees 4%) | Driver 4R (fairway 53%, trees 8%) |  |
| 5 | 4 (4/4) | 440 / 440 | 376 / 376 | 353, 388, 440, 465, 485 | 102 | Driver 1.5R (fairway 49%, trees 12%) | Driver 17L (fairway 51%, trees 7%) |  |
| 6 | 4 (4/4) | 443 / 443 | 380 / 380 | 340, 382, 441 | 97 | Driver 3.5R (fairway 53%, trees 10%) | Driver 7.5L (fairway 52%, trees 4%) |  |
| 7 | 3 (3/3) | 216 / 216 | 182 / 182 | 130, 141, 165, 206 | 48 | plays 223 | plays 188 |  |
| 8 | 5 (5/5) | 625 / 625 | 554 / 554 | 489, 533, 551, 591 | 134 | Driver 6R (fairway 33%, trees 7%) | Driver 15.5R (fairway 41%, trees 16%) | Blue: tee CHECK (tee_axis; 3 yds from the nearest OSM tee box) |
| 9 | 3 (3/3) | 202 / 202 | 143 / 143 | 138, 180 | 54 | plays 210 | plays 152 |  |
| 10 | 4 (4/4) | 456 / 456 | 437 / 437 | 345, 377, 433 | 175 | Driver 5.5R (fairway 47%, trees 2%) | Driver 9R (fairway 43%, trees 4%) |  |
| 11 | 3 (3/3) | 237 / 237 | 223 / 223 | 165, 217 | 48 | plays 228 | plays 214 |  |
| 12 | 4 (4/4) | 496 / 496 | 422 / 422 | 368, 396, 419, 486 | 88 | Driver 1.5R (fairway 48%, trees 7%) | Driver 17R (fairway 42%, trees 8%) |  |
| 13 | 4 (4/4) | 406 / 406 | 298 / 298 | 390 | 88 | Driver 7R (fairway 50%, trees 12%) | Driver 8R (fairway 74%, trees 4%) | White: tee CHECK (walkback; 78 yds from the nearest OSM tee box) |
| 14 | 5 (5/5) | 529 / 529 | 480 / 480 | 517 | 61 | Driver 3L (fairway 44%, trees 18%) | Driver 14.5L (fairway 48%, trees 1%) | White: tee CHECK (walkback; 21 yds from the nearest OSM tee box) |
| 15 | 3 (3/3) | 155 / 155 | 130 / 130 | 121, 137, 153 | 76 | plays 160 | plays 135 |  |
| 16 | 5 (5/5) | 576 / 576 | 501 / 501 | 503, 545 | 70 | Driver 7.5L (fairway 59%, trees 1%, water 4%) | Driver 30.5R (fairway 52%, trees 7%, water 4%) | Blue: tee CHECK (texture_pad; 27 yds from the nearest OSM tee box) |
| 17 | 4 (4/4) | 414 / 414 | 366 / 366 | 289, 328, 370, 403 | 154 | 4-wood 8L (fairway 65%, water 4%) | Driver 3R (fairway 25%, water 5%) | White: tee CHECK (tee_axis; 6 yds from the nearest OSM tee box); aim: Driver +3 lands 295 yds out in rough (8 yds from fairway) |
| 18 | 4 (4/4) | 503 / 503 | 410 / 410 | 401, 485 | 67 | Driver 3L (fairway 61%, trees 3%) | Driver 2.5R (fairway 51%, trees 8%) |  |
| total | | 7,464 / 7,464 | 6,584 / 6,584 | | | | | |

The CHECKs:
- **8 Blue** (625; OSM back box 591) and **16 Blue** (576; OSM 545): the Blue tees are behind the last mapped box, so
  the marker was placed by tee axis or texture 3-27 yds off a box. The pictures show tee ground there.
- **13 White** (298; the one OSM box is at 390) and **14 White** (480; the one OSM box at 517): only the back box is
  mapped, so the marker was walked 78 and 21 yds up the hole line. That is right for the card.
- **17 White**: tee 6 yds off the box, and Driver +3 lands 295 out in rough, 8 yds from the fairway (fairway 25%,
  water right 5%). The CHECK is right. 4-wood is the tie on Blue.

No aim is past 30.5 yds (16 White, to the right of the lake on the left). Nothing is off the course. Water on 16 and 17
is avoided in the pictures, and the par-3 targets sit on the greens.

## Fix

None needed. No rebuild.
