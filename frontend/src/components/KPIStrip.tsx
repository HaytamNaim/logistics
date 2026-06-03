import type { ReactNode } from "react";
import styles from "./KPIStrip.module.css";

export type KPIItem = {
  label: string;
  value: ReactNode;
  positive?: boolean;
  bar?: number;
};

type Props = { items: KPIItem[]; className?: string };

export function KPIStrip({ items, className = "" }: Props) {
  return (
    <section
      className={`${styles.strip} ${className}`.trim()}
      aria-label="Key metrics"
    >
      {items.map((item, i) => (
        <div key={i} className={styles.item}>
          <span className={styles.value} data-positive={item.positive ?? undefined}>
            {item.value}
          </span>
          <span className={styles.label}>{item.label}</span>
          {item.bar != null && (
            <div className={styles.barTrack} role="presentation">
              <div
                className={styles.barFill}
                style={{ width: `${Math.min(100, Math.max(0, item.bar))}%` }}
              />
            </div>
          )}
        </div>
      ))}
    </section>
  );
}
