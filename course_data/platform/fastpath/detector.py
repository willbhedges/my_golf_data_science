"""Which segment U-Net the fast path runs, and the routing models fitted on its scenes.

    FASTSCENE_UNET_MODEL = v1 | v2 | v3     (default DEFAULT below)
      v1: course_data/segment/models/golfseg_own     (IA / MO training set)
      v2: course_data/segment/models/golfseg_own_v2  (national fine-tune of v1)
      v3: course_data/segment/models/golfseg_own_v3  (tee-targeted fine-tune of v2; routing fits route_models/v3/,
          a file missing there falls back to v2's, then this folder's)
    FASTSCENE_UNET=<file.safetensors> still overrides the weights file (fastscene.unet_weights).

The routing models (route_learn / route_rerank / route_tee / the per-hole gate) read per-pixel U-Net maps, so each
U-Net has its own fit: the files in this folder are the v1 fits; another model's live in route_models/<name>/ and
are used when that model is selected (a file missing there falls back to this folder's). Each module's env override
(ROUTE_LEARN_MODEL, ROUTE_RERANK_MODEL, ROUTE_TEE_MODEL, ROUTE_GATE_PARAMS) wins over both. v2 default: every scene
tee complex enters routing (cutoff 0, fits in route_models/v2/); ROUTE_TEE_ALL=0 rolls back to the cutoff 0.3 with
its fits in route_models/v2_p03/ (route_p_tee / tee_rollback below). v2 default also adds P(tee) peak complexes
(route_tee_peaks below); ROUTE_TEE_PEAKS=0 turns them off with the fits in route_models/v2_nopk/.
"""
from __future__ import annotations

import os

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
DEFAULT = "v2"            # national fine-tune (NOTES_PERCEPTION.md 2026-11-19); FASTSCENE_UNET_MODEL=v1 rolls back
UNETS = {"v1": os.path.join(CD, "segment", "models", "golfseg_own", "model.safetensors"),
         "v2": os.path.join(CD, "segment", "models", "golfseg_own_v2", "model.safetensors"),
         "v3": os.path.join(CD, "segment", "models", "golfseg_own_v3", "model.safetensors")}
FIT_FALLBACK = {"v3": ["v2"]}            # routing fits a U-Net without its own file reads (before this folder's)


def objects_dir(model_dir):
    """the second-stage object models (fastscene_model/objects_unet[_<model>], perc_objects.py) for the selected U-Net:
    its own folder, else the FIT_FALLBACK model's (logged once: v3 before its objects_unet_v3 refit runs on v2's), else
    model_dir/objects_unet (v1's) when the model is v1. None when nothing fits."""
    m = unet_model()
    base = os.path.join(model_dir, "objects_unet")
    if m == "v1":
        return base if os.path.isdir(base) else None
    for i, k in enumerate([m] + FIT_FALLBACK.get(m, [])):
        d = base + "_" + k
        if os.path.isdir(d):
            if i and m not in _WARNED:
                _WARNED.add(m)
                import sys
                print(f"detector: no objects_unet_{m}; using objects_unet_{k} (FASTSCENE_UNET_MODEL={m})", file=sys.stderr)
            return d
    raise FileNotFoundError(f"FASTSCENE_UNET_MODEL={m}: no second-stage object models ({base}_{m} or a fallback); "
                            "fit them with perc_objects.py or set FASTSCENE_OBJECTS2")


_WARNED = set()


# Scene tee complexes enter routing (route_scene.candidates) at p * (1 - p_range_tee) >= route_p_tee(); each U-Net's
# routing fits were made at its value. v2 default since 2026-11-19 (NOTES_ROUTING.md "tee cutoff 0 default"): every
# scene complex enters (cutoff 0.0, fits in route_models/v2/). ROUTE_TEE_ALL=0 rolls back to the cutoff 0.3 and its
# fits (route_models/v2_p03/). Env ROUTE_P_TEE overrides the cutoff alone (the fits must match it: ROUTE_*_MODEL).
ROUTE_P_TEE = {"v1": 0.3, "v2": 0.0, "v3": 0.0}
TEE_ROLLBACK = {"v2": ("v2_p03", 0.3)}        # U-Net -> (routing fits folder, cutoff) under ROUTE_TEE_ALL=0


def tee_rollback():
    """the (routing fits folder, cutoff) of the rollback ROUTE_TEE_ALL=0 for the selected U-Net, else None"""
    return TEE_ROLLBACK.get(unet_model()) if os.environ.get("ROUTE_TEE_ALL", "1") == "0" else None


