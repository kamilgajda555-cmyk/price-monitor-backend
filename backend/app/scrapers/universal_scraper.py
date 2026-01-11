from app.scrapers.base_scraper import BaseScraper
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class UniversalScraper(BaseScraper):
    """
    Universal scraper that uses configurable CSS selectors
    
    Config format:
    {
        "price_selector": ".price",
        "availability_selector": ".availability",
        "name_selector": "h1.product-title",
        "image_selector": "img.product-image",
        "use_browser": true/false,
        "wait_for_selector": ".price"  # Optional
    }
    """
    
    async def scrape_price(self, url: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Scrape price using provided config"""
        
        if not config:
            raise ValueError("Config is required for UniversalScraper")
        
        use_browser = config.get("use_browser", False)
        
        try:
            # Fetch page
            html = await self.fetch_page(url, use_browser=use_browser)
            soup = self.parse_html(html)
            
            # Extract price
            price = None
            price_selector = config.get("price_selector")
            if price_selector:
                price_element = soup.select_one(price_selector)
                if price_element:
                    price_text = price_element.get_text()
                    price = self.extract_price_from_text(price_text)
            
            if price is None:
                logger.warning(f"Could not find price for {url}")
                return {"error": "Price not found"}
            
            # Extract availability
            availability = True
            availability_selector = config.get("availability_selector")
            if availability_selector:
                avail_element = soup.select_one(availability_selector)
                if avail_element:
                    avail_text = avail_element.get_text().lower()
                    availability = not any(word in avail_text for word in ["niedostępny", "unavailable", "out of stock"])
            
            # Extract product name (optional)
            product_name = None
            name_selector = config.get("name_selector")
            if name_selector:
                name_element = soup.select_one(name_selector)
                if name_element:
                    product_name = name_element.get_text().strip()
            
            # Extract image URL (optional)
            image_url = None
            image_selector = config.get("image_selector")
            if image_selector:
                image_element = soup.select_one(image_selector)
                if image_element:
                    image_url = image_element.get("src")
            
            result = {
                "price": price,
                "currency": "PLN",  # Default, could be in config
                "availability": availability
            }
            
            if product_name:
                result["product_name"] = product_name
            if image_url:
                result["image_url"] = image_url
            
            logger.info(f"Successfully scraped {url}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {"error": str(e)}


class AllegroScraper(BaseScraper):
    """Specialized scraper for Allegro"""
    
    async def scrape_price(self, url: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            html = await self.fetch_page(url, use_browser=True)
            soup = self.parse_html(html)
            
            # Allegro-specific selectors (these may need to be updated)
            price_element = soup.select_one('[data-box-name="Price"] span, .price, [itemprop="price"]')
            if not price_element:
                return {"error": "Price not found"}
            
            price = self.extract_price_from_text(price_element.get_text())
            
            # Check availability
            availability = True
            buy_button = soup.select_one('button[data-role="buy-button"]')
            if not buy_button or "niedostępny" in soup.get_text().lower():
                availability = False
            
            return {
                "price": price,
                "currency": "PLN",
                "availability": availability
            }
            
        except Exception as e:
            logger.error(f"Error scraping Allegro {url}: {e}")
            return {"error": str(e)}


class AmazonScraper(BaseScraper):
    """Specialized scraper for Amazon"""
    
    async def scrape_price(self, url: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            html = await self.fetch_page(url, use_browser=True)
            soup = self.parse_html(html)
            
            # Amazon-specific selectors
            price_selectors = [
                '.a-price-whole',
                '#priceblock_ourprice',
                '#priceblock_dealprice',
                '.a-offscreen'
            ]
            
            price = None
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price = self.extract_price_from_text(price_element.get_text())
                    if price:
                        break
            
            if not price:
                return {"error": "Price not found"}
            
            # Check availability
            availability = True
            availability_element = soup.select_one('#availability')
            if availability_element and "unavailable" in availability_element.get_text().lower():
                availability = False
            
            return {
                "price": price,
                "currency": "PLN",  # Or extract from page
                "availability": availability
            }
            
        except Exception as e:
            logger.error(f"Error scraping Amazon {url}: {e}")
            return {"error": str(e)}


class EmpikScraper(BaseScraper):
    """Specialized scraper for Empik"""
    
    async def scrape_price(self, url: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            html = await self.fetch_page(url, use_browser=True)
            soup = self.parse_html(html)
            
            # Empik-specific selectors
            price_element = soup.select_one('.price, [data-ta="product-price"]')
            if not price_element:
                return {"error": "Price not found"}
            
            price = self.extract_price_from_text(price_element.get_text())
            
            # Check availability
            availability = True
            if "niedostępny" in soup.get_text().lower():
                availability = False
            
            return {
                "price": price,
                "currency": "PLN",
                "availability": availability
            }
            
        except Exception as e:
            logger.error(f"Error scraping Empik {url}: {e}")
            return {"error": str(e)}


def get_scraper(source_name: str) -> BaseScraper:
    """Factory function to get appropriate scraper"""
    scrapers = {
        "allegro": AllegroScraper,
        "amazon": AmazonScraper,
        "empik": EmpikScraper
    }
    
    source_lower = source_name.lower()
    for key, scraper_class in scrapers.items():
        if key in source_lower:
            return scraper_class()
    
    # Default to universal scraper
    return UniversalScraper()
