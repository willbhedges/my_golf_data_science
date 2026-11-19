"""Which segment U-Net the fast path runs, and the routing models fitted on its scenes.

    FASTSCENE_UNET_MODEL = v1 | v2     (default DEFAULT below)
      v1: course_data/segment/models/golfseg_own     (IA / MO training set)
      v2: course_data/segment/models/golfseg_own_v2  (national fine-tune of v1)
    FASTSCENE_UNET=<file.safetensors> still overrides the weights file (fastscene.unet_weights).

The routing models (route_learn / route_rerank / route_tee / the per-hole gate) read per-pixel U-Net maps, so each
U-Net has its own fit: the files in this folder are the v1 fits; another model's live in route_models/<name>/ and
are used when that model is selected (a file missing there falls back to this folder's). Each module's env override
(ROUTE_LEARN_MODEL, ROUTE_RERANK_MODEL, ROUTE_TEE_MODEL, ROUTE_GATE_PARAMS) wins over both.
"""
from __future__ import annotations

import os

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
DEFAULT = "v2"            # national fine-tune (NOTES_PERCEPTION.md 2026-11-19); FASTSCENE_UNET_MODEL=v1 rolls back
UNETS = {"v1": os.path.join(CD, "segment", "models", "golfseg_own", "model.safetensors"),
         "v2": os.path.join(CD, "segment", "models", "golfseg_own_v2", "model.safetensors")}


def unet_model():
    m = os.environ.get("FASTSCENE_UNET_MODEL", DEFAULT)
    if m not in UNETS:
        raise ValueError(f"FASTSCENE_UNET_MODEL={m!r}: one of {sorted(UNETS)}")
    return m


def unet_file():
    return UNETS[unet_model()]


def routing_file(name, env=None):
    """the routing model file `name` (e.g. route_learn_model.pkl) for the selected U-Net"""
    if env and os.environ.get(env):
        return os.environ[env]
    m = unet_model()
    if m != "v1":
        p = os.path.join(HERE, "route_models", m, name)
        if os.path.exists(p):
            return p
    return os.path.join(HERE, name)
