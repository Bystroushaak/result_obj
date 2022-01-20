#! /usr/bin/env python3
import time
from typing import Any
from dataclasses import field
from dataclasses import dataclass


@dataclass
class MetricInfo:
    type: int
    tags: dict
    value: Any = None
    timestamp: float = field(init=False)

    def __post_init__(self):
        self.timestamp = time.time()


class Metrics:
    def __init__(self):
        self._metrics = {}
        self._stream = []

    def add_to_stream(self, info):
        self._stream.append(info)

    def __getattr__(self, item):
        return Metric(item, self)


class Metric:
    TYPE_START = 0
    TYPE_STOP = 1
    TYPE_INCREMENT = 2
    TYPE_VALUE = 3

    def __init__(self, name, metrics):
        self.name = name
        self.metrics = metrics

    def start(self, **kwargs):
        self.metrics.add_to_stream(MetricInfo(self.TYPE_START, kwargs))

    def stop(self, **kwargs):
        self.metrics.add_to_stream(MetricInfo(self.TYPE_STOP, kwargs))

    def increment(self, **kwargs):
        self.metrics.add_to_stream(MetricInfo(self.TYPE_INCREMENT, kwargs))

    def value(self, value, **kwargs):
        self.metrics.add_to_stream(
            MetricInfo(self.TYPE_VALUE, kwargs, value)
        )


class Result:
    def __init__(self, path=None):
        self.path = path if path is not None else self._get_path()
        self.metrics = Metrics()

    def _get_path(self):
        return "/tmp"
