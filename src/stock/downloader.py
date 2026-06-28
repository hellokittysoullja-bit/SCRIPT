from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import hashlib

from src.pexels.api import PexelsClient


@dataclass
class DownloadedAsset:

    pexels_id: int

    role: str

    query: str

    path: Path

    width: int

    height: int

    duration: float

    media_type: str

    photographer: str


class Downloader:

    """
    Главный класс загрузки ассетов.

    Получает поисковый запрос.

    Находит лучший ассет.

    Проверяет кэш.

    При необходимости скачивает.

    Возвращает DownloadedAsset.
    """

    def __init__(

        self,

        client: PexelsClient,

        cache_dir: Path

    ):

        self.client = client

        self.cache_dir = cache_dir

        self.video_dir = cache_dir / "videos"

        self.photo_dir = cache_dir / "photos"

        self.video_dir.mkdir(

            parents=True,

            exist_ok=True

        )

        self.photo_dir.mkdir(

            parents=True,

            exist_ok=True

        )
        
    # ---------------------------------------------------------

    def _video_path(self, pexels_id: int) -> Path:
        return self.video_dir / f"{pexels_id}.mp4"

    # ---------------------------------------------------------

    def _photo_path(self, pexels_id: int) -> Path:
        return self.photo_dir / f"{pexels_id}.jpg"

    # ---------------------------------------------------------

    def has_video(self, pexels_id: int) -> bool:
        return self._video_path(pexels_id).exists()

    # ---------------------------------------------------------

    def has_photo(self, pexels_id: int) -> bool:
        return self._photo_path(pexels_id).exists()

    # ---------------------------------------------------------

    def download_video(

        self,

        role: str,

        query: str

    ) -> Optional[DownloadedAsset]:

        response = self.client.search_videos(

            query=query,

            per_page=15,

            orientation="landscape"

        )

        videos = response.get("videos", [])

        if not videos:
            return None

        best = videos[0]

        best_file = self.client.choose_best_video_file(best)

        pexels_id = best["id"]

        destination = self._video_path(pexels_id)

        if not destination.exists():

            self.client.download_file(

                best_file["link"],

                destination

            )

        return DownloadedAsset(

            pexels_id=pexels_id,

            role=role,

            query=query,

            path=destination,

            width=best_file.get("width", 0),

            height=best_file.get("height", 0),

            duration=best.get("duration", 0),

            media_type="video",

            photographer=best.get("user", {}).get("name", "")

        )

    # ---------------------------------------------------------

    def download_photo(

        self,

        role: str,

        query: str

    ) -> Optional[DownloadedAsset]:

        response = self.client.search_photos(

            query=query,

            per_page=15,

            orientation="landscape"

        )

        photos = response.get("photos", [])

        if not photos:
            return None

        best = photos[0]

        pexels_id = best["id"]

        destination = self._photo_path(pexels_id)

        if not destination.exists():

            self.client.download_file(

                best["src"]["original"],

                destination

            )

        return DownloadedAsset(

            pexels_id=pexels_id,

            role=role,

            query=query,

            path=destination,

            width=best.get("width", 0),

            height=best.get("height", 0),

            duration=0,

            media_type="photo",

            photographer=best.get("photographer", "")

        )

    # ---------------------------------------------------------

    def md5(

        self,

        path: Path

    ) -> str:

        h = hashlib.md5()

        with open(path, "rb") as f:

            while True:

                chunk = f.read(1024 * 1024)

                if not chunk:
                    break

                h.update(chunk)

        return h.hexdigest()