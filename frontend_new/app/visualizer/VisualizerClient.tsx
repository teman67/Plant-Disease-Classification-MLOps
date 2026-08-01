"use client";

import Image from "next/image";
import { useState } from "react";
import { API_BASE_URL } from "@/lib/api";

const labels = ["Healthy", "Powdery", "Rust"] as const;

export default function VisualizerClient() {
  const [showHealthyPowdery, setShowHealthyPowdery] = useState(false);
  const [showHealthyRust, setShowHealthyRust] = useState(false);
  const [showDiffHealthyPowdery, setShowDiffHealthyPowdery] = useState(false);
  const [showDiffHealthyRust, setShowDiffHealthyRust] = useState(false);
  const [showMontage, setShowMontage] = useState(false);
  const [selectedLabel, setSelectedLabel] = useState<(typeof labels)[number]>("Healthy");
  const [montageNonce, setMontageNonce] = useState<number | null>(null);

  return (
    <section className="panel">
      <div className="page-hero visualizer-hero">
        <p className="page-kicker">Visual Analytics</p>
        <div className="hero-title-row">
          <span className="hero-glyph">V</span>
          <h2>Plant Image Visualizer</h2>
        </div>
        <p>Study visual differences between healthy and diseased leaves, then generate a class montage.</p>
        <div className="hero-chip-list">
          <span className="hero-chip">Average and Variability</span>
          <span className="hero-chip">Average Difference</span>
          <span className="hero-chip">Image Montage</span>
        </div>
      </div>

      <div className="visualizer-controls page-card">
        <label className="check-row">
          <input type="checkbox" checked={showHealthyPowdery} onChange={(e) => setShowHealthyPowdery(e.target.checked)} />
          <span>Difference between average and variability image; Healthy vs. Powdery</span>
        </label>

        <label className="check-row">
          <input type="checkbox" checked={showHealthyRust} onChange={(e) => setShowHealthyRust(e.target.checked)} />
          <span>Difference between average and variability image; Healthy vs. Rust</span>
        </label>

        <label className="check-row">
          <input
            type="checkbox"
            checked={showDiffHealthyPowdery}
            onChange={(e) => setShowDiffHealthyPowdery(e.target.checked)}
          />
          <span>Differences between average healthy and average powdery plants</span>
        </label>

        <label className="check-row">
          <input type="checkbox" checked={showDiffHealthyRust} onChange={(e) => setShowDiffHealthyRust(e.target.checked)} />
          <span>Differences between average healthy and average rust plants</span>
        </label>

        <label className="check-row">
          <input type="checkbox" checked={showMontage} onChange={(e) => setShowMontage(e.target.checked)} />
          <span>Image Montage</span>
        </label>
      </div>

      {showHealthyPowdery ? (
        <section className="visualizer-block cards-stagger">
          <p className="alert warning">
            We notice the average and variability images did not show patterns where we could intuitively differentiate one from another. However, a small difference in colour pigment is visible.
          </p>
          <div className="asset-grid">
            <figure className="asset-card page-card">
              <Image
                src={`${API_BASE_URL}/static/v1/avg_var_Healthy.png`}
                alt="Healthy Plant - Average and Variability"
                width={900}
                height={560}
                style={{ width: "100%", height: "auto" }}
              />
              <figcaption style={{ padding: "8px" }}>Healthy Plant - Average and Variability</figcaption>
            </figure>
            <figure className="asset-card page-card">
              <Image
                src={`${API_BASE_URL}/static/v1/avg_var_Powdery.png`}
                alt="Powdery Plant - Average and Variability"
                width={900}
                height={560}
                style={{ width: "100%", height: "auto" }}
              />
              <figcaption style={{ padding: "8px" }}>Powdery Plant - Average and Variability</figcaption>
            </figure>
          </div>
        </section>
      ) : null}

      {showHealthyRust ? (
        <section className="visualizer-block cards-stagger">
          <p className="alert warning">
            We notice the average and variability images did not show patterns where we could intuitively differentiate one from another. However, a small difference in colour pigment is visible.
          </p>
          <div className="asset-grid">
            <figure className="asset-card page-card">
              <Image
                src={`${API_BASE_URL}/static/v1/avg_var_Healthy.png`}
                alt="Healthy Plant - Average and Variability"
                width={900}
                height={560}
                style={{ width: "100%", height: "auto" }}
              />
              <figcaption style={{ padding: "8px" }}>Healthy Plant - Average and Variability</figcaption>
            </figure>
            <figure className="asset-card page-card">
              <Image
                src={`${API_BASE_URL}/static/v1/avg_var_Rust.png`}
                alt="Rust Plant - Average and Variability"
                width={900}
                height={560}
                style={{ width: "100%", height: "auto" }}
              />
              <figcaption style={{ padding: "8px" }}>Rust Plant - Average and Variability</figcaption>
            </figure>
          </div>
        </section>
      ) : null}

      {showDiffHealthyPowdery ? (
        <section className="visualizer-block cards-stagger">
          <p className="alert warning">
            We notice this study did not show patterns where we could intuitively differentiate one from another.
          </p>
          <figure className="asset-card page-card">
            <Image
              src={`${API_BASE_URL}/static/v1/avg_diff_label1_label2.png`}
              alt="Difference between average healthy and average powdery"
              width={900}
              height={560}
              style={{ width: "100%", height: "auto" }}
            />
            <figcaption style={{ padding: "8px" }}>Difference between average images</figcaption>
          </figure>
        </section>
      ) : null}

      {showDiffHealthyRust ? (
        <section className="visualizer-block cards-stagger">
          <p className="alert warning">
            We notice this study did not show patterns where we could intuitively differentiate one from another.
          </p>
          <figure className="asset-card page-card">
            <Image
              src={`${API_BASE_URL}/static/v1/avg_diff_label1_label3.png`}
              alt="Difference between average healthy and average rust"
              width={900}
              height={560}
              style={{ width: "100%", height: "auto" }}
            />
            <figcaption style={{ padding: "8px" }}>Difference between average images</figcaption>
          </figure>
        </section>
      ) : null}

      {showMontage ? (
        <section className="visualizer-block page-card">
          <p>To refresh the montage, click on the Create Montage button.</p>
          <div className="actions">
            <select value={selectedLabel} onChange={(e) => setSelectedLabel(e.target.value as (typeof labels)[number])}>
              {labels.map((label) => (
                <option key={label} value={label}>
                  {label}
                </option>
              ))}
            </select>
            <button onClick={() => setMontageNonce(Date.now())}>Create Montage</button>
          </div>

          {montageNonce ? (
            <figure className="asset-card page-card" style={{ marginTop: "12px" }}>
              <Image
                src={`${API_BASE_URL}/api/v1/visualizer/montage?label=${selectedLabel}&rows=9&cols=3&r=${montageNonce}`}
                alt={`${selectedLabel} montage`}
                width={760}
                height={1900}
                style={{ width: "100%", height: "auto" }}
              />
              <figcaption style={{ padding: "8px" }}>{selectedLabel} montage</figcaption>
            </figure>
          ) : null}
        </section>
      ) : null}
    </section>
  );
}
