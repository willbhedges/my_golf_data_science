# Swope Memorial Golf Course: rebuild QA (2026-11-02)

**Verdict: BLOCKED** on the 2026 card. The rebuild itself is right: holes 3-9 now sit on the correct OSM holes, and every
hole matches the pre-renovation card. But the club's own site now says the restored course is **6,324 yds, par 71**,
while the page (and every third-party card) says Blue 6,274, **par 72**. At least one par and several yardages changed
in the 2025-26 restoration, so the page cannot be published until the 2026 card is read.

Page checked: `course_data/library/swope_memorial/page.html`, built 2026-11-02T03:11Z. Both solved sets (Blue 6,274,
White 5,770, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at every
phone hole picture.

## Review fixes

| fix in review.md | applied? |
|---|---|
| Rebuild with `card_review.json` + `osm_supplement.geojson` (18 ways renumbered to the card) + `ignore_osm_holes` + tees Blue/White | **yes.** Request carries all four. Pars 4 4 4 4 5 3 4 3 5 / 4 4 5 3 4 4 3 5 4. Page yardage equals the card on all 36 hole-sets. The measured length is within 5 everywhere: 3 Blue 267, 4 368, 5 451 (lidar pad, 447), 6 172, 7 330, 8 167, 9 477. |
| Holes 3-9 on the wrong OSM holes (par 3 tee walked 200 yds into the woods, etc.) | **fixed.** Every picture now shows the tee box, its own fairway and its own green. No line crosses another hole. |
| Renovation: check the 2026 club card before publishing | **open.** See below. |

## The 2026 card

`course_data/research/web/rv_swope_falls2/` (fetched after the review):

- `00.txt`, swopememorialgolfcourse.com/About: "Following an extensive restoration that returned Swope Memorial to A.W.
  Tillinghast's original design ... **6,324 Yardage, 71 Par**, 18 holes".
- `02.*`, Scorecard-2026.pdf: fetched, but it is a scanned image inside a PDF and was saved as text, so the JPEG bytes
  are corrupted (243 KB on disk vs 130,951 bytes fetched). It is not readable from the repo.
- Shark Club, Golf Handicapp: the old 6,274 / par 72 card (same as golfify). Caddie Tap GPS: par 72, 6,237, hole 5 at
  407 (the OSM way measures 407 too; the card says 451, par 5).

So the old card is outdated in at least one par (72 -> 71) and 50 yds in total. Hole 5 (451-yd par 5 on the card,
about 407 on the ground) is the obvious candidate. The page's hole 5 Blue tee is a lidar pad 44 yds behind the OSM
way start.

## Holes

| hole | Blue | White | note |
|---|---|---|---|
| 1, 2, 10-18 | OK | OK | routing, green and tees on OSM boxes, as reviewed. 2 Blue Driver to 39 yds short among trees (fairway 12%), uncertain as reviewed |
| 3-4, 6-9 | **fixed** | **fixed** | card par and yardage on the right OSM hole |
| 5 | fixed vs the old card; **probably changed in 2026** | same | see above |

The imagery is NAIP 2020, before the restoration (new tees, greens, bunkers and a pond).

## Next fix

1. Re-fetch `https://www.swopememorialgolfcourse.com/docs/Scorecard-2026.pdf` as **binary**. The web_fetch workflow
   stores it as text; it needs a binary or base64 mode for PDFs and images. Then OCR or read it, and type the 2026
   card into `card_review.json` (par 71, 6,324).
2. Rebuild with the same keys. If the routing order changed in the restoration, recheck the supplement numbering
   against the 2026 card.
3. Publish only with the 2026 card. Until newer imagery exists, the page should say that the hazard zones are
   pre-restoration.
