import Spinner from "./Spinner";

export const BACKEND_WAKE_HINT =
  "The backend is hosted on Heroku and may take up to a minute to wake up on the first request. Please keep this page open.";

type LoadingStateProps = {
  title: string;
  hint?: string;
};

export default function LoadingState({ title, hint = BACKEND_WAKE_HINT }: LoadingStateProps) {
  return (
    <div className="loading-state" role="status" aria-live="polite">
      <Spinner size={28} />
      <div className="loading-state-text">
        <p className="loading-state-title">{title}</p>
        <p className="loading-state-hint">{hint}</p>
      </div>
    </div>
  );
}
