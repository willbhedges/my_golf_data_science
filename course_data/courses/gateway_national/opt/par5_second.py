"""Gateway National par 5s: the SECOND shot (go for the green or lay up, and where), and the tee pick re-checked with
the second shot played out (PAR5.md).

  OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/par5_second.py --which truth --sets Back
  OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/par5_second.py --which truth_middle --sets Middle
  python3 course_data/courses/gateway_national/opt/par5_second.py page       (rewrite par5_second.json from results)

One process per base (`truth` = Back, also The Tips / Champions by moving the tee back along its line;
`truth_middle` = Middle, also Forward). Writes opt/results/par5_second_<set>.json.

Model (the tee-shot engine's own pieces, nothing new invented where the engine has a rule):
  * Map: the hole's zones (course.py, native = penalty area as the engine has it at Gateway) rastered at 0.5 yd in the
    tee frame out past the green (the engine's raster stops at 430 yds); untraced ground = rough.
  * Value of the ball after the second shot: the engine's per-cell strokes (Raster.strokes: the am table by lie and
    distance, short game inside 20 yds, putts on the green, punch-out from trees, tree line in the way).
  * Penalty ball (water, tall native): one stroke + the engine's rough value at the point where the ball last crossed
    the edge, walking back along the SHOT's line (the engine walks back along the tee line). OB: stroke and distance
    from the second-shot spot.
  * Swing: model.shots() (same mishits, tilt, roll noise), club numbers from DECK below, the temperature at the hole,
    the forecast wind turned onto the shot's own line. No elevation on the second shot. Flight-path trees not priced.
  * Sweep: club x direction (1-deg steps, +/-28 deg of the line to the green centre). An option is a LAY-UP when its
    stock total stops 20+ yds short of the front edge, otherwise a GO.
"""
import argparse
import copy
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GW = os.path.dirname(HERE)
CD = os.path.dirname(os.path.dirname(GW))
ROOT = os.path.dirname(CD)
sys.path[:0] = [os.path.join(CD, "courses")]
# P5_TALL_GRASS=lost: the page's second rule set (config engine.tall_grass_alt; v2_course.activate(tall_grass="lost")):
# a ball finishing in tall native grass is a lost ball = one stroke and the same shot again from the same spot, in
# closed form per club and direction (v2_course.lost_ball_ev); water keeps one stroke + a drop where it crossed.
# Everything is then written beside the drop-rule files: opt/results_lost/ and *_lost.json (also par5_menu.py,
# par5_page.py, layup10.py, which import this module).
LOST = os.environ.get("P5_TALL_GRASS") == "lost"
SUF = "_lost" if LOST else ""
OUT = os.path.join(HERE, "results" + SUF)
PAGE = os.path.join(GW, f"par5_second{SUF}.json")
SLUG = "gateway_national"
PAR5 = (3, 6, 13, 18)
BASE_OF = {"Back": "truth", "The Tips": "truth", "Champions": "truth", "Middle": "truth_middle", "Forward": "truth_middle"}
DAYS = {"sat": "2026-11-14", "sun": "2026-11-15"}

# ---------------------------------------------------------------- clubs off the deck (ASSUMPTIONS, see PAR5.md)
# (carry at 70 F, total, 95 % width, 95 % carry window, wind-sensitivity name). Driver and 2-wood are not hit off the
# deck. 4-wood: the golfer's own number, Nov 13: "4-wood same as off tee" = 255 carry / 270 total (the first build
# took 15 off: DECK_SETS "assumed" keeps that). Its width and every other pattern: DECK_SETS below.
# Irons: the engine's Long / Mid iron and 8-iron, then the par-3 bag (12-yd gaps).
DECK = {
    "4-wood": (255, 270, 50, 24, "4-wood"),
    "Long iron": (210, 220, 40, 20, "Long iron"),
    "Mid iron": (185, 192, 34, 18, "Mid iron"),
    "8-iron": (162, 167, 30, 16, "8-iron"),
    "9-iron": (150, 154, 28, 15, "8-iron"),
    "PW": (138, 141, 26, 14, "8-iron"),
    "GW": (126, 128, 24, 13, "8-iron"),
    "SW": (113, 115, 22, 12, "8-iron"),
}
PAGE_NAME = {"Long iron": "long iron", "Mid iron": "mid iron", "PW": "pitching wedge", "GW": "gap wedge", "SW": "sand wedge"}
# lie rules (second_pass/model/mdp.py, the model review's rollout): spread x, carry x, longest club allowed
LIE = {"fairway": (1.0, 1.0, "4-wood"), "rough": (1.25, 0.96, "Long iron"), "sand": (1.5, 0.93, "Mid iron")}
# sensitivity runs (PAR5.md): P5_WOOD_SPREAD / P5_WOOD_CARRY = the 4-wood off the deck wider / shorter (yds at 70 F);
# P5_ALL_SPREAD = every second shot wider
VAR = dict(wood_spread=float(os.environ.get("P5_WOOD_SPREAD", 1.0)), wood_carry=float(os.environ.get("P5_WOOD_CARRY", 0.0)),
           all_spread=float(os.environ.get("P5_ALL_SPREAD", 1.0)))
