"""Shared helpers: paths, slugs, US states, polite HTTP for Overpass / Nominatim (Actions only)."""
import json
import math
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
COURSE_DATA = os.path.dirname(HERE)
ROOT = os.path.dirname(COURSE_DATA)
PACKAGES = os.path.join(COURSE_DATA, "packages")
REQUESTS = os.path.join(HERE, "requests")
YD = 0.9144
UA = {"User-Agent": "my_golf_data_science course-platform (github.com/willbhedges/my_golf_data_science)"}
OVERPASS = ["https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.private.coffee/api/interpreter"]
NOMINATIM = "https://nominatim.openstreetmap.org"

STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
    "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts",
    "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}


def state_code(state):
    """'Iowa' / 'ia' / 'US-IA' -> 'IA'."""
    s = str(state or "").strip()
    s = re.sub(r"^US-", "", s, flags=re.I)
    if s.upper() in STATES:
        return s.upper()
    for k, v in STATES.items():
        if v.lower() == s.lower():
            return k
    raise ValueError(f"unknown US state {state!r}")


GENERIC = r"\b(golf|course|club|country|gc|cc|links|the|and|of|at|g\s*c|c\s*c|golf\s*club)\b"


def core_name(name):
    """'Spirit Hollow Golf Course' -> 'spirit hollow' (lower case, generic golf words removed)."""
    s = re.sub(r"[^a-z0-9 ]+", " ", str(name).lower().replace("&", " and "))
    s = re.sub(GENERIC, " ", s)
    return " ".join(s.split())


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "_", core_name(name)).strip("_") or "course"


def name_regex(name):
    """Overpass regex for the core name, tolerant of spaces / hyphens / apostrophes between words."""
    words = core_name(name).split() or [str(name).lower()]
    return "[ '-]*".join(re.escape(w) for w in words)


def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(h))


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ----------------------------------------------------------------------------- network (Actions only)
def overpass(query, tries=3, timeout=200):
    import requests
    last = None
    for attempt in range(tries):
        for url in OVERPASS:
            try:
                r = requests.post(url, data={"data": query}, headers=UA, timeout=timeout)
                if r.status_code == 200:
                    return r.json()
                last = f"{url}: HTTP {r.status_code} {r.text[:200]}"
            except Exception as e:                          # noqa: BLE001
                last = f"{url}: {e!r}"
            log("overpass failed:", last)
        time.sleep(20 * (attempt + 1))
    raise RuntimeError(f"all Overpass endpoints failed: {last}")


_last_nominatim = [0.0]


def nominatim(path, **params):
    """GET /search or /reverse with the 1 request / second policy."""
    import requests
    wait = 1.1 - (time.time() - _last_nominatim[0])
    if wait > 0:
        time.sleep(wait)
    params.setdefault("format", "jsonv2")
    try:
        r = requests.get(f"{NOMINATIM}/{path}", params=params, headers=UA, timeout=60)
        _last_nominatim[0] = time.time()
        r.raise_for_status()
        return r.json()
    except Exception as e:                                  # noqa: BLE001
        log(f"nominatim {path} {params} failed: {e!r}")
        _last_nominatim[0] = time.time()
        return None


def read_json(path, default=None):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def write_json(path, obj, indent=1):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=indent, default=_default)
        fh.write("\n")


def _default(o):
    try:
        import numpy as np
        if isinstance(o, np.generic):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
    except ImportError:
        pass
    if isinstance(o, tuple):
        return list(o)
    raise TypeError(type(o))
