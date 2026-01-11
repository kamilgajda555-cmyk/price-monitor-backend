import React, { useState, useEffect } from 'react';
import { sourcesAPI } from '../services/api';
import { Source } from '../types';

const Sources: React.FC = () => {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newSource, setNewSource] = useState({
    name: '',
    type: 'marketplace',
    base_url: '',
    scraper_config: '{}',
  });

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    try {
      const response = await sourcesAPI.getAll();
      setSources(response.data);
    } catch (error) {
      console.error('Error loading sources:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSource = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      let config = {};
      try {
        config = JSON.parse(newSource.scraper_config);
      } catch {
        alert('Invalid JSON in scraper config');
        return;
      }

      await sourcesAPI.create({
        ...newSource,
        scraper_config: config,
      });
      setShowAddModal(false);
      setNewSource({ name: '', type: 'marketplace', base_url: '', scraper_config: '{}' });
      loadSources();
    } catch (error) {
      console.error('Error adding source:', error);
    }
  };

  const handleDeleteSource = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this source?')) {
      try {
        await sourcesAPI.delete(id);
        loadSources();
      } catch (error) {
        console.error('Error deleting source:', error);
      }
    }
  };

  if (loading) {
    return <div className="loading">Loading sources...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Sources</h1>
        <p className="page-subtitle">Manage price monitoring sources</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">All Sources</h2>
          <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
            + Add Source
          </button>
        </div>

        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Base URL</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sources.map((source) => (
              <tr key={source.id}>
                <td style={{ fontWeight: 500 }}>{source.name}</td>
                <td>
                  <span className="badge badge-info">
                    {source.type || 'General'}
                  </span>
                </td>
                <td style={{ fontSize: '12px', color: '#666' }}>
                  {source.base_url || '-'}
                </td>
                <td>
                  <span className={`badge ${source.is_active ? 'badge-success' : 'badge-danger'}`}>
                    {source.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>{new Date(source.created_at).toLocaleDateString()}</td>
                <td>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDeleteSource(source.id)}
                    style={{ padding: '5px 10px', fontSize: '12px' }}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
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
              width: '600px',
              maxHeight: '80vh',
              overflow: 'auto',
            }}
          >
            <h2 style={{ marginBottom: '20px' }}>Add New Source</h2>
            <form onSubmit={handleAddSource}>
              <div className="form-group">
                <label className="form-label">Name *</label>
                <input
                  type="text"
                  className="form-control"
                  value={newSource.name}
                  onChange={(e) => setNewSource({ ...newSource, name: e.target.value })}
                  required
                  placeholder="e.g. Allegro, Amazon"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Type</label>
                <select
                  className="form-control"
                  value={newSource.type}
                  onChange={(e) => setNewSource({ ...newSource, type: e.target.value })}
                >
                  <option value="marketplace">Marketplace</option>
                  <option value="distributor">Distributor</option>
                  <option value="retailer">Retailer</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Base URL</label>
                <input
                  type="url"
                  className="form-control"
                  value={newSource.base_url}
                  onChange={(e) => setNewSource({ ...newSource, base_url: e.target.value })}
                  placeholder="https://example.com"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Scraper Config (JSON)</label>
                <textarea
                  className="form-control"
                  value={newSource.scraper_config}
                  onChange={(e) => setNewSource({ ...newSource, scraper_config: e.target.value })}
                  rows={6}
                  placeholder='{"price_selector": ".price", "use_browser": true}'
                />
                <small style={{ color: '#666' }}>
                  Example: {'{'}price_selector: ".price", use_browser: true{'}'}
                </small>
              </div>
              <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button type="submit" className="btn btn-primary">
                  Add Source
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

export default Sources;