# Pattern sets for every shot off the deck (second_pass/FAIRWAY_WOOD_DATA.md). `spread` multiplies the 95 % width and
# the carry window of every deck club, `mis` = (slight, heavy) mishit rates (None = the engine's 12 % / 2.5 %),
# `wood_carry` = yds added to the 4-wood's 255 carry at 70 F, `rough` = (spread x, carry x) from rough.
#   assumed     = the first build (Nov 13): the tee pattern kept off the deck. On a flat, calm, 15-yd-radius green it
#                 hits 70 % of greens from 220 and leaves 39 ft: better than the PGA Tour's 42 ft from 200-225.
#   central     = published data: Tour proximity by distance x 1.5 club for club (a scratch player's pattern is about
#                 1.5 x a Tour player's), which also gives the scratch "good shot" rate from 200 (39 %).
#   pessimistic = the scratch amateur's proximity by distance (80 ft from 200-225), more mishits, rough 8 % shorter
#                 and 50 % wider.
# Distance off the deck is the golfer's own (central, pessimistic); "assumed" keeps the first build's 240 carry.
# central since Nov 14 (late) = ANISOTROPIC, from config approach_pattern.deck (golfer: "why 79 yards wide with a
# 220-yard shot?"; FAIRWAY_WOOD_DATA.md "Sideways and distance apart"): `lat` multiplies the 95 % width only (x 1.0:
# the tee pattern, his planning width), `depth` the carry window (x 2.25), and the slightly mishit share grows with the club
# (`mis_slight` / `mis_heavy` = [at carry c0, at carry c1], linear in the club's 70-F carry, `mis_slight_carry` = the
# share of the carry a slight mishit goes). central_175 = the run before (x 1.75 on both axes).
_AP = json.load(open(os.path.join(GW, "config.json"))).get("approach_pattern", {}).get("deck")
DECK_SETS = {
    "assumed": dict(spread=1.0, mis=None, wood_carry=-15.0, rough=(1.25, 0.96)),
    "central": (dict(spread=1.0, lat=_AP["lat"], depth=_AP["depth"], mis=None, mis_by_carry=_AP, wood_carry=0.0,
                     rough=(1.25, 0.96)) if _AP else dict(spread=1.75, mis=None, wood_carry=0.0, rough=(1.25, 0.96))),
    "central_175": dict(spread=1.75, mis=None, wood_carry=0.0, rough=(1.25, 0.96)),
    "pessimistic": dict(spread=2.0, mis=(0.20, 0.06), wood_carry=0.0, rough=(1.5, 0.92)),
}
# The par-5 page data (this file's solve, par5_menu.py) is built on "central" (P5_DECK_SET overrides); a plain import
# keeps "assumed", so the hole 10 lay-up table (layup10.py, not re-solved) reproduces as published.
SET = dict(DECK_SETS[os.environ.get("P5_DECK_SET", "assumed")])


# In-between shots (golfer, Nov 14: "you never put in like a 230-yard shot ... make sure we have all those gaps
# closed"): the bag jumps from the long iron (210 carry) to the 4-wood (255). GAP = carries 220 / 230 / 240 at 70 F: a
# long iron hit hard, a hybrid he does not carry, an eased 4-wood. Total, width and carry window interpolated on
# carry between the long iron's and the 4-wood's tuples (so they get the same pattern set as every deck club);
# wind sensitivity of the nearer club. Not stock clubs: the page marks them, and summarise() also gives the best
# stock club (go_bag / lay_bag). LADDER = the 5-iron and 7-iron of the par-3 bag (config par3_bag), which close the
# 25- and 23-yd holes among the lay-up clubs. Both are added by use_set() only (the par-5 page path): a plain
# import keeps the first build's DECK, so layup10.py reproduces. From rough the longest shot is the 220 shot.
GAP = {
    "240 shot": (240, 253.3, 46.7, 22.7, "4-wood"),
    "230 shot": (230, 242.2, 44.4, 21.8, "Hybrid ~235 (not in bag)"),
    "220 shot": (220, 231.1, 42.2, 20.9, "Long iron"),
}
LADDER = {"5-iron": (198, 206, 37, 19, "Long iron"), "7-iron": (174, 180, 32, 17, "Mid iron")}


