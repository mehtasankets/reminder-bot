from reminder.model.subscription import Subscription
from reminder.dao.subscription_dao import SubscriptionDao
import telebot
import logging

help_str = """
Supported commands:
    /help
    /subscribe <config_group_identity>
    /done <event_id>
"""


class TelegramInteractor():
    def __init__(self, token, connection):
        self.telegram_bot_instance = telebot.TeleBot(token)
        self.subscription_dao = SubscriptionDao(connection)

    def notify(self, group_messages):
        subscriptions = self.subscription_dao.fetch_all()
        subscription_details = {}
        for s in subscriptions:
            subscription_details[s.config_group_identity] = [s.user_id] if s.config_group_identity not in subscription_details.keys(
            ) else subscription_details[s.config_group_identity] + [s.user_id]
        for group_identity, message in group_messages.items():
            user_ids = subscription_details[group_identity]
            for user_id in user_ids:
                self.telegram_bot_instance.send_message(user_id, message)

    def interact(self):

        @self.telegram_bot_instance.message_handler(commands=['start'])
        def start(message):
            self.telegram_bot_instance.send_message(
                message.chat.id, "Welcome to SaTan Reminder Bot!" + help_str)

        @self.telegram_bot_instance.message_handler(commands=['help'])
        def help(message):
            self.telegram_bot_instance.reply_to(message, help_str)

        @self.telegram_bot_instance.message_handler(commands=['subscribe'])
        def subscribe(message):
            config_group_identity = " ".join(message.text.split()[1:])
            subscription = Subscription(
                message.from_user.id, message.from_user.username, config_group_identity)
            self.subscription_dao.subscribe(subscription)
            self.telegram_bot_instance.reply_to(
                message, f"Subscribed to '{config_group_identity}' group successfully!")

        @self.telegram_bot_instance.message_handler(func=lambda message: True)
        def default_message_reply(message):
            self.telegram_bot_instance.reply_to(
                message, "Invalid command\n" + help_str)

        self.telegram_bot_instance.polling()
