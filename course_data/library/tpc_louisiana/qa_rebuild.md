# TPC Louisiana: rebuild QA, Geofabrik OSM (2026-11-03)

**Verdict: NEEDS FIX (no scorecard).** The OSM geometry is complete and the picks are sensible on all 18 holes. The
yardages and pars are plausible for this course: par 72, 7,410 yds from the back OSM boxes, par 3s on 3, 9, 14 and
17, par 5s on 2, 7, 11 and 18. Two problems block it:

- No card was matched, so every hole carries a yardage / par CHECK.
- Golfers see the internal set name: "from the **osm_back** tee". The par-3 badges also say "176 **on the card**"
  although no card exists.

Page checked: `course_data/library/tpc_louisiana/page.html`, GitHub Actions run 41539188571 (built
2026-11-02T23:44Z). One set (`osm_back`), single-set page: 18 holes, phone and desktop, 0 page problems, no console
errors. I looked at every phone hole picture.

## OSM source

`raw/summary.json` → `osm_source`: `{"source": "geofabrik", "reason": "complete", "mirror": "geofabrik:LA",
"osm_base": "2026-11-01T21:21:36Z"}`. Counts: 18 holes, 22 greens, 62 tees, 17 pins, 97 bunkers, 20 fairways. The
package has 315 features, 18/18 holes mapped, 18/18 greens found and 62 tee boxes. On the photos the Dye waste
bunkers, lagoons and fairways are all drawn and line up. The feature set looks complete.

## Yardages and pars (no card)

Measured from the OSM tee nearest each hole-line start (on an OSM box on every hole):
395, 547, 176, 466, 425, 498, 552, 370, 232 | 391, 572, 485, 398, 213, 491, 432, 209, 558 = 7,410, par 36-36.
This is close to the published championship length (about 7,400) and has the par layout I expect for this course.
I did not verify it against a card (none in the repo).

## Holes

| hole | osm_back | note |
|---|---|---|
| 1-18 | OK (CHECK: no card) | tee on an OSM box; every tee shot lands on fairway (43-73%) with 0-18% trees / water / OB; aims within ±16 |
| 12 | OK | Driver straight, fairway 49%, sand 16% / trees 18% (waste bunker and trees down the left) |
| 16 | OK | 2-wood +4 (tie with 4-wood), sand 33%: the long waste bunker by the landing area |

## Next fix

1. Get a card: `webfetch_*.json` for the golfify / TPC page, then a `yardages` + `pars` request for the two longest
   sets. Rebuild.
2. Pipeline: when there is no card, the set label and the par-3 "on the card" badge should not show (see the report).
