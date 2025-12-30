# Unvan.az Scraper

One file. Crash-proof. Async. Gets phone numbers.

## Install

```bash
pip install aiohttp beautifulsoup4
```

## Use

```bash
# Scrape first 5 pages
python unvan_scraper.py --max-pages 5

# Scrape everything
python unvan_scraper.py

# Reset and start fresh
python unvan_scraper.py --reset

# Custom settings
python unvan_scraper.py --concurrent 10 --delay 0.5
```

## Output

- **listings.csv** - All data (id, title, url, category, price, description, name, phone, location, date, image)
- **progress.json** - Progress tracking (auto-resumes after crash/interrupt)

## Crash Recovery

Press Ctrl+C to stop. Run again to resume automatically.

## Tested

✓ Works
✓ Tested with 30 listings
✓ Phone numbers extracted via AJAX
✓ Progress saved after each batch
