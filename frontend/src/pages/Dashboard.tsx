import { KPIStrip } from "../components/KPIStrip";
import { ProgressStream } from "../components/ProgressStream";
import { Card, CardHeader, CardBody } from "../components/Card";
import { StatusPill } from "../components/StatusPill";
import { MapPin, User, Clock } from "lucide-react";
import styles from "./Dashboard.module.css";

const kpiItems = [
  { label: "Deliveries today", value: "12", positive: true },
  { label: "In transit", value: "2" },
  { label: "Completed", value: "8", positive: true, bar: 67 },
  { label: "Delayed", value: "0", bar: 0 },
];

const deliveries = [
  { id: "1", ref: "DEL-2041", status: "in_transit" as const, address: "123 River Rd", driver: "M. Costa", time: "14:20" },
  { id: "2", ref: "DEL-2040", status: "delivered" as const, address: "45 Oak Lane", driver: "M. Costa", time: "13:55" },
  { id: "3", ref: "DEL-2039", status: "preparation" as const, address: "78 Hill St", driver: undefined, time: "15:00" },
];

export function Dashboard() {
  return (
    <>
      <div className={styles.top}>
        <h1 className={styles.pageTitle}>Dashboard</h1>
        <p className={styles.pageSubtitle}>Today’s deliveries at a glance</p>
      </div>

      <KPIStrip items={kpiItems} />

      <ProgressStream value={8} max={12} label="Day progress" aria-label="8 of 12 deliveries completed" />

      <div className={styles.grid}>
        <Card className={styles.mapCard} aria-label="Map view">
          <CardHeader title="Live map" />
          <CardBody>
            <div className={styles.mapPlaceholder} aria-hidden>
              <div className={styles.mapTexture} />
              <span className={styles.mapHint}>Map area — terrain or hybrid style</span>
              <div className={styles.mapMarkers}>
                <span className={styles.marker} data-status="in_transit" />
                <span className={styles.marker} data-status="delivered" />
                <span className={styles.marker} data-status="preparation" />
              </div>
            </div>
          </CardBody>
        </Card>

        <Card className={styles.listCard} aria-label="Recent deliveries">
          <CardHeader title="Recent deliveries" />
          <CardBody>
            <ul className={styles.list} role="list">
              {deliveries.map((d) => (
                <li key={d.id} className={styles.listItem}>
                  <div className={styles.itemLeft}>
                    <span className={`font-mono ${styles.ref}`}>{d.ref}</span>
                    <StatusPill status={d.status} />
                  </div>
                  <div className={styles.itemMeta}>
                    <span className={styles.metaLine}>
                      <MapPin size={12} strokeWidth={1.8} aria-hidden />
                      {d.address}
                    </span>
                    {d.driver && (
                      <span className={styles.metaLine}>
                        <User size={12} strokeWidth={1.8} aria-hidden />
                        {d.driver}
                      </span>
                    )}
                  </div>
                  <span className={styles.time}>
                    <Clock size={12} strokeWidth={1.8} aria-hidden />
                    {d.time}
                  </span>
                </li>
              ))}
            </ul>
          </CardBody>
        </Card>
      </div>
    </>
  );
}
