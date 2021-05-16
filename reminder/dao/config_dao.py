from reminder.model.config import Config
from reminder.model.frequency import Frequency
import json


class ConfigDao():
    def __init__(self, connection):
        self.connection = connection

    def fetch_all(self):
        cursor = self.connection.execute(
            """
                SELECT 
                    id, config_group_identity, todo, frequency, repetition_count, snooze_for_minutes
                FROM config
            """)
        configs = []
        for c in cursor:
            freq_dict = json.loads(c[3])
            frequency = Frequency(**freq_dict)
            config = Config(c[0], c[1], c[2], frequency, c[4], c[5])
            configs.append(config)
        return configs

    def insert(self, config):
        frequency_json = json.dumps(config.frequency, default=lambda o: o.__dict__)
        self.connection.execute(
            f"""
                INSERT INTO config(config_group_identity, todo, frequency, repetition_count, snooze_for_minutes)
                VALUES('{config.config_group_identity}', 
                    '{config.todo}', '{frequency_json}', {config.repetition_count}, {config.snooze_for_minutes})
            """)
        self.connection.commit()
