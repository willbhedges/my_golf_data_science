"""Gate 0 for a learned hole field (part affinity field, as OpenPose associates joints): can a small network, given
only the layout of a course's greens / tees / fairways / bunkers / water, predict a direction field along each hole
(unit vector tee -> green within FIELD_M of the hole line) well enough to pair every green with its own tee?

Data: the bench courses' OSM (benchdata/big/courses/<slug>/osm_golf.geojson.gz), rasterised at RES m / pixel on a
SIZE x SIZE canvas. Split by course (crc32 % 5 == 0 is the test fold). No imagery: this is the OSM-given setting, where
the scene router still pairs 5.9 % of holes with another hole's tee or a non-hole green (NOTES_ROUTING.md 2026-11-27).

Evaluation on the test fold, candidates = the first point of every mapped hole line (tees) x every hole green:
  score(t, g) = mean over the straight segment t -> g of field . unit(t -> g)   (the PAF line integral)
  top1     a green's best tee is its own
  assign   Hungarian over the score matrix: holes paired right
  baseline the same two numbers for a hand score (length plausibility + fairway share along the segment)
Usage: python3 holefield_gate0.py OUT_DIR [epochs]     (numpy / scipy for data + evaluation; torch for training)
       python3 holefield_gate0.py --selftest           (no torch: the truth field must pair ~every hole)
"""
import gzip
import json
import math
import os
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FP = os.path.dirname(HERE)
BD = os.path.join(FP, "benchdata", "big", "courses")
RES, SIZE, FIELD_M = 5.0, 384, 22.0
KINDS = ["green", "tee", "fairway", "bunker", "water"]


def _rings(g):
    if g["type"] == "Polygon":
        return [g["coordinates"][0]]
    if g["type"] == "MultiPolygon":
        return [p[0] for p in g["coordinates"]]
    return []


def load(slug):
    """-> dict(x [5, S, S] float32, field [2, S, S], mask [S, S], holes [(ref, tee_px, green_px, line_px)]) or None"""
    from skimage.draw import polygon as fill
    p = os.path.join(BD, slug, "osm_golf.geojson.gz")
    if not os.path.exists(p):
        return None
    fc = json.load(gzip.open(p, "rt"))
    holes = []
    for f in fc["features"]:
        pr = f.get("properties") or {}
        if pr.get("golf") == "hole" and f["geometry"]["type"] == "LineString" and str(pr.get("ref") or "").isdigit() \
                and 1 <= int(pr["ref"]) <= 18 and len(f["geometry"]["coordinates"]) >= 2:
            holes.append((int(pr["ref"]), np.asarray(f["geometry"]["coordinates"], float)[:, :2]))
    seen, hs = set(), []
    for r, co in sorted(holes, key=lambda h: h[0]):
        if r not in seen:
            seen.add(r)
            hs.append((r, co))
    if len(hs) < 9:
        return None
    allp = np.concatenate([co for _, co in hs])
    lon0, lat0 = allp.mean(0)
    kx, ky = math.cos(math.radians(lat0)) * 111320.0, 111320.0

    def px(ll):
        ll = np.asarray(ll, float).reshape(-1, 2)
        return np.c_[(ll[:, 0] - lon0) * kx / RES + SIZE / 2, SIZE / 2 - (ll[:, 1] - lat0) * ky / RES]
    x = np.zeros((len(KINDS), SIZE, SIZE), np.float32)
    tees = []
    for f in fc["features"]:
        pr = f.get("properties") or {}
        k = pr.get("golf") if pr.get("golf") in KINDS else ("water" if pr.get("natural") == "water" else None)
        if k is None:
            continue
        g = f["geometry"]
        if g["type"] == "Point" and k in ("tee", "green"):
            q = px(g["coordinates"][:2])[0]
            rr, cc = np.ogrid[:SIZE, :SIZE]
            x[KINDS.index(k)][(rr - q[1]) ** 2 + (cc - q[0]) ** 2 <= 2.0] = 1
        for ring in _rings(g):
            q = px(np.asarray(ring, float)[:, :2])
            if k == "tee":
                tees.append(q.mean(0))
            rr, cc = fill(q[:, 1], q[:, 0], (SIZE, SIZE))
            x[KINDS.index(k)][rr, cc] = 1
            if len(rr) == 0:                                   # smaller than a pixel
                c = np.clip(q.mean(0).round().astype(int), 0, SIZE - 1)
                x[KINDS.index(k)][c[1], c[0]] = 1
    field = np.zeros((2, SIZE, SIZE), np.float32)
    best = np.full((SIZE, SIZE), 1e9, np.float32)
    yy, xx = np.mgrid[:SIZE, :SIZE].astype(np.float32)
    out = []
    for r, co in hs:
        q = px(co)
        if q.min() < 2 or q.max() > SIZE - 3:
            return None                                        # the course does not fit the canvas
        for a, b in zip(q[:-1], q[1:]):
            v = b - a
            L = float(np.hypot(*v))
            if L < 1e-6:
                continue
            u = v / L
            t = np.clip(((xx - a[0]) * u[0] + (yy - a[1]) * u[1]), 0, L)
            d = np.hypot(xx - (a[0] + t * u[0]), yy - (a[1] + t * u[1]))
            m = (d <= FIELD_M / RES) & (d < best)
            field[0][m], field[1][m] = u[0], u[1]
            best[m] = d[m]
        out.append((r, q[0], q[-1], q))
    return dict(slug=slug, x=x, field=field, mask=(best < 1e8).astype(np.float32), holes=out,
                tees=[t for t in tees if 0 <= t[0] < SIZE and 0 <= t[1] < SIZE])


