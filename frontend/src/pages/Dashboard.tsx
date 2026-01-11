import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import { DashboardStats, PriceAlert } from '../types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentAlerts, setRecentAlerts] = useState<PriceAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, alertsRes] = await Promise.all([
        dashboardAPI.getStats(),
        dashboardAPI.getRecentAlerts(),
      ]);
      setStats(statsRes.data);
      setRecentAlerts(alertsRes.data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Overview of your price monitoring system</p>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total Products</div>
            <div className="stat-value">{stats.total_products}</div>
            <div className="stat-change positive">
              {stats.active_products} active
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Total Sources</div>
            <div className="stat-value">{stats.total_sources}</div>
            <div className="stat-change positive">
              {stats.active_sources} active
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Price Checks Today</div>
            <div className="stat-value">{stats.total_price_checks_today}</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Average Price Change</div>
            <div className="stat-value">
              {stats.average_price_change.toFixed(2)}%
            </div>
            <div
              className={`stat-change ${
                stats.average_price_change >= 0 ? 'positive' : 'negative'
              }`}
            >
              {stats.products_with_price_drop} drops, {stats.products_with_price_increase} increases
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recent Price Alerts</h2>
        </div>
        {recentAlerts.length === 0 ? (
          <p>No recent price alerts</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Source</th>
                <th>Old Price</th>
                <th>New Price</th>
                <th>Change</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {recentAlerts.map((alert, index) => (
                <tr key={index}>
                  <td>{alert.product_name}</td>
                  <td>{alert.source_name}</td>
                  <td>{alert.old_price} PLN</td>
                  <td>{alert.new_price} PLN</td>
                  <td>
                    <span
                      className={`badge ${
                        alert.change_percent < 0 ? 'badge-success' : 'badge-danger'
                      }`}
                    >
                      {alert.change_percent > 0 ? '+' : ''}
                      {alert.change_percent.toFixed(2)}%
                    </span>
                  </td>
                  <td>{format(new Date(alert.checked_at), 'yyyy-MM-dd HH:mm')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
