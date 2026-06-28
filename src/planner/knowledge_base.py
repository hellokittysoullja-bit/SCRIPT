from __future__ import annotations

import json
import random
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List


DATABASE_VERSION = 1


@dataclass
class QueryEntry:

    query: str

    score: float = 100.0

    used: int = 0

    success: int = 0

    failed: int = 0

    last_used: str = ""


class KnowledgeBase:

    def __init__(self, db_path: str | Path):

        self.db_path = Path(db_path)

        self.roles: Dict[str, Dict[str, QueryEntry]] = {}

        self.load()

    # --------------------------------------------------

    def load(self):

        if not self.db_path.exists():

            self.roles = {}

            return

        raw = json.loads(

            self.db_path.read_text(

                encoding="utf-8"

            )

        )

        self.roles = {}

        for role, values in raw["roles"].items():

            self.roles[role] = {}

            for q, info in values.items():

                self.roles[role][q] = QueryEntry(

                    **info

                )

    # --------------------------------------------------

    def save(self):

        self.db_path.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        data = {

            "version": DATABASE_VERSION,

            "roles": {}

        }

        for role, values in self.roles.items():

            data["roles"][role] = {}

            for q, entry in values.items():

                data["roles"][role][q] = asdict(

                    entry

                )

        self.db_path.write_text(

            json.dumps(

                data,

                indent=4,

                ensure_ascii=False

            ),

            encoding="utf-8"

        )

    # --------------------------------------------------

    def ensure_role(

        self,

        role: str

    ):

        if role not in self.roles:

            self.roles[role] = {}

    # --------------------------------------------------

    def add_query(

        self,

        role: str,

        query: str,

        score: float = 100

    ):

        self.ensure_role(role)

        if query in self.roles[role]:

            return

        self.roles[role][query] = QueryEntry(

            query=query,

            score=score

        )

    # --------------------------------------------------

    def choose(

        self,

        role: str,

        amount: int = 4

    ) -> List[str]:

        self.ensure_role(role)

        entries = list(

            self.roles[role].values()

        )

        if len(entries) == 0:

            return []

        entries.sort(

            key=lambda x: (

                x.score,

                -x.used

            ),

            reverse=True

        )

        top = entries[:max(amount * 2, amount)]

        random.shuffle(top)

        top.sort(

            key=lambda x: x.score,

            reverse=True

        )

        selected = top[:amount]

        return [

            x.query

            for x in selected

        ]

    # --------------------------------------------------

    def mark_used(

        self,

        role: str,

        query: str

    ):

        if role not in self.roles:

            return

        if query not in self.roles[role]:

            return

        self.roles[role][query].used += 1

        self.roles[role][query].score *= 0.985

    # --------------------------------------------------

    def mark_success(

        self,

        role: str,

        query: str

    ):

        if role not in self.roles:

            return

        if query not in self.roles[role]:

            return

        item = self.roles[role][query]

        item.success += 1

        item.score += 3

        item.score = min(

            item.score,

            200

        )

    # --------------------------------------------------

    def mark_failed(

        self,

        role: str,

        query: str

    ):

        if role not in self.roles:

            return

        if query not in self.roles[role]:

            return

        item = self.roles[role][query]

        item.failed += 1

        item.score -= 5

        item.score = max(

            item.score,

            10

        )

    # --------------------------------------------------

    def statistics(self):

        roles = len(self.roles)

        queries = 0

        for values in self.roles.values():

            queries += len(values)

        return {

            "roles": roles,

            "queries": queries

        }
