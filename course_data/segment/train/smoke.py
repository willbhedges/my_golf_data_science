"""Smoke test of train.py + model.load(<dir>) + predict_raster on synthetic data (Actions, ~2 min CPU).

    python course_data/segment/train/smoke.py
"""
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.dirname(HERE)]


def main():
    rng = np.random.default_rng(0)
    with tempfile.TemporaryDirectory() as td:
        data, out = os.path.join(td, "data"), os.path.join(td, "model")
        os.makedirs(data)
        for i in range(4):
            img = rng.integers(0, 255, (4, 450, 500), dtype=np.uint8)
            lab = rng.integers(0, 6, (450, 500)).astype(np.uint8)
            lab[:20] = 255
            np.savez_compressed(os.path.join(data, f"c{i}.npz"), img=img, lab=lab)
        subprocess.run([sys.executable, os.path.join(HERE, "train.py"), "--data", data, "--out", out,
                        "--minutes", "0.4", "--size", "128", "--bs", "2", "--encoder", "resnet18"], check=True)
        import model as M
        mdl, cfg, sha = M.load(out)
        p = M.predict_raster(mdl, rng.integers(0, 255, (4, 600, 700), dtype=np.uint8), tta=False,
                             mean=cfg["image_mean"], std=cfg["image_std"], log=None)
        assert p.shape == (6, 600, 700) and np.allclose(p.sum(0), 1, atol=1e-3), p.shape
        print("smoke ok", sha[:8], cfg["image_mean"])


if __name__ == "__main__":
    main()
