import { Calendar } from "lucide-react";
import styles from "./LeftRail.module.css";

const quickStats = [
  { label: "Today", value: "12", sub: "deliveries" },
  { label: "In transit", value: "2", sub: "active" },
  { label: "Completed", value: "8", sub: "so far" },
];

export function LeftRail() {
  return (
    <aside className={styles.rail} aria-label="Filters and quick stats">
      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>Date range</h3>
        <div className={styles.dateChip}>
          <Calendar size={16} strokeWidth={1.8} aria-hidden />
          <span>Today</span>
        </div>
      </section>
      <span className="flow-divider" role="presentation" />
      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>Quick stats</h3>
        <div className={styles.stats}>
          {quickStats.map((s) => (
            <div key={s.label} className={styles.stat}>
              <span className={styles.statValue}>{s.value}</span>
              <span className={styles.statLabel}>{s.label}</span>
              <span className={styles.statSub}>{s.sub}</span>
            </div>
          ))}
        </div>
      </section>
      <span className="flow-divider" role="presentation" />
      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>Filters</h3>
        <div className={styles.filterChips}>
          <button type="button" className={styles.filterChipActive}>
            All
          </button>
          <button type="button" className={styles.filterChip}>
            In transit
          </button>
          <button type="button" className={styles.filterChip}>
            Pending
          </button>
        </div>
      </section>
    </aside>
  );
}
