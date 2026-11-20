"""Smoke test of train_v2.py on synthetic v2-format data (JPEG GeoTIFF image + lab npz), fine-tuned from the v1
model dir, one job then a resumed one (Actions, ~3 min CPU). Extra arguments go to train_v2.py (v3: e.g. --init
<v2 dir> --tee-focus ... --select green,tee); one synthetic course then also gets a chm_add.py tree mask.

    python course_data/segment/train/smoke_v2.py [train_v2.py args]
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "models", "golfseg_own")


def main():
    import rasterio
    from rasterio.transform import from_origin
    rng = np.random.default_rng(0)
    with tempfile.TemporaryDirectory() as td:
        data, out, ck = os.path.join(td, "data", "shard0"), os.path.join(td, "model"), os.path.join(td, "ck", "sub", "ck.pt")
        os.makedirs(data)
        idx = {"courses": {}}
        for i in range(6):
            H, W = 700, 800
            img = rng.integers(0, 255, (4, H, W), dtype=np.uint8)
            lab = rng.integers(0, 6, (H, W)).astype(np.uint8)
            lab[:20] = 255
            name = f"way_{i}"
            with rasterio.open(os.path.join(data, name + ".tif"), "w", driver="GTiff", width=W, height=H, count=4,
                               dtype="uint8", crs="EPSG:32615", transform=from_origin(0, 0, 0.6, 0.6), tiled=True,
                               compress="jpeg") as dst:
                dst.write(img)
            np.savez_compressed(os.path.join(data, name + ".npz"), lab=lab)
            if i == 0 and len(sys.argv) > 1:
                tree = rng.random((H, W)) < 0.6
                np.savez_compressed(os.path.join(data, name + "_chm.npz"), tree=np.packbits(tree.ravel()),
                                    shape=np.array([H, W]), valid=np.float32(1.0))
            idx["courses"][f"way/{i}"] = dict(file=name + ".npz", image=name + ".tif", state="IA", inside=int((lab != 255).sum()),
                                              pixels={c: int((lab == k).sum()) for k, c in
                                                      enumerate(["green", "tee", "fairway", "bunker", "water"], 1)})
        json.dump(idx, open(os.path.join(data, "index.json"), "w"))
        base = [sys.executable, os.path.join(HERE, "train_v2.py"), "--data", os.path.dirname(data), "--out", out,
                "--init", V1, "--ckpt", ck, "--size", "128", "--bs", "2", "--pool", "3", "--swap-s", "1",
                "--eval-every", "4", "--max-val", "3", "--total-minutes", "1.0", "--val-share", "0.4"] + sys.argv[1:]
        subprocess.run(base + ["--minutes", "0.3"], check=True)
        subprocess.run(base + ["--minutes", "0.5", "--resume"], check=True)
        log = json.load(open(os.path.join(out, "train_log.json")))
        assert len(log["state"]["jobs"]) == 2 and log["state"]["step"] > 0, log["state"]["jobs"]
        pre = json.load(open(os.path.join(out, "preprocessor_config.json")))
        assert pre["image_mean"] == json.load(open(os.path.join(V1, "preprocessor_config.json")))["image_mean"]
        if "--tee-focus" in sys.argv:
            assert log["pool_stats"] and log["pool_stats"]["chm"] >= 0, log.get("pool_stats")
            print("tee focus pool stats", log["pool_stats"])
        print("smoke v2 ok: steps", log["state"]["step"], "of", log["state"]["total"], "exported", log["exported_step"])


if __name__ == "__main__":
    main()
