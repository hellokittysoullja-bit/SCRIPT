from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .knowledge_base import KnowledgeBase
from .roles import get_role


@dataclass
class AssetCandidate:

    role: str

    query: str

    priority: float


class AssetSelector:

    """
    Выбирает лучшие поисковые запросы
    для конкретной сцены.

    Planner вообще ничего не знает
    про Pexels.

    Он знает только роль.

    AssetSelector превращает роль
    в реальные поисковые запросы.
    """

    def __init__(self, kb: KnowledgeBase):

        self.kb = kb

    def prepare_role(self, role_name: str):

        role = get_role(role_name)

        for index, query in enumerate(role.searches):

            score = 100 - index

            self.kb.add_query(

                role_name,

                query,

                score

            )

    def choose_queries(

        self,

        role_name: str,

        amount: int = 4

    ) -> List[AssetCandidate]:

        self.prepare_role(role_name)

        queries = self.kb.choose(

            role_name,

            amount

        )

        result = []

        for q in queries:

            entry = self.kb.roles[role_name][q]

            result.append(

                AssetCandidate(

                    role=role_name,

                    query=q,

                    priority=entry.score

                )

            )

        result.sort(

            key=lambda x: x.priority,

            reverse=True

        )

        return result