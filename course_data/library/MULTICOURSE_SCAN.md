# Multi-course scan: library pages built as a mix of two courses (2026-11-03)

Commit dab692c65 added `sanity.split_courses` / `course_groups` (in `clean_osm`, before `select_hole_ways`). Before
it, a facility mapped as one OSM outline with refs 1-18 more than once had one way kept per ref. That could build a
MIX of courses. This scan lists the library pages where the old and new logic pick different hole ways.

## Method

1. **Committed raw OSM**: all 417 OSM caches in the repo. That is `packages/*/raw/osm.geojson` (41),
   `ob/*/raw/osm.geojson` (38), mozingo, spirit_hollow, `structure/data/*` (131), `zero_tap/data/*` (189) and
   `generalize/courses/*` (97). The library keeps no raw OSM: only `raw/course.json` and `raw/summary.json` are
   committed. Each cache was run through `clean_osm` twice, once with the pre-dab692c65 `sanity.py` and once with the
   current one, using the same names and near point as the request. The kept golf=hole ways were then compared. The
   structure and zero_tap caches carry no `inside_course` flags, so these were recomputed with
   `fetch_course.summarise` from each cache's own `course.json` boundary.
2. **Library pages without raw OSM**: each `library/<slug>/raw/summary.json` lists every golf=hole way in the fetch
   box (ref, name, osm id). `split_courses` acts only when at least 6 plain refs repeat, so a page whose summary has
   fewer than 6 repeated refs cannot change. That covers every library page except 14. For those 14, current OSM was
   fetched with `webfetch_multicourse_scan_osm.json` (OSM API map tiles over each page's own fetch box), committed by
   Actions to `course_data/research/web/multicourse_scan_osm/`. The `inside_course` flags were rebuilt from the
   page's `raw/course.json` boundary. Each **built page hole line** (`package.json` `hole_line_ll`) was matched to
   its OSM way (start points coincide within 0 yds on most pages; worst cases 12, 28 and 58 yds) and compared with
   the new pick.
3. **Published**: the "Published" lines in `course_data/MANAGER_TODO.md`.

**Caveat (not verified)**: replaying the *old* `clean_osm` on today's OSM does not always reproduce the built page.
TPC Sawgrass differs on 6 holes, and downstream stages (tee and routing) also move holes. The table below therefore
compares the page **as built** with what the new logic keeps. No page was rebuilt or rescored here.

## Result: library pages built as a mix (rebuild needed)

None of these pages is published. Every one is "needs confirm", except grand_national_links, which is "blocked".

| slug | request names | built page (old logic) | new logic keeps | holes that change | published |
|---|---|---|---|---|---|
| tpc_sawgrass | TPC Sawgrass Stadium | **16 Valley + 2 Stadium (11, 18)** | Stadium 18 (named: hole names "Stadium N" / "Valley N") | 16 | no |
| bandon_dunes | Bandon Dunes | **17 Old Macdonald + 1 Bandon Dunes (5)** | Bandon Dunes 18 (named: hole names; Pacific Dunes 18 and Old Macdonald 18 dropped) | 17 | no |
| tpc_harding_park | TPC Harding Park | **1-9 Fleming nine + 10-18 Harding** | Harding 18 (largest chain; CHECK note, no name decides) | 9 | no |
| sand_hollow | Sand Hollow Championship Course | **1-9 Links nine + 10-18 Championship** | Championship 18 (largest chain, "champion" names; CHECK note) | 9 | no |
| longview_lake | Fred Arbanas Golf Course | **1-9 from the 9-hole course + 10-18** | the 18-hole chain (largest; CHECK note) | 9 | no |
| seneca | Seneca Golf Course | **1-9 from the extra nine + 10-18** | the 18-hole chain (largest; CHECK note) | 9 | no |
| grand_national_links | Grand National Links Course | **27 holes: 12 Links + 6 Lake (3, 5, 6, 8, 15, 16) + 9 from ref-less ways** | Links 18 (near point; the Lake chain carries golf:course:name=Lake) **plus 17 ref-less hole ways kept** | 6 + the 9 extras | no (blocked) |

Rebuild after review: **tpc_sawgrass, bandon_dunes, tpc_harding_park, sand_hollow, longview_lake, seneca**.
**grand_national_links** should wait for the fix below. No course_page request was pushed.

## Multi-course facilities where the new logic does NOT build a clean single course

- **grand_national_links** (Links / Lake / Short): `split_courses` correctly keeps the Links 18 and drops the Lake 18.
  The 17 golf=hole ways with no ref and no number in their name are probably the Short Course. They are not in any
  group, so they survive (`new_n` = 35 hole ways). The old build turned 9 of them into holes 19-27, so a rebuild
  would still not be a clean 18. Fix: when a split happens, drop hole ways with no ref that fall in no kept group.
- **paa_ko_ridge** (27 holes, three nines): **a regression; do not rebuild yet.** OSM has three sub-course outlines,
  "Paa-ko Ridge 1-9", "10-18" and "19-27", with refs 1-9, 10-18 and 10-18. `course_groups` treats each nine as a
  course and keeps "the largest", so it keeps **9 holes** (the 10-18 nine). The old page was 18 holes: the 1-9 nine
  plus the 19-27 nine (built holes 10-18 = the 19-27 ways). Fix: merge nine-hole sub-outlines whose refs do not
  overlap (1-9 + 10-18) into one 18, and then pick between them.
- **oxmoor_valley** (Ridge / Valley, request "Oxmoor Valley Ridge"): the old and new picks agree with the built page.
  It is one course, not a mix. OSM names neither chain, so the new logic keeps the first of two equal 18s, with a
  CHECK note. Measured hole-line totals are 7,074 yds for the kept course and 7,288 for the other. That suggests the
  kept one is Ridge, but this is from memory of the cards and **not verified**.
- **bobby_jones** (9-hole reversible, mapped as two 9-hole routings): the new logic keeps the 9-way chain the page
  already uses. No change.
- **bethpage_state_park**: OSM maps only 3 Black holes. `normalize_hole_refs` (refs "Black - N"), not
  `split_courses`, handles it. No clean course is possible from OSM.
- **gate/gate_national_kc** (National KC, 27 holes): OSM has 2 hole ways, so `split_courses` never acts. The 27
  holes come from structure inference and are still not a clean 18.
- **pinehurst, neshanic_valley, old_works**: qualified refs ("1 - #2", "L4", "Practice N") are handled by
  `normalize_hole_refs`, so they are unaffected by dab692c65.
- **queenstown_harbor, troon_north**: no library page exists (status failed). They are the fix's own test cases and are
  being rebuilt in run 41580200431. The note in MANAGER_TODO not to publish the Troon page from run 41567617061 still
  applies.

Repeated refs, but the new logic does not change the page: **forest_dunes, gamble_sands, rebsamen, torrey_pines**.
The repeats are a neighbouring course outside the page's boundary, so `split_courses` does not act.
**buffalo_ridge** (published) was checked on the committed package OSM and its summary: no change. Pages with fewer
than 6 repeated refs cannot change: harbour_town 4, caledonia 4, pevely_farms 4 (published), wolf_creek 5,
crosswater, hodge_park (published), royal_new_kent and ironhorse 1, and every other library page. **No published
page is affected.**

Library pages with no summary (status failed, never built): deer_creek_op, keller, kokopelli,
lake_of_the_woods_como, theodore_wirth, gate_pine_dunes. These could not be checked.

## Committed raw OSM caches (not library pages)

None of the 41 package caches or 38 ob caches, nor mozingo or spirit_hollow, change. On the other caches, 19 change
(generalize 4, structure 7, zero_tap 8). Two patterns are worth a look before more 27/36-hole courses go through the
library:

- **Nines mapped twice** (a 9-hole course mapped as front + back nines with refs 1-9 on both): mascoutin_wi,
  lake_venice_fl, hunt_valley_md, fox_hills_mi, boulder_creek_nv. Old and new each keep 9 ways, but different ones.
- **A 27-hole facility split into 18 + 9 by chains**: atkinson_resort_nh, fargo_nd, crescent_farms_mo. The new logic
  keeps the 18. With hole-name groups (carillon_il white / red / blue, del_rio_ca river / bluff, willowbend_ma
  bay / bog / bend), a single nine is kept where the card is a pair of nines: the same issue as Paa-Ko.
- dismal_river_ne (two unnamed 18s, Red / White): 16 refs change and the largest group is kept with a CHECK note.
  tumble_brook_ct goes from 9 kept ways to 12. Small 1-2 hole swaps on chains (newcastle_wa, ponkapoag_ma,
  toscana_ca, isabella_ar, spurwing_id, greenbrier_meadows_wv) were not checked by hand.
