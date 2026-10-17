# Zero-tap workstream B: outside evidence of which hole is which

Plan: `course_data/ZERO_TAP_PLAN.md` (workstream B). Results: `results.json`, `osm_ref_population.json`,
per-course evidence in `courses/<slug>.json`. Findings: section 3 (filled from the latest run).

## 1. Contract: `hole_evidence/1`

One file per course, `courses/<slug>.json`:

```json
{
  "schema": "hole_evidence/1",
  "slug": "skokie_il", "name": "Skokie Country Club", "split": "test",
  "sources": ["osm_feature_ref", "website_hole_image"],
  "holes": {
    "7": [
      {"role": "green", "point": [lon, lat], "source": "osm_feature_ref",
       "url": "https://www.openstreetmap.org/way/123", "confidence": 0.95},
      {"role": "footprint", "footprint": [[lon, lat] x4], "tee": [lon, lat], "green": [lon, lat],
       "source": "website_hole_image", "url": "<image url>", "page": "<page url>",
       "inliers": 57, "confidence": 0.84},
      {"role": "label", "point": [lon, lat], "source": "website_map_ocr", "url": "<image url>",
       "inliers": 40, "ocr_conf": 91, "confidence": 0.7}
    ]
  }
}
```

Keys of `holes` are hole numbers (strings, "1".."18"). Each item is one piece of evidence:

| role | meaning | how a consumer uses it |
|---|---|---|
| `green` / `tee` | a point that is the green (or tee) of this hole | snap to the nearest candidate green / tee complex within ~40 m |
| `label` | a hole-number label placed on the ground (OCR from a registered map) | the nearest hole corridor (tee-green segment) within ~60 m is this hole |
| `footprint` | ground quad of a registered per-hole image; `tee`/`green` are the image's bottom/top centre (hole-image convention, weak) | the hole whose tee-green line lies mostly inside the quad is this hole |

`confidence` is the source's P(item is right) before fusion; for registered images it is a function of RANSAC
inliers (`evaluate.py: reg_confidence`), for OSM refs a constant measured in `results.json`. Workstream C
should treat items from one `url` as correlated (one registration).

Rules kept: robots.txt honoured for our UA token and `*`, >= 1 s between requests per host, pages capped at 40
per course, no images or page text stored in the repo, only derived positions and the source URL.

## 2. Sources and how they are measured

| source | code | what |
|---|---|---|
| `osm_feature_ref` | `evaluate.py: ev_osm_ref`, `osm_ref_population.py` | OSM golf=green / pin / tee carrying their own `ref` (independent of golf=hole lines) |
| `website_hole_image` | `probe.py` crawl + `NaipFeatures.match` (v1), `register.py: register` (v2) | per-hole images on the course site (hole number from file name / alt / page URL). v1: global RootSIFT + MAGSAC homography to NAIP 0.6 m. v2: exhaustive rotation x ground-resolution NCC search (gradient + excess-green) at 1.8 m, top hypotheses verified by local RootSIFT |
| `website_hole_image_pairmatch` | `register.py: match_corridors` | per-hole image vs. each candidate tee-green corridor (NAIP pulled into the image frame, NCC); here scored with the TRUE pairs as candidates (`oracle_pairs`), an upper bound |
| `website_map_ocr` / `scorecard_pdf_map_ocr` | `probe.py: ocr_numbers` | overview map / scorecard PDF page registered to NAIP, tesseract digits 1-18 placed on the ground |
| `golfify`, `opengolfapi` | `probe.py: golfify_probe, opengolfapi_probe` | free JSON scanned for any per-hole coordinates |
| hole signs in imagery | (argument, section 3) | |

Truth: the zero-tap benchmark (`course_data/zero_tap/BENCH.md`, `truth/<slug>.json`, 161 in-bench courses, dev /
test split by state); the 27 generalize validation courses outside the benchmark are reported as `offbench`
(OSM golf=hole lines). Accuracy = share of scored items whose nearest truth hole has the claimed number;
coverage = share of courses (holes) with any evidence.

