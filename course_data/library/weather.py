"""Weather for a course page: the hourly forecast when the event is close, else climate normals.

  python course_data/library/weather.py --lat 38.9 --lon -94.6 --days 2026-11-07,2026-11-08 --out weather.json

forecast  Open-Meteo hourly forecast (weather/fetch_forecast.py, the source the tournament pages use) when the first
          event day is within FORECAST_DAYS of today.
normals   otherwise (or when the forecast fails): the same calendar window (event days +/- WINDOW days) in each of
          the last YEARS years from the Open-Meteo ERA5 archive, averaged per local hour: mean temperature, mean
          wind speed and gust, and the prevailing direction (vector mean of the wind-from directions, weighted by
          speed). The file is marked "placeholder": true, so the page shows its "climate normals, not a forecast"
          banner.
fallback  no network: a constant-wind placeholder from STATE_NORMALS (rough monthly means), also a placeholder.

Output: the forecast format v2_course.forecast() reads ({"hourly": [{date, hour, temp_f, wind_mph, gust_mph,
wind_from_deg}], "placeholder", "note", "fetched_utc", "kind"}). Network only on GitHub Actions.
"""
import argparse
import datetime as dt
import json
import math
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
FORECAST_DAYS = 14
YEARS = 10
WINDOW = 7
HOURS = range(6, 20)
UA = "my_golf_data_science course-page weather (github.com/willbhedges/my_golf_data_science)"

# rough Midwest monthly means (low F, high F, wind mph, from deg) for the no-network fallback only
STATE_NORMALS = {1: (18, 36, 11, 320), 2: (22, 41, 11, 320), 3: (32, 53, 12, 180), 4: (43, 65, 12, 180),
                 5: (53, 74, 10, 180), 6: (63, 84, 9, 190), 7: (67, 88, 8, 200), 8: (65, 86, 8, 190),
                 9: (56, 78, 9, 180), 10: (44, 66, 10, 190), 11: (33, 51, 11, 200), 12: (22, 39, 11, 320)}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:                                    # noqa: BLE001
            err = e
    raise RuntimeError(f"{url[:120]}: {err}")


def forecast(lat, lon, days):
    sys.path.insert(0, os.path.join(CD, "weather"))
    import fetch_forecast as F
    F.LAT, F.LON, F.TZ = lat, lon, "auto"
    F.HOURS = HOURS
    url, rows = F.open_meteo(days)
    if not rows:
        raise RuntimeError("Open-Meteo forecast returned no rows")
    return dict(kind="forecast", placeholder=False, fetched_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                note="Open-Meteo hourly forecast", sources=dict(open_meteo=url), hourly=rows,
                location=dict(lat=lat, lon=lon), days=days)


def normals(lat, lon, days, years=YEARS, window=WINDOW):
    d0 = [dt.date.fromisoformat(d) for d in days]
    now = dt.date.today()
    acc = {}                                                     # hour -> lists
    used = []
    for y in range(now.year - years, now.year):
        try:
            lo = min(d.replace(year=y) for d in d0) - dt.timedelta(days=window)
            hi = max(d.replace(year=y) for d in d0) + dt.timedelta(days=window)
        except ValueError:                                        # Feb 29
            continue
        if hi >= now - dt.timedelta(days=7):
            continue
        url = ("https://archive-api.open-meteo.com/v1/archive"
               f"?latitude={lat}&longitude={lon}&start_date={lo}&end_date={hi}"
               "&hourly=temperature_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m"
               "&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=auto")
        h = get(url)["hourly"]
        for i, t in enumerate(h["time"]):
            hr = int(t[11:13])
            if hr not in HOURS:
                continue
            T, S, Dd, G = (h[k][i] for k in ("temperature_2m", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"))
            if None in (T, S, Dd):
                continue
            a = acc.setdefault(hr, dict(t=[], s=[], u=[], v=[], g=[]))
            a["t"].append(T)
            a["s"].append(S)
            a["u"].append(S * math.sin(math.radians(Dd)))
            a["v"].append(S * math.cos(math.radians(Dd)))
            a["g"].append(G if G is not None else S * 1.6)
        used.append(y)
    if not acc:
        raise RuntimeError("no archive rows")
    mean = lambda x: sum(x) / len(x)                             # noqa: E731
    prof = {}
    for hr, a in acc.items():
        prof[hr] = dict(temp_f=round(mean(a["t"]), 1), wind_mph=round(mean(a["s"]), 1), gust_mph=round(mean(a["g"]), 1),
                        wind_from_deg=round(math.degrees(math.atan2(mean(a["u"]), mean(a["v"]))) % 360, 0))
    rows = [dict(date=d, hour=hr, **prof[hr]) for d in days for hr in HOURS if hr in prof]
    return dict(kind="climate normals", placeholder=True,
                fetched_utc=f"climate normals (ERA5 via the Open-Meteo archive, {min(used)}-{max(used)})",
                note=(f"PLACEHOLDER: climate normals for these dates (ERA5 reanalysis via the Open-Meteo archive, "
                      f"{len(used)} years {min(used)}-{max(used)}, event days +/- {window} days, mean per hour; wind "
                      "direction is the prevailing one). Rebuild inside ~10 days of the event for a real forecast."),
                hourly=rows, location=dict(lat=lat, lon=lon), days=days, years=used)


def fallback(days):
    m = dt.date.fromisoformat(days[0]).month
    lo, hi, mph, frm = STATE_NORMALS[m]
    rows = []
    for d in days:
        for hr in HOURS:
            x = (hr - 6) / 9.0 if hr <= 15 else 1 - (hr - 15) / 12.0
            T = lo + (hi - lo) * math.sin(min(max(x, 0), 1) * math.pi / 2)
            rows.append(dict(date=d, hour=hr, temp_f=round(T, 1), wind_mph=float(mph), gust_mph=round(mph * 1.6, 1),
                             wind_from_deg=float(frm)))
    return dict(kind="fallback", placeholder=True, fetched_utc="placeholder (rough monthly means, no network)",
                note="PLACEHOLDER: rough Midwest monthly means (no weather data could be fetched), constant wind.",
                hourly=rows, days=days)


def course_weather(lat, lon, days, today=None):
    today = today or dt.date.today()
    first = dt.date.fromisoformat(days[0])
    errs = []
    if (first - today).days <= FORECAST_DAYS and dt.date.fromisoformat(days[-1]) >= today:
        try:
            return forecast(lat, lon, days)
        except Exception as e:                                    # noqa: BLE001
            errs.append(f"forecast: {e}")
    try:
        w = normals(lat, lon, days)
    except Exception as e:                                        # noqa: BLE001
        errs.append(f"normals: {e}")
        w = fallback(days)
    if errs:
        w["errors"] = errs
    return w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--days", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    w = course_weather(a.lat, a.lon, a.days.split(","))
    json.dump(w, open(a.out, "w"), indent=1)
    print(w["kind"], w.get("errors", ""))


if __name__ == "__main__":
    main()
