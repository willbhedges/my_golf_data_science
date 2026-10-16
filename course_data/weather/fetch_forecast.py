"""Fetch the hourly weekend forecast for Spirit Hollow Golf Course, Burlington, Iowa.

Runs on GitHub Actions (the development sandbox cannot reach weather APIs).
Primary source: Open-Meteo (no key). Cross-check: NWS api.weather.gov
(needs a User-Agent). Writes course_data/weather/forecast_spirit_hollow.json.
Re-run by pushing any change to this file (last refresh request: Fri 2026-10-16 evening).

Coordinates: course centroid from course_data/spirit_hollow/summary.json
(OSM golf_course polygon), 40.7605 N, 91.1442 W.

Note: wind is the 10 m (33 ft) standard anemometer height. A driver apex is
~30-35 yds (~30 m), where wind over open ground is typically ~15-25% stronger
(log/power-law profile, alpha ~0.14-0.2); wind.adjust() is calibrated on
"reported" (10 m-ish) wind, the way rules of thumb are quoted, so we store the
raw 10 m numbers and do not rescale them here.
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.request

LAT, LON = 40.7605, -91.1442
TZ = "America/Chicago"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "forecast_spirit_hollow.json")
UA = "my_golf_data_science weather fetch (github.com/willbhedges/my_golf_data_science)"
HOURS = range(7, 19)  # 7am..6pm local inclusive
COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def get(url, headers=None, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001
            print(f"GET {url} failed ({e}); attempt {i + 1}", file=sys.stderr)
            time.sleep(3 * (i + 1))
    return None


def target_days():
    days = os.environ.get("DAYS")
    if days:
        return [d.strip() for d in days.split(",") if d.strip()]
    today = dt.date.today()
    sat = today + dt.timedelta(days=(5 - today.weekday()) % 7)
    return [sat.isoformat(), (sat + dt.timedelta(days=1)).isoformat()]


def compass(deg):
    return COMPASS[int((deg % 360) / 22.5 + 0.5) % 16]


def open_meteo(days):
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={LAT}&longitude={LON}"
           "&hourly=wind_speed_10m,wind_gusts_10m,wind_direction_10m,temperature_2m,"
           "precipitation_probability,precipitation"
           "&wind_speed_unit=mph&temperature_unit=fahrenheit&precipitation_unit=inch"
           f"&timezone={TZ}&start_date={days[0]}&end_date={days[-1]}")
    d = get(url)
    if not d:
        return url, []
    h = d["hourly"]
    rows = []
    for i, t in enumerate(h["time"]):
        day, hh = t[:10], int(t[11:13])
        if day in days and hh in HOURS:
            rows.append({
                "time": t, "date": day, "hour": hh,
                "wind_mph": h["wind_speed_10m"][i],
                "gust_mph": h["wind_gusts_10m"][i],
                "wind_from_deg": h["wind_direction_10m"][i],
                "wind_from": compass(h["wind_direction_10m"][i]),
                "temp_f": h["temperature_2m"][i],
                "precip_prob_pct": h.get("precipitation_probability", [None] * len(h["time"]))[i],
                "precip_in": h.get("precipitation", [None] * len(h["time"]))[i],
            })
    return url, rows


def nws(days):
    pts = get(f"https://api.weather.gov/points/{LAT},{LON}",
              {"Accept": "application/geo+json"})
    if not pts:
        return None, []
    url = pts["properties"]["forecastHourly"]
    d = get(url, {"Accept": "application/geo+json"})
    if not d:
        return url, []
    rows = []
    for p in d["properties"]["periods"]:
        t = p["startTime"]  # local time with offset
        day, hh = t[:10], int(t[11:13])
        if day not in days or hh not in HOURS:
            continue
        ws = p.get("windSpeed", "")
        try:
            mph = float(ws.split()[0])
        except Exception:  # noqa: BLE001
            mph = None
        dirs = p.get("windDirection")
        deg = COMPASS.index(dirs) * 22.5 if dirs in COMPASS else None
        rows.append({"time": t, "date": day, "hour": hh, "wind_mph": mph,
                     "wind_from": dirs, "wind_from_deg": deg,
                     "temp_f": p.get("temperature"),
                     "short_forecast": p.get("shortForecast"),
                     "precip_prob_pct": (p.get("probabilityOfPrecipitation") or {}).get("value")})
    return url, rows


def circ_mean(degs, w):
    import math
    s = sum(wi * math.sin(math.radians(d)) for d, wi in zip(degs, w))
    c = sum(wi * math.cos(math.radians(d)) for d, wi in zip(degs, w))
    return round(math.degrees(math.atan2(s, c)) % 360, 0)


def summarise(rows, nws_rows):
    out = {}
    for day in sorted({r["date"] for r in rows}):
        rs = [r for r in rows if r["date"] == day]
        ws = [r["wind_mph"] for r in rs]
        dmean = circ_mean([r["wind_from_deg"] for r in rs], ws)
        n = [r for r in nws_rows if r["date"] == day and r["wind_mph"] is not None]
        out[day] = {
            "weekday": dt.date.fromisoformat(day).strftime("%A"),
            "hours": "07:00-18:00 local",
            "wind_mph_mean": round(sum(ws) / len(ws), 1),
            "wind_mph_min": min(ws), "wind_mph_max": max(ws),
            "gust_mph_max": max(r["gust_mph"] for r in rs),
            "wind_from_deg_mean": dmean, "wind_from_mean": compass(dmean),
            "temp_f_min": min(r["temp_f"] for r in rs),
            "temp_f_max": max(r["temp_f"] for r in rs),
            "temp_f_mean": round(sum(r["temp_f"] for r in rs) / len(rs), 1),
            "precip_prob_max_pct": max((r["precip_prob_pct"] or 0) for r in rs),
            "nws_wind_mph_mean": round(sum(r["wind_mph"] for r in n) / len(n), 1) if n else None,
            "nws_wind_from_mode": max({r["wind_from"] for r in n},
                                      key=[r["wind_from"] for r in n].count) if n else None,
            "nws_temp_f_range": [min(r["temp_f"] for r in n), max(r["temp_f"] for r in n)] if n else None,
        }
    return out


def main():
    days = target_days()
    om_url, rows = open_meteo(days)
    nws_url, nrows = nws(days)
    if not rows:
        print("Open-Meteo fetch failed", file=sys.stderr)
        sys.exit(1)
    data = {
        "location": {"name": "Spirit Hollow Golf Course, Burlington, Iowa",
                     "lat": LAT, "lon": LON, "timezone": TZ,
                     "coord_source": "course_data/spirit_hollow/summary.json (OSM centroid)"},
        "fetched_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "days": days,
        "units": {"wind": "mph at 10 m", "direction": "degrees true, wind blows FROM",
                  "temp": "degF at 2 m"},
        "sources": {"open_meteo": om_url, "nws": nws_url},
        "summary": summarise(rows, nrows),
        "hourly": rows,
        "nws_hourly": nrows,
    }
    with open(OUT, "w") as f:
        json.dump(data, f, indent=1)
    print(json.dumps(data["summary"], indent=1))


if __name__ == "__main__":
    main()
