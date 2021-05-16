from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event():
    id: int
    config_id: int
    config_group_identity: str
    todo: str
    next_trigger_time: datetime
    remaining_repetition_count: int
    snooze_for_minutes: int