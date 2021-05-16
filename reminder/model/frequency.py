from dataclasses import dataclass


@dataclass
class Frequency():
    cron: str = ""
    time_zone: str = 'Asia/Kolkata'
    start_time: str = None
    end_time: str = None
