import type { ReactNode } from "react";
import styles from "./Card.module.css";

type Props = {
  children: ReactNode;
  className?: string;
  "aria-label"?: string;
};

export function Card({ children, className = "", "aria-label": ariaLabel }: Props) {
  return (
    <article
      className={`${styles.card} ${className}`.trim()}
      aria-label={ariaLabel}
    >
      {children}
    </article>
  );
}

export function CardHeader({
  title,
  action,
  className = "",
}: {
  title: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={`${styles.header} ${className}`.trim()}>
      <h3 className={styles.title}>{title}</h3>
      {action && <div className={styles.action}>{action}</div>}
    </div>
  );
}

export function CardBody({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`${styles.body} ${className}`.trim()}>{children}</div>;
}
