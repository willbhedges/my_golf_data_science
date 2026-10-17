"""Golfer confirm: the fewest questions that make the hole routing right (routing_v2 + its posterior).

    from confirm import Session
    s = Session(inp, card, fc=fc, boundary=boundary)       # routing_v2 context + first solve
    payload = s.payload(course={"name": ...})              # golf_confirm/1 JSON for the app (CONFIRM_UX.md)
    s.answer({"question": "q1", "answer": "yes"})          # or "no", or {"tee_ll": [lon, lat], "green_ll": [...]}
    payload = s.payload()                                  # re-solved: one answer propagates to every hole

Questions (both re-solve the whole round with the answer as a constraint):
  confirm  "Is this hole 7?" - the map shows hole 7's line (tee -> green); 1 tap. yes pins the hole; no forbids
           that (green, tee complex) for hole 7.
  locate   "Tap hole 7's tee, then its green" - 2 taps. Pins hole 7 to the tapped points (snapped to a detected
           tee box / green within 25 / 15 yds, else the taps become new candidates).
Choice: expected information gain per tap over the posterior's routings (routing_v2: Boltzmann over the distinct
top routings at the calibrated temperature): a confirm on hole n is worth H(p_n) bits (p_n = posterior of the
shown answer, floored at 2 % doubt), a locate is worth the entropy of hole n's whole answer distribution.
The session stops asking when every unconfirmed hole has p_hole >= p_stop (the flag threshold).
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import routing as R  # noqa: E402
import routing_v2 as R2  # noqa: E402

DOUBT = 0.02
RISK_CONFIRM_P = 0.35
SNAP_GREEN, SNAP_TEE = 15.0, 25.0


def entropy(ps):
    ps = np.asarray([p for p in ps if p > 0], float)
    return float(-(ps * np.log2(ps)).sum()) if len(ps) else 0.0


class Session:
    def __init__(self, inp, card, fc=None, boundary=None, w=None, tau=None, p_check=None, p_stop=None, policy="risk"):
        w0, t0, p0 = R2.load_weights()
        self.w = w0 if w is None else w
        self.tau = t0 if tau is None else tau
        self.p_check = p0 if p_check is None else p_check
        self.p_stop = self.p_check if p_stop is None else p_stop
        self.inp, self.card, self.fc, self.boundary = dict(inp), card, fc, boundary
        self.policy = policy
        self.ctx = R2.context(self.inp, card, fc=fc, boundary=boundary)
        self.fixed, self.exclude = {}, {}
        self.taps, self.history = 0, []
        self.rejected = set()                  # holes answered "no": only a locate is asked next
        self.res = None
        self._qs = {}
        self.solve()

    # ------------------------------------------------------------------ solve / posterior
    def solve(self):
        self.res = R2.solve(self.ctx, w=self.w, fixed=self.fixed, exclude=self.exclude, tau=self.tau,
                            p_check=self.p_check, keep_top=300, margins=True)
        top = self.res.get("top") or []
        self.keys = [(c, [R2._hole_key(self.ctx, t, g) for t, g in a]) for c, a in top]
        return self.res

    def marginals(self):
        if not self.keys:
            return []
        c = np.array([k[0] for k in self.keys])
        p = np.exp(-(c - c.min()) / max(self.tau, 1e-6))
        p /= p.sum()
        out = []
        for h in range(len(self.keys[0][1])):
            d = {}
            for pi, k in zip(p, self.keys):
                d[k[1][h]] = d.get(k[1][h], 0.0) + float(pi)
            out.append(d)
        return out

    def done(self):
        hs = self.res.get("holes", {})
        return all(h.get("p_hole", 0) >= self.p_stop for r, h in hs.items() if r not in self.fixed)

    # ------------------------------------------------------------------ questions
    def questions(self, k=5, policy=None):
        """[question] best first. policy "eig": expected bits per tap over the posterior; "risk": the hole most
        likely wrong first, as a confirm when p_hole >= RISK_CONFIRM_P (else, or after a "no", a locate), scored
        by (1 - p_hole) per tap."""
        policy = policy or self.policy
        hs = self.res.get("holes", {})
        marg = self.marginals()
        qs = []
        for r, h in hs.items():
            if r in self.fixed:
                continue
            d = marg[int(r) - 1] if marg else {}
            key = R2._hole_key(self.ctx, h["t_idx"], h["g_idx"])
            p = min(max(d.get(key, 0.0), 1e-6), 1 - 1e-6)
            ig_c = max(entropy([p, 1 - p]), entropy([1 - DOUBT, DOUBT]) * (1 - p))
            ig_l = entropy(list(d.values()) + [max(0.0, 1 - sum(d.values()))])
            line = [h.get("back_tee_ll") or h.get("tee_ll"), h.get("green_ll")]
            if r not in self.rejected:
                qs.append(dict(id=f"c{r}", kind="confirm", ref=r, taps=1, bits=round(ig_c, 3),
                               bits_per_tap=round(ig_c, 3), p_hole=round(p, 3),
                               prompt=f"Is this hole {r}?" + (f" (par {h['par']})" if h.get("par") else ""),
                               show=dict(line=line if all(line) else None, tee_ll=h.get("tee_ll"), green_ll=h.get("green_ll")),
                               answers=["yes", "no"]))
            if r in self.rejected:             # the golfer said the shown line is wrong: the answer is open again
                ig_l = max(ig_l, 1.0)
            qs.append(dict(id=f"l{r}", kind="locate", ref=r, taps=2, bits=round(ig_l, 3),
                           bits_per_tap=round(ig_l / 2, 3), p_hole=round(p, 3),
                           prompt=f"Tap hole {r}'s tee, then its green",
                           show=dict(line=None, tee_ll=None, green_ll=None), answers=[{"tee_ll": "[lon, lat]",
                                                                                         "green_ll": "[lon, lat]"}]))
        if policy == "risk":
            for q in qs:
                p = q["p_hole"]
                want = "locate" if (q["ref"] in self.rejected or p < RISK_CONFIRM_P) else "confirm"
                q["risk_per_tap"] = round((1 - p) / q["taps"], 4) if q["kind"] == want else -1.0
            qs = [q for q in qs if q["risk_per_tap"] >= 0]
            qs.sort(key=lambda q: (-q["risk_per_tap"], int(q["ref"])))
        else:
            qs.sort(key=lambda q: (-q["bits_per_tap"], q["taps"], int(q["ref"])))
        self._qs = {q["id"]: q for q in qs}
        return qs[:k]

    # ------------------------------------------------------------------ answers
    def _snap_or_add(self, kind, ll, tol):
        items = self.ctx["G"] if kind == "green" else self.ctx["T"]
        p = R.Proj(*ll)
        d = np.array([math.hypot(*p.fwd(*it["ll"])) for it in items]) if items else np.array([])
        if len(d) and d.min() <= tol:
            return int(np.argmin(d))
        new = dict(id=f"golfer:{kind}:{len(items)}", ll=tuple(ll), poly=None, src="osm")
        self.inp["greens" if kind == "green" else "tees"] = list(items) + [new]
        # appended at the end: earlier pins / exclusions (indices, hole keys) stay valid
        self.ctx = R2.context(self.inp, self.card, fc=self.fc, boundary=self.boundary)
        return len(items)

    def answer(self, a, resolve=True):
        """a = {"question": id, "answer": "yes" | "no" | {"tee_ll": [lon, lat], "green_ll": [lon, lat]}}
        (or {"ref": "7", "kind": "locate", ...}). -> the new result."""
        q = self._qs.get(a.get("question")) or dict(kind=a.get("kind", "confirm"), ref=str(a.get("ref")))
        ref, ans = q["ref"], a.get("answer")
        h = self.res["holes"][ref]
        if q["kind"] == "confirm":
            self.taps += 1
            if ans in ("yes", True):
                self.fixed[ref] = (h["t_idx"], h["g_idx"])
            else:
                self.exclude.setdefault(ref, set()).add(R2.reject(self.ctx, h["t_idx"], h["g_idx"]))
                self.rejected.add(ref)
        else:
            self.taps += 2
            gk = self._snap_or_add("green", ans["green_ll"], SNAP_GREEN) if ans.get("green_ll") else h["g_idx"]
            tk = self._snap_or_add("tee", ans["tee_ll"], SNAP_TEE) if ans.get("tee_ll") else h["t_idx"]
            self.fixed[ref] = (tk, gk)
        self.history.append(dict(question=q.get("id"), kind=q["kind"], ref=ref,
                                 answer=ans if isinstance(ans, str) else "tapped"))
        return self.solve() if resolve else self.res

    # ------------------------------------------------------------------ app contract
    def payload(self, course=None, k=3):
        """golf_confirm/1 (CONFIRM_UX.md): the current routing, its confidence, and the next questions."""
        hs = self.res.get("holes", {})
        holes = []
        for r in sorted(hs, key=int):
            h = hs[r]
            line = [h.get("back_tee_ll") or h.get("tee_ll"), h.get("green_ll")]
            holes.append(dict(ref=int(r), par=h.get("par"), card_yards=h.get("card_yards"),
                              tee=dict(ll=h.get("tee_ll"), id=h.get("tee_id"), src=h.get("tee_src")) if h.get("tee_ll") else None,
                              green=dict(ll=h.get("green_ll"), id=h.get("green_id"), src=h.get("green_src")) if h.get("green_ll") else None,
                              line=line if all(line) else None, straight_yd=h.get("straight_yd"),
                              p_hole=h.get("p_hole"), confirmed=r in self.fixed,
                              status="confirmed" if r in self.fixed else h.get("status"), flags=h.get("flags", [])))
        qs = [] if self.done() else self.questions(k)
        for q in qs:
            q.pop("risk_per_tap", None)
        return dict(schema="golf_confirm/1", course=course or {}, method=self.res.get("method"),
                    n_holes=self.res.get("n_holes"), card=bool(self.card), holes=holes,
                    summary=dict(confirmed=len(self.fixed), to_check=sum(1 for x in holes if x["status"] == "check"),
                                 taps_so_far=self.taps, done=self.done(), p_stop=self.p_stop,
                                 expected_correct_holes=round(sum(x["p_hole"] or 0 for x in holes), 1)),
                    questions=qs, history=self.history,
                    candidates=dict(greens=[dict(id=g["id"], ll=list(g["ll"]), src=g["src"]) for g in self.ctx["G"]],
                                    tees=[dict(id=t["id"], ll=list(t["ll"]), src=t["src"]) for t in self.ctx["T"]]),
                    answer_format={"question": "<questions[].id>",
                                   "answer": "'yes' | 'no' (confirm) or {'tee_ll': [lon, lat], 'green_ll': [lon, lat]} (locate)"})


def main():
    """python course_data/platform/confirm.py <generalize course dir> [--hide-holes] [--out payload.json]
    -> golf_confirm/1 for that course's cached inputs (an example for the app prototype)."""
    import argparse
    import json
    ap = argparse.ArgumentParser()
    ap.add_argument("course_dir")
    ap.add_argument("--hide-holes", action="store_true", help="drop OSM golf=hole ways / refs (as for an unmapped course)")
    ap.add_argument("--out")
    a = ap.parse_args()
    rd = lambda p: json.load(open(os.path.join(a.course_dir, p))) if os.path.exists(os.path.join(a.course_dir, p)) else None  # noqa: E731
    fc, course = rd("osm_golf.geojson"), rd("course.json") or {}
    sc = rd("scorecard.json") or {}
    card = next((c["card"] for c in sc.get("cards", []) if c["source"] == sc.get("chosen")), None)
    pads = [dict(id=p["id"], centroid=p["centroid"], coords=[tuple(c) for c in p["coords"]]) for p in (rd("pads.json") or [])]
    inp = R.inputs_from_fc(fc, segment=rd("segment.geojson"), pads=pads, boundary=course.get("boundary"),
                           hide_holes=a.hide_holes)
    fch = dict(fc, features=[f for f in fc["features"] if not (a.hide_holes and f["properties"].get("golf") == "hole")])
    s = Session(inp, card, fc=fch, boundary=course.get("boundary"))
    pl = s.payload(course=dict(name=course.get("name"), osm=course.get("osm"), state=course.get("state")))
    out = json.dumps(pl, indent=1, default=str)
    if a.out:
        open(a.out, "w").write(out)
    else:
        print(out[:4000])


if __name__ == "__main__":
    main()
