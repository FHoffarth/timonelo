"""
src/timonelo/harvester/fetcher.py

Polite HTTP Fetcher with robots.txt compliance and rate limiting.
"""

import time
import urllib.request
import urllib.robotparser
import urllib.parse
from typing import Tuple, Optional, Dict
from timonelo.harvester.config import MSC_SOURCE_CONFIG


class ArtifactFetcher:
    def __init__(self, config: Dict = MSC_SOURCE_CONFIG):
        self.config = config
        self.robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self.last_request_time: float = 0.0

    def get_robots_parser(self, base_url: str) -> urllib.robotparser.RobotFileParser:
        parsed = urllib.parse.urlparse(base_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        if domain in self.robots_cache:
            return self.robots_cache[domain]

        rp = urllib.robotparser.RobotFileParser()
        robots_url = urllib.parse.urljoin(domain, "/robots.txt")
        rp.set_url(robots_url)
        try:
            req = urllib.request.Request(robots_url, headers={"User-Agent": self.config["user_agent"]})
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode("utf-8", errors="ignore")
                rp.parse(content.splitlines())
        except Exception:
            # If robots.txt is unavailable or 404, default to allow
            rp.allow_all = True

        self.robots_cache[domain] = rp
        return rp

    def is_url_allowed(self, url: str) -> bool:
        if not self.config.get("respect_robots_txt", True):
            return True
        try:
            rp = self.get_robots_parser(url)
            return rp.can_fetch(self.config["user_agent"], url)
        except Exception:
            return True

    def fetch_url(self, url: str) -> Tuple[bool, int, str, bytes, Optional[str]]:
        """
        Fetches an artifact over HTTP.
        Returns: (success, status_code, final_url, data, error_message)
        """
        # 1. Robots.txt check
        if not self.is_url_allowed(url):
            return False, 403, url, b"", "ROBOTS_BLOCKED"

        # 2. Polite rate limiting
        now = time.time()
        elapsed = now - self.last_request_time
        delay = self.config.get("request_delay_seconds", 1.0)
        if elapsed < delay:
            time.sleep(delay - elapsed)

        headers = {
            "User-Agent": self.config["user_agent"],
            "Accept": "application/pdf,application/xhtml+xml,text/html;q=0.9,*/*;q=0.8"
        }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                self.last_request_time = time.time()
                status_code = response.getcode()
                final_url = response.geturl()
                data = response.read()
                return True, status_code, final_url, data, None
        except urllib.error.HTTPError as he:
            self.last_request_time = time.time()
            return False, he.code, url, b"", f"HTTP_ERROR_{he.code}"
        except Exception as e:
            self.last_request_time = time.time()
            return False, 0, url, b"", f"FETCH_EXCEPTION: {str(e)}"
