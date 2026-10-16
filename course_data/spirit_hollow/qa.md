# QA: Spirit Hollow Golf Course, black tees (2026-10-16T19:23Z)

| hole | par | yds | score | band | OSM | imagery | inferred | flags |
|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 391 | 0.79 | check the flags | 41% | 11% | 48% | tee: tee stage: black tee_axis |
| 2 | 5 | 501 | 0.78 | check the flags | 42% | 5% | 52% | tee: tee stage: black tee_axis |
| 3 | 3 | 148 | 0.93 | auto | 100% | 0% | 0% | tee: tee stage: black tee_axis |
| 4 | 5 | 529 | 0.78 | check the flags | 34% | 14% | 51% | tee: tee stage: black tee_axis |
| 5 | 4 | 383 | 0.81 | auto | 47% | 14% | 39% | tee: tee stage: black tee_axis |
| 6 | 4 | 409 | 0.76 | check the flags | 38% | 2% | 60% | tee: tee stage: black tee_axis |
| 7 | 3 | 154 | 0.93 | auto | 100% | 0% | 0% | tee: tee stage: black tee_axis |
| 8 | 4 | 385 | 0.77 | check the flags | 42% | 0% | 58% | tee: tee stage: black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 9 | 4 | 368 | 0.74 | check the flags | 21% | 18% | 62% | tee: tee stage: black tee_axis |
| 10 | 5 | 501 | 0.80 | auto | 52% | 4% | 44% | tee: tee stage: black tee_axis |
| 11 | 4 | 341 | 0.78 | check the flags | 28% | 24% | 48% | tee: tee stage: black tee_axis |
| 12 | 3 | 184 | 0.93 | auto | 100% | 0% | 0% | tee: tee stage: black tee_axis |
| 13 | 4 | 412 | 0.81 | auto | 37% | 12% | 51% |  |
| 14 | 4 | 395 | 0.76 | check the flags | 36% | 7% | 57% | tee: tee stage: black tee_axis |
| 15 | 3 | 144 | 0.93 | auto | 100% | 0% | 0% | tee: tee stage: black tee_axis |
| 16 | 4 | 379 | 0.78 | check the flags | 31% | 22% | 47% | tee: tee stage: black tee_axis; OB from the course boundary on 2% of the landing zone |
| 17 | 4 | 446 | 0.77 | check the flags | 38% | 6% | 56% | tee: tee stage: black tee_axis |
| 18 | 5 | 521 | 0.81 | auto | 40% | 7% | 53% |  |

Stages:

- **osm**: ok: course_data/spirit_hollow/osm.geojson
- **scorecard**: ok: course_data/tees/scorecard.json
- **tees**: ok: course_data/tees/tee_positions.json (set 'black'; card yardage -> box where the file has no point)
- **vision**: ok: course_data/imagery/spirit_hollow/gapfill.geojson, course_data/imagery/spirit_hollow/naip_trees.geojson
- **geometry**: geometry/build_holes.py:build
- **images**: ok: previous render (--no-images) (18/18)
