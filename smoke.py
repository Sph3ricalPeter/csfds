from json import dump
from pathlib import Path

from movies.scraper import Client, parse_detail, parse_list

TEST_FETCH = False
OUT_DIR = Path("tmp")

with Client() as c:
    OUT_DIR.mkdir(exist_ok=True)

    html = c.fetch_html(
        "https://www.csfd.cz/zebricky/filmy/nejlepsi/",
        wait_for_selector="article.article-poster-60",
        use_cache=not TEST_FETCH,
        headless=False,
    )
    print(
        f"len={len(html)} has_films={'article-poster-60' in html} anubis_blocked={'Access Denied' in html}"
    )

    films = parse_list(html)
    print(f"Parsed {len(films)} films, first: {films[0] if films else 'N/A'}")

    films_with_actors = []
    for film in films[:1]:
        detail_html = c.fetch_html(
            film["csfd_url"], wait_for_selector="div.creators", use_cache=not TEST_FETCH
        )
        films_with_actors.append({**film, **parse_detail(detail_html)})

    print(
        f"Parsed detail for {len(films_with_actors)} films, first: {films_with_actors[0] if films else 'N/A'}"
    )

    with open(OUT_DIR / "data.json", "w", encoding="utf-8") as f:
        dump(films_with_actors, f, ensure_ascii=False, indent=2)
