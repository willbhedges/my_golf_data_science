# QA: Spirit Hollow Golf Course, white tees (2026-10-16T18:23Z)

| hole | par | yds | score | band | OSM | imagery | inferred | flags |
|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 419 | 0.59 | needs review | 36% | 0% | 64% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 5 | 530 | 0.60 | check the flags | 39% | 0% | 61% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 3 | 175 | 0.77 | check the flags | 100% | 0% | 0% | tee: tee nearest the hole-line start |
| 4 | 5 | 595 | 0.59 | needs review | 36% | 0% | 64% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 4 | 457 | 0.64 | check the flags | 53% | 0% | 47% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 4 | 451 | 0.60 | check the flags | 41% | 0% | 59% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 3 | 120 | 0.77 | check the flags | 100% | 0% | 0% | tee: tee nearest the hole-line start |
| 8 | 4 | 427 | 0.60 | needs review | 39% | 0% | 61% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 9 | 4 | 393 | 0.58 | needs review | 33% | 0% | 67% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 5 | 563 | 0.64 | check the flags | 54% | 0% | 46% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 345 | 0.57 | needs review | 27% | 0% | 73% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 3 | 203 | 0.77 | check the flags | 100% | 0% | 0% | tee: tee nearest the hole-line start |
| 13 | 4 | 479 | 0.60 | check the flags | 40% | 0% | 60% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 4 | 466 | 0.57 | needs review | 28% | 0% | 72% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 3 | 156 | 0.77 | check the flags | 100% | 0% | 0% | tee: tee nearest the hole-line start |
| 16 | 4 | 392 | 0.58 | needs review | 34% | 0% | 66% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); OB from the course boundary on 1% of the landing zone |
| 17 | 4 | 486 | 0.60 | check the flags | 40% | 0% | 60% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 5 | 551 | 0.59 | needs review | 36% | 0% | 64% | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

Stages:

- **osm**: ok: course_data/spirit_hollow/osm.geojson
- **scorecard**: missing
- **tees**: no yardages: OSM tee nearest the hole-line start; tees/place_tee.py available (not yet wired into geometry)
- **vision**: missing (no gap-fill layers)
- **geometry**: geometry/build_holes.py:build
- **images**: ok: imagery/render.py:render_hole (18/18)
