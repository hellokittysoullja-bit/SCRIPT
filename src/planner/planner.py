from __future__ import annotations

import re
from pathlib import Path
from typing import List

from .models import (
    Scene,
    SearchQuery,
    Emotion,
    MediaType,
    CameraMotion,
    Transition,
    Timeline,
)


class ScenePlanner:

    """
    Главный мозг проекта.

    Задачи:

    1. Читает сценарий
    2. Делит его на смысловые сцены
    3. Определяет эмоцию
    4. Назначает роль
    5. Генерирует поисковые запросы
    """

    def __init__(self):

        self.min_scene_length = 10
        self.max_scene_length = 18

    # ------------------------------------------------

    def load_script(
        self,
        path: str | Path
    ) -> str:

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(path)

        return path.read_text(
            encoding="utf-8"
        )

    # ------------------------------------------------

    def split_into_sentences(
        self,
        text: str
    ) -> List[str]:

        text = text.replace("\n", " ")

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        parts = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        return [

            p.strip()

            for p in parts

            if p.strip()

        ]

    # ------------------------------------------------

    def estimate_duration(
        self,
        sentence: str
    ) -> float:

        words = len(sentence.split())

        seconds = words / 2.3

        seconds = max(
            self.min_scene_length,
            seconds
        )

        seconds = min(
            self.max_scene_length,
            seconds
        )

        return round(seconds, 2)

    # ------------------------------------------------

    def detect_emotion(
        self,
        sentence: str
    ) -> Emotion:

        s = sentence.lower()

        if any(

            x in s

            for x in [

                "stress",
                "anxiety",
                "fear",
                "panic",
                "depression",
                "lonely",
                "alone"

            ]

        ):

            return Emotion.ANXIETY

        if any(

            x in s

            for x in [

                "brain",
                "dopamine",
                "science",
                "neuron",
                "psychology"

            ]

        ):

            return Emotion.SCIENTIFIC

        if any(

            x in s

            for x in [

                "calm",
                "peace",
                "nature",
                "meditation"

            ]

        ):

            return Emotion.CALM

        if any(

            x in s

            for x in [

                "motivation",
                "success",
                "discipline"

            ]

        ):

            return Emotion.MOTIVATIONAL

        return Emotion.NEUTRAL

    # ------------------------------------------------

    def detect_role(
        self,
        sentence: str
    ) -> str:

        s = sentence.lower()

        roles = {

            "phone": [

                "phone",
                "smartphone",
                "social media",
                "instagram",
                "tiktok",
                "youtube"

            ],

            "brain": [

                "brain",
                "dopamine",
                "mind",
                "psychology",
                "neuron"

            ],

            "city": [

                "city",
                "street",
                "urban"

            ],

            "walking": [

                "walk",
                "walking"

            ],

            "nature": [

                "forest",
                "river",
                "nature",
                "mountain"

            ],

            "meditation": [

                "meditation",
                "mindfulness"

            ]

        }

        for role, words in roles.items():

            for word in words:

                if word in s:

                    return role

        return "generic"

    # ------------------------------------------------

    def generate_keywords(
        self,
        role: str
    ) -> List[SearchQuery]:

        database = {

            "phone": [

                "scrolling phone social media",

                "phone addiction",

                "person using smartphone",

                "checking notifications"

            ],

            "brain": [

                "dopamine neuroscience",

                "brain neurons",

                "scientist laboratory",

                "brain scan"

            ],

            "city": [

                "city night lights",

                "busy street",

                "urban skyline"

            ],

            "walking": [

                "person walking city",

                "walking downtown",

                "walking alone"

            ],

            "nature": [

                "nature calm peaceful",

                "beautiful forest",

                "river landscape"

            ],

            "meditation": [

                "meditation mindfulness calm",

                "peaceful meditation",

                "calm breathing"

            ],

            "generic": [

                "abstract background",

                "thinking person",

                "cinematic lifestyle"

            ]

        }

        return [

            SearchQuery(

                text=q,

                weight=1.0

            )

            for q in database.get(

                role,

                database["generic"]

            )

        ]
        
    # ------------------------------------------------

    def create_scene(
        self,
        scene_id: int,
        sentence: str,
        start_time: float
    ) -> Scene:

        duration = self.estimate_duration(sentence)

        role = self.detect_role(sentence)

        emotion = self.detect_emotion(sentence)

        media = MediaType.VIDEO

        if scene_id % 2 == 0:
            media = MediaType.PHOTO

        scene = Scene(

            id=scene_id,

            start=start_time,

            end=start_time + duration,

            duration=duration,

            narration=sentence,

            emotion=emotion,

            role=role,

            media_type=media,

            camera_motion=CameraMotion.SLOW,

            transition=Transition.FADE,

            importance=0.5,

            keywords=self.generate_keywords(role)

        )

        return scene

    # ------------------------------------------------

    def build_timeline(
        self,
        script: str
    ) -> Timeline:

        timeline = Timeline()

        sentences = self.split_into_sentences(script)

        current = 0.0

        for index, sentence in enumerate(sentences, start=1):

            scene = self.create_scene(

                index,

                sentence,

                current

            )

            timeline.add(scene)

            current = scene.end

        timeline.sort()

        return timeline

    # ------------------------------------------------

    def save_timeline(
        self,
        timeline: Timeline,
        output_file: str | Path
    ):

        output_file = Path(output_file)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file.write_text(

            timeline.to_json(),

            encoding="utf-8"

        )

    # ------------------------------------------------

    def run(
        self,
        script_path: str | Path,
        output_json: str | Path
    ) -> Timeline:

        script = self.load_script(

            script_path

        )

        timeline = self.build_timeline(

            script

        )

        self.save_timeline(

            timeline,

            output_json

        )

        return timeline


# ----------------------------------------------------
# TEST
# ----------------------------------------------------

if __name__ == "__main__":

    planner = ScenePlanner()

    timeline = planner.run(

        "../../data/script.txt",

        "../../data/timeline.json"

    )

    print()

    print("=" * 60)

    print("Timeline")

    print("=" * 60)

    print()

    print(

        timeline.to_json()

    )