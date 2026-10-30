"""Scorecards for any course: sources, parsing, and choosing the golfer's tee set.

Normalised card (the shape of course_data/tees/scorecard.json, which pipeline._norm_card also reads):

  {"schema": "scorecard/1", "source": "<url or file>", "par": [18], "handicap": [18] | null,
   "tee_sets": {"Black": {"colour": "black", "aliases": [...], "yards": [18], "par": [18] | absent,
                          "total": 6589, "rating": 71.4, "slope": 124, "source": "..."}}}

Sources, in the order package.py tries them (fetch_* need the web, i.e. GitHub Actions):
  1. request yardages        request["yardages"] = [..] or {"1": 391, ...} (+ optional "pars")
  2. local card file         request["scorecard"] = "course_data/tees/scorecard.json" (tees/ format)
  then the web cards by source reliability (RELIABILITY; never by how well a card fits the OSM map: the
  map is often older than the card, auto_course_lookup.md 6.3), the first one that passes the
  consistency check (`consistency`: per-hole yards sum to each set's stated total, longer sets longer on
  every hole) winning; when none passes, the most reliable one, flagged "mixed versions":
  3. the club website        OSM website=* page + links that look like a scorecard (html or pdf), parsed
                             with the generic text-table parser (`parse_text`)
  4. golfify.io              structured Next.js JSON (tees[].holeInformation); slug guesses, then a
                             DuckDuckGo site: search; the facility's state must match
  4b. BlueGolf / GolfPass / AllSquare  course directories with a scorecard page (`fetch_directory`, DIRECTORIES):
                             DuckDuckGo (then Bing) for the course on the site, the page's scorecard URL
                             parsed with `parse_text`; the page must name the course's state (or town) and the
                             card must fit the OSM hole count / lengths (`plausible`). Tried only when no
                             consistent card was found above (fetch_package.fetch_scorecards)
  5. OpenGolfAPI             api.opengolfapi.org (free, no key, ODbL 1.0; 1,000 anonymous calls/day):
                             /v1/courses/search then /api/v1/courses/{id} (`fetch_opengolfapi`,
                             `parse_opengolfapi`). Attribute "Contains data from OpenGolfAPI".
Raw pages are saved under packages/<slug>/raw/scorecard/ for audit.
"""
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
from urllib.parse import quote_plus, urljoin, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
import platform_common as pc  # noqa: E402

BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/124.0 Safari/537.36")
COLOURS = ("black", "blue", "white", "gold", "red", "green", "silver", "yellow", "orange", "rust", "copper",
           "tan", "purple", "grey", "gray", "championship", "tips", "back", "middle", "forward", "front",
           "senior", "ladies", "women", "men", "member", "combo", "teal", "burgundy", "maroon", "bronze", "platinum")
SYNONYMS = {"back": "longest", "tips": "longest", "championship": "longest", "tournament": "longest",
            "forward": "shortest", "front": "shortest", "ladies": "shortest", "women": "shortest",
            "middle": "median", "member": "median", "men": "median", "regular": "median"}


# ----------------------------------------------------------------------------- normalise / choose
def card_from_yardages(yards, pars=None, name="request", source="request file"):
    if isinstance(yards, dict):
        n = max(int(k) for k in yards)
        yards = [yards.get(str(i + 1), yards.get(i + 1)) for i in range(n)]
    if isinstance(pars, dict):
        pars = [pars.get(str(i + 1), pars.get(i + 1)) for i in range(len(yards))]
    ts = dict(colour=name.lower(), aliases=[name.lower()], yards=[int(y) if y else None for y in yards],
              total=sum(int(y) for y in yards if y), source=source)
    return dict(schema="scorecard/1", source=source, par=list(pars) if pars else None, handicap=None,
                tee_sets={name: ts})


def normalise(card):
    """Accept scorecard/1 with per-hole `holes` dicts (ARCHITECTURE 3.3) or the list shape; -> list shape."""
    out = dict(card)
    sets = {}
    for name, s in (card.get("tee_sets") or {}).items():
        s = dict(s)
        if "holes" in s and "yards" not in s:
            refs = sorted(s["holes"], key=lambda r: int(r))
            s["yards"] = [s["holes"][r].get("yards") for r in refs]
            s["par"] = [s["holes"][r].get("par") for r in refs]
            s.pop("holes")
        s.setdefault("colour", name.lower())
        s.setdefault("aliases", [])
        if s.get("total") is not None:
            s.setdefault("total_stated", s["total"])
        s.setdefault("total", sum(y for y in s["yards"] if y))
        sets[name] = s
    out["tee_sets"] = sets = dedupe_sets(sets)
    for a, b in (card.get("aliases") or {}).items():        # top-level {"blue": "Black"} map
        for name in sets:
            if name.lower() == str(b).lower():
                sets[name]["aliases"] = list(sets[name]["aliases"]) + [a.lower()]
    if not out.get("par"):
        for s in sets.values():
            if s.get("par"):
                out["par"] = s["par"]
                break
    return out


_DUP = re.compile(r"^\s*(.+?)\s*\(\s*(.+?)\s*\)\s*$")
_DUPN = re.compile(r"^\s*(.+?)\s+#\d+\s*$")             # parse_golfify's name for a repeated set


def dedupe_sets(sets):
    """'Gold (Gold)' / 'Gold #2' -> 'Gold' (QA P6: golfify lists a set again with its other rating). When 'Gold' is
    already on the card the duplicate is folded into its `alt_ratings` (name, rating, slope, par, total), else
    it is renamed; a name like 'Blue (Men)' is left alone."""
    out, dups = {}, []
    for name, s in sets.items():
        m, mn = _DUP.match(name), _DUPN.match(name)
        if m and m.group(1).lower() == m.group(2).lower():
            dups.append((name, m.group(1), s))
        elif mn and any(k.lower() == mn.group(1).lower() for k in sets):
            dups.append((name, mn.group(1), s))
        else:
            out[name] = s
    for name, base, s in dups:
        hit = next((k for k in out if k.lower() == base.lower()), None)
        if hit is None:
            out[base] = dict(s, aliases=sorted(set(s.get("aliases", [])) | {name.lower()}))
        else:
            alt = dict({k: s.get(k) for k in ("rating", "slope", "par", "total") if s.get(k) is not None}, name=name)
            out[hit] = dict(out[hit], alt_ratings=list(out[hit].get("alt_ratings", [])) + [alt])
    return out


