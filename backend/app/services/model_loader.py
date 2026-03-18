from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

import joblib
from tensorflow.keras.models import load_model

from app.core.config import get_settings


@dataclass
class ModelContext:
    model: object
    image_shape: tuple[int, int, int]


class ModelRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._ctx: ModelContext | None = None

    def load(self) -> ModelContext:
        if self._ctx is not None:
            return self._ctx

        settings = get_settings()
        with self._lock:
            if self._ctx is None:
                model = load_model(str(settings.model_path))
                image_shape = joblib.load(str(settings.image_shape_path))
                self._ctx = ModelContext(model=model, image_shape=tuple(image_shape))
        return self._ctx

    def is_loaded(self) -> bool:
        return self._ctx is not None


model_registry = ModelRegistry()
