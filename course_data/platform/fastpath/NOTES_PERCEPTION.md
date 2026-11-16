# Notes from the perception / hole-inference side (fast path)

## Requests to the fetch / imagery side

None open. The perception scene reads only what the fetch stage already writes: `imagery/naip_rgb.tif`,
`imagery/naip_nir.tif` (0.6 m, NAIP CRS), `imagery/dem.tif` (1 m UTM), `canopy/chm_meta.tif`, `raw/course.json`,
`raw/osm.geojson` (non-golf OSM buildings / roads are used as a negative mask).

## The segment U-Net (blocked on access, decision with the user)

`fastscene.py` uses the U-Net when its weights exist (`FASTSCENE_UNET=<file>` or
`fastscene_model/unet/model.safetensors`), else the LightGBM pixel classifier. The forward pass runs without torch
(`fastc/perception/unet.py`, numpy + OpenBLAS GEMMs, C im2col / epilogues; tested on random weights). Weights:

* our own model: Actions run 38987845450 (segment_train.yml, 2026-10-17), artifact `golfseg-own-model` (45 MB,
  expires 2027-01-15); its download host (productionresultssa*.blob.core.windows.net) is refused by this container's
  proxy;
* ariadgolf/golf-course-segmentation on Hugging Face (no licence grant: never commit it); huggingface.co is refused.

Timing with random weights on Yorba Linda (48 tiles of 512 px at 0.6 m, no flip TTA): 61 s for the U-Net step.
