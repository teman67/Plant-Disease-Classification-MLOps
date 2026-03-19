# ─────────────────────────────────────────────
# Plant Disease Classification – Backend image
# Build context: repo root
#   docker build -t plant-disease-api .
#   docker run -p 8000:8000 plant-disease-api
# ─────────────────────────────────────────────

FROM python:3.11-slim

# System libraries required by TensorFlow-CPU and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Python dependencies (cached layer) ──────
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# ── Application code ────────────────────────
COPY backend/ backend/

# ── ML artifacts ────────────────────────────
# v2: model + metrics used for inference and performance page
COPY jupyter_notebooks/outputs/v2/ jupyter_notebooks/outputs/v2/
# v1: visualizer static assets (mean/variability PNGs, evaluation.pkl)
COPY jupyter_notebooks/outputs/v1/ jupyter_notebooks/outputs/v1/

# ── Dataset (Test split) ────────────────────
# Required by the visualizer montage endpoint.
# Remove this COPY and set DATASET_TEST_PATH env var to an external
# volume mount if you want a smaller image without the dataset.
COPY inputs/plants_dataset/Merged_split_images_swapped/Test/ \
     inputs/plants_dataset/Merged_split_images_swapped/Test/

EXPOSE 8000

# Run from backend/ so Python resolves `app.main:app` as a package.
# PROJECT_ROOT in config.py walks 3 levels up from config.py and lands
# at /app, which is where the artifacts were copied.
WORKDIR /app/backend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
