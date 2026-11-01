"""Confirm-and-resolve for pathroute v2: the golfer confirms a fact, the route is re-solved with it fixed.

    s = Session(d, pr, calib)                  # d: pathroute v1+v2 features of one course, pr: Models2.predict(d)
    holes, conf = s.solve()                    # decoded holes + calibrated per-hole pair confidence (fixed -> 1.0)
    i = s.ask()                                # index of the hole to ask about next (lowest confidence) or None
    s.confirm_pair(number, tee, green)         # (a) "hole N is this tee complex + green" (number None = pair only)
    s.not_a_hole(green)                        # the green is a practice / putting green
    s.hole_one(tee)                            # (b) "this tee is hole 1" (fixes the start and the direction)
    s.solve()                                  # re-solve with every fact fixed (decode2.decode2(fix=...))

Facts are kept in `s.fix` (decode2.apply_fix format, JSON-able with tee / green indices); `to_ids` / `from_ids`
convert them to OSM ids so an app can store them and re-solve later.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
for _p in (HERE, os.path.join(ZT, "pathroute"), ZT):
    if _p not in sys.path:
        sys.path.append(_p)
import complexes as CX  # noqa: E402
import run2 as R2  # noqa: E402


class Session:
    def __init__(self, d, pr, calib, cfg=None, fix=None):
        self.d, self.pr, self.calib = d, pr, calib
        self.cfg = cfg or R2.CFG
        self.comp = CX.cluster(len(d["tees"]), d["tpp"], pr["tpair"], thr=self.cfg["comp_thr"])
        self.fix = dict(pairs=[], not_green=[], first_tee=None)
        if fix:
            self.fix.update({k: (list(v) if isinstance(v, (list, tuple)) else v) for k, v in fix.items()})
        self.holes, self.conf, self.route_conf = [], np.zeros(0), 0.0

    # ------------------------------------------------------------------ facts
    def confirm_pair(self, number, tee, green):
        tee, green = int(tee), int(green)
        self.fix["pairs"] = [p for p in self.fix["pairs"] if p[2] != green and p[1] != tee
                             and (number is None or p[0] != number)]
        self.fix["pairs"].append((None if number is None else int(number), tee, green))

    def not_a_hole(self, green):
        if int(green) not in self.fix["not_green"]:
            self.fix["not_green"].append(int(green))

    def hole_one(self, tee):
        self.fix["first_tee"] = int(tee)

    def fixed_pairs(self):
        return {(t, g) for _, t, g in self.fix["pairs"]}

    # ------------------------------------------------------------------ solve / ask
    def solve(self):
        holes, rc, X = R2.decode_course(self.d, self.pr, self.cfg, fix=self.fix, comp=self.comp)
        if not holes and self.fix.get("first_tee") is not None:          # inconsistent hole-1 tee: drop it
            self.fix["first_tee"] = None
            holes, rc, X = R2.decode_course(self.d, self.pr, self.cfg, fix=self.fix, comp=self.comp)
        c = self.calib.predict(X) if len(holes) else np.zeros(0)
        fp = self.fixed_pairs()
        c = np.array([1.0 if (h["t"], h["g"]) in fp else float(ci) for h, ci in zip(holes, c)])
        self.holes, self.conf, self.route_conf = holes, c, rc
        return holes, c

    def ask(self, thr=1.0):
        """Index of the unconfirmed hole with the lowest confidence (< thr), or None."""
        fp = self.fixed_pairs()
        best = None
        for i, (h, c) in enumerate(zip(self.holes, self.conf)):
            if (h["t"], h["g"]) not in fp and c < thr and (best is None or c < self.conf[best]):
                best = i
        return best

    # ------------------------------------------------------------------ ids <-> indices
    def to_ids(self):
        T, G = self.d["tees"], self.d["greens"]
        return dict(pairs=[[n, T[t]["id"], G[g]["id"]] for n, t, g in self.fix["pairs"]],
                    not_green=[G[g]["id"] for g in self.fix["not_green"]],
                    first_tee=None if self.fix["first_tee"] is None else T[self.fix["first_tee"]]["id"])

    @staticmethod
    def from_ids(d, f):
        ti = {t["id"]: i for i, t in enumerate(d["tees"])}
        gi = {g["id"]: i for i, g in enumerate(d["greens"])}
        return dict(pairs=[(n, ti[t], gi[g]) for n, t, g in f.get("pairs") or () if t in ti and g in gi],
                    not_green=[gi[g] for g in f.get("not_green") or () if g in gi],
                    first_tee=ti.get(f.get("first_tee")))
