from pydantic import BaseModel, Field, HttpUrl


class UrlPredictRequest(BaseModel):
    urls: list[HttpUrl] = Field(default_factory=list)


class PredictionResult(BaseModel):
    id: str
    source_type: str
    source_name: str
    predicted_class: str | None
    probabilities: dict[str, float] = Field(default_factory=dict)
    rgb_converted: bool = False
    treatment_suggestion: str | None = None
    image_preview: str | None = None
    errors: list[str] = Field(default_factory=list)


class PredictionListResponse(BaseModel):
    predictions: list[PredictionResult]


class CsvAiData(BaseModel):
    diagnosis: str = ""
    why: str = ""
    immediate_actions: list[str] = Field(default_factory=list)
    prevention: list[str] = Field(default_factory=list)


class CsvReportRequest(BaseModel):
    predictions: list[PredictionResult]
    ai_data: dict[str, CsvAiData] = Field(default_factory=dict)


class AiAssistRequest(BaseModel):
    prediction: PredictionResult


class AiAssistResponse(BaseModel):
    model: str
    diagnosis: str
    why: str
    immediate_actions: list[str] = Field(default_factory=list)
    prevention: list[str] = Field(default_factory=list)
    raw_response: str = ""
