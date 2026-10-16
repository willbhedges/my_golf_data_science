"""Scorecards for any course: sources, parsing, and choosing the golfer's tee set.

Normalised card (the shape of course_data/tees/scorecard.json, which pipeline._norm_card also reads):

  {"schema": "scorecard/1", "source": "<url or file>", "par": [18], "handicap": [18] | null,
   "tee_sets": {"Black": {"colour": "black", "aliases": [...], "yards": [18], "par": [18] | absent,
                          "total": 6589, "rating": 71.4, "slope": 124, "source": "..."}}}

Sources, in the order package.py tries them (fetch_* need the web, i.e. GitHub Actions):
  1. request yardages        request["yardages"] = [..] or {"1": 391, ...} (+ optional "pars")
  2. local card file         request["scorecard"] = "course_data/tees/scorecard.json" (tees/ format)
  3. golfify.io              structured Next.js JSON (tees[].holeInformation); slug guesses, then a
                             DuckDuckGo site: search; the facility's state must match
  4. the club website        OSM website=* page + links that look like a scorecard (html or pdf), parsed
                             with the generic text-table parser (`parse_text`)
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
        s.setdefault("total", sum(y for y in s["yards"] if y))
        sets[name] = s
    out["tee_sets"] = sets
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
                          rating=t.get("rating"), slope=t.get("slope"), source="golfify")
    if not sets:
        return None, fac
    first = next(iter(sets.values()))
    card = dict(schema="scorecard/1", source="golfify.io", par=par, handicap=first.get("handicap"),
                tee_sets=sets, facility={k: fac.get(k) for k in ("clubName", "city", "state", "address",
                                                                 "latitude", "longitude", "numberOfHoles", "website")})
    return card, fac


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


def fetch_golfify(name, state, town, raw_dir):
    """-> (card, url) or (None, reason)."""
    s = _session()
    st = pc.STATES[pc.state_code(state)].lower()
    urls = [f"https://www.golfify.io/courses/{g}" for g in golfify_slugs(name, town)]
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
            if card and str(fac.get("state", "")).lower() in (st, pc.state_code(state).lower()):
                card["source"] = u
                for ts in card["tee_sets"].values():
                    ts["source"] = u
                return card, u
            pc.log("golfify: wrong state or no tees", u, fac.get("state"))
    return None, f"golfify: no matching page ({len(tried)} URLs tried)"


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
