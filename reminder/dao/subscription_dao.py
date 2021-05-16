from reminder.model.subscription import Subscription
import sqlite3


class SubscriptionDao():
    def __init__(self, connection):
        self.connection = connection

    def fetch_all(self):
        cursor = self.connection.execute(
            """
                SELECT user_id, username, config_group_identity FROM subscription
            """)
        subscriptions = [Subscription(r[0], r[1], r[2]) for r in cursor]
        return subscriptions

    def subscribe(self, subscription):
        self.connection.execute(
            f"""
                INSERT INTO subscription(user_id, username, config_group_identity)
                VALUES({subscription.user_id}, '{subscription.username}', '{subscription.config_group_identity}')
            """)
        self.connection.commit()
