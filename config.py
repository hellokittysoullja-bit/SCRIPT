# config.py
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"
DOWNLOADS_DIR = BASE_DIR / "downloads"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"
LOGS_DIR = BASE_DIR / "logs"

VIDEO_CACHE_DIR = CACHE_DIR / "videos"
PHOTO_CACHE_DIR = CACHE_DIR / "photos"
METADATA_DIR = CACHE_DIR / "metadata"
SRC_DIR = BASE_DIR / "src"


def ensure_directories() -> None:
    for path in [
        DATA_DIR,
        CACHE_DIR,
        DOWNLOADS_DIR,
        OUTPUT_DIR,
        TEMP_DIR,
        LOGS_DIR,
        VIDEO_CACHE_DIR,
        PHOTO_CACHE_DIR,
        METADATA_DIR,
        SRC_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class PexelsConfig:
    api_key: str = field(default_factory=lambda: os.getenv("PEXELS_API_KEY", "").strip())
    base_url: str = "https://api.pexels.com/v1"
    per_page: int = 15
    max_results_per_query: int = 15
    orientation: str = "landscape"


@dataclass(frozen=True)
class RenderConfig:
    width: int = 1920
    height: int = 1080
    fps: int = 30
    photo_duration: float = 8.0
    video_duration: float = 10.0
    transition_duration: float = 0.35
    audio_volume: float = 1.0
    stock_frontload_seconds: int = 300
    default_video_bitrate: str = "10M"
    default_audio_bitrate: str = "192k"


@dataclass(frozen=True)
class ScriptConfig:
    encoding: str = "utf-8"
    default_language: str = "ru"
    scene_min_seconds: int = 8
    scene_max_seconds: int = 22
    max_keywords_per_scene: int = 6


@dataclass(frozen=True)
class AppConfig:
    project_name: str = "auto_editor"
    pexels: PexelsConfig = field(default_factory=PexelsConfig)
    render: RenderConfig = field(default_factory=RenderConfig)
    script: ScriptConfig = field(default_factory=ScriptConfig)

    default_stock_queries: List[str] = field(
        default_factory=lambda: [
            "scrolling phone social media",
            "dopamine neuroscience",
            "person thinking alone",
            "city night lights",
            "meditation mindfulness calm",
            "person walking city",
            "abstract mind psychology",
            "human connection loneliness",
            "morning routine lifestyle",
            "stress anxiety person",
            "nature calm peaceful",
        ]
    )


CONFIG = AppConfig()


def project_paths() -> dict[str, Path]:
    return {
        "base": BASE_DIR,
        "data": DATA_DIR,
        "cache": CACHE_DIR,
        "downloads": DOWNLOADS_DIR,
        "output": OUTPUT_DIR,
        "temp": TEMP_DIR,
        "logs": LOGS_DIR,
        "video_cache": VIDEO_CACHE_DIR,
        "photo_cache": PHOTO_CACHE_DIR,
        "metadata": METADATA_DIR,
    }