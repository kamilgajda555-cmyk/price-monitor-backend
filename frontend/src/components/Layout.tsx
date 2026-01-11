import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
  onLogout: () => void;
}

const Layout: React.FC<LayoutProps> = ({ children, onLogout }) => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-header">
          📊 Price Monitor
        </div>
        <nav>
          <ul className="sidebar-nav">
            <li>
              <Link to="/" className={isActive('/')}>
                🏠 Dashboard
              </Link>
            </li>
            <li>
              <Link to="/products" className={isActive('/products')}>
                📦 Products
              </Link>
            </li>
            <li>
              <Link to="/sources" className={isActive('/sources')}>
                🔗 Sources
              </Link>
            </li>
            <li>
              <Link to="/alerts" className={isActive('/alerts')}>
                🔔 Alerts
              </Link>
            </li>
            <li>
              <Link to="/reports" className={isActive('/reports')}>
                📄 Reports
              </Link>
            </li>
          </ul>
        </nav>
        <div className="sidebar-footer">
          <button className="logout-btn" onClick={onLogout}>
            Logout
          </button>
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
};

export default Layout;
