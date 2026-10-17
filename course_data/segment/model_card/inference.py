"""Predict six semantic classes from four-band aerial imagery."""

import argparse
import json
from pathlib import Path

import numpy as np
import rasterio
import segmentation_models_pytorch as smp
import torch
from huggingface_hub import hf_hub_download

DEFAULT_REPO = 'ariadgolf/golf-course-segmentation'


def load_model(model_id=DEFAULT_REPO, revision=None, device='cpu'):
    path = Path(model_id)
    if path.is_dir():
        config_path = path / 'preprocessor_config.json'
    else:
        config_path = Path(hf_hub_download(model_id, 'preprocessor_config.json', revision=revision))
    config = json.loads(config_path.read_text())
    model = smp.from_pretrained(str(model_id), revision=revision)
    model = model.float().to(device).eval()
    return model, config


@torch.inference_mode()
def predict(model, config, image, tta=True):
    image = np.asarray(image)
    expected = (4, config['tile_size'], config['tile_size'])
    if image.shape != expected or image.dtype != np.uint8:
        raise ValueError(f'Expected uint8 RGB+NIR array with shape {expected}; got {image.dtype} {image.shape}')
    mean = np.asarray(config['image_mean'], dtype=np.float32)[:, None, None]
    std = np.asarray(config['image_std'], dtype=np.float32)[:, None, None]
    normalized = np.ascontiguousarray((image.astype(np.float32) - mean) / std)
    x = torch.from_numpy(normalized)[None].to(next(model.parameters()).device)
    probabilities = []
    for dimension in ((None, 3, 2) if tta else (None,)):
        augmented = x if dimension is None else x.flip(dimension)
        probability = model(augmented).softmax(dim=1)
        if dimension is not None:
            probability = probability.flip(dimension)
        probabilities.append(probability)
    return torch.stack(probabilities).mean(dim=0)[0].cpu().numpy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--model', default=DEFAULT_REPO)
    parser.add_argument('--revision')
    parser.add_argument('--device', default='cpu', choices=['cpu', 'cuda', 'mps'])
    parser.add_argument('--no-tta', action='store_true')
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve() or args.output.exists():
        parser.error('Choose a new output path to preserve existing data.')
    with rasterio.open(args.input) as src:
        if src.count != 4:
            parser.error('The input must have exactly four bands in R, G, B, NIR order.')
        if src.colorinterp[3] == rasterio.enums.ColorInterp.alpha:
            parser.error('The fourth band is marked as alpha. Supply near-infrared imagery with correct band metadata.')
        image = src.read()
        valid = np.all(src.read_masks() > 0, axis=0)
        profile = {'driver':'GTiff', 'width':src.width, 'height':src.height,
                   'crs':src.crs, 'transform':src.transform, 'dtype':'uint8',
                   'count':1, 'nodata':255, 'compress':'deflate'}
    model, config = load_model(args.model, args.revision, args.device)
    probabilities = predict(model, config, image, tta=not args.no_tta)
    mask = probabilities.argmax(axis=0).astype(np.uint8)
    mask[~valid] = 255
    with rasterio.open(args.output, 'w', **profile) as dst:
        dst.write(mask, 1)
        dst.set_band_description(1, 'semantic_class')
        dst.update_tags(id2label=json.dumps(config['id2label']))
    print(args.output)


if __name__ == '__main__':
    main()
