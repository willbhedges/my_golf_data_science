"""The tee-shot landing pattern a library page draws (the dashed yellow oval), measured in the tee-line frame.

spirit_hollow/v2/build_page_v2.cloud (read-only) summarises the simulated finishes by the eigenvectors of their
covariance and half of the 2.5-97.5 percentile range along each eigen axis, centred on the median. On the v2
engine that turns the model's horizontal oval into a near circle (library audit 2026-11-03, memorial_park and
tournament_club_iowa driver picks: drawn depth / width 0.92-1.04, the model's own finish 95 % extents 0.78-0.96):

  * the depth spread is one-sided: slight mishits (12 %, 92-95 % carry), heavy mishits (2.5 %, 65-85 %) and
    balls that stop in rough or trees all finish SHORT, so the 2.5 % point is ~33-43 yds short of the median and
    the 97.5 % point only ~19-28 long. A symmetric half-range draws the long side 8-15 yds too deep.
  * that short tail inflates the depth variance until it nearly equals the lateral one, so the eigen axes turn
    arbitrarily (21-81 degrees off the tee line on those holes) and the drawn "major axis" mixes depth and width.

This module measures the same finishes without rotating: lateral 95 % extents left / right of the median, the
depth 95 % extents short / long of the median after taking out a linear tilt (yds deeper per yd right: the model's
push-slice-short correlation and any one-sided roll), so the drawn shape is the model's: wider than long, with its
short tail and tilt.

Heavy mishits (the v2 world's 2.5 % of swings at 65-85 % of carry: tops, big heel / toe strikes) are left out of
the pattern, as DECADE / launch-monitor patterns leave out the "off-the-planet" shots and as the app's pattern is
defined ("95 % of your good strikes"); the model still scores them. Kept in, the 2.5 % depth point sits exactly on
the edge of that 2.5 % cluster and jumps 15-20 yds with the random draws (memorial_park 1 Driver: 37 short at 6000
swings, 47 at 3000). Slight mishits (12 %, 92-95 % carry) stay in: they are most of the short side.

page_cloud(...) returns the build_page_v2.cloud fields (dA, dL, A, B, u, w, width; u / w = the tee line and its
right, so an unpatched template still draws an axis-aligned oval of the right overall size) plus the shape
(long, short, left, right, tilt) that course_page.PAGE_PATCHES draws.
"""
import numpy as np

TILT_MAX = 0.5          # |yds deeper per yd right| kept: a tilt steeper than ~27 degrees is a map artefact


def pattern(a, l):
    """95 % pattern of finishes (along, lateral yds in the tee frame): centre (median), tilt, extents."""
    a, l = np.asarray(a, float).ravel(), np.asarray(l, float).ravel()
    ca, cl = float(np.median(a)), float(np.median(l))
    dl = l - cl
    var = float(np.var(dl))
    k = float(np.cov(a, l)[0, 1] / var) if var > 1e-9 else 0.0
    k = float(np.clip(k, -TILT_MAX, TILT_MAX))
    r = a - ca - k * dl
    l0, l1 = np.percentile(dl, [2.5, 97.5])
    r0, r1 = np.percentile(r, [2.5, 97.5])
    return dict(along=ca, lat=cl, tilt=k, left=float(-l0), right=float(l1), short=float(-r0), long=float(r1))


def outline(p, n=48, scale=1.0):
    """[(along, lat)] around the pattern (the same shape the page draws): lateral by side, depth by side, tilt."""
    out = []
    for i in range(n):
        t = 2 * np.pi * i / n
        c, s = np.cos(t), np.sin(t)
        x = s * (p["right"] if s >= 0 else p["left"]) * scale
        y = c * (p["long"] if c >= 0 else p["short"]) * scale + p["tilt"] * x
        out.append((p["along"] + y, p["lat"] + x))
    return out


def good_swings(M, P, z):
    """Mask of the swings drawn (z = M.draws_z rows: z_lat, z_car, u_mishit, ...) that are not heavy mishits."""
    u = np.asarray(z[2])
    return ~((u >= P["mis_slight"]) & (u < P["mis_slight"] + P["mis_heavy"]))


def page_cloud(M, h, grid0, temp_f, n=6000, seed=17):
    """build_page_v2.cloud on the v2 engine M (same swings, same central world), measured in the tee frame."""
    hd = M.HOLES[h]
    P = M.central(temp_f=temp_f)
    R = M.Raster(hd)
    S = R.strokes(P, hd["length"])
    z = M.draws_z(n, seed)
    elev = hd.get("elev", {})
    out = {}
    for c, v in grid0["clubs"].items():
        _, (a, l, lie, s) = M.ev_curve(R, S, hd, c, P, z, np.array([v["aim"]]))
        keep = good_swings(M, P, z)
        p = pattern(a[keep, 0], l[keep, 0])
        dc, rf, kick = elev.get(c, (0.0, 1.0, 0.0))
        page_total = (v["carry"] + dc) + (v["total"] - v["carry"]) * rf
        out[c] = dict(dA=round(p["along"] - page_total, 1), dL=round(p["lat"] - (v["aim"] + kick), 1),
                      A=round((p["long"] + p["short"]) / 2, 1), B=round((p["left"] + p["right"]) / 2, 1),
                      u=[1.0, 0.0], w=[0.0, 1.0], width=v["width"],
                      long=round(p["long"], 1), short=round(p["short"], 1), left=round(p["left"], 1),
                      right=round(p["right"], 1), tilt=round(p["tilt"], 3))
    return out
