"""Course-review fixes in a library folder -> extra course-page request keys (course_page.py request / pkgreq).

A review agent leaves, in course_data/library/<slug>/:
  review.json            {"course_review/1": {...}} (or the body bare): holes [{n, verdict, notes, fix}] where
                         fix = {"tee_ll": {set: [lat, lon]}, "yards": 399 | {set: 399}, "yards_by_set": {set: y},
                         (a bare "yards" goes to the set tee_ll names, else "*" only on a single-set rebuild,
                         else it is dropped into review_not_applied: _bare_yards)
                         "par": 4, "green_ll", "renumber_as"}; course_notes / summary text ("tees ['Gold', 'Black']");
                         "rebuild_hint" (top level or in summary) {yardages, pars, tees, osm_supplement, scorecard};
                         "page_set_should_be" ("Black, Blue"); "ignore_osm_holes: true" in the notes
  card_review.json, card_fix.json, card_golfify.json, card_*.json   scorecard/1 full cards
  osm_supplement.geojson hand-mapped golf=hole / tee / green features (fetch_package.py "osm_supplement")
library_request(folder) -> {scorecard, osm_supplement, tees, tee_overrides {ref: {set: [lat, lon]}},
yardage_overrides {ref: {set | "*": yds}}, par_overrides {ref: par}, green_overrides {ref: [lat, lon]},
hole_renumber {page ref: {to: card ref, near_ll: [lat, lon]} | card ref}, yardages, pars, ...}. A set name the
rebuilt card does not have ("Web", "osm_back") or "*" means the solved set (platform/package.py override_set).
Renumbering (platform/package.py apply_hole_renumber): "renumber": {"page_to_card": {...}} or a hole's fix
"renumber_as" / "card_hole" maps the page's (OSM / router) hole number to the card's; every per-hole fix is
re-keyed to the card number (the build applies overrides after renumbering). With "ignore_osm_holes" and an
osm_supplement the supplement's ways are taken as already card-numbered, so no hole_renumber is sent.
green_ll (platform/package.py apply_green_overrides): the hole line ends on that green (a missed hole is added
from its review tee).
"""
import glob
import json
import os
import re

CARD_FILES = ("card_review.json", "card_fix.json", "card_golfify.json")
HINT_KEYS = ("yardages", "pars", "tees", "scorecard", "osm_supplement", "typed_card", "near", "osm", "ignore_osm_holes",
             "boundary_ll")


def _read(p):
    try:
        with open(p) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def load_review(folder):
    """review.json in its schema variants -> {holes: {card ref: {verdict, tee_ll, yards, par, green_ll}}, tees, hint,
    renumber {page ref: card ref | {to, near_ll}}, skipped}."""
    d = _read(os.path.join(folder, "review.json"))
    if not isinstance(d, dict):
        return None
    d = d.get("course_review/1", d)
    holes, skipped = {}, []
    raw = d.get("holes") or []
    items = list(raw.items() if isinstance(raw, dict) else ((h.get("n") or h.get("hole") or h.get("ref"), h) for h in raw))
    ren = _renumber_map(d, items)
    cand = []
    for ref, h in items:
        if not isinstance(h, dict) or ref is None:
            continue
        f = h.get("fix") or {}
        if not isinstance(f, dict):
            f = {}
        n0 = ref
        ref = ren.get(str(ref), str(ref))                      # fixes are keyed by the card (renumbered) hole
        e = dict(verdict=h.get("verdict"))
        if isinstance(f.get("tee_ll"), dict):
            e["tee_ll"] = {s: ll for s, ll in f["tee_ll"].items() if isinstance(ll, (list, tuple)) and len(ll) >= 2}
        y = f.get("yards_by_set") or f.get("yards")
        if isinstance(y, dict):
            e["yards"] = {s: int(v) for s, v in y.items() if v}
        elif y:
            by, why = _bare_yards(int(y), list(e.get("tee_ll") or {}), str(ref), d, folder, h.get("notes"))
            if by:
                e["yards"] = by
            else:
                skipped.append(f"hole {ref}: bare yards {int(y)} dropped ({why}); give per-set yards")
        if f.get("par"):
            e["par"] = int(f["par"])
        g = f.get("green_ll")
        if isinstance(g, (list, tuple)) and len(g) >= 2:
            e["green_ll"] = [float(g[0]), float(g[1])]
        cand.append((str(n0) in ren, str(n0), ref, e))
    for moved, n0, ref, e in sorted(cand, key=lambda c: c[0]):   # renumbered holes last: they win the number
        if ref in holes and len(holes[ref]) > 1 and len(e) > 1 and moved:
            skipped.append(f"hole {ref}: its fixes dropped (renumbered hole {n0} is now card hole {ref})")
        if len(e) > 1 or ref not in holes:
            holes[ref] = e
    summ = d.get("summary") if isinstance(d.get("summary"), dict) else {}
    texts = _texts(d)
    hint = {k: v for k, v in (d.get("rebuild_hint") or summ.get("rebuild_hint") or {}).items() if k in HINT_KEYS and v}
    if any(re.search(r"ignore_osm_holes\W+true", t) for t in texts):
        hint["ignore_osm_holes"] = True
    for k in ("yardages", "pars"):                              # "430 386 206 ..." -> [430, 386, 206, ...]
        if isinstance(hint.get(k), str):
            hint[k] = [int(x) for x in re.findall(r"\d+", hint[k])]
    tees = hint.pop("tees", None) or d.get("tees") or _tees_in(texts) or d.get("page_set_should_be")
    if isinstance(tees, str):
        tees = [t.strip() for t in tees.split(",") if t.strip()]
    renumber = {}
    for old, new in ren.items():                               # near_ll: the review's tee point on that hole
        tee = next((ll for ll in (holes.get(new, {}).get("tee_ll") or {}).values()), None)
        renumber[old] = dict(to=int(new), near_ll=list(tee)) if tee else int(new)
    if ren and hint.get("ignore_osm_holes") and os.path.exists(os.path.join(folder, "osm_supplement.geojson")):
        renumber = {}            # the supplement's hole ways replace OSM's and are already in card numbering
    return dict(holes=holes, tees=tees, hint=hint, skipped=skipped, renumber=renumber,
                publish=d.get("publish", d.get("publish_as_is")))


