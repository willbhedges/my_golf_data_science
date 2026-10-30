"""Course-review fixes in a library folder -> extra course-page request keys (course_page.py request / pkgreq).

A review agent leaves, in course_data/library/<slug>/:
  review.json            {"course_review/1": {...}} (or the body bare): holes [{n, verdict, notes, fix}] where
                         fix = {"tee_ll": {set: [lat, lon]}, "yards": 399 | {set: 399}, "yards_by_set": {set: y},
                         "par": 4, "green_ll", "renumber_as"}; course_notes / summary text ("tees ['Gold', 'Black']");
                         "rebuild_hint" (top level or in summary) {yardages, pars, tees, osm_supplement, scorecard};
                         "page_set_should_be" ("Black, Blue"); "ignore_osm_holes: true" in the notes
  card_review.json, card_fix.json, card_golfify.json, card_*.json   scorecard/1 full cards
  osm_supplement.geojson hand-mapped golf=hole / tee / green features (fetch_package.py "osm_supplement")
library_request(folder) -> {scorecard, osm_supplement, tees, tee_overrides {ref: {set: [lat, lon]}},
yardage_overrides {ref: {set | "*": yds}}, par_overrides {ref: par}, yardages, pars, ...}. A set name the
rebuilt card does not have ("Web", "osm_back") or "*" means the solved set (platform/package.py override_set).
Not applied: green_ll (the build takes greens from OSM; map them with an osm_supplement) and holes with
"renumber_as" (a routing fix: the hole's other fixes refer to the old number, so they are skipped too).
"""
import glob
import json
import os
import re

CARD_FILES = ("card_review.json", "card_fix.json", "card_golfify.json")
HINT_KEYS = ("yardages", "pars", "tees", "scorecard", "osm_supplement", "typed_card", "near", "osm", "ignore_osm_holes")


def _read(p):
    try:
        with open(p) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def load_review(folder):
    """review.json in its schema variants -> {holes: {ref: {verdict, tee_ll, yards, par}}, tees, hint, notes}."""
    d = _read(os.path.join(folder, "review.json"))
    if not isinstance(d, dict):
        return None
    d = d.get("course_review/1", d)
    holes, skipped = {}, []
    raw = d.get("holes") or []
    items = raw.items() if isinstance(raw, dict) else ((h.get("n") or h.get("hole") or h.get("ref"), h) for h in raw)
    for ref, h in items:
        if not isinstance(h, dict) or ref is None:
            continue
        ref = str(ref)
        f = h.get("fix") or {}
        if not isinstance(f, dict):
            f = {}
        if f.get("renumber_as") is not None:
            skipped.append(f"hole {ref}: renumber_as {f['renumber_as']} (routing fix; not applied)")
            continue
        e = dict(verdict=h.get("verdict"))
        if isinstance(f.get("tee_ll"), dict):
            e["tee_ll"] = {s: ll for s, ll in f["tee_ll"].items() if isinstance(ll, (list, tuple)) and len(ll) >= 2}
        y = f.get("yards_by_set") or f.get("yards")
        if isinstance(y, dict):
            e["yards"] = {s: int(v) for s, v in y.items() if v}
        elif y:
            e["yards"] = {"*": int(y)}
        if f.get("par"):
            e["par"] = int(f["par"])
        if f.get("green_ll"):
            skipped.append(f"hole {ref}: green_ll (greens come from OSM; not applied)")
        holes[ref] = e
    summ = d.get("summary") if isinstance(d.get("summary"), dict) else {}
    texts = [x for k in ("course_notes", "summary", "course_level", "rebuild_advice", "publish") for x in
             (d.get(k) if isinstance(d.get(k), list) else [d.get(k)]) if isinstance(x, str)]
    texts += [x for x in summ.values() if isinstance(x, str)]
    hint = {k: v for k, v in (d.get("rebuild_hint") or summ.get("rebuild_hint") or {}).items() if k in HINT_KEYS and v}
    if any(re.search(r"ignore_osm_holes\W+true", t) for t in texts):
        hint["ignore_osm_holes"] = True
    for k in ("yardages", "pars"):                              # "430 386 206 ..." -> [430, 386, 206, ...]
        if isinstance(hint.get(k), str):
            hint[k] = [int(x) for x in re.findall(r"\d+", hint[k])]
    tees = hint.pop("tees", None) or d.get("tees") or _tees_in(texts) or d.get("page_set_should_be")
    if isinstance(tees, str):
        tees = [t.strip() for t in tees.split(",") if t.strip()]
    return dict(holes=holes, tees=tees, hint=hint, skipped=skipped, publish=d.get("publish", d.get("publish_as_is")))


def _tees_in(texts):
    """'... tees ['Gold', 'Black'] ...' in a review's notes -> ['Gold', 'Black']."""
    for t in texts:
        m = re.search(r"\btees\s*\[([^\]]+)\]", t)
        if m:
            names = re.findall(r"['\"]([^'\"]+)['\"]", m.group(1))
            if names:
                return names
    return None


def card_file(folder):
    """The folder's scorecard/1 file (card_review > card_fix > card_golfify > other card_*.json)."""
    rest = sorted(os.path.basename(p) for p in glob.glob(os.path.join(folder, "card_*.json")))
    for name in list(CARD_FILES) + [n for n in rest if n not in CARD_FILES]:
        c = _read(os.path.join(folder, name))
        if isinstance(c, dict) and c.get("tee_sets"):
            return os.path.join(folder, name)
    return None


def library_request(folder, root):
    """Request keys from the folder's review files (paths relative to root); {} when there is nothing."""
    rel = lambda p: os.path.relpath(p, root)                    # noqa: E731
    out, used = {}, []
    card = card_file(folder)
    if card:
        out["scorecard"] = rel(card)
        used.append(os.path.basename(card))
    sup = os.path.join(folder, "osm_supplement.geojson")
    if os.path.exists(sup):
        out["osm_supplement"] = rel(sup)
        used.append("osm_supplement.geojson")
    rv = load_review(folder)
    if rv:
        used.append("review.json")
        out.update(rv["hint"])
        if rv["tees"]:
            out["tees"] = rv["tees"]
        tees = {r: h["tee_ll"] for r, h in rv["holes"].items() if h.get("tee_ll")}
        yards = {r: h["yards"] for r, h in rv["holes"].items() if h.get("yards")}
        pars = {r: h["par"] for r, h in rv["holes"].items() if h.get("par")}
        if tees:
            out["tee_overrides"] = tees
        if yards:
            out["yardage_overrides"] = yards
        if pars:
            out["par_overrides"] = pars
        if rv["skipped"]:
            out["review_not_applied"] = rv["skipped"]
    if out:
        out["library_fixes"] = used
    return out


def merge(q, folder, root):
    """q with the folder's review fixes; the request's own keys win. q["library_fixes"] = False opts out."""
    if q.get("library_fixes") is False or not os.path.isdir(folder):
        return q
    extra = library_request(folder, root)
    if q.get("scorecard") or q.get("yardages") or q.get("typed_card"):
        extra.pop("scorecard", None)                            # the request's own card wins
    return dict(extra, **q) if extra else q
