from __future__ import annotations

import base64
from dataclasses import dataclass
from io import BytesIO
import ipaddress
from pathlib import Path
import socket
from urllib.parse import urlparse

import numpy as np
import requests
from PIL import Image
from requests import HTTPError

from app.core.config import get_settings
from app.core.constants import CLASS_MAPPING, TREATMENT_SUGGESTIONS
from app.schemas.prediction import PredictionResult
from app.services.model_loader import model_registry
from app.services.preprocess import load_pil_from_bytes, normalize_image


def _make_thumbnail_data_url(payload: bytes, max_size: int = 160) -> str | None:
    """Return a base64 JPEG data-URL thumbnail, or None on any failure."""
    try:
        img = Image.open(BytesIO(payload))
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=80)
        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return None


@dataclass
class InputItem:
    source_type: str
    source_name: str
    payload: bytes


def _is_public_hostname(hostname: str) -> bool:
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False

    for info in infos:
        address = info[4][0]
        ip_addr = ipaddress.ip_address(address)
        if (
            ip_addr.is_private
            or ip_addr.is_loopback
            or ip_addr.is_link_local
            or ip_addr.is_multicast
            or ip_addr.is_reserved
        ):
            return False
    return True


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are supported")
    if not parsed.hostname or not _is_public_hostname(parsed.hostname):
        raise ValueError("URL host is not allowed")


def fetch_url_image(url: str) -> bytes:
    settings = get_settings()
    validate_url(url)

    # Some hosts block generic clients; try browser-like headers first.
    request_variants = [
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Referer": "https://www.google.com/",
        },
        {
            "User-Agent": "curl/8.0.1",
            "Accept": "image/*,*/*;q=0.8",
        },
    ]

    last_error: Exception | None = None
    response = None
    for headers in request_variants:
        try:
            response = requests.get(url, timeout=settings.url_fetch_timeout_sec, headers=headers)
            response.raise_for_status()
            break
        except Exception as exc:
            last_error = exc
            response = None

    if response is None:
        if isinstance(last_error, HTTPError) and last_error.response is not None:
            if last_error.response.status_code == 403:
                raise ValueError(
                    "Remote host denied access (403). Please download the image and upload it as a file instead."
                ) from last_error
        raise ValueError("Failed to fetch image URL") from last_error

    content_type = response.headers.get("content-type", "").lower()
    if not content_type.startswith("image/"):
        raise ValueError("URL does not point to an image")

    return response.content


def predict_input_item(item: InputItem, item_id: str) -> PredictionResult:
    ctx = model_registry.load()

    try:
        img = load_pil_from_bytes(item.payload)
        x, rgb_converted = normalize_image(img, ctx.image_shape)
        pred_proba = ctx.model.predict(x, verbose=0)[0]
        pred_idx = int(np.argmax(pred_proba))
        predicted_class = CLASS_MAPPING[pred_idx]

        probabilities = {
            CLASS_MAPPING[i]: float(prob)
            for i, prob in enumerate(pred_proba.tolist())
        }

        return PredictionResult(
            id=item_id,
            source_type=item.source_type,
            source_name=item.source_name,
            predicted_class=predicted_class,
            probabilities=probabilities,
            rgb_converted=rgb_converted,
            treatment_suggestion=TREATMENT_SUGGESTIONS[predicted_class],
            image_preview=_make_thumbnail_data_url(item.payload),
            errors=[],
        )
    except Exception as exc:
        return PredictionResult(
            id=item_id,
            source_type=item.source_type,
            source_name=item.source_name,
            predicted_class=None,
            probabilities={},
            rgb_converted=False,
            treatment_suggestion=None,
            image_preview=_make_thumbnail_data_url(item.payload),
            errors=[str(exc)],
        )


def filename_or_fallback(name: str | None, index: int) -> str:
    if not name:
        return f"image_{index + 1}.png"
    # Normalize Windows backslashes so Path().name works correctly on Linux too.
    return Path(name.replace("\\", "/")).name
