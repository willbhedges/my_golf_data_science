# Spike: "tell me the course and tees" instead of screenshots

Question: can the tee-strategy model get its hole maps (tee, aim line, green, and fairway /
trees / native / water / sand / OB polygons) from a course name and tee choice, with no
screenshots and no hand tracing?

**Verdict: yes, partly.** OpenStreetMap supplies the hole skeleton and the golf-specific
features for this course. It does not supply trees, native grass or OB. Those are the
hazards that drive tee strategy. Public-domain NAIP imagery at 0.3 m can fill them, but
that needs a classifier and a short user review.

## 1. What the prototype did (GitHub Actions)

The sandbox blocks Overpass, Nominatim and the Planetary Computer. The work therefore ran
on Actions (`.github/workflows/course_fetch.yml`), using the same pattern as
`deep_features.yml`: a push trigger with a paths filter, `contents: write`, a bot commit,
`pull --rebase` and push with retries.

| Run | Result |
|---|---|
| 1 (38944118883) | Course found (OSM relation 13353211). Failed because Overpass returns no `bounds` for relations. |
| 2 (38944563567) | Failed because `out geom` drops `center`. |
| 3 (38944953113) | Success: OSM, NAIP and the model-frame conversion were committed. |
| 4 (38946346234) | Success, with Mozingo Lake (OSM only) added as a second course for comparison. |

`workflow_dispatch` can't be triggered from the session: both `gh` and the MCP tool get
HTTP 403 "Resource not accessible by integration". New courses therefore need a push, or
the owner can click "Run workflow" in the UI. Overpass took about 1–2 min per run.

### Files

- `course_data/fetch_course.py`
  - Finds `leisure=golf_course` by name near a lat/lon (falls back to Nominatim).
  - Pulls every golf, land-cover, water, road and building feature in the course bbox.
  - Writes `osm.geojson`, `osm_raw.json` and `summary.json`.
  - Clips the latest NAIP from the Planetary Computer STAC (no key needed).
- `course_data/osm_to_model.py`
  - Turns OSM into **drop-in `HOLES` dicts** for `mozingo/tee_strategy.py` (see §3).
  - Writes `holes_from_osm.json` and `holes_preview.png`.
- `course_data/compare_traced.py`: compares the OSM-derived lies with the hand-traced
  `spirit_hollow/course.py` maps.
- Outputs are in `course_data/spirit_hollow/` and `course_data/mozingo/`.

### Location confirmed

The course is Spirit Hollow GC, 5592 Clubhouse Dr, Burlington, Iowa, about 4.5 mi south
of town. The OSM centre is 40.7605, -91.1442. NAIP shows US-61 (four-lane) along the west
edge, creeks through the middle, and the housing development inside the course. This
matches the screenshots (highway on 5, creek, houses as OB).

## 2. OSM coverage

| | Spirit Hollow | Mozingo Lake |
|---|---|---|
| `golf=hole` centre-lines | **18/18**, all with `ref` and `par`; no `handicap` or `dist` | **18/18**, with `ref` and `par` |
| OSM total length (line start to green) | 7,245 yd (scorecard Gold is about 7,0xx–7,5xx; sources disagree) | – |
| `golf=tee` polygons | 103, **0** tagged with colour or ref | 84 (66 inside the course), 12 tagged |
| `golf=green` | 26 (25 inside: 18 + practice) | 30 |
| `golf=fairway` | 20 | 20 |
| `golf=bunker` | 50 (also `natural=sand`) | 25 |
| water | 11 `lateral_water_hazard`, 14 `natural=water`, 11 streams + 3 drains (lines only) | 3 `water_hazard`, 3 `natural=water` |
| `golf=rough` | 34 polygons (mown rough) | 22 |
| **trees** (`natural=wood`, `landuse=forest`) | **none** | none (12 single `natural=tree` points) |
| **native / long grass** | **none** | none (`landuse=grass` ×119) |
| **OB** | none tagged. Proxies: course boundary, 24 buildings, `landuse=residential`, US-61 (`highway=trunk`) | same |

### Pars and lengths against the traced maps

- **Pars:** all 15 traced holes agree with OSM.
- **Lengths:** after the tee-box choice (below), OSM matches the traced length within
  2–10 yd on 14 of 16 tee/hole combinations. The two exceptions are 2B and 17: there,
  no OSM tee box matches the traced length.

### Agreement in the landing zone

Grid: 200–320 yd along the line, ±45 yd across, 5 yd spacing.

- **Raw overall lie agreement is about 0.40.** Run `python course_data/compare_traced.py`
  to reproduce it.
