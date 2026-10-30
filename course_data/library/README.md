# Course library: any US course -> a checked wind and club-pick page

One request file builds one page. `.github/workflows/course_page.yml` runs the whole chain on GitHub Actions;
`course_page.py` holds every stage. Automatic pages go here, in `course_data/library/<slug>/`. They never go to
`course_data/courses/`, where the hand-checked tournament pages live.

## Request

`course_data/requests/course_page_<slug>.json` (schema `course_page/1`):

```json
{"schema": "course_page/1", "name": "Swope Memorial Golf Course", "city": "Kansas City", "state": "MO",
 "near": "39.0,-94.5", "osm": "way/123",
 "tees": ["Blue", "White"], "days": ["2026-11-07", "2026-11-08"], "tee_hour": 9.0,
 "slug": "swope_memorial", "group": "library", "compute": {"draws": 48, "swings": 2500}, "rev": 1}
```

Only `name` and `state` are required. `city`, `near` or `osm` resolve ambiguous names. `tees` lists the tee sets
of interest. Without it, the two longest non-combination sets on the card are solved. `days` are the event days.
Without them the page uses the next Saturday and Sunday, with climate normals. `group: "gate"` writes to
`library/gate/<slug>/` and is used for the blind gate builds of the hand-checked courses (below).

To rebuild a list of courses, push `course_data/requests/course_batch_<name>.json` `{"requests": [paths], "rev": n}`.
One batch can hold many courses (the 60-course `course_batch_us60.json` is one run). Each course runs as its own
call of `course_page_one.yml` (package -> compute -> finish -> commit), up to 20 courses at a time, so the first
courses are committed while later ones are still packaging. Runs no longer share a branch-wide concurrency group, so
a later push never cancels an earlier one; parallel runs only share the account's limit of 20 concurrent jobs (extra
jobs wait in the queue). A run only sees the request files its own push changed: to rebuild courses from an older
run, list their requests in a new `course_batch_*.json`.

Picking courses: OSM completeness (every `golf=hole` ref 1-18 inside the course, 18 greens and 18 tees) is counted
on Actions by `osm_check.py` (workflow `osm_check.yml`, trigger `course_data/requests/osm_check_<name>.json`,
result `course_data/library/osm_check/<name>.json`). Requests built from it carry the checked `osm` id.

## What the workflow does

| job | what | code |
|---|---|---|
| plan | the request files the push changed -> a course matrix and a compute matrix (2 bases x wind / decide). Skips any target whose `config.json` says `"hand_checked": true`, and every slug that has a tournament folder in `course_data/courses/` (Blue Hills, Eagle Knoll, ...) or is Spirit Hollow / Mozingo. | `course_page.py plan` |
| package | resolve (OSM) + OSM features + web scorecard + NAIP + 3DEP: `platform/package.py run`. Then the vision layer (`vision_any/fetch_any.py`, `v2_fetch.py`, `v2_model.py --infer --integrate yes`), OB evidence (`ob/fetch.py`) and a package rebuild, so vision zones and inferred OB are in the first plan (Eagle Knoll F1 / Blue Hills B1). Then bases + weather, and the sharpest leaf-on NAIP year (finest gsd among the scored leaf-on candidates, newest on ties) fetched at 0.3 m for the hole pictures only. `imagery.dir` and `sources.imagery.dir` both point at it (the bh_sharp lesson). Then `v2_course.py prepare` for each base. | `course_page.py pkgreq / configure / prepare` |
| compute | per solved base: the v2 wind grids (base tee, plus offsets for any other set of interest) and the calm-day Bayesian decide (`draws` prior draws). Holes are split over the runner's cores. | `course_page.py compute` |
| finish | merge, then the v2 page (`v2_course.py page`, main base `auto`, second base `auto_b` folded in through `alt_bases`). Then the picture checks (`picture_checks.py`) and `courses/qa_page.js` (phone + desktop, from each solved set), then `qa_report.md`, `qa.json` and `status.json`, and a commit. | `course_page.py finish` |
| index | `course_data/library/index.json` | `course_page.py index` |

