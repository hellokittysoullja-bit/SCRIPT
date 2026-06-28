# src/pexels/api.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import os
import time
import requests


class PexelsAPIError(RuntimeError):
    """Raised when the Pexels API returns an error response."""


@dataclass
class RateLimitInfo:
    limit: Optional[int] = None
    remaining: Optional[int] = None
    reset: Optional[int] = None


class PexelsClient:
    """
    Minimal Pexels API client for photos and videos.

    Auth:
        Authorization: YOUR_API_KEY
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.pexels.com/v1",
        timeout: int = 30,
    ) -> None:
        self.api_key = (api_key or os.getenv("PEXELS_API_KEY", "")).strip()
        if not self.api_key:
            raise PexelsAPIError(
                "PEXELS_API_KEY is missing. Put it into your environment or .env file."
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": self.api_key,
                "User-Agent": "auto-editor/1.0",
                "Accept": "application/json",
            }
        )
        self.last_rate_limit = RateLimitInfo()

    def _request(self, method: str, url: str, params: Optional[dict] = None) -> Dict[str, Any]:
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise PexelsAPIError(f"Network error while calling Pexels: {exc}") from exc

        self._update_rate_limit(response.headers)

        if response.status_code == 429:
            raise PexelsAPIError(
                "Pexels rate limit exceeded. Check X-Ratelimit-Remaining / X-Ratelimit-Reset."
            )

        if not response.ok:
            message = response.text.strip()
            raise PexelsAPIError(
                f"Pexels API error {response.status_code} for {url}: {message[:300]}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise PexelsAPIError("Pexels returned invalid JSON.") from exc

    def _update_rate_limit(self, headers: Dict[str, str]) -> None:
        def _get_int(name: str) -> Optional[int]:
            raw = headers.get(name)
            if raw is None:
                return None
            try:
                return int(raw)
            except (TypeError, ValueError):
                return None

        self.last_rate_limit = RateLimitInfo(
            limit=_get_int("X-Ratelimit-Limit"),
            remaining=_get_int("X-Ratelimit-Remaining"),
            reset=_get_int("X-Ratelimit-Reset"),
        )

    def get_rate_limit(self) -> RateLimitInfo:
        return self.last_rate_limit

    # -------------------------
    # Photos
    # -------------------------
    def search_photos(
        self,
        query: str,
        page: int = 1,
        per_page: int = 15,
        orientation: Optional[str] = None,
        size: Optional[str] = None,
        color: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search Pexels photos.
        """
        params: Dict[str, Any] = {
            "query": query,
            "page": page,
            "per_page": per_page,
        }
        if orientation:
            params["orientation"] = orientation
        if size:
            params["size"] = size
        if color:
            params["color"] = color

        return self._request("GET", f"{self.base_url}/search", params=params)

    # -------------------------
    # Videos
    # -------------------------
    def search_videos(
        self,
        query: str,
        page: int = 1,
        per_page: int = 15,
        orientation: Optional[str] = None,
        size: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search Pexels videos.
        """
        params: Dict[str, Any] = {
            "query": query,
            "page": page,
            "per_page": per_page,
        }
        if orientation:
            params["orientation"] = orientation
        if size:
            params["size"] = size

        return self._request("GET", f"{self.base_url}/videos/search", params=params)

    def popular_videos(
        self,
        page: int = 1,
        per_page: int = 15,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        orientation: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get popular Pexels videos.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        if min_width is not None:
            params["min_width"] = min_width
        if min_height is not None:
            params["min_height"] = min_height
        if orientation:
            params["orientation"] = orientation

        return self._request("GET", f"{self.base_url}/videos/popular", params=params)

    # -------------------------
    # Helpers
    # -------------------------
    @staticmethod
    def choose_best_video_file(video: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pick the best available file from Pexels video metadata.

        Heuristic:
        - prefer larger resolution
        - prefer more FPS if available
        - prefer mp4
        """
        files = video.get("video_files", []) or []
        if not files:
            raise PexelsAPIError("Video item does not contain video_files.")

        def score(item: Dict[str, Any]) -> Tuple[int, int, int, int]:
            width = int(item.get("width") or 0)
            height = int(item.get("height") or 0)
            fps = int(item.get("fps") or 0)
            file_type = str(item.get("file_type") or "").lower()
            mp4_bonus = 1 if file_type == "video/mp4" else 0
            return (width * height, fps, mp4_bonus, width)

        return sorted(files, key=score, reverse=True)[0]

    @staticmethod
    def best_preview_picture(video: Dict[str, Any]) -> Optional[str]:
        """
        Return the first preview picture URL if present.
        """
        pics = video.get("video_pictures", []) or []
        if not pics:
            return None
        first = pics[0] or {}
        return first.get("picture")

    def search_all_videos(
        self,
        query: str,
        max_results: int = 30,
        per_page: int = 15,
        orientation: Optional[str] = None,
        size: Optional[str] = None,
        sleep_between_pages: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Collect results across pages until max_results is reached.
        """
        results: List[Dict[str, Any]] = []
        page = 1

        while len(results) < max_results:
            payload = self.search_videos(
                query=query,
                page=page,
                per_page=min(per_page, 80),
                orientation=orientation,
                size=size,
            )
            batch = payload.get("videos", []) or []
            if not batch:
                break

            results.extend(batch)
            if len(batch) < min(per_page, 80):
                break

            page += 1
            if sleep_between_pages > 0:
                time.sleep(sleep_between_pages)

        return results[:max_results]

    def search_all_photos(
        self,
        query: str,
        max_results: int = 30,
        per_page: int = 15,
        orientation: Optional[str] = None,
        size: Optional[str] = None,
        color: Optional[str] = None,
        sleep_between_pages: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Collect photo results across pages until max_results is reached.
        """
        results: List[Dict[str, Any]] = []
        page = 1

        while len(results) < max_results:
            payload = self.search_photos(
                query=query,
                page=page,
                per_page=min(per_page, 80),
                orientation=orientation,
                size=size,
                color=color,
            )
            batch = payload.get("photos", []) or []
            if not batch:
                break

            results.extend(batch)
            if len(batch) < min(per_page, 80):
                break

            page += 1
            if sleep_between_pages > 0:
                time.sleep(sleep_between_pages)

        return results[:max_results]

    @staticmethod
    def download_file(url: str, destination: Path, chunk_size: int = 1024 * 1024) -> Path:
        """
        Download any file by URL to destination.
        """
        destination.parent.mkdir(parents=True, exist_ok=True)

        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with destination.open("wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)

        return destination