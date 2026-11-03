# Sand Hollow Championship (UT): multi-course rebuild QA (2026-11-03)

**Verdict: NEEDS FIX → card added, rebuild pushed.** The page is the Championship 18. No Links-nine hole is in it, the
routing runs 1→18, and the pars match the card. **Hole 4** is wrong: it plays 345 yds from a forward OSM tee 122 yds
ahead of the hole line's start, and the card has 463 from the Black tees. The page has no card. The GolfPass
Championship card is now `card_review.json`, which gives the tee stage card yardages to walk back to.

Page checked: `course_data/library/sand_hollow/page.html`, GitHub Actions run 41583713847 (built 2026-11-03T05:59Z, on
269de3c1d). One set (`osm_back`, 7,135 from the map). I ran it through `qa_page.js`, phone and desktop: 18 holes, 0
page problems. I looked at every hole picture.

## Championship, not Links

- Package warning: "by hole chains (green -> next tee): champion 18, #2 9; kept the largest group (no name or near
  point decides: CHECK the course)". The kept 18 are the OSM "Champion" ways; the 9 unnamed ways (the Links nine) are
  dropped.
- Chain green n → tee n+1: 48-214 yds on every link.

## Card (added)

The card is GolfPass's "The Championship Course" (`research/web/mc_cards/05.html`, web_fetch run 41603917727): par
4-5-3-4-4-4-5-3-4 / 5-3-4-4-4-3-4-5-4 = 72. That equals the page's (OSM) pars on all 18, including 14 as a 525-yd par
4. The sets are Black 7,315 (73.7 / 131), Blue 6,893, White 6,462, Combo 5,934 and Red 5,306. GolfPass's hole table
labels those rows Red / Yellow / Green / Combo / Blue, but its rating table names the same totals Black / Blue / White
/ Red. I used the rating-table names; this is not verified against the club's own card.

## Holes (page as built vs card Black)

| hole | par | page yds | card Black | pick | note |
|---|---|---|---|---|---|
| 1 | 4 | 439 | 447 | Driver 13 R | fairway 85% |
| 2 | 5 | 571 | 577 | Driver 14.5 R | fairway 83% |
| 3 | 3 | 205 | 208 | plays 203 | |
| 4 | 4 | **345** | **463** | Driver 22.5 L | **wrong tee**: the OSM line starts 122 yds behind the chosen box (line 472); no OSM box at the back |
| 5 | 4 | 350 | 355 | Driver | fairway 77% |
| 6 | 4 | 492 | 493 | Driver 4.5 L | fairway 85% |
| 7 | 5 | 573 | 577 | Driver 10 R | fairway 79% |
| 8 | 3 | 156 | 162 | plays 160 | |
| 9 | 4 | 434 | 433 | Driver 7.5 L | fairway 75% |
| 10 | 5 | 562 | 565 | Driver | fairway 69% |
| 11 | 3 | 187 | 190 | plays 186 | |
| 12 | 4 | 441 | 443 | Driver | fairway 57% |
| 13 | 4 | 318 | 320 | Driver 5 L | fairway 39%, 40 yds in |
| 14 | 4 | 527 | 525 | Driver | fairway 74% |
| 15 | 3 | 228 | 230 | plays 217 | the signature par 3 |
| 16 | 4 | 361 | 369 | Driver 10 R (tie 4-wood) | fairway 54% |
| 17 | 5 | 523 | 523 | Driver | fairway 74% |
| 18 | 4 | 423 | 435 | Driver 7 R | fairway 59% |

Apart from 4, every hole is within 12 yds of the card. No aim is past ±23 and nothing is off the course.

## Check on the rebuild

Hole 4 must be ~463 from a tee near the hole line's start (walkback or lidar pad, with a tee CHECK). The set should be
Black 7,315. The title should name the Championship course (nit: it is "Sand Hollow Resort Caddie").
