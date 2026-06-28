from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional
import json


# ---------------------------------------------------
# ENUMS
# ---------------------------------------------------

class MediaType(str, Enum):
    VIDEO = "video"
    PHOTO = "photo"
    AUTO = "auto"


class Emotion(str, Enum):
    NEUTRAL = "neutral"
    CALM = "calm"
    HAPPY = "happy"
    SAD = "sad"
    ANXIETY = "anxiety"
    SCIENTIFIC = "scientific"
    DRAMATIC = "dramatic"
    MOTIVATIONAL = "motivational"


class CameraMotion(str, Enum):
    STATIC = "static"
    SLOW = "slow"
    FAST = "fast"
    HANDHELD = "handheld"


class Transition(str, Enum):
    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"


# ---------------------------------------------------
# SEARCH QUERY
# ---------------------------------------------------

@dataclass
class SearchQuery:

    text: str
    weight: float = 1.0

    def to_dict(self):
        return asdict(self)


# ---------------------------------------------------
# SCENE
# ---------------------------------------------------

@dataclass
class Scene:

    id: int

    start: float
    end: float

    narration: str

    duration: float

    emotion: Emotion = Emotion.NEUTRAL

    media_type: MediaType = MediaType.AUTO

    camera_motion: CameraMotion = CameraMotion.SLOW

    transition: Transition = Transition.FADE

    importance: float = 0.5

    role: str = ""

    keywords: List[SearchQuery] = field(default_factory=list)

    selected_media: Optional[str] = None

    metadata: dict = field(default_factory=dict)

    @property
    def length(self):

        return round(self.end - self.start, 3)

    def to_dict(self):

        data = asdict(self)

        data["emotion"] = self.emotion.value
        data["media_type"] = self.media_type.value
        data["camera_motion"] = self.camera_motion.value
        data["transition"] = self.transition.value

        return data

    def to_json(self):

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            indent=4
        )


# ---------------------------------------------------
# TIMELINE
# ---------------------------------------------------

@dataclass
class Timeline:

    scenes: List[Scene] = field(default_factory=list)

    total_duration: float = 0

    def add(self, scene: Scene):

        self.scenes.append(scene)

        self.total_duration = max(
            self.total_duration,
            scene.end
        )

    def sort(self):

        self.scenes.sort(
            key=lambda s: s.start
        )

    def to_dict(self):

        return {

            "duration": self.total_duration,

            "scenes": [

                s.to_dict()

                for s in self.scenes

            ]

        }

    def to_json(self):

        return json.dumps(

            self.to_dict(),

            ensure_ascii=False,

            indent=4

        )