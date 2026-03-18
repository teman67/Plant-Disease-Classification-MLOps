# FastAPI Backend (Migration)

## Run locally

1. Create and activate a virtual environment
2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Start API:

```bash
uvicorn backend.app.main:app --reload
```

Open docs at `http://127.0.0.1:8000/docs`.

## Implemented endpoints

- `GET /api/v1/health`
- `POST /api/v1/predict/files`
- `POST /api/v1/predict/urls`
- `POST /api/v1/predict/mixed`
- `POST /api/v1/reports/csv`
- `GET /api/v1/performance/summary`
- `GET /api/v1/visualizer/assets`
- `GET /api/v1/visualizer/montage`

## Testing

Dependencies are in `requirements-dev.txt`. Install them alongside the main requirements:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### Unit tests (default)

Run from the `backend/` directory. All external dependencies (model, dataset, joblib
files) are mocked — no GPU or real artifacts required.

```bash
pytest
```

184 tests covering API routes, services, schemas, and configuration.

### Integration tests

Integration tests load the **real Keras model** (`plant_disease_detector.h5`) and
read the actual joblib/pkl artifacts from `jupyter_notebooks/outputs/v2/`. They also
use real images from `inputs/plants_dataset/`. The model loads once per session so
the full suite finishes in ~10 seconds after the initial load.

```bash
pytest -m integration
```

61 tests across four files:

| File | What it tests |
|---|---|
| `test_integration_prediction.py` | Model loading and service-layer inference with real images |
| `test_integration_api.py` | Full HTTP stack — uploads, batch predict, CSV report |
| `test_integration_artifacts.py` | Joblib/pkl integrity, performance endpoint, visualizer montage |

> **Skip condition** — if `plant_disease_detector.h5` is not found all integration
> tests are automatically skipped, so CI stays green without the large model file.

### Run everything

```bash
pytest -m "integration or not integration"
```
