#!/usr/bin/env python3
"""
Unvan.az Scraper - Single file, crash-proof, async scraper
Usage: python unvan_scraper.py [--max-pages N] [--reset]
"""

import asyncio
import aiohttp
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime
import argparse
import sys


def log(msg: str):
    """Log to both console and file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {msg}"
    print(msg)
    try:
        with open('scraper.log', 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    except:
        pass


class UnvanScraper:
    BASE_URL = "https://unvan.az"
    SEARCH_URL = f"{BASE_URL}/search/"
    AJAX_URL = f"{BASE_URL}/ajax.php"

    PROGRESS_FILE = "progress.json"
    CSV_FILE = "listings.csv"

    CSV_HEADERS = [
        'id', 'title', 'url', 'category', 'price', 'currency',
        'description', 'name', 'phone', 'location', 'date', 'image', 'scraped_at'
    ]

    def __init__(self, city="31", concurrent=5, delay=1.0):
        self.city = city
        self.delay = delay
        self.sem = asyncio.Semaphore(concurrent)
        self.processed: Set[str] = set()
        self.failed: Set[str] = set()
        self.page = 0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en-US;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': self.BASE_URL,
            'Referer': f'{self.BASE_URL}/search/'
        }
        self.load_progress()

    def load_progress(self):
        """Load saved progress"""
        if Path(self.PROGRESS_FILE).exists():
            try:
                with open(self.PROGRESS_FILE) as f:
                    data = json.load(f)
                    self.processed = set(data.get('processed', []))
                    self.failed = set(data.get('failed', []))
                    self.page = data.get('page', 0)
                    log(f"✓ Loaded: {len(self.processed)} processed, page {self.page}")
            except:
                pass

    def save_progress(self):
        """Save progress"""
        try:
            with open(self.PROGRESS_FILE, 'w') as f:
                json.dump({
                    'processed': list(self.processed),
                    'failed': list(self.failed),
                    'page': self.page,
                    'updated': datetime.now().isoformat()
                }, f)
        except Exception as e:
            log(f"✗ Save failed: {e}")

    def save_csv(self, listings: List[Dict]):
        """Save to CSV"""
        if not listings:
            return

        exists = Path(self.CSV_FILE).exists()
        try:
            with open(self.CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.CSV_HEADERS)
                if not exists:
                    writer.writeheader()
                for item in listings:
                    row = {h: item.get(h, '') for h in self.CSV_HEADERS}
                    writer.writerow(row)
            log(f"✓ Saved {len(listings)} listings to CSV")
        except Exception as e:
            log(f"✗ CSV save failed: {e}")

    async def fetch(self, session, url, method='GET', data=None):
        """Fetch with rate limit"""
        async with self.sem:
            try:
                await asyncio.sleep(self.delay)
                async with session.request(
                    method, url, data=data, headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        return await resp.text()
                    log(f"✗ HTTP {resp.status}: {url}")
            except asyncio.TimeoutError:
                log(f"✗ Timeout: {url}")
            except Exception as e:
                log(f"✗ Error: {e}")
        return None

    def extract_id(self, url: str) -> Optional[str]:
        """Extract listing ID from URL"""
        m = re.search(r'-(\d+)\.html', url)
        return m.group(1) if m else None

    def parse_search(self, html: str) -> List[Dict]:
        """Parse search results page"""
        soup = BeautifulSoup(html, 'html.parser')
        listings = []

        for div in soup.find_all('div', class_='index prodbig'):
            try:
                link = div.find('div', class_='prodname').find('a')
                url = urljoin(self.BASE_URL, link['href'])
                title = link.get_text(strip=True)

                price_tag = div.find('span', class_='sprice')
                price_text = price_tag.get_text(strip=True) if price_tag else ''
                pm = re.search(r'([\d,]+)\s*(\w+)', price_text)

                desc = div.find('p', class_='prodful')
                img = div.find('div', class_='holderimg').find('img')

                lid = self.extract_id(url)
                if lid:
                    listings.append({
                        'id': lid,
                        'url': url,
                        'title': title,
                        'price': pm.group(1).replace(',', '') if pm else '',
                        'currency': pm.group(2) if pm else '',
                        'description': desc.get_text(strip=True) if desc else '',
                        'image': urljoin(self.BASE_URL, img['src']) if img else ''
                    })
            except Exception as e:
                log(f"✗ Parse error: {e}")

        return listings

    async def get_phone(self, session, lid: str, hash_code: str) -> Optional[str]:
        """Get phone via AJAX"""
        data = {'act': 'telshow', 'id': lid, 't': 'elanlar', 'h': hash_code, 'rf': 'search/'}
        try:
            async with session.post(self.AJAX_URL, data=data, headers=self.headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get('ok') == 1:
                        return result.get('tel', '')
        except:
            pass
        return None

    def parse_detail(self, html: str, lid: str) -> Dict:
        """Parse detail page"""
        soup = BeautifulSoup(html, 'html.parser')
        data = {}

        try:
            # Title
            title = soup.find('h1', class_='leftfloat')
            if title:
                data['title'] = title.get_text(strip=True)

            # Category
            breadcrumb = soup.find('div', class_='breadcrumb')
            if breadcrumb:
                links = breadcrumb.find_all('a')
                data['category'] = links[-1].get_text(strip=True) if links else ''

            # Price
            price = soup.find('span', class_='pricecolor')
            if price:
                pm = re.search(r'([\d,]+)\s*(\w+)', price.get_text(strip=True))
                if pm:
                    data['price'] = pm.group(1).replace(',', '')
                    data['currency'] = pm.group(2)

            # Description
            desc = soup.find('p', class_='infop100 fullteshow')
            if desc:
                data['description'] = desc.get_text(strip=True)

            # Contact
            contact = soup.find('div', class_='infocontact')
            if contact:
                user = contact.find('a', href=re.compile(r'/user/'))
                if user:
                    data['name'] = user.get_text(strip=True).replace('(Bütün Elanları)', '').strip()

                loc = contact.find('span', class_='glyphicon-map-marker')
                if loc and loc.next_sibling:
                    data['location'] = loc.next_sibling.strip()

            # Date
            date = soup.find('span', class_='viewsbb clear')
            if date:
                dm = re.search(r'Tarix:\s*([\d.]+)', date.get_text(strip=True))
                if dm:
                    data['date'] = dm.group(1)

            # Hash for phone
            telshow = soup.find('div', id='telshow')
            if telshow:
                data['hash'] = telshow.get('data-h', '')

        except Exception as e:
            log(f"✗ Detail parse error: {e}")

        return data

    async def scrape_detail(self, session, listing: Dict) -> Optional[Dict]:
        """Scrape full listing"""
        lid = listing['id']
        url = listing['url']

        if lid in self.processed:
            return None

        log(f"→ Scraping {lid}")

        html = await self.fetch(session, url)
        if not html:
            self.failed.add(lid)
            return None

        detail = self.parse_detail(html, lid)
        complete = {**listing, **detail}

        # Get phone
        if detail.get('hash'):
            await asyncio.sleep(0.3)
            phone = await self.get_phone(session, lid, detail['hash'])
            if phone:
                complete['phone'] = phone

        complete['scraped_at'] = datetime.now().isoformat()
        self.processed.add(lid)

        return complete

    async def scrape_page(self, session, page: int) -> List[Dict]:
        """Scrape one search page"""
        log(f"\n▶ Page {page}")

        data = {
            'query': '',
            'city': self.city,
            'hhh': '&mh=dd52429d516d6a1077a7e725d4273b3c&mr=1767109214',
            'start': str(page)
        }

        html = await self.fetch(session, self.SEARCH_URL, 'POST', data)
        if not html or '<div class="index prodbig">' not in html:
            log(f"✗ No listings on page {page}")
            return []

        listings = self.parse_search(html)
        log(f"✓ Found {len(listings)} listings")

        return listings

    async def scrape(self, max_pages: Optional[int] = None):
        """Main scrape loop"""
        log(f"\n{'='*60}")
        log(f"Unvan.az Scraper Starting")
        log(f"Starting from page: {self.page}")
        log(f"Already processed: {len(self.processed)}")
        log(f"{'='*60}\n")

        async with aiohttp.ClientSession() as session:
            page = self.page
            batch_size = 10

            while True:
                if max_pages and page >= self.page + max_pages:
                    log(f"\n✓ Reached max pages: {max_pages}")
                    break

                listings = await self.scrape_page(session, page)
                if not listings:
                    log("\n✓ No more listings. Done!")
                    break

                # Process in batches
                for i in range(0, len(listings), batch_size):
                    batch = listings[i:i + batch_size]
                    tasks = [self.scrape_detail(session, l) for l in batch]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    valid = [r for r in results if r and not isinstance(r, Exception)]

                    if valid:
                        self.save_csv(valid)

                    self.page = page
                    self.save_progress()

                    log(f"  ✓ Batch: {len(valid)}/{len(batch)} saved")

                page += 1
                await asyncio.sleep(2)

        log(f"\n{'='*60}")
        log(f"Scraping Complete!")
        log(f"Total processed: {len(self.processed)}")
        log(f"Failed: {len(self.failed)}")
        log(f"Output: {self.CSV_FILE}")
        log(f"{'='*60}\n")


async def main():
    parser = argparse.ArgumentParser(description='Scrape unvan.az')
    parser.add_argument('--max-pages', type=int, help='Max pages to scrape')
    parser.add_argument('--city', default='31', help='City code')
    parser.add_argument('--concurrent', type=int, default=5, help='Concurrent requests')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests')
    parser.add_argument('--reset', action='store_true', help='Reset progress')

    args = parser.parse_args()

    if args.reset:
        if Path(UnvanScraper.PROGRESS_FILE).exists():
            Path(UnvanScraper.PROGRESS_FILE).unlink()
            log("✓ Progress reset")

    scraper = UnvanScraper(
        city=args.city,
        concurrent=args.concurrent,
        delay=args.delay
    )

    try:
        await scraper.scrape(max_pages=args.max_pages)
    except KeyboardInterrupt:
        log("\n\n⚠ Interrupted! Progress saved. Run again to resume.")
        scraper.save_progress()
    except Exception as e:
        log(f"\n✗ Error: {e}")
        scraper.save_progress()
        raise


if __name__ == '__main__':
    asyncio.run(main())
