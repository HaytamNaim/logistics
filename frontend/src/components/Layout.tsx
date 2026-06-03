import { Outlet } from "react-router-dom";
import { Header } from "./Header";
import { LeftRail } from "./LeftRail";
import { RightRail } from "./RightRail";
import styles from "./Layout.module.css";

export function Layout() {
  return (
    <div className={styles.root}>
      <Header />
      <main className={styles.main} id="main-content">
        <div className={styles.garden}>
          <LeftRail />
          <div className={styles.center}>
            <Outlet />
          </div>
          <RightRail />
        </div>
      </main>
    </div>
  );
}
