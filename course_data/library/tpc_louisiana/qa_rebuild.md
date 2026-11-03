# TPC Louisiana: rebuild QA, club scorecard (2026-11-03)

**Verdict: PUBLISH.** This is the first build with the club card (`card_review.json`, tpc.com PDF). PGA TOUR is
7,425 and Black 6,931, par 72. Every tee measures the card ±5. The internal set name and the no-card wording are
gone. The expected yardage CHECKs on 3, 9, 16 and 18 did not fire. On each of those holes the tee localizer found
a spot at the card yardage on a mapped teeing ground or a lidar pad. The card is the right side on all four (below),
so no `review.json` tee fix is needed.

Page checked: `course_data/library/tpc_louisiana/page.html`, GitHub Actions run 41569861705 (package built
2026-11-03T03:34Z). No mapper layers (none made for this course). The two solved sets (PGA TOUR, Black) were run
through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems, no console errors. I looked at every phone
hole picture. I also drew each set's tee on the page's own hole images for 2, 6, 12, 13, 16 and 18.

## Wording

- `osm_back` and "Back tees (from the map)" appear nowhere in `page.html`. The labels read "from the PGA TOUR tee"
  and "from the Black tee".
- "N on the card" appears only on the par-3 badges, and each one is the real card number: 3 221/167, 9 207/195,
  14 216/192, 17 215/172. "to the middle" exists only inside the template's `D.no_card` branch, which is not used here.

## OSM tee vs card (3, 9, 16, 18)

The OSM figures in the brief were measured from the tee box nearest each hole-line start (the no-card build). Most
OSM tees here are long Dye-style strips, so a single box covers several sets.

| hole | OSM (no-card build) | card PGA TOUR / Black | page tee | which is right |
|---|---|---|---|---|
| 3 | 176 | 221 / 167 | PGA TOUR on the hole-line start (220 straight), at the back of strip 340813495; Black 53 yds forward on the same strip | **card.** The strip runs from about 226 down to about 135. The 176 was a mid-strip box, not the back. The par-3 picture shows only the green, so the tee is not checked on the photo |
| 9 | 232 | 207 / 195 | PGA TOUR 26 yds in front of the line start, on strip 340813596 (box error 0); Black 12 yds in front of that | **card.** The 232 is the back end of the same long strip, not a separate tee. The tips marker on the card is 25 yds up it. Not checked on the photo (green-only picture) |
| 16 | 432 | 355 / 340 | PGA TOUR on a lidar pad at the back of the visible long tee strip (page picture), 13 yds behind OSM box 340816265, where Black-Green are | **card.** The tee is on the visible strip. The OSM line starts 84 yds farther back, on a box at 423-432, with another box at 394. That box is 76 yds from the 10 green and 86 from the 15 green, outside the page picture. It may be an extra tournament tee or another hole's; not resolved |
| 18 | 558 | 585 / 565 | PGA TOUR 30 yds behind the line start, inside strip 340816273 (box error 0; OSM tee options include 582); Black/Blue at the line start | **card.** On the page picture the PGA TOUR dot is at the back of the long tee strip beside the lake. The 558 was the line start (the Black/Blue end) |

All four holes are right on the page. There is no wrong box to fix.

## Holes

| hole | PGA TOUR | Black | note |
|---|---|---|---|
| 1, 2, 4-7, 10-12, 15, 17, 18 | OK | OK | measured = card ±5 (2 PGA 543 / 548); fairway 39-82% in every landing pattern, aims within ±16 |
| 3, 9, 14, 17 | OK | OK | par-3 boxes on the green; badges = card |
| 8 | OK | OK | 4-wood (Black calm Driver) |
| 12 | OK (marginal) | OK (marginal) | Driver straight, sand 13-17%, trees 17-19% (the left waste bunker and trees) |
| 13 | OK | caveat | Black Driver -40.0 (pinned on the ±40 bound, window -40 to -38.5) across the waste-bunker corner. Fairway 67%, sand 13%, 37 yds in. Exactly 40, so no wide-aim CHECK. Same solver pattern as Weaver 10. PGA TOUR Driver +2.5 is clean. The Black tee is about 6 yds left of the visible strip. Minor |
| 16 | OK (CHECK) | OK (CHECK) | PGA TOUR: long iron on the line, fairway 76%, lidar-pad tee CHECK printed. Black: Driver +52 (calm +59) across the dogleg-right toward the green, fairway 44%, trees 16%, water 11%; wide-aim CHECK printed |

## Next fix

None blocking. Optional: identify the OSM box at 423-432 behind 16 (another hole's tee, or a tournament tee not on
the card) when imagery for the course is in the repo. Its line start currently begins there; the page does not use it.