def use_set(name=None, gaps=True):
    name = name or os.environ.get("P5_DECK_SET", "central")
    SET.clear()
    SET.update(DECK_SETS[name])
    if gaps and os.environ.get("P5_GAPS", "1") != "0":
        allc = sorted({**DECK, **GAP, **LADDER}.items(), key=lambda kv: -kv[1][0])
        DECK.clear()
        DECK.update(allc)
        LIE["rough"] = LIE["rough"][:2] + ("220 shot",)
    return name
ANG = np.arange(-28.0, 28.01, 1.0)
LAY_GAP = 20.0


def deck_clubs(lie):
    names = list(DECK)
    return names[names.index(LIE[lie][2]):]


# ---------------------------------------------------------------- course
class World:
    def __init__(self, which):
        import v2_course as vc
        self.vc = vc
        self.which = which
        self.cfg = vc.config(SLUG)
        self.course, self.meta, self.M, self.D = vc.activate(SLUG, which, tall_grass="lost" if LOST else None)
        import wind as W
        import wind_grid_v2 as WG2
        self.W, self.WG2 = W, WG2
        self.base_set = self.meta["tee_set"]
        self.fc = vc.forecast(SLUG)["hourly"]
        for nm, tup in DECK.items():
            self.M.CLUBS["deck:" + nm] = tuple(float(x) for x in tup[:4])

    def wx(self, h, day):
        rows = [r for r in self.fc if r["date"] == day]
        hh = np.array([r["hour"] for r in rows], float)
        # the day's own tee time (config tee_hours [Sat, Sun], else tee_hour), the same clock as the page
        th, days = self.cfg.get("tee_hours"), list(self.cfg.get("days", []))
        t0 = float(th[days.index(day)]) if th and day in days else float(self.cfg.get("tee_hour", 9.0))
        hr = t0 + (h - 1) * 14.0 / 60.0
        ang = np.radians([r["wind_from_deg"] for r in rows])
        s, c = np.interp(hr, hh, np.sin(ang)), np.interp(hr, hh, np.cos(ang))
        return dict(temp=float(np.interp(hr, hh, [r["temp_f"] for r in rows])),
                    mph=float(np.interp(hr, hh, [r["wind_mph"] for r in rows])),
                    frm=float(np.degrees(np.arctan2(s, c)) % 360), hour=hr)

    def hole(self, h, set_name):
        """A copy of the hole with the tee moved to `set_name` (yds back of the base tee along the tee line)."""
        hd = copy.deepcopy(self.course.HOLES[h])
        y = self.meta["holes"][str(h)]["yards"]
        back = float(y[set_name] - y[self.base_set])
        if back:
            tee, d = np.array(hd["tee"], float), np.array(hd["dot270"], float)
            f = (d - tee) / np.linalg.norm(d - tee)
            ppy = np.linalg.norm(d - tee) / 270
            hd["tee"] = tuple(tee - f * back * ppy)
            hd["dot270"] = tuple(np.array(hd["tee"]) + f * 270 * ppy)
            hd["length"] = hd["length"] + back
        return hd, back

    def big(self, hd):
        """Lie raster out past the green; untraced ground = rough."""
        M = self.M
        R0 = M.Raster(hd)
        ga = float(R0.green[0])
        keep = (M.A1, M.L0, M.L1, M.CHECKED_HALF_WIDTH)
        try:
            M.A1, M.L0, M.L1, M.CHECKED_HALF_WIDTH = int(ga + 70), -170, 170, 1e9
            Rb = M.Raster(hd)
            A0, L0 = M.A0, M.L0
        finally:
            M.A1, M.L0, M.L1, M.CHECKED_HALF_WIDTH = keep
        na, nl = len(Rb.a), len(Rb.l)

        def idx(a, l):
            ia = np.clip(np.rint((np.asarray(a) - A0) / M.RES).astype(np.int32), 0, na - 1)
            il = np.clip(np.rint((np.asarray(l) - L0) / M.RES).astype(np.int32), 0, nl - 1)
            return ia, il
        Rb.idx = idx
        Rb.lie_at = lambda a, l: Rb.lie[idx(a, l)]
        Rb._blocked()
        return R0, Rb


