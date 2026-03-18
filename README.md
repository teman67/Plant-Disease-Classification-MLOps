# Plant Disease Classification (Full-Stack App)

This is the migrated full-stack version of the original Streamlit dashboard.

- Frontend: Next.js (TypeScript)
- Backend API: FastAPI (Python)
- ML Inference: TensorFlow model and artifacts from `jupyter_notebooks/outputs/v2`

## Table of Contents

- [Introduction](#introduction)
- [Business Requirements](#business-requirements)
- [Hypotheses and Validation](#hypotheses-and-validation)
- [Rationale: Business Requirements to Data/ML Tasks](#rationale-business-requirements-to-dataml-tasks)
- [ML Business Case](#ml-business-case)
- [User Stories](#user-stories)
- [Full-Stack Architecture](#full-stack-architecture)
- [Project Structure](#project-structure)
- [Feature and Route Map](#feature-and-route-map)
- [Local Setup](#local-setup)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Project Outcomes](#project-outcomes)
- [Hypothesis Outcomes](#hypothesis-outcomes)
- [Testing](#testing)
- [Bugs](#bugs)
- [Deployment Notes](#deployment-notes)
- [Languages and Libraries](#languages-and-libraries)
- [Credits](#credits)

## Introduction

The application classifies plant leaf images into:
- Healthy
- Powdery
- Rust

In addition to prediction, it provides treatment guidance, performance insights, visual exploration tools, and downloadable reports.

Original Streamlit deployment reference:
- https://plant-disease-classification-mlops.streamlit.app/

## Business Requirements

The client needs an automated way to identify leaf diseases at scale and reduce manual inspection effort. The target requirements are:

- Visually differentiate healthy leaves from powdery mildew and rust leaves.
- Predict healthy/powdery/rust with high confidence (target around 95% test accuracy).
- Provide treatment recommendations based on predicted class.
- Provide downloadable reports for prediction runs.

## Hypotheses and Validation

1. Healthy, powdery, and rust leaves can be visually differentiated.
2. The model can reach high performance on unseen test data (target around 95%).
3. Prediction quality may degrade when image backgrounds differ substantially from dataset background conditions.
4. RGB images are preferred; non-RGB images should be converted before inference.

## Rationale: Business Requirements to Data/ML Tasks

- Requirement 1 (Visualization):
  - Show mean/variability visuals for class comparisons.
  - Show difference-between-averages visuals.
  - Provide class montage generation.
- Requirement 2 (Classification):
  - Train and run a 3-class image classifier.
  - Return class probabilities and treatment suggestions.
- Requirement 3 (Report):
  - Export prediction outcomes and related analysis to CSV.

## ML Business Case

The classification workflow follows standard ML stages:
- Data collection
- Data preprocessing and resizing
- Feature learning with CNN layers
- Model training/validation/testing
- Deployment and monitoring

Dataset source:
- https://www.kaggle.com/datasets/rashikrahmanpritom/plant-disease-recognition-dataset

The project data contains healthy, powdery, and rust leaf classes and uses resized images for practical training/inference performance.

## User Stories

- As a client, I want intuitive navigation so I can quickly access all analysis pages.
- As a client, I want visual comparisons between healthy and infected leaves.
- As a client, I want montage previews by class.
- As a client, I want to upload files or URLs and get predictions with confidence values.
- As a client, I want treatment suggestions for infected classes.
- As a client, I want downloadable CSV reports for record keeping.

## Full-Stack Architecture

### Frontend (Next.js)

- Route-based app with pages:
  - `/summary`
  - `/visualizer`
  - `/detector`
  - `/hypothesis`
  - `/performance`

### Backend (FastAPI)

- Serves inference and reporting APIs under `/api/v1`.
- Loads model and artifacts at startup.
- Handles file and URL ingestion.
- Serves visualizer/performance image assets.
- Integrates optional AI assistant response generation.

### ML Artifacts

- `jupyter_notebooks/outputs/v2/plant_disease_detector.h5`
- `jupyter_notebooks/outputs/v2/image_shape.pkl`
- `jupyter_notebooks/outputs/v2/confusion_matrix.joblib`
- `jupyter_notebooks/outputs/v2/metrics.joblib`
- Visual assets from `jupyter_notebooks/outputs/v1`

## Project Structure

```text
Plant-Disease-Classification-Project/
  backend/
    app/
      api/
      core/
      schemas/
      services/
    requirements.txt
    .env.example
  frontend/
    app/
    components/
    lib/
    package.json
    .env.example
  inputs/
  jupyter_notebooks/
  readme/
  README.md
  readme_new.md
```

## Feature and Route Map

1. Summary (`/summary`)
- Quick project context, disease background, data overview.

2. Visualizer (`/visualizer`)
- Mean/variability visuals.
- Difference-between-averages visuals.
- Dynamic montage generation by class.

3. Detector (`/detector`)
- Multi-file upload and multi-URL input.
- Per-item prediction with probabilities.
- Treatment suggestion per class.
- Optional AI diagnosis details.
- Analysis report table and CSV download.

4. Hypothesis (`/hypothesis`)
- Hypothesis statements and validation narrative.

5. Performance (`/performance`)
- Label distribution, training curves, evaluation summary.
- Confusion matrix and metrics.

## Local Setup

## Prerequisites

- Python 3.10+
- Node.js 20+
- npm 10+

## Backend Setup (FastAPI)

1. Open terminal in `backend`.
2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate it (Windows PowerShell):

```bash
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Create env file:

```bash
copy .env.example .env
```

6. Run API:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

API docs:
- http://127.0.0.1:8000/docs

## Frontend Setup (Next.js)

1. Open terminal in `frontend`.
2. Install dependencies:

```bash
npm install
```

3. Create env file:

```bash
copy .env.example .env.local
```

4. Start frontend:

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

## Project Outcomes

- Business Requirement 1 (Visualization): implemented via visualizer page with average/variability and montage workflows.
- Business Requirement 2 (Classification): implemented via detector page with multi-input support and probability outputs.
- Business Requirement 3 (Reporting): implemented via analysis table + CSV export.

## Hypothesis Outcomes

Based on the original project findings and retained artifact behavior:

- Visual differentiation between healthy and infected classes is supported by montage and average/variability studies.
- The selected model version is the stronger-performing artifact set used by the app.
- Background differences in user images can still affect prediction quality.
- RGB normalization is applied to avoid mode-related inference failures.

## Testing

Testing is covered through:

- Artifact-based validation from the original ML workflow (`jupyter_notebooks`).
- UI flow checks for all pages.
- Detector checks:
  - file upload and URL ingestion
  - prediction rendering
  - probability outputs
  - treatment suggestions
  - CSV export
- Frontend linting (`npm run lint`).

## Bugs

### Fixed (historical + migration)

- Non-RGB image mode crash: fixed by RGB conversion before inference.
- Image size/performance issues: mitigated with image preprocessing/resizing.
- Name mapping inconsistencies from mixed upload sources: corrected in prediction flow.
- CSV mismatch with analysis table: updated to export AI report-aligned columns.

### Known Unfixed

- No known functional blockers at the time of writing.

## Deployment Notes

### Legacy Streamlit Deployment

The original project includes Heroku/Streamlit deployment documentation in the legacy README.

### Full-Stack Deployment Direction

For this migrated version, deploy frontend and backend independently:

- Frontend (Next.js): Vercel or containerized hosting.
- Backend (FastAPI): Render, Railway, Azure Web App, AWS ECS/Fargate, or VM/container.

Minimum production requirements:

- Configure `ALLOWED_ORIGINS` to frontend domain(s).
- Configure `NEXT_PUBLIC_API_BASE_URL` to backend URL.
- Provide model/artifact files at configured paths.
- Set `OPENAI_API_KEY` only if AI assistant is enabled.

## Languages and Libraries

### Languages

- Python
- TypeScript
- JavaScript

### Frameworks and Libraries

- FastAPI
- Uvicorn
- TensorFlow / Keras
- NumPy
- Pandas
- Joblib
- Pillow
- Requests
- Next.js
- React
- React Markdown
- ESLint

### Data/Workflow Tooling (Project History)

- Jupyter Notebook
- Kaggle
- Streamlit (original implementation)
- GitHub / Git / GitHub Projects

## Credits

- Code Institute Malaria Detector walkthrough for solution inspiration.
- Original README template inspiration from mildew detection project.
- Dataset: Plant disease recognition dataset on Kaggle (CC0 Public Domain).
- CRISP-DM diagram and educational references noted in the original README.
- Community educational resources used during model and app development.