- **Registration is part of the gap.** The app's tee and red aim line differ from the OSM
  tee box and centre-line by up to about 8° and 40 yd. With a best rotation and shift per
  hole, fairway agreement rises from 0.65 to 0.75.
- **OSM fairways are accurate but narrow.**
  - Where OSM says fairway, the traced map also says fairway 98% of the time.
  - The traced fairway covers about 1.7× the OSM area. OSM is about 25–50 yd wide at
    270 yd; traced is about 55–65 yd.
  - An overlay on 0.3 m NAIP shows the OSM fairway outlines sitting on the mown stripes.
    So the traced maps probably include the first cut. That is worth checking, because
    it affects every fairway-percentage number in the model.
- **Trees and native grass are the real gap.** Of the traced `recovery` and `native`
  points, about 90% come out as plain rough from OSM.
- **Water is partial.** Creeks are mapped as centre-lines (buffered to 4 yd here), but
  the traced creek-bank hazards are wider. 52% of traced water points are matched after
  registration.

### Tee colours

Tees aren't colour-tagged here, so `pick_tee` chooses the OSM tee box whose playing
length (tee → hole-line nodes ahead → green) best matches the **scorecard yardage** for
the chosen tee set. Only boxes within 30 yd of the hole line are considered. The
scorecard therefore becomes the key input.

## 3. Conversion to the model frame

`osm_to_model.convert()` puts each hole in yards, rotated so the tee line points up:

```
tee = (0, 0)    dot270 = (0, -270)    point = (yds right, -yds along)    px_per_yd = 1
```

`hole_frame()`, `lie_at()` and `simulate()` therefore work unchanged.

- **Aim line:** tee → first hole-line node at least 60 yd ahead. That is the dogleg
  corner, or the green on a par 3.
- **Lies:** fairway, sand (bunkers), water (hazards, ponds, buffered streams), recovery
  (wood, scrub, tree rows) and native (grassland, meadow) map to the model's lies. OB
  comes from buildings, residential land, buffered roads, and *outside the course
  boundary*. The boundary area is encoded as a keyhole polygon so that `Path`'s
  nonzero-winding test treats the course as a hole.
- **Order:** later zones win, in the order ob < native < recovery < fairway < water < sand.
- **Boundary caution:** boundary-as-OB is a proxy. On Spirit Hollow it marks the
  housing pods and the farmland correctly, but OSM boundaries can be loose.

## 4. Data sources

| Source | Coverage | Resolution | Licence | Access |
|---|---|---|---|---|
| **OpenStreetMap** golf tagging (`golf=hole` with ref/par/handicap and a centre-line whose node count is par−1; tee, green, fairway, bunker, water_hazard, lateral_water_hazard, rough, driving_range; `natural=wood/scrub`) | Worldwide but uneven. Both courses here are complete for golf features and have no tree or native polygons. | Vector; hand-mapped from imagery, often within a few metres | **ODbL 1.0**: attribution; share-alike if you *publish* a derived database. Personal use is fine. | Overpass API (free, rate-limited, blocked from the sandbox, fine on Actions). Geofabrik extracts for bulk. |
| **OpenGolfAPI** (opengolfapi.org) | Claims about 16.8k US courses: location, scorecards, ratings/slope/yardages ("ongoing" coverage) | – | ODbL data, CC0 standards. Launched in 2026, tiny budget; durability is a risk. | REST with no key, 1,000 calls/day; bulk GeoJSON/CSV on GitHub |
| **USDA NAIP** via Microsoft Planetary Computer STAC (`naip`) | Continental US, roughly every 2–3 years | **0.3 m** for Iowa 2023 (fetched); 0.6 m in older years and other states; 4 bands RGB+NIR; leaf-on (summer) | US Government work, **public domain** | `pystac-client` + `planetary-computer`, anonymous, signed COG URLs. Iowa years: 2011–2023. Also USGS National Map / EarthExplorer. |
| USGS 3DEP lidar (not tried) | Iowa has statewide lidar | Point cloud, 1–2 pts/m² or better | Public domain | Planetary Computer `3dep-lidar-*` collections or AWS. Gives a canopy-height model: the most reliable *trees* layer. |
| Esri World Imagery | Worldwide, often sharper and more recent | Sub-metre | Esri Master License Agreement. Basemap layer not for export or offline use; derived-data rights are unclear. **Don't build on it.** | Tile service (blocked here) |
| Google / Bing imagery | Worldwide | Sub-metre | ToS forbid tracing or derived datasets (Bing allowed OSM tracing only) | – |
| iGolf, GolfLogix (35k+ courses), 18Birdies, GolfNow | Near-complete commercial course maps (hazard polygons, greens) | Survey or app grade | Proprietary B2B licensing (iGolf licenses to 60+ brands). App ToS prohibit scraping. No self-serve API. | Commercial contract only |
| GolfAPI.io, Zyla-style "golf course API" resellers | Course lists, coordinates, sometimes scorecards | – | Commercial, terms vary | Paid keys |
| Scorecards: club website, BlueGolf, GolfPass, GolfNow listings | Hole-by-hole yardage per tee (for Spirit Hollow, GolfPass lists Gold 7,550 / 74.8 / 134, White 6,010, Red 5,053; other sites differ) | – | Copyrighted pages; facts (yardages) are fine to use personally | Scraping or manual. Another agent's `tees-fetch` workflow already pulls the pages. |
| USGA NCRDB (Course Rating / Slope database) | All rated US tees: rating, slope, *total* yardage per tee | – | USGA terms; lookup site, no API | Manual lookup. Authoritative for tee-set names and totals, not hole-by-hole. |
| Danish Golf Courses Orthophotos (Kaggle / Dataset Ninja) | 1,123 + 108 labelled orthophotos from 107 courses: green, fairway, tee, bunker, water | 1:1000 | ODbL | Pretraining data for a segmentation model. It has no tree or native class. |

