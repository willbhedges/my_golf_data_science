"""Hourly forecast for a course's coordinates (course_data/weather/fetch_forecast.py, re-pointed).

fetch(lat, lon, days)   Open-Meteo (+ NWS cross-check) for the given point; runs on GitHub Actions (the
                        sandbox cannot reach weather APIs). Returns the fetch_forecast.py JSON layout.
nearby(lat, lon)        an already-committed course_data/weather/forecast_*.json within 5 km, else None.
"""
import glob
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEATHER = os.path.join(os.path.dirname(HERE), "weather")


def _ff():
    spec = importlib.util.spec_from_file_location("product_fetch_forecast", os.path.join(WEATHER, "fetch_forecast.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def fetch(lat, lon, name, days=None, tries=2):
    import datetime as dt
    ff = _ff()
    ff.LAT, ff.LON, ff.TZ = round(float(lat), 4), round(float(lon), 4), "auto"
    get0 = ff.get
    ff.get = lambda url, headers=None, tries_=tries: get0(url, headers, tries_)
    days = days or ff.target_days()
    om_url, rows = ff.open_meteo(days)
    if not rows:
        return None
    try:
        nws_url, nrows = ff.nws(days)
    except Exception:                                              # noqa: BLE001
        nws_url, nrows = None, []
    return {"location": {"name": name, "lat": ff.LAT, "lon": ff.LON, "timezone": "auto (course local)",
                         "coord_source": "course package centre"},
            "fetched_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "days": days,
            "units": {"wind": "mph at 10 m", "direction": "degrees true, wind blows FROM", "temp": "degF at 2 m"},
            "sources": {"open_meteo": om_url, "nws": nws_url},
            "summary": ff.summarise(rows, nrows), "hourly": rows, "nws_hourly": nrows}


def _km(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dl = math.radians(b[1] - a[1])
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def nearby(lat, lon, km=5.0):
    best = None
    for f in sorted(glob.glob(os.path.join(WEATHER, "forecast_*.json"))):
        try:
            d = json.load(open(f))
            loc = d["location"]
            dist = _km((lat, lon), (loc["lat"], loc["lon"]))
        except Exception:                                          # noqa: BLE001
            continue
        if dist <= km and (best is None or dist < best[0]):
            best = (dist, f, d)
    return (best[1], best[2]) if best else (None, None)


if __name__ == "__main__":
    lat, lon = map(float, sys.argv[1].split(","))
    print(json.dumps(fetch(lat, lon, "test"), indent=1)[:2000])
