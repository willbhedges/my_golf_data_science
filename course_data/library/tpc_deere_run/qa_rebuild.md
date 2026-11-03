# TPC Deere Run: rebuild QA, mapper wave 2c (2026-11-03)

**Verdict: PUBLISH.** The mapper's three tee moves are on the page. 9 Black is now 480 = card, on a visible box in the
Gold complex, no longer on a green complex. 13 White and Red are on their pads (those sets are not solved). The native
grass added on 5, 9, 10 and 11 is in the layers. One known caveat remains: the 6 Black Driver over the dogleg corner,
which now carries an aim CHECK.

Page checked: `course_data/library/tpc_deere_run/page.html`, GitHub Actions run 41554623184 (package built
2026-11-03T01:38Z). Mapper layers: `course_data/mapper/tpc_deere_run/` (7 zone edits on 4 holes, 3 tees moved, 90
checked). Both solved sets (Gold 7,267, Black 6,984, par 71) were run through `qa_page.js`: 18 holes each, phone and
desktop, 0 page problems, no console errors. I looked at every phone hole picture, plus 6, 9 and 13 Black closer up.

## Mapper edits

| edit | on the page? |
|---|---|
| 9 Black moved 47 yds onto the visible box (agent tee, 480) | **yes.** Measured 480 = card. The marker is on a tee pad at the start of the hole. Driver -1.5, fairway 58% |
| 13 White / Red onto their pads (351 / 325) | in the package; those sets are not on the page. 13 Black (411) and Gold (424) are unchanged on OSM 681512536 |
| native: 5 (1,506 sq yds), 9 (3,349), 10 (11,240), 11 (3,153) | yes. 10 shows long grass 2-3% in the Driver pattern. On 5, 9 and 11 the native sits outside the picked landing ovals (fairway 58-77%) |

## Holes

| hole | Gold | Black | note |
|---|---|---|---|
| 1-3, 5, 8, 10-12, 14, 16, 17 | OK | OK | measured = card ±1 on every hole-set; par-3 boxes on the green |
| 4 | OK (marginal) | OK (marginal) | Driver +22 / +26.5, trees 24-32% (right tree line). Model choice |
| 6 | OK | **pick doubtful (CHECK)** | Black Driver +33 over the corner, fairway 1%, trees 21%, 75 yds in. The aim CHECK ("lands 307 yds out in rough") is now printed. Gold plays 4-wood. Not blocking, as on 2026-11-02 |
| 7 | OK (CHECK) | OK (CHECK) | lidar pad 21-26 yds from the OSM box; tee CHECK printed, as reviewed |
| 9 | OK | OK (**fixed**) | Black 480 from the mapper's box |
| 13, 15 | OK | OK | |
| 18 | OK (tie) | OK | Gold Driver -40 (on the bound, not past it), fairway 53%. Black 4-wood -12 |

No aim is past ±40.

## Next fix

None blocking. Solver: 6 Black Driver over the corner (fairway 1%).
