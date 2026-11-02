"""Wide-aim CHECK for library pages: any tee-shot aim the page prints more than GUARD_AIM yds off the tee line.

library/v2_adaptive.py lets a calm / forecast pick widen from +/-40 to +/-60 yds on a dog-leg. The quick engine
(product/decide.py wide_aim_flags, commit 67fda313c) makes such an aim a CHECK; the library page did not (library QA
2026-11-02: Gustin Gold 6 4-wood -60, Sycamore Ridge 18 Driver +58.5, Harvester Blue 2 Driver +60, Prairie Highlands
Blue 10 calm book Driver +60, all printed silently). Here the same rule is applied to what the page itself prints,
read from the page data (const D of a v2_course page):

  * the calm-day book pick and aim (h.calm, the note's "Aim N yds left / right");
  * the forecast pick for every forecast hour of the event days, solved exactly as the page's solveTee does it
    (speed / direction / temperature interpolation of the compact wind grids; the book pick kept, with the wind's aim
    change, when the quick model's pick in this wind equals its calm pick), for every tee offset grid the hole has.
    A forecast aim counts only when its wind-free line (aim + drift) is past the bound too, by more than FINISH_TOL:
    the v2 bound is +/-40 on that line (shifted by the drift), so an aim of 44 into a crosswind that finishes at 30 is
    the normal bound, not a widened dog-leg line (2026-11-02 library scan: 40-41 finishes are interpolation).

flags(h, D) -> the CHECK reasons for one tee-shot hole, worded exactly as product/decide.wide_aim_flags (the widest
wide aim on each side). landing_extent(h, D) -> how far left / right of the tee line the wide aims' landing ovals
reach (v2_adaptive.py widens the hole picture's crop to it).
"""
import math

GUARD_AIM = 40.0          # = product/decide.GUARD_AIM (test_wide_aims checks the two stay equal)
FINISH_TOL = 2.0          # yds: a forecast aim's line (aim + drift) past GUARD_AIM by more than this is a widened one


def wide_aim_flags(club, aim):
    """Same rule and wording as product/decide.wide_aim_flags (not imported: decide loads the Mozingo engine)."""
    if abs(float(aim)) <= GUARD_AIM + 1e-6:
        return []
    side = "right" if aim > 0 else "left"
    return [f"{club} aim {aim:+.0f} yds is more than {GUARD_AIM:.0f} yds {side} of the tee line (dog-leg corner, "
            "wider aim bound): confirm the line on the map"]


def _hypo(c):
    return "not in bag" in c


def _key(x):
    return f"{float(x):g}"


def _clubs(cl):
    return {c: dict(aim=a[0], ev=a[1], total=a[5], width=a[6], drift=a[7]) for c, a in cl.items()}


def _temp_weights(GB, temps, tF):
    TT = list(temps)
    t = min(max(tF, TT[0]), TT[-1])
    j = 0
    while j < len(TT) - 2 and t > TT[j + 1]:
        j += 1
    w = (t - TT[j]) / (TT[j + 1] - TT[j]) if TT[j + 1] != TT[j] else 0.0
    return [(GB[_key(TT[j])], 1 - w), (GB[_key(TT[j + 1])], w)]


def _cell(g, sp, d):
    return g["0_0"] if sp == 0 else g[f"{_key(sp)}_{int(d % 360)}"]


def solve(h, D, mph, frm, tF, back="0"):
    """The page's solveTee for hole dict h at this wind (mph, from deg) and temperature -> (pick, aim, clubs)."""
    GB = h["grids"][str(back)]
    if len(D["temps"]) < 2:
        TW = [(GB[_key(D["temps"][0])], 1.0)]
        TW0 = TW
    else:
        TW = _temp_weights(GB, D["temps"], tF)
        TW0 = _temp_weights(GB, D["temps"], (h.get("calm") or {}).get("temp", tF)) if h.get("calm") else TW
    S = D["speeds"]
    rel = ((frm - (h.get("bearing") or 0)) % 360 + 360) % 360
    mph = min(mph, S[-1])
    i = 0
    while i < len(S) - 2 and mph > S[i + 1]:
        i += 1
    s0, s1 = S[i], S[i + 1]
    ws = (mph - s0) / (s1 - s0)
    d0 = math.floor(rel / 30) * 30
    d1, wd = (d0 + 30) % 360, (rel - d0) / 30
    corners = [(s0, d0, (1 - ws) * (1 - wd)), (s0, d1, (1 - ws) * wd), (s1, d0, ws * (1 - wd)), (s1, d1, ws * wd)]
    out = {}
    for c in TW[0][0]["0_0"]:
        r = dict(ev=0.0, aim=0.0, width=0.0, drift=0.0)
        for g, tw in TW:
            for sp, dd, w0 in corners:
                if w0 * tw == 0:
                    continue
                v = _clubs({c: _cell(g, sp, dd)[c]})[c]
                for k in r:
                    r[k] += w0 * tw * v[k]
        out[c] = r
    order = sorted((c for c in out if not _hypo(c)), key=lambda c: out[c]["ev"])
    pick, aim = order[0], out[order[0]]["aim"]
    calm = h.get("calm")
    if calm and str(back) == "0" and calm.get("pick") in out:
        g0 = {}
        for g, tw in TW0:
            for c, a in g["0_0"].items():
                e = g0.setdefault(c, dict(ev=0.0, aim=0.0))
                e["ev"] += tw * a[1]
                e["aim"] += tw * a[0]
        calm_quick = min((c for c in g0 if not _hypo(c)), key=lambda c: g0[c]["ev"])
        if pick == calm_quick:
            pick = calm["pick"]
            aim = calm["aim"] + (out[pick]["aim"] - g0[pick]["aim"])
    return pick, float(aim), out


