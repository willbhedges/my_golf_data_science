"""Export a hole-field fit for the fast path (no torch there): batch norms folded into the convolutions, float16
weights in holefield_weights.npz, plus one reference input / output pair (holefield_ref.npz) the numpy forward pass
(holefield.forward) is checked against.
Usage: python3 holefield_export.py OUT_DIR [WEIGHTS.pt] [n_input_channels]   (default $PREV_DIR/holefield_fold9.pt, 7)"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import holefield_gate0 as G0  # noqa: E402


def main():
    import torch
    out = sys.argv[1]
    w = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.environ["PREV_DIR"], "holefield_fold9.pt")
    cin = int(sys.argv[3]) if len(sys.argv) > 3 else 7
    os.makedirs(out, exist_ok=True)
    G0.KINDS = ["c%d" % i for i in range(cin)]
    net = G0.build_net()
    sd = torch.load(w, map_location="cpu")
    net.load_state_dict(sd)
    net.eval()
    W = {}

    def fold(prefix, name):                                   # block = conv, bn, relu, conv, bn, relu
        for j, (ci, bi) in enumerate(((0, 1), (3, 4))):
            cw, cb = sd[f"{prefix}.{ci}.weight"].double(), sd[f"{prefix}.{ci}.bias"].double()
            g, b = sd[f"{prefix}.{bi}.weight"].double(), sd[f"{prefix}.{bi}.bias"].double()
            m, v = sd[f"{prefix}.{bi}.running_mean"].double(), sd[f"{prefix}.{bi}.running_var"].double()
            s = g / torch.sqrt(v + 1e-5)
            W[f"{name}_{j}_w"] = (cw * s[:, None, None, None]).numpy().astype(np.float32)
            W[f"{name}_{j}_b"] = ((cb - m) * s + b).numpy().astype(np.float32)
    for i in range(5):
        fold(f"down.{i}", f"d{i}")
    for i in range(4):
        fold(f"up.{i}", f"u{i}")
    W["head_w"] = sd["head.weight"].numpy().astype(np.float32)[:, :, 0, 0]
    W["head_b"] = sd["head.bias"].numpy().astype(np.float32)
    np.savez_compressed(os.path.join(out, "holefield_weights.npz"), **{k: v.astype(np.float16) for k, v in W.items()})
    # the reference pair comes from the full-precision fit: the float16 weights reproduce it to about 1e-2
    rng = np.random.default_rng(0)
    x = (rng.random((cin, G0.SIZE, G0.SIZE)) < 0.03).astype(np.float32) * rng.random((cin, G0.SIZE, G0.SIZE)).astype(np.float32)
    with torch.no_grad():
        y = net(torch.from_numpy(x[None]))[0].numpy()
    np.savez_compressed(os.path.join(out, "holefield_ref.npz"), x=x.astype(np.float16), y=y.astype(np.float32))
    print("RESULT", {"params": int(sum(v.size for v in W.values())), "cin": cin, "y_abs_mean": float(np.abs(y).mean())})


if __name__ == "__main__":
    main()
