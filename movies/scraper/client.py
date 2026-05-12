from hashlib import sha1
from pathlib import Path

from playwright.sync_api import sync_playwright


class Client:
    """Client for fetching HTML content of a URL, with caching and storage state management."""

    def __init__(
        self,
        cache_dir: Path = Path(".cache"),
        encoding: str = "utf-8",
        headless: bool = True,
        recycle_browser_after: int = 100,
    ):
        self.cache_dir = cache_dir
        self.encoding = encoding
        self.state_file = self.cache_dir / "state_storage.json"
        self.context = None
        self.browser = None
        self.headless = headless
        self.recycle_browser_after = recycle_browser_after
        self.recycle_counter = 0

    def __enter__(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.pw = sync_playwright().start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context is not None:
            self.context.close()
        if self.browser is not None:
            self.browser.close()
        self.pw.stop()

    def _save_state(self):
        if self.context is not None:
            self.context.storage_state(path=self.state_file)

    def fetch_html(self, url: str, *, wait_for_selector: str, use_cache: bool = True) -> str:
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
        page.wait_for_function('!document.title.startsWith("Access Denied")', timeout=5000)
        page.wait_for_selector(wait_for_selector, timeout=5000)
        html = page.content()
        page.close()

        # Save to disk cache + storage_state
        cache_file.write_text(html, encoding=self.encoding)
        self._save_state()

        self.recycle_counter += 1
        if self.recycle_counter >= self.recycle_browser_after:
            print("Recycling browser ...")
            self.context.close()
            self.browser.close()
            self.context = None
            self.browser = None
            self.recycle_counter = 0

        return html