class Field:
    """Per-cell third-shot values on the big raster for one hole / tee / day."""

    def __init__(self, Wd, hd, P, Rb):
        from matplotlib.path import Path
        M = Wd.M
        self.M, self.R, self.P, self.hd = M, Rb, P, hd
        self.S = Rb.strokes(P, hd["length"])
        lie0 = Rb.lie
        Rb.lie = np.zeros_like(lie0)                         # every cell rough: the value of a drop
        blk0 = Rb.blocked
        Rb.blocked = np.zeros_like(blk0)
        self.Srough = Rb.strokes(P, hd["length"])
        Rb.lie, Rb.blocked = lie0, blk0
        tee, fwd, right, ppy = M.frame(hd)
        gp = hd.get("green_poly")
        if hd.get("green_poly_px") is not None:
            dd = (np.asarray(hd["green_poly_px"], float) - tee) / ppy
            gp = np.column_stack([dd @ fwd, dd @ right])
        self.gpoly = np.asarray(gp, float)
        self.gpath = Path(self.gpoly)
        self.ongreen = self.gpath.contains_points(np.column_stack([Rb.AA.ravel(), Rb.LL.ravel()])).reshape(Rb.AA.shape)
        self.pen = np.isin(Rb.lie, [M.CODE["water"]] + ([] if LOST else [M.CODE["native"]]))   # one stroke + drop
        self.green = np.asarray(Rb.green, float)

    def front(self, a0, l0):
        """yds from (a0, l0) to the first point of the green on the line to its centre, and to the centre."""
        d = float(np.hypot(*(self.green - (a0, l0))))
        s = np.arange(0.0, d + 0.01, 0.25)
        u = (self.green - (a0, l0)) / d
        on = self.ongreen[self.R.idx(a0 + s * u[0], l0 + s * u[1])]
        return (float(s[np.argmax(on)]) if on.any() else d), d


def shot_numbers(Wd, P, club, lie, wx, bearing_shot):
    """model.shots() inputs for a deck club: a P copy and a wind hook on the shot's own line."""
    M, W = Wd.M, Wd.W
    spread, cmult, _ = LIE[lie]
    if lie == "rough":
        spread, cmult = SET["rough"]
    spread = spread * VAR["all_spread"] * SET["spread"]
    key = "deck:" + club
    P2 = dict(P)
    P2["width"] = dict(P["width"])
    P2["width"][key] = (DECK[club][2] * (70.0 / 65.0) * spread * SET.get("lat", 1.0)
                        * (VAR["wood_spread"] if club == "4-wood" else 1.0))
    P2["c_club"] = dict(P.get("c_club") or {})
    if club == "4-wood":
        P2["c_club"][key] = VAR["wood_carry"] + SET["wood_carry"]
    if SET["mis"]:
        P2["mis_slight"], P2["mis_heavy"] = SET["mis"]
    mb = SET.get("mis_by_carry")
    if mb:                                                   # mishit share by club length (config approach_pattern)
        c0, c1 = mb["mis_carry_range"]
        f = float(np.clip((DECK[club][0] - c0) / (c1 - c0), 0.0, 1.0))
        P2["mis_slight"] = mb["mis_slight"][0] + f * (mb["mis_slight"][1] - mb["mis_slight"][0])
        P2["mis_heavy"] = mb["mis_heavy"][0] + f * (mb["mis_heavy"][1] - mb["mis_heavy"][0])
        P2["mis_slight_carry"] = tuple(mb["mis_slight_carry"])
    P2["depth_mult"] = P["depth_mult"] * spread * SET.get("depth", 1.0)
    P2["_cmult"] = cmult
    rel = (wx["frm"] - bearing_shot) % 360
    sens = DECK[club][4]

    def hook(carry, roll, sig_lat, sig_car):
        carry = carry * cmult
        c2, t2, w2, d2, drift = W.adjust((carry, carry + roll, 4 * sig_lat, 4 * sig_car), wx["mph"], rel, club_name=sens)
        return c2, max(t2 - c2, 0.0), w2 / 4, d2 / 4, drift
    return key, P2, hook


