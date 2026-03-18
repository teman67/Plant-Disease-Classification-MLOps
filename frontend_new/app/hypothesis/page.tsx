export default function HypothesisPage() {
  return (
    <section className="panel">
      <div className="hypothesis-hero">
        <p className="hypothesis-kicker">Reasoning Layer</p>
        <div className="hero-title-row">
          <span className="hero-glyph">H</span>
          <h2>Project Hypothesis and Validation</h2>
        </div>
        <p>
          This section explains the core assumptions behind the disease classifier and shows how each one maps to visual analysis and model behavior.
        </p>
        <div className="hero-chip-list">
          <span className="hero-chip">Assumptions</span>
          <span className="hero-chip">Validation</span>
        </div>
      </div>

      <div className="hypothesis-grid">
        <article className="hypothesis-card">
          <p className="hypothesis-step">Hypothesis 1</p>
          <h3>Visual Distinction Exists</h3>
          <p>
            Healthy leaves and diseased leaves can be separated through average-image comparisons and montage exploration.
          </p>
          <span className="hypothesis-status">Validated by visualizer assets</span>
        </article>

        <article className="hypothesis-card">
          <p className="hypothesis-step">Hypothesis 2</p>
          <h3>Classifier Can Reach High Accuracy</h3>
          <p>
            A CNN can achieve strong multi-class prediction performance for Healthy, Powdery, and Rust labels.
          </p>
          <span className="hypothesis-status">Validated by test metrics near 95%</span>
        </article>

        <article className="hypothesis-card">
          <p className="hypothesis-step">Hypothesis 3</p>
          <h3>Background Shift Impacts Reliability</h3>
          <p>
            Different image backgrounds may reduce model confidence and classification stability.
          </p>
          <span className="hypothesis-status">Monitored during live detector usage</span>
        </article>

        <article className="hypothesis-card">
          <p className="hypothesis-step">Hypothesis 4</p>
          <h3>RGB Input Improves Consistency</h3>
          <p>
            RGB images are preferred for inference; non-RGB samples should be converted automatically before prediction.
          </p>
          <span className="hypothesis-status">Enforced in backend preprocessing</span>
        </article>
      </div>

      <div className="hypothesis-summary">
        <h3>Outcome Summary</h3>
        <ul>
          <li>Visualizer confirms meaningful visual class differences.</li>
          <li>Performance metrics support strong generalization on test data.</li>
          <li>Detector flow preserves practical recommendations for disease handling.</li>
        </ul>
      </div>
    </section>
  );
}
