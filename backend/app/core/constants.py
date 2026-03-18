CLASS_MAPPING = {0: "Healthy", 1: "Powdery", 2: "Rust"}

TREATMENT_SUGGESTIONS = {
    "Healthy": "No treatment needed",
    "Powdery": (
        "1. Remove and destroy infected leaves. "
        "2. Apply fungicides such as sulfur, neem oil, or potassium bicarbonate. "
        "3. Ensure proper air circulation around plants."
    ),
    "Rust": (
        "1. Remove and destroy infected leaves. "
        "2. Apply fungicides such as copper-based compounds or sulfur. "
        "3. Prune affected areas and ensure proper air circulation."
    ),
}

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
