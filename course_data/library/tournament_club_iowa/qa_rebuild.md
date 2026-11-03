# Tournament Club of Iowa: rebuild QA, Geofabrik OSM (2026-11-03)

**Verdict: NEEDS FIX (hole 1 only).** This rebuild fixes everything wrong on the older published page (run
40995757384): hole numbering, tees and pars. On hole 1, though, the Palmer tee shot finishes in the native prairie
past the creek. The course has no long-grass layer at all (no mapper pass, so no `agent_layers`). The model therefore
scores the prairie as plain rough. Every other hole is OK.

Page checked: `course_data/library/tournament_club_iowa/page.html`, GitHub Actions run 41539188571 (built
2026-11-02T23:41Z). Both solved sets (King 7,041, Palmer 6,516, par 71) were run through `qa_page.js`: 18 holes each,
phone and desktop, 0 page problems, no console errors. I looked at every phone hole picture and drew the package
zones, tees and lines on 1, 4, 7 and 10.

## OSM source

`raw/summary.json` → `osm_source`: `{"source": "geofabrik", "reason": "complete", "mirror": "geofabrik:IA",
"osm_base": "2026-11-01T21:21:36Z"}`. Counts: 18 holes, 26 greens, 72 tees, 26 bunkers, 23 fairways. The package
has 1,059 OSM features, 18/18 holes mapped, 18/18 greens found and 70 tee boxes, with 2 range tees dropped. The
fairways, bunkers, ponds and creek all line up with the 2023 NAIP image on every hole I overlaid. The feature set
looks complete against the imagery.

## Against the older page

| problem on the old page (`review.md`) | now |
|---|---|
| nines swapped (OSM hole c = card c±9) | **fixed.** `osm_supplement.geojson` + `ignore_osm_holes`: card hole 1 is the 553-yd par 5 by the clubhouse, card 18 is 459 |
| mid tees (5,923 yds total) | **fixed.** Review tees (King / Palmer) are used; measured within 12 yds of the card on every hole-set |
| pars wrong on 10 and 15 (page numbering) | **fixed.** Pars = card, 71 |
| page 10 driver 40 left into waste | gone (that hole is now card 1, see below) |

## Holes

| hole | King | Palmer | note |
|---|---|---|---|
| **1** | marginal (CHECK) | **bad pick** | 553 / 527. King: 2-wood -14.5 (total 307) reaches the end of the first fairway at the cart-path / creek crossing. Palmer: the forecast play is **Driver, total 338, 162 to green**, and its pattern sits in the native prairie past the creek. The calm 4-wood also lands 295 out, 18 yds off the fairway, with 29% water, plus a wide-aim CHECK on Driver -63. The sensible play is a lay-up to the first fairway, about 250-270 |
| 2, 3, 8, 9, 12, 13, 17, 18 | OK | OK | |
| 4 | OK | OK (on the bound) | Driver -35.5 / -40 up the left of the fairway, 65-80% fairway |
| 5 | OK (CHECK) | OK | King 174 measured / 185 card (-11), on the OSM box |
| 6, 11, 14, 16 | OK (CHECK) | OK / CHECK | review tees 16-21 yds from the nearest OSM box (tee CHECKs only) |
| 7 | OK (CHECK) | OK (CHECK) | King 374 / 386 (-12). Palmer 2-wood -54 across the dogleg-left corner beside the creek, 69% fairway; wide-aim CHECK printed |
| 10 | OK (CHECK) | OK (CHECK) | Driver -27 / -28 lands 9 yds off the fairway at the bend left, 28-29% fairway |
| 15 | OK | OK (CHECK) | Palmer 193 measured / 182 card (+11) |

## Next fix

A mapper pass with long grass (and trees) for hole 1. The native prairie runs from the creek crossing at about
300-330 yds to the second fairway. Then rebuild with `agent_layers`. TCI has prairie on several holes, so the mapper
should also check the long-grass verdicts on 4, 7, 10 and 17.
