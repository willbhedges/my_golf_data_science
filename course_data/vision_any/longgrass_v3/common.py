import numpy as np, os, glob
HERE = os.path.dirname(os.path.abspath(__file__))
NATIVE = 4; ROUGH = 0; FC = 1; FW = 2
COURSES = ["gateway_national", "spirit_hollow", "coldwater", "ellis", "mozingo", "eagle_knoll", "veenker",
           "pine_dunes", "hot_springs_arlington", "blue_hills", "national_kc"]
NORM = ["n0_ndvi_s3", "n0_nir_s3", "n0_br_s3", "n0_chroma_s3", "n0_exg_s3", "n0_std_nir_7", "n0_std_nir_15",
        "n0_std_ndvi_7", "n0_glcm_con", "n0_glcm_hom", "n0_lbp_ent", "my_ndvi_mean", "my_ndvi_min", "my_ndvi_std",
        "my_nir_mean", "my_nir_min", "my_chroma_mean", "my_chroma_max", "my_tex_mean", "my_tex_max", "my_con_mean",
        "li_hag", "li_hag_max3", "li_hag_low_s1", "li_hag_low_s3", "li_hag_low_std5", "li_hagstd3", "li_hagmean3"]

def load(slug):
    z = np.load(os.path.join(HERE, f"ds_{slug}.npz"), allow_pickle=True)
    return {k: z[k] for k in z.files}

def ref_mask(d, X, names):
    """Per-course mown-rough reference: eligible cells 3-12 m from OSM fairway (not label-based)."""
    df = X[:, names.index("d_fairway")]
    return (df >= 3) & (df <= 12)

def add_norm(d):
    names = list(d["names"])
    out = {}
    for key in ("X", "Xc"):
        X = d[key]
        ref = ref_mask(d, d["Xc"], names)        # reference from the course-wide sample (label-free)
        cols = []
        for n in NORM:
            if n not in names: continue
            r = d["Xc"][ref, names.index(n)]; r = r[np.isfinite(r)]
            if len(r) < 200: cols.append(np.full(len(X), np.nan, np.float32)); continue
            med = np.median(r); s = 1.4826 * np.median(np.abs(r - med)) + 1e-4
            cols.append(((X[:, names.index(n)] - med) / s).astype(np.float32))
        out[key] = np.column_stack(cols)
    nn = ["z_" + n for n in NORM if n in names]
    return out, nn
