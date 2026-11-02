# Osage National: rebuild QA (2026-11-02)

**Verdict: PUBLISH, with the renovation caveat shown to the user.** The hole 1 Palmer fix is applied, and every hole on
both sets matches the OpenGolfAPI card. Two things this page cannot rule out:

- **Renovation:** River and Mountain were renovated in 2025-26, but the page imagery is NAIP **2016**, and the card is
  OpenGolfAPI's (no other source was reachable). Bunker, tree and water zones, and possibly tee yardages, may be stale.
- **3 Palmer:** the tee is still a lidar pad in the parking lot behind the pond (377 measured / card 370). The reviewer
  marked this uncertain: either the tips are unmapped, or the card predates the renovation.

The Tournament set is clean on every hole. If the coordinator wants no caveat at all, publish with Tournament as the
default set.

Page checked: `course_data/library/osage_national/page.html`, built 2026-11-01T21:15Z. Both solved sets (Palmer 7,120,
Tournament 6,681, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at
every phone hole picture. The 18 holes are Mountain + River (the Links nine is closed until April 2027), as reviewed.

## Review fixes

| fix in review.md | applied? |
|---|---|
| 1 Palmer: lidar pad at the parking edge -> OSM back box 793605682 (369 yds) | **yes.** Tee snapped 5 yds to OSM tee 793605682, 365 measured; the page shows the card's 377. 4-wood on the line, fairway 64%. |

## Holes

| hole | Palmer | Tournament | note |
|---|---|---|---|
| 1 | **fixed** | OK (marginal) | Tournament Driver/4-wood tie, Driver aim 10 right, trees 13%, fairway 17% |
| 2, 6, 7 | OK | OK | Palmer walk-back / lidar pads behind the back OSM box at card length (unmapped tips, as reviewed) |
| 3 | **uncertain** | OK | see above |
| 4, 5, 8-10, 12-18 | OK | OK | OSM boxes, card length; par-3 boxes on the green |
| 11 | OK | OK | Tournament Driver/2-wood tie lands near the cart path crossing, sand 8% |
| 15 | OK | OK | long iron to the narrowing fairway on a 314/291-yd par 4 |
| 10 | OK | OK | build note: Green tee moved 5 yds off a building (Green is not on the page) |

## Next fix

None blocking. Before or after publishing: get a post-renovation card from the club, and check 3 Palmer against it.
Rebuild when NAIP newer than 2025 is available.
