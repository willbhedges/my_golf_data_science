# Auto course: architecture

The goal is that the golfer says **"Spirit Hollow, white tees"** (any US course) and the system builds, with
no screenshots, everything `mozingo/tee_strategy.py` and `mozingo/yardage_book.py` need for every hole:
the tee point for the chosen tee set, the green centre, par, yardage, hazard polygons (`fairway`,
`recovery` = trees, `native` = long grass, `water`, `sand`, `ob`) in the model's frame, and a clean
overhead image for the book.

Owner of this file, `pipeline.py` and `acceptance.py`: architect. Stage owners are listed in section 1.
The status section (section 8) is kept current; read it first.

---

## 1. Stages

```
 "Spirit Hollow", "white"
        |
 S0 RESOLVE ------------- course.json         (OSM id, name, centre, bbox, slug)                 spike: fetch_course.find_course
        |
 S1 FETCH (Actions) ----- osm.geojson         (every golf/landcover feature, WGS84)              spike: fetch_course.py
        |                 scorecard.json      (tee sets x holes: par, yards, hcp)                tees/   (fetch_scorecards.py ...)
        |                 imagery/naip.tif    (NAIP RGB(+NIR) GeoTIFF, date, CRS)                imagery/
        |
 S2 TEES ---------------- tees.json           (per hole: tee point for the chosen set + how)    tees/
        |
 S3 BUILD HOLES --------- holes_osm.json      (per hole in the yard frame, OSM zones only)       geometry/
        |
 S4 GAP-FILL ------------ zones_vision.json   (classifier zones where OSM has nothing)           imagery/  (+ spirit_hollow/vision*.py)
        |
 S5 RENDER -------------- images/holeNN.png   (920x2000 overhead in the virtual pixel frame)     imagery/
        |
 S6 MERGE + QA ---------- holes.json         (the course model, with provenance + confidence)    architect: pipeline.py
        |                 course_auto.py      (generated module, same API as spirit_hollow/course.py)
        |                 qa.md               (per-hole flags; holes below the bar are listed)
        |
 S7 BOOK ---------------- <slug>/output/*_Strategy.pdf via yardage_book.use_course(...)          existing book code
```

| Stage | Runs where | Owner | Module (expected entry point) |
|---|---|---|---|
| S0 resolve | Actions (Nominatim + Overpass) | spike | `fetch_course.find_course(name, near, radius_m)` |
| S1 OSM fetch | Actions | spike | `fetch_course.py --name --near --out` -> `osm.geojson`, `summary.json` |
| S1 scorecard | Actions (web) | tee scientist | `tees/fetch_scorecards.py` -> `tees/raw/`; parsed to `scorecard.json` |
| S1 imagery | Actions (Planetary Computer STAC) | imagery | `imagery/*` -> `imagery/naip.tif` + `imagery/meta.json` |
| S2 tees | local, offline | tee scientist | `tees.<mod>.place_tees(fc, scorecard, tee_set) -> tees.json` |
| S3 holes | local, offline | geometry | `geometry.<mod>.build_holes(fc, tees) -> {ref: hole}` (fallback: spike `osm_to_model.convert`) |
| S4 gap-fill | local or Actions | imagery | `imagery.<mod>.gapfill(course_dir, holes) -> {ref: [zone,...]}` |
| S5 render | local (needs the GeoTIFF) | imagery | `imagery.<mod>.render_hole(course_dir, hole, out_png, frame)` |
| S6 merge, QA | local | architect | `pipeline.py` |
| S7 book | local | existing | `yardage_book.use_course(...)`, `yardage_book.build()` |

The network rule: this sandbox cannot reach Overpass, Nominatim, Planetary Computer or scorecard
sites. Everything with a URL in it runs in a GitHub Actions workflow that commits its outputs to the
branch (pattern: `.github/workflows/course_fetch.yml`, `deep_features.yml`). Everything after S1 is
offline and deterministic given the S1 files, so it runs in the sandbox, in CI or on the golfer's laptop.
`pipeline.py` never fetches; when an S1 file is missing it prints the `gh workflow run` command to get it.

## 2. Coordinate systems

Four frames, each with one job. Every conversion goes through the hole's **tee line**.

