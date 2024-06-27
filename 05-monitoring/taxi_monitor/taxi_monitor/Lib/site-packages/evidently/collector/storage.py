import abc
from asyncio import Lock
from typing import Any
from typing import Dict
from typing import List

import pandas as pd

from evidently._pydantic_compat import BaseModel
from evidently.pydantic_utils import PolymorphicModel


class LogEvent(BaseModel):
    ok: bool
    error: str = ""


class CollectorStorage(PolymorphicModel):
    class Config:
        underscore_attrs_are_private = True

    _locks: Dict[str, Lock] = {}

    def lock(self, id: str):
        return self._locks[id]

    def init(self, id: str):
        self._locks[id] = Lock()

    def init_all(self, config):
        for id in config.collectors:
            self.init(id)

    @abc.abstractmethod
    def append(self, id: str, data: Any):
        raise NotImplementedError

    @abc.abstractmethod
    def get_buffer_size(self, id: str):
        raise NotImplementedError

    @abc.abstractmethod
    def get_and_flush(self, id: str):
        raise NotImplementedError

    @abc.abstractmethod
    def log(self, id: str, event: LogEvent):
        raise NotImplementedError

    @abc.abstractmethod
    def get_logs(self, id: str) -> List[LogEvent]:
        raise NotImplementedError


class InMemoryStorage(CollectorStorage):
    max_log_events: int = 10

    _buffers: Dict[str, List[Any]] = {}
    _logs: Dict[str, List[LogEvent]] = {}

    def init(self, id: str):
        super().init(id)
        self._buffers[id] = []
        self._logs[id] = []

    def append(self, id: str, data: Any):
        self._buffers[id].append(data)

    def get_buffer_size(self, id: str):
        return len(self._buffers[id])

    def get_and_flush(self, id: str):
        if id not in self._buffers or len(self._buffers[id]) == 0:
            return None

        res = pd.concat([pd.DataFrame.from_dict(o) for o in self._buffers[id]])
        self._buffers[id].clear()
        return res

    def log(self, id: str, event: LogEvent):
        self._logs[id].insert(0, event)
        if self.max_log_events > 0:
            self._logs[id] = self._logs[id][: self.max_log_events]

    def get_logs(self, id: str) -> List[LogEvent]:
        return self._logs.get(id, [])
