import json
import urllib.request
import urllib.error

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class BankFetcher:
    def __init__(self, name: str, url: str, headers: dict | None = None):
        self.name = name
        self.url = url
        self.headers = headers or {"User-Agent": DEFAULT_USER_AGENT}
        self._cached_text: str | None = None
        self._cached_json: object | None = None

    def fetch_text(self) -> str:
        if self._cached_text is None:
            req = urllib.request.Request(self.url, headers=self.headers)
            try:
                with urllib.request.urlopen(req, timeout=15) as response:
                    self._cached_text = response.read().decode("utf-8", errors="ignore")
            except urllib.error.HTTPError as e:
                raise RuntimeError(f"HTTP error fetching {self.name}: {e.code} {e.reason}")
            except urllib.error.URLError as e:
                raise RuntimeError(f"Network error fetching {self.name}: {e.reason}")
            except Exception as e:
                raise RuntimeError(f"Unexpected error fetching {self.name}: {e}")
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
        raise RuntimeError(f"USD rate not found for {self.name}")