def printed(h, D):
    """[(what, club, aim, lateral centre of the landing, half width)] for every tee-shot aim the page prints."""
    if h.get("kind") != "tee" or not h.get("grids"):
        return []
    rows = []
    calm = h.get("calm")
    if calm and calm.get("pick"):
        try:
            _, _, out = solve(h, D, 0.0, 0.0, calm.get("temp", D["temps"][len(D["temps"]) // 2]))
            v = out.get(calm["pick"]) or {}
        except (KeyError, IndexError, ZeroDivisionError):
            v = {}
        rows.append(("calm-day book", calm["pick"], float(calm["aim"]), float(calm["aim"]) + v.get("drift", 0.0),
                     v.get("width", 0.0) / 2))
    days = set(D.get("days") or [])
    for back in h["grids"]:
        for f in D.get("forecast") or []:
            if f.get("date") not in days:
                continue
            try:
                pick, aim, out = solve(h, D, round(f["mph"] * 10) / 10, round(f["dir"]), f["temp"], back)
            except (KeyError, IndexError, ZeroDivisionError):
                continue
            rows.append((f"forecast {f['date']} {int(f['hour']):02d}:00" + ("" if str(back) == "0" else f" (tee {back})"),
                         pick, aim, aim + out[pick]["drift"], out[pick]["width"] / 2))
    return rows


def wide(h, D):
    """The printed() rows that are wide: the calm book aim past GUARD_AIM, or a forecast aim past GUARD_AIM whose
    line (aim + drift) is past GUARD_AIM + FINISH_TOL on the same side."""
    out = []
    for r in printed(h, D):
        what, _, aim, line, _ = r
        if abs(aim) <= GUARD_AIM + 1e-6:
            continue
        if what.startswith("calm") or (line * aim > 0 and abs(line) > GUARD_AIM + FINISH_TOL):
            out.append(r)
    return out


def flags(h, D, rows=None):
    """CHECK reasons for one hole (product/decide.wide_aim_flags words): the widest wide aim on each side."""
    rows = wide(h, D) if rows is None else rows
    why = []
    for side in (-1, 1):
        rs = [r for r in rows if side * r[2] > 0]
        if rs:
            _, club, aim, _, _ = max(rs, key=lambda r: side * r[2])
            why += wide_aim_flags(club, aim)
    return why


def landing_extent(h, D, pad=10.0, rows=None):
    """(left, right) yds off the tee line that the landing ovals (line +/- half the 95% width) of the WIDE aims reach,
    + pad; None when no printed aim is wide (the picture keeps its usual crop)."""
    rows = wide(h, D) if rows is None else rows
    if not rows:
        return None
    left = max(max(0.0, -(c - w)) for _, _, _, c, w in rows) + pad
    right = max(max(0.0, c + w) for _, _, _, c, w in rows) + pad
    return left, right


def page_flags(D):
    """{set: {hole key: (reasons, where)}} for a whole page (D.holes = the base set, D.alt = the other solved sets);
    where = the printed places of the wide aims ("calm-day book", "forecast <date> <hour>", ...)."""
    out = {}
    for s, hs in [(D.get("base_set"), D.get("holes") or [])] + list((D.get("alt") or {}).items()):
        for h in hs:
            rows = wide(h, D)
            if rows:
                out.setdefault(s, {})[str(h.get("key"))] = (flags(h, D, rows), sorted({r[0].split(" ")[0] for r in rows}))
    return out
