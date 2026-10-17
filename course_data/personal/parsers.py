"""Parsers: what golfers can already export -> bayes.Data records.

Launch monitors (one row per shot; carry + side at landing):
  parse_launch_monitor(path)   Garmin Approach R10/R50 (Garmin Golf app, session -> share -> CSV),
                               TrackMan (TPS: Shot History -> Table View -> export -> "Trackman CSV"),
                               FlightScope Mevo/Mevo+ (myflightscope.com -> session -> CSV), Rapsodo MLM2PRO,
                               SkyTrak, Foresight, Uneekor, or any CSV with club / carry / side columns.
                               Column names are matched through ALIASES; a second "units" row ([yds], [m], [mph])
                               is detected and metres are converted.
On-course shot tracking (tee shot start + end points):
  parse_arccos_json(path, bag_map)   arccos-api (unofficial, read-only, your own login) `arccos export -f json
                               --detail` or `arccos round ID --json`: holes[].shots[] with startLat/startLong/
                               endLat/endLong, clubId, noOfPenalties.
  parse_garmin_scorecards(path)  Garmin Connect scorecard JSON (community bookmarklet export): per-hole
                               fairway outcome + penalties -> summary stats; CT10 shot lists if present.
  parse_golfpad_shots(path)    Golf Pad comprehensive export (Premium) shots CSV: club, shot length, distance
                               from the fairway centre (- = left).
  parse_shot_csv(path)         generic CSV: club, start_lat, start_lon, end_lat, end_lon[, aim_lat, aim_lon,
                               penalty] (the app's own logger writes this).
Summary stats:
  parse_manual(path_or_dict)   the manual stats form (manual_stats.schema.json): fairways, misses L/R, tee
                               penalties, average drive. Read them off any app's stats screen (Arccos, 18Birdies,
                               Shot Scope, TheGrint, Golfshot, Garmin) or a paper scorecard.
  parse_golfpad_rounds(path)   Golf Pad free rounds CSV (fairways hit, penalties per round).
"""
from __future__ import annotations

import csv
import io
import json
import math
import re

from bayes import Data

YD_PER_M = 1.0936133

# ----------------------------------------------------------------------------------- clubs
_NUM = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9}


def canonical_club(raw: str) -> str:
    """Normalise a club label: 'Dr' / '1W' / 'Driver' -> 'Driver', '3W' / '3 Wood' -> '3-wood',
    '4H' / '4 Hybrid' -> '4-hybrid', '7i' / '7 Iron' -> '7-iron', 'PW' -> 'PW'."""
    s = str(raw or "").strip().lower().replace("_", " ")
    if not s:
        return ""
    if s in ("d", "dr", "drv", "driver", "1w", "1 wood", "1-wood"):
        return "Driver"
    m = re.match(r"^(\d)\s*-?\s*(w|wd|wood|fw|fairway wood|fairway)$", s) or re.match(r"^(?:wood|fairway)\s*(\d)$", s)
    if m:
        return f"{m.group(1)}-wood"
    m = re.match(r"^(\d)\s*-?\s*(h|hy|hyb|hybrid|rescue|u|ut|utility)$", s) or re.match(r"^(?:hybrid|rescue)\s*(\d)$", s)
    if m:
        return f"{m.group(1)}-hybrid"
    m = re.match(r"^(\d)\s*-?\s*(i|ir|iron)$", s) or re.match(r"^iron\s*(\d)$", s)
    if m:
        return f"{m.group(1)}-iron"
    for w in ("pw", "gw", "aw", "sw", "lw", "uw"):
        if s in (w, w[0] + " wedge", {"pw": "pitching wedge", "gw": "gap wedge", "aw": "approach wedge",
                                       "sw": "sand wedge", "lw": "lob wedge", "uw": "utility wedge"}[w]):
            return w.upper()
    m = re.match(r"^(\d\d)\s*(°|deg)?$", s)
    if m:
        return f"{m.group(1)}deg"
    return str(raw).strip()


def map_club(raw, bag_aliases: dict | None):
    """Club label -> bag name. bag_aliases: {"Driver": ["Driver"], "4-wood": ["4-wood", "5-wood"], ...}
    (canonical names). Unmapped clubs return the canonical label."""
    c = canonical_club(raw)
    for name, al in (bag_aliases or {}).items():
        if c == canonical_club(name) or c in {canonical_club(a) for a in al}:
            return name
    return c


