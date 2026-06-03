import { useState } from "react";
import { X, MapPin, User, Clock } from "lucide-react";
import { StatusPill } from "./StatusPill";
import styles from "./RightRail.module.css";

type Delivery = {
  id: string;
  ref: string;
  status: "in_transit" | "delivered" | "preparation" | "delayed";
  address: string;
  driver?: string;
  eta?: string;
};

const sample: Delivery = {
  id: "1",
  ref: "DEL-2041",
  status: "in_transit",
  address: "123 River Rd, Downtown",
  driver: "M. Costa",
  eta: "~14:20",
};

export function RightRail() {
  const [selected, setSelected] = useState<Delivery | null>(sample);

  return (
    <aside className={styles.rail} aria-label="Delivery detail">
      {selected ? (
        <div className={styles.panel}>
          <div className={styles.panelHeader}>
            <h3 className={styles.panelTitle}>Delivery detail</h3>
            <button
              type="button"
              className={styles.closeBtn}
              onClick={() => setSelected(null)}
              aria-label="Close panel"
            >
              <X size={18} strokeWidth={1.8} />
            </button>
          </div>
          <div className={styles.content}>
            <div className={styles.refRow}>
              <span className={`font-mono ${styles.ref}`}>{selected.ref}</span>
              <StatusPill status={selected.status} />
            </div>
            <div className={styles.meta}>
              <span className={styles.metaItem}>
                <MapPin size={14} strokeWidth={1.8} aria-hidden />
                {selected.address}
              </span>
              {selected.driver && (
                <span className={styles.metaItem}>
                  <User size={14} strokeWidth={1.8} aria-hidden />
                  {selected.driver}
                </span>
              )}
              {selected.eta && (
                <span className={styles.metaItem}>
                  <Clock size={14} strokeWidth={1.8} aria-hidden />
                  ETA {selected.eta}
                </span>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className={styles.empty}>
          <p className={styles.emptyText}>Select a delivery on the map or list to see details.</p>
        </div>
      )}
    </aside>
  );
}
