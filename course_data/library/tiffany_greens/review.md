# Tiffany Greens: course review (2026-10-30)

**Verdict: the geometry is safe, but two Blue picks are bad and the tee-set names are unconfirmed.**

* **Card conflict.** The build used golfify: Gold 6,977 / Blue 6,613 / White 6,173 / Red 4,497, par 72. OpenGolfAPI
  lists The Tiffs 7,034 / Gold 6,648 / Blue 6,218 / Blue-White 5,992 / White 5,674.
  * Hole by hole, the golfify sets line up with the OpenGolfAPI sets one tier longer:
    * golfify Gold is about OpenGolfAPI The Tiffs.
    * golfify Blue is about OpenGolfAPI Gold.
    * golfify White is about OpenGolfAPI Blue.
  * The OpenGolfAPI yardages fit the OSM tee boxes better: 47 of 72 set-holes are within 6 yds, against 29 of 54 for
    golfify.
  * If the club's current card is the OpenGolfAPI one, the page's "Gold" is really the Tiffs tees and the page's "Blue"
    is really Gold. The real Blue (6,218) is then not on the page, and a golfer who picks their tee colour is shown a
    set about 330-400 yds longer.
  * The club and AllSquare fetch (`course_data/requests/webfetch_rv_ph_tg.json`) was still queued in Actions when I
    finished, so this is not confirmed.
* **Pars, routing and greens:** all 18 holes are right. I drew every hole on the page photo with OSM greens, hole
  lines, all tee sets and the calm landing spot.
* **Tees:** they sit on or next to real OSM tee boxes and match the stated yardages. The Gold tee on hole 1 is a
  lidar pad under trees behind the Blue box, which is plausible but unconfirmed. The Gold tee on 16 measures 526
  against 535.
* **Wrong picks (Blue set):**
  * **Hole 1:** 4-wood +1 lands 285 yds out at the edge of the lake that crosses the fairway (36% water). The tee shot
    should stay at about 250.
  * **Hole 16:** Driver -40 lands 292 yds out in the trees left of the dogleg corner. A shorter club to the fairway is
    the sensible play.
* **Picks checked and OK:** 17 (-35/-40, cutting the corner) and 18 (+27/+40) land on the fairway at the bend.
* **qa_page.js:** 0 problems on Gold and on Blue.

**Rebuild:** wait for the club card first.

* If the club card matches OpenGolfAPI, rebuild with:

  ```
  "scorecard": "course_data/library/tiffany_greens/card_review.json"
  "tees": ["The_Tiffs", "Gold"]
  ```

  The `card_review.json` set names are marked `confirmed: false`.
* If the club card matches golfify, no rebuild is needed for the names. Blue 1 and Blue 16 still need a solver
  re-check.
