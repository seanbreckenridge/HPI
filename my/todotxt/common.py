from typing import Any, Dict, cast, Optional
from datetime import datetime

from pytodotxt import Task  # type: ignore[import]


class Todo(Task):
    # support serializing with hpi query
    def _serialize(self) -> Dict[str, Any]:
        assert self._raw is not None
        return {
            "completed": self.is_completed,
            "completion_date": self.completion_date,
            "deadline": self.deadline,
            "creation_date": self.creation_date,
            "priority": self.priority,
            "text": self.bare_description(),
            "projects": self.projects,
            "contexts": self.contexts,
            "attributes": self.attributes,
            "raw": self._raw,
        }

    @property
    def bare(self) -> str:
        if hasattr(self, "_bare"):
            return str(self._bare)
        setattr(self, "_bare", self.bare_description())
        return cast(str, self._bare)

    # parse the deadline created by https://github.com/seanbreckenridge/full_todotxt
    # this is optional, so if it fails, just return None
    @property
    def deadline(self) -> Optional[datetime]:
        attrs = self.attributes
        if not attrs:
            return None
        if not isinstance(attrs, dict):
            return None
        if "deadline" in attrs:
            try:
                data = attrs["deadline"][0]
                parsed = datetime.strptime(data, "%Y-%m-%dT%H-%M%z")
                return parsed
            except ValueError:
                pass
        return None

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Task):
            return False
        return cast(bool, self.bare == other.bare)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.bare)


TODOTXT_FILES = ["todo.txt", "done.txt"]
