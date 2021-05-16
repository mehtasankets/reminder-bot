from datetime import datetime, timedelta
import logging
from reminder.dao.subscription_dao import SubscriptionDao
from reminder.dao.event_dao import EventDao
import time

log = logging.getLogger(__name__)

class EventNotifier():
    def __init__(self, telegram_interactor, connection):
        self.telegram_interactor = telegram_interactor
        self.event_dao = EventDao(connection)

    def notify(self):
        log.info("Event notifier started!")
        while (True):
            try:
                current_time = datetime.now()
                log.debug(f"starting event notifier at {current_time}")
                events = self.event_dao.fetch_all_active()
                events_to_be_notified = []
                for event in events:
                    if event.next_trigger_time < current_time:
                        events_to_be_notified.append(event)
                log.debug(events_to_be_notified)
                if len(events_to_be_notified) > 0:
                    log.info(f"Events to be notified: {events_to_be_notified}")
                    self.send_telegram_notification(events_to_be_notified)
                    self.update_next_occurrence(events_to_be_notified)
            except Exception as e:
                log.error(e)
            finally:
                time.sleep(30)

    def send_telegram_notification(self, events):
        group_messages = {}
        for event in events:
            message = f"{event.id}. {event.todo} @ {event.next_trigger_time}\n"
            group_messages[event.config_group_identity] = group_messages.get(
                event.config_group_identity, "") + message
        self.telegram_interactor.notify(group_messages)

    def update_next_occurrence(self, events):
        for event in events:
            event.next_trigger_time = event.next_trigger_time + \
                timedelta(minutes=event.snooze_for_minutes)
            event.remaining_repetition_count -= 1
            self.event_dao.update(event)
