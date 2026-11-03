# TPC Sawgrass Stadium (FL): multi-course rebuild QA (2026-11-03)

**Verdict: NEEDS FIX → card added, rebuild pushed.** The split worked: all 18 holes are Stadium holes, and the Valley
ways are all dropped. But the card the build matched is **Dye's Valley's**. The build then renumbered the Stadium
holes to fit the Valley card's pars and lengths, so the page's routing is scrambled. Page hole 5 is the island-green
17th, labelled "par 3, 158". Page hole 1 is Stadium 9. Chains from green n to tee n+1 run 237-1,557 yds. This page
must not be published.

Page checked: `course_data/library/tpc_sawgrass/page.html`, GitHub Actions run 41583713847 (built 2026-11-03T06:47Z,
on 269de3c1d). I ran it through `qa_page.js`, phone and desktop: 18 holes, 0 page problems. The page renders fine;
the content is wrong. I looked at every hole picture.

## What went wrong

- Package warning: "by hole way names: stadium 18, valley 18; kept 'stadium'". Correct.
- Card: opengolfapi 8a0c713e ("Tpc" / "Web" 6,847, par 5-3-4-4-3-4-4-5-4 / 4-3-4-4-3-4-5-5-4). That is Dye's Valley
  (GolfPass's Valley card, `research/web/mc_cards/09.html`). The Stadium is par 4-5-3-4-4-4-4-3-5 / 4-5-4-3-4-4-5-3-4,
  7,352 from The Players tees.
- Warning: "OSM hole numbering differs from the card: OSM hole refs -> card holes 1->12, 2->8, 3->14, 5->9, 6->3,
  7->13, 8->11, 9->1, 11->16, 12->7, 13->2, 14->6, 16->17, 17->5 (CHECK)". The page's hole n is therefore:

| page | Stadium hole (OSM way) | page par / yds | Stadium card (The Players) |
|---|---|---|---|
| 1 | 9 | 5 / 558 | 5 / 601 |
| 2 | 13 | 3 / 171 | 3 / 183 |
| 3 | 6 | 4 / 354 | 4 / 413 |
| 4 | 4 | 4 / 403 | 4 / 387 |
| 5 | **17 (island green)** | 3 / 158 | 3 / 141 |
| 6 | 14 | 4 / 445 | 4 / 485 |
| 7 | 12 | 4 / 326 | 4 / 365 |
| 8 | 2 | 5 / 503 | 5 / 555 |
| 9 | 5 | 4 / 436 | 4 / 469 |
| 10 | 10 | 4 / 408 | 4 / 419 |
| 11 | 8 | 3 / 229 | 3 / 236 |
| 12 | 1 | 4 / 363 | 4 / 424 |
| 13 | 7 | 4 / 409 | 4 / 450 |
| 14 | 3 | 3 / 203 | 3 / 182 |
| 15 | 15 | 4 / 402 | 4 / 470 |
| 16 | 11 | 5 / 559 | 5 / 573 |
| 17 | 16 | 5 / 499 | 5 / 537 |
| 18 | 18 | 4 / 421 | 4 / 462 |

Within each hole the picture, tee and plan are of a real Stadium hole. Only the number, the par source and the card
yardage are wrong.

## Fix (pushed)

`course_data/library/tpc_sawgrass/card_review.json` holds the Stadium card from GolfPass
(`research/web/mc_cards/00.html`, web_fetch run 41603917727). The sets are The Players 7,352 (76.8 / 155), Blue 6,670,
Blue/White 6,396, White 6,086, White/Green 5,509 and Green 5,019. Every set's out, in and total add up, and the pars
equal the OSM "Stadium N" ways' pars on all 18. The OSM Stadium way lengths are within ~25 yds of The Players yardage
on 15 holes, so the build should keep OSM numbering 1→18 with no renumbering. The request asks for "Black": The
Players carries colour black, so `choose_tee_set` picks it (checked locally). The rebuild is in
`course_batch_mc_cards.json` (course_page_tpc_sawgrass rev 3).

## Check on the rebuild

The 17th must be the island green at ~141 and the 18th a par 4 of ~462 with water left. There must be no "OSM hole
numbering differs" warning, and the chains must all be short. The title should name the Stadium (nit: it is "TPC
Sawgrass Caddie").
