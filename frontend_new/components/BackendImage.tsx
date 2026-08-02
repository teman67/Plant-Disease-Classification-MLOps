"use client";

import Image, { ImageProps } from "next/image";
import { useState } from "react";
import Spinner from "./Spinner";

type BackendImageProps = ImageProps & {
  loadingLabel?: string;
  loadingHint?: string;
};

export default function BackendImage({
  loadingLabel = "Loading image from the backend...",
  loadingHint = "First load can be slow while the server wakes up.",
  alt,
  onLoad,
  onError,
  ...imageProps
}: BackendImageProps) {
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [trackedSrc, setTrackedSrc] = useState(imageProps.src);

  // A new src (for example a freshly requested montage) starts a new load.
  if (trackedSrc !== imageProps.src) {
    setTrackedSrc(imageProps.src);
    setStatus("loading");
  }

  return (
    <div className={`backend-image is-${status}`}>
      {status === "loading" ? (
        <div className="backend-image-status" role="status" aria-live="polite">
          <Spinner size={26} />
          <span className="backend-image-label">{loadingLabel}</span>
          <span className="backend-image-hint">{loadingHint}</span>
        </div>
      ) : null}

      {status === "error" ? (
        <div className="backend-image-status" role="status" aria-live="polite">
          <span className="backend-image-label">Image could not be loaded from the backend.</span>
          <span className="backend-image-hint">The server may still be starting up. Please try again.</span>
        </div>
      ) : null}

      <Image
        loading="eager"
        {...imageProps}
        alt={alt}
        onLoad={(event) => {
          setStatus("ready");
          onLoad?.(event);
        }}
        onError={(event) => {
          setStatus("error");
          onError?.(event);
        }}
      />
    </div>
  );
}
