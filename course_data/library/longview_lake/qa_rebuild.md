# Fred Arbanas Golf Course (Longview Lake, Kansas City MO): multi-course rebuild QA (2026-11-03)

**Verdict: NEEDS FIX (card only) — rebuild pushed.** The page is the Championship 18 and only the 18: the 9-hole par-3
course is gone, the routing chains 1→18, and every hole is sensible. The one problem is the card. The OpenGolfAPI card
the build used does not add up (Blue holes sum to 6,906 vs its stated 6,879; White 6,354 vs 6,299), and the page puts
the Blue tee on hole 11 at **230** where a consistent card says **203**. I added the golfify Championship card
(`card_golfify.json`, every set sums to its total) and pushed a rebuild (batch `course_batch_qa_mcb_cards.json`).
Publish after that build is QA'd.

Page checked: `page.html` from GitHub Actions run 41583713847 (built 2026-11-03T05:48Z, split dab692c65 + 269de3c1d).
`qa_page.js` phone + desktop: 18 holes, 0 problems, 0 console errors. Montage of all 18 hole pictures and a routing
plot of the kept hole lines (scratch, not committed).

## The right 18

- Package warning: "2 courses' hole ways in one outline (by hole chains: #1 18, #2 9); kept the largest group … 18
  ways; ignored 9". The kept 18 is the Championship course: pars 4 4 5 3 5 4 3 4 4 / 5 3 4 4 5 4 3 4 4 (par 72) equal
  the golfify Championship card on all 18 holes, and every hole's Blue length is within 1 yd of the card except 11.
- Routing: front nine south-east of the clubhouse, back nine north-west. Green n → tee n+1 is 47-98 yds on 16 links,
  188 yds on 7→8 and 111 yds on 18→1. 9 green and 18 green both come back to the clubhouse; no line crosses another
  course's holes.

## The card issue

golfify (Championship) vs the OpenGolfAPI card on the page:

| set | golfify total (= hole sum) | OpenGolfAPI hole sum / stated | holes that differ |
|---|---|---|---|
| Blue | 6,879 | 6,906 / 6,879 | 11: 203 (golfify) vs 230 |
| White | 6,299 | 6,354 / 6,299 | 4: 147 vs 156; 5: 444 vs 490 |
| Gold, Red | 5,822 / 5,505 | same | none (Red 8: 339, 14: 435 within 5) |

The OpenGolfAPI "Web" set (6,851; 8 = 367, 11 = 195) is a combination of the others and goes away with the golfify card,
so the rebuilt page should solve Blue + White. On the map there is an OSM tee box 230 yds from the 11th green (the page
uses it) and others at 195 / 185: the 230 box is probably an unused tips box. Not verified on site.

## Holes (Blue, current page)

| hole | par | yds (page / golfify) | pick | note |
|---|---|---|---|---|
| 1 | 4 | 387 / 387 | Driver -14 | fairway 42% |
| 2 | 4 | 376 / 376 | Driver +6 (tie) | pond right of the line, short of the landing; fairway 42% |
| 3 | 5 | 518 / 518 | Driver +5 | sand 6% |
| 4 | 3 | 222 / 222 | 221 to the box | |
| 5 | 5 | 511 / 511 | Driver -2 | sand 10%, trees 5% |
| 6 | 4 | 399 / 399 | Driver +25 | fairway 55%, trees 3% |
| 7 | 3 | 182 / 182 | 175 to the box | |
| 8 | 4 | 388 / 388 | 4-wood +2 | pond left of the landing (water 3%), fairway 70% |
| 9 | 4 | 369 / 369 | Driver -28 | follows the dogleg, fairway 59% |
| 10 | 5 | 548 / 548 | Driver +6 | fairway 62% |
| 11 | 3 | **230 / 203** | 229 to the box | **card issue above** |
| 12 | 4 | 403 / 403 | Driver +0 | sand 17%, trees 7% (bunkers right of the landing) |
| 13 | 4 | 457 / 457 | Driver +2 | sand 14% |
| 14 | 5 | 519 / 519 | Driver -18 | trees on the left edge of the oval (4%) |
| 15 | 4 | 400 / 400 | Driver -22 | fairway 57% |
| 16 | 3 | 174 / 174 | 176 to the box | |
| 17 | 4 | 401 / 401 | Driver +14 | fairway 36% |
| 18 | 4 | 422 / 422 | Driver -2 | trees 13% left; plausible |

No aim past ±40, no CHECK hole, nothing off the course. Not verified: hole 11's real back tee (203 vs 230).

## Fix pushed

`course_data/library/longview_lake/card_golfify.json` (golfify Championship, fetched by web_fetch `qa_mcb_cards2`);
`course_page_longview_lake.json` rev 5; batch `course_batch_qa_mcb_cards.json`. Expect: card matched (no "mixed card
versions"), Blue 6,879 with hole 11 at about 203 (a lidar pad or the 195 box), sets Blue + White.
