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
    def __init__(self, name: str, url: str, headers: dict | None = None):
        self.name = name
        self.url = url
        self.headers = {**DEFAULT_HEADERS, **(headers or {})}
        self._cached_text: str | None = None
        self._cached_json: object | None = None

    def fetch_text(self) -> str:
        if self._cached_text is None:
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