# ----------------------------------------------------------------------------------- launch monitors
ALIASES = {
    "club": ["club", "club type", "club name", "clubtype", "club_type", "schlägerart", "tipo de palo"],
    "carry": ["carry distance", "carry", "carry dist", "carry (yds)", "carry (m)", "carry flat - length", "carry_yds",
              "carry-distanz", "distancia de vuelo", "carry_distance"],
    "side": ["carry deviation distance", "carry side", "side", "carry flat - side", "offline", "lateral",
             "lateral landing", "side carry", "carry lateral", "offline (yds)", "side (yds)", "carry_side",
             "carry-abweichungsdistanz", "deviation", "carry deviation"],
    "total": ["total distance", "total", "total (yds)", "est. total flat - length", "total_distance", "gesamtstrecke"],
    "side_total": ["total deviation distance", "total side", "side total", "est. total flat - side",
                   "gesamtabweichungsdistanz"],
    "date": ["date", "time", "datum", "timestamp", "session date"],
    "session": ["session", "session id", "session name", "tag"],
}


def _norm(h):
    return re.sub(r"\s+", " ", str(h).strip().lower().replace("﻿", ""))


def _find(header, key):
    hn = [_norm(h) for h in header]
    for a in ALIASES[key]:
        if a in hn:
            return hn.index(a)
    return None


def _num(v):
    if v is None:
        return None
    s = str(v).strip()
    if s in ("", "-", "--", "n/a", "NaN", "nan"):
        return None
    m = re.match(r"^\s*([-+]?\d+(?:[.,]\d+)?)\s*([LRlr])?\s*$", s)        # "12.3 L" / "8.0R"
    if m:
        x = float(m.group(1).replace(",", "."))
        if m.group(2):
            x = -abs(x) if m.group(2).upper() == "L" else abs(x)
        return x
    m = re.match(r"^\s*([LRlr])\s*([-+]?\d+(?:[.,]\d+)?)\s*$", s)          # "L 12"
    if m:
        x = abs(float(m.group(2).replace(",", ".")))
        return -x if m.group(1).upper() == "L" else x
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None


def parse_launch_monitor(path_or_text, bag_aliases=None, units=None, side_sign=+1, session=None, ball="premium",
                         clubs=None, max_rel_dev=None):
    """Launch-monitor CSV -> Data(lm=[...]). `units` 'yds'/'m' overrides detection; side_sign=-1 if the
    file's side is + = left. `clubs` keeps only these bag names. A row with no carry is skipped.
    Detection of a units row: the row after the header whose cells look like [yds] / (m) / mph."""
    text = open(path_or_text, encoding="utf-8-sig").read() if "\n" not in str(path_or_text) else path_or_text
    rows = list(csv.reader(io.StringIO(text)))
    rows = [r for r in rows if any(c.strip() for c in r)]
    hi = next(i for i, r in enumerate(rows) if _find(r, "carry") is not None)    # TrackMan puts metadata first
    header = rows[hi]
    body = rows[hi + 1:]
    unit_row = None
    if body and sum(bool(re.search(r"\[.*\]|\(.*\)|^(yds|m|mph|deg|rpm|ft|%)$", c.strip(), re.I)) for c in body[0]) >= 2:
        unit_row, body = body[0], body[1:]
    ic, ica, isd = _find(header, "club"), _find(header, "carry"), _find(header, "side")
    ise = _find(header, "session")
    u = units
    if u is None:
        lab = (unit_row[ica] if unit_row and ica < len(unit_row) else header[ica]).lower()
        u = "m" if re.search(r"\bm\b|\[m\]|\(m\)|meter|metre", lab) and "mph" not in lab else "yds"
    k = YD_PER_M if u == "m" else 1.0
    out = []
    for r in body:
        if ica >= len(r):
            continue
        c = _num(r[ica])
        if c is None or c <= 0:
            continue
        club = map_club(r[ic], bag_aliases) if ic is not None and ic < len(r) else "Driver"
        if clubs and club not in clubs:
            continue
        s = _num(r[isd]) if isd is not None and isd < len(r) else None
        sess = session or (r[ise] if ise is not None and ise < len(r) and r[ise].strip() else "s0")
        out.append(dict(club=club, carry=c * k, side=None if s is None else side_sign * s * k,
                        session=str(sess), ball=ball, source="launch_monitor"))
    return Data(lm=out)


