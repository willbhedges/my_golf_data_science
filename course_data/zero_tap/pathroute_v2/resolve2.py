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


# Sticky re-solve: on every re-solve after a fact, each unconfirmed pair of the previous solve gets a bonus of
# w = alpha * conf nats (w = pin_w once conf >= pin) so an answer only moves the holes it implicates, and a pair that
# survives keeps its previous confidence (its min-marginal is not recomputed). None = plain re-solve.
STICKY = dict(alpha=0.0, pin=0.0, pin_w=30.0, keep=True, cap=1.0, boxes=False)


def sticky_w(c, st):
    return float(st["pin_w"]) if c >= st["pin"] else float(st["alpha"]) * float(c)


class Session:
    def __init__(self, d, pr, calib, cfg=None, fix=None, calib_fix=None, sticky="default"):
        """calib: confidence of the free decode; calib_fix (optional, confidence.Calib2 fitted on constrained
        re-solves by calib_resolve.py): used once any fact is set. sticky: STICKY-like dict, None = plain re-solve."""
        self.d, self.pr, self.calib, self.calib_fix = d, pr, calib, calib_fix
        self.sticky = STICKY if sticky == "default" else sticky
        self.prev = {}                          # (tee, green) -> confidence of the previous solve's unconfirmed holes
        self.cfg = cfg or R2.CFG
        self.comp = CX.cluster(len(d["tees"]), d["tpp"], pr["tpair"], thr=self.cfg["comp_thr"])
        self.fix = dict(pairs=[], not_green=[], first_tee=None)
        if fix:
            self.fix.update({k: (list(v) if isinstance(v, (list, tuple)) else v) for k, v in fix.items()})
        self.holes, self.conf, self.route_conf = [], np.zeros(0), 0.0
        self.X, self.free = np.zeros((0, 0)), None

    # ------------------------------------------------------------------ facts
    def confirm_pair(self, number, tee, green):
        tee, green = int(tee), int(green)
        self.fix["pairs"] = [p for p in self.fix["pairs"] if p[2] != green and p[1] != tee
                             and (number is None or p[0] != number)]
        self.fix["pairs"].append((None if number is None else int(number), tee, green))
        if self.fix.get("reject"):
            self.fix["reject"] = [r for r in self.fix["reject"] if tuple(r) != (tee, green)]

    def confirm_yes(self, i, number=None):
        """"Yes": hole i of the current solve is right (as decoded) -> it is confirmed WITHOUT a re-solve (the pin /
        number applies at the next re-solve). Re-solving after a "yes" moves more right holes than it repairs (dev:
        PATHROUTE.md "Sticky re-solve"), so the app re-solves only after a correction / "no" / practice green."""
        h = self.holes[i]
        self.confirm_pair(number, h["t"], h["g"])
        if self.conf is not None and len(self.conf):
            self.conf = np.array(self.conf, float)
            self.conf[i] = 1.0
        self.prev.pop((h["t"], h["g"]), None)
        if getattr(self, "kept", None):
            self.kept[i] = 2

    def drop_hole(self, i):
        """"Not a hole" for hole i's green (a practice green) WITHOUT a re-solve: the hole leaves the route (a missing
        true hole is then added by the golfer, as in the no-resolve flow)."""
        h = self.holes[i]
        self.not_a_hole(h["g"])
        self.prev.pop((h["t"], h["g"]), None)
        self.holes = [x for k, x in enumerate(self.holes) if k != i]
        if self.conf is not None and len(self.conf):
            self.conf = np.delete(np.asarray(self.conf, float), i)
        if getattr(self, "kept", None):
            self.kept = [x for k, x in enumerate(self.kept) if k != i]

    def reject_pair(self, tee, green):
        """"No, this is not a hole": the tee's complex never plays to this green."""
        r = self.fix.setdefault("reject", [])
        if (int(tee), int(green)) not in {tuple(x) for x in r}:
            r.append((int(tee), int(green)))
        self.fix["pairs"] = [p for p in self.fix["pairs"] if (p[1], p[2]) != (int(tee), int(green))]

    def not_a_hole(self, green):
        if int(green) not in self.fix["not_green"]:
            self.fix["not_green"].append(int(green))
        self.fix["pairs"] = [p for p in self.fix["pairs"] if p[2] != int(green)]

    def hole_one(self, tee):
        self.fix["first_tee"] = int(tee)

    def fixed_pairs(self):
        return {(t, g) for _, t, g in self.fix["pairs"]}

    # ------------------------------------------------------------------ solve / ask
    def free_pairs(self):
        """(tee, green) pairs of the no-fact decode (cached): the `changed` calibration feature."""
        if self.free is None:
            fh, _, _ = R2.decode_course(self.d, self.pr, self.cfg, conf_feats=False, comp=self.comp)
            self.free = {(h["t"], h["g"]) for h in fh}
        return self.free

    def has_fix(self):
        return bool(self.fix.get("pairs") or self.fix.get("not_green") or self.fix.get("reject")
                    or self.fix.get("first_tee") is not None)

    def solve_fix(self):
        """The decoder's fix: the golfer facts + (sticky re-solve) the previous solve's unconfirmed pairs."""
        st = self.sticky
        if not st or not self.prev or not self.has_fix():
            return self.fix
        fp = self.fixed_pairs()
        sk = [(t, g, sticky_w(c, st)) for (t, g), c in sorted(self.prev.items()) if (t, g) not in fp]
        return dict(self.fix, sticky=[x for x in sk if x[2] > 0]) if any(x[2] > 0 for x in sk) else self.fix

    def solve(self, conf=True):
        """Re-solve with every fact; conf=False: pairing / numbering only (no min-marginals, self.conf = None)."""
        fr = self.free_pairs()
        st = self.sticky
        keep = dict(self.prev) if (st and st.get("keep") and self.has_fix()) else {}
        fx = self.solve_fix()
        kw = dict(comp=self.comp, free=fr, conf_feats=conf, mm_skip=set(keep))
        holes, rc, X = R2.decode_course(self.d, self.pr, self.cfg, fix=fx, **kw)
        if not holes and self.fix.get("first_tee") is not None:          # inconsistent hole-1 tee: drop it
            self.fix["first_tee"] = None
            fx = self.solve_fix()
            holes, rc, X = R2.decode_course(self.d, self.pr, self.cfg, fix=fx, **kw)
        self.X = X
        if keep and st.get("boxes"):
            holes = self.keep_boxes(holes, keep)
        self.holes, self.route_conf = holes, rc
        if not conf:
            self.conf = None
            return holes, None
        cal = self.calib_fix if (self.has_fix() and self.calib_fix is not None) else self.calib
        c = cal.predict(X) if len(holes) else np.zeros(0)
        fp = self.fixed_pairs()
        cap = float(st.get("cap", 1.0)) if (st and keep) else 1.0      # a pair the re-solve moved: at most cap
        c = np.array([1.0 if (h["t"], h["g"]) in fp else keep.get((h["t"], h["g"]), min(float(ci), cap))
                      for h, ci in zip(holes, c)])
        self.kept = [2 if (h["t"], h["g"]) in fp else int((h["t"], h["g"]) in keep) for h in holes]
        self.conf = c
        self.prev = {(h["t"], h["g"]): float(ci) for h, ci in zip(holes, c) if (h["t"], h["g"]) not in fp}
        self.prev_boxes = {(h["t"], h["g"]): list(h["boxes"]) for h in holes}
        return holes, c

    def keep_boxes(self, holes, keep):
        """A pair the sticky re-solve kept keeps its previous box set (the decoder hands boxes out in tour order, so a
        re-order would move a right hole's true tee box to a neighbour), minus tees now used by another hole."""
        pb = getattr(self, "prev_boxes", {})
        kept = [(h["t"], h["g"]) in keep and (h["t"], h["g"]) in pb for h in holes]
        taken = {h["t"] for h in holes} | {b for h, k in zip(holes, kept) if not k for b in h["boxes"]}
        tc, gc = np.asarray(self.d["tc"], float), np.asarray(self.d["gc"], float)
        out = []
        for h, k in zip(holes, kept):
            if k:
                bx = sorted(int(b) for b in pb[(h["t"], h["g"])] if b not in taken)
                L = max([float(np.hypot(*(gc[h["g"]] - tc[b]))) for b in bx + [h["t"]]])
                h = dict(h, boxes=bx, L=L)
            out.append(h)
        return out

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
                    first_tee=None if self.fix["first_tee"] is None else T[self.fix["first_tee"]]["id"],
                    **({"reject": [[T[t]["id"], G[g]["id"]] for t, g in self.fix["reject"]]}
                       if self.fix.get("reject") else {}))

    @staticmethod
    def from_ids(d, f):
        ti = {t["id"]: i for i, t in enumerate(d["tees"])}
        gi = {g["id"]: i for i, g in enumerate(d["greens"])}
        return dict(pairs=[(n, ti[t], gi[g]) for n, t, g in f.get("pairs") or () if t in ti and g in gi],
                    not_green=[gi[g] for g in f.get("not_green") or () if g in gi],
                    first_tee=ti.get(f.get("first_tee")),
                    **({"reject": [(ti[t], gi[g]) for t, g in f.get("reject") or () if t in ti and g in gi]}
                       if f.get("reject") else {}))
