from dataclasses import dataclass, field
from datetime import datetime

from libs.typing.scenario import BaseModel, BaseDocument
from libs.typing.event_scenario import EventScenario


# Strategy
@dataclass
class Activation(BaseModel):
    responsible: str
    time: datetime
    conditions: str
    metrics: list[str]
    notifications: list[str]


@dataclass
class Action(BaseModel):
    name: str
    responsible: str
    details: str
    risk: str
    recovery_action: str


@dataclass
class StrategyScenario(BaseDocument):
    event: EventScenario | None = None
    activation: Activation | None = None
    initial_response: list[Action] = field(default_factory=list)
    containment_measures: list[Action] = field(default_factory=list)
    monitoring: list[Action] = field(default_factory=list)
    recovery: list[Action] = field(default_factory=list)