# ----------------------------------------------------------------------------------- geometry
def _local_yds(lat0, lon0, lat, lon):
    """Equirectangular offsets in yards (x east, y north) -- fine over a few hundred yards."""
    R = 6371008.8 / 0.9144
    x = math.radians(lon - lon0) * math.cos(math.radians(lat0)) * R
    y = math.radians(lat - lat0) * R
    return x, y


def tee_shot_geometry(start, end, target):
    """(total, lateral) yds of a ball from `start` to `end` measured against the line start -> target
    (lateral + = right of the line)."""
    ex, ey = _local_yds(start[0], start[1], end[0], end[1])
    tx, ty = _local_yds(start[0], start[1], target[0], target[1])
    tl = math.hypot(tx, ty)
    if tl < 1:
        return math.hypot(ex, ey), None
    ux, uy = tx / tl, ty / tl
    along = ex * ux + ey * uy
    lat = ex * uy - ey * ux                 # right of the line = clockwise from the direction
    return math.hypot(ex, ey), lat


AIM_SD = {"plan": 3.0, "aim_point": 4.0, "fairway_centre": 6.0, "green_line": 10.0}


def parse_shot_csv(path_or_text, bag_aliases=None, beyond=35.0):
    """Generic on-course tee shots CSV: club, start_lat, start_lon, end_lat, end_lon, and optionally
    aim_lat, aim_lon (the intended target), aim_source (plan / aim_point / fairway_centre / green_line),
    penalty (0/1), penalty_side (left/right), lateral_yds, total_yds (already measured)."""
    text = open(path_or_text, encoding="utf-8-sig").read() if "\n" not in str(path_or_text) else path_or_text
    rd = csv.DictReader(io.StringIO(text))
    out = []
    for r in rd:
        r = {_norm(k): v for k, v in r.items()}
        club = map_club(r.get("club"), bag_aliases)
        src = (r.get("aim_source") or "").strip() or ("aim_point" if r.get("aim_lat") else "green_line")
        pen = str(r.get("penalty", "0")).strip().lower() in ("1", "true", "yes", "t")
        tot, lat = _num(r.get("total_yds")), _num(r.get("lateral_yds"))
        if tot is None and r.get("end_lat"):
            st = (float(r["start_lat"]), float(r["start_lon"]))
            en = (float(r["end_lat"]), float(r["end_lon"]))
            tg = (float(r["aim_lat"]), float(r["aim_lon"])) if r.get("aim_lat") else None
            if tg is None and r.get("green_lat"):
                tg = (float(r["green_lat"]), float(r["green_lon"]))
            tot, lat = tee_shot_geometry(st, en, tg) if tg else (tee_shot_geometry(st, en, en)[0], None)
        rec = dict(club=club, total=tot, lateral=lat, aim_sd=AIM_SD.get(src, 8.0), gps_sd=5.0, cond_sd=8.0,
                   censored=None, beyond=float(r.get("beyond") or beyond), source="shot_csv")
        if pen:
            side = (r.get("penalty_side") or "").strip().lower()
            rec.update(total=None, lateral=None, censored=side if side in ("left", "right") else "both")
        out.append(rec)
    return Data(course=out)


