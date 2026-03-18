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
