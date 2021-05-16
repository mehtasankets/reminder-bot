import logging
from reminder.dao.event_dao import EventDao
from reminder.model.event import Event
from croniter import croniter
from datetime import datetime, timedelta
import time
from reminder.dao.config_dao import ConfigDao

log = logging.getLogger(__name__)


class EventCreator():
    def __init__(self, connection):
        self.config_dao = ConfigDao(connection)
        self.event_dao = EventDao(connection)

    def create(self):
        log.info("Event creator started!")
        self.sleep_until_start_of_hour()
        while(True):
            try:
                from_datetime = datetime.now()
                until_datetime = from_datetime + timedelta(hours=12)
                log.info(
                    f"starting event creation from {from_datetime} until {until_datetime}")
                configs = self.config_dao.fetch_all()
                for config in configs:
                    iter = croniter(config.frequency.cron, from_datetime)
                    next_occurrence = iter.get_next(datetime)
                    while(next_occurrence <= until_datetime):
                        log.debug(
                            f"I will create new event to occur at {next_occurrence} for {config.todo}")
                        new_event = Event(None, config.id, config.config_group_identity, config.todo,
                                          next_occurrence, config.repetition_count, config.snooze_for_minutes)
                        self.event_dao.upsert(new_event)
                        next_occurrence = iter.get_next(datetime)
            except Exception as e:
                log.error(e)
            finally:
                time.sleep(10 * 60 * 60)

    def sleep_until_start_of_hour(self):
        now = datetime.now()
        next_hour = (now + timedelta(hours=1)
                     ).replace(microsecond=0, second=0, minute=0)
        wait_seconds = (next_hour - now).seconds
        log.debug(f"Current time is {now}")
        log.info(f"Sleeping for {wait_seconds} seconds i.e. until {next_hour}")
        time.sleep(wait_seconds)
