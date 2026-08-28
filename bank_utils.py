import json
import urllib.request
import urllib.error

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class BankFetcher:
    def __init__(self, name: str, url: str, headers: dict | None = None, use_browser: bool = False):
        self.name = name
        self.url = url
        self.headers = {**DEFAULT_HEADERS, **(headers or {})}
        self.use_browser = use_browser
        self._cached_text: str | None = None
        self._cached_json: object | None = None

    def fetch_text(self) -> str:
        if self._cached_text is None:
            if self.use_browser:
                self._cached_text = self._fetch_text_via_browser()
                return self._cached_text

            urls_to_try = [self.url]
            if "#" in self.url:
                urls_to_try.append(self.url.split("#", 1)[0])

            last_error: Exception | None = None
            for attempt, url in enumerate(urls_to_try):
                req = urllib.request.Request(url, headers=self.headers)
                try:
                    with urllib.request.urlopen(req, timeout=20) as response:
                        self._cached_text = response.read().decode("utf-8", errors="ignore")
                        return self._cached_text
                except urllib.error.HTTPError as e:
                    last_error = RuntimeError(f"HTTP error fetching {self.name}: {e.code} {e.reason}")
                    if e.code in {403, 429, 500, 502, 503, 504} and attempt < len(urls_to_try) - 1:
                        continue
                    raise last_error
                except urllib.error.URLError as e:
                    last_error = RuntimeError(f"Network error fetching {self.name}: {e.reason}")
                    if attempt < len(urls_to_try) - 1:
                        continue
                    raise last_error
                except Exception as e:
                    last_error = RuntimeError(f"Unexpected error fetching {self.name}: {e}")
                    if attempt < len(urls_to_try) - 1:
                        continue
                    raise last_error

            if last_error is not None:
                raise last_error

            raise RuntimeError(f"Unable to fetch {self.name}")
        return self._cached_text

    def _fetch_text_via_browser(self) -> str:
        """Fetch via a real headless browser.

        Some bank sites (e.g. BOC, ComBank) sit behind a WAF that blocks
        plain HTTP clients outright (403) but allows real browsers through,
        regardless of the requesting IP. Playwright is only imported here so
        the plain-urllib path (used by most banks) never needs it installed.
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as e:
            raise RuntimeError(
                f"Playwright is required to fetch {self.name} "
                "(install with `pip install playwright && playwright install --with-deps chromium`)"
            ) from e

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                try:
                    page = browser.new_page(
                        user_agent=self.headers.get("User-Agent", DEFAULT_USER_AGENT)
                    )
                    # domcontentloaded is enough — the rate tables are present in
                    # the server-rendered HTML. "networkidle" never fires on some
                    # of these pages (e.g. combank.lk's chat widget long-polls).
                    page.goto(self.url, wait_until="domcontentloaded", timeout=30000)
                    return page.content()
                finally:
                    browser.close()
        except Exception as e:
            raise RuntimeError(f"Browser error fetching {self.name}: {e}") from e

    def fetch_json(self):
        if self._cached_json is None:
            self._cached_json = json.loads(self.fetch_text())
        return self._cached_json

    def fetch_all_rates(self) -> dict[str, float]:
        raise NotImplementedError

    def fetch_rate(self) -> float:
        rates = self.fetch_all_rates()
        if "USD" in rates and rates["USD"] is not None:
            return rates["USD"]
        text_len = len(self._cached_text) if self._cached_text is not None else 0
        preview = (self._cached_text or "")[:300].replace("\n", " ")
        raise RuntimeError(
            f"USD rate not found for {self.name} "
            f"(parsed {len(rates)} rates, fetched {text_len} chars, preview: {preview!r})"
        )