def _along(field, pts):
    """mean alignment of the field with a polyline (pixel points), sampled every ~2 pixels"""
    tot = w = 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        v = b - a
        L = float(np.hypot(*v))
        if L < 1e-6:
            continue
        u = v / L
        k = max(2, int(L / 2))
        q = a[None] + np.linspace(0.0, 1.0, k)[:, None] * v[None]
        c = np.clip(q[:, 0].round().astype(int), 0, SIZE - 1)
        r = np.clip(q[:, 1].round().astype(int), 0, SIZE - 1)
        tot += float(np.sum(field[0][r, c] * u[0] + field[1][r, c] * u[1])) * L / k
        w += L
    return tot / max(w, 1e-6)


BENDS = [(f, o) for f in (0.35, 0.5, 0.65) for o in (-90, -70, -50, -35, -20, 20, 35, 50, 70, 90)]    # dog-leg: m off the chord


def line_score(field, t, g):
    """the PAF line integral of tee -> green: the straight segment, or the best single bend (a dog-leg), the bend
    paying a little for its extra length"""
    v = g - t
    L = float(np.hypot(*v))
    if L < 1e-6:
        return -1.0
    u, nrm = v / L, np.array([-v[1], v[0]]) / L
    t0, g0 = t + 0.06 * v, g - 0.06 * v
    best = _along(field, [t0, g0])
    if L * RES > 230:                                          # only a hole long enough to bend
        for f, o in BENDS:
            m = t + f * v + nrm * (o / RES)
            best = max(best, _along(field, [t0, m, g0]) - 0.0012 * abs(o))
    return best


