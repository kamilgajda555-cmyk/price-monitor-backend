from abc import ABC, abstractmethod
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
import logging
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Base scraper class with common functionality"""
    
    def __init__(self):
        self.timeout = int(os.getenv("SCRAPING_TIMEOUT", 30)) * 1000
        self.delay = int(os.getenv("SCRAPING_DELAY", 2))
        self.user_agent = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_page(self, url: str, use_browser: bool = False) -> str:
        """Fetch page content with retry logic"""
        if use_browser:
            return await self._fetch_with_playwright(url)
        else:
            return await self._fetch_with_requests(url)
    
    async def _fetch_with_playwright(self, url: str) -> str:
        """Fetch page using Playwright (for JavaScript-heavy sites)"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            try:
                await page.goto(url, timeout=self.timeout, wait_until="networkidle")
                await asyncio.sleep(self.delay)
                content = await page.content()
                return content
            except Exception as e:
                logger.error(f"Error fetching {url} with Playwright: {e}")
                raise
            finally:
                await browser.close()
    
    async def _fetch_with_requests(self, url: str) -> str:
        """Fetch page using aiohttp (faster for simple pages)"""
        import aiohttp
        
        headers = {"User-Agent": self.user_agent}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=self.timeout/1000) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f"HTTP {response.status} for {url}")
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML with BeautifulSoup"""
        return BeautifulSoup(html, 'lxml')
    
    @abstractmethod
    async def scrape_price(self, url: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Scrape price from URL using config
        
        Returns:
            {
                "price": float,
                "currency": str,
                "availability": bool,
                "product_name": str (optional),
                "image_url": str (optional)
            }
        """
        pass
    
    def extract_price_from_text(self, text: str) -> Optional[float]:
        """Extract price from text string"""
        import re
        
        # Remove whitespace
        text = text.strip().replace(" ", "").replace("\n", "")
        
        # Common patterns for prices
        patterns = [
            r'(\d+[,.]?\d*)',  # Basic number
            r'(\d+)\s*zł',  # Polish zloty
            r'PLN\s*(\d+[,.]?\d*)',
            r'\$(\d+[,.]?\d*)',
            r'€(\d+[,.]?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                price_str = match.group(1).replace(',', '.')
                try:
                    return float(price_str)
                except ValueError:
                    continue
        
        return None