def parse_arccos_json(path_or_obj, bag_map: dict, par: dict | None = None, targets: dict | None = None,
                      tee_clubs=None, beyond=35.0):
    """arccos-api round detail JSON (a round or a list of rounds) -> on-course tee shots.
    bag_map: {clubId: bag name} (from `arccos clubs --json`). The tee shot = shot 1 of a hole with >= 3
    shots (par 4/5 unless `par` {hole: par} says otherwise). Reference line: `targets` {hole: (lat, lon)}
    if given (aim_point), else tee -> the hole location, taken as the end of the last shot (green_line,
    aim sd 10 yds: doglegs should be given a target or dropped). A tee shot with noOfPenalties > 0 is censored
    on the side its end point (drop) lies."""
    obj = json.load(open(path_or_obj)) if isinstance(path_or_obj, str) else path_or_obj
    rounds = obj if isinstance(obj, list) else obj.get("rounds", [obj])
    out = []
    for rd in rounds:
        for h in rd.get("holes", []):
            shots = sorted(h.get("shots", []), key=lambda s: s.get("shotId", 0))
            hid = h.get("holeId")
            if not shots or (par and par.get(hid, par.get(str(hid))) == 3) or (not par and len(shots) < 3):
                continue
            s0 = shots[0]
            club = bag_map.get(s0.get("clubId"), bag_map.get(str(s0.get("clubId"))))
            if club is None or (tee_clubs and club not in tee_clubs) or s0.get("endLat") is None:
                continue
            st, en = (s0["startLat"], s0["startLong"]), (s0["endLat"], s0["endLong"])
            tgt = (targets or {}).get(hid) or (targets or {}).get(str(hid))
            src = "aim_point"
            if tgt is None:
                last = shots[-1]
                tgt = (last.get("endLat") or last["startLat"], last.get("endLong") or last["startLong"])
                src = "green_line"
            tot, lat = tee_shot_geometry(st, en, tgt)
            rec = dict(club=club, total=tot, lateral=lat, aim_sd=AIM_SD[src], gps_sd=5.0, cond_sd=8.0,
                       censored=None, beyond=beyond, source="arccos")
            if (s0.get("noOfPenalties") or 0) > 0:
                rec.update(total=None, lateral=None,
                           censored=("right" if (lat or 0) > 0 else "left") if lat is not None and abs(lat) > 15 else "both")
            out.append(rec)
    return Data(course=out)


def parse_golfpad_shots(path_or_text, bag_aliases=None, tee_only=True):
    """Golf Pad comprehensive export, shots file (Premium). Column names vary by version, so they are
    matched by keyword: club, shot number, shot length, lie, and the distance from the fairway centre
    (- = left, + = right). Tee shots = shot number 1 (lie 'tee')."""
    text = open(path_or_text, encoding="utf-8-sig").read() if "\n" not in str(path_or_text) else path_or_text
    rd = csv.DictReader(io.StringIO(text))
    cols = {_norm(c): c for c in rd.fieldnames or []}

    def col(*keys):
        for n, c in cols.items():
            if all(k in n for k in keys):
                return c
        return None
    c_club, c_num, c_len = col("club"), col("shot", "number") or col("shot #"), col("shot", "length") or col("distance")
    c_fw = col("fairway", "center") or col("fairway", "centre") or col("from", "fairway")
    c_lie, c_out = col("lie"), col("outcome")
    out = []
    for r in rd:
        if tee_only and c_num and str(r.get(c_num, "")).strip() not in ("1", "1.0"):
            continue
        if c_lie and r.get(c_lie) and "tee" not in r[c_lie].lower() and tee_only and not c_num:
            continue
        outcome = (r.get(c_out) or "").lower() if c_out else ""
        rec = dict(club=map_club(r.get(c_club), bag_aliases), total=_num(r.get(c_len)) if c_len else None,
                   lateral=_num(r.get(c_fw)) if c_fw else None, aim_sd=AIM_SD["fairway_centre"], gps_sd=5.0,
                   cond_sd=8.0, censored=None, beyond=35.0, source="golfpad")
        if any(w in outcome for w in ("penalty", "ob", "out of bounds", "lost", "water", "hazard")):
            rec.update(total=None, lateral=None, censored="both")
        out.append(rec)
    return Data(course=out)


# ----------------------------------------------------------------------------------- summaries
SUMMARY_FIELDS = ("rounds", "n_tee", "fairways", "miss_left", "miss_right", "tee_penalties", "avg_drive", "n_drives")


