import {
  AiDiagnosisResponse,
  PerformanceResponse,
  PredictionItem,
  PredictionResponse,
  VisualizerAssetsResponse,
} from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export async function fetchVisualizerAssets(): Promise<VisualizerAssetsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/visualizer/assets`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Failed to load visualizer assets");
  }
  return response.json();
}

export async function fetchPerformance(): Promise<PerformanceResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/performance/summary`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Failed to load performance summary");
  }
  return response.json();
}

export async function predictMixed(formData: FormData): Promise<PredictionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/predict/mixed`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Prediction request failed");
  }
  return response.json();
}

export async function downloadCsv(
  predictions: unknown,
  aiData: Record<string, unknown> = {},
): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/v1/reports/csv`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ predictions, ai_data: aiData }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "CSV generation failed");
  }

  return response.blob();
}

export async function fetchAiDiagnosis(prediction: PredictionItem): Promise<AiDiagnosisResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/assist/prediction`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prediction }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "AI diagnosis request failed");
  }

  return response.json();
}
