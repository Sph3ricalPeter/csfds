from argparse import ArgumentParser
from os import environ as env

from django.core.management.base import BaseCommand
from django.db import transaction

from movies.models import Actor, Film
from movies.scraper.client import Client
from movies.scraper.parsers import parse_detail, parse_list


class Command(BaseCommand):
    help = "Scrape movie data from CSFD"

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--limit",
            type=int,
            default=300,
            help="Limit the number of films to scrape",
        )
        parser.add_argument(
            "--no-cache",
            action="store_false",
            dest="no_cache",
            default=False,
            help="Disable cache when fetching HTML",
        )

    def handle(self, *args, **options):
        env["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

        errs = []
        with Client(headless=False) as c:
            films = []
            for start_rank in [1, 100, 200]:
                try:
                    html = c.fetch_html(
                        f"https://www.csfd.cz/zebricky/filmy/nejlepsi/?from={start_rank}",
                        wait_for_selector="article.article-poster-60",
                        use_cache=not options["no_cache"],
                    )

                    films.extend(parse_list(html))
                    print(f"Parsed {len(films)} films")

                    if len(films) >= options["limit"]:
                        films = films[: options["limit"]]
                        break
                except Exception as e:
                    errs.append(str(e))

            for film_data in films:
                try:
                    detail_html = c.fetch_html(
                        film_data["csfd_url"],
                        wait_for_selector="div.creators",
                        use_cache=not options["no_cache"],
                    )
                    film_data = {**film_data, **parse_detail(detail_html)}

                    print(f"Parsed detail for {film_data['rank']} films")

                    with transaction.atomic():
                        film_obj = Film.objects.update_or_create(
                            csfd_url=film_data["csfd_url"],
                            defaults={
                                "rank": film_data["rank"],
                                "title": film_data["title"],
                                "title_normalized": film_data["title_normalized"],
                                "year": film_data["year"],
                            },
                        )[0]
                        actor_objs = [
                            Actor.objects.get_or_create(
                                csfd_url=actor["csfd_url"],
                                defaults={
                                    "name": actor["name"],
                                    "name_normalized": actor["name_normalized"],
                                },
                            )[0]
                            for actor in film_data["actors"]
                        ]
                        film_obj.actors.set(actor_objs)
                except Exception as e:
                    errs.append(str(e))

        if errs:
            print("Errors occurred during scraping:")
            for err in errs:
                print(f"- {err}")

            exit(1)
