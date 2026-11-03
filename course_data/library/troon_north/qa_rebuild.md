# Troon North Monument (AZ): multi-course rebuild QA (2026-11-03)

**Verdict: PUBLISH.** The page is Monument's 18, and only Monument's. The card is Monument's, not Pinnacle's, and every
hole is sensible.

Page checked: `course_data/library/troon_north/page.html`, GitHub Actions run 41580200431 (built 2026-11-03T06:15Z, on
dab692c65 + 269de3c1d). One solved set, Black (7,039, par 72). I ran it through `qa_page.js`, phone and desktop: 18
holes, 0 page problems. I looked at every hole picture (montage in the QA scratch, not committed).

## Monument, not Pinnacle

- Package warning: "2 courses' hole ways in one outline (by hole way names: Pinnacle Course 18, Monument Course 18);
  kept 'Monument Course' (named in the request), 18 ways; ignored 18". The OSM course tag is `golf:par` "71 + 72".
- The 18 kept hole lines measure 443, 173, 541, 411, 465, 278, 211, 403, 526 / 377, 505, 417, 219, 577, 303, 234, 486,
  363. Each is a different OSM way, one per ref, and within 25 yds of the Monument card on every hole except 6 (line
  278, card 306; the tee is on the OSM box and measures 304).
- Chain green n → tee n+1: 68-158 yds on 15 links, and 249 (9→10) and 238 (11→12). These are cart rides through the
  desert, not jumps to the other course.
- Landmarks: the 556-yd par-5 3rd (the boulder hole), the drivable par-4 15th (299), the lake left of 18.

## Card

The card is opengolfapi c9dcf35f (Black 7,039, 73.3 / 148, par 4-3-5-4-4-4-3-4-5 / 4-5-4-3-5-4-3-4-4 = 72). That is
**Monument's** card: it matches GolfPass's Monument scorecard hole for hole (all 6 sets;
`course_data/research/web/mc_cards/08.html`, web_fetch run 41603917727). Pinnacle is par 71. No card_review.json is
needed. Measured vs card: within 5 yds on 17 holes, and hole 16 is 240 vs 244.

## Holes

| hole | par | yds | pick | note |
|---|---|---|---|---|
| 1 | 4 | 444 | 4-wood 5 L | fairway 84%, OB 5% |
| 2 | 3 | 172 | plays 190 | |
| 3 | 5 | 556 | 4-wood 18 R (tie 2-wood) | fairway 69%, sand 8%. Tee CHECK: 7 yds from the OSM box |
| 4 | 4 | 420 | 4-wood 12 R | fairway 94% |
| 5 | 4 | 464 | Driver | fairway 84% |
| 6 | 4 | 306 | Long iron | lays up, fairway 94% |
| 7 | 3 | 205 | plays 221 | |
| 8 | 4 | 408 | 4-wood 3 R | fairway 80%, OB (desert) 20% |
| 9 | 5 | 530 | 4-wood | fairway 74%, OB 25% |
| 10 | 4 | 396 | 4-wood 6 L | fairway 75% |
| 11 | 5 | 512 | 4-wood 9.5 L | fairway 78% |
| 12 | 4 | 426 | 4-wood 16 L | fairway 85% |
| 13 | 3 | 222 | plays 227 | |
| 14 | 5 | 570 | 4-wood 2.5 L | fairway 79%; pond by the tee is not in play |
| 15 | 4 | 299 | 4-wood 14 L | lands short of the green complex, 34 yds in; fairway 44% |
| 16 | 3 | 244 | plays 229 | |
| 17 | 4 | 495 | 4-wood 11.5 R (tie 2-wood) | fairway 82% |
| 18 | 4 | 370 | 4-wood 8 L | fairway 66%, lake left |

No aim is past ±20, so there are no wide-aim CHECKs. No tee line crosses houses or leaves the course. "OB" here is the
desert. The only CHECK is hole 3's tee.

## Nits (not blocking)

- The page title is "Troon North Golf Club Caddie". It should say "Monument", because the facility has two courses.
- The MANAGER_TODO note not to publish the run-41567617061 page is now superseded by this build.
