from django.test import TestCase
from django.urls import reverse

from movies.models import Actor, Film
from movies.normalize import normalize


class NormalizeTests(TestCase):
    def test_normalize(self):
        self.assertEqual(normalize("    Český Film   "), "cesky film")
        self.assertEqual(normalize("Nejkulaťoulinkatější"), "nejkulatoulinkatejsi")
        self.assertEqual(normalize("ČSFD"), "csfd")


class SearchViewTests(TestCase):
    def setUp(self):
        self.film = Film.objects.create(
            rank=1,
            title="Vykoupení z věznice Shawshank",
            title_normalized="vykoupeni z veznice shawshank",
            year=1994,
            csfd_url="https://x/1",
        )
        self.actor = Actor.objects.create(
            name="Tim Robbins",
            name_normalized="tim robbins",
            csfd_url="https://x/a/1",
        )

    def test_search(self):
        resp = self.client.get(reverse("movies:search"), {"q": "vykoupeni"})
        self.assertContains(resp, "Vykoupení")

        resp = self.client.get(reverse("movies:search"), {"q": "VyKOUpeňÍ"})
        self.assertContains(resp, "Vykoupení")

        resp = self.client.get(reverse("movies:search"), {"q": "TIM"})
        self.assertContains(resp, "Tim Robbins")

    def test_search_negative(self):
        rest = self.client.get(reverse("movies:search"))
        self.assertNotContains(rest, "Tim Robbins")


class DetailViewTests(TestCase):
    def setUp(self):
        self.film = Film.objects.create(
            rank=1, title="Matrix", title_normalized="matrix", year=1999, csfd_url="https://x/1"
        )

    def test_film_detail_renders(self):
        resp = self.client.get(reverse("movies:film_detail", args=[self.film.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Matrix")

    def test_film_detail_404(self):
        resp = self.client.get(reverse("movies:film_detail", args=[9999]))
        self.assertEqual(resp.status_code, 404)
