# Price Monitor API Documentation

## Base URL
```
http://localhost/api/v1
```

## Authentication

All endpoints (except `/auth/login` and `/auth/register`) require a Bearer token in the Authorization header.

### Get Token

**POST** `/auth/login`

Request:
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

Use the token in subsequent requests:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Products

### List Products

**GET** `/products/`

Query Parameters:
- `skip` (int): Offset for pagination (default: 0)
- `limit` (int): Number of items (default: 100)
- `search` (string): Search by name, SKU, or EAN
- `category` (string): Filter by category
- `is_active` (bool): Filter by active status

Response:
```json
[
  {
    "id": 1,
    "name": "Product Name",
    "sku": "SKU123",
    "ean": "1234567890123",
    "category": "Electronics",
    "brand": "Brand",
    "base_price": 99.99,
    "is_active": true,
    "current_prices": [
      {
        "source_id": 1,
        "source_name": "Allegro",
        "price": 95.99,
        "checked_at": "2024-01-01T12:00:00"
      }
    ],
    "min_price": 95.99,
    "max_price": 105.99,
    "avg_price": 99.99
  }
]
```

### Create Product

**POST** `/products/`

Request:
```json
{
  "name": "Product Name",
  "sku": "SKU123",
  "ean": "1234567890123",
  "category": "Electronics",
  "brand": "Brand",
  "base_price": 99.99,
  "is_active": true
}
```

### Get Product Details

**GET** `/products/{id}`

### Update Product

**PUT** `/products/{id}`

### Delete Product

**DELETE** `/products/{id}`

### Get Price History

**GET** `/products/{id}/price-history`

Query Parameters:
- `source_id` (int): Filter by source
- `days` (int): Number of days (default: 30)

## Sources

### List Sources

**GET** `/sources/`

### Create Source

**POST** `/sources/`

Request:
```json
{
  "name": "Allegro",
  "type": "marketplace",
  "base_url": "https://allegro.pl",
  "is_active": true,
  "scraper_config": {
    "price_selector": ".price",
    "availability_selector": ".stock",
    "use_browser": true
  }
}
```

### Product-Source Mapping

**POST** `/sources/product-sources/`

Request:
```json
{
  "product_id": 1,
  "source_id": 1,
  "source_url": "https://allegro.pl/oferta/123",
  "is_active": true,
  "selector_config": {
    "price_selector": ".custom-price"
  }
}
```

## Alerts

### List Alerts

**GET** `/alerts/`

### Create Alert

**POST** `/alerts/`

Request:
```json
{
  "product_id": 1,
  "alert_type": "price_drop",
  "condition": {
    "threshold": 90.00,
    "percentage": 10
  },
  "is_active": true
}
```

Alert Types:
- `price_drop` - Price drops below threshold or by percentage
- `price_increase` - Price increases above threshold or by percentage
- `availability` - Product availability changes
- `competitor` - Competitor has lower price

## Reports

### Generate Report

**POST** `/reports/generate`

Request:
```json
{
  "report_type": "products",
  "format": "excel",
  "date_from": "2024-01-01T00:00:00",
  "date_to": "2024-12-31T23:59:59"
}
```

Report Types:
- `products` - Products list
- `price_changes` - Price history
- `sources` - Sources overview

Formats:
- `excel` - .xlsx
- `csv` - .csv
- `pdf` - .pdf

Response: Binary file download

## Dashboard

### Get Stats

**GET** `/dashboard/stats`

Response:
```json
{
  "total_products": 100,
  "active_products": 95,
  "total_sources": 5,
  "active_sources": 5,
  "total_price_checks_today": 500,
  "products_with_price_drop": 10,
  "products_with_price_increase": 5,
  "average_price_change": -2.5
}
```

### Get Recent Alerts

**GET** `/dashboard/recent-alerts`

### Get Scraping Status

**GET** `/dashboard/scraping-status`

## Error Responses

All endpoints may return these error codes:

- `400` Bad Request - Invalid input
- `401` Unauthorized - Missing or invalid token
- `403` Forbidden - Insufficient permissions
- `404` Not Found - Resource not found
- `500` Internal Server Error - Server error

Error format:
```json
{
  "detail": "Error message"
}
```
