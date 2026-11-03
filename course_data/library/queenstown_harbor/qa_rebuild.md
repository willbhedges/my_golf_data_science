# Queenstown Harbor River Course (MD): first-build QA (2026-11-03)

**Verdict: PUBLISH (as a no-card page).** It is River's 18, and only River's: no holes are mixed in from Lakes. The
routing chains 1→18, the tee shots go up their own corridors, and pars (sum 72) and map yardages (6,936) are
plausible. The page labels are golfer-friendly ("Back tees (from the map)"). Two things for the coordinator, neither
blocking: the par of hole 7 (below), and some footer and CHECK wording that only makes sense with a card.

Page checked: `course_data/library/queenstown_harbor/page.html`, GitHub Actions run 41580200431 (built
2026-11-03T05:14Z), with the multi-course split dab692c65 and the Geofabrik OSM extract. One solved set (`osm_back`,
shown as "Back tee"). I ran it through `qa_page.js`, phone and desktop: 18 holes, 0 page problems, no console errors. I
looked at every hole picture, and drew the package zones (OSM fairway, sand, water, vision trees, OB) on the page's
hole images (scratch `queenstown_harbor_zones.png`).

## River, not Lakes

- Package warning: "2 courses' hole ways in one outline (by hole chains: river 18, #2 18); kept 'river'". The 18 kept
  ways are exactly the `QH_RIVER` set in `platform/test_sanity.py`. They include the name-only ways "#3 - par 4", "#6",
  "#7", "#8" and "River # 9 - par 4". The other 18 (refs 1-18, east and south of the clubhouse) are all left out.
- Chain green n → tee n+1: 38-212 yds on 16 links. 5→6 is 355 yds (from the far north end of 5 back south to the
  clubhouse side), and 18→1 is 173.
- Each hole's picture shows its own fairway, green and water. No tee line runs through woods or off the course. Holes
  4 and 15 carry water off the tee, and 9 carries the marsh, as the photo shows.

## Pars and yardages (no card: golfify, allsquare, bluegolf, golfpass, opengolfapi all missed)

Front 3,414 (par 36), back 3,522 (par 36), total 6,936 (par 72), from the OSM tee nearest each line start. Pars come
from OSM on 1, 2 and 10-18, and from the length rule on 3-9.

| hole | par | yds | hole | par | yds |
|---|---|---|---|---|---|
| 1 | 4 | 358 | 10 | 4 | 456 |
| 2 | 3 | 157 | 11 | 5 | 564 |
| 3 | 4 | 422 | 12 | 4 | 356 |
| 4 | 4 | 374 | 13 | 3 | 155 |
| 5 | 5 | 559 | 14 | 4 | 413 |
| 6 | 4 | 348 | 15 | 4 | 433 |
| 7 | **5** | 542 | 16 | 3 | 199 |
| 8 | 3 | 240 | 17 | 4 | 367 |
| 9 | 4 | 414 | 18 | 5 | 579 |

**Hole 7:** OSM names the way "#7 - par 4", but its line measures 542. The photo shows two fairway sections split by a
creek and tree band, which reads as a par 5. The length-rule par 5 also makes the total 72. The names on 3, 6, 8 and
9 agree with the page. Not verified against a card.

## Labels

Good: "Par 4 · 358 yds · from the Back tee", "Back tees (from the map)", "157 to the middle", and the header "automatic
page: NEEDS CONFIRM".

Nits (not blocking):
- Every hole's note ends with "Auto-map CHECK: yardage: no card yardage for the back tees (from the map); par: no card
  par". This is 18 identical CHECKs that are really one course-level fact.
- The footer says "card from no card". It also says "Other tee sets move the tee back or up the line by the
  scorecard difference from Back tees", which does not apply when there is no card and only one set.

## Holes

| hole | pick | note |
|---|---|---|
| 1 | 4-wood +4.5 | lake right; fairway 62%, water 2% |
| 2, 13, 16 | par 3 | target on the green; 157 / 155 / 199 |
| 3 | 2-wood -9 (tie) | lands at the dogleg corner. The long side of the oval reaches the tree band behind the corner (page trees 4%; the photo looks heavier). Marginal |
| 4 | 4-wood +7 | over the pond to the fairway, water 3% |
| 5 | Driver -5.5 | fairway 34% |
| 6 | Driver -7 | tee in a wooded chute, landing on the fairway short of the green-side water |
| 7 | 4-wood -5 (aim CHECK) | lands at the path crossing, 6 yds off the fairway; fairway 18% |
| 8 | par 3, 240 | long, but plausible from the tips |
| 9 | Driver +19.5 | over the marsh to the fairway by the bunkers |
| 10, 14, 15, 18 | Driver, -13.5 to +2.5 | fairway 43-54%; 15 water right 5%; 18 sand 12%, trees 10% |
| 11 | Driver -22 | dogleg left, fairway 49% |
| 12 | Driver +30 | around the water (dogleg right), fairway 43%, water 4% |
| 17 | Long iron -3 | lays up short of the cross hazard, fairway 81% |

No aim is past ±40. Every hole's only CHECK is the no-card one (plus the aim CHECK on 7).

## Next fix

1. Coordinator: confirm the par of River 7 (par 5 at 542 yds on the page; OSM name says par 4) if a card turns up.
2. Optional, page text: collapse the per-hole no-card CHECK into the header line, and drop the "card from no card" and
   "other tee sets" footer clauses when there is no card.
