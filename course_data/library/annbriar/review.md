# Annbriar Golf Course: course check (rv03)

Card: golfify (Hickory 6841 / Black 6517, par 72), cross-checked with AllSquare (the same card in metres).
Pages checked: phone screenshots for every hole on Hickory and Black (`qa_page.js`, 0 problems), plus the package tees.

* **OK: 17 holes.** Tees on OSM boxes within 0-6 yds of the card, pars match, routing follows the photo.
* **Hole 9, Black: wrong tee.** The tee sits on a lidar pad in the trees about 36 yds east of the tee complex, so the
  line runs along the right-hand trees and the pick is a 2-wood aimed 40 yds right. Fix: put the tee on the complex 14 yds
  in front of the Hickory box (card 475). `osm_supplement.geojson` adds that box.
* **Hole 13, Hickory: kept, uncertain.** The lidar-pad tee measures 384 against a card of 383. The back OSM box measures
  only about 371, and the photo shows an open tee corridor, so an unmapped back tee is likely.
* Notes on picks: these are model judgments, not geometry errors. Hole 9 Hickory (aim 33 yds right, 26% fairway),
  hole 14 Hickory (aim 38 yds left, 32% fairway) and hole 18 Black (25% fairway) land partly off the fairway.

Publish as-is? Yes for Hickory. Black is fine except hole 9: its tee shot is wrong until the rebuild with the supplement.
