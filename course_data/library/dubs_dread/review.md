# Dub's Dread: course check (rv05, agent)

Evidence: `qa_page.js` shots (18 holes, 0 page problems), package geometry against all 19 OSM greens and 67 OSM tees, and the
golfify card (Championship 7,230, par 72; `card_golfify.json`). The page was built with no card.

**Verdict: not safe to publish as-is.** 9 holes OK, 9 need fixes (1 routing, 2 tees, 1 par, 5 yardages).

| hole | verdict | fix |
|---|---|---|
| 4 | wrong routing | Page hole 4 duplicates hole 13. The real 4 is a par 3 of 216: OSM way 1029130675 (no ref), tee way/505295054 to green way/505295060. Added to `osm_supplement.geojson`. |
| 12 | wrong par | The card says par 5 (547). The page plays it as a par 4 (the OSM tag). |
| 5 | wrong tee | 352 vs card 382. The tee moves to the OSM hole-way start (~25 yds back). A tee box is added in the supplement. |
| 9 | wrong tee (uncertain) | 367 vs card 418. The tee moves to the hole-way start (~29 yds back), which is still ~20 yds short. |
| 3, 6, 7, 13 | yardage | Card 446 / 467 / 550 / 420 against page 434 / 488 / 570 / 407. |
| 1, 2, 8, 10, 11, 14-18 | OK | within 10 yds of Championship, routing consistent |

Rebuild needs: the card (request `yardages` + `pars`, Championship) and the supplement. `course_page.py pkgreq` does not pass
`osm_supplement` through yet.
