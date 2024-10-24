import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyFetcher:
    def __init__(self):
        self.proxies = set()
        self.sources = [
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            # ad more sourrces here ;)
        ]

    async def fetch_url(self, session, url):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    return content
                logger.warning(f"Failed to fetch {url}: Status {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def parse_proxy_list(self, content):
        if not content:
            return
        
        # Einfache Zeilen-basierte Parsing
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and ':' in line:
                # Basic Validierung
                try:
                    host, port = line.split(':')[:2]
                    if host and port.isdigit() and 1 <= int(port) <= 65535:
                        self.proxies.add(f"{host}:{port}")
                except Exception:
                    continue

    async def fetch_all_proxies(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_url(session, url) for url in self.sources]
            results = await asyncio.gather(*tasks)
            
            for content in results:
                if content:
                    self.parse_proxy_list(content)

    def save_proxies(self):
        if not self.proxies:
            logger.warning("No proxies found to save!")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('proxies.txt', 'w') as f:
            f.write(f"# Proxy List - Updated: {timestamp}\n")
            f.write(f"# Total proxies: {len(self.proxies)}\n\n")
            for proxy in sorted(self.proxies):
                f.write(f"{proxy}\n")
        
        logger.info(f"Saved {len(self.proxies)} proxies to proxies.txt")

async def main():
    fetcher = ProxyFetcher()
    await fetcher.fetch_all_proxies()
    fetcher.save_proxies()

if __name__ == "__main__":
    asyncio.run(main())