def play(Wd, F, P, z, a0, l0, lie, wx, bearing_tee, detail=False, clubs=None):
    """Every club x direction from (a0, l0). Returns per-option arrays (and per-ball detail for the best ones)."""
    M, R = Wd.M, F.R
    d_front, d_ctr = F.front(a0, l0)
    u0 = (F.green - (a0, l0)) / d_ctr
    th0 = np.degrees(np.arctan2(u0[1], u0[0]))               # shot line, deg right of the tee line
    v_start = float(M.table("fairway" if lie == "fairway" else "rough", d_ctr, P))
    out = []
    hd0 = dict(F.hd)
    hd0.pop("elev", None)
    for club in (clubs or deck_clubs(lie)):
        key, P2, hook = shot_numbers(Wd, P, club, lie, wx, bearing_tee + th0)
        car, dev, roll = M.shots(hd0, key, P2, z, wind=hook)
        c_w, r_w, _, _, drift = hook(*M.club_numbers(hd0, key, P2))
        th = np.radians(th0 + ANG)[None, :]
        ua, ul = np.cos(th), np.sin(th)
        a = a0 + car[:, None] * ua - dev[:, None] * ul
        l = l0 + car[:, None] * ul + dev[:, None] * ua
        la, ll = a.copy(), l.copy()
        n = np.hypot(a - a0, l - l0)
        fa, fl = (a - a0) / np.maximum(n, 1e-9), (l - l0) / np.maximum(n, 1e-9)
        code = R.lie_at(a, l)
        left = np.broadcast_to(roll[:, None], a.shape).astype(float).copy()
        left = np.where(code == M.CODE["rough"], left * P["rough_roll"], left)
        left = np.where(M.HAZ[code], 0.0, left)
        while True:
            mv = left > 1e-9
            if not mv.any():
                break
            st = np.minimum(left, 2.0) * mv
            a, l = a + fa * st, l + fl * st
            left = left - st
            new = R.lie_at(a, l)
            was = (code == M.CODE["fairway"]) | (code == M.CODE["first_cut"])
            left = np.where(mv & (new == M.CODE["rough"]) & was, left * P["rough_roll"], left)
            left = np.where(M.HAZ[new], 0.0, left)
            code = np.where(mv, new, code)
        ia, il = R.idx(a, l)
        s = F.S[ia, il].copy()
        pen = F.pen[ia, il]
        if pen.any():                                        # drop where the ball last crossed the edge on its own line
            pa, pl, pfa, pfl, pn = a[pen], l[pen], fa[pen], fl[pen], np.hypot(a[pen] - a0, l[pen] - l0)
            da, dl = np.full(pa.shape, a0), np.full(pa.shape, l0)
            found = np.zeros(pa.shape, bool)
            for k in np.arange(1.0, float(pn.max()) + 1.0, 1.0):
                t = np.maximum(pn - k, 0.0)
                qa, ql = a0 + pfa * t, l0 + pfl * t
                dry = ~F.pen[R.idx(qa, ql)] | (t <= 0)
                newf = dry & ~found
                da[newf], dl[newf] = qa[newf], ql[newf]
                found |= newf
                if found.all():
                    break
            s[pen] = 1.0 + F.Srough[R.idx(da, dl)]
        ob = code == M.CODE["ob"]
        s[ob] = 1.0 + v_start                                # stroke and distance: play again from the same spot
        lostb = np.zeros(code.shape, bool)
        if LOST:                                             # tall grass: F.S carries the lost marker there
            lostb = s < 0
            ev, s = Wd.vc.lost_ball_ev(s)
        else:
            ev = 1.0 + s.mean(0)
        pen = pen | lostb
        stock = c_w + r_w
        out.append(dict(club=club, ev=ev, stock=float(stock), carry=float(c_w), drift=float(drift),
                        a=a, l=l, la=la, ll=ll, code=code, s=s, pen=pen | ob, car=car))
    return dict(opts=out, d_front=d_front, d_ctr=d_ctr, th0=float(th0), a0=a0, l0=l0, lie=lie)


