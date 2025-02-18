from dataclasses import dataclass, field
from datetime import datetime

from libs.typing.scenario import BaseModel, BaseDocument


@dataclass
class ImpactDuration(BaseModel):
    start: datetime
    end: datetime


@dataclass
class EventMetric(BaseModel):
    name: str
    probability: str
    overview: str
    process: str
    risk: str


@dataclass
class EventCase(BaseModel):
    version: str
    name: str
    probability: str
    overview: str
    process: str
    risk: str


@dataclass
class Timeline(BaseModel):
    time: datetime
    status: str
    impact: str


@dataclass
class Evidence(BaseModel):
    name: str
    url: str


@dataclass
class Reference(BaseModel):
    name: str
    url: str


@dataclass
class EventScenario(BaseDocument):
    impact_level: str = ""
    overview: str = ""
    impact_duration: ImpactDuration | None = None
    event_metrics: EventMetric | None = None
    event_cases: list[EventCase] = field(default_factory=list)
    timeline: list[Timeline] = field(default_factory=list)
    evidences: list[Evidence] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