Weather (`weather.py`): if the first event day is within 14 days, the Open-Meteo hourly forecast. Otherwise,
**climate normals**: the same calendar window (+/- 7 days) over the last 10 years of ERA5 (Open-Meteo archive),
averaged per local hour, with the speed-weighted prevailing direction. Normals are marked `placeholder`, so the
page shows its "climate normals, not a forecast" banner. Grid temperatures span the 8 am to 4 pm range of that
weather, rounded to 5 F (3 temperatures).

## Picture checks and the confidence gate

Each check is run on each solved base, hole by hole (`picture_checks.py`):

| check | passes when |
|---|---|
| tee | the tee marker is inside an OSM `golf=tee` polygon (3 yds of slack). A lidar pad, a texture pad or a walk-back fails. |
| yardage | the measured tee-to-green length is within 10 yds of the card |
| par | the hole's par equals the card's par. At course level, the pars must also sum to the card's total. |
| aim (par 4/5) | the calm-day pick's landing point (club total along the tee line, at its aim) is on fairway, on first cut, or on rough within 6 yds of fairway |
| oval (par 4/5) | the pick's landing ellipse (the club's 95 % width x carry window + 6 yds of roll spread) is at most 40 % trees / water / OB. Unverified ground beyond the mapped corridor counts half, as in the model. |
| par-3 box | the calm target box the page draws has its centre on the OSM green polygon, with at least 60 % of its area on it. A green with no OSM outline fails. |
| page | `qa_page.js` finds no problems: console errors, NaN / undefined text, an empty play, a missing image, an empty table, horizontal scroll, or a hole that does not advance |

Course status (`status.json`, `index.json`):

* **auto-OK**: OSM maps every hole (`pipeline.holes.method == "osm"`, an OSM green for every hole), the web
  scorecard matched (found, consistent, no flags, same number of holes), the pars sum to the card, and every check
  above passes on every hole of every solved base.
* **needs confirm**: anything else. `check_holes` lists the holes to confirm, and `reasons` gives the
  course-level causes. Each CHECK hole's note on the page starts "Auto-map CHECK:" with its reasons.
* **failed**: no page (resolve ambiguous / not found, package or compute failure). `reasons` says where it
  stopped. `qa_report.md` lists the OSM candidates for an ambiguous name, so the request can add `osm` or `near`.

How the gate scores against the hand-checked courses is in `gate/GATE.md`. In short, no blind build passes the
strict gate: every course with a card still has 1-17 CHECK holes, mostly tees on lidar pads or walk-backs,
yardage more than 10 off the card, and calm picks landing in rough just off the mapped fairway. CHECK holes are
where wrong clubs concentrate (about 4x the PASS-hole rate), but hazard-perception errors (trees, long grass)
also cause wrong picks on PASS holes, and no geometry check can see those.

## Starter library (40 courses, MO / KS / IA / IL)

Requests: `course_data/requests/course_page_<slug>.json`. The status of each course is in `index.json`.

| outcome | courses | why |
|---|---|---|
| needs confirm: complete OSM holes + web card, only per-hole CHECKs | 18 | 1-17 CHECK holes each (Old Kinderhook 1; Annbriar, Prairie Highlands 2; Rivercut, Shoal Creek, Tiffany Greens 3) |
| needs confirm: no usable web card | 9 | no golfify / club-site / OpenGolfAPI card, or mixed card versions; holes and tees come from OSM only (the page solves the back OSM tee). A typed card (`"typed_card"`) moves these up a tier. |
| needs confirm: OSM holes incomplete | 9 | holes routed by routing v2 / structure / geometry; some courses come out short of 18 holes |
| failed | 4 | Deer Creek (OSM marks it "Former": closed); Lake of the Woods (OSM has no greens or tees); Longview Lake / Fred Arbanas (package job hit the 150-min timeout); Kokopelli (resolve: not found in OSM under that name; add `near` or `osm`) |

## `index.json` (schema `course_library/1`)

The app reads this file. The fields are stable. New fields may be added, but none will be renamed or removed.

