# Bandon Dunes (OR): rebuild QA, GolfPass card (2026-11-03, run 41620964363)

**Verdict: NEEDS FIX (page title only), fix pushed and rebuild requested.** The content is right. The GolfPass card is
matched (`card_review.json`, kind "file"). Both page sets equal the card hole by hole: Tournament 7,212 and Black
6,732, pars 4 3 5 4 4 3 4 4 5 / 4 4 3 5 4 3 4 4 5. The routing is the Bandon Dunes course only, holes 1→18. The package
kept the 18 'bandon dunes' ways and dropped 36 Pacific Dunes / Old Macdonald ways plus 24 neighbouring hole ways.
Green-to-next-tee chains run 45-192 yds. What is wrong is the title: the page says **"Bandon Dunes Golf Resort Caddie"**,
the OSM facility name, on a page that holds one of the resort's courses. It should read "Bandon Dunes Caddie".

Page checked: `course_data/library/bandon_dunes/page.html`, built 2026-11-03T11:12Z. `qa_page.js` ran on phone and
desktop, for the opening set (Tournament) and for Black: 18 holes each, 0 problems. I looked at all 36 hole pictures in
the montages. Status "needs confirm", 4 CHECK holes (1, 8, 10, 11). `regate` blocks nothing.

## Why the title is wrong

`course_page.page_name` keeps the OSM name whenever the kept course's words ({bandon, dunes}) are already in it.
"Bandon Dunes Golf Resort" contains them, so the resort name survived. The fix: when the OSM name says "resort" and the
request's name names the kept course without "resort", use the request's name. The new test in
`test_publish_gate.py` covers this. Sawgrass, Troon North, Pinehurst and Queenstown keep their titles.

## Holes (page as built)

