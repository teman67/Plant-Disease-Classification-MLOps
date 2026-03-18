from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from app.core.config import get_settings


def _normalize_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.float32, np.float64)):
        return float(value)
    if isinstance(value, (np.integer, np.int32, np.int64)):
        return int(value)
    if isinstance(value, pd.DataFrame):
        return value.to_dict(orient="records")
    if isinstance(value, pd.Series):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(k): _normalize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_value(item) for item in value]
    return value


def _safe_joblib_load(path: Path) -> Any:
    if not path.exists():
        return None
    return joblib.load(str(path))


def _extract_evaluation(evaluation: Any, metrics: Any) -> dict[str, float | None]:
    loss: float | None = None
    accuracy: float | None = None

    if isinstance(evaluation, np.ndarray):
        evaluation = evaluation.tolist()

    if isinstance(evaluation, (list, tuple)) and len(evaluation) >= 2:
        if isinstance(evaluation[0], (int, float, np.floating, np.integer)):
            loss = float(evaluation[0])
        if isinstance(evaluation[1], (int, float, np.floating, np.integer)):
            accuracy = float(evaluation[1])
    elif isinstance(evaluation, dict):
        raw_loss = evaluation.get("loss")
        raw_acc = evaluation.get("accuracy")

        if raw_loss is None:
            raw_loss = evaluation.get("test_loss")
        if raw_acc is None:
            raw_acc = evaluation.get("test_accuracy")

        if isinstance(raw_loss, (int, float, np.floating, np.integer)):
            loss = float(raw_loss)
        if isinstance(raw_acc, (int, float, np.floating, np.integer)):
            accuracy = float(raw_acc)

    if accuracy is None and isinstance(metrics, dict):
        raw_acc = metrics.get("accuracy")
        if isinstance(raw_acc, (int, float, np.floating, np.integer)):
            accuracy = float(raw_acc)

    return {"loss": loss, "accuracy": accuracy}


def get_performance_summary() -> dict[str, Any]:
    settings = get_settings()

    confusion_matrix = _safe_joblib_load(settings.confusion_matrix_path)
    metrics = _safe_joblib_load(settings.metrics_path)
    evaluation_path = settings.visualizer_assets_path / "evaluation.pkl"
    evaluation = _safe_joblib_load(evaluation_path)
    normalized_metrics = _normalize_value(metrics)

    return {
        "confusion_matrix": _normalize_value(confusion_matrix),
        "metrics": normalized_metrics,
        "evaluation": _extract_evaluation(evaluation, normalized_metrics),
    }
