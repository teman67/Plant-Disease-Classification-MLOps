from __future__ import annotations

from contextlib import asynccontextmanager
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Allows running this file directly with `python main.py` from backend/app.
if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.api.routes import router
from app.core.config import get_settings
from app.services.model_loader import model_registry


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Load model once at boot for lower first-request latency.
    model_registry.load()
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exposes existing visual/performance image artifacts through /static.
app.mount("/static", StaticFiles(directory=str(settings.visualizer_assets_path.parent)), name="static")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Plant Disease Classification API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
