# Plant Disease Classification (Full-Stack App)

This document describes the new full-stack implementation of the project:
- Frontend: Next.js (TypeScript)
- Backend API: FastAPI (Python)
- ML Inference: TensorFlow model artifacts from `jupyter_notebooks/outputs/v2`

## Overview

The application predicts plant leaf condition for three classes:
- Healthy
- Powdery
- Rust

It includes:
- Multi-image and URL-based prediction
- Probability outputs and treatment suggestions
- AI diagnosis assistant (GPT-4.1 by default)
- Visualizer assets and montage generation
- Performance metrics page
- CSV report download

## Project Structure

```text
Plant-Disease-Classification-Project/
  backend/                 # FastAPI service
    app/
      api/
      core/
      schemas/
      services/
    requirements.txt
    .env.example
  frontend/                # Next.js app
    app/
    lib/
    package.json
    .env.example
  jupyter_notebooks/
    outputs/
      v1/                  # visualizer/performance images
      v2/                  # model + evaluation artifacts
```

## Prerequisites

- Python 3.10+
- Node.js 20+
- npm 10+

## Backend Setup (FastAPI)

1. Open terminal in `backend`
2. Create virtual environment

```bash
python -m venv .venv
```

3. Activate virtual environment

Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies

```bash
pip install -r requirements.txt
```

5. Create env file

```bash
copy .env.example .env
```

6. Update `backend/.env` values if needed (especially `OPENAI_API_KEY`)

7. Run API server

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

API docs:
- http://127.0.0.1:8000/docs

## Frontend Setup (Next.js)

1. Open terminal in `frontend`
2. Install dependencies

```bash
npm install
```

3. Create env file

```bash
copy .env.example .env.local
```

4. Run development server

```bash
npm run dev
```

Frontend URL:
- http://localhost:3000

## Environment Variables

### Backend (`backend/.env`)

```env
APP_NAME=Plant Disease Classification API
APP_VERSION=0.1.0
MODEL_PATH=../jupyter_notebooks/outputs/v2/plant_disease_detector.h5
IMAGE_SHAPE_PATH=../jupyter_notebooks/outputs/v2/image_shape.pkl
CONFUSION_MATRIX_PATH=../jupyter_notebooks/outputs/v2/confusion_matrix.joblib
METRICS_PATH=../jupyter_notebooks/outputs/v2/metrics.joblib
VISUALIZER_ASSETS_PATH=../jupyter_notebooks/outputs/v1
DATASET_TEST_PATH=../inputs/plants_dataset/Merged_split_images_swapped/Test
ALLOWED_ORIGINS=http://localhost:3000
MAX_UPLOAD_SIZE_MB=10
MAX_FILES_PER_REQUEST=20
MAX_URLS_PER_REQUEST=20
URL_FETCH_TIMEOUT_SEC=8
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1
OPENAI_TIMEOUT_SEC=20
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## API Endpoints

Base: `/api/v1`

- `GET /health`
- `POST /predict/files`
- `POST /predict/urls`
- `POST /predict/mixed`
- `POST /reports/csv`
- `POST /assist/prediction`
- `GET /performance/summary`
- `GET /visualizer/assets`
- `GET /visualizer/montage`

## Frontend Routes

- `/summary`
- `/visualizer`
- `/detector`
- `/hypothesis`
- `/performance`

## CSV Report Behavior

The detector report CSV exports the same AI-focused content shown in the Analysis Report table:
- Name/Source
- Diagnosis
- Why
- Immediate Actions
- Prevention
- Errors

Note: AI columns are populated only for items where AI diagnosis has been requested.

## Troubleshooting

### 1) `OPENAI_API_KEY is not configured`
- Ensure `backend/.env` contains a valid `OPENAI_API_KEY`
- Restart backend after editing env file

### 2) Frontend cannot reach backend
- Confirm backend is running on `127.0.0.1:8000`
- Confirm `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local`
- Restart frontend after env changes

### 3) Running backend from wrong folder
- Run from `backend` using:
  - `uvicorn app.main:app --reload`

### 4) Missing Python packages in editor
- Activate the same `.venv` used for backend runtime in your VS Code Python interpreter

## Notes

- The backend auto-loads `backend/.env` at startup.
- Model and metrics are loaded from the artifact paths configured in env.
- Static visual assets are served through backend static mounting.