## 5. Recommended architecture

For a US course with OSM golf coverage:

1. **Resolve the course.** From name + town, use Overpass / Nominatim (or OpenGolfAPI
   search) to get the OSM id and boundary. Show the user the boundary on NAIP to confirm.
2. **Get the scorecard.** For the chosen tee set, the user pastes or confirms 18
   yardages; pars come from OSM. Pre-fill from OpenGolfAPI or a club scorecard scrape,
   and sanity-check the total against NCRDB.
3. **Build the skeleton (done in this spike).** OSM hole lines and tee boxes, with
   `pick_tee` matching the scorecard yardage → tee, aim line and green in the model frame.
4. **Take golf polygons from OSM.** Fairway, bunker, water, green.
5. **Fill hazards from imagery.** Use NAIP 0.3 m RGB+NIR, the texture and colour
   features from `spirit_hollow/vision.py`, and OSM polygons as free training labels
   (fairway / green / bunker / water, plus `golf=rough` as mown). Predict trees (NIR +
   texture; ideally 3DEP canopy height) and native grass (unmown, inside the boundary,
   not covered by any golf polygon). Hand-traced Spirit Hollow and Mozingo serve as the
   validation set.
6. **Infer OB.** Buildings, residential land, roads and the outside of the boundary
   become OB *candidates*; the user confirms them on the preview.
7. **Review.** Show the per-hole preview (as in `holes_preview.png`, over NAIP). The user
   taps to fix the tee, the green, or a mislabelled area. Then run the model.

Where OSM is sparse, run steps 3–4 from user taps: tee and green per hole (two taps)
plus the imagery classifier for everything else. The classifier then also has to find
fairways and bunkers, so expect lower confidence and more review.

**Effort estimate:**

- Hardening fetch/convert (caching, multi-course, registration check): about 2–3 days.
- Scorecard ingestion with manual fallback: about 1–2 days.
- NAIP (+ lidar) tree/native classifier, validated against the traced maps: about 1–2 weeks.
- Review/preview UI: about 1 week.
- Total: **about 3–4 weeks** for a dependable v1 on US courses.

## 6. Risks

- **The missing hazards matter most.** Trees, native grass and OB are absent from OSM,
  and they dominate the tee decision. The classifier is the critical path.
- **The fairway-width disagreement (1.7×) must be resolved** before trusting either
  source. OSM looks right against NAIP, which would mean the traced maps overstate
  fairway hit rates.
- **OSM quality varies by course.** Both test courses happen to be well mapped (the way
  ids suggest a 2021 import or survey). Many courses have only a boundary.
- **Tee colours are rarely tagged,** so tee choice depends on scorecard yardages.
  Forward tees offset from the centre-line can be missed (hole 2B and 17 here).
- **Aim line:** the OSM centre-line differs from the GPS app's line, and the strategy
  depends on the aim reference. Report aims relative to a stated target such as
  "the 150 marker" or "the left edge of the fairway bunker".
- **Imagery season:** NAIP is leaf-on summer imagery; the screenshots are winter, so the
  classifier would need retraining. NAIP is also 1–3 years old, so recent course changes
  can be missed.
- **Licensing:**
  - Fine for personal use.
  - Publishing the derived course database triggers ODbL share-alike.
  - Never mix in Esri, Google or commercial-app data.
- **Infrastructure:**
  - Overpass and the Planetary Computer are free community and Microsoft services, with
    no SLA.
  - Planetary Computer data APIs have had deprecation notices; keep USGS as a backup
    NAIP source.
  - Actions `workflow_dispatch` is not callable from the session.
