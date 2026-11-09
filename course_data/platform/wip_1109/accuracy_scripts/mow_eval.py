"""Mowing line, leave-one-course-out: edge error vs the hand-truth native + variant packages for the error budget.
python3 mow_eval.py MOWDIR MODELS.pkl AN_V1 AN_V2 OUT_PREFIX [json params]
Sides / thresholds / gate exactly as apply_native.py (LOCO p from mapper/eval_native_auto.json)."""
import json, os, sys, pickle, warnings
warnings.filterwarnings("ignore")
import numpy as np
WT = "/home/user/my_golf_data_science"; CD = os.path.join(WT, "course_data")
for p in ("mapper", "product", "platform"):
    sys.path.insert(0, os.path.join(CD, p))
import importlib.util
import common as M, native_auto as NA, native_confirm as NC, error_budget as E, mowing_line as ML
D, MP, A1, A2, OUT = sys.argv[1:6]
PAR = json.loads(sys.argv[6]) if len(sys.argv) > 6 else {}
WRITE = not PAR.pop("nowrite", False)
VETO = PAR.pop("veto", None)
SCORE = PAR.pop("score", "pix")
PMIN = PAR.pop("pmin", None)
MIX = PAR.pop("mix", 0.0)
import mow_self as MS
spec = importlib.util.spec_from_file_location("bud_platform_package", os.path.join(CD, "platform", "package.py"))
PP = importlib.util.module_from_spec(spec); sys.modules["bud_platform_package"] = PP; spec.loader.exec_module(PP)
EV = json.load(open(os.path.join(CD, "mapper", "eval_native_auto.json")))["courses"]
MODELS = pickle.load(open(MP, "rb"))["models"]
cfgs = {c["slug"]: (c, "v1") for c in E.SETS["v1"]()}; cfgs.update({c["slug"]: (c, "v2") for c in E.SETS["v2"]()})
TRACED = ("gateway_national", "coldwater", "spirit_hollow", "sand_creek_station")
tot = {}
for slug, e in EV.items():
    if not e["fires"] or slug not in cfgs: continue
    cfg, sv = cfgs[slug]
    pkg = M.rj(os.path.join(A1 if sv == "v1" else A2, slug, "package.json"))
    # strip the 10-yd band the an_ package carries
    for h in pkg["holes"].values():
        h["zones_ll"] = [z for z in h.get("zones_ll") or [] if z.get("src") != NA.SRC]
    S = cfg["tees"]
    frames = M.make_frames(pkg, M.tee_set_of(pkg, S) if any(k.lower() == S.lower() for k in pkg.get("tee_sets") or {}) else M.tee_set_of(pkg))
    sides = NA.sides_from_p(e["p"], e["thr"])
    G = pickle.load(open(os.path.join(D, slug + ".pkl"), "rb"))["holes"]
    model = MODELS[slug] if slug in MODELS else MODELS["_all"]
    model = getattr(model, "booster_", model)
    CS = MS.course_score(G, sides, params=PAR, mix=MIX)[0] if SCORE == "course" else None
    lines = {}; st = dict(err_new=[], err_old=[], iou_new=[0, 0], iou_old=[0, 0], fp_new=0, fp_old=0, fn_new=0, fn_old=0, e=[], none=0, nst=0, dropped=[])
    for ref, ss in sides.items():
        if not ss or ref not in G or ref not in frames: continue
        g = G[ref]; f, m = ML.features(g); p = ML.unmown_p(g, model, f, m)
        sh = g["shape"]; X = np.tile(ML.XS, (sh[0], 1)); A = np.repeat(ML.AS, sh[1]).reshape(sh); d = m["d"]
        lines[ref] = {}
        for s in ss:
            if SCORE == "self":
                p = MS.side_score(g, f, m, s, params=PAR)
            if SCORE == "course":
                p = CS[ref][s][0]
            ln = ML.detect(g, p, s, m, PAR); mk = ML.band_mask(g, ln, s)
            if PMIN is not None:
                from scipy import ndimage
                ps = ndimage.uniform_filter(np.nan_to_num(p, nan=1.0), 7)
                mk &= ps >= PMIN
            ev = [v for v in ln["e"] if v is not None]
            if VETO is not None and len(ev) < VETO * len(ln["e"]):
                st["dropped"].append(f"{ref}{s}"); mk[:] = False
            ln["_mask"] = mk; lines[ref][s] = ln
            st["e"] += ev; st["none"] += len(ln["e"]) - len(ev); st["nst"] += len(ln["e"])
            if "foot" not in g: continue
            sm = ((X < 0) if s == "L" else (X > 0)) & g["foot"].reshape(sh) & (d > 0) & m["open"] & (A >= 150) & (A <= 345)
            tn = g["t_native"].reshape(sh) & sm
            old = sm & (d >= 10)
            new = mk & sm
            for nm, b in (("new", new), ("old", old)):
                st["iou_" + nm][0] += (b & tn).sum(); st["iou_" + nm][1] += (b | tn).sum()
                st["fp_" + nm] += (b & ~tn).sum(); st["fn_" + nm] += (~b & tn).sum()
            # edge error per 5-yd station: truth inner edge (5th pct of d over truth native) vs the line / 10
            for j, a0 in enumerate(np.arange(150, 345, 5)):
                q = tn & (A >= a0) & (A < a0 + 5)
                if q.sum() < 10: continue
                dt = np.percentile(d[q], 5)
                jj = int((a0 + 2.5 - ML.AS[0]) // ML.STEP_A)
                en = ln["e"][jj] if not st["dropped"] or st["dropped"][-1] != f"{ref}{s}" else None
                st["err_new"].append((en if en is not None else 50.0) - dt); st["err_old"].append(10.0 - dt)
    en, eo = np.array(st["err_new"]), np.array(st["err_old"])
    tot[slug] = st
    print(f"{slug:20s} sides {sum(len(v) for v in lines.values()):2d} line med e {np.median(st['e']) if st['e'] else float('nan'):5.1f} none {st['none']}/{st['nst']} dropped {','.join(st['dropped']) or '-'} | "
          f"edge |err| med old {np.median(np.abs(eo)):5.1f} new {np.median(np.abs(en)):5.1f}  >8yd old {np.mean(np.abs(eo) > 8):.2f} new {np.mean(np.abs(en) > 8):.2f} | "
          f"IoU old {st['iou_old'][0] / max(st['iou_old'][1], 1):.2f} new {st['iou_new'][0] / max(st['iou_new'][1], 1):.2f} | FP cells old {st['fp_old']} new {st['fp_new']} FN old {st['fn_old']} new {st['fn_new']}", flush=True)
    if WRITE:
        out = PP.reframe(ML.apply_lines(pkg, frames, sides, lines, e["p"]))
        dst = os.path.join(f"{OUT}_{sv}", slug); os.makedirs(dst, exist_ok=True)
        json.dump(out, open(os.path.join(dst, "package.json"), "w"))
for nm, grp in (("traced", TRACED), ("all", tuple(tot))):
    en = np.concatenate([np.array(tot[s]["err_new"]) for s in grp if s in tot]); eo = np.concatenate([np.array(tot[s]["err_old"]) for s in grp if s in tot])
    io = [sum(tot[s]["iou_old"][i] for s in grp if s in tot) for i in (0, 1)]; inn = [sum(tot[s]["iou_new"][i] for s in grp if s in tot) for i in (0, 1)]
    print(f"== {nm}: stations {len(en)} |err| med old {np.median(np.abs(eo)):.1f} new {np.median(np.abs(en)):.1f}; >8 yds old {np.mean(np.abs(eo) > 8):.3f} new {np.mean(np.abs(en) > 8):.3f}; mean signed old {eo.mean():+.1f} new {np.clip(en, -50, 50).mean():+.1f}; IoU old {io[0] / io[1]:.3f} new {inn[0] / inn[1]:.3f}")
