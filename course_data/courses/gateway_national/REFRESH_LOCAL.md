# Gateway National: forecast refresh without GitHub Actions

Use only if Actions is not starting jobs (it stopped for ~10 min on 2026-11-09). Normal path: bump `rev` in
`course_data/requests/weather_gateway_national.json`, then in `course_data/requests/display_gateway_national.json`
(keep `"year": 2023`).

Local path (from the repo root; api.open-meteo.com and api.weather.gov are allowed in this environment):

1. Forecast: `python3 course_data/weather/fetch_course_forecast.py course_data/requests/weather_gateway_national.json`
   writes `course_data/weather/forecast_gateway_national.json`. If Open-Meteo is rate-limited (429) it uses the NWS
   hourly forecast alone (gust = 1.4 x wind; `sources.primary` says which). NOT yet run end to end locally.
2. Page: `python3 course_data/courses/v2_course.py page --slug gateway_national --which truth`, then
   `git checkout -- course_data/courses/gateway_national/*/course.py course_data/courses/gateway_national/*/meta.json`.
   Without `V2_DISPLAY_DIR` the photos come from the package imagery (NAIP 2023, the same source the page uses);
   compare a par-3 screenshot with the published page for sharpness before publishing.
3. QA: `node course_data/courses/qa_page.js course_data/courses/gateway_national/wind_page/index.html <out> "<set>"`
   for The Tips, Champions, Back, Middle, Forward (expect 18 holes, 0 problems); look at the phone screenshots.
4. Commit the forecast and the page (`git add -f` the page), push, republish the artifact from the same file path.

The refresh rebuilds the page and its wind picks; it does not re-solve the calm-day book (temperatures in the book
are the Nov 9 forecast's).

## The "Tall grass: Drop | Lost ball" control (Nov 13)

The page carries two solved rule sets; the same plain rebuild (step 2 above, nothing else) embeds both:

    python3 course_data/courses/v2_course.py page --slug gateway_national --which truth

It reads `truth/v2` + `truth_middle/v2` (Drop, the default) and `truth/v2_lost` + `truth_middle/v2_lost` (Lost ball),
and the `*_lost.json` files named in config `tall_grass_alt`. Neither set is re-solved by a refresh. The four
forecast-dependent tables (par-3 clubs for the day, par-5 Second shot block and menu) keep the forecast they were
solved on in both rule sets, as before. To re-solve the Lost ball set (only after a map or engine change), 91 s:

    FASTSOLVE_SLOTS=<dir>:4 python3 course_data/courses/fastsolve/run.py solve --slug gateway_national --which truth \
        --request course_data/requests/nccga_v2_gateway_national.json --out <dir>/b --draws 128 --tall-grass lost
    ... --which truth_middle ... --out <dir>/m --draws 128 --card-only --tall-grass lost      (copy *.json into v2_lost/)

QA with the control on: `QA_TALL=1 node course_data/courses/qa_page.js <page> <out> "<set>"` and
`QA_TALL=1 node course_data/courses/gateway_national/opt/qa_mode_fit.js <page> <out>`.