def summarise(Wd, F, res):
    """Best GO and best LAY-UP of a play() result, with shares."""
    M = Wd.M
    d_front, d_ctr, a0, l0 = res["d_front"], res["d_ctr"], res["a0"], res["l0"]
    best = {"go": None, "lay": None}
    for o in res["opts"]:
        kind = "lay" if o["stock"] <= d_front - LAY_GAP else "go"
        sm = np.convolve(o["ev"], [0.25, 0.5, 0.25], mode="same")
        sm[0], sm[-1] = o["ev"][0], o["ev"][-1]
        j = int(np.argmin(sm))
        if best[kind] is None or sm[j] < best[kind][0]:
            best[kind] = (float(sm[j]), o, j)
    out = dict(d_front=round(d_front, 1), d_ctr=round(d_ctr, 1), start=[round(a0, 1), round(l0, 1)], lie=res["lie"])
    rows = []
    for o in res["opts"]:
        sm = np.convolve(o["ev"], [0.25, 0.5, 0.25], mode="same")
        sm[0], sm[-1] = o["ev"][0], o["ev"][-1]
        j = int(np.argmin(sm))
        th = np.radians(res["th0"] + ANG[j])
        ta = a0 + o["stock"] * np.cos(th) - o["drift"] * np.sin(th)
        tl = l0 + o["stock"] * np.sin(th) + o["drift"] * np.cos(th)
        rows.append(dict(club=o["club"], kind="lay" if o["stock"] <= d_front - LAY_GAP else "go", ev=round(float(sm[j]), 4),
                         ang=float(ANG[j]), stock=round(o["stock"], 1), target=[round(float(ta), 1), round(float(tl), 1)],
                         leave=round(float(np.hypot(ta - F.green[0], tl - F.green[1])), 1),
                         penalty=round(float(o["pen"][:, j].mean()), 4),
                         target_lie=M.LIES[int(F.R.lie_at(np.array([ta]), np.array([tl]))[0])]))
    out["by_club"] = rows
    best_bag = {"go": None, "lay": None}                    # the same, stock clubs only (no in-between shot)
    for o in res["opts"]:
        if o["club"] in GAP:
            continue
        kind = "lay" if o["stock"] <= d_front - LAY_GAP else "go"
        sm = np.convolve(o["ev"], [0.25, 0.5, 0.25], mode="same")
        sm[0], sm[-1] = o["ev"][0], o["ev"][-1]
        j = int(np.argmin(sm))
        if best_bag[kind] is None or sm[j] < best_bag[kind][0]:
            best_bag[kind] = (float(sm[j]), o, j)
    todo = [(k, b) for k, b in best.items()]
    todo += [(k + "_bag", b) for k, b in best_bag.items() if b is not None and best[k] is not None and best[k][1]["club"] in GAP]
    for kind, b in todo:
        if b is None:
            out[kind] = None
            continue
        ev, o, j = b
        a, l, code = o["a"][:, j], o["l"][:, j], o["code"][:, j]
        on = F.ongreen[F.R.idx(a, l)]
        dg = np.hypot(a - F.green[0], l - F.green[1])
        pen = o["pen"][:, j]
        sand = code == M.CODE["sand"]
        trees = code == M.CODE["recovery"]
        around = ~on & ~pen & ~sand & ~trees & (dg <= 40)
        ang = float(ANG[j])
        th = np.radians(res["th0"] + ang)
        # the target = where a solid shot finishes (stock total on the chosen line, wind drift included)
        ta = a0 + o["stock"] * np.cos(th) - o["drift"] * np.sin(th)
        tl = l0 + o["stock"] * np.sin(th) + o["drift"] * np.cos(th)
        ok = ~pen & ~trees
        fwy = np.isin(code, [M.CODE["fairway"], M.CODE["first_cut"]]) & ~on
        out[kind] = dict(club=o["club"], ev=round(ev, 4), se=round(float(o["s"][:, j].std(ddof=1) / np.sqrt(len(a))), 4),
                         ang=ang, aim_at_green=round(float(np.tan(np.radians(ang)) * d_ctr), 1),
                         target=[round(float(ta), 1), round(float(tl), 1)],
                         leave=round(float(np.hypot(ta - F.green[0], tl - F.green[1])), 1),
                         leave_med=round(float(np.median(dg[ok])), 1) if ok.any() else None,
                         stock=round(o["stock"], 1), carry=round(o["carry"], 1),
                         green=round(float(on.mean()), 4), around=round(float(around.mean()), 4),
                         fairway=round(float(fwy.mean()), 4),
                         sand=round(float(sand.mean()), 4), penalty=round(float(pen.mean()), 4),
                         trees=round(float(trees.mean()), 4),
                         reach_carry=round(float((o["car"] >= d_front).mean()), 4),
                         reach_total=round(float(((np.hypot(a - a0, l - l0) >= d_front) | on).mean()), 4),
                         target_lie=M.LIES[int(F.R.lie_at(np.array([ta]), np.array([tl]))[0])],
                         ev_by_ang=[round(float(x), 4) for x in o["ev"]])
    if out["go"] and out["lay"]:
        out["go_minus_lay"] = round(out["go"]["ev"] - out["lay"]["ev"], 4)
    return out


def tee_shot(Wd, hd, R, S, P, z, club, wx, bearing):
    """Engine tee shot at its best aim for the day: aim, pattern centre, per-ball finishes on an aim grid."""
    M, D, WG2 = Wd.M, Wd.D, Wd.WG2
    rel = (wx["frm"] - bearing) % 360
    hook = WG2.wind_hook(club, wx["mph"], rel) if wx["mph"] > 0 else None
    c, r, sl, sc = M.club_numbers(hd, club, P)
    dr = 0.0
    if hook:
        c, r, sl, sc, dr = hook(c, r, sl, sc)
    L = float(D.AIM_LIMIT)
    aims = np.arange(-(L + 20.0), L + 20.01, 0.5)
    ev, _ = M.ev_curve(R, S, hd, club, P, z, aims, wind=hook)
    ra = D.robust_aim(aims, ev, lo=-L - dr, hi=L - dr)
    return dict(club=club, aim=float(ra["aim"]), ev=float(ra["ev"]), carry=float(c), total=float(c + r), drift=float(dr),
                centre=[float(c + r), float(ra["aim"] + dr)], hook=hook)


