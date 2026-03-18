"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { downloadCsv, fetchAiDiagnosis, predictMixed } from "@/lib/api";
import { AiDiagnosisResponse, PredictionItem } from "@/lib/types";

const classes = ["Healthy", "Powdery", "Rust"] as const;

function score(value: number | undefined): string {
  return `${((value || 0) * 100).toFixed(2)}%`;
}

function conicChartStyle(item: PredictionItem): string {
  const healthy = Math.max(0, item.probabilities.Healthy || 0);
  const powdery = Math.max(0, item.probabilities.Powdery || 0);

  const a = healthy * 360;
  const b = powdery * 360;
  const stopB = a + b;

  return `conic-gradient(
    #16a34a 0deg ${a}deg,
    #f59e0b ${a}deg ${stopB}deg,
    #dc2626 ${stopB}deg 360deg
  )`;
}

export default function DetectorClient() {
  const [files, setFiles] = useState<File[]>([]);
  const [urlInput, setUrlInput] = useState("");
  const [confirmedUrls, setConfirmedUrls] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [predictions, setPredictions] = useState<PredictionItem[]>([]);
  const [previewByPredictionId, setPreviewByPredictionId] = useState<Record<string, string>>({});
  const [aiAdviceById, setAiAdviceById] = useState<Record<string, AiDiagnosisResponse>>({});
  const [aiErrorById, setAiErrorById] = useState<Record<string, string>>({});
  const [aiLoadingById, setAiLoadingById] = useState<Record<string, boolean>>({});
  const objectPreviewUrlsRef = useRef<string[]>([]);

  const validUrls = useMemo(
    () =>
      urlInput
        .split("\n")
        .map((u) => u.trim())
        .filter(Boolean),
    [urlInput],
  );

  useEffect(() => {
    return () => {
      objectPreviewUrlsRef.current.forEach((url) => URL.revokeObjectURL(url));
      objectPreviewUrlsRef.current = [];
    };
  }, []);

  async function onPredict() {
    if (files.length === 0 && confirmedUrls.length === 0) {
      setError("Upload at least one image or provide one URL.");
      return;
    }

    setLoading(true);
    setError(null);

    const nextFilePreviewUrls = files.map((file) => URL.createObjectURL(file));

    try {
      const form = new FormData();
      files.forEach((file) => form.append("files", file));
      form.append("urls_json", JSON.stringify(confirmedUrls));

      const result = await predictMixed(form);

      objectPreviewUrlsRef.current.forEach((url) => URL.revokeObjectURL(url));
      objectPreviewUrlsRef.current = nextFilePreviewUrls;

      let fileIdx = 0;
      let urlIdx = 0;
      const nextPreviewById: Record<string, string> = {};
      result.predictions.forEach((item) => {
        if (item.source_type === "file") {
          nextPreviewById[item.id] = nextFilePreviewUrls[fileIdx] || "";
          fileIdx += 1;
          return;
        }

        nextPreviewById[item.id] = confirmedUrls[urlIdx] || item.source_name;
        urlIdx += 1;
      });

      setPredictions(result.predictions);
      setPreviewByPredictionId(nextPreviewById);
    } catch (err) {
      nextFilePreviewUrls.forEach((url) => URL.revokeObjectURL(url));
      setError(err instanceof Error ? err.message : "Prediction failed");
    } finally {
      setLoading(false);
    }
  }

  function onConfirmUrls() {
    setConfirmedUrls(validUrls);
    if (validUrls.length === 0) {
      setError("No valid URL lines found to confirm.");
      return;
    }
    setError(null);
  }

  async function onDownloadCsv() {
    try {
      const blob = await downloadCsv(predictions, aiAdviceById);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "analysis_report.csv";
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "CSV download failed");
    }
  }

  async function onAskAi(item: PredictionItem) {
    setAiLoadingById((prev) => ({ ...prev, [item.id]: true }));
    setAiErrorById((prev) => ({ ...prev, [item.id]: "" }));

    try {
      const response = await fetchAiDiagnosis(item);
      setAiAdviceById((prev) => ({ ...prev, [item.id]: response }));
    } catch (err) {
      setAiErrorById((prev) => ({
        ...prev,
        [item.id]: err instanceof Error ? err.message : "AI diagnosis failed",
      }));
    } finally {
      setAiLoadingById((prev) => ({ ...prev, [item.id]: false }));
    }
  }

  return (
    <section className="panel">
      <div className="page-hero detector-hero">
        <p className="page-kicker">Inference Console</p>
        <div className="hero-title-row">
          <span className="hero-glyph">D</span>
          <h2>Plant Disease Detector</h2>
        </div>
        <p>
          Upload multiple images, paste URL lines, then run prediction. RGB conversion is applied automatically when needed.
        </p>
        <div className="hero-chip-list">
          <span className="hero-chip">Batch Upload</span>
          <span className="hero-chip">URL Ingestion</span>
          <span className="hero-chip">CSV Report</span>
        </div>
      </div>

      <p className="alert warning">
        The client is interested in identifying whether a plant image is Healthy, Powdery, or Rust.
      </p>

      <p>
        You can download a test image set for live prediction from{" "}
        <a href="https://www.kaggle.com/datasets/rashikrahmanpritom/plant-disease-recognition-dataset?select=Test" target="_blank" rel="noreferrer">
          Kaggle Test Images
        </a>
        .
      </p>

      <div className="form-grid page-card">
        <label className="field">
          <span>Upload image files</span>
          <input
            type="file"
            accept="image/png,image/jpeg,image/webp"
            multiple
            onChange={(e) => setFiles(Array.from(e.target.files || []))}
          />
        </label>

        <label className="field">
          <span>Image URLs (one per line)</span>
          <textarea
            rows={6}
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="https://example.com/leaf-1.jpg"
          />
        </label>
      </div>

      <div className="actions">
        <button onClick={onConfirmUrls} disabled={loading}>
          Confirm URLs
        </button>
        <button onClick={onPredict} disabled={loading}>
          {loading ? "Predicting..." : "Predict"}
        </button>
      </div>

      {confirmedUrls.length > 0 ? (
        <p className="alert">Confirmed URLs: {confirmedUrls.length}</p>
      ) : null}

      {error ? <p className="alert error">{error}</p> : null}

      {predictions.length > 0 ? (
        <div className="results cards-stagger">
          {predictions.map((item) => (
            <article className="result-card" key={item.id}>
              <h3>{item.source_name}</h3>
              <p>
                <strong>Prediction:</strong> {item.predicted_class || "Failed"}
              </p>
              {item.rgb_converted ? (
                <p className="alert warning">Source image was converted to RGB.</p>
              ) : null}
              {item.treatment_suggestion ? (
                <p>
                  <strong>Treatment:</strong> {item.treatment_suggestion}
                </p>
              ) : null}
              {item.errors.length > 0 ? <p className="alert error">{item.errors.join(" | ")}</p> : null}

              <div className="result-visual-row">
                {previewByPredictionId[item.id] ? (
                  <div className="result-image-wrap">
                    <img
                      className="result-image"
                      src={previewByPredictionId[item.id]}
                      alt={`Input image: ${item.source_name}`}
                      loading="lazy"
                    />
                  </div>
                ) : null}
                <div className="probability-wheel-wrap">
                  <div className="probability-wheel" style={{ background: conicChartStyle(item) }} aria-hidden="true">
                    <div className="probability-wheel-center">Probabilities</div>
                  </div>
                  <div className="probability-legend">
                    <span><i className="legend-dot healthy" />Healthy</span>
                    <span><i className="legend-dot powdery" />Powdery</span>
                    <span><i className="legend-dot rust" />Rust</span>
                  </div>
                </div>
              </div>

              <table className="data-table">
                <thead>
                  <tr>
                    <th>Class</th>
                    <th>Prediction Probability</th>
                  </tr>
                </thead>
                <tbody>
                  {classes.map((label) => (
                    <tr key={label}>
                      <td>{label}</td>
                      <td>{score(item.probabilities[label])}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="actions" style={{ marginTop: "10px" }}>
                <button onClick={() => onAskAi(item)} disabled={aiLoadingById[item.id] || !!item.errors.length}>
                  {aiLoadingById[item.id] ? "Thinking..." : "Get AI Diagnosis (GPT-4.1)"}
                </button>
              </div>

              {aiErrorById[item.id] ? <p className="alert error">{aiErrorById[item.id]}</p> : null}

              {aiAdviceById[item.id] ? (
                (() => {
                  const ai = aiAdviceById[item.id];
                  return (
                    <div className="ai-advice-box">
                      <div className="ai-advice-top">
                        <p className="ai-advice-head">AI Assistant</p>
                        <span className="ai-model-pill">{ai.model}</span>
                      </div>
                      <div className="ai-sections-grid">
                        <section className="ai-section-card">
                          <h4>Diagnosis</h4>
                          <ReactMarkdown>{ai.diagnosis || "Not provided."}</ReactMarkdown>
                        </section>

                        <section className="ai-section-card">
                          <h4>Why</h4>
                          <ReactMarkdown>{ai.why || "Not provided."}</ReactMarkdown>
                        </section>

                        <section className="ai-section-card">
                          <h4>Immediate Actions</h4>
                          {ai.immediate_actions.length > 0 ? (
                            <ul>
                              {ai.immediate_actions.map((action) => (
                                <li key={action}>{action}</li>
                              ))}
                            </ul>
                          ) : (
                            <p>Not provided.</p>
                          )}
                        </section>

                        <section className="ai-section-card">
                          <h4>Prevention</h4>
                          {ai.prevention.length > 0 ? (
                            <ul>
                              {ai.prevention.map((itemText) => (
                                <li key={itemText}>{itemText}</li>
                              ))}
                            </ul>
                          ) : (
                            <p>Not provided.</p>
                          )}
                        </section>
                      </div>
                    </div>
                  );
                })()
              ) : null}
            </article>
          ))}
        </div>
      ) : null}

      {predictions.length > 0 ? (
        <section className="table-showcase" style={{ marginTop: "16px" }}>
          <h3>Analysis Report</h3>
          <div className="report-table-wrap">
            <table className="data-table analysis-report-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Diagnosis</th>
                  <th>Why</th>
                  <th>Immediate Actions</th>
                  <th>Prevention</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((item) => {
                  const ai = aiAdviceById[item.id];
                  const isAiLoading = aiLoadingById[item.id];
                  return (
                    <tr key={`report-${item.id}`}>
                      <td className="report-name-cell">{item.source_name}</td>
                      <td>{isAiLoading ? <span className="ai-loading-inline">…</span> : ai ? ai.diagnosis : "—"}</td>
                      <td>{isAiLoading ? <span className="ai-loading-inline">…</span> : ai ? ai.why : "—"}</td>
                      <td>
                        {isAiLoading ? (
                          <span className="ai-loading-inline">…</span>
                        ) : ai && ai.immediate_actions.length > 0 ? (
                          <ul className="report-ai-list">
                            {ai.immediate_actions.map((a) => (
                              <li key={a}>{a}</li>
                            ))}
                          </ul>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        {isAiLoading ? (
                          <span className="ai-loading-inline">…</span>
                        ) : ai && ai.prevention.length > 0 ? (
                          <ul className="report-ai-list">
                            {ai.prevention.map((p) => (
                              <li key={p}>{p}</li>
                            ))}
                          </ul>
                        ) : (
                          "—"
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="actions" style={{ marginTop: "12px" }}>
            <button onClick={onDownloadCsv} disabled={!predictions.length || loading}>
              Download CSV
            </button>
          </div>
        </section>
      ) : null}
    </section>
  );
}
