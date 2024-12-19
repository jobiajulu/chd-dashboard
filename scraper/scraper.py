import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
from pathlib import Path
import json
from datetime import datetime
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class STSScraper:
    BASE_URLS = [
        "https://publicreporting.sts.org/congenital/50{:03d}",
        "https://publicreporting.sts.org/congenital/51{:03d}"
    ]
    DATA_DIR = Path(__file__).parent.parent / "data"
    
    def __init__(self):
        self.DATA_DIR.mkdir(exist_ok=True)
        self.session = None
        self.hospitals = []
        self.valid_hospitals = 0

    async def init_session(self):
        """Initialize aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def fetch_page(self, url):
        """Fetch a single page and return its content"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def parse_hospital_data(self, html_content, url):
        """Parse hospital data from HTML content"""
        if not html_content:
            return None

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract hospital name
        title = soup.find('title')
        if not title:
            return None
        
        hospital_name = title.text.split('|')[0].strip()
        
        # Skip pages that don't contain actual hospital data
        if hospital_name == "STS Public Reporting":
            return None
        
        # Extract data table
        data = {
            'hospital_name': hospital_name,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'mortality_data': [],
            'raw_html': html_content  # Store raw HTML for future parsing if needed
        }

        # Find all data tables
        tables = soup.find_all('table')
        for table in tables:
            headers = []
            rows_data = []
            
            # Get headers
            headers_row = table.find('thead')
            if headers_row:
                headers = [th.text.strip() for th in headers_row.find_all('th')]
            
            # Get rows
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if cells:
                    row_data = [cell.text.strip() for cell in cells]
                    rows_data.append(row_data)
            
            if headers and rows_data:
                data['mortality_data'].append({
                    'headers': headers,
                    'rows': rows_data
                })

        return data

    async def scrape_hospital(self, prefix, number):
        """Scrape data for a single hospital"""
        url = prefix.format(number)
        content = await self.fetch_page(url)
        if content:
            data = self.parse_hospital_data(content, url)
            if data:
                self.hospitals.append(data)
                self.valid_hospitals += 1
                return True
        return False

    async def scrape_all_hospitals(self):
        """Scrape data from all hospitals"""
        await self.init_session()
        try:
            tasks = []
            # Create tasks for both URL patterns (50XXX and 51XXX)
            for prefix in self.BASE_URLS:
                max_number = 200 if "50" in prefix else 100  # 51XXX only goes up to 099
                for i in range(max_number):
                    tasks.append(self.scrape_hospital(prefix, i))
            
            # Use tqdm to show progress
            results = []
            total_tasks = len(tasks)
            for f in tqdm(asyncio.as_completed(tasks), total=total_tasks, desc="Scraping hospitals"):
                results.append(await f)
            
            # Save results
            logger.info(f"Successfully scraped {self.valid_hospitals} valid hospitals")
            
            # Save to JSON file
            output_file = self.DATA_DIR / f"hospitals_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump({
                    'metadata': {
                        'total_urls_checked': total_tasks,
                        'valid_hospitals_found': self.valid_hospitals,
                        'scraped_at': datetime.now().isoformat()
                    },
                    'hospitals': self.hospitals
                }, f, indent=2)
            
            logger.info(f"Data saved to {output_file}")
            
        finally:
            await self.close_session()

async def main():
    scraper = STSScraper()
    await scraper.scrape_all_hospitals()

if __name__ == "__main__":
    asyncio.run(main())
