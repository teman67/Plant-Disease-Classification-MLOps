from __future__ import annotations

from io import BytesIO
import random

from PIL import Image

from app.core.config import get_settings


def list_visualizer_assets() -> list[dict[str, str]]:
    settings = get_settings()
    base = settings.visualizer_assets_path
    if not base.exists():
        return []

    assets: list[dict[str, str]] = []
    for path in sorted(base.glob("*")):
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            assets.append(
                {
                    "name": path.name,
                    "url": f"/static/v1/{path.name}",
                }
            )
    return assets


def build_montage(label: str, rows: int = 3, cols: int = 3) -> bytes:
    settings = get_settings()
    label_dir = settings.dataset_test_path / label
    if not label_dir.exists() or not label_dir.is_dir():
        raise FileNotFoundError(f"Label directory not found: {label_dir}")

    image_paths = [
        path
        for path in label_dir.iterdir()
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    ]
    if not image_paths:
        raise FileNotFoundError(f"No images found under: {label_dir}")

    grid_size = max(1, rows * cols)
    selected = random.sample(image_paths, k=min(grid_size, len(image_paths)))

    loaded_images = [Image.open(path).convert("RGB") for path in selected]
    tile_w = min(img.width for img in loaded_images)
    tile_h = min(img.height for img in loaded_images)

    montage = Image.new("RGB", (cols * tile_w, rows * tile_h), color=(240, 240, 240))

    for idx in range(grid_size):
        x = (idx % cols) * tile_w
        y = (idx // cols) * tile_h
        if idx < len(loaded_images):
            tile = loaded_images[idx].resize((tile_w, tile_h), Image.LANCZOS)
            montage.paste(tile, (x, y))

    out = BytesIO()
    montage.save(out, format="PNG")
    return out.getvalue()