Run: commit `requests/evidence_probe_<name>.json` (see `.github/workflows/zero_tap_evidence.yml`; the newest
committed request wins), then `python course_data/zero_tap/evidence/evaluate.py --run runs/val1 --run runs/bench1
--run runs/v2`. Runs: `val1` (82 generalize validation courses, crawl + v1 registration), `bench1` (the other 106
benchmark courses), `v2` (registrar v2 + corridor matching on the candidate images of both).

## 3. Findings (188 courses: 161 benchmark + 27 off-bench)

**Verdict: outside evidence does not carry zero-tap.** One source is accurate but rare (OSM refs); the
large-coverage hope (course websites registered to NAIP) produced no usable evidence; the free hole-data APIs
carry no per-hole coordinates.

| source | courses with evidence | hole coverage | accuracy |
|---|---|---|---|
| `osm_feature_ref` (dev) | 12 / 77 (15.6 %) | 13.9 % | 98.2 % (325 / 331) |
| `osm_feature_ref` (test, reported once) | 10 / 84 (11.9 %) | 7.9 % | 96.5 % (251 / 260) |
| `website_hole_image` (v1 + v2 registration) | 0 / 161 | 0 | - (0 of 337 candidate images, 0 of 1 814 v1 tries registered) |
| `website_hole_image_pairmatch`, oracle pairs (all) | 15 / 161 | 2.7 % | 10.5 % (11 / 105; chance about 6 %) |
| golfify JSON | 55 pages, 0 with hole coordinates | 0 | - |
| OpenGolfAPI detail | 144 courses; hole geometry fields exist but are null on every course | 0 | - |

1. **OSM green / tee / pin refs** are the one real signal: about 97 % right where present. But they sit almost
   only on courses that already have golf=hole lines (`osm_ref_population.json`: 4.5 % of 2 986 courses in 10
   states carry ref'd greens; of courses WITHOUT hole lines only 1 % do in that run, 4.5 % in the earlier run
   that covered IL / WI, concentrated in IL (23) and WI (20)). The benchmark's `osm_card` tier hides these refs,
   so they add nothing there; for unmapped-line courses in production they are worth reading (cheap, ~97 %) but
   reach a few percent of courses.
2. **Course websites**: 162 / 188 have a site, 121 reachable, 18 robots-blocked at the home page. Per-hole
   images for >= 9 holes on only 8 courses (21 with any), 25 with a layout map, 42 with PDFs (mostly scorecards,
   rules, menus). The images are artwork, drone obliques, flyover stills or GPS-app renders.
   - v1 global RootSIFT to NAIP: every high-inlier "match" was a degenerate homography (0 sane).
   - v2 (coarse NCC search + local SIFT verification) recovers synthetic NAIP crops exactly (3 / 4, rotation and
     scale unknown, colour-shifted) but registered 0 real website images, and 1 / 23 of the Spirit Hollow
     18Birdies screenshots (the one with a near-nadir, same-season look). Season / sensor / render differences
     plus oblique views defeat feature matching at 0.6 m.
   - Corridor matching (does this hole image look like corridor k?) even with the true tee-green pairs as the
     only candidates: 11 / 105 top-1 (chance ~6 %), 45 / 121 in the top 6, and the margin is not calibrated
     (top margins are wrong more often than right). On Spirit Hollow screenshots: 8 / 23 top-1. Not usable as
     evidence for workstream C.
3. **Hole signs / tee markers in imagery**: not attempted beyond the argument: NAIP at 0.6 m cannot resolve a
   hole sign (< 1 m), and no free sub-0.3 m imagery covers the benchmark consistently.

What would change the verdict: a source with per-hole coordinates (a GPS-app API under licence; OpenGolfAPI
fills `tee_coords` / `green` later), or a per-course human tap. Neither is free outside evidence.
