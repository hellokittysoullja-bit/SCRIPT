from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class VisualRole:
    """
    Визуальная роль.

    Не хранит конкретное видео.
    Хранит способы показать одну и ту же идею.
    """

    name: str

    preferred_media: str = "video"

    camera_motion: str = "slow"

    emotion: str = "neutral"

    searches: List[str] = field(default_factory=list)


ROLE_LIBRARY: Dict[str, VisualRole] = {

    "phone": VisualRole(

        name="phone",

        preferred_media="video",

        camera_motion="slow",

        emotion="neutral",

        searches=[

            "scrolling phone social media",

            "phone addiction",

            "checking notifications",

            "smartphone user",

            "using smartphone at night",

            "social media feed",

            "person texting phone"

        ]

    ),

    "brain": VisualRole(

        name="brain",

        preferred_media="photo",

        emotion="scientific",

        searches=[

            "dopamine neuroscience",

            "brain neurons",

            "brain scan",

            "scientist laboratory",

            "human brain animation",

            "medical brain",

            "psychology"

        ]

    ),

    "walking": VisualRole(

        name="walking",

        preferred_media="video",

        emotion="neutral",

        searches=[

            "person walking city",

            "walking downtown",

            "walking street",

            "walking silhouette",

            "walking alone",

            "urban walking"

        ]

    ),

    "city": VisualRole(

        name="city",

        preferred_media="video",

        emotion="neutral",

        searches=[

            "city night lights",

            "busy city",

            "urban skyline",

            "street traffic",

            "night traffic",

            "city aerial"

        ]

    ),

    "nature": VisualRole(

        name="nature",

        preferred_media="video",

        emotion="calm",

        searches=[

            "nature calm peaceful",

            "forest sunlight",

            "river landscape",

            "mountain sunrise",

            "green forest",

            "waterfall"

        ]

    ),

    "meditation": VisualRole(

        name="meditation",

        preferred_media="video",

        emotion="calm",

        searches=[

            "meditation mindfulness calm",

            "person meditating",

            "peaceful meditation",

            "mindfulness",

            "breathing exercise"

        ]

    ),

    "stress": VisualRole(

        name="stress",

        preferred_media="video",

        emotion="anxiety",

        searches=[

            "stress anxiety person",

            "person overwhelmed",

            "working late",

            "burnout",

            "mental stress",

            "head in hands"

        ]

    ),

    "loneliness": VisualRole(

        name="loneliness",

        preferred_media="video",

        emotion="sad",

        searches=[

            "human connection loneliness",

            "person sitting alone",

            "empty room",

            "alone at night",

            "lonely city"

        ]

    ),

    "generic": VisualRole(

        name="generic",

        preferred_media="video",

        emotion="neutral",

        searches=[

            "cinematic lifestyle",

            "abstract background",

            "thinking person",

            "daily life",

            "close up face"

        ]

    )

}


def get_role(name: str) -> VisualRole:

    return ROLE_LIBRARY.get(

        name,

        ROLE_LIBRARY["generic"]

    )
