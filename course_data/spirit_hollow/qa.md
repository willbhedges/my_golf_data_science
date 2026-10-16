# QA: Spirit Hollow Golf Course, black tees (2026-10-16T18:42Z)

| hole | par | yds | score | band | OSM | imagery | inferred | flags |
|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 391 | 0.76 | check the flags | 41% | 0% | 59% | tee: tee stage: black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 5 | 501 | 0.77 | check the flags | 42% | 0% | 57% | tee: tee stage: black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 3 | 148 | 0.93 | auto | 100% | 0% | 0% | tee: tee stage: black tee_axis |
| 4 | 5 | 529 | 0.75 | check the flags | 34% | 0% | 66% | tee: tee stage: black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 4 | 383 | 0.78 | check the flags | 47% | 0% | 53% | tee: tee stage: black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 4 | 409 | 0.76 | check the flags | 38% | 0% | 62% | tee: tee stage: black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 3 | 154 | 0.93 | auto | 100% | 0% | 0% | tee: tee stage: black tee_axis |
| 8 | 4 | 385 | 0.77 | check the flags | 42% | 0% | 58% | tee: tee stage: black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 9 | 4 | 368 | 0.71 | check the flags | 21% | 0% | 79% | tee: tee stage: black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 5 | 501 | 0.80 | check the flags | 52% | 0% | 48% | tee: tee stage: black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 341 | 0.73 | check the flags | 28% | 0% | 72% | tee: tee stage: black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 3 | 184 | 0.93 | auto | 100% | 0% | 0% | tee: tee stage: black tee_axis |
| 13 | 4 | 412 | 0.79 | check the flags | 37% | 0% | 63% | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 4 | 395 | 0.75 | check the flags | 36% | 0% | 64% | tee: tee stage: black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 3 | 144 | 0.93 | auto | 100% | 0% | 0% | tee: tee stage: black tee_axis |
| 16 | 4 | 379 | 0.74 | check the flags | 31% | 0% | 69% | tee: tee stage: black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); OB from the course boundary on 6% of the landing zone |
| 17 | 4 | 446 | 0.76 | check the flags | 38% | 0% | 62% | tee: tee stage: black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 5 | 521 | 0.80 | check the flags | 40% | 0% | 60% | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

Stages:

- **osm**: ok: course_data/spirit_hollow/osm.geojson
- **scorecard**: ok: course_data/tees/scorecard.json
- **tees**: ok: course_data/tees/tee_positions.json (set 'black'; card yardage -> box where the file has no point)
- **vision**: missing (no gap-fill layers)
- **geometry**: geometry/build_holes.py:build
- **images**: ok: imagery/render.py:render_hole (18/18)
