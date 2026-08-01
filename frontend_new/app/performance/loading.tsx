export default function PerformanceLoading() {
  return (
    <section className="panel">
      <div className="page-hero performance-hero">
        <p className="page-kicker">Model Audit</p>
        <div className="hero-title-row">
          <span className="hero-glyph">P</span>
          <h2>Machine Learning Performance</h2>
        </div>
        <p>Train/validation behavior and test-set performance, aligned with the original Streamlit analysis.</p>
      </div>

      <div className="loading-panel">
        <span className="spinner spinner-lg" role="status" aria-label="Loading" />
        <p className="loading-panel-title">Fetching performance data from the backend…</p>
        <p className="loading-panel-hint">
          If the server was asleep, this first request may time out after ~30s. If the page shows an
          error, wait a few seconds and refresh — the server will be warm by then.
        </p>
      </div>

      <div className="perf-history-grid" style={{ marginTop: "16px" }}>
        <div className="skeleton-block" style={{ height: 220 }} />
        <div className="skeleton-block" style={{ height: 220 }} />
      </div>
    </section>
  );
}
