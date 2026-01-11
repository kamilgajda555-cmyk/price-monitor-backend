import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { productsAPI } from '../services/api';
import { ProductWithPrices } from '../types';

const Products: React.FC = () => {
  const [products, setProducts] = useState<ProductWithPrices[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newProduct, setNewProduct] = useState({
    name: '',
    sku: '',
    ean: '',
    category: '',
    brand: '',
    base_price: '',
  });

  useEffect(() => {
    loadProducts();
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
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDeleteProduct(product.id)}
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
    </div>
  );
};

export default Products;