# P(tee) peak complexes (route_learn.augment_scene / _peak_tees): threshold per U-Net, 0 = off. v2 default 0.1 since
# 2026-11-19 (NOTES_ROUTING.md "tee detection"), fits in route_models/v2/; ROUTE_TEE_PEAKS=0 turns them off and reads
# the fits made without them (route_models/v2_nopk/); ROUTE_TEE_ALL=0 (cutoff 0.3 rollback) turns them off too.
TEE_PEAKS = {"v1": 0.0, "v2": 0.1, "v3": 0.1}
NO_PEAKS_FITS = {"v2": "v2_nopk"}


def route_tee_peaks():
    if tee_rollback():
        return 0.0
    v = os.environ.get("ROUTE_TEE_PEAKS")
    if v not in (None, ""):
        return float(v)
    return TEE_PEAKS[unet_model()]


# DEM pad complexes (route_learn.augment_scene / _pad_tees; NOTES_ROUTING.md 2026-11-20 "DEM pads"): opt-in
# ROUTE_TEE_PADS=1 (v2 only); off with every rollback.
TEE_PADS = {"v1": False, "v2": False, "v3": False}
PADS_FITS = {"v2": "v2_pads"}            # the fits made with pads (route_learn / re-ranker / tee / gate + route_pad_model)


def route_tee_pads():
    """DEM pads on: only with their own fits (route_models/v2_pads), so off under every other rollback / variant"""
    if tee_rollback() or select_rollback() or route_tee_peaks() == 0:
        return False
    v = os.environ.get("ROUTE_TEE_PADS")
    if v not in (None, ""):
        return v == "1" and unet_model() == "v2"
    return TEE_PADS[unet_model()]


def route_p_tee():
    v = os.environ.get("ROUTE_P_TEE")
    if v:
        return float(v)
    rb = tee_rollback()
    return rb[1] if rb else ROUTE_P_TEE[unet_model()]


def unet_model():
    m = os.environ.get("FASTSCENE_UNET_MODEL", DEFAULT)
    if m not in UNETS:
        raise ValueError(f"FASTSCENE_UNET_MODEL={m!r}: one of {sorted(UNETS)}")
    return m


def unet_file():
    return UNETS[unet_model()]


# Routing selection (NOTES_ROUTING.md 2026-11-20 "routing selection" and "re-ranker features"): v2's re-ranker is a
# bagged lambdarank ranker over all alternative kinds with the extended features, the tee refinement a ranker /
# classifier hybrid with a card-residual penalty (route_models/v2/). Rollbacks of the re-ranker / tee / gate fits:
# ROUTE_SELECT=w1e (route_models/v2_w1e/: single ranker over start / end alternatives), ROUTE_SELECT=0
# (route_models/v2_pk/: regressor re-ranker, eps tie-break tee choice).
# ROUTE_SELECT=chosen (route_models/v2_chosen/): the fits made with the bench's old card (scorecard.json's chosen card),
# before the 2026-11-20 refit under the production card pick (NOTES_ROUTING.md "refit under the card pick").
# ROUTE_SELECT=hf (route_models/v2_hf/): the refit whose hole model also reads the learned hole field (holefield.py,
# NOTES_ROUTING.md 2026-11-27: +1.2 points out of fold); files it lacks (route_conf.json) come from route_models/v2/.
SELECT_ROLLBACK = {"v2": {"0": "v2_pk", "w1e": "v2_w1e", "chosen": "v2_chosen", "hf": "v2_hf"}}


def select_rollback():
    return SELECT_ROLLBACK.get(unet_model(), {}).get(os.environ.get("ROUTE_SELECT", "1"))


def routing_file(name, env=None):
    """the routing model file `name` (e.g. route_learn_model.pkl) for the selected U-Net"""
    if env and os.environ.get(env):
        return os.environ[env]
    m = unet_model()
    rb = tee_rollback()
    np_ = NO_PEAKS_FITS.get(m) if not rb and TEE_PEAKS.get(m) and route_tee_peaks() == 0 else None
    sr = select_rollback() if not rb and not np_ else None
    pd = PADS_FITS.get(m) if not rb and not np_ and not sr and route_tee_pads() else None
    for d in ([rb[0]] if rb else []) + ([np_] if np_ else []) + ([sr] if sr else []) + ([pd] if pd else []) + \
            ([m] if m != "v1" else []) + FIT_FALLBACK.get(m, []):
        p = os.path.join(HERE, "route_models", d, name)
        if os.path.exists(p):
            return p
    return os.path.join(HERE, name)
