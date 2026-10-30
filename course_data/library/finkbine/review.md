# Finkbine Golf Course: course review (rv02, agent)

**Do not publish.** finkbine.com: the course and range are **closed for renovation for all of 2026** (an $11M Scott
Hoffman redesign that reroutes holes, reopening about May 2027). The page is built for Sat 10/31 and Sun 11/1 2026 on the
old layout (2021 NAIP). Rebuild it after the reopening, once OSM and imagery show the new holes.

On the pre-renovation layout:

* **Card.** Golfify / AllSquare (Black 7017) is an older card: Black 449 is listed on holes 9, 10 and 18. The current club card
  (Black/Gold/White/Gray, golfimprovement.ai, Black 6951) fits the OSM tee boxes. It explains every Black walk-back
  (1: 375, 10: 410, 13: 182) and the 3 / 12 / 14 differences.
* **Holes.** 12 OK. 6 have the wrong card value or tee (1, 3, 9, 10, 12, 13), with fixes in review.json (tee at the
  OSM hole-line start, plus the current card yards). None are uncertain once the current card is used.
* Page render (qa_page.js, phone + desktop): no problems. The only console error is the sandbox's certificate error.

Evidence: course_data/research/web/rv02_cards (golfify, AllSquare, club site, renovation news) and rv02_cards2/02.txt (current card).
