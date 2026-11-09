"""Hourly forecast for any course (tournament courses in course_data/courses/<slug>/), same sources and format as
fetch_forecast.py (Open-Meteo primary, NWS hourly cross-check), so v2_course.py can read it as config "forecast".

  python course_data/weather/fetch_course_forecast.py course_data/requests/weather_<slug>.json
     request: {"slug": "blue_hills", "name": "...", "lat": 38.898, "lon": -94.599, "days": ["2026-10-27"],
               "hours": [6, 19], "rev": n, optional "not_before": "YYYY-MM-DD" (skip until then)}
  -> course_data/weather/forecast_<slug>.json

Runs on GitHub Actions (.github/workflows/weather_course.yml), or locally where api.open-meteo.com / api.weather.gov
are reachable (course_data/courses/gateway_national/REFRESH_LOCAL.md); NWS alone if Open-Meteo fails.
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
    nb = q.get("not_before")            # optional "YYYY-MM-DD": before it a forecast for the days is not worth it
    if nb and dt.date.today() < dt.date.fromisoformat(nb):
        print(f"{q['slug']}: not before {nb} (today {dt.date.today()}): skipped; the page keeps climate normals")
        return
    F.LAT, F.LON = float(q["lat"]), float(q["lon"])
    h0, h1 = q.get("hours", [6, 19])
    F.HOURS = range(int(h0), int(h1) + 1)
    days = q["days"]
    om_url, rows = F.open_meteo(days)
    nws_url, nrows = F.nws(days)
    primary = "open_meteo"
    if not rows:
        # Open-Meteo down / rate-limited (local runs, Nov 2026: 429): NWS hourly alone when it covers every hour asked;
        # NWS has no gusts, so gust = 1.4 x wind (the Open-Meteo ratio on these courses' forecasts is ~1.4-1.7)
        want = {(d, h) for d in days for h in F.HOURS}
        for r in nrows:                                 # NWS gives no direction for a calm hour
            if r.get("wind_mph") == 0 and r.get("wind_from_deg") is None:
                r["wind_from_deg"], r["wind_from"] = 0.0, "N"
        have = {(r["date"], r["hour"]) for r in nrows if r.get("wind_mph") is not None and r.get("wind_from_deg") is not None}
        if not want <= have:
            print("Open-Meteo fetch failed and NWS does not cover every hour", file=sys.stderr)
            sys.exit(1)
        rows = [dict(r, gust_mph=round(1.4 * r["wind_mph"], 1), gust_note="1.4 x wind (NWS gives none)")
                for r in nrows if (r["date"], r["hour"]) in want]
        primary = "nws"
        print("Open-Meteo failed: using NWS hourly", file=sys.stderr)
    data = {
        "location": {"name": q.get("name", q["slug"]), "lat": F.LAT, "lon": F.LON, "timezone": F.TZ,
                     "coord_source": q.get("coord_source", "course package centre (OSM golf_course)")},
        "fetched_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "days": days,
        "units": {"wind": "mph at 10 m", "direction": "degrees true, wind blows FROM", "temp": "degF at 2 m"},
        "sources": {"open_meteo": om_url, "nws": nws_url, "primary": primary},
        "summary": F.summarise(rows, nrows),
        "hourly": rows,
        "nws_hourly": nrows,
    }
    out = os.path.join(HERE, f"forecast_{q['slug']}.json")
    json.dump(data, open(out, "w"), indent=1)
    print(json.dumps(data["summary"], indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
