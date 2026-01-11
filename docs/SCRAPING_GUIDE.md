# Scraping Configuration Guide

## Overview

The scraping system uses configurable CSS selectors to extract prices from different websites. You can configure scrapers at two levels:
1. **Source level** - Default configuration for all products from that source
2. **Product-Source level** - Override configuration for specific products

## Scraper Configuration

### Basic Configuration

```json
{
  "price_selector": ".price",
  "availability_selector": ".stock-status",
  "name_selector": "h1.product-title",
  "image_selector": "img.product-image",
  "use_browser": true
}
```

### Configuration Options

- **price_selector** (required): CSS selector for price element
- **availability_selector** (optional): CSS selector for availability
- **name_selector** (optional): CSS selector for product name
- **image_selector** (optional): CSS selector for product image
- **use_browser** (bool): Use Playwright for JavaScript-heavy sites (default: false)
- **wait_for_selector** (optional): Wait for this selector before scraping

## Platform-Specific Configurations

### Allegro

```json
{
  "price_selector": "[data-box-name='Price'] span",
  "availability_selector": "button[data-role='buy-button']",
  "use_browser": true
}
```

**Tips for Allegro:**
- Always use `use_browser: true` (heavy JavaScript)
- Price is usually in `data-box-name="Price"` element
- Check network tab for API endpoints (faster alternative)

### Amazon

```json
{
  "price_selector": ".a-price-whole",
  "availability_selector": "#availability",
  "use_browser": true
}
```

**Alternative selectors:**
- `#priceblock_ourprice`
- `#priceblock_dealprice`
- `.a-offscreen`

### Empik

```json
{
  "price_selector": "[data-ta='product-price']",
  "availability_selector": ".availability-info",
  "use_browser": true
}
```

### Generic E-commerce Sites

Try these common selectors:

```json
{
  "price_selector": ".price, .product-price, [itemprop='price'], .sale-price",
  "availability_selector": ".in-stock, .availability, [itemprop='availability']",
  "use_browser": false
}
```

## Finding Selectors

### Method 1: Browser DevTools

1. Open the product page
2. Right-click on the price → Inspect
3. Find the CSS selector in DevTools
4. Test in console: `document.querySelector('.your-selector')`

### Method 2: Browser Extensions

Install extensions like:
- **SelectorGadget** (Chrome/Firefox)
- **CSS Selector Tester** (Chrome)

### Method 3: Common Patterns

**Price patterns:**
```css
.price
.product-price
.sale-price
[itemprop="price"]
[data-price]
.price-value
```

**Availability patterns:**
```css
.in-stock
.availability
.stock-status
[itemprop="availability"]
```

## Testing Scrapers

### Test via API

```python
import requests

url = "http://localhost/api/v1/products/1/test-scrape"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
data = {
    "source_url": "https://example.com/product/123",
    "config": {
        "price_selector": ".price",
        "use_browser": True
    }
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### Test Manually

```bash
docker-compose exec celery_worker python -c "
import asyncio
from app.scrapers.universal_scraper import UniversalScraper

async def test():
    scraper = UniversalScraper()
    config = {
        'price_selector': '.price',
        'use_browser': True
    }
    result = await scraper.scrape_price('https://example.com/product', config)
    print(result)

asyncio.run(test())
"
```

## Troubleshooting

### Issue: Price not found

**Solutions:**
1. Check if selector is correct
2. Try different selectors (price can be in multiple places)
3. Enable `use_browser: true` if site uses JavaScript
4. Check if site requires cookies/login

### Issue: Scraping too slow

**Solutions:**
1. Set `use_browser: false` if possible
2. Increase timeout: `SCRAPING_TIMEOUT=60` in .env
3. Use API endpoints if available (faster than HTML parsing)

### Issue: Getting blocked

**Solutions:**
1. Increase delay: `SCRAPING_DELAY=5` in .env
2. Rotate user agents
3. Use proxy services
4. Respect robots.txt

### Issue: Incorrect prices

**Solutions:**
1. Check if selector includes currency symbol
2. Verify if price is in correct format (99.99 vs 99,99)
3. Check for sale prices vs regular prices
4. Look for hidden elements

## Advanced: Multiple Price Elements

Some sites show different prices (regular, sale, member):

```json
{
  "price_selector": ".sale-price, .regular-price",
  "use_browser": true
}
```

The scraper will use the first matching selector.

## Rate Limiting

Configure in `.env`:

```env
SCRAPING_DELAY=2          # Seconds between requests
SCRAPING_TIMEOUT=30       # Request timeout
MAX_RETRIES=3            # Number of retries
```

## Best Practices

1. **Start simple**: Test with `use_browser: false` first
2. **Be specific**: Use unique selectors to avoid false matches
3. **Handle variants**: Account for different page layouts
4. **Test regularly**: Websites change, selectors break
5. **Respect robots.txt**: Check allowed/disallowed paths
6. **Monitor errors**: Check logs for failed scrapes
7. **Cache when possible**: Don't scrape the same page repeatedly

## Example Workflow

1. **Find product URL** on target site
2. **Inspect HTML** to find price element
3. **Create source** with base configuration
4. **Add product-source mapping** with URL
5. **Test scraping** manually
6. **Run scheduled job** to collect prices
7. **Monitor and adjust** selectors as needed

## API Endpoints for Testing

```bash
# Test scraping configuration
POST /api/v1/products/{id}/test-scrape

# Run scrape job for single product
POST /api/v1/scrape/product/{product_id}/{source_id}

# Run scrape job for all products
POST /api/v1/scrape/all
```

## Support

If you need help with specific websites:
1. Check documentation for that platform
2. Look for official APIs (often better than scraping)
3. Consider using third-party scraping services
4. Check if site has terms of service regarding scraping
