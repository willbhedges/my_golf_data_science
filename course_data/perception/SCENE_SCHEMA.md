# Course scene schema (`course_scene/1`)

Owner: course perception (`course_data/perception/`). Consumers: hole-graph / sequence inference, routing,
vision gap-fill, QA. **This contract is stable**: fields are only ever added; a breaking change bumps the
schema to `course_scene/2` and both are written for a transition period.

The perception stage looks at a course bbox from first principles (NAIP 4-band imagery + USGS 3DEP lidar
HAG / classification / intensity / DTM) and outputs every structural element it can see, each with a
confidence `p`. It does **not** need a scorecard or any OSM golf mapping. OSM is used only (a) as training
labels / evaluation truth, and (b) optionally as hints in `mode: "osm_hints"` (never in `mode: "blind"`, which
is what every reported metric uses).

Two files per course, written side by side:

* `scene.json` - the structured scene (this document).
* `scene.geojson` - the same elements as one GeoJSON FeatureCollection (WGS84) for maps and for the
  routing code: every feature has `properties.class` (see table) **and the OSM-style tags routing already
  reads** (`golf=green|tee|fairway|bunker|water_hazard|cartpath|driving_range|clubhouse`, `building=yes`,
  `amenity=parking`), plus `id`, `p`, `src="perception:<model id>"`. So `routing.inputs_from_fc(scene_fc)`
  works unchanged.

Conventions: coordinates are `[lon, lat]` WGS84 (ARCHITECTURE section 2), rounded to 1e-7 deg; distances and
areas in metres / m2; bearings in degrees true (0 = north, clockwise); undirected axes in [0, 180).
`p` is a calibrated probability that the element is real and of that class (calibrated on held-out states,
see `REPORT.md`). Ids are stable within one scene only (`g3`, `t12`, `f4`, `b7`, `w2`, `c5`, `n40`, `e51`,
`bl3`, `pk2`); they are not stable across runs.

## Top level

```json
{"schema": "course_scene/1",
 "slug": "urbana_il", "name": "Urbana Country Club",
 "built_utc": "2026-10-17T05:00:00Z",
 "mode": "blind",                                  // "blind" (no OSM golf input) | "osm_hints"
 "bbox_wsen": [-88.21, 40.09, -88.19, 40.11],      // the area that was perceived (course bbox + margin)
 "grid": {"crs": "EPSG:32616", "res_m": 1.0, "width": 1820, "height": 2040,
          "transform": [1.0, 0, 398000.0, 0, -1.0, 4440000.0]},
 "sources": {"naip": {"year": 2023, "acquired": ["2023-07-14"], "res_m": 0.6},
             "lidar": {"hag": "3dep-lidar-hag", "classification": true, "intensity": true, "dtm": "3dep-lidar-dtm"},
             "models": {"segment": "ariadgolf-v4@abcd1234", "perception": "perception-v1@<git sha or date>"}},
 "coverage": {"lidar": 0.99, "naip": 1.0},          // share of the grid with valid data
 "greens": [...], "tee_complexes": [...], "fairways": [...], "bunkers": [...], "water": [...], "trees": [...],
 "cart_paths": {"nodes": [...], "edges": [...]},
 "buildings": [...], "parking": [...],
 "clubhouse": {...} | null,
 "practice": {"putting_greens": ["g19"], "driving_range": {...} | null},
 "relations": {"green_to_tee": [...]},
 "summary": {"greens_hole": 18, "greens_practice": 1, "tee_complexes": 19, "fairways": 14, "cart_path_km": 6.2, ...},
 "warnings": ["no lidar: tee pads from imagery only", ...]}
```

## Elements

Every polygonal element carries `id`, `p`, `centroid` `[lon, lat]`, `area_m2`, `polygon` (outer ring,
`[[lon, lat], ...]`, closed, simplified to ~0.5 m; holes dropped) and `src` (list of evidence names:
`segment` = NAIP U-Net, `lidar_pad`, `lidar_hag`, `lidar_class`, `naip_ndvi`, `naip_nir_water`, `osm_hint`).
Elevation fields are DTM metres (NAVD88) and absent without lidar.

