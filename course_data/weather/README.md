# Weather: Spirit Hollow weekend forecast

`forecast_spirit_hollow.json` is written by `fetch_forecast.py`, which runs on
GitHub Actions (`.github/workflows/weather_fetch.yml`; the dev sandbox cannot
reach weather APIs). Re-run it with "Run workflow" (optional `days` input,
comma-separated `YYYY-MM-DD`; default in the workflow is 2026-10-17,2026-10-18),
or by pushing a change to the script/workflow.

- Location: 40.7605 N, 91.1442 W (OSM course centroid from
  `course_data/spirit_hollow/summary.json`), timezone America/Chicago.
- Primary: Open-Meteo `api.open-meteo.com/v1/forecast` (hourly
  `wind_speed_10m, wind_gusts_10m, wind_direction_10m, temperature_2m,
  precipitation_probability`), mph / degF.
- Cross-check: NWS `api.weather.gov` hourly forecast (gridpoint DVN 49,31);
  NWS reports wind in 5-mph steps and 16-point compass directions, no gusts.
- Hours kept: 07:00-18:00 local. `summary` has per-day mean/min/max wind,
  max gust, wind-weighted circular-mean direction, temperature range and the
  NWS comparison.
- Directions are degrees true, the direction the wind blows FROM.
- Heights: wind is at 10 m, temperature at 2 m. A driver apex is about 30 m,
  where open-ground wind is about 15-25% stronger, but averaged over the whole
  flight it is within a few % of the 10 m value. `spirit_hollow/wind.py` is
  calibrated on reported (10 m) wind, so use these numbers as they are, with
  `exposure` < 1 on tree-sheltered tees.

## Forecast (fetched 2026-10-16 18:27 UTC, Actions run 38947459138)

| Day | Wind (mean, range) | Max gust | From | Temp | Precip |
|---|---|---|---|---|---|
| Sat 10/17 | 4.0 mph (1.6-6.1) | 11 mph | NNW early, then SW (~225 deg) from 11am | 36 -> 53 F | 0% |
| Sun 10/18 | 11.1 mph (7.6-13.6) | 23 mph (early morning) | S (180-193 deg) all day | 40 -> 63 F | 0% |

NWS agrees: Saturday is calm to 5 mph SW in the afternoon, 35-57 F, sunny,
with frost early. Sunday is S 5-10 mph, 38-66 F, sunny. Open-Meteo runs about
2-3 mph above NWS on Sunday.
Sunday is the windy day: steady S 12-14 mph from 10am to 4pm, with gusts of
16-20 mph (gusts above 20 mph before 10am).

## Usage

```python
import json, wind
fc = json.load(open("course_data/weather/forecast_spirit_hollow.json"))
row = next(r for r in fc["hourly"] if r["time"] == "2026-10-18T12:00")
rel = wind.hole_relative(row["wind_from_deg"], hole_bearing_deg_true)
club = wind.temperature_adjust((275, 300, 65, 28), row["temp_f"])
carry, total, width, depth, drift = wind.adjust(club, row["wind_mph"], rel,
                                                "Driver", gust_mph=row["gust_mph"])
```

Example: Sunday noon, Driver (13 mph from 190 deg, gusts 18 mph, 58 F):
playing S carries 252 (total 270, width 71); playing N carries 286 (total
318, width 60); playing E carries 275 with a drift of 15 yd left.
