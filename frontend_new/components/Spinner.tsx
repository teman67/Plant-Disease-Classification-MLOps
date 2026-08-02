type SpinnerProps = {
  size?: number;
};

export default function Spinner({ size = 22 }: SpinnerProps) {
  return (
    <span
      className="spinner"
      style={{ width: `${size}px`, height: `${size}px` }}
      aria-hidden="true"
    />
  );
}
