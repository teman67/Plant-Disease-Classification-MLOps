from __future__ import annotations

import json
from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response, StreamingResponse

from app.core.config import get_settings
from app.schemas.prediction import (
    AiAssistRequest,
    AiAssistResponse,
    CsvReportRequest,
    PredictionListResponse,
    UrlPredictRequest,
)
from app.services.ai_assistant import generate_prediction_guidance
from app.services.model_loader import model_registry
from app.services.performance import get_performance_summary
from app.services.predict import InputItem, fetch_url_image, filename_or_fallback, predict_input_item
from app.services.reporting import build_csv_report
from app.services.visualizer import build_montage, list_visualizer_assets


router = APIRouter(prefix="/api/v1", tags=["v1"])


@router.get("/health")
def health() -> dict[str, object]:
    settings = get_settings()
    return {
        "status": "ok",
        "version": settings.app_version,
        "model_loaded": model_registry.is_loaded(),
    }


@router.post("/predict/files", response_model=PredictionListResponse)
async def predict_files(files: list[UploadFile] = File(...)) -> PredictionListResponse:
    settings = get_settings()
    if len(files) > settings.max_files_per_request:
        raise HTTPException(status_code=400, detail="Too many files")

    items: list[InputItem] = []
    for index, file in enumerate(files):
        payload = await file.read()
        if len(payload) > settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"File too large: {file.filename}")

        items.append(
            InputItem(
                source_type="file",
                source_name=filename_or_fallback(file.filename, index),
                payload=payload,
            )
        )

    predictions = [predict_input_item(item, item_id=f"file-{idx + 1}") for idx, item in enumerate(items)]
    return PredictionListResponse(predictions=predictions)


@router.post("/predict/urls", response_model=PredictionListResponse)
def predict_urls(request: UrlPredictRequest) -> PredictionListResponse:
    settings = get_settings()
    if len(request.urls) > settings.max_urls_per_request:
        raise HTTPException(status_code=400, detail="Too many URLs")

    predictions = []
    for idx, url in enumerate(request.urls):
        item_id = f"url-{idx + 1}"
        try:
            payload = fetch_url_image(str(url))
            item = InputItem(source_type="url", source_name=str(url), payload=payload)
            predictions.append(predict_input_item(item, item_id=item_id))
        except Exception as exc:
            predictions.append(
                predict_input_item(
                    InputItem(source_type="url", source_name=str(url), payload=b""),
                    item_id=item_id,
                ).model_copy(update={"errors": [str(exc)]})
            )

    return PredictionListResponse(predictions=predictions)


@router.post("/predict/mixed", response_model=PredictionListResponse)
async def predict_mixed(
    files: list[UploadFile] = File(default_factory=list),
    urls_json: str = Form(default="[]"),
) -> PredictionListResponse:
    try:
        urls = json.loads(urls_json)
        if not isinstance(urls, list):
            raise ValueError("urls_json must be a JSON array")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid urls_json payload: {exc}") from exc

    results = []

    for idx, file in enumerate(files):
        payload = await file.read()
        item = InputItem(
            source_type="file",
            source_name=filename_or_fallback(file.filename, idx),
            payload=payload,
        )
        results.append(predict_input_item(item, item_id=f"mixed-file-{idx + 1}"))

    for idx, url in enumerate(urls):
        item_id = f"mixed-url-{idx + 1}"
        try:
            payload = fetch_url_image(str(url))
            item = InputItem(source_type="url", source_name=str(url), payload=payload)
            results.append(predict_input_item(item, item_id=item_id))
        except Exception as exc:
            results.append(
                predict_input_item(
                    InputItem(source_type="url", source_name=str(url), payload=b""),
                    item_id=item_id,
                ).model_copy(update={"errors": [str(exc)]})
            )

    return PredictionListResponse(predictions=results)


@router.post("/reports/csv")
def reports_csv(request: CsvReportRequest) -> StreamingResponse:
    csv_data = build_csv_report(request.predictions, request.ai_data)
    return StreamingResponse(
        BytesIO(csv_data.encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=analysis_report.csv"},
    )


@router.post("/assist/prediction", response_model=AiAssistResponse)
def assist_prediction(request: AiAssistRequest) -> AiAssistResponse:
    try:
        model, advice = generate_prediction_guidance(request.prediction)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return AiAssistResponse(model=model, **advice)


@router.get("/performance/summary")
def performance_summary() -> dict[str, object]:
    return get_performance_summary()


@router.get("/visualizer/assets")
def visualizer_assets() -> dict[str, object]:
    return {"assets": list_visualizer_assets()}


@router.get("/visualizer/montage")
def visualizer_montage(label: str, rows: int = 3, cols: int = 3) -> Response:
    if label not in {"Healthy", "Powdery", "Rust"}:
        raise HTTPException(status_code=400, detail="Invalid label")

    if rows < 1 or cols < 1 or rows > 12 or cols > 12:
        raise HTTPException(status_code=400, detail="rows/cols out of allowed range")

    try:
        image_data = build_montage(label=label, rows=rows, cols=cols)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return Response(content=image_data, media_type="image/png")
