import styles from "./ProgressStream.module.css";

type Props = {
  value: number;
  max?: number;
  label?: string;
  showLabel?: boolean;
  "aria-label"?: string;
};

export function ProgressStream({
  value,
  max = 100,
  label,
  showLabel = true,
  "aria-label": ariaLabel,
}: Props) {
  const pct = max <= 0 ? 0 : Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div className={styles.wrap} role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={max} aria-label={ariaLabel ?? label}>
      {showLabel && (label || value != null) && (
        <div className={styles.labelRow}>
          {label && <span className={styles.label}>{label}</span>}
          <span className={styles.value}>
            {typeof value === "number" && typeof max === "number" && max !== 100
              ? `${value} / ${max}`
              : `${Math.round(pct)}%`}
          </span>
        </div>
      )}
      <div className={styles.track}>
        <div
          className={styles.fill}
          style={{ width: `${pct}%` }}
        />
        <div className={styles.glow} style={{ width: `${pct}%` }} aria-hidden />
      </div>
    </div>
  );
}
