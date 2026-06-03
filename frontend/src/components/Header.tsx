import { Link, useLocation } from "react-router-dom";
import { Package, MapPin, Route, Truck, BarChart3, Bell, User } from "lucide-react";
import styles from "./Header.module.css";

const nav = [
  { path: "/orders", label: "Orders", icon: Package },
  { path: "/deliveries", label: "Deliveries", icon: MapPin },
  { path: "/routes", label: "Routes", icon: Route },
  { path: "/fleet", label: "Fleet", icon: Truck },
  { path: "/analytics", label: "Analytics", icon: BarChart3 },
] as const;

export function Header() {
  const location = useLocation();

  return (
    <header className={styles.header} role="banner">
      <div className={styles.brand}>
        <span className={styles.logo} aria-hidden>
          <Package size={24} strokeWidth={1.8} />
        </span>
        <span className={styles.productName}>Logistics in Harmony</span>
      </div>
      <nav className={styles.nav} aria-label="Primary">
        <ul className={styles.navList}>
          <li>
            <Link to="/dashboard" className={location.pathname === "/dashboard" ? styles.navLinkActive : styles.navLink}>
              Dashboard
            </Link>
          </li>
          {nav.map(({ path, label, icon: Icon }) => (
            <li key={path}>
              <Link to={path} className={location.pathname.startsWith(path) ? styles.navLinkActive : styles.navLink}>
                <Icon size={18} strokeWidth={1.8} aria-hidden />
                {label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      <div className={styles.actions}>
        <button type="button" className={styles.iconBtn} aria-label="Notifications">
          <Bell size={20} strokeWidth={1.8} />
        </button>
        <button type="button" className={styles.iconBtn} aria-label="Account">
          <User size={20} strokeWidth={1.8} />
        </button>
      </div>
    </header>
  );
}