def hand_score(x, t, g, n=24):
    """no learning: a playable length and fairway (or tee / green) under the segment"""
    L = float(np.hypot(*(g - t))) * RES / 0.9144
    if not 70 <= L <= 680:
        return -1.0
    s = np.linspace(0.05, 0.95, n)[:, None]
    q = t[None] + s * (g - t)[None]
    c = np.clip(q[:, 0].round().astype(int), 0, SIZE - 1)
    r = np.clip(q[:, 1].round().astype(int), 0, SIZE - 1)
    turf = np.maximum(x[2][r, c], np.maximum(x[0][r, c], x[1][r, c]))
    other_green = x[0][r, c][: n * 3 // 4].mean()             # a green in the way before the last quarter
    return float(turf.mean() - 0.5 * other_green - 0.0006 * abs(L - 380) + (0.25 if L < 250 else 0.0) * (1 - turf.mean()))


def _pt_line(p, q, frac=0.6):
    """pixels from p to the first `frac` of polyline q"""
    seg = np.hypot(*np.diff(q, axis=0).T)
    lim, acc, best = frac * seg.sum(), 0.0, 1e9
    for a, b, L in zip(q[:-1], q[1:], seg):
        if L < 1e-6:
            continue
        e = min(1.0, max(0.0, (lim - acc) / L))
        t = min(e, max(0.0, float(np.dot(p - a, b - a)) / (L * L)))
        best = min(best, float(np.hypot(*(p - (a + t * (b - a))))))
        acc += L
        if acc >= lim:
            break
    return best


def evaluate(courses, fields, hand=False):
    """top1: over every tee candidate (each mapped tee polygon and each hole start; its owner is the hole whose line
    starts within 60 m, nearest) a green's best tee belongs to its own hole. assign: Hungarian, hole starts x greens."""
    from scipy.optimize import linear_sum_assignment
    n = top = asg = 0
    per = []
    for c, F in zip(courses, fields):
        rng = np.random.default_rng(zlib.crc32(c["slug"].encode()))
        G = [h[2] for h in c["holes"]]
        st = np.array([h[1] for h in c["holes"]])
        f = (lambda t, g: hand_score(c["x"], t, g)) if hand else (lambda t, g: line_score(F, t, g))
        cand = list(st) + list(c["tees"])
        own = []
        for t in cand:                                         # nearest hole line (its first 60 %), within 40 m
            d = [_pt_line(t, h[3]) for h in c["holes"]]
            own.append(int(np.argmin(d)) if min(d) * RES <= 40 else -1)
        own = np.array(own)
        S = np.array([[f(t, g) for t in cand] for g in G])
        S = S + rng.uniform(0, 1e-6, S.shape)                  # ties broken at random, not by index
        t1 = int((own[S.argmax(1)] == np.arange(len(G))).sum())
        perm = rng.permutation(len(G))
        ri, ci = linear_sum_assignment(-S[:, :len(G)][:, perm])
        a = int((perm[ci[np.argsort(ri)]] == np.arange(len(G))).sum())
        n += len(G)
        top += t1
        asg += a
        per.append((c["slug"], len(G), t1, a))
    return dict(holes=n, top1=round(top / max(n, 1), 4), assign=round(asg / max(n, 1), 4),
                courses_all_right=round(float(np.mean([p[3] == p[1] for p in per])), 4)), per


def is_test(slug):
    return zlib.crc32(slug.encode()) % 5 == 0


def train(tr, te, epochs, out):
    import torch
    import torch.nn as nn
    import torch.nn.functional as Fn
    torch.manual_seed(0)
    torch.set_num_threads(os.cpu_count() or 4)

    def block(i, o):
        return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(inplace=True),
                             nn.Conv2d(o, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(inplace=True))

    class Net(nn.Module):                                      # 5 levels: the field needs a whole hole in view
        def __init__(self, cin=len(KINDS), b=24):
            super().__init__()
            w = [b, 2 * b, 4 * b, 8 * b, 8 * b]
            self.down = nn.ModuleList([block(cin if i == 0 else w[i - 1], w[i]) for i in range(5)])
            self.up = nn.ModuleList([block(w[i] + w[i - 1], w[i - 1]) for i in range(4, 0, -1)])
            self.head = nn.Conv2d(b, 3, 1)                     # dx, dy, on-a-hole logit

        def forward(self, x):
            sk = []
            for i, d in enumerate(self.down):
                x = d(x if i == 0 else Fn.max_pool2d(x, 2))
                sk.append(x)
            for u, s in zip(self.up, sk[-2::-1]):
                x = u(torch.cat([Fn.interpolate(x, size=s.shape[-2:], mode="bilinear", align_corners=False), s], 1))
            return self.head(x)
    net = Net()
    opt = torch.optim.AdamW(net.parameters(), 2e-3, weight_decay=1e-4)
    steps = epochs * math.ceil(len(tr) / 8)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, 2e-3, total_steps=steps)
    X = np.stack([c["x"] for c in tr])
    Y = np.stack([np.concatenate([c["field"], c["mask"][None]]) for c in tr])
    rng = np.random.default_rng(0)

    def aug(x, y):
        k = int(rng.integers(4))
        if k:                                                  # rot90 k times: (dx, dy) -> (dy, -dx) each time (row axis down)
            x, y = np.rot90(x, k, (1, 2)).copy(), np.rot90(y, k, (1, 2)).copy()
            for _ in range(k):
                y[0], y[1] = y[1].copy(), -y[0].copy()
        if rng.random() < 0.5:                                 # mirror left-right
            x, y = x[:, :, ::-1].copy(), y[:, :, ::-1].copy()
            y[0] = -y[0]
        return x, y

    def predict(cs):
        net.eval()
        out_ = []
        with torch.no_grad():
            for c in cs:
                o = net(torch.from_numpy(c["x"][None]))[0].numpy()
                out_.append(o[:2] * (1 / (1 + np.exp(-o[2])))[None])
        net.train()
        return out_
    log = []
    for ep in range(epochs):
        order = rng.permutation(len(tr))
        run = 0.0
        for i in range(0, len(order), 8):
            b = [aug(X[j], Y[j]) for j in order[i:i + 8]]
            xb = torch.from_numpy(np.stack([q[0] for q in b]))
            yb = torch.from_numpy(np.stack([q[1] for q in b]))
            o = net(xb)
            m = yb[:, 2:3]
            loss = (((o[:, :2] - yb[:, :2]) ** 2) * (0.15 + m)).mean() + Fn.binary_cross_entropy_with_logits(o[:, 2:3], m)
            opt.zero_grad()
            loss.backward()
            opt.step()
            sched.step()
            run += loss.item() * len(b)
        row = dict(epoch=ep + 1, loss=round(run / len(tr), 5))
        if (ep + 1) % 5 == 0 or ep + 1 == epochs:
            row.update(test=evaluate(te, predict(te))[0])
        log.append(row)
        print(json.dumps(row), flush=True)
    torch.save(net.state_dict(), os.path.join(out, "holefield_gate0.pt"))
    return predict(te), log


