from __future__ import annotations

from io import BytesIO

import numpy as np
from PIL import Image, UnidentifiedImageError


def load_pil_from_bytes(payload: bytes) -> Image.Image:
    try:
        return Image.open(BytesIO(payload))
    except UnidentifiedImageError as exc:
        raise ValueError("Unsupported or corrupt image payload") from exc


def normalize_image(img: Image.Image, image_shape: tuple[int, int, int]) -> tuple[np.ndarray, bool]:
    rgb_converted = False
    if img.mode != "RGB":
        img = img.convert("RGB")
        rgb_converted = True

    target_height, target_width = image_shape[0], image_shape[1]
    img_resized = img.resize((target_width, target_height), Image.LANCZOS)

    x = np.array(img_resized, dtype=np.float32) / 255.0
    x = np.expand_dims(x, axis=0)
    return x, rgb_converted