def _texts(d):
    summ = d.get("summary") if isinstance(d.get("summary"), dict) else {}
    texts = [x for k in ("course_notes", "summary", "course_level", "rebuild_advice", "publish") for x in
             (d.get(k) if isinstance(d.get(k), list) else [d.get(k)]) if isinstance(x, str)]
    return texts + [x for x in summ.values() if isinstance(x, str)]


NOT_SETS = ("par", "pars", "si", "hcp", "handicap", "stroke_index")


def _review_card(d):
    """The review's own card {set: [yards]}: card.set = {set: [...]} or the card bare {set: [...], par: [...]}."""
    c = d.get("card") if isinstance(d.get("card"), dict) else {}
    c = c.get("set") if isinstance(c.get("set"), dict) else c
    return {s: v for s, v in c.items() if isinstance(v, list) and str(s).lower() not in NOT_SETS}


def _card_sets(d, folder):
    """{set: [yards]}: the folder card (card_review.json ...) > the review's card > the last build's package.json."""
    pkg = _read(os.path.join(folder, "package.json")) or {}
    out = {s: v["yards"] for s, v in (pkg.get("tee_sets") or {}).items()
           if isinstance(v, dict) and isinstance(v.get("yards"), list)}
    out.update(_review_card(d))
    cf = card_file(folder)
    for s, v in (((_read(cf) or {}).get("tee_sets") or {}) if cf else {}).items():
        if isinstance(v, dict) and isinstance(v.get("yards"), list):
            out[s] = v["yards"]
    return out


def _n_sets(d, folder):
    """How many tee sets the rebuild's card has (the build solves every set on the card, whatever "tees" says):
    the folder card's, else the review card's, else the last build's (a card-less page has one, osm_back);
    0 when unknown."""
    cf = card_file(folder)
    if cf:
        return len((_read(cf) or {}).get("tee_sets") or {})
    rc = _review_card(d)
    if rc:
        return len(rc)
    return len((_read(os.path.join(folder, "package.json")) or {}).get("tee_sets") or {})


def _bare_yards(y, named, ref, d, folder, notes=None):
    """A fix's bare "yards" -> ({set: y}, None) or (None, why). The set the fix's tee_ll names gets it; when it
    names several, or none, the sets whose card value on that hole is y; else the one card set the hole's notes
    name; else "*" (the solved set) only when the rebuild has a single set. Never "*" on a multi-set page: it lands on
    whichever set is solved (The Falls, Weaver Ridge: the Gold-box yardage on Blue / Black)."""
    if len(named) == 1:
        return {named[0]: y}, None
    i = int(ref) - 1 if str(ref).isdigit() else -1
    sets = _card_sets(d, folder)
    if len(sets) == 1 and not named:
        return {"*": y}, None
    hit = [s for s, v in sets.items() if (not named or s in named) and 0 <= i < len(v) and v[i] == y]
    if hit:
        return {s: y for s in hit}, None
    if named:
        return None, f"tee_ll names {', '.join(named)}: which set?"
    said = [s for s in sets if isinstance(notes, str) and re.search(rf"\b{re.escape(s)}\b", notes)]
    if len(said) == 1:
        return {said[0]: y}, None
    if _n_sets(d, folder) == 1:
        return {"*": y}, None
    return None, "no set named and the rebuild has several sets"


def _renumber_map(d, items):
    """{page ref: card ref} from "renumber": {"page_to_card": {...}} (or the map bare) and per-hole fix
    "renumber_as" / "card_hole"; identity entries dropped."""
    m = {}
    top = d.get("renumber")
    if isinstance(top, dict):
        top = top.get("page_to_card", top)
        m.update({str(k): str(v) for k, v in top.items() if str(v).isdigit()})
    for ref, h in items:
        f = (h.get("fix") if isinstance(h, dict) else None) or {}
        to = f.get("renumber_as", f.get("card_hole")) if isinstance(f, dict) else None
        if ref is not None and to is not None and str(to).isdigit():
            m[str(ref)] = str(int(to))
    return {k: v for k, v in m.items() if k != v}


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
        greens = {r: h["green_ll"] for r, h in rv["holes"].items() if h.get("green_ll")}
        if greens:
            out["green_overrides"] = greens
        if rv["renumber"]:
            out["hole_renumber"] = rv["renumber"]
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
