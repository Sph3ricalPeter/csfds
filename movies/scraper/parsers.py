from bs4 import BeautifulSoup
from unidecode import unidecode

BASE_URL = "https://www.csfd.cz"

# <article id="highlight-2294" class="article article-poster-60">
#     <figure class="article-img">
#         <a href="/film/2294-vykoupeni-z-veznice-shawshank/prehled/" title="Vykoupení z věznice Shawshank">
#             <img src="//image.pmgstatic.com/cache/resized/w60h85/files/images/film/posters/162/505/162505167_735db9.jpg"
#                 loading="lazy" width="60" height="84"
#                 srcset="//image.pmgstatic.com/cache/resized/w60h85/files/images/film/posters/162/505/162505167_735db9.jpg 1x, //image.pmgstatic.com/cache/resized/w120h170/files/images/film/posters/162/505/162505167_735db9.jpg 2x, //image.pmgstatic.com/cache/resized/w180h255/files/images/film/posters/162/505/162505167_735db9.jpg 3x"
#                 alt="Vykoupení z věznice Shawshank">
#         </a>
#     </figure>
#     <div class="article-content article-content-toplist">
#         <header class="article-header">
#             <h3 class="film-title-norating">
#                 <span class="film-title-user">
#                     1.
#                 </span>
#                 <a href="/film/2294-vykoupeni-z-veznice-shawshank/prehled/" title="Vykoupení z věznice Shawshank"
#                     class="film-title-name">
#                     Vykoupení z věznice Shawshank
#                 </a>
#                 <span class="film-title-info">
#                     <span class="info">(1994)</span>
#                 </span>
#             </h3>
#         </header>

#         <p class="film-origins-genres"><span class="info"><span class="info-country">USA</span>, Drama / Krimi</span>
#         </p>
#         <p class="film-creators">Režie: <a href="/tvurce/2869-frank-darabont/prehled/">Frank Darabont</a></p>
#         <p class="film-creators">Hrají: <a href="/tvurce/103-tim-robbins/prehled/">Tim Robbins</a>, <a
#                 href="/tvurce/92-morgan-freeman/prehled/">Morgan Freeman</a></p>
#         <div class="article-toplist-rating">
#             <div class="rating-average red">95,4%</div>
#             <div class="rating-total">
#                 115&nbsp;885 <span>hodnocení</span>
#                 <span class="rating-mobile">hodn.</span>
#             </div>
#         </div>
#     </div>
# </article>


def parse_list(html: str) -> list[dict]:
    """Parse HTML of the film list page, extract rank, title, year, URL."""

    soup = BeautifulSoup(html, 'html.parser')
    films = []

    for article in soup.select('article.article-poster-60'):
        rank = int(article.select_one(
            '.film-title-user').text.strip().rstrip('.'))
        title = article.select_one('.film-title-name').text.strip()
        year_text = article.select_one('.film-title-info .info').text.strip()
        year = int(year_text.strip('()')) if year_text else None
        url = f"{BASE_URL}{article.select_one('.film-title-name')['href']}"
        films.append({
            'rank': rank,
            'title': title,
            'title_normalized': normalize(title),
            'year': year,
            'csfd_url': url,
            'actors': []  # Placeholder for actors, to be filled in detail parsing
        })

    return films


# <div class="creators" id="creators">
#     ...
#     <div>
#         <h4>Hudba:</h4>
#         <a href="/tvurce/62417-thomas-newman/prehled/">Thomas Newman</a>
#     </div>
#     <div>
#         <h4>Hrají:</h4>
#         <a href="/tvurce/103-tim-robbins/prehled/">Tim Robbins</a>,
#         <a href="/tvurce/92-morgan-freeman/prehled/">Morgan Freeman</a>,
#         <a href="/tvurce/202-bob-gunton/prehled/">Bob Gunton</a>,
#         ...
#     </div>
#     <div class="other-professions hidden">
#         <h4>Produkce:</h4>
#         <span>
#             <a href="/tvurce/381729-niki-marvin/prehled/">Niki Marvin</a>
#         </span>
#     </div>
#     ...
# </div>


def parse_detail(html: str) -> dict:
    """Parse HTML of the film detail page, extract actors."""

    soup = BeautifulSoup(html, 'html.parser')
    actors = []

    for a in soup.select('div.creators div:has(h4:-soup-contains("Hrají")) a[href^="/tvurce/"]'):
        name = a.text.strip()
        url = f"{BASE_URL}{a['href']}"
        actors.append({
            'name': name,
            'name_normalized': normalize(name),
            'csfd_url': url
        })
    return {'actors': actors}

def normalize(s: str) -> str:
    return unidecode(s).strip().lower()
