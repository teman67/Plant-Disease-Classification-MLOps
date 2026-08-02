import LoadingState from "@/components/LoadingState";

export default function PerformanceLoading() {
  return (
    <section className="panel">
      <div className="page-hero performance-hero">
        <p className="page-kicker">Model Audit</p>
        <div className="hero-title-row">
          <span className="hero-glyph">P</span>
          <h2>Machine Learning Performance</h2>
        </div>
        <p>Fetching train/validation behavior and test-set performance from the API.</p>
      </div>

      <LoadingState title="Loading performance metrics from the backend..." />

      <div className="skeleton-stack" aria-hidden="true">
        <div className="skeleton skeleton-block" />
        <div className="skeleton-row">
          <div className="skeleton skeleton-block skeleton-block-sm" />
          <div className="skeleton skeleton-block skeleton-block-sm" />
        </div>
        <div className="skeleton skeleton-line" />
        <div className="skeleton skeleton-line" />
        <div className="skeleton skeleton-line skeleton-line-short" />
      </div>
    </section>
  );
}
