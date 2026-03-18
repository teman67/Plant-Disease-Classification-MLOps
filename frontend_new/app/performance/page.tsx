import Image from "next/image";
import { API_BASE_URL, fetchPerformance } from "@/lib/api";
import { PerformanceResponse } from "@/lib/types";

const classLabels = ["Healthy", "Powdery", "Rust"];

function asPercent(value: number | undefined): string {
  if (value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return `${(value * 100).toFixed(2)}%`;
}

export default async function PerformancePage() {
  let errorText = "";
  let payload: PerformanceResponse | null = null;

  try {
    payload = await fetchPerformance();
  } catch (error) {
    errorText = error instanceof Error ? error.message : "Failed to load performance data";
  }

  const testLoss = payload?.evaluation?.loss ?? undefined;
  const testAccuracy = payload?.evaluation?.accuracy ?? undefined;

  const confusion = payload?.confusion_matrix || [];
  const metrics = payload?.metrics || {};

  return (
    <section className="panel">
      <div className="page-hero performance-hero">
        <p className="page-kicker">Model Audit</p>
        <div className="hero-title-row">
          <span className="hero-glyph">P</span>
          <h2>Machine Learning Performance</h2>
        </div>
        <p>Train/validation behavior and test-set performance, aligned with the original Streamlit analysis.</p>
        <div className="hero-chip-list">
          <span className="hero-chip">Accuracy and Loss</span>
          <span className="hero-chip">Confusion Matrix</span>
          <span className="hero-chip">Metrics Table</span>
        </div>
      </div>

      {errorText ? <p className="alert error">{errorText}</p> : null}

      <h3 className="section-title">Train, Validation and Test Set: Labels Frequencies</h3>
      <p>
        Dataset has Healthy, Powdery, and Rust leaves split into Train (70%), Validation (10%), and Test (20%).
      </p>
      <figure className="perf-showcase perf-showcase-lg cards-stagger" style={{ marginBottom: "14px" }}>
        <div className="perf-image-wrap perf-image-wrap-lg">
          <Image
            src={`${API_BASE_URL}/static/v1/labels_distribution.png`}
            alt="Labels distribution"
            width={1100}
            height={560}
            style={{ width: "100%", height: "auto" }}
          />
        </div>
        <figcaption className="perf-caption">Label frequencies across train, validation, and test splits</figcaption>
      </figure>

      <h3 className="section-title">Model History</h3>
      <p>
        Accuracy and loss trends suggest a stable fit, with train and validation curves following similar patterns.
      </p>
      <div className="perf-history-grid cards-stagger">
        <figure className="perf-showcase">
          <div className="perf-image-wrap perf-image-wrap-sm">
            <Image
              src={`${API_BASE_URL}/static/v1/model_training_acc.png`}
              alt="Model training accuracy"
              width={900}
              height={520}
              style={{ width: "100%", height: "auto" }}
            />
          </div>
          <figcaption className="perf-caption">Training vs validation accuracy trend</figcaption>
        </figure>
        <figure className="perf-showcase">
          <div className="perf-image-wrap perf-image-wrap-sm">
            <Image
              src={`${API_BASE_URL}/static/v1/model_training_losses.png`}
              alt="Model training losses"
              width={900}
              height={520}
              style={{ width: "100%", height: "auto" }}
            />
          </div>
          <figcaption className="perf-caption">Training vs validation loss trend</figcaption>
        </figure>
      </div>

      <h3 className="section-title">Generalised Performance on Test Set</h3>
      <div className="table-showcase cards-stagger">
        <table className="data-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Loss</td>
              <td>{testLoss !== undefined ? testLoss.toFixed(4) : "-"}</td>
            </tr>
            <tr>
              <td>Accuracy</td>
              <td>{asPercent(testAccuracy)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3 className="section-title">Confusion Matrix</h3>
      <figure className="perf-showcase perf-showcase-lg cards-stagger" style={{ marginBottom: "12px" }}>
        <div className="perf-image-wrap perf-image-wrap-lg">
          <Image
            src={`${API_BASE_URL}/static/v2/confusion_matrix.png`}
            alt="Confusion matrix plot"
            width={900}
            height={600}
            style={{ width: "100%", height: "auto" }}
          />
        </div>
        <figcaption className="perf-caption">Confusion matrix highlighting true and false predictions</figcaption>
      </figure>

      <div className="table-showcase cards-stagger">
        <table className="data-table">
          <thead>
            <tr>
              <th>Actual \ Predicted</th>
              {classLabels.map((label) => (
                <th key={label}>{label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {classLabels.map((actual, rowIndex) => (
              <tr key={actual}>
                <td className="row-label">{actual}</td>
                {classLabels.map((predicted, colIndex) => (
                  <td key={`${actual}-${predicted}`}>{confusion[rowIndex]?.[colIndex] ?? "-"}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3 className="section-title">Model Evaluation Metrics</h3>
      <div className="table-showcase cards-stagger">
        <table className="data-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(metrics).map(([key, value]) => (
              <tr key={key}>
                <td>{key}</td>
                <td>
                  {typeof value === "number" ? value.toFixed(4) : String(value)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="alert warning" style={{ marginTop: "16px" }}>
        Conclusion: the model maintains strong test performance around the 95% target while preserving disease treatment recommendations in the detector flow.
      </p>
    </section>
  );
}
