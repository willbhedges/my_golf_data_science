# Hodge Park GC: rebuild QA, wide-aim pass (2026-11-03)

**Verdict: PUBLISH.** Hole 10 is back on the OSM line. The page's line is `osm_supplement.geojson` way 1565676856
vertex for vertex: from the tee NE over the cart path, 225 yds up the mown strip to the fairway bend, then NNW to the
green. Blue measures 400 (card 405), White 373 (371), Red 331 (329). The Red review tees on 1, 3, 11, 12 and 16 are
in the package at card distance. Red is not a page set, though, so they do not show on the page.

Page checked: `course_data/library/hodge_park/page.html`, GitHub Actions run 41537321619 (committed 2026-11-03 00:35Z).
I ran both solved sets (Blue, White) through `qa_page.js`, phone and desktop: 18 holes each, 0 page problems, no
console errors. I looked at every Blue phone hole picture and the White 10 desktop picture. I drew the OSM way onto
the page's own hole-10 image: the first leg runs up the mown strip, and the bend is on the fairway. Every landing oval
was checked against the picture edge on both sets.

## Checks

| check | result |
|---|---|
| Hole 10 | on the OSM line. Blue tee at the review point in the mown strip (18 yds behind the blue-tag box, "review" tee CHECK, as the review expects); White inside OSM tee 279487450; Red inside 279487451. Blue 4-wood 16.5 left to the bend (fairway 60%). White 4-wood 60 left past the bend (fairway 38%, trees 12%), wide-aim CHECK. The green is 132 yds left of the tee line, so it is off this tee-shot picture; the landing ovals are inside |
| Red tees 1 / 3 / 11 / 12 / 16 | 327 / 330, 124 / 123, 428 / 429, 148 / 149, 161 / 161 (measured / card), all "review (inside OSM tee)". Package only: Red is not a page set |
| Hole 3 | fixed: Blue 167 / 168 and White 144 / 148, now on separate boxes (inside OSM tee), not one shared centroid |
| Card / pars | page yardage = card on all 36 hole-sets; measured within 8 yds (White 1: 372 / 380) |
| Wide-aim CHECK | Blue 9 (Driver +40; row +69), 15 (Mid iron pick; Driver row +62) and 18 (2-wood +51.5). White 9 (Driver +45), 10 (4-wood -60), 15 (Driver +51.5) and 18 (4-wood +40; row +55) |
| Ovals | White 8 Driver 40 left clips the left edge by 11-12 px (about 3 yds), forecast and calm. The aim is on the ±40 bound, so the picture was not widened. Blue 10 calm Driver row is 8 px off. Everything else is inside |
| Native check cards (Blue) | 2 (Driver +20) and 5 (Driver -8) = page |
| Mapper layers | applied (62 ops); landings plausible |

## Holes

| hole | Blue | White | note |
|---|---|---|---|
| 1, 4-7, 11, 13, 14, 16, 17 | OK | OK | |
| 2, 12 | OK (tee CHECK) | OK | tagged boxes 3 / 13 yds off |
| 3 | **fixed** | **fixed** | separate boxes |
| 8 | OK (marginal) | OK (oval clips 3 yds) | Driver 30 / 40 left over the dogleg trees |
| 9 | OK (CHECK) | OK (CHECK) | Driver 40-45 right at the dogleg, trees 5-16% |
| 10 | **fixed** (tee CHECK) | **fixed** (CHECK) | see above |
| 15 | OK (CHECK) | OK (CHECK) | Blue mid iron to the fairway (forecast); White Driver 51.5 right, trees 12% |
| 18 | OK (CHECK) | OK (CHECK) | 2-wood / 4-wood 40-51.5 right toward the green on a 277-302 par 4 |

## Next fix

None. Optional: widen the picture for aims on the ±40 bound too (White 8).
