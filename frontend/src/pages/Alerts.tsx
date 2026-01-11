import React, { useState, useEffect } from 'react';
import { alertsAPI, productsAPI } from '../services/api';
import { Alert, Product } from '../types';

const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newAlert, setNewAlert] = useState({
    product_id: '',
    alert_type: 'price_drop',
    threshold: '',
    percentage: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [alertsRes, productsRes] = await Promise.all([
        alertsAPI.getAll(),
        productsAPI.getAll({ limit: 1000 }),
      ]);
      setAlerts(alertsRes.data);
      setProducts(productsRes.data);
    } catch (error) {
      console.error('Error loading alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const condition: any = {};
      if (newAlert.threshold) {
        condition.threshold = parseFloat(newAlert.threshold);
      }
      if (newAlert.percentage) {
        condition.percentage = parseFloat(newAlert.percentage);
      }

      await alertsAPI.create({
        product_id: parseInt(newAlert.product_id) || undefined,
        alert_type: newAlert.alert_type,
        condition,
        is_active: true,
      });
      setShowAddModal(false);
      setNewAlert({ product_id: '', alert_type: 'price_drop', threshold: '', percentage: '' });
      loadData();
    } catch (error) {
      console.error('Error adding alert:', error);
    }
  };

  const handleDeleteAlert = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this alert?')) {
      try {
        await alertsAPI.delete(id);
        loadData();
      } catch (error) {
        console.error('Error deleting alert:', error);
      }
    }
  };

  const handleToggleAlert = async (alert: Alert) => {
    try {
      await alertsAPI.update(alert.id, { is_active: !alert.is_active });
      loadData();
    } catch (error) {
      console.error('Error updating alert:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading alerts...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Alerts</h1>
        <p className="page-subtitle">Manage price alerts and notifications</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">All Alerts</h2>
          <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
            + Add Alert
          </button>
        </div>

        {alerts.length === 0 ? (
          <p>No alerts configured</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Type</th>
                <th>Condition</th>
                <th>Status</th>
                <th>Last Triggered</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((alert) => {
                const product = products.find((p) => p.id === alert.product_id);
                return (
                  <tr key={alert.id}>
                    <td>{product?.name || 'All Products'}</td>
                    <td>
                      <span className="badge badge-info">
                        {alert.alert_type.replace('_', ' ')}
                      </span>
                    </td>
                    <td>
                      {alert.condition.threshold && `Threshold: ${alert.condition.threshold} PLN`}
                      {alert.condition.percentage && `Change: ${alert.condition.percentage}%`}
                    </td>
                    <td>
                      <button
                        onClick={() => handleToggleAlert(alert)}
                        className={`badge ${alert.is_active ? 'badge-success' : 'badge-danger'}`}
                        style={{ cursor: 'pointer', border: 'none' }}
                      >
                        {alert.is_active ? 'Active' : 'Inactive'}
                      </button>
                    </td>
                    <td>
                      {alert.last_triggered
                        ? new Date(alert.last_triggered).toLocaleDateString()
                        : 'Never'}
                    </td>
                    <td>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDeleteAlert(alert.id)}
                        style={{ padding: '5px 10px', fontSize: '12px' }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {showAddModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000,
          }}
        >
          <div
            style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '30px',
              width: '500px',
            }}
          >
            <h2 style={{ marginBottom: '20px' }}>Add New Alert</h2>
            <form onSubmit={handleAddAlert}>
              <div className="form-group">
                <label className="form-label">Product</label>
                <select
                  className="form-control"
                  value={newAlert.product_id}
                  onChange={(e) => setNewAlert({ ...newAlert, product_id: e.target.value })}
                >
                  <option value="">All Products</option>
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Alert Type *</label>
                <select
                  className="form-control"
                  value={newAlert.alert_type}
                  onChange={(e) => setNewAlert({ ...newAlert, alert_type: e.target.value })}
                  required
                >
                  <option value="price_drop">Price Drop</option>
                  <option value="price_increase">Price Increase</option>
                  <option value="availability">Availability Change</option>
                  <option value="competitor">Competitor Price</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Price Threshold (PLN)</label>
                <input
                  type="number"
                  step="0.01"
                  className="form-control"
                  value={newAlert.threshold}
                  onChange={(e) => setNewAlert({ ...newAlert, threshold: e.target.value })}
                  placeholder="e.g. 100.00"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Percentage Change (%)</label>
                <input
                  type="number"
                  step="0.1"
                  className="form-control"
                  value={newAlert.percentage}
                  onChange={(e) => setNewAlert({ ...newAlert, percentage: e.target.value })}
                  placeholder="e.g. 10"
                />
              </div>
              <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button type="submit" className="btn btn-primary">
                  Add Alert
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Alerts;