def choose_tee_set(card, wanted):
    """-> (set name, how) or (None, reason). Matches name, colour, aliases, then back/middle/forward words."""
    sets = (card or {}).get("tee_sets") or {}
    if not sets:
        return None, "no scorecard"
    if not wanted:
        name = max(sets, key=lambda k: sets[k].get("total") or 0)
        return name, "no tee set requested: longest set"
    w = str(wanted).strip().lower()
    for name, s in sets.items():
        if name.lower() == w:
            return name, "name"
    for name, s in sets.items():
        if str(s.get("colour", "")).lower() == w:
            return name, "colour"
    for name, s in sets.items():
        if w in [str(a).lower() for a in s.get("aliases", [])]:
            return name, "alias"
    for name in sets:
        if w in name.lower().split() or w in re.split(r"[^a-z]+", name.lower()):
            return name, "word in set name"
    rule = SYNONYMS.get(w)
    if rule:
        order = sorted(sets, key=lambda k: sets[k].get("total") or 0)
        name = {"longest": order[-1], "shortest": order[0], "median": order[len(order) // 2]}[rule]
        return name, f"'{wanted}' read as the {rule} set"
    return None, f"tee set '{wanted}' not on the card (sets: {', '.join(sets)})"


def per_hole(card, set_name, refs):
    """{ref: {yards, par, hcp}} for the chosen set, indexed by hole number."""
    s = card["tee_sets"][set_name]
    pars = s.get("par") or card.get("par") or []
    hcp = s.get("handicap") or card.get("handicap") or []
    if isinstance(hcp, dict):
        hcp = hcp.get("men") or hcp.get("M") or next(iter(hcp.values()), [])
    out = {}
    for r in refs:
        if not str(r).isdigit():
            continue
        i = int(r) - 1
        y = s["yards"][i] if i < len(s["yards"]) else None
        out[str(r)] = dict(yards=y, par=pars[i] if i < len(pars) else None,
                           hcp=hcp[i] if isinstance(hcp, list) and i < len(hcp) else None)
    return out


# ----------------------------------------------------------------------------- reliability / consistency
RELIABILITY = ["club_site", "golfify", "bluegolf", "golfpass", "allsquare", "opengolfapi"]   # most reliable first
CARD_CONFIDENCE = dict(request=1.0, file=0.95, club_site=0.9, typed=0.9, golfify=0.85, bluegolf=0.85, golfpass=0.8,
                       allsquare=0.8, opengolfapi=0.75)
SUM_TOL_YD = 15
OPENGOLFAPI_ATTRIBUTION = ("Contains data from OpenGolfAPI (opengolfapi.org), ODbL 1.0; "
                           "(c) OpenStreetMap contributors")


def consistency(card, tol=SUM_TOL_YD):
    """Internal card check: does each set's per-hole yardage add up to the total the source states, and is
    every longer set at least as long on each hole (5-yd slack)? A source that mixes card versions (current
    totals over stale per-hole numbers: OpenGolfAPI's Spirit Hollow Gold sums to 7268 under a 7550 total)
    fails it. -> {ok, sets: {name: {sum, total_stated, diff, missing, ok}}, order_violations, flags}."""
    sets = (card or {}).get("tee_sets") or {}
    out, flags = {}, []
    for name, t in sets.items():
        ys = t.get("yards") or []
        tot = sum(y for y in ys if y)
        miss = sum(1 for y in ys if not y)
        stated = t.get("total_stated")
        diff = None if stated is None else tot - int(stated)
        ok = (diff is None or abs(diff) <= tol) and miss == 0
        out[name] = dict(sum=tot, total_stated=stated, diff=diff, missing=miss, ok=ok)
        if diff is not None and abs(diff) > tol:
            flags.append(f"{name}: holes sum to {tot} but the source says {stated} ({diff:+d}): mixed card versions")
        if miss:
            flags.append(f"{name}: {miss} hole(s) without a yardage")
    order = sorted((n for n in sets if sets[n].get("yards")), key=lambda n: -(sets[n].get("total") or 0))
    viol = []
    for a, b in zip(order, order[1:]):
        for i, (ya, yb) in enumerate(zip(sets[a]["yards"], sets[b]["yards"])):
            if ya and yb and ya + 5 < yb:
                viol.append(dict(hole=i + 1, longer=a, shorter=b, yards=[ya, yb]))
    if viol:
        flags.append(f"{len(viol)} hole(s) where a longer set is shorter than the next set: "
                     + ", ".join(f"{v['hole']} {v['longer']} {v['yards'][0]} < {v['shorter']} {v['yards'][1]}"
                                 for v in viol[:4]))
    return dict(ok=not flags, sets=out, order_violations=viol, flags=flags)


def _set_key(name, s):
    return {str(name).lower(), str(s.get("colour") or "").lower()} | {str(a).lower() for a in s.get("aliases", [])}


def cross_check(card, other, tol=10):
    """Per-hole comparison of two cards' matching sets (name / colour / alias): {set: {other_set, mae,
    holes_over_tol: [hole, ...]}}; sets without a counterpart are skipped."""
    out = {}
    osets = (other or {}).get("tee_sets") or {}
    for name, s in ((card or {}).get("tee_sets") or {}).items():
        k = _set_key(name, s) - {""}
        hit = next((n for n, o in osets.items() if k & (_set_key(n, o) - {""})), None)
        if not hit:
            continue
        a, b = s.get("yards") or [], osets[hit].get("yards") or []
        d = [(i + 1, abs(x - y)) for i, (x, y) in enumerate(zip(a, b)) if x and y]
        if not d:
            continue
        out[name] = dict(other_set=hit, mae=round(sum(v for _, v in d) / len(d), 1),
                         holes_over_tol=[h for h, v in d if v > tol])
    return out


def choose_card(cards):
    """cards = [(kind, card, url)] from the web. -> (kind, card, url, consistency) by RELIABILITY: the most
    reliable card that passes `consistency`, else the most reliable one (flagged). Never by map fit."""
    ranked = sorted([c for c in cards if c[1]], key=lambda c: RELIABILITY.index(c[0]) if c[0] in RELIABILITY
                    else len(RELIABILITY))
    if not ranked:
        return None
    checked = [(c, consistency(c[1])) for c in ranked]
    for c, chk in checked:
        if chk["ok"]:
            return (*c, chk)
    c, chk = checked[0]
    return (*c, chk)


# ----------------------------------------------------------------------------- parsers
def parse_golfify(next_data):
    """golfify.io __NEXT_DATA__ (dict or JSON text) -> (card, facility dict)."""
    d = json.loads(next_data) if isinstance(next_data, str) else next_data
    pp = d.get("props", {}).get("pageProps", d)
    tees = pp.get("tees") or []
    fac = pp.get("facility") or {}
    if not tees:
        return None, fac
    sets, par = {}, None
    for t in tees:
        hi = sorted(t.get("holeInformation") or [], key=lambda h: h.get("number", 0))
        if not hi:
            continue
        name = t.get("teeName") or t.get("teeColor") or f"Tee {len(sets) + 1}"
        if name in sets:                                    # golfify lists a set twice for M / W ratings
            base, n = name, 2
            while f"{base} #{n}" in sets:
                n += 1
            name = f"{base} #{n}"
        yards = [h.get("length") for h in hi]
        pars = [h.get("par") for h in hi]
        par = par or pars
        sets[name] = dict(colour=str(t.get("teeColor") or name).lower(),
                          aliases=sorted({str(t.get("teeColor") or "").lower()} - {""}),
                          yards=yards, par=pars, handicap=[h.get("si") for h in hi],
                          total=t.get("totalDistance") or sum(y for y in yards if y),
                          total_stated=t.get("totalDistance"),
                          rating=t.get("rating"), slope=t.get("slope"), source="golfify")
    if not sets:
        return None, fac
    first = next(iter(sets.values()))
    card = dict(schema="scorecard/1", source="golfify.io", par=par, handicap=first.get("handicap"),
                tee_sets=sets, facility={k: fac.get(k) for k in ("clubName", "city", "state", "address",
                                                                 "latitude", "longitude", "numberOfHoles", "website")})
    return card, fac


def parse_opengolfapi(detail):
    """OpenGolfAPI /api/v1/courses/{id} JSON (or a research/raw wrapper {"json": ...}) -> card or None.
    One set per tee colour: tees[] gives name, colour, gender, rating, slope and the stated total;
    holes_data[].yardages{colour} the per-hole yards. A colour listed for both genders keeps the men's
    rating and puts the other in alt_ratings."""
    d = detail.get("json", detail) if isinstance(detail, dict) else None
    if not d:
        return None
    holes = sorted(d.get("holes_data") or [], key=lambda h: h.get("number") or 0)
    if d.get("holes") in (9, 18):                         # the 9-hole Watson course lists 25 rows
        holes = [h for h in holes if 1 <= int(h.get("number") or 0) <= d["holes"]]
    if not holes:
        return None
    per = {}
    for h in holes:
        for col, y in (h.get("yardages") or {}).items():
            per.setdefault(str(col).lower(), {})[int(h["number"])] = y
    n = len(holes)
    sets = {}
    tees = sorted(d.get("tees") or [], key=lambda t: 0 if str(t.get("gender", "")).lower().startswith("m") else 1)
    for t in tees:
        col = str(t.get("tee_color") or t.get("tee_name") or "").lower()
        name = str(t.get("tee_name") or col or "Tee").strip().title()
        if col not in per:
            continue
        if name in sets:
            sets[name].setdefault("alt_ratings", []).append(dict(
                name=f"{name} ({t.get('gender')})", rating=t.get("course_rating"), slope=t.get("slope"),
                total=t.get("yardage"), par=t.get("par")))
            continue
        ys = [per[col].get(i + 1) for i in range(n)]
        sets[name] = dict(colour=col, aliases=sorted({col} - {""}), yards=ys, total=sum(y for y in ys if y),
                          total_stated=t.get("yardage"), rating=t.get("course_rating"), slope=t.get("slope"),
                          gender=t.get("gender"), source="opengolfapi")
    for col, ys_ in per.items():                         # colours with yardages but no tee entry
        if not any(s["colour"] == col for s in sets.values()):
            ys = [ys_.get(i + 1) for i in range(n)]
            sets[col.title()] = dict(colour=col, aliases=[col], yards=ys, total=sum(y for y in ys if y),
                                     source="opengolfapi")
    if not sets:
        return None
    sets = dict(sorted(sets.items(), key=lambda kv: -(kv[1].get("total") or 0)))
    return dict(schema="scorecard/1", source=f"https://api.opengolfapi.org/api/v1/courses/{d.get('id')}",
                par=[h.get("par") for h in holes], handicap=[h.get("handicap_index") for h in holes],
                tee_sets=sets, attribution=OPENGOLFAPI_ATTRIBUTION, licence="ODbL-1.0",
                facility={k: d.get(k) for k in ("id", "course_name", "club_name", "city", "state", "lat", "lng",
                                                "holes", "yardage", "website")})


_NUM = re.compile(r"^\d{1,3}$")
_NUM4 = re.compile(r"^\d{1,4}$")              # row tables carry Out / In / Total columns


def _strip_totals(nums):
    """Per-hole values from a scorecard row, dropping Out / In / Total columns (checked by the sums)."""
    n = len(nums)
    s = sum
    layouts = []
    if n == 21:
        layouts.append((nums[0:9] + nums[10:19], s(nums[0:9]) == nums[9] and s(nums[10:19]) == nums[19]))
    if n == 20:
        layouts.append((nums[0:9] + nums[10:19], s(nums[0:9]) == nums[9] and s(nums[10:19]) == nums[19]))
    if n == 19:
        layouts.append((nums[:18], s(nums[:18]) == nums[18]))
    if n == 18:
        layouts.append((nums, True))
    if n == 11:
        layouts.append((nums[:9], s(nums[:9]) == nums[9]))
    if n == 10:
        layouts.append((nums[:9], s(nums[:9]) == nums[9]))
    if n == 9:
        layouts.append((nums, True))
    for vals, ok in layouts:
        if ok:
            return vals
    return None


def _label_ok(label):
    lw = label.lower()
    return any(c in lw.split() or lw.startswith(c) for c in COLOURS) or "tee" in lw or "yard" in lw


def parse_rows(text):
    """Row-oriented tables: 'Black 391 507 148 ... 3272 ... 6589' and 'Par 4 5 3 ...'."""
    sets, par, hcp = {}, None, None
    for line in text.splitlines():
        toks = line.replace(",", "").split()
        lab, nums = [], []
        for t in toks:
            if _NUM4.match(t) and lab:
                nums.append(int(t))
            elif not nums:
                lab.append(t)
            else:
                break
        label = " ".join(lab).strip(" :")
        if not label or len(nums) < 9:
            continue
        vals = _strip_totals(nums)
        if not vals:
            continue
        ll = label.lower()
        if ll.startswith("par") and all(3 <= v <= 6 for v in vals):
            par = par or vals
        elif re.match(r"(hcp|handicap|hdcp|si|stroke)", ll) and all(1 <= v <= 18 for v in vals):
            hcp = hcp or vals
        elif _label_ok(label) and all(40 <= v <= 720 for v in vals) and label not in sets:
            sets[label.title()] = dict(colour=ll.split()[0], aliases=[ll], yards=vals, total=sum(vals))
            if len(nums) in (19, 21) and nums[-1] > 720:                 # a Total column as printed
                sets[label.title()]["total_stated"] = nums[-1]
    return sets, par, hcp


def parse_columns(text):
    """Hole-per-line tables with a header: 'Hole Gold SI Par Black White ...' then '1 426 3 4 391 ...'."""
    lines = [ln.split() for ln in text.splitlines()]
    best = ({}, None, None)
    for i, hdr in enumerate(lines):
        if not hdr or hdr[0].lower() not in ("hole", "holes", "#"):
            continue
        cols = hdr[1:]
        rows = {}
        for ln in lines[i + 1:i + 30]:
            if ln and ln[0].isdigit() and 1 <= int(ln[0]) <= 18 and len(ln) - 1 == len(cols) \
                    and all(_NUM.match(t) for t in ln[1:]):
                rows[int(ln[0])] = [int(t) for t in ln[1:]]
        if len(rows) not in (9, 18) or sorted(rows) != list(range(1, len(rows) + 1)):
            continue
        sets, par, hcp = {}, None, None
        for j, c in enumerate(cols):
            vals = [rows[h][j] for h in sorted(rows)]
            cl = c.lower()
            if cl == "par":
                par = par or vals
            elif cl in ("si", "hcp", "handicap", "hdcp"):
                hcp = hcp or vals
            elif all(40 <= v <= 720 for v in vals):
                sets[c.title()] = dict(colour=cl, aliases=[cl], yards=vals, total=sum(vals))
        if len(sets) > len(best[0]):
            best = (sets, par, hcp)
    return best


def parse_hole_blocks(text):
    """Hole-by-hole pages: 'Hole #1 ... PAR 4 - 426 - 391 - 376 - 299' (yardages back to front, unnamed)."""
    rows = {}
    for m in re.finditer(r"(?is)hole\s*(?:#|no\.?|number)?\s*(\d{1,2})\b((?:(?!hole).){0,160}?)\bpar\s*:?\s*([3-6])\b"
                         r"((?:\s*[-\u2013\u2014|/,:]?\s*(?:yards?|yds?)?\s*\d{2,3}){1,7})", text):
        h = int(m.group(1))
        ys = [int(v) for v in re.findall(r"\d{2,3}", m.group(4)) if 40 <= int(v) <= 720]
        if 1 <= h <= 18 and ys and h not in rows:
            rows[h] = (int(m.group(3)), ys)
    n = len(rows)
    if n not in (9, 18) or sorted(rows) != list(range(1, n + 1)):
        return {}, None, None
    k = min(len(v[1]) for v in rows.values())
    if any(len(v[1]) != k for v in rows.values()):
        return {}, None, None
    names = ["Back", "Middle", "Forward"] if k == 3 else (["Back", "Forward"] if k == 2 else
                                                         [f"Tee {i + 1}" for i in range(k)])
    sets = {}
    for i in range(k):
        vals = [rows[h][1][i] for h in range(1, n + 1)]
        al = ["back", "tips"] if i == 0 else (["forward", "front"] if i == k - 1 else [])
        sets[names[i]] = dict(colour=names[i].lower(), aliases=al + [f"tee {i + 1}"], yards=vals,
                              total=sum(vals), order=i, note="unnamed on the source: listed back to front")
    return sets, [rows[h][0] for h in range(1, n + 1)], None


def parse_text(text, source="text"):
    """Generic scorecard text (an HTML page or pdftotext output) -> card or None."""
    sets, par, hcp = parse_columns(text)
    s2, p2, h2 = parse_rows(text)
    if len(s2) > len(sets):
        sets, par, hcp = s2, p2 or par, h2 or hcp
    par = par or p2
    if not sets:
        sets, par, hcp = parse_hole_blocks(text)
    if not sets:
        return None
    n = len(next(iter(sets.values()))["yards"])
    sets = {k: dict(v, source=source) for k, v in sets.items() if len(v["yards"]) == n}
    return dict(schema="scorecard/1", source=source, par=par if par and len(par) == n else None,
                handicap=hcp if hcp and len(hcp) == n else None, tee_sets=sets)


def text_of(body):
    body = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", body)
    body = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d|table)>", "\n", body)
    body = re.sub(r"(?i)</t[dh]>", " ", body)
    body = re.sub(r"<[^>]+>", " ", body)
    body = html.unescape(body)
    body = re.sub(r"[ \t\r\f\v]+", " ", body)
    return re.sub(r"\n\s*\n+", "\n", body).strip()


def plausible(card, n_holes=None, osm_lengths=None):
    """Reject parses that can't be this course (hole count, wildly different lengths)."""
    if not card or not card.get("tee_sets"):
        return False
    n = len(next(iter(card["tee_sets"].values()))["yards"])
    if n_holes and n_holes in (9, 18) and not (n == n_holes or (n_holes == 9 and n == 18)):
        return False
    if osm_lengths:
        longest = max(card["tee_sets"].values(), key=lambda s: s.get("total") or 0)["yards"]
        diffs = [abs(longest[int(r) - 1] - L) / max(L, 1) for r, L in osm_lengths.items()
                 if str(r).isdigit() and int(r) - 1 < len(longest) and longest[int(r) - 1]]
        if diffs and sorted(diffs)[len(diffs) // 2] > 0.25:
            return False
    return True


# ----------------------------------------------------------------------------- fetchers (Actions)
def _session():
    import requests
    s = requests.Session()
    s.headers.update({"User-Agent": BROWSER_UA, "Accept-Language": "en-US,en;q=0.9"})
    return s


def _save(raw_dir, url, r):
    os.makedirs(raw_dir, exist_ok=True)
    key = hashlib.sha1(url.encode()).hexdigest()[:10]
    is_pdf = "pdf" in r.headers.get("content-type", "") or url.lower().endswith(".pdf")
    if is_pdf:
        p = os.path.join(raw_dir, key + ".pdf")
        with open(p, "wb") as fh:
            fh.write(r.content)
        txt = os.path.join(raw_dir, key + ".txt")
        try:
            subprocess.run(["pdftotext", "-layout", p, txt], check=True, timeout=60)
            text = open(txt).read()
        except Exception as e:                            # noqa: BLE001
            text = ""
            pc.log("pdftotext failed", e)
        os.remove(p)                                       # keep the text only (copyright, size)
    else:
        text = text_of(r.text)
        with open(os.path.join(raw_dir, key + ".txt"), "w") as fh:
            fh.write(f"URL: {url}\n\n{text}")
    idx_p = os.path.join(raw_dir, "index.json")
    idx = pc.read_json(idx_p, {})
    idx[url] = dict(status=r.status_code, file=key + ".txt", bytes=len(r.content))
    pc.write_json(idx_p, idx)
    return text


def golfify_slugs(name, town=None):
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    core = re.sub(r"[^a-z0-9]+", "-", pc.core_name(name)).strip("-")
    out = [base, f"{core}-golf-course", f"{core}-golf-club", f"{core}-country-club", core]
    if town:
        t = re.sub(r"[^a-z0-9]+", "-", town.lower()).strip("-")
        out += [f"{base}-{t}", f"{core}-golf-course-{t}", f"{core}-{t}"]
    out += [f"{core}-golf-links", f"{core}-golf-and-country-club", f"{core}-recreation-park-golf-course"]
    seen = []
    for s in out:
        if s and s not in seen:
            seen.append(s)
    return seen


def ddg_urls(query, host):
    """Result URLs on `host` from DuckDuckGo's HTML endpoint and Bing (best effort; may be rate-limited)."""
    s = _session()
    hrefs = []
    for url in ("https://html.duckduckgo.com/html/?q=" + quote_plus(query),
                "https://www.bing.com/search?q=" + quote_plus(query)):
        try:
            r = s.get(url, timeout=30)
            hrefs += re.findall(r'href="([^"]+)"', r.text)
        except Exception as e:                            # noqa: BLE001
            pc.log("search failed", url, e)
    out = []
    for h in hrefs:
        h = html.unescape(h)
        m = re.search(r"uddg=([^&]+)", h)
        if m:
            from urllib.parse import unquote
            h = unquote(m.group(1))
        if host in urlparse(h).netloc and h not in out:
            out.append(h)
    return out


def fetch_golfify(name, state, town, raw_dir, center=None):
    """-> (card, url) or (None, reason). Derived URLs first (`golfify_urls`), then a web search; the page
    must pass `page_matches` (state, fuzzy name, distance when center [lon, lat] is given)."""
    s = _session()
    st = pc.STATES[pc.state_code(state)].lower()
    urls = golfify_urls(name, town, limit=10)
    tried = []
    for extra in (None, "search"):
        if extra == "search":
            urls = [u for u in ddg_urls(f"golfify {name} {town or ''} {st} scorecard", "golfify.io")
                    if "/courses/" in u and u not in tried][:5]
        for u in urls:
            tried.append(u)
            try:
                r = s.get(u, timeout=30)
            except Exception as e:                        # noqa: BLE001
                pc.log("golfify", u, e)
                continue
            time.sleep(1)
            if r.status_code != 200:
                continue
            m = re.search(r'(?is)<script[^>]*__NEXT_DATA__[^>]*>(.*?)</script>', r.text)
            if not m:
                continue
            _save(raw_dir, u, r)
            try:
                card, fac = parse_golfify(m.group(1))
            except Exception as e:                        # noqa: BLE001
                pc.log("golfify parse", u, e)
                continue
            ok, how = page_matches(golfify_page_info(fac), name, state, town, center)
            if card and ok:
                card["source"] = u
                for ts in card["tee_sets"].values():
                    ts["source"] = u
                return card, u
            pc.log("golfify: not this course or no tees", u, how)
    return None, f"golfify: no matching page ({len(tried)} URLs tried)"


# ----------------------------------------------------------------------------- derived directory URLs (no search engine)
# Card discovery that does not need DuckDuckGo / Bing (both bot-challenge GitHub runners after a few queries):
# golfify and AllSquare put the course page at a URL built from the course name (CARDS.md):
#   golfify    https://www.golfify.io/courses/<name-slug>[-<town>]          (__NEXT_DATA__ pageProps.tees, yards)
#   AllSquare  https://www.allsquaregolf.com/golf-courses/<state-name>/<name-slug>   (__NEXT_DATA__ apolloState
#              Teebox.distances in YARDS; the HTML table shows METRES on first render)
# A fetched page must pass `page_matches` (fuzzy name + state, + town or distance when known).
M_PER_YD = 0.9144


def metres_to_yards(m):
    """AllSquare's rendered table is in metres: 379 m -> 414 yd (rounded like their own toggle)."""
    return None if m is None else int(round(float(m) / M_PER_YD))


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower().replace("&", " and ").replace("'", "")).strip("-")


def _name_variants(name):
    """'A.L. Gustin Jr. Golf Course' -> slugs a-l-gustin-jr-golf-course, a-l-gustin-golf-course, al-gustin-..."""
    base = _slug(name)
    out = [base]
    no_the = re.sub(r"^the-", "", base)
    out.append(no_the)
    out.append(re.sub(r"-(jr|sr|ii|iii)(?=-|$)", "", base))               # 'Jr.' often dropped
    out.append(re.sub(r"\b([a-z])-(?=[a-z]-)", r"\1", base))            # a-l-gustin -> al-gustin
    core = _slug(pc.core_name(str(name).replace("'", "").replace("\u2019", "")))
    if core:
        m = re.match(r"^the-golf-club-at-(.+)$", base)                     # 'The Golf Club at Creekmoor'
        if m:
            out += [f"{m.group(1)}-golf-club", f"golf-club-at-{m.group(1)}"]
        out += [f"{core}-golf-course", f"{core}-golf-club", f"{core}-country-club"]
    if base == no_the:
        out.insert(min(len(out), 3), "the-" + base)                       # golfify: the-harvester-golf-club
    seen = []
    for s in out:
        if s and s not in seen:
            seen.append(s)
    return seen


def golfify_urls(name, town=None, limit=10):
    """golfify course-page URLs to try, best first (exact name slug, its variants, then '-<town>' forms that
    golfify uses when two facilities share a name: st-andrews-golf-club-overland-park)."""
    slugs = _name_variants(name)
    if town:
        t = _slug(town)
        slugs += [f"{s}-{t}" for s in slugs if not s.startswith("the-")][:4]
    for s in golfify_slugs(name, town):
        if s not in slugs:
            slugs.append(s)
    return [f"https://www.golfify.io/courses/{s}" for s in slugs[:limit]]


def allsquare_urls(name, state, limit=4):
    """AllSquare course-page URLs: /golf-courses/<state name>/<name slug>. A slug clash gets '-<id>' appended
    on AllSquare (elks-country-club-27821), which cannot be derived: those need search."""
    st = _slug(pc.STATES[pc.state_code(state)])
    return [f"https://www.allsquaregolf.com/golf-courses/{st}/{s}" for s in _name_variants(name)[:limit]]


def derived_card_urls(name, state, town=None):
    return dict(golfify=golfify_urls(name, town), allsquare=allsquare_urls(name, state))


def _tokens(s):
    stop = {"golf", "course", "club", "country", "the", "at", "and", "links", "gc", "cc", "of", "jr", "sr",
            "municipal", "muni", "resort", "community", "public"}
    toks = set()
    for w in re.split(r"[^a-z0-9]+", str(s or "").lower().replace(".", "")):
        if w and w not in stop:
            toks.add(w)
    return toks


def name_similarity(a, b):
    """Token overlap of the distinctive name words (Jaccard; initials 'A. L.' == 'AL', "Dub's" == 'dubs')."""
    def norm(x):
        words = re.split(r"[^a-z0-9]+", str(x or "").lower().replace("'", "").replace("\u2019", ""))
        merged, run = [], ""
        for w in words + [""]:
            if len(w) == 1:
                run += w
                continue
            if run:
                merged.append(run)
                run = ""
            if w:
                merged.append(w)
        return _tokens(" ".join(merged))
    ta, tb = norm(a), norm(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def page_matches(page, name, state, town=None, center=None, min_sim=0.5, max_km=8.0):
    """Is a directory page (dict name, state, city, lat, lon) this course? -> (ok, why). The state must match;
    the name must be similar; when both carry a position it must be within max_km, else the town must match
    when the names are only partly similar."""
    st = pc.state_code(state)
    pst = pc.state_code(page.get("state")) if page.get("state") else None
    if pst and pst != st:
        return False, f"state {page.get('state')} != {st}"
    sim = name_similarity(page.get("name"), name)
    if sim < min_sim:
        return False, f"name '{page.get('name')}' vs '{name}' similarity {sim:.2f}"
    if center and page.get("lat") is not None and page.get("lon") is not None:
        km = _km(center, (float(page["lon"]), float(page["lat"])))
        if km > max_km:
            return False, f"{km:.1f} km from the course"
        return True, f"name {sim:.2f}, {km:.1f} km"
    if sim < 1.0 and town and page.get("city") and _slug(town) != _slug(page["city"]):
        return False, f"town {page.get('city')} != {town} and name only {sim:.2f}"
    if not pst:
        return False, "page has no state"
    return True, f"name {sim:.2f}, state {st}"


def golfify_page_info(fac):
    return dict(name=fac.get("clubName"), state=fac.get("state"), city=fac.get("city"),
                lat=fac.get("latitude"), lon=fac.get("longitude"))


def _next_data(html_text):
    m = re.search(r'(?is)<script[^>]*__NEXT_DATA__[^>]*>(.*?)</script>', html_text or "")
    return json.loads(m.group(1)) if m else None


def parse_allsquare(page_html):
    """AllSquare course page -> (card | None, page info {name, state, city, lat, lon, last_edit}).
    Reads __NEXT_DATA__ apolloState: Club (zipcode 'IA 52242' gives the state), Scorecard.grid[] (par,
    handicap, Men/Women teebox groups) and Teebox.distances (yards). Without that JSON the rendered table is
    read and its metres converted to yards."""
    d = _next_data(page_html)
    if not d:
        return _allsquare_table(page_html)
    a = (d.get("props") or {}).get("apolloState") or {}
    slug = ((d.get("query") or {}).get("slug") or "")
    clubs = [v for k, v in a.items() if k.startswith("Club:") and "zipcode" in v]
    club = next((c for c in clubs if c.get("slug") == slug), clubs[0] if clubs else {})
    zm = re.match(r"\s*([A-Z]{2})\b", str(club.get("zipcode") or ""))
    info = dict(name=club.get("name"), state=zm.group(1) if zm else None, city=club.get("city"),
                lat=club.get("latitude"), lon=club.get("longitude"), slug=club.get("slug"))
    cards = sorted([v for k, v in a.items() if k.startswith("Scorecard:")], key=lambda s: s.get("position") or 0)
    if not cards:
        return None, info
    sc = cards[0]
    info["last_edit"] = sc.get("lastEdit")
    info["scorecards"] = [c.get("name") for c in cards]
    sets, par, hcp = {}, None, None
    n = sc.get("holesCount")
    for grp in sc.get("grid") or []:
        gpar, ghcp = grp.get("par"), grp.get("handicap")
        men = str(grp.get("teeboxType") or "").lower().startswith("men")
        if gpar and (par is None or men):
            par = par if (par and not men) else gpar
        if ghcp and men and hcp is None:
            hcp = ghcp
        for ref in grp.get("teeboxes") or []:
            t = a.get(ref.get("__ref") if isinstance(ref, dict) else ref) or {}
            ys = [int(y) if y else None for y in (t.get("distances") or [])]
            if not ys or not any(ys):
                continue
            col = a.get(((t.get("color") or {}).get("__ref")) or "", {}).get("name") or t.get("name")
            name = str(t.get("name") or col or f"Tee {len(sets) + 1}").strip()
            if name in sets:
                if sets[name]["yards"] == ys:
                    sets[name].setdefault("alt_ratings", []).append(dict(
                        name=f"{name} ({grp.get('teeboxType')})", rating=t.get("rating"), slope=t.get("slope")))
                    continue
                name = f"{name} ({grp.get('teeboxType')})"
            sets[name] = dict(colour=str(col or name).lower(), aliases=sorted({str(col or "").lower()} - {""}),
                              yards=ys, par=gpar, total=sum(y for y in ys if y), rating=t.get("rating"),
                              slope=t.get("slope"), source="allsquare", teebox_type=grp.get("teeboxType"))
    if not sets:
        return None, info
    if n:
        sets = {k: v for k, v in sets.items() if len(v["yards"]) == n} or sets
    sets = dict(sorted(sets.items(), key=lambda kv: -(kv[1]["total"] or 0)))
    card = dict(schema="scorecard/1", source="allsquaregolf.com", par=par, handicap=hcp, tee_sets=sets,
                facility=info, card_name=sc.get("name"),
                card_date=time.strftime("%Y-%m-%d", time.gmtime(sc["lastEdit"] / 1000)) if sc.get("lastEdit") else None)
    return card, info


def _allsquare_table(page_html):
    """Fallback: the rendered scorecard table (metres when the Meters toggle is active) -> yards."""
    metres = re.search(r'as-button--primary-flat[^>]*>\s*Meters', page_html or "") is not None
    card = parse_text(text_of(page_html or ""), source="allsquaregolf.com")
    if card and metres:
        for s in card["tee_sets"].values():
            s["yards"] = [metres_to_yards(y) for y in s["yards"]]
            s["total"] = sum(y for y in s["yards"] if y)
            s.pop("total_stated", None)
            s["note"] = "converted from metres"
    return card, {}


def fetch_allsquare(name, state, town, raw_dir, center=None, get=None):
    """AllSquare by derived URL (no search) -> (card, url) or (None, reason)."""
    s = None if get else _session()
    get = get or (lambda u: s.get(u, timeout=30))
    why = []
    for u in allsquare_urls(name, state):
        try:
            r = get(u)
        except Exception as e:                            # noqa: BLE001
            why.append(f"{u}: {e!r}"[:120])
            continue
        time.sleep(1)
        if r.status_code != 200:
            why.append(f"{u.rsplit('/', 1)[-1]}: HTTP {r.status_code}")
            continue
        _save(raw_dir, u, r)
        card, info = parse_allsquare(r.text)
        ok, how = page_matches(info, name, state, town, center)
        if not ok:
            why.append(f"{u.rsplit('/', 1)[-1]}: {how}")
            continue
        if card:
            card["source"] = u
            for ts in card["tee_sets"].values():
                ts["source"] = u
            return card, u
        why.append(f"{u.rsplit('/', 1)[-1]}: no scorecard on the page")
    return None, ("allsquare: " + "; ".join(why))[:300]


SCORE_LINK = re.compile(r"(?i)score|card|\.pdf|hole|tee|yard|course-info|the-course|layout")
SKIP_LINK = re.compile(r"(?i)instagram|facebook|twitter|youtube|foreup|teesnap|chronogolf|\.css|\.js|\.jpg|\.png|"
                       r"mailto:|tel:|login|cart|book|tee-?time|event|wedding|menu|news|blog")


def fetch_club_site(website, raw_dir, n_holes=None, osm_lengths=None, max_pages=24):
    """Club website + its scorecard-looking links (one level) -> (card, url) or (None, reason)."""
    if not website:
        return None, "no website tag in OSM"
    if not website.startswith("http"):
        website = "https://" + website
    s = _session()
    try:
        r = s.get(website, timeout=30)
    except Exception as e:                                # noqa: BLE001
        return None, f"club site unreachable: {e!r}"[:200]
    pages = [(website, r)]
    host = urlparse(r.url).netloc
    links = []
    for href in re.findall(r'href="([^"#]+)"', r.text):
        u = urljoin(r.url, html.unescape(href))
        if (urlparse(u).netloc in (host, "") or u.lower().endswith(".pdf")) and SCORE_LINK.search(u) \
                and not SKIP_LINK.search(u) and u not in links:
            links.append(u)
    root = f"{urlparse(r.url).scheme}://{host}"
    base_path = r.url.rstrip("/")
    for guess in ("/scorecard", "/score-card", "/course", "/the-course", "/course-info", "/golf/scorecard",
                  "/golf/course", "/hole-by-hole", "/golf/hole-by-hole", "/course-tour"):
        for u in (root + guess, base_path + guess):
            if u not in links:
                links.append(u)
    links.sort(key=lambda u: (0 if re.search(r"(?i)scorecard|score-card", u) else
                              1 if re.search(r"(?i)\.pdf|card", u) else 2))
    for u in links[:max_pages]:
        try:
            pages.append((u, s.get(u, timeout=30)))
            time.sleep(0.5)
        except Exception as e:                            # noqa: BLE001
            pc.log("club page", u, e)
    best = None
    for u, rr in pages:
        if rr.status_code != 200:
            continue
        text = _save(raw_dir, u, rr)
        card = parse_text(text, source=u)
        if plausible(card, n_holes, osm_lengths):
            if best is None or len(card["tee_sets"]) > len(best[0]["tee_sets"]):
                best = (card, u)
    return best if best else (None, f"club site: no parsable scorecard in {len(pages)} pages")


# ----------------------------------------------------------------------------- course directories (Actions)
# label -> (host, regex for a course page URL on the host (group 1 = the course key), scorecard URL from the key)
DIRECTORIES = {
    "bluegolf": ("bluegolf.com", r"https?://course\.bluegolf\.com/bluegolf/course/course/([a-z0-9]+)/",
                 "https://course.bluegolf.com/bluegolf/course/course/{}/detailedscorecard.htm"),
    "golfpass": ("golfpass.com", r"https?://www\.golfpass\.com/travel-advisor/courses/(\d+-[a-z0-9-]+)",
                 "https://www.golfpass.com/travel-advisor/courses/{}/scorecard-and-layout"),
    "allsquare": ("allsquaregolf.com", r"https?://allsquaregolf\.com/golf-courses/([a-z0-9-]+/[a-z0-9-]+/[a-z0-9-]+)",
                  "https://allsquaregolf.com/golf-courses/{}/scorecard"),
}


def directory_urls(label, name, state, town=None, search=None):
    """Scorecard URLs on a directory site for this course, from a web search (best first, at most 3)."""
    host, pat, fmt = DIRECTORIES[label]
    st = pc.STATES[pc.state_code(state)]
    search = search or ddg_urls
    out = []
    for q in (f"{name} {town or ''} {st} scorecard site:{host}", f"{pc.core_name(name)} golf {town or st} {host}"):
        for u in search(q, host):
            m = re.match(pat, u)
            if m and fmt.format(m.group(1)) not in out:
                out.append(fmt.format(m.group(1)))
        if out:
            break
        time.sleep(3)
    return out[:3]


def _names_course(text, name, state, town=None):
    """The page is about this course: half its distinctive name tokens and its state (or town) appear."""
    low = text.lower()
    toks = [t for t in _name_tokens(name) if len(t) > 2]
    st = pc.state_code(state)
    where = (pc.STATES[st].lower() in low or re.search(rf"\b{st}\b", text) is not None
             or (town and town.lower() in low))
    return bool(where) and (not toks or sum(t in low for t in toks) >= max(1, (len(toks) + 1) // 2))


def fetch_directory(label, name, state, town, raw_dir, n_holes=None, osm_lengths=None, search=None, get=None):
    """One directory site (DIRECTORIES) -> (card, url) or (None, reason)."""
    urls = directory_urls(label, name, state, town, search=search)
    if not urls:
        return None, f"{label}: no course page found by search"
    s = None if get else _session()
    get = get or (lambda u: s.get(u, timeout=30))
    for u in urls:
        try:
            r = get(u)
        except Exception as e:                            # noqa: BLE001
            pc.log(label, u, e)
            continue
        time.sleep(1)
        if r.status_code != 200:
            continue
        text = _save(raw_dir, u, r)
        if not _names_course(text, name, state, town):
            pc.log(f"{label}: page does not name the course / state", u)
            continue
        card = parse_text(text, source=u)
        if plausible(card, n_holes, osm_lengths):
            for ts in card["tee_sets"].values():
                ts["source"] = u
            return card, u
    return None, f"{label}: no parsable scorecard ({len(urls)} page(s): {', '.join(urls)})"[:300]


# ----------------------------------------------------------------------------- OpenGolfAPI (Actions)
OPENGOLFAPI = "https://api.opengolfapi.org"
OPENGOLFAPI_UA = "my_golf_data_science course package builder (GitHub Actions; contact via the repo)"
OPENGOLFAPI_MIN_INTERVAL_S = 1.1           # well under 1,000 anonymous calls/day/IP
_last_call = [0.0]


def _name_tokens(name):
    stop = {"golf", "course", "club", "country", "the", "at", "and", "links", "memorial", "gc", "cc"}
    return {w for w in re.split(r"[^a-z0-9]+", str(name).lower()) if w and w not in stop}


def _km(a_lonlat, b_lonlat):
    import math
    la = math.radians((a_lonlat[1] + b_lonlat[1]) / 2)
    return math.hypot((a_lonlat[0] - b_lonlat[0]) * math.cos(la), a_lonlat[1] - b_lonlat[1]) * 111.32


def pick_opengolfapi_candidate(cands, name, state, center=None, max_km=5.0):
    """Best search hit: same state, shares a name word, and (when center [lon, lat] is known) within max_km.
    -> (candidate | None, reason)."""
    want = _name_tokens(name)
    st = pc.state_code(state).upper() if state else None
    best = None
    for c in cands or []:
        if st and str(c.get("state", "")).upper() not in (st, str(pc.STATES.get(st, st)).upper()):
            continue
        overlap = len(want & _name_tokens(c.get("course_name") or c.get("name") or ""))
        if not overlap:
            continue
        km = None
        if center and c.get("latitude") is not None and c.get("longitude") is not None:
            km = _km(center, (c["longitude"], c["latitude"]))
            if km > max_km:
                continue
        score = (overlap, -(km if km is not None else max_km))
        if best is None or score > best[0]:
            best = (score, c, km)
    if best is None:
        return None, f"opengolfapi: no candidate in {state} matching '{name}'" + (f" within {max_km} km" if center else "")
    return best[1], f"opengolfapi: {best[1].get('course_name') or best[1].get('name')} ({best[2] and round(best[2], 2)} km)"


def _oga_get(session, url, sleep=time.sleep, now=time.time):
    """GET with the anonymous-tier courtesy interval and one Retry-After wait on 429."""
    for attempt in (0, 1):
        wait = OPENGOLFAPI_MIN_INTERVAL_S - (now() - _last_call[0])
        if wait > 0:
            sleep(wait)
        r = session.get(url, timeout=30, headers={"User-Agent": OPENGOLFAPI_UA, "Accept": "application/json"})
        _last_call[0] = now()
        if r.status_code == 429 and attempt == 0:
            try:
                ra = float(r.headers.get("Retry-After", 30))
            except ValueError:
                ra = 30.0
            sleep(min(max(ra, 1.0), 60.0))
            continue
        return r
    return r


def fetch_opengolfapi(name, state, center, raw_dir, session=None, sleep=time.sleep, max_calls=4, course_id=None):
    """OpenGolfAPI search + detail (GitHub Actions only) -> (card, url) or (None, reason). At most
    max_calls requests; raw JSON saved to raw_dir/opengolfapi_*.json (ODbL: keep the attribution).
    course_id: the request's pinned OpenGolfAPI id (e.g. one club's second course): no search."""
    s = session or _session()
    os.makedirs(raw_dir, exist_ok=True)
    calls = 0
    if course_id:
        return _opengolfapi_detail(s, dict(id=course_id, course_name=name), raw_dir, "pinned by the request", sleep)
    core = pc.core_name(name) if hasattr(pc, "core_name") else name
    queries = [core, name] if core and core != name else [name]
    cand, why = None, "opengolfapi: not tried"
    for q in queries:
        if calls >= max_calls:
            break
        url = f"{OPENGOLFAPI}/v1/courses/search?q={quote_plus(q)}&state={pc.state_code(state)}&limit=20"
        r = _oga_get(s, url, sleep=sleep)
        calls += 1
        if r.status_code != 200:
            why = f"opengolfapi search HTTP {r.status_code}"
            continue
        js = r.json()
        pc.write_json(os.path.join(raw_dir, "opengolfapi_search.json"), dict(url=url, json=js))
        cand, why = pick_opengolfapi_candidate(js.get("courses") or [], name, state, center)
        if cand:
            break
    if not cand:
        return None, why
    return _opengolfapi_detail(s, cand, raw_dir, why, sleep)


def _opengolfapi_detail(s, cand, raw_dir, why, sleep=time.sleep):
    url = f"{OPENGOLFAPI}/api/v1/courses/{cand['id']}"
    r = _oga_get(s, url, sleep=sleep)
    if r.status_code != 200:
        return None, f"opengolfapi detail HTTP {r.status_code} ({why})"
    js = r.json()
    pc.write_json(os.path.join(raw_dir, f"opengolfapi_{cand['id']}.json"), dict(url=url, json=js))
    card = parse_opengolfapi(js)
    if not card:
        return None, f"opengolfapi: no tees / holes_data for {cand.get('course_name')} ({why})"
    card["source"] = url
    return card, url
