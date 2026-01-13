import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { productsAPI, sourcesAPI, scrapingAPI } from '../services/api';
import { ProductWithPrices, Source } from '../types';

const Products: React.FC = () => {
  const [products, setProducts] = useState<ProductWithPrices[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showAddSourceModal, setShowAddSourceModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<number | null>(null);
  const [newProduct, setNewProduct] = useState({
    name: '',
    sku: '',
    ean: '',
    category: '',
    brand: '',
    base_price: '',
  });
  const [newSource, setNewSource] = useState({
    source_id: '',
    source_url: '',
  });

  useEffect(() => {
    loadProducts();
    loadSources();
  }, [search]);

  const loadProducts = async () => {
    try {
      const response = await productsAPI.getAll({ search, limit: 100 });
      setProducts(response.data);
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSources = async () => {
    try {
      const response = await sourcesAPI.getAll();
      setSources(response.data);
    } catch (error) {
      console.error('Error loading sources:', error);
    }
  };

  const handleAddProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await productsAPI.create({
        ...newProduct,
        base_price: parseFloat(newProduct.base_price) || undefined,
      });
      setShowAddModal(false);
      setNewProduct({ name: '', sku: '', ean: '', category: '', brand: '', base_price: '' });
      loadProducts();
    } catch (error) {
      console.error('Error adding product:', error);
      alert('Error adding product. Check console.');
    }
  };

  const handleAddSource = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProduct || !newSource.source_id || !newSource.source_url) {
      alert('Please select source and enter URL');
      return;
    }
    try {
      await sourcesAPI.createProductSource({
        product_id: selectedProduct,
        source_id: parseInt(newSource.source_id),
        source_url: newSource.source_url,
      });
      setShowAddSourceModal(false);
      setNewSource({ source_id: '', source_url: '' });
      setSelectedProduct(null);
      alert('Source added successfully! You can now scrape this product.');
      loadProducts();
    } catch (error) {
      console.error('Error adding source:', error);
      alert('Error adding source. Check console.');
    }
  };

  const handleScrapeProduct = async (productId: number) => {
    if (!window.confirm('Start scraping this product now?')) return;
    try {
      const response = await scrapingAPI.scrapeProduct(productId);
      alert(`Scraping started! Job ID: ${response.data.job_id || 'N/A'}`);
      // Reload after 3 seconds to show updated prices
      setTimeout(loadProducts, 3000);
    } catch (error) {
      console.error('Error starting scrape:', error);
      alert('Error starting scrape. Check console.');
    }
  };

  const handleDeleteProduct = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await productsAPI.delete(id);
        loadProducts();
      } catch (error) {
        console.error('Error deleting product:', error);
      }
    }
  };

  if (loading) {
    return <div className="loading">Loading products...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Products</h1>
        <p className="page-subtitle">Manage your product catalog</p>
      </div>

      <div className="card">
        <div className="card-header">
          <div style={{ display: 'flex', gap: '10px', flex: 1 }}>
            <input
              type="text"
              className="form-control"
              placeholder="Search products..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ maxWidth: '400px' }}
            />
          </div>
          <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
            + Add Product
          </button>
        </div>

        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>SKU</th>
              <th>EAN</th>
              <th>Category</th>
              <th>Base Price</th>
              <th>Current Prices</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.id}>
                <td>
                  <Link to={`/products/${product.id}`} style={{ color: '#0f3460', fontWeight: 500 }}>
                    {product.name}
                  </Link>
                </td>
                <td>{product.sku || '-'}</td>
                <td>{product.ean || '-'}</td>
                <td>{product.category || '-'}</td>
                <td>{product.base_price ? `${product.base_price} PLN` : '-'}</td>
                <td>
                  {product.current_prices.length > 0 ? (
                    <div>
                      Min: {product.min_price?.toFixed(2)} PLN<br />
                      Max: {product.max_price?.toFixed(2)} PLN<br />
                      Avg: {product.avg_price?.toFixed(2)} PLN
                    </div>
                  ) : (
                    'No prices'
                  )}
                </td>
                <td>
                  <span className={`badge ${product.is_active ? 'badge-success' : 'badge-danger'}`}>
                    {product.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => {
                        setSelectedProduct(product.id);
                        setShowAddSourceModal(true);
                      }}
                      style={{ padding: '5px 10px', fontSize: '12px' }}
                    >
                      + Add Source
                    </button>
                    <button
                      className="btn btn-success btn-sm"
                      onClick={() => handleScrapeProduct(product.id)}
                      style={{ padding: '5px 10px', fontSize: '12px' }}
                    >
                      🔄 Scrape
                    </button>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDeleteProduct(product.id)}
                      style={{ padding: '5px 10px', fontSize: '12px' }}
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Add Product Modal */}
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
              maxHeight: '80vh',
              overflow: 'auto',
            }}
          >
            <h2 style={{ marginBottom: '20px' }}>Add New Product</h2>
            <form onSubmit={handleAddProduct}>
              <div className="form-group">
                <label className="form-label">Name *</label>
                <input
                  type="text"
                  className="form-control"
                  value={newProduct.name}
                  onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">SKU</label>
                <input
                  type="text"
                  className="form-control"
                  value={newProduct.sku}
                  onChange={(e) => setNewProduct({ ...newProduct, sku: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">EAN</label>
                <input
                  type="text"
                  className="form-control"
                  value={newProduct.ean}
                  onChange={(e) => setNewProduct({ ...newProduct, ean: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Category</label>
                <input
                  type="text"
                  className="form-control"
                  value={newProduct.category}
                  onChange={(e) => setNewProduct({ ...newProduct, category: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Brand</label>
                <input
                  type="text"
                  className="form-control"
                  value={newProduct.brand}
                  onChange={(e) => setNewProduct({ ...newProduct, brand: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Base Price (PLN)</label>
                <input
                  type="number"
                  step="0.01"
                  className="form-control"
                  value={newProduct.base_price}
                  onChange={(e) => setNewProduct({ ...newProduct, base_price: e.target.value })}
                />
              </div>
              <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button type="submit" className="btn btn-primary">
                  Add Product
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

      {/* Add Source Modal */}
      {showAddSourceModal && (
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
            <h2 style={{ marginBottom: '20px' }}>Add Source to Product</h2>
            <form onSubmit={handleAddSource}>
              <div className="form-group">
                <label className="form-label">Source *</label>
                <select
                  className="form-control"
                  value={newSource.source_id}
                  onChange={(e) => setNewSource({ ...newSource, source_id: e.target.value })}
                  required
                >
                  <option value="">Select source...</option>
                  {sources.map((source) => (
                    <option key={source.id} value={source.id}>
                      {source.name} ({source.type})
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Product URL *</label>
                <input
                  type="url"
                  className="form-control"
                  value={newSource.source_url}
                  onChange={(e) => setNewSource({ ...newSource, source_url: e.target.value })}
                  placeholder="https://example.com/product/123"
                  required
                />
                <small style={{ color: '#666' }}>
                  Enter the full URL to the product on this source
                </small>
              </div>
              <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button type="submit" className="btn btn-primary">
                  Add Source
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowAddSourceModal(false);
                    setSelectedProduct(null);
                    setNewSource({ source_id: '', source_url: '' });
                  }}
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

export default Products;
