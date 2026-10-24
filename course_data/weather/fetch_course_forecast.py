"""Hourly forecast for any course (tournament courses in course_data/courses/<slug>/), same sources and format as
fetch_forecast.py (Open-Meteo primary, NWS hourly cross-check), so v2_course.py can read it as config "forecast".

  python course_data/weather/fetch_course_forecast.py course_data/requests/weather_<slug>.json
     request: {"slug": "blue_hills", "name": "...", "lat": 38.898, "lon": -94.599, "days": ["2026-10-27"],
               "hours": [6, 19], "rev": n}
  -> course_data/weather/forecast_<slug>.json

Runs on GitHub Actions (.github/workflows/weather_course.yml); the sandbox cannot reach weather APIs.
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fetch_forecast as F  # noqa: E402


def main(req):
    q = json.load(open(req))
    F.LAT, F.LON = float(q["lat"]), float(q["lon"])
    h0, h1 = q.get("hours", [6, 19])
    F.HOURS = range(int(h0), int(h1) + 1)
    days = q["days"]
    om_url, rows = F.open_meteo(days)
    nws_url, nrows = F.nws(days)
    if not rows:
        print("Open-Meteo fetch failed", file=sys.stderr)
        sys.exit(1)
    data = {
        "location": {"name": q.get("name", q["slug"]), "lat": F.LAT, "lon": F.LON, "timezone": F.TZ,
                     "coord_source": q.get("coord_source", "course package centre (OSM golf_course)")},
        "fetched_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "days": days,
        "units": {"wind": "mph at 10 m", "direction": "degrees true, wind blows FROM", "temp": "degF at 2 m"},
        "sources": {"open_meteo": om_url, "nws": nws_url},
        "summary": F.summarise(rows, nrows),
        "hourly": rows,
        "nws_hourly": nrows,
    }
    out = os.path.join(HERE, f"forecast_{q['slug']}.json")
    json.dump(data, open(out, "w"), indent=1)
    print(json.dumps(data["summary"], indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