def solve_hole(Wd, h, set_name, day, n=4000, n_grid=500, n_tee=12000, seed=5, two_stage=True):
    M, D = Wd.M, Wd.D
    hd, back = Wd.hole(h, set_name)
    wx = Wd.wx(h, DAYS[day])
    P = M.central(temp_f=wx["temp"])
    bearing = float(Wd.course.BEARINGS[h])
    R0, Rb = Wd.big(hd)
    F = Field(Wd, hd, P, Rb)
    S0 = R0.strokes(P, hd["length"])
    zt = M.draws_z(n_tee, 77)
    z = M.draws_z(n, seed)
    out = dict(hole=h, set=set_name, day=day, back=back, length=hd["length"], wx={k: round(v, 1) for k, v in wx.items()},
               green=[round(float(x), 1) for x in F.green], bearing=bearing,
               green_poly=[[round(float(a), 1), round(float(b), 1)] for a, b in F.gpoly], tee={}, second={})
    tees = {}
    for club in ("Driver", "2-wood", "4-wood"):
        t = tee_shot(Wd, hd, R0, S0, P, zt, club, wx, bearing)
        tees[club] = t
        out["tee"][club] = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in t.items() if k != "hook"}
    order = sorted(tees, key=lambda c: tees[c]["ev"])
    out["tee_pick_engine"] = order[0]
    for club in ("Driver", "2-wood"):
        a0, l0 = tees[club]["centre"]
        for lie in ("fairway", "rough"):
            if lie == "rough" and club != order[0] and club != "Driver":
                continue
            res = play(Wd, F, P, z, a0, l0, lie, wx, bearing)
            sm = summarise(Wd, F, res)
            sm["spot_lie"] = M.LIES[int(Rb.lie_at(np.array([a0]), np.array([l0]))[0])]
            out["second"][f"{club}|{lie}"] = sm
    if two_stage:
        out["two_stage"] = two_stage_check(Wd, F, hd, R0, S0, P, wx, bearing, tees, zt, n_grid)
    return out


def two_stage_check(Wd, F, hd, R0, S0, P, wx, bearing, tees, zt, n_grid, step=6.0):
    """Tee clubs re-scored with the second shot played out from where each tee ball finishes: a value grid
    (best second shot; best lay-up only) per lie on a 6-yd lattice over the tee balls' area, interpolated."""
    from scipy.interpolate import RegularGridInterpolator
    M = Wd.M
    z = M.draws_z(n_grid, 9)
    fin = {}
    for club, t in tees.items():
        aims = t["aim"] + np.arange(-10.0, 10.01, 1.0)
        ev, (a, l, lie, s) = M.ev_curve(R0, S0, hd, club, P, zt, aims, wind=t["hook"])
        fin[club] = (aims, ev, a, l, lie, s)
    A = np.concatenate([f[2].ravel() for f in fin.values()])
    L = np.concatenate([f[3].ravel() for f in fin.values()])
    ok = np.concatenate([np.isin(f[4], [M.CODE[k] for k in ("fairway", "first_cut", "rough", "sand")]).ravel() for f in fin.values()])
    ga = np.arange(np.floor(A[ok].min() / step) * step, A[ok].max() + step, step)
    gl = np.arange(np.floor(L[ok].min() / step) * step, L[ok].max() + step, step)
    # only nodes near a ball
    occ = np.zeros((len(ga), len(gl)), bool)
    ia = np.clip(np.rint((A[ok] - ga[0]) / step).astype(int), 0, len(ga) - 1)
    il = np.clip(np.rint((L[ok] - gl[0]) / step).astype(int), 0, len(gl) - 1)
    occ[ia, il] = True
    from scipy import ndimage
    occ = ndimage.binary_dilation(occ, iterations=1)
    V = {lie: {k: np.full(occ.shape, np.nan) for k in ("best", "lay")} for lie in LIE}
    for i, a0 in enumerate(ga):
        for j, l0 in enumerate(gl):
            if not occ[i, j]:
                continue
            for lie in LIE:
                # the tee re-check plays the second shot with stock clubs only (no in-between shot)
                res = play(Wd, F, P, z, float(a0), float(l0), lie, wx, bearing, clubs=[c for c in deck_clubs(lie) if c not in GAP])
                b, ly = np.inf, np.inf
                for o in res["opts"]:
                    m = float(o["ev"].min())
                    b = min(b, m)
                    if o["stock"] <= res["d_front"] - LAY_GAP:
                        ly = min(ly, m)
                V[lie]["best"][i, j] = b
                V[lie]["lay"][i, j] = ly if np.isfinite(ly) else b
    out = {}
    for kind in ("engine", "best", "lay"):
        row = {}
        for club, (aims, ev, a, l, lie, s) in fin.items():
            if kind == "engine":
                tot = 1.0 + s
            else:
                tot = 1.0 + s.copy()
                if LOST:                                     # the replay is worth this kind's own value: re-solved below
                    tot[lie == M.CODE["native"]] = 0.0       # = 1 + the lost marker
                for lname, codes in (("fairway", ("fairway", "first_cut")), ("rough", ("rough",)), ("sand", ("sand",))):
                    grid = V[lname][kind]
                    filled = np.where(np.isnan(grid), np.nanmean(grid), grid)
                    f = RegularGridInterpolator((ga, gl), filled, bounds_error=False, fill_value=None)
                    m = np.isin(lie, [M.CODE[c] for c in codes]) & ~F.ongreen[F.R.idx(a, l)]
                    if m.any():
                        v = f(np.column_stack([a[m], l[m]]))
                        if lname == "fairway":
                            fc = lie[m] == M.CODE["first_cut"]
                            if fc.any():
                                gr = V["rough"][kind]
                                fr = RegularGridInterpolator((ga, gl), np.where(np.isnan(gr), np.nanmean(gr), gr),
                                                             bounds_error=False, fill_value=None)
                                v2 = fr(np.column_stack([a[m][fc], l[m][fc]]))
                                v[fc] = v[fc] + P["first_cut"] * (v2 - v[fc])
                        tot[m] = 1.0 + v
                if LOST:
                    tot = 1.0 + Wd.vc.lost_ball_ev(tot - 1.0)[1]
            e = tot.mean(0)
            sm = np.convolve(e, [0.25, 0.5, 0.25], mode="same")
            sm[0], sm[-1] = e[0], e[-1]
            j = int(np.argmin(sm))
            row[club] = dict(ev=round(float(sm[j]), 4), aim=float(aims[j]), se=round(float(tot[:, j].std(ddof=1) / np.sqrt(tot.shape[0])), 4),
                             per=tot[:, j])
        base = row["Driver"]["per"]
        for club in row:
            dd = row[club]["per"] - base
            row[club]["vs_driver"] = round(float(row[club]["ev"] - row["Driver"]["ev"]), 4)
            row[club]["vs_driver_se"] = round(float(dd.std(ddof=1) / np.sqrt(len(dd))), 4)
        for club in row:
            del row[club]["per"]
        out[kind] = row
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="solve")
    ap.add_argument("--which", default="truth")
    ap.add_argument("--sets", default="Back")
    ap.add_argument("--holes", default="3,6,13,18")
    ap.add_argument("--days", default="sat,sun")
    ap.add_argument("--no-two-stage", action="store_true")
    ap.add_argument("--two-stage-days", default="sat")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    if a.cmd == "describe":
        return describe(a)
    use_set()
    os.makedirs(OUT, exist_ok=True)
    Wd = World(a.which)
    for s in a.sets.split(","):
        assert BASE_OF[s] == a.which, (s, a.which)
        path = os.path.join(OUT, f"par5_second_{s.replace(' ', '_')}{a.tag}.json")
        res = json.load(open(path)) if os.path.exists(path) else {}
        for h in [int(x) for x in a.holes.split(",")]:
            for day in a.days.split(","):
                ts = (not a.no_two_stage) and day in a.two_stage_days.split(",")
                r = solve_hole(Wd, h, s, day, two_stage=ts)
                res[f"{h}|{day}"] = r
                d = r["second"].get(r["tee_pick_engine"] + "|fairway") or r["second"]["Driver|fairway"]
                print(s, h, day, "pick", r["tee_pick_engine"], r["tee"][r["tee_pick_engine"]]["centre"],
                      "front", d["d_front"], "go", d["go"] and (d["go"]["club"], d["go"]["ev"], d["go"]["reach_carry"]),
                      "lay", d["lay"] and (d["lay"]["club"], d["lay"]["ev"], d["lay"]["target"], d["lay"]["leave"]),
                      file=sys.stderr, flush=True)
                json.dump(res, open(path, "w"), indent=0)


