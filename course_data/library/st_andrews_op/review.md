# St Andrews Golf Club (Overland Park, KS): course check (rv09)

Card: golfify, re-fetched and confirmed (Black 6362 / Blue 5986, par 71). OSM `dist` tags agree with it on 17 of 18 holes. The page renders cleanly on phone and desktop (qa_page.js: 18 holes, 0 problems).

QA CHECK holes were 5, 10, 15 and 16. Every hole was inspected on the page photos, with all tee sets, greens and hole lines overlaid.

| hole | verdict | note |
|---|---|---|
| 1-4, 6-9, 11-14, 17, 18 | OK | Routing, tee boxes and greens match the photo. 9 Black measures 378 vs 386 on the card. |
| 5 | OK | Dogleg left. The Blue calm pick cuts the corner and lands just off the fairway. The aim is marginal, but the geometry is correct. |
| 10 | OK (uncertain) | The Black tee is on a lidar pad 36 yds behind the Blue box, in a mowed area between the cart paths. It is probably a real back tee that OSM does not map. |
| 15 | bad pick | Black 4-wood aimed 40 yds left lands at the dogleg corner by the trees (51% trees). The sensible play is a straighter, shorter club. |
| 16 | **wrong tee** | The Black tee was walked back 28 yds to reach the card's 419, which puts it on the 15th green. Fix: move it to the back of the Blue box (about 393 yds). No tee behind that box is visible. |

Verdict: one real geometry error (16 Black tee) and one questionable pick (15 Black). Do not publish as-is with the Black set on hole 16. The fix is in review.json. It is a tee override, not an OSM supplement, because the box already exists in OSM and the gap is between the card and the ground.
