import type { ReactNode } from "react";
import { X } from "lucide-react";
import styles from "./Toast.module.css";

export type ToastVariant = "success" | "info" | "warning" | "attention";

type Props = {
  variant: ToastVariant;
  title?: string;
  children: ReactNode;
  onDismiss?: () => void;
  "aria-label"?: string;
};

const variantClass: Record<ToastVariant, string> = {
  success: styles.success,
  info: styles.info,
  warning: styles.warning,
  attention: styles.attention,
};

export function Toast({ variant, title, children, onDismiss, "aria-label": ariaLabel }: Props) {
  return (
    <div
      role="alert"
      aria-label={ariaLabel ?? title ?? "Notification"}
      className={`${styles.toast} ${variantClass[variant]}`}
    >
      <div className={styles.content}>
        {title && <strong className={styles.title}>{title}</strong>}
        <span className={styles.body}>{children}</span>
      </div>
      {onDismiss && (
        <button
          type="button"
          className={styles.dismiss}
          onClick={onDismiss}
          aria-label="Dismiss notification"
        >
          <X size={16} strokeWidth={1.8} />
        </button>
      )}
    </div>
  );
}
