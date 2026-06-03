import type { ReactNode } from "react";
import styles from "./StatusPill.module.css";

export type StatusKind =
  | "delivered"
  | "success"
  | "in_transit"
  | "info"
  | "preparation"
  | "pending"
  | "warning"
  | "delayed"
  | "attention"
  | "cancelled"
  | "inactive";

const statusConfig: Record<
  StatusKind,
  { label: string; className: string; "aria-label"?: string }
> = {
  delivered: { label: "Delivered", className: styles.success },
  success: { label: "Success", className: styles.success },
  in_transit: { label: "In transit", className: styles.info },
  info: { label: "Info", className: styles.info },
  preparation: { label: "Preparation", className: styles.warning },
  pending: { label: "Pending", className: styles.warning },
  warning: { label: "Warning", className: styles.warning },
  delayed: { label: "Delayed", className: styles.attention },
  attention: { label: "Needs attention", className: styles.attention },
  cancelled: { label: "Cancelled", className: styles.inactive },
  inactive: { label: "Inactive", className: styles.inactive },
};

type Props = { status: StatusKind; children?: ReactNode; "aria-label"?: string };

export function StatusPill({ status, children, "aria-label": ariaLabel }: Props) {
  const config = statusConfig[status] ?? statusConfig.inactive;
  const label = (children as string) ?? config.label;
  return (
    <span
      className={`${styles.pill} ${config.className}`}
      role="status"
      aria-label={ariaLabel ?? `Status: ${label}`}
    >
      {label}
    </span>
  );
}