| hole | par page (card Tournament/Black) | Tournament page / card | Black page / card | OSM tee boxes (yds to green) | chain | Tournament pick, lie | Black pick, lie | CHECKs |
|---|---|---|---|---|---|---|---|---|
| 1 | 4 (4/4) | 398 / 398 | 386 / 386 | 404 | - | Driver 8.5R (fairway 75%, sand 5%, OB 1%) | Driver 11.5R (fairway 77%, sand 4%) | Tournament: tee CHECK (lidar_pad; 19 yds from the nearest OSM tee box); Black: tee CHECK (lidar_pad; 16 yds from the nearest OSM tee box) |
| 2 | 3 (3/3) | 220 / 220 | 189 / 189 | 153, 173, 215 | 124 | plays 227 | plays 194 |  |
| 3 | 5 (5/5) | 563 / 563 | 543 / 543 | 419, 464, 488, 517, 540, 561 | 67 | Driver 7.5R (fairway 86%, about 244 yds in) | Driver 3R (fairway 88%, sand 3%) |  |
| 4 | 4 (4/4) | 443 / 443 | 410 / 410 | 301, 335, 357, 401, 436 | 139 | Driver 5R (fairway 51%, sand 2%) | Driver 25R (fairway 40%, sand 4%) |  |
| 5 | 4 (4/4) | 445 / 445 | 428 / 428 | 355, 385, 412, 432 | 68 | Driver 9L (fairway 80%, about 151 yds in) | Driver 10L (fairway 71%, about 140 yds in) |  |
| 6 | 3 (3/3) | 217 / 217 | 161 / 161 | 111, 126, 128, 148, 162, 178, 217 | 86 | plays 216 | plays 160 |  |
| 7 | 4 (4/4) | 411 / 411 | 383 / 383 | 372, 380, 405, 419, 437, 445, 453 | 166 | Driver 13.5L (fairway 96%, about 120 yds in) | Driver 2.5L (fairway 98%, about 96 yds in) |  |
| 8 | 4 (4/4) | 385 / 385 | 359 / 359 | 292, 323, 345, 356, 387 | 48 | Driver 22.5R (fairway 86%, sand 9%) | Driver 49.5R (fairway 58%, sand 16%) | Black: wide_aim: Driver aim +57 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 9 | 5 (5/5) | 585 / 585 | 558 / 558 | 452, 515, 535, 565, 593, 654, 681 | 192 | Driver 34R (fairway 70%, sand 8%) | Driver 38.5R (fairway 67%, sand 10%) |  |
| 10 | 4 (4/4) | 380 / 380 | 362 / 362 | 268, 335 | 63 | Driver 2R (fairway 94%, about 88 yds in) | Driver 12R (fairway 91%, sand 1%) | Tournament: tee CHECK (lidar_pad; 25 yds from the nearest OSM tee box) |
| 11 | 4 (4/4) | 452 / 452 | 384 / 384 | 445, 463 | 45 | Driver 2.5L (fairway 86%, sand 3%) | Driver 3L (fairway 82%, sand 7%) | Black: tee CHECK (walkback; 54 yds from the nearest OSM tee box) |
| 12 | 3 (3/3) | 238 / 238 | 199 / 199 | 96, 136, 168, 199, 238 | 74 | plays 232 | plays 193 |  |
| 13 | 5 (5/5) | 553 / 553 | 553 / 553 | 439, 477, 527, 570, 588, 606 | 110 | Driver 8.5L (fairway 96%, about 250 yds in) | Driver 8.5L (fairway 96%, about 250 yds in) |  |
| 14 | 4 (4/4) | 390 / 390 | 359 / 359 | 261, 292, 305, 326, 359, 374, 381, 393 | 80 | 2-wood 17.5R (fairway 78%, sand 3%) | Driver 28R (fairway 46%, sand 19%) |  |
| 15 | 3 (3/3) | 206 / 206 | 163 / 163 | 110, 133, 153, 176, 208 | 78 | plays 201 | plays 160 |  |
| 16 | 4 (4/4) | 363 / 363 | 363 / 363 | 240, 273, 286, 309, 337, 354 | 47 | Driver 36.5R (fairway 65%, sand 15%) | Driver 36.5R (fairway 65%, sand 15%) |  |
| 17 | 4 (4/4) | 405 / 405 | 389 / 389 | 328, 369, 389, 404 | 46 | 4-wood 8L (fairway 94%, sand 1%) | Driver 24.5L (fairway 48%, sand 10%) |  |
| 18 | 5 (5/5) | 558 / 558 | 543 / 543 | 408, 456, 499, 522, 526, 546 | 52 | Driver 8R (fairway 81%, sand 2%) | Driver 3.5R (fairway 75%, sand 7%) |  |
| total | | 7,212 / 7,212 | 6,732 / 6,732 | | | | | |

The CHECKs:
- **1** (both sets) and **10** (Tournament): the tee was placed on a lidar-flat pad 16-25 yds from the nearest OSM tee
  box. OSM maps only one box on 1 (404) and two on 10 (268, 335), so the card's 398/386 and 380 tees are unmapped.
  The pad placement is plausible, and the CHECK is right.
- **8 Black**: the Driver aim is 49.5 yds right of the tee line (+57 bound). The picture shows the landing on the
  right-hand fairway beyond the corner, all on the course (58% fairway, 16% sand). Tournament aims 22.5 R on the same
  hole. Leave it for a human to confirm.
- **11 Black**: walkback. OSM has only the two back boxes (445, 463), so Black 384 sits 54 yds ahead of them. That is
  right for the card, and the box is unmapped.

Other notes (no CHECK): Black 17 picks Driver 24.5 L (48% fairway, 10% sand) where Tournament picks 4-wood 8 L (94%).
That is aggressive, but the shot stays on the course. No aim goes off the course, and the par-3 targets sit on the
greens.

## Fix (pushed)

- `course_data/library/course_page.py` `page_name`: a resort named after its flagship takes the request's course
  name. A test is in `test_publish_gate.py`.
- `course_page_bandon_dunes.json` rev 5, in `course_batch_qa_bmc.json`. Expect the same holes and yardages, and the
  title "Bandon Dunes Caddie".
