export type DiseaseClass = "Healthy" | "Powdery" | "Rust";

export type PredictionItem = {
  id: string;
  source_type: "file" | "url";
  source_name: string;
  predicted_class: DiseaseClass | null;
  probabilities: Partial<Record<DiseaseClass, number>>;
  rgb_converted: boolean;
  treatment_suggestion: string | null;
  image_preview: string | null;
  errors: string[];
};

export type PredictionResponse = {
  predictions: PredictionItem[];
};

export type AiDiagnosisResponse = {
  model: string;
  diagnosis: string;
  why: string;
  immediate_actions: string[];
  prevention: string[];
  raw_response: string;
};

export type PerformanceResponse = {
  confusion_matrix: number[][] | null;
  metrics: Record<string, number> | null;
  evaluation: {
    loss: number | null;
    accuracy: number | null;
  } | null;
};

export type VisualizerAsset = {
  name: string;
  url: string;
};

export type VisualizerAssetsResponse = {
  assets: VisualizerAsset[];
};
