# TRAIN-BIG frozen bench inputs (routing bench, split "big")

These are copied from `cache/big/` as built by `route_big.py` (2026-11-17 / 2026-11-19), and committed because
they cannot be refetched reproducibly. OSM has been edited since, and the card sites change. The scenes, U-Net
probabilities and maps (`cache/v2root/big/{scenes,probs,maps}`, about 1 GB) are not here; they can be rebuilt from
free imagery.

* `courses/<slug>/osm_golf.geojson.gz`: the course's raw OSM features, including the golf=hole ways the bench
  scores against (the router never reads golf features). `course.json` is the resolved course (outline, bbox,
  tags). `scorecard.json` holds the web cards found then, plus `chosen` (route_bench.bench_card: production's pick
  by default, or `chosen` with ROUTE_BENCH_CARD=chosen). This is the same kind of data as
  `course_data/generalize/courses/`.
* `manifest.json`: the TRAIN-BIG candidate list. `status/<slug>.json`: build status per course (`ok` = in the bench)
  and timings.

route_big.BIG reads `$FASTPATH_CACHE/big` or `ROUTE_BIG_DIR`. On a fresh checkout, `refit/link_benchdata.sh` links
`cache/big/{courses,manifest.json,status}` (and the same paths under `cache/v2root/big`) to this folder.
