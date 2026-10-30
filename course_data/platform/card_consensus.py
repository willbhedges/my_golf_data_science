"""Card consensus: several web scorecards that disagree -> one card, settled hole by hole on the OSM ground.

Reviewers' main source of bad auto-built pages is the scorecard: a stale card (Finkbine, Harvester), a scrambled
one (Eagle Bend golfify: holes 2-9 are really 11-18), a card typed in metres (AllSquare shows metres), set names
swapped (WeaverRidge on OpenGolfAPI: "Gold" rows under the Black total). scorecard.choose_card ranks cards by
source reliability only; this module adds the ground:

  ground = {ref: {"line": OSM hole-line length (yd), "tees": [OSM tee-box distances to the green (yd)]}}
           (`ground_from_package` reads package.json holes[].tee_options; `ground_from_summary` the hole lines only)

  1. units      a card whose longest set runs ~0.91 x the ground is in metres -> converted (flag)
  2. swaps      sets whose rows sum to another set's stated total, or whose order by length contradicts the
                OSM tee order, are flagged (and renamed when the stated totals prove it)
  3. base card  the card that fits the ground on most holes (a value within FIT_YD of an OSM tee / the hole
                line); among cards within 10% of the best, the most recent (card_date) then the most reliable
  4. per hole   for each set of the base card, when another card's matching set disagrees by > DISAGREE_YD on a
                hole and fits the ground clearly better (by > MARGIN_YD, and within FIT_YD), its value is used

-> consensus(cards, ground) = {card, base, changes[], flags[], scores{}}. Pure functions; no network.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
import scorecard as scm  # noqa: E402

FIT_YD = 12          # a card value "fits" the ground within this of an OSM tee box or the hole line
DISAGREE_YD = 8      # cards disagree on a hole by more than this
MARGIN_YD = 8        # the replacement must fit the ground this much better
NEAR = 0.20          # cards within this share of the best ground fit count as fitting; reliability decides
STRONG_ALT_YD = 3    # a base value two cards agree on is replaced only by one within 3 yd of the ground ...
STRONG_BASE_YD = 24  # ... when the agreed value misses the ground by >= 24 yd (Finkbine 1/10/13, Harvester 13/14)
SAME_SET = 0.06      # matched sets of two cards are the same set when their totals are within 6%
M_PER_YD = 0.9144
SUM_TOL = 15


# ----------------------------------------------------------------------------- ground
def ground_from_package(pkg):
    """package.json -> ground. tee_options are the OSM tee boxes' distances to the green along the hole."""
    out = {}
    holes = pkg.get("holes") or {}
    for ref, h in (holes.items() if isinstance(holes, dict) else ((str(h.get("ref")), h) for h in holes)):
        line = None
        ll = h.get("hole_line_ll")
        if ll and len(ll) > 1:
            line = round(sum(_yd(a, b) for a, b in zip(ll, ll[1:])))
        out[str(ref)] = dict(line=line, tees=sorted(t for t in (h.get("tee_options") or []) if t))
    return out


def ground_from_summary(summ):
    """raw/summary.json (fetch-time OSM) -> ground with hole lines only."""
    return {str(h["ref"]): dict(line=h.get("length_yd"), tees=[]) for h in summ.get("holes") or []
            if str(h.get("ref", "")).isdigit() and h.get("length_yd")}


def _yd(a, b):
    import math
    la = math.radians((a[1] + b[1]) / 2)
    return math.hypot((a[0] - b[0]) * math.cos(la), a[1] - b[1]) * 111320 / M_PER_YD


def _cands(g):
    c = list(g.get("tees") or [])
    if g.get("line"):
        c.append(g["line"])
    return c


def fit(y, g):
    """Distance (yd) from a card value to the nearest ground length on the hole; None when no ground."""
    c = _cands(g or {})
    if not y or not c:
        return None
    return min(abs(y - x) for x in c)


def _longest(card):
    sets = card["tee_sets"]
    return max(sets, key=lambda k: sets[k].get("total") or 0)


def card_fit(card, ground, set_name=None):
    """{holes, fit (count within FIT_YD), share, mean_err} for one set (default: the longest) of a card."""
    s = card["tee_sets"][set_name or _longest(card)]
    errs = []
    for i, y in enumerate(s.get("yards") or []):
        f = fit(y, ground.get(str(i + 1)))
        if f is not None:
            errs.append(f)
    n = len(errs)
    good = sum(1 for e in errs if e <= FIT_YD)
    return dict(holes=n, fit=good, share=round(good / n, 3) if n else None,
                mean_err=round(sum(errs) / n, 1) if n else None)


def _all_sets_fit(card, ground):
    """Share of (hole, set) values within FIT_YD of a ground length: a card-level score over every set."""
    n = good = 0
    for s in card["tee_sets"].values():
        for i, y in enumerate(s.get("yards") or []):
            f = fit(y, ground.get(str(i + 1)))
            if f is not None:
                n += 1
                good += f <= FIT_YD
    return good / n if n else 0.0