def main():
    slugs = sorted(os.listdir(BD))
    if sys.argv[1] == "--selftest":
        cs = [c for c in (load(s) for s in slugs[:40]) if c]
        print("courses", len(cs), "truth field", evaluate(cs, [c["field"] for c in cs])[0],
              "zero field", evaluate(cs, [np.zeros_like(c["field"]) for c in cs])[0], "hand", evaluate(cs, cs, hand=True)[0])
        y = np.concatenate([cs[0]["field"], cs[0]["mask"][None]])
        print("mask share", round(float(cs[0]["mask"].mean()), 3), "x share", cs[0]["x"].mean((1, 2)).round(4).tolist(), y.shape)
        return
    out = sys.argv[1]
    epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    os.makedirs(out, exist_ok=True)
    cs = [c for c in (load(s) for s in slugs) if c]
    tr, te = [c for c in cs if not is_test(c["slug"])], [c for c in cs if is_test(c["slug"])]
    print("courses", len(cs), "of", len(slugs), "train", len(tr), "test", len(te), flush=True)
    res = dict(n_train=len(tr), n_test=len(te), hand=evaluate(te, te, hand=True)[0],
               truth_field=evaluate(te, [c["field"] for c in te])[0])
    print(json.dumps(res), flush=True)
    F, log = train(tr, te, epochs, out)
    ev, per = evaluate(te, F)
    res.update(learned=ev, log=log, per_course=per)
    json.dump(res, open(os.path.join(out, "holefield_gate0.json"), "w"), indent=1)
    print("RESULT", json.dumps({k: res[k] for k in ("n_train", "n_test", "hand", "truth_field", "learned")}))


if __name__ == "__main__":
    main()
