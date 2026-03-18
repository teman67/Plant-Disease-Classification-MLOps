from functools import lru_cache
from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _load_env_file(env_path: Path) -> None:
    if not env_path.exists() or not env_path.is_file():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        # Keep shell-provided values as highest priority.
        os.environ.setdefault(key, value)


_load_env_file(PROJECT_ROOT / "backend" / ".env")


class Settings:
    app_name: str = "Plant Disease Classification API"
    app_version: str = "0.1.0"

    model_path: Path = PROJECT_ROOT / "jupyter_notebooks" / "outputs" / "v2" / "plant_disease_detector.h5"
    image_shape_path: Path = PROJECT_ROOT / "jupyter_notebooks" / "outputs" / "v2" / "image_shape.pkl"
    confusion_matrix_path: Path = PROJECT_ROOT / "jupyter_notebooks" / "outputs" / "v2" / "confusion_matrix.joblib"
    metrics_path: Path = PROJECT_ROOT / "jupyter_notebooks" / "outputs" / "v2" / "metrics.joblib"

    visualizer_assets_path: Path = PROJECT_ROOT / "jupyter_notebooks" / "outputs" / "v1"
    dataset_test_path: Path = (
        PROJECT_ROOT
        / "inputs"
        / "plants_dataset"
        / "Merged_split_images_swapped"
        / "Test"
    )

    allowed_origins: list[str] = ["*"]
    max_upload_size_mb: int = 10
    max_files_per_request: int = 20
    max_urls_per_request: int = 20
    url_fetch_timeout_sec: int = 8
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1"
    openai_timeout_sec: int = 20

    @classmethod
    def from_env(cls) -> "Settings":
        settings = cls()
        settings.app_name = os.getenv("APP_NAME", settings.app_name)
        settings.app_version = os.getenv("APP_VERSION", settings.app_version)

        settings.model_path = Path(os.getenv("MODEL_PATH", str(settings.model_path)))
        settings.image_shape_path = Path(os.getenv("IMAGE_SHAPE_PATH", str(settings.image_shape_path)))
        settings.confusion_matrix_path = Path(
            os.getenv("CONFUSION_MATRIX_PATH", str(settings.confusion_matrix_path))
        )
        settings.metrics_path = Path(os.getenv("METRICS_PATH", str(settings.metrics_path)))
        settings.visualizer_assets_path = Path(
            os.getenv("VISUALIZER_ASSETS_PATH", str(settings.visualizer_assets_path))
        )
        settings.dataset_test_path = Path(
            os.getenv("DATASET_TEST_PATH", str(settings.dataset_test_path))
        )

        allowed_origins_raw = os.getenv("ALLOWED_ORIGINS")
        if allowed_origins_raw:
            settings.allowed_origins = [origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()]

        settings.max_upload_size_mb = int(
            os.getenv("MAX_UPLOAD_SIZE_MB", str(settings.max_upload_size_mb))
        )
        settings.max_files_per_request = int(
            os.getenv("MAX_FILES_PER_REQUEST", str(settings.max_files_per_request))
        )
        settings.max_urls_per_request = int(
            os.getenv("MAX_URLS_PER_REQUEST", str(settings.max_urls_per_request))
        )
        settings.url_fetch_timeout_sec = int(
            os.getenv("URL_FETCH_TIMEOUT_SEC", str(settings.url_fetch_timeout_sec))
        )
        settings.openai_api_key = os.getenv("OPENAI_API_KEY", settings.openai_api_key)
        settings.openai_model = os.getenv("OPENAI_MODEL", settings.openai_model)
        settings.openai_timeout_sec = int(
            os.getenv("OPENAI_TIMEOUT_SEC", str(settings.openai_timeout_sec))
        )
        return settings


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
