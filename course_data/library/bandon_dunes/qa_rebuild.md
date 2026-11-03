# Bandon Dunes (OR), the Bandon Dunes course: multi-course rebuild QA (2026-11-03)

**Verdict: NEEDS FIX (card only) → card added, rebuild pushed.** The page is the Bandon Dunes course's 18, with no
Pacific Dunes, Old Macdonald or Bandon Trails hole in it. The routing runs 1→18 and every hole is sensible. What was
missing was a card: the page plays "from the map" (no par or card yardage). The GolfPass card is now
`card_review.json`. Without the card the page would be publishable as a no-card page, but a rebuild with the card is
better.

Page checked: `course_data/library/bandon_dunes/page.html`, GitHub Actions run 41583713847 (built 2026-11-03T05:59Z, on
269de3c1d). One set (`osm_back`, 6,994 from the map). I ran it through `qa_page.js`, phone and desktop: 18 holes, 0 page problems. I
looked at every hole picture.

## Bandon Dunes, not the sister courses

- Package warning: "3 courses' hole ways in one outline (by hole way names: dunes pacific 18, bandon dunes 18, Old
  Macdonald 18); kept 'bandon dunes'"; 24 more ways outside the boundary ignored (Trails, Preserve).
- The kept lines are the OSM "Bandon Dunes 1-18" ways: 395, 207, 561, 437, 434, 219, 383, 388, 594 / 354, 466, 238,
  542, 324, 207, 356, 406, 549.
- Chain green n → tee n+1: 32-169 yds on every link. Hole 1 starts by the lodge, and 16 runs along the bluff.

## Card (added)

The card is GolfPass's Bandon Dunes card (`research/web/mc_cards/02.html`, web_fetch run 41603917727): par
4-3-5-4-4-3-4-4-5 / 4-4-3-5-4-3-4-4-5 = 72. Those are exactly the page's pars, which came from OSM. The sets are
Tournament 7,212, Black 6,732 (74.1 / 143), Green 6,221, Gold 5,716, Orange 5,040 and Royal Blue 3,986 (hole-table
sums; GolfPass's rating table says Orange 5,072 and Royal Blue 3,945). The request asks for "Black", so Black is
chosen by name.

## Holes (page as built, back tees from the map, vs the card's Tournament set)

| hole | par | page yds | Tournament | pick | note |
|---|---|---|---|---|---|
| 1 | 4 | 404 | 398 | Driver 7.5 R | fairway 77% |
| 2 | 3 | 215 | 220 | plays 222 | |
| 3 | 5 | 561 | 563 | Driver 5.5 R | fairway 87% |
| 4 | 4 | 436 | 443 | Driver 8 R | fairway 47% |
| 5 | 4 | 432 | 445 | Driver 10 L | fairway 74% |
| 6 | 3 | 217 | 217 | plays 216 | |
| 7 | 4 | 380 | 411 | Driver | fairway 98% |
| 8 | 4 | 387 | 385 | Driver 22.5 R | fairway 85% |
| 9 | 5 | 593 | 585 | Driver 32 R | fairway 69% |
| 10 | 4 | 335 | 380 | Driver 25.5 R | fairway 77%; tee 20 yds up from the line start |
| 11 | 4 | 463 | 452 | Driver | fairway 86% |
| 12 | 3 | 238 | 238 | plays 232 | |
| 13 | 5 | 527 | 553 | Driver 3 L | fairway 94% |
| 14 | 4 | 326 | 390 | Driver 49.5 R, **wide-aim CHECK** | dogleg corner, fairway 63% |
| 15 | 3 | 176 | 206 | plays 172 | tee 29 yds up from the line start |
| 16 | 4 | 354 | 363 | Driver 40 R | bluff hole, fairway 64% (at the 40-yd CHECK limit, not flagged) |
| 17 | 4 | 404 | 405 | 4-wood 8.5 L | fairway 93% |
| 18 | 5 | 546 | 558 | Driver 5 R | fairway 76% |

The aims on 14 (CHECKed) and 16 are into the dogleg and look right on the photo. Nothing is off the course.

## Check on the rebuild

The set should be Black 6,732 with card pars. Tee CHECKs are likely where the OSM has no Black box. The title should
name the course (nit: it is "Bandon Dunes Golf Resort Caddie").