def describe(a):
    """Add the fairway's left / right edge (yds right of the tee line) across each target to the saved results."""
    Wd = World(a.which)
    M = Wd.M
    for s in a.sets.split(","):
        path = os.path.join(OUT, f"par5_second_{s.replace(' ', '_')}{a.tag}.json")
        res = json.load(open(path))
        cache = {}
        for key, r in res.items():
            h = r["hole"]
            if h not in cache:
                hd, _ = Wd.hole(h, s)
                cache[h] = Wd.big(hd)[1]
            Rb = cache[h]
            fwm = np.isin(Rb.lie, [M.CODE["fairway"], M.CODE["first_cut"]])

            def span(t):
                ia, il = Rb.idx(np.array([t[0]]), np.array([t[1]]))
                row = fwm[int(ia[0])]
                j = int(il[0])
                if not row[j]:
                    on = np.nonzero(row)[0]
                    if not len(on) or np.abs(on - j).min() * M.RES > 15:
                        return None
                    j = int(on[np.argmin(np.abs(on - j))])
                lo = hi = j
                while lo > 0 and row[lo - 1]:
                    lo -= 1
                while hi < len(row) - 1 and row[hi + 1]:
                    hi += 1
                return [float(Rb.l[lo]), float(Rb.l[hi])]
            for v in r["second"].values():
                v["start_fw"] = span(v["start"])
                for kind in ("go", "lay", "go_bag", "lay_bag"):
                    if v.get(kind):
                        v[kind]["fw"] = span(v[kind]["target"])
                for row in v["by_club"]:
                    row["fw"] = span(row["target"])
        json.dump(res, open(path, "w"), indent=0)
        print("described", path)


if __name__ == "__main__":
    main()
