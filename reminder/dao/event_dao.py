from datetime import datetime
from reminder.model.event import Event


class EventDao():
    def __init__(self, connection):
        self.connection = connection

    def fetch_all_active(self):
        cursor = self.connection.execute(
            """
                SELECT 
                    id, config_id, config_group_identity, todo, 
                    next_trigger_time, remaining_repetition_count, 
                    snooze_for_minutes 
                FROM event
                WHERE remaining_repetition_count > 0
            """)
        events = []
        for c in cursor:
            event = Event(c[0], c[1], c[2], c[3],
                          datetime.fromisoformat(c[4]), c[5], c[6])
            events.append(event)
        return events

    def fetch(self, event_id):
        cursor = self.connection.execute(
            f"""
                SELECT 
                    id, config_id, config_group_identity, todo, 
                    next_trigger_time, remaining_repetition_count, 
                    snooze_for_minutes 
                FROM event
                WHERE id ={event_id}
            """)
        events = []
        for c in cursor:
            event = Event(c[0], c[1], c[2], c[3],
                          datetime.fromisoformat(c[4]), c[5], c[6])
            events.append(event)
        return next(iter(events), None)

    def upsert(self, event):
        query = f"""
            INSERT INTO event (config_id, config_group_identity, todo, 
                next_trigger_time, remaining_repetition_count, snooze_for_minutes)
            SELECT {event.config_id}, '{event.config_group_identity}','{event.todo}', 
                '{event.next_trigger_time.isoformat()}', {event.remaining_repetition_count}, 
                {event.snooze_for_minutes}
            WHERE NOT EXISTS (
                SELECT 1 FROM event WHERE config_id = {event.config_id} AND 
                next_trigger_time = '{event.next_trigger_time.isoformat()}'
            )
        """
        self.connection.execute(query)
        self.connection.commit()

    def update(self, event):
        self.connection.execute(
            f"""
                UPDATE event
                SET config_id = {event.config_id}, 
                    config_group_identity = '{event.config_group_identity}', 
                    todo = '{event.todo}', 
                    next_trigger_time = '{event.next_trigger_time.isoformat()}', 
                    remaining_repetition_count = {event.remaining_repetition_count},
                    snooze_for_minutes = {event.snooze_for_minutes}
                WHERE
                    id = {event.id}
            """)
        self.connection.commit()

    def mark_as_done(self, event_id):
        self.connection.execute(
            f"""
                UPDATE event
                SET remaining_repetition_count = 0
                WHERE
                    id = {event_id}
            """)
        self.connection.commit()
