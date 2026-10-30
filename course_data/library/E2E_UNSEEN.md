# End-to-end on never-built courses ("pick any US course -> solved page")

Status 2026-10-30 20:05Z: **not measured yet.** The 5 courses are chosen and their requests are written, but the build was
not queued: course_page run 41110038362 (14 courses) was running and run 41114019985 was queued, and a new
course_page push cancels a running one. The truth fetches (scorecards, OSM counts) were pushed but had not come back
when this was written (see "What blocked the measurement"). Rows below are filled in as the results land.

## The 5 courses

Chosen to spread over regions and over how hard each should be for the pipeline. None is in `index.json`,
`library/gate/`, `courses/`, or the zero_tap benchmark (`zero_tap/selection.json`).

| slug | course | state | why it is hard (expected) |
|---|---|---|---|
| bandon_dunes | Bandon Dunes (Bandon) | OR | resort, expected well mapped; 6 courses on one site, so resolve must pick the right one |
| memorial_park_houston | Memorial Park Golf Course (Houston) | TX | big-city muni, Hanse redesign 2019-20: OSM and NAIP may predate it |
| papago | Papago Golf Course (Phoenix) | AZ | desert: rough is dirt / scrub, vision layer trained on Midwest grass |
| grand_national_links | Grand National, Links Course (Opelika) | AL | wooded Southeast, 3 courses on one site, lake holes |
| bethpage_black | Bethpage Black (Farmingdale) | NY | Northeast state-park muni, 5 courses on one site, tree-lined |

Requests (name, city, state, `near` only, as a user would type them; default tees and dates):
`course_page_<slug>.json` + `course_batch_e2e_unseen.json`, held uncommitted for the coordinator to queue (pushing
them starts course_page.yml).

## Truth (to confirm)

Card values below are from memory and **not yet verified** against a fetched card. They are here so a wrong card
in the build stands out. The fetch is `course_data/requests/webfetch_e2e_unseen_cards.json` (golfify slug guesses
and a DuckDuckGo search per course, for these 5 and 13 reserve candidates). Results land in
`course_data/research/web/e2e_unseen_cards/`.

| slug | holes | par (back tee) | yards (back tee) | source |
|---|---|---|---|---|
| bandon_dunes | 18 | 72 | ~6,730 | memory, unverified |
| memorial_park_houston | 18 | 70 | ~7,400 (post-2020) | memory, unverified |
| papago | 18 | 72 | ~7,300 | memory, unverified |
| grand_national_links | 18 | 72 | ~7,300 | memory, unverified |
| bethpage_black | 18 | 71 | ~7,460 | memory, unverified |

## Results table (to fill in after the build)

| slug | build | holes page / card | par agree | yardage within 10 yds | PASS / CHECK | wrong club or aim (photo) | build time | top failure causes |
|---|---|---|---|---|---|---|---|---|
| bandon_dunes | not run | | | | | | | |
| memorial_park_houston | not run | | | | | | | |
| papago | not run | | | | | | | |
| grand_national_links | not run | | | | | | | |
| bethpage_black | not run | | | | | | | |

How to fill it in, per course, from `course_data/library/<slug>/`:

* build: `status.json` status (auto-OK / needs confirm / failed) and `reasons`.
* holes, par, yardage: `package.json` holes against the verified card (not the card the pipeline found; a wrong
  card agreeing with itself is the failure to catch). Par: count of holes equal to the card. Yardage: holes
  within 10 yds of the card for the solved tee set.
* PASS / CHECK: `qa.json` per-hole checks (`check_holes` in `status.json`).
* wrong club or aim: hole by hole on the page's photo, does the calm-day aim land on fairway with a club that
  leaves a sensible approach, and does the routing (tee -> green) match the course (hole n's green near tee n+1,
  1 and 10 near the clubhouse)? Count holes where a golfer would not hit that club at that line.
* build time: the course's `course_page_one.yml` call, package start to finish commit.

## What blocked the measurement (and is itself the main finding)

1. **One GitHub Actions queue for everything.** The account's 20 concurrent jobs were held by the 14-course
   course_page batch; all web_fetch runs (mine and ~10 other agents') sat "queued" for 50+ minutes, so even a
   scorecard fetch cannot run while a batch builds. A user's "build this course" would wait the same way.
2. **Overpass state-wide counts time out.** `osm_check.yml` (the README's tool for checking OSM coverage before
   picking a course) ran 60 min on 152 candidates (runs 41108961280, 41111020902: both cancelled at the job
   timeout, nothing committed), and the 18-candidate `osm_check_e2e_unseen.json` run 41112878276 was still on the
   Overpass step after 55 min. The script writes its output only at the end, so a timeout loses every count. It
   needs per-candidate incremental output, a bbox query around `near` instead of `area["ISO3166-2"=...]`, and a
   per-query cap.
3. **A new course_page push cancels a running one** (coordinator note; the concurrency group is per-sha but runs were
   still cancelled once), so builds must be serialised by hand.
