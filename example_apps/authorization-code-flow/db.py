from typing import Dict, Any, List, Optional
from datetime import datetime


class StubDatabase:
    def __init__(self, storage: Dict[str, Any] = None) -> None:
        if storage is None:
            storage = {}
        self.storage = storage

    def get(self, key: str) -> Any:
        return self.storage.get(key)

    def set_or_overwrite(self, key: str, value: Any) -> None:
        self.storage[key] = value

    def delete(self, key: str) -> None:
        if key in self.storage:
            del self.storage[key]

    def clear(self) -> None:
        self.storage.clear()