def parse_manual(path_or_dict):
    """Manual stats form (manual_stats.schema.json) -> Data(summary=[...]).
    Accepts percentages (fairway_pct, miss_left_pct, miss_right_pct, tee_penalties_per_round) with
    rounds + tee_shots_per_round, and converts them to counts (the likelihood needs counts)."""
    d = json.load(open(path_or_dict)) if isinstance(path_or_dict, str) else dict(path_or_dict)
    rounds = d.get("rounds")
    n_tee = d.get("n_tee")
    if n_tee is None and rounds:
        n_tee = int(round(rounds * d.get("tee_shots_per_round", 14)))
    fw = d.get("fairways")
    if fw is None and d.get("fairway_pct") is not None and n_tee:
        fw = int(round(n_tee * d["fairway_pct"] / 100))
    L, R = d.get("miss_left"), d.get("miss_right")
    if L is None and d.get("miss_left_pct") is not None and n_tee:
        L = int(round(n_tee * d["miss_left_pct"] / 100))
    if R is None and d.get("miss_right_pct") is not None and n_tee:
        R = int(round(n_tee * d["miss_right_pct"] / 100))
    if (d.get("fairways") is None and d.get("miss_right") is None and None not in (fw, L, R)
            and abs(d.get("fairway_pct", 0) + d.get("miss_left_pct", 0) + d.get("miss_right_pct", 0) - 100) < 1.5):
        R = n_tee - fw - L                          # percentages that add to 100: keep the counts consistent
    pen = d.get("tee_penalties")
    if pen is None and d.get("tee_penalties_per_round") is not None and rounds:
        pen = int(round(d["tee_penalties_per_round"] * rounds))
    rec = dict(n_tee=n_tee, fairways=fw, miss_left=L, miss_right=R, tee_penalties=pen,
               avg_drive=d.get("avg_drive"), n_drives=d.get("n_drives") or n_tee, club=d.get("club", "Driver"),
               course=d.get("course", "spirit_hollow"), holes=d.get("holes"), rounds=rounds, source=d.get("source", "manual"))
    return Data(summary=[rec])


def parse_golfpad_rounds(path_or_text, course="spirit_hollow", tee_shots_per_round=14):
    """Golf Pad rounds CSV (free export): sums fairways hit and penalties over rounds. Penalties there are
    all penalties; tee shots cause most of them for a low handicap, but treat them as an upper bound
    (the form's tee_penalties is better)."""
    text = open(path_or_text, encoding="utf-8-sig").read() if "\n" not in str(path_or_text) else path_or_text
    rd = csv.DictReader(io.StringIO(text))
    cols = {_norm(c): c for c in rd.fieldnames or []}
    c_fw = next((c for n, c in cols.items() if "fairway" in n and "hit" in n), None)
    c_fwp = next((c for n, c in cols.items() if "fairway" in n and ("possible" in n or "total" in n)), None)
    c_pen = next((c for n, c in cols.items() if "penalt" in n), None)
    n = fw = pen = rounds = 0
    for r in rd:
        rounds += 1
        f = _num(r.get(c_fw)) if c_fw else None
        fw += f or 0
        n += (_num(r.get(c_fwp)) if c_fwp else None) or tee_shots_per_round
        pen += (_num(r.get(c_pen)) if c_pen else 0) or 0
    return parse_manual(dict(rounds=rounds, n_tee=int(n), fairways=int(fw), tee_penalties=int(pen) if c_pen else None,
                             course=course, source="golfpad_rounds"))


def parse_garmin_scorecards(path_or_obj, course="spirit_hollow"):
    """Garmin Connect scorecard JSON (community export: scorecards[].holes[] with fairwayShotOutcome
    HIT / LEFT / RIGHT and penalties). Field names come from community exports; check one file."""
    obj = json.load(open(path_or_obj)) if isinstance(path_or_obj, str) else path_or_obj
    cards = obj.get("scorecards", obj if isinstance(obj, list) else [obj]) if isinstance(obj, (dict, list)) else []
    n = fw = L = R = pen = rounds = 0
    for c in cards:
        c = c.get("scorecard", c)
        rounds += 1
        for h in c.get("holes", []):
            o = str(h.get("fairwayShotOutcome") or h.get("fairway") or "").upper()
            if not o or o in ("NONE", "NA", "N/A"):
                continue
            n += 1
            fw += o == "HIT"
            L += o == "LEFT"
            R += o == "RIGHT"
            pen += int(h.get("penalties") or 0)
    return parse_manual(dict(rounds=rounds, n_tee=n, fairways=fw, miss_left=L, miss_right=R, tee_penalties=pen,
                             course=course, source="garmin_scorecards"))
