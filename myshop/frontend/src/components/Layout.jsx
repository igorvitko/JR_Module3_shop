import { Outlet } from "react-router-dom";

import Footer from "./Footer";
import Header from "./Header";

export default function Layout() {
  return (
    <div className="page-shell">
      <Header />
      <main className="page-content">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
