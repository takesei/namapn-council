from dataclasses import dataclass
import json
from typing import List, Any
from datetime import datetime
import pandas as pd

JSON: type = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


@dataclass
class BaseDocument:
    name: str
    id: str
    issue_date: str
    version: str
    department: str
    responsible_person: str
    mail: str

    def to_json(self) -> str:
        json.dumps(self)


@dataclass
class ProcessCaller:
    name: str
    kwargs: dict[str, Any]


# TODO: pandera, version, compare with what?
@dataclass
class Forecast:
    name: str
    keys: list[str]
    values: list[str]
    df: pd.DataFrame
    segments: list[str]

    diff: pd.DataFrame | None


@dataclass
class Forecasts:
    _contents: list[Forecast]

    def contents(self) -> list[str]:
        return [c.name for c in self._contents]

    def __getitem__(self, key: str):
        return [c for c in self.contents if c.name == key][0]


# Event
@dataclass
class ImpactDuration:
    start: datetime
    end: datetime


@dataclass
class EventMetrics:
    version: str
    name: str
    probability: str
    overview: str
    process: str
    risk: str


@dataclass
class EventScenario(BaseDocument):
    impact_level: str
    overview: str
    impact_duration: ImpactDuration
    event_metrics: EventMetrics


# Strategy
@dataclass
class Activation:
    responsible: str
    time: datetime
    conditions: str
    metrics: List[str]
    notifications: List[str]


@dataclass
class Action:
    name: str
    responsible: str
    details: str
    risk: str
    recovery_action: str


@dataclass
class StrategyScenario(BaseDocument):
    event: EventScenario
    activation: Activation
    initial_response: List[Action]
    containment_measures: List[Action]
    monitoring: List[Action]
    recovery: List[Action]
