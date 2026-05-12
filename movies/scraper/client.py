from pathlib import Path
from playwright.sync_api import sync_playwright
from hashlib import sha1


class Client:
    """Client for fetching HTML content of a URL, with caching and storage state management."""

    def __init__(
        self,
        cache_dir: Path = Path(".cache"),
        encoding: str = "utf-8",
        headless: bool = True,
    ):
        self.cache_dir = cache_dir
        self.encoding = encoding
        self.state_file = self.cache_dir / "state_storage.json"
        self.context = None
        self.browser = None
        self.headless = headless

    def __enter__(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.pw = sync_playwright().start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context is not None:
            self.context.storage_state(path=self.state_file)
        if self.browser is not None:
            self.browser.close()
        self.pw.stop()

    def fetch_html(
        self, url: str, *, wait_for_selector: str, use_cache: bool = True
    ) -> str:
        """Fetch URL via PW, write disk cache + storage_state. Return HTML."""
        url_hash = sha1(url.encode()).hexdigest()[:16]
        cache_file = self.cache_dir / f"{url_hash}.html"
        if use_cache and cache_file.exists():
            return cache_file.read_text(encoding=self.encoding)

        if not self.browser:
            self.browser = self.pw.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context(
                storage_state=str(self.state_file) if self.state_file.exists() else None
            )

        page = self.context.new_page()
        page.goto(url)
        # Wait for the specific selector that indicates the page has loaded the relevant content
        page.wait_for_selector(wait_for_selector)
        html = page.content()
        page.close()

        # Save to disk cache + storage_state
        cache_file.write_text(html, encoding=self.encoding)

        return html
