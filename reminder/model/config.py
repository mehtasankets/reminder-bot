from dataclasses import dataclass
from reminder.model.frequency import Frequency

@dataclass(frozen=True)
class Config():
    id: int
    config_group_identity: str
    todo: str 
    frequency: Frequency
    repetition_count: int
    snooze_for_minutes: int