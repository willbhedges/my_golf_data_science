# Old Kinderhook: rebuild QA, mapper wave 2b (2026-11-03)

**Verdict: PUBLISH.** The card (club Championship column, 6,855, par 71) and the 9 / 15 tee fixes are still in, and
the mapper layers apply cleanly (37 zone edits on 12 holes, 0 tees moved). Every tee shot lands on fairway with 0-18%
trees / water / OB. The only CHECK is a tee-position CHECK on the 7th (par 3).

Page checked: `course_data/library/old_kinderhook/page.html`, GitHub Actions run 41539963949 (built 2026-11-02T23:54Z),
mapper layers `course_data/mapper/old_kinderhook/`. One solved set (Championship), a single-set page:
`qa_page.js` checked the page's own set. 18 holes, phone and desktop, 0 page problems, no console errors. I looked at
every phone hole picture.

## Checks

| check | result |
|---|---|
| Card / pars | source `request file yardages`; par 71; page yardage = card on all 18; measured within 5 yds except 9 (506 / 514) |
| Review fixes (`review.md`) | 15: OSM / supplement box, 405 measured / 402, 4-wood +2.5, fairway 88%, past the pond. 9: off the lidar pad in the woods, onto the hole-line start, 506 / 514, Driver +6.5 |
| Mapper layers | recovery adds on 1, 2, 4, 5, 9, 10, 12, 17, 18; OB add on 12 and 15; water erase on 8 (633 yd2). No long grass anywhere (mapper verdict: smooth mown rough both sides) |
| Aims past ±40 | none (largest +23, 14) |

## Holes

| hole | Championship | note |
|---|---|---|
| 1-6, 8, 10-18 | OK | tees on OSM / supplement boxes; yardage = card ±5 |
| 7 | OK (CHECK) | par 3, tee_axis 4 yds off the box, 147 / 152 |
| 9 | OK | 506 / 514 (as reviewed) |

## Next fix

None.