| Frame | Units, axes | Used for |
|---|---|---|
| **WGS84** | `[lon, lat]` (GeoJSON order, always) | Storage of everything fetched: OSM, tees, greens, imagery bounds |
| **Local ENU** | metres east, north of a course origin (equirectangular: `e = (lon-lon0)*cos(lat0)*111320`, `n = (lat-lat0)*111320`) | Distances, buffering, imagery warping. Error < 0.1% within 3 km. |
| **Yard frame** (proposed native model frame) | yards; `x` = right of the tee line, `y` = **minus** yards along it (screen y grows down). Tee = `(0, 0)`, `dot270 = (0, -270)`. | `holes.json`. The model runs on it directly: `hole_frame` gives `ppy = 1`, `fwd = (0,-1)`, `right = (1,0)`. |
| **Virtual pixel frame** | 920 x 2000 px, `ppy = 3.4`, tee at `(460, 1900)`: `px = 460 + 3.4*x`, `py = 1900 + 3.4*y` | Generated `course_auto.py` and the rendered images, so `yardage_book.draw_tee` (`extent=(0,920,2000,0)`, view `y 540..2000` = 0-429 yds, `x` = +/-135 yds) works unchanged. |

**The tee line.** Tee point -> *aim point*, where the aim point is the first OSM `golf=hole` node at least
60 yds past the tee (the hole's first dog-leg node; the green for a par 3). This plays the role of the
app's dashed line in the screenshots. Aim offsets in the book ("5 yds left of the line") are relative to
it. It differs from the app's line by a few degrees on dog-legs, which is why `acceptance.py` registers
frames before comparing positions.

Conversions (implemented in `osm_to_model.Frame`; the geometry module must give the same numbers):

```
en      = ENU(lon, lat) about the tee            (metres -> yards: / 0.9144)
fwd     = unit(ENU(aim) - ENU(tee));  right = (fwd.n, -fwd.e)
x, y    = en . right,  -(en . fwd)               (yard frame)
px, py  = 460 + 3.4 x,  1900 + 3.4 y            (virtual pixel frame)
```

The inverse (pixel -> WGS84) is what the image renderer needs: `x = (px-460)/3.4`, `y = (py-1900)/3.4`,
`en = x*right - y*fwd` (yards -> metres), then ENU -> lon/lat. `holes.json` stores `tee_ll`, `aim_ll` per
hole, so any consumer can rebuild the frame without the geometry code.

**Why a yard-native frame.** The traced maps carry a scale error from one tee->270-dot vector per
screenshot (PROJECT.md R5: 1-2% = 3-6 yds at 300). Real coordinates have no scale to estimate; the
frame is yards by construction. The model already accepts it (it only uses ratios through `hole_frame`).
The pixel frame exists only for the book's image extent; it can be retired when `draw_image` takes
`extent` from the hole dict (one-line change in `yardage_book.py`, integrator's call).

## 3. Data contracts

All JSON is UTF-8, keys are strings, hole refs are strings (`"1"`, `"2"`, ... `"9"`; multi-tee keys are
added in S6 as `"2B"`, `"2F"` when the golfer asks for two sets). Coordinates in WGS84 are `[lon, lat]`.

### 3.1 `course.json` (S0)
```json
{"schema": "course/1", "name": "Spirit Hollow Golf Course", "slug": "spirit_hollow",
 "osm": {"type": "relation", "id": 13353211}, "center": [-91.1442, 40.7605],
 "bbox": [-91.1522, 40.7531, -91.1362, 40.7679], "address": "Burlington, IA",
 "candidates": [{"name": "...", "osm": {...}, "dist_km": 3.1}]}
```
Today `summary.json["course"]` carries this; `pipeline.py` reads either.

### 3.2 `osm.geojson` (S1)
A GeoJSON FeatureCollection, WGS84. Each feature's `properties` = the raw OSM tags plus `osm_id`,
`osm_type`, `inside_course` (bool). Holes are `golf=hole` LineStrings from tee end to green end with
`ref`, `par`, maybe `dist`/`handicap`. Produced by `fetch_course.py` (exists, works for Spirit Hollow:
18 holes, 103 tee boxes, 26 greens, 20 fairways, 50 bunkers, 11 lateral water hazards; **no tee colours,
no woods/scrub polygons, no tall-grass tagging** on this course).

### 3.3 `scorecard.json` (S1, tee scientist)
```json
{"schema": "scorecard/1", "source": "https://...", "fetched": "2026-10-16",
 "tee_sets": {
   "white": {"rating": 70.1, "slope": 125, "total": 6100,
             "holes": {"1": {"par": 4, "yards": 401, "hcp": 7}, "...": {}}},
   "blue":  {"...": {}}},
 "aliases": {"middle": "white", "men": "white"}}
```
Pars are tee-independent in most cards but are stored per set (some courses differ for forward tees).

### 3.4 `tees.json` (S2, tee scientist)
```json
{"schema": "tees/1", "tee_set": "white",
 "holes": {"1": {"tee_ll": [-91.14, 40.76], "box_osm_id": 923958000,
                 "how": "tagged|length_match|interpolated|hole_line_start",
                 "scorecard_yards": 401, "measured_yards": 404, "confidence": 0.9}}}
```
`measured_yards` = tee -> hole-line nodes -> green centre, along the line (how scorecards measure).
`how` order of trust: `tagged` (OSM tee box tagged with the colour) > `length_match` (the box whose
measured yards are within 8 yds of the card) > `interpolated` (box between two matched sets, or a
point on the hole line at the card yardage when no box fits) > `hole_line_start`.

### 3.5 Hole in the yard frame (S3 output, S6 input) - `holes_osm.json`
```json
{"schema": "holes/1", "frame": "yard", "holes": {"1": {
  "ref": "1", "par": 4, "length": 401,
  "tee_ll": [lon, lat], "aim_ll": [lon, lat], "green_ll": [lon, lat],
  "tee": [0, 0], "dot270": [0, -270], "green": [-14.2, -398.0],
  "hole_line": [[0, 0], [0, -290], [-14, -398]],
  "green_polygon": [[x, y], ...],
  "zones": [["ob", [[x, y], ...]], ["fairway", [[x, y], ...]], ...],
  "zone_src": ["osm:way/123", "osm:boundary", ...],
  "provenance": {"tee": "length_match", "green": "osm_green", "par": "osm", "length": "scorecard"}}}}
```
Zone rules (the model's `lie_at` contract): later zones win where they overlap, so S3/S6 sort by
`ob < native < recovery < fairway < water < sand` (spike's `ZONE_ORDER`). Polygons are simple vertex
lists (no holes); holes are encoded as keyholes (`osm_to_model.keyhole`). Anything not covered is rough.
Window kept per hole: +/-150 yds lateral, 40 yds behind the tee to 40 yds past the green (min 330 along).

### 3.6 `zones_vision.json` (S4, imagery)
```json
{"schema": "zones_vision/1", "imagery": {"source": "naip", "date": "2023-08-14", "gsd_m": 0.6},
 "model": "vision2 / ndvi-texture v1",
 "holes": {"1": [{"lie": "recovery", "poly": [[x, y], ...], "p": 0.86, "area_yd2": 3120}]}}
```
Gap-fill only adds `recovery`, `native` and `water` where OSM has no polygon of a penal class; it never
removes or reshapes an OSM `fairway`, `water`, `sand` or `green`. Minimum polygon 150 yd2,
probability >= 0.7, simplified to 2 yds.

### 3.7 Images (S5)
`<slug>/images/holeNN.png` (and `holeNN_b.png` for second tee sets), 920 x 2000 RGB, north-unaware:
rendered in the **virtual pixel frame of that hole**, so the tee is at `(460, 1900)` and the tee line runs
straight up. Par 3s use the same frame with the flag on the line. A sidecar `images/index.json` records
for each image the imagery date, the frame (`tee_ll`, `aim_ll`, `ppy`, `tee_px`) and the fraction of
pixels with no imagery.

### 3.8 `holes.json` (S6, the course model - the one file the rest of the system reads)
```json
{"schema": "course_model/1", "course": {...course.json...}, "tee_set": "white",
 "built": "2026-10-16T18:30Z", "frame": "yard", "pixel_frame": {"size": [920, 2000], "tee_px": [460, 1900], "ppy": 3.4},
 "stages": {"osm": "ok", "scorecard": "missing", "tees": "fallback:osm_to_model.pick_tee", "geometry": "fallback:spike", "vision": "missing", "images": "missing"},
 "holes": {"1": {...hole in the yard frame (3.5)...,
                 "image": "hole01.png",
                 "confidence": {"score": 0.71, "osm": 0.62, "imagery": 0.0, "inferred": 0.38,
                                "flags": ["no tree polygons in the landing zone", "tee from length match"]}}},
 "par3": {"7": {"tee": [0, 0], "flag": [0, -159], "center": 159, "front": 150, "back": 170,
                "green": [[lat, depth], ...], "haz": {"left": "sand", "right": "rough", "short": "water", "long": "native"}}}}
```

### 3.9 Generated `course_auto.py` (S6) - compatibility with `spirit_hollow/course.py`
Exposes `HOLES`, `PAR3`, `NOTES`, `AIM_AT`, `ORDER`, `LABELS`, `APP` (empty), `GREEN_SIDE` (empty), in the
**virtual pixel frame**, so `build.py` swaps `import course` for `import course_auto as course`:

* `HOLES[k] = dict(par, image, length, tee=(460, 1900), dot270=(460, 1900 - 270*3.4), green=(px, py),
  zones=[(lie, [(px, py), ...]), ...], aim_min=-40, aim_max=40, auto=dict(confidence...))`
  The model reads `tee`/`dot270` only through `hole_frame`, so a synthesised `dot270` exactly 270 yds up the
  line reproduces the yard-frame results bit for bit (the scale is exact, not estimated).
* `length` = scorecard yards for the set when known (the convention the book prints), else the
  measured tee -> green distance along the hole line.
* Par 3s go to `PAR3` via the same fields `_par3` produces: `tee`, `flag` (green centroid), `center`,
  `front`/`back` (along the tee-flag line), `green` as `(yds right, yds past the flag)`, `haz` from the
  zones touching each side of the green, plus generated `note`/`short`.
* `NOTES`/`AIM_AT` get a generated provenance line ("OSM fairway + bunkers, trees from imagery,
  tee matched to the card at 401 yds"); the book's text fields stay human-editable.

## 4. Merge rules (S6)

1. Tee: `tees.json` if present; else spike `pick_tee` with the card yardage; else hole-line start.
2. Green: OSM `golf=green` polygon nearest the hole line's last node (within 40 yds); centre = polygon
   centroid. Else the last node (flag: `green from hole line`).
3. Par: card > OSM `par` tag > length rule (<= 250 -> 3, <= 470 -> 4, else 5).
4. Length: card yards > measured along the line. A measured-vs-card gap > 15 yds is a QA flag (wrong box).
5. Zones: OSM first, then vision gap-fill for penal classes, then the course boundary as OB (only if
   the course has OB evidence - see failure modes), sorted by `ZONE_ORDER`.

## 5. Failure modes and what the pipeline does

| Failure | Detection | Handling |
|---|---|---|
| Course name ambiguous / not in OSM | S0 returns 0 or several `leisure=golf_course` | Ask the golfer with the candidate list (name, town, distance). No guess. |
| Holes missing in OSM (no `golf=hole`, or fewer than 9/18) | count refs vs scorecard | Hole line = tee box -> green pairs by card yardage and sequence (nearest unused green at the card distance +/-10%). Flag `inferred hole line`, confidence <= 0.5. Course with no tees *and* no greens: stop, ask for screenshots (the old path). |
| Tees missing / untagged colours (Spirit Hollow: 103 boxes, 0 colours) | `how != tagged` | Length match to the card (S2). No card: the box nearest 85% of the longest box (a typical white/middle) and flag it. |
| Tee box shared by two holes or a practice tee | box within 30 yds of two hole lines | Choose by projected position and heading toward the hole's aim node (spike's window `-150 < s < L-100`). |
| Mis-tagged polygons (fairway mapped as rough, `natural=sand` on a beach, ponds as `landuse=basin`) | vision disagreement > 40% of a polygon; area sanity (fairway 25-70 yds wide) | Keep OSM, add a QA flag; imagery-only classes never override `fairway`/`water`/`sand`. |
| Under-mapped trees and long grass (the common case: Spirit Hollow has none) | penal-class area in the landing zone = 0 while imagery NDVI/texture says woods | S4 gap-fill. Without imagery: hole confidence capped at 0.5 and the book says "trees not mapped". |
| OB not mapped | no `golf=out_of_bounds`, only the course boundary | Course boundary -> OB only where it borders `building`/`landuse=residential`/roads within 40 yds; elsewhere boundary = `native`. Flag every hole with OB from inference; golfer confirms from local rules. |
| Imagery date / season | NAIP `datetime` in metadata | Prefer leaf-on (May-Sep) for trees, leaf-off is better for creeks under canopy; store both when available. Record date in `images/index.json`; flag course changes (OSM `start_date`, construction). |
| Imagery shadow / tilt | NAIP is orthorectified: no lean, unlike the app screenshots | Trees traced at the canopy edge from NAIP, i.e. *wider* than the hand maps (traced at trunks). Acceptance expects tree IoU to be the weakest class. |
| Water as a line only (`waterway=stream`) | LineString | Buffer 4 yds (stream/ditch) or 10 yds (river); banks are `native` only if imagery says so. |
| Card has a hole the course re-routed | card par/yards vs OSM differ > 25% | Trust OSM geometry, card par; flag. |

## 6. Confidence per hole

Each hole gets `confidence = {score, osm, imagery, inferred, flags}`:

* Evaluate the landing-zone grid (220-340 yds along, +/-45 yds lateral, 5-yd step, 425 cells) and the
  source of the lie each cell gets: `osm` (inside an OSM polygon), `imagery` (inside a gap-fill polygon),
  `inferred` (rough by default, boundary OB, buffered lines). `osm + imagery + inferred = 1`.
* Default-rough cells count as `inferred` unless imagery checked them (imagery says "grass, low"),
  because the dangerous error is an unmapped hazard scored as rough (PROJECT.md R6).
* Point items: tee (`tagged` 1.0, `length_match` 0.9, `interpolated` 0.6, `hole_line_start` 0.4),
  green (`osm_green` 1.0, `hole_line_end` 0.6), par/length (card 1.0, OSM 0.8, rule 0.5).
* `score = 0.35 * tee + 0.15 * green + 0.10 * par_length + 0.40 * (osm + 0.8 imagery + 0.3 inferred)`.
* Bands: >= 0.8 "auto", 0.6-0.8 "check the flags", < 0.6 "needs screenshots / human review". The book
  prints the band on each hole page; `qa.md` lists the flags.

## 7. Acceptance (`acceptance.py`)

Compares an auto build of Spirit Hollow with the hand-reviewed `spirit_hollow/course.py`.

* Frames: the traced holes are in screenshot pixels with no georeference, and their line is the app's,
  not OSM's. So each traced hole is first converted to yards (`hole_frame`) and then **registered** to the
  auto hole by a rigid transform (rotation +/-15 deg, shift +/-40 yds, scale 0.95-1.05) that maximises
  agreement of the hazard rasters (fairway, water, sand, which both sources map well) over the whole
  window. The tee and green are *not* used to fit, so their errors are honest. The fitted scale is
  reported: it measures the screenshot scale error (R5).
* Per hole: tee error and green error (yds, after registration), length error (|card or measured -
  traced `length`|, frame-free), landing-zone IoU per class (220-340 along, +/-45, in the traced frame),
  and the club pick: `t.best_aim` for Driver, 2-wood and 4-wood on both maps, same club or not.
* Bar (proposed): tee and green within 10 yds, length within 5 yds, landing-zone IoU > 0.6 for water,
  OB and trees (classes present on the hole in either map), same club on >= 80% of the 16 tee shots.
* Hole keys: traced `2B`/`2F`/`9B`/`9F` are matched to auto holes 2/9 built with the traced length as the
  card yardage (that picks the same box), so one auto build covers both tees.

Run: `python3 course_data/acceptance.py [--holes course_data/spirit_hollow/holes.json] [--fast]`.
Writes `course_data/spirit_hollow/acceptance.json` and `acceptance.md`.

## 8. Status

(updated by the architect; newest first)

STATUS_PLACEHOLDER