```json
{"schema": "course_library/1", "doc": "course_data/library/README.md", "updated": "2026-10-29T20:00Z",
 "counts": {"hand-checked": 6, "auto-OK": 3, "needs confirm": 30, "failed": 7},
 "courses": [
  {"slug": "swope_memorial", "name": "Swope Memorial Golf Course", "city": "Kansas City", "state": "MO",
   "status": "needs confirm", "check_holes": [4, 11], "reasons": ["2 hole(s) with a CHECK"],
   "group": "library",
   "tee_sets": [{"name": "Blue", "yards": 6274, "par": 72, "rating": 70.3, "slope": 128, "colour": "blue",
                 "on_page": "solved"}, {"name": "White", "yards": 5900, "par": 72, "rating": null, "slope": null,
                 "colour": null, "on_page": null}],
   "solved_sets": ["Blue", "White"],
   "page": "course_data/library/swope_memorial/page.html", "page_bytes": 2711000,
   "qa_report": "course_data/library/swope_memorial/qa_report.md",
   "center": [39.0, -94.5], "osm": "way/123", "holes": 18, "days": ["2026-11-07", "2026-11-08"],
   "weather": "climate normals", "built": "2026-10-29T20:00Z"}]}
```

* `status`: `hand-checked` (tournament pages in `course_data/courses/<slug>/wind_page/index.html`, `group: "tournament"`),
  `auto-OK`, `needs confirm` or `failed`. Rows are sorted in that order, then by state and name.
* `tee_sets`: every set on the card, longest first. `on_page` is `solved` (its own tees, aims and calm-day picks),
  `offset` (the main base's tee moved along the line) or `null` (on the card but not on the page).
* `page`: a self-contained HTML file (no network needed), repo-relative. It is `null` for a failed course.
  `page_bytes` is its size.
* `center`: `[lat, lon]`. `days` are the event days the page was built for. `weather` is `forecast`,
  `climate normals` or `fallback`.
* The gate builds (`library/gate/`) are not in the index. They duplicate hand-checked courses.

Page format: the same v2 wind page as the tournament pages (`courses/wind_page_template_course.html`). The one
difference is that the page data (`D`) is gzip-compressed and base64-inlined, and a small boot script unpacks it
with `DecompressionStream` before the page code runs (Chrome 80+, Safari 16.4+, Firefox 113+). The global `D`
is the same object either way.

## Size policy (what is committed)

The two biggest parts of a page are the wind grids (about 4 MB of JSON per base) and the hole pictures (1.3 MB
per base at 0.6 m NAIP, up to 3 MB at 0.3 m). Library pages carry the grids gzip-compressed (about 6x smaller)
and the pictures at JPEG quality 66 (tournament pages use 76). A two-base page comes to about 2-4 MB instead of
10-15 MB.

Committed per course (`course_data/library/<slug>/`):

* `page.html`, `qa_report.md`, `qa.json`, `status.json`, `config.json`, `weather.json`, `sharp.json`
* rebuild data: `package_request.json`, `package.json` (the built course package: holes, tees, zones, card),
  `package_qa.md`, `raw/course.json`, `raw/summary.json`,
  `raw/scorecard_web.json`, `evidence/vision_any.geojson` (the inferred tree / long-grass / water layer),
  `evidence/ob_sources.json`, `evidence/vision_raw_meta.json`

Measured on the starter library (36 pages + 10 gate pages): page median 2.6 MB, largest 6.1 MB, 151 MB of pages
in all. With the packages and vision layers the checked-out `course_data/library/` is about 260 MB, and the JSON
part compresses about 5x in git. `package_v0_no_vision.json` (the package before the vision layer) was committed
for the first runs and is no longer committed. The pages are the largest part: if the library grows past about
100 courses, keep only the auto-OK and recently requested pages in the repo and rebuild the others on request.

Not committed: NAIP / DEM / lidar rasters, `course_data/packages/<slug>/` and `course_data/vision_any/<slug>/raw`
(the workflow's scratch), course modules, hole pictures, and the raw wind grids. Re-running the request (bump
`rev`) rebuilds everything from public sources. The committed `package.json` and the vision layer let you inspect
or re-score a page without a refetch.

## National course index

`us_courses.json.gz` (schema `us_courses/1`) lists every named `leisure=golf_course` in the 50 states + DC on
OpenStreetMap, with how completely OSM maps it. `national_index.py` builds it on Actions
(`.github/workflows/national_index.yml`; push `course_data/requests/national_index_<name>.json`
`{"states": [] (all) or ["IA", ...], "oga": true, "rev": n}`). The sandbox cannot reach Overpass. Each state is one
Overpass query (course outlines + `golf=hole|green|tee` + place names for the city), with retries over three
endpoints. A second pass retries failed states, and a state a run does not fetch keeps its rows from the committed
file. OpenGolfAPI's state listings (about 200 calls in all) mark courses it knows, matched by name + state, or by a
shared name stem within 1.5 km.

Columnar: `{"fields": [...], "rows": [[...]]}`. Fields: `name, city, state, lat, lon, osm, holes, osm_holes,
greens, tees, card, tier, closed`. `city` is `addr:city`, else the nearest city / town / village node. `holes` is
the outline's `holes` tag, else 18 or 9 from the mapped holes. `osm_holes` counts the distinct `ref`s of the golf=hole
ways inside the outline's bbox (a feature in two bboxes goes to the smaller course). `card` is `library` (a library
build found a web card), `oga` (OpenGolfAPI lists it with a par; its detail call usually gives the card), `oga?`
(listed without a par) or empty.

