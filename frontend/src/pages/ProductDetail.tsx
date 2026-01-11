import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { productsAPI } from '../services/api';
import { ProductWithPrices, PriceHistory } from '../types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

const ProductDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<ProductWithPrices | null>(null);
  const [priceHistory, setPriceHistory] = useState<PriceHistory[]>([]);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadProduct();
      loadPriceHistory();
    }
  }, [id, days]);

  const loadProduct = async () => {
    try {
      const response = await productsAPI.getOne(parseInt(id!));
      setProduct(response.data);
    } catch (error) {
      console.error('Error loading product:', error);
    }
  };

  const loadPriceHistory = async () => {
    try {
      const response = await productsAPI.getPriceHistory(parseInt(id!), { days });
      setPriceHistory(response.data);
    } catch (error) {
      console.error('Error loading price history:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading product details...</div>;
  }

  if (!product) {
    return <div className="error">Product not found</div>;
  }

  // Prepare chart data
  const chartData = priceHistory.reduce((acc: any[], item) => {
    const date = format(new Date(item.checked_at), 'yyyy-MM-dd');
    const existing = acc.find((d) => d.date === date);
    
    if (existing) {
      existing[item.source_name || `Source ${item.source_id}`] = item.price;
    } else {
      acc.push({
        date,
        [item.source_name || `Source ${item.source_id}`]: item.price,
      });
    }
    
    return acc;
  }, []);

  // Get unique sources for chart lines
  const sources = [...new Set(priceHistory.map((p) => p.source_name || `Source ${p.source_id}`))];
  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#a4de6c'];

  return (
    <div>
      <div className="page-header">
        <button className="btn btn-secondary" onClick={() => navigate('/products')}>
          ← Back to Products
        </button>
      </div>

      <div className="card">
        <h1 style={{ fontSize: '28px', marginBottom: '10px' }}>{product.name}</h1>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginTop: '20px' }}>
          <div>
            <strong>SKU:</strong> {product.sku || 'N/A'}
          </div>
          <div>
            <strong>EAN:</strong> {product.ean || 'N/A'}
          </div>
          <div>
            <strong>Category:</strong> {product.category || 'N/A'}
          </div>
          <div>
            <strong>Brand:</strong> {product.brand || 'N/A'}
          </div>
          <div>
            <strong>Base Price:</strong> {product.base_price ? `${product.base_price} PLN` : 'N/A'}
          </div>
          <div>
            <strong>Status:</strong>{' '}
            <span className={`badge ${product.is_active ? 'badge-success' : 'badge-danger'}`}>
              {product.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Current Prices</h2>
        </div>
        {product.current_prices.length === 0 ? (
          <p>No current prices available</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
            {product.current_prices.map((price) => (
              <div
                key={price.source_id}
                style={{
                  padding: '15px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                }}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                  {price.source_name}
                </div>
                <div style={{ fontSize: '24px', color: '#0f3460', fontWeight: 'bold' }}>
                  {price.price} PLN
                </div>
                <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                  Checked: {format(new Date(price.checked_at), 'yyyy-MM-dd HH:mm')}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Price History</h2>
          <select
            className="form-control"
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value))}
            style={{ width: 'auto' }}
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={180}>Last 180 days</option>
          </select>
        </div>
        {chartData.length === 0 ? (
          <p>No price history available</p>
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              {sources.map((source, index) => (
                <Line
                  key={source}
                  type="monotone"
                  dataKey={source}
                  stroke={colors[index % colors.length]}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Price History Table</h2>
        </div>
        {priceHistory.length === 0 ? (
          <p>No price history available</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Source</th>
                <th>Price</th>
                <th>Availability</th>
              </tr>
            </thead>
            <tbody>
              {priceHistory.slice(0, 50).map((item) => (
                <tr key={item.id}>
                  <td>{format(new Date(item.checked_at), 'yyyy-MM-dd HH:mm')}</td>
                  <td>{item.source_name || `Source ${item.source_id}`}</td>
                  <td>{item.price} {item.currency}</td>
                  <td>
                    <span className={`badge ${item.availability ? 'badge-success' : 'badge-danger'}`}>
                      {item.availability ? 'Available' : 'Unavailable'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default ProductDetail;