# ----------------------------------------------------------------------------- 1. units
def _scaled(card, k):
    out = dict(card, tee_sets={})
    for name, s in card["tee_sets"].items():
        ys = [int(round(y * k)) if y else y for y in s.get("yards") or []]
        t = dict(s, yards=ys, total=sum(y for y in ys if y))
        if t.get("total_stated"):
            t["total_stated"] = int(round(t["total_stated"] * k))
        out["tee_sets"][name] = t
    return out


def _ratio(card, other):
    """Median per-hole ratio card/other over sets matched by name; None when nothing matches."""
    rs = []
    for name, s in card["tee_sets"].items():
        on = _match(name, s, other)
        if on:
            rs += [a / b for a, b in zip(s["yards"], other["tee_sets"][on]["yards"]) if a and b]
    return sorted(rs)[len(rs) // 2] if len(rs) >= 6 else None


def check_units(card, ground, others=()):
    """-> (card, flag | None). Metres when the longest set is ~0.91 of the ground and converting fits better;
    vetoed when another card's same-named sets agree with it as printed (ratio ~1), forced when another card
    runs 1/0.9144 of it (Painted Hills: OpenGolfAPI White-only 0.93 x ground, but equal to golfify White)."""
    for o in others:
        r = _ratio(card, o)
        if r is not None and 0.97 <= r <= 1.03:
            return card, None
    lines = []
    s = card["tee_sets"][_longest(card)]
    for i, y in enumerate(s.get("yards") or []):
        g = ground.get(str(i + 1)) or {}
        c = _cands(g)
        if y and c:
            lines.append(y / max(c))
    if len(lines) < 6:
        return card, None
    med = sorted(lines)[len(lines) // 2]
    if not 0.84 <= med <= 0.95 or sum(0.85 <= x <= 0.97 for x in lines) < 0.5 * len(lines):
        return card, None
    conv = _scaled(card, 1 / M_PER_YD)
    if _all_sets_fit(conv, ground) > _all_sets_fit(card, ground) + 0.15:
        return conv, (f"card is in metres (longest set runs {med:.2f} x the OSM lengths): converted to yards "
                      f"({s.get('total')} m -> {conv['tee_sets'][_longest(conv)]['total']} yd)")
    return card, None


# ----------------------------------------------------------------------------- 2. swapped set names
def stated_swaps(card, tol=scm.SUM_TOL_YD):
    """Pairs (a, b) whose per-hole rows sum to each other's stated totals (but not their own): the rows sit
    under the wrong names (WeaverRidge OpenGolfAPI: 'Gold' rows sum 6876 under Gold 6500 / Black 7000)."""
    sets = card["tee_sets"]
    out = []
    names = [n for n in sets if sets[n].get("total_stated")]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            sa, sb = sets[a]["total"], sets[b]["total"]
            ta, tb = sets[a]["total_stated"], sets[b]["total_stated"]
            own = abs(sa - ta) + abs(sb - tb)
            cross = abs(sa - tb) + abs(sb - ta)
            if cross + tol < own and abs(sa - tb) <= max(tol * 3, 0.06 * tb) and abs(sa - ta) > tol:
                out.append((a, b))
    return out


def osm_order_swaps(card, ground):
    """Adjacent sets (by stated total, else name order) whose per-hole lengths fit the OSM tee order the other
    way round: set A says it is the longer, but on most holes with >= 2 OSM tees B is the one at the longer box."""
    sets = card["tee_sets"]
    order = sorted(sets, key=lambda n: -(sets[n].get("total_stated") or sets[n].get("total") or 0))
    out = []
    for a, b in zip(order, order[1:]):
        ya, yb = sets[a]["yards"], sets[b]["yards"]
        vote = tot = 0
        for i, (x, y) in enumerate(zip(ya, yb)):
            g = ground.get(str(i + 1)) or {}
            if not x or not y or len(g.get("tees") or []) < 2 or abs(x - y) <= DISAGREE_YD:
                continue
            tot += 1
            vote += (x < y)
        if tot >= 4 and vote / tot >= 0.6:
            out.append((a, b, vote, tot))
    return out


def fix_swaps(card, ground):
    """-> (card, flags). Stated-total swaps are fixed (rows moved to the right names); OSM-order swaps flagged."""
    flags = []
    sw = stated_swaps(card)
    if sw:
        sets = {k: dict(v) for k, v in card["tee_sets"].items()}
        for a, b in sw:
            for key in ("yards", "total"):
                sets[a][key], sets[b][key] = sets[b][key], sets[a][key]
            flags.append(f"set names swapped: the rows under '{a}' sum to {sets[a]['total']} = the stated '{a}' "
                         f"total {sets[a]['total_stated']}; they were listed as '{b}' (rows moved back)")
        card = dict(card, tee_sets=dict(sorted(sets.items(), key=lambda kv: -(kv[1]["total"] or 0))))
    for a, b, v, t in osm_order_swaps(card, ground):
        flags.append(f"set order: '{b}' is longer than '{a}' on {v} of {t} holes with several OSM tees: "
                     "names may be swapped")
    return card, flags


# ----------------------------------------------------------------------------- 3 + 4. consensus
def _match(name, s, other):
    k = scm._set_key(name, s) - {""}
    return next((n for n, o in other["tee_sets"].items() if k & (scm._set_key(n, o) - {""})), None)


def _same_card(a, b, tol=SUM_TOL):
    """Two cards list the same yardages: the longest sets' totals and per-hole values agree."""
    la, lb = a["tee_sets"][_longest(a)], b["tee_sets"][_longest(b)]
    if abs((la.get("total") or 0) - (lb.get("total") or 0)) > tol:
        return False
    return sum(1 for x, y in zip(la["yards"], lb["yards"]) if x and y and abs(x - y) > 3) <= 1


def _hole_agrees(name, s, other, i, y):
    on = _match(name, s, other)
    ys = other["tee_sets"][on]["yards"] if on else []
    return bool(y and i < len(ys) and ys[i] and abs(ys[i] - y) <= 3)


def _rank(kind):
    if kind in ("request", "file", "review", "typed"):                 # a card a person typed or checked
        return -1
    return scm.RELIABILITY.index(kind) if kind in scm.RELIABILITY else len(scm.RELIABILITY)


def consensus(cards, ground):
    """cards = [(kind, card, url)] (scorecard/1, any shape `scorecard.normalise` accepts); ground as above.
    -> {card, base, base_url, changes, flags, scores} or None when there are no cards."""
    prepared, flags = [], []
    normed = [(k, scm.normalise(c), u) for k, c, u in cards if c and c.get("tee_sets")]
    for kind, c, url in normed:
        c, f = check_units(c, ground, [o for k2, o, u2 in normed if o is not c])
        if f:
            flags.append(f"{kind}: {f}")
        c, fs = fix_swaps(c, ground)
        flags += [f"{kind}: {x}" for x in fs]
        prepared.append((kind, c, url))
    if not prepared:
        return None
    scores = {}
    for kind, c, url in prepared:
        lf = card_fit(c, ground)
        scores[f"{kind} {url or ''}".strip()] = dict(lf, all_sets=round(_all_sets_fit(c, ground), 3),
                                                     consistent=scm.consistency(c)["ok"], date=c.get("card_date"))
    keyed = []
    for k, c, u in prepared:
        sc = scores[f"{k} {u or ''}".strip()]
        agree = sum(1 for k2, c2, u2 in prepared if c2 is not c and k2 != k and _same_card(c, c2))
        sc["corroborated_by"] = agree
        keyed.append((sc["all_sets"] + 0.05 * min(agree, 2), k, c, u))
    best = max(s for s, *_ in keyed)
    near = [x for x in keyed if x[0] >= best - NEAR]
    near.sort(key=lambda x: (_rank(x[1]), -(int((x[2].get("card_date") or "0").replace("-", "") or 0)), -x[0]))
    _, base_kind, base, base_url = near[0]
    stale = set()
    for s_, k, c, u in keyed:
        if s_ < best - 0.25 and len(keyed) > 1:
            stale.add(id(c))
            flags.append(f"{k}: fits the OSM ground on only {s_:.0%} of hole/set values (best card {best:.0%}): "
                         "stale or scrambled card")
    merged = {k: dict(v, yards=list(v["yards"])) for k, v in base["tee_sets"].items()}
    changes = []
    for name, s in merged.items():
        for i, y in enumerate(s["yards"]):
            g = ground.get(str(i + 1))
            fy = fit(y, g)
            if fy is None or fy <= FIT_YD:
                continue
            best_alt = None
            corroborated = any(c is not base and _hole_agrees(name, s, c, i, y) for k, c, u in prepared)
            for k, c, u in prepared:
                if c is base or id(c) in stale:
                    continue
                on = _match(name, s, c)
                if not on:
                    continue
                o = c["tee_sets"][on]
                if abs((o.get("total") or 0) - (s.get("total") or 0)) > SAME_SET * max(s.get("total") or 1, 1):
                    continue                                     # a different set under the same name
                ys = o["yards"]
                if i >= len(ys) or not ys[i] or abs(ys[i] - (y or 0)) <= DISAGREE_YD:
                    continue
                fa = fit(ys[i], g)
                if corroborated and not (fa <= STRONG_ALT_YD and fy >= STRONG_BASE_YD):
                    continue                                     # two cards agree: only a clear ground misfit
                if fa is not None and fa <= FIT_YD and fa + MARGIN_YD < fy and (best_alt is None or fa < best_alt[0]):
                    best_alt = (fa, ys[i], k, on)
            if best_alt:
                changes.append(dict(hole=i + 1, set=name, card=y, chosen=best_alt[1], source=best_alt[2],
                                    source_set=best_alt[3], ground_err=[fy, best_alt[0]]))
                s["yards"][i] = best_alt[1]
    for s in merged.values():
        s["total"] = sum(y for y in s["yards"] if y)
        if any(ch["set"] in merged and s is merged[ch["set"]] for ch in changes):
            s.pop("total_stated", None)
            s["note"] = "per-hole consensus on the OSM ground (card_consensus.py)"
    out = dict(base, tee_sets=merged, consensus=dict(base=base_kind, changes=len(changes)))
    return dict(card=out, base=base_kind, base_url=base_url, changes=changes, flags=flags, scores=scores)
