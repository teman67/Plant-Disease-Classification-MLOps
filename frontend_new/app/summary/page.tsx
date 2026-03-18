const bullets = [
  "Automates healthy vs powdery vs rust detection from leaf images.",
  "Supports multi-image and multi-URL predictions with confidence scores.",
  "Delivers treatment guidance and downloadable CSV analysis reports.",
];

export default function SummaryPage() {
  return (
    <section className="panel">
      <div className="page-hero summary-hero">
        <p className="page-kicker">Orientation</p>
        <div className="hero-title-row">
          <span className="hero-glyph">S</span>
          <h2>Quick Project Summary</h2>
        </div>
        <p>
          The migrated stack keeps Streamlit feature parity while adding a cleaner UI layer and API-first backend.
        </p>
        <div className="hero-chip-list">
          <span className="hero-chip">Feature Parity</span>
          <span className="hero-chip">Next.js + FastAPI</span>
          <span className="hero-chip">TensorFlow Inference</span>
        </div>
      </div>

      <div className="summary-kpi-strip cards-stagger">
        <article className="summary-kpi">
          <p className="summary-kpi-label">Classes</p>
          <p className="summary-kpi-value">3</p>
          <p className="summary-kpi-note">Healthy, Powdery, Rust</p>
        </article>
        <article className="summary-kpi">
          <p className="summary-kpi-label">Core Routes</p>
          <p className="summary-kpi-value">5</p>
          <p className="summary-kpi-note">Summary to Performance</p>
        </article>
        <article className="summary-kpi">
          <p className="summary-kpi-label">Detector Inputs</p>
          <p className="summary-kpi-value">2</p>
          <p className="summary-kpi-note">Upload files and URLs</p>
        </article>
      </div>

      <div className="page-grid cards-stagger">
        <article className="page-card summary-card">
          <h3>Business Direction</h3>
          <ul>
            {bullets.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>

        <article className="page-card summary-card">
          <h3>Dataset Context</h3>
          <p>
            Uses the apple leaf dataset split into Train, Validation, and Test subsets with three classes: Healthy, Powdery, and Rust.
          </p>
          <p>
            Read complete project background in the {" "}
            <a className="summary-inline-link" href="https://github.com/teman67/Plant-Disease-Classification-Project" target="_blank" rel="noreferrer">
              repository README
            </a>
            .
          </p>
        </article>

        <article className="page-card summary-card">
          <h3>Architecture Snapshot</h3>
          <p>
            Frontend handles interaction and presentation. Backend handles prediction, CSV reports, metrics, and montage generation.
          </p>
        </article>

        <article className="page-card summary-card">
          <h3>Current Parity Status</h3>
          <p>
            Summary, Visualizer, Detector, Hypothesis, and Performance routes are now available in Next.js.
          </p>
        </article>
      </div>
    </section>
  );
}