| tier | meaning | what the course_page pipeline does |
|---|---|---|
| A | OSM has a hole, a green and a tee per hole, and a card is known | its best case: holes by OSM, card cross-check (auto-OK candidates) |
| B | complete OSM holes, no card known | page from OSM tees; a typed card moves it to A |
| C | some OSM holes / greens / tees | routing v2 places the holes; often short of 18 (the "OSM holes incomplete" row above) |
| D | outline only | no page until someone maps it |

`us_readiness.json` has the per-state and national counts (`national`, `states.<ST>`, `best_states`).

<!-- NATIONAL_COUNTS -->

## Requests

Golfers ask for courses from the app (`course_data/app/course_index.js`, SCHEMA.md "National index and requests").
Every course in the national index can be searched on the pick screen. A course with no page yet has a
**Request this course** button, which writes one doc per golfer per course to the published app's shared db
collection `requests`:
`{schema: "golf_request/1", slug, name, city, state, osm, lat, lon, holes, requested_at, user_id}`. Publish the app
with the rule `{"path": "requests", "read": "view", "write": "interact"}` next to `maps` and `reports`.

Turning requests into pages (coordinator):

1. Read the collection: `ArtifactData` `list` (or `query`) on the app artifact's URL, collection `requests`. Save the
   result as JSON (any wrapper works: a list of docs, `{"docs": [...]}`, `{"documents": [{"id", "data"}]}`).
2. `python course_data/library/requests_to_batch.py requests.json --name req_nov01 --max 10`. It groups docs by
   OSM id (else state + slug), ranks courses by how many golfers asked (then by the earliest request), and skips
   courses that already have a library folder, request file, index entry or tournament folder. It writes
   `course_data/requests/course_page_<slug>.json` (`course_page/1`, with `osm` and `near` from the index, so resolve
   is not ambiguous) and `course_data/requests/course_batch_<name>.json`. `--dry-run` only prints the plan. Run it in
   a full checkout so the skip list sees every library folder.
3. Commit those files and push. One push starts one `course_page.yml` run. Push the next batch only after that run
   has started (see "Request" above). Requests are not deleted. A course whose page is built is skipped next time.

Docs are untrusted: the converter checks every field (state code, name length, `osm` pattern, coordinates inside
the US) and drops anything else.

## Files

| file | what |
|---|---|
| `national_index.py`, `us_courses.json.gz`, `us_readiness.json` | the national course index (above) and its readiness counts |
| `requests_to_batch.py` | app request docs -> course_page request files + a course_batch (above) |
| `course_page.py` | every stage (plan, pkgreq, configure, prepare, compute, finish, index) |
| `picture_checks.py` | the per-hole picture checks for one solved base |
| `weather.py` | forecast or climate normals |
| `gate_eval.py`, `gate/GATE.md` | blind gate builds of the hand-checked courses scored against their truth |
| `index.json` | the library index (above) |
| `../../.github/workflows/course_page.yml` | the workflow (plan, one `course_page_one.yml` call per course, index) |
| `osm_check.py`, `../../.github/workflows/osm_check.yml` | Overpass completeness counts for candidate courses |