### `greens[]`
| field | meaning |
|---|---|
| `kind` | `"hole"` (a putting surface some hole ends on) / `"practice"` (practice / putting green) / `"uncertain"` |
| `p` | P(it is a green of any kind) |
| `p_hole` | P(it is a hole's green, not practice), already multiplied by `p` |
| `p_practice` | P(practice green), already multiplied by `p`; `p_hole + p_practice <= p` |
| `collar_polygon` | ring ~2 m outside the putting surface (fringe), when the imagery shows it |
| `elev_m`, `raised_m` | mean DTM height; height above the 15-40 m surround (greens are often built up) |
| `slope_pct` | mean surface slope |
| `tees_in_range` | number of tee complexes 80-600 m away (a hole green has >= 1; practice greens often 0) |
| `dist_clubhouse_m` | distance to the clubhouse point, null if none |

### `tee_complexes[]`
One complex per hole start: all individual tee boxes of one hole clustered together (boxes within ~35 m that
line up along a common axis).

| field | meaning |
|---|---|
| `boxes` | `[{"id": "t3.1", "centroid", "polygon", "area_m2", "p", "src": ["segment", "lidar_pad"]}]` (front to back is not ordered) |
| `centroid`, `polygon` | centroid / convex hull of the boxes |
| `axis_deg` | undirected long axis of the complex (boxes of one hole line up along the line of play), null for a single round box |
| `length_m` | extent along `axis_deg` (back box to front box) |
| `p` | P(this is a real tee complex of a hole) |
| `p_range_tee` | P(it is the driving-range hitting area instead) |
| `elev_m` | mean DTM |

### `fairways[]`
| field | meaning |
|---|---|
| `centerline` | `[[lon, lat], ...]` medial-axis polyline end to end (the longest skeleton path, smoothed) |
| `length_m`, `width_m` | along the centreline; median width |
| `axis_deg` | undirected bearing of the end-to-end chord |
| `ends` | the two centreline ends `[[lon, lat], [lon, lat]]` (direction of play is unknown here) |
| `stripe_deg` | dominant mowing-stripe orientation (undirected) from the NAIP texture, null when not visible; on most courses stripes run along the line of play |
| `stripe_strength` | 0-1 coherence of that orientation |

### `bunkers[]`, `water[]`
Polygons; `water[].kind` = `"pond"` / `"stream"` (elongated, width < 15 m).

### `trees[]`
Canopy clusters from lidar HAG >= 4 m (NAIP NDVI + texture without lidar): `polygon`, `area_m2`,
`height_m` (p90), `kind` = `"stand"` (>= 400 m2) / `"tree"`. Small, lone trees are kept (they shape holes).

### `cart_paths`
A graph. Paved / gravel paths 1.5-4 m wide, detected per pixel, skeletonised, gaps <= 12 m bridged.

```json
{"nodes": [{"id": "n4", "ll": [lon, lat], "degree": 3, "kind": "junction" | "end" | "bend",
            "near": {"green": "g7", "tee": null, "building": null, "parking": null}}],
 "edges": [{"id": "e9", "u": "n4", "v": "n5", "length_m": 182.3, "line": [[lon, lat], ...], "p": 0.83,
            "width_m": 2.6, "surface": "paved" | "gravel" | "unknown"}],
 "total_km": 6.2, "components": 3}
```
`near` links a node to an element within 25 m (green: within 30 m of the green edge).

### `buildings[]`, `parking[]`
Buildings: `height_m` (lidar), `p`, `polygon`. Parking: large, flat, low-NDVI paved areas (>= 400 m2) with
`p` and `polygon`; `n_stall_lines` when stripes are visible (0 when not measured).

### `clubhouse`
```json
{"ll": [lon, lat], "building": "bl2", "p": 0.8, "radius_m": 60,
 "evidence": {"parking": "pk1", "putting_green": "g19", "range": true, "cart_paths_converge": 4}}
```
`radius_m` is the expected localisation error (from validation).

### `practice`
`putting_greens` lists green ids with `kind == "practice"`. `driving_range` =
`{"polygon", "centroid", "axis_deg", "hitting_end": [lon, lat], "length_m", "width_m", "p", "tee_complex", "fairway"}`
or null (`tee_complex` / `fairway`: the element ids the range was found from, either may be null).

### `relations.green_to_tee`
Ordering evidence for the hole-graph inference. One entry per (green, tee complex) pair within 450 m:

```json
{"green": "g7", "tee": "t8", "dist_m": 96.0,
 "path_m": 120.5,           // shortest cart-path route green -> tee (null when the graph does not connect them)
 "path_edges": ["e9", "e10"],
 "path_direct": true,       // the route passes no other green / tee complex on the way
 "aims_at_green": false,    // the complex's long axis points at this green (likely the green's OWN hole tee)
 "p_next": 0.71}            // perception's own P(tee is the next hole's tee after this green); a prior only
```
`p_next` uses only geometry + cart paths (distance, path detour, whether the tee's axis points away from
the green); the sequence agent should treat it as a likelihood term, not a decision.

## Evaluation file (`eval.json`, when OSM labels exist)
Per course and pooled, from `course_data/perception/evaluate.py` (definitions in `REPORT.md`):
`greens {tp, fp, fn, precision, recall, practice_confusions}`, `tee_complexes {recall, precision}`,
`fairways`, `bunkers`, `water`, `cart_paths {length_precision, length_recall, connectivity_acc}`,
`buildings`, `clubhouse {error_m}`, `driving_range {hit}`.

## Where the files are

Actions (`perception.yml`) commits, per course, `course_data/perception/scenes/<slug>/scene.json.gz` (gzipped
`scene.json`; `scene.geojson` is not committed: rebuild it with `scene.to_geojson(scene)`) and `eval.json`.
`perceive.py <stack dir> --out DIR` writes the uncompressed pair locally.

## How to read it

```python
import gzip, json
scene = json.load(gzip.open("course_data/perception/scenes/<slug>/scene.json.gz"))
hole_greens = [g for g in scene["greens"] if g["kind"] == "hole"]
complexes = sorted(scene["tee_complexes"], key=lambda t: -t["p"])
nxt = [r for r in scene["relations"]["green_to_tee"] if r["path_m"] is not None]
```
