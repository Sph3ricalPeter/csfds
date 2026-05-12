# CSFDS - CSFD's Top 300 in Django

Search the [CSFD](https://www.csfd.cz/zebricky/filmy/nejlepsi/) top 300 films by film title or actor name.

## Stack

- Python 3.13, Django 5.2 LTS, SQLite
- Playwright (headed Chromium) for scraping to get around [Anubis](https://github.com/TecharoHQ/anubis)
- BeautifulSoup4 + lxml, Unidecode

# Setup & run

```bash
uv venv --python 3.13
.venv\Scripts\Activate.ps1            # PowerShell
# source .venv/bin/activate           # bash/zsh

uv pip install -r requirements.txt
python -m playwright install chromium

python manage.py migrate
python manage.py test

# optional re-scrape (db already contains 300 films)
python manage.py scrape --limit 300

# `--limit N` — scrape only the top N films (default 300).
# `--no-cache` — bypass the disk cache (fetched html + PW state storage) and re-fetch from CSFD.

python manage.py runserver
# Open <http://127.0.0.1:8000/>. Type into the search box. Click a result.
```

## Known Issues

- **Scraper needs headed Chromium** - without can get blocked after ~100 detail fetch requests
- **Rank 300 is missing** - pagination quirk