"""Keyless public feed. Cache each bounded page and never execute source HTML."""
import asyncio
import time
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlparse
import httpx

_cache = {}
_lock = asyncio.Lock()

class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

def normalize(item):
    url = item.get("url", "")
    if urlparse(url).scheme != "https" or urlparse(url).hostname not in {"www.arbeitnow.com", "arbeitnow.com"}:
        raise ValueError("Unsupported source URL")
    parser = PlainText()
    parser.feed(unescape(item["description"]))
    return dict(source="arbeitnow", external_id=item["slug"][:160],
                company=item["company_name"][:160], title=item["title"][:180],
                location=item.get("location", "")[:180],
                work_type="remote" if item.get("remote") else "any",
                experience_level="unspecified", salary="", url=url,
                description=" ".join(parser.parts)[:100000],
                requirements={"required": [], "preferred": [], "source_tags": item.get("tags", []),
                              "analysis_status": "not_analyzed"},
                posted_at=datetime.fromtimestamp(item["created_at"], timezone.utc))

async def fetch_page(page):
    async with _lock:
        old = _cache.get(page)
        if old and time.monotonic() - old[0] < 3600:
            return old[1], old[2], False, old[3]
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get("https://www.arbeitnow.com/api/job-board-api", params={"page": page})
                response.raise_for_status()
                payload = response.json()
            rows = []
            for item in payload["data"]:
                try:
                    rows.append(normalize(item))
                except (KeyError, ValueError, TypeError, OverflowError):
                    continue
            fetched = datetime.now(timezone.utc).isoformat()
            more = bool(payload.get("links", {}).get("next"))
            _cache[page] = (time.monotonic(), rows, fetched, more)
            return rows, fetched, False, more
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            if old:
                return old[1], old[2], True, old[3]
            raise RuntimeError("Arbeitnow is unavailable. Please try again later.") from None
