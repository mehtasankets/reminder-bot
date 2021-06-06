from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from reminder.model.event import Event
from reminder.dao.event_dao import EventDao
from reminder.model.subscription import Subscription
from reminder.dao.subscription_dao import SubscriptionDao
import telebot
import logging

help_str = """
Supported commands:
    /help
    /subscribe <config_group_identity>
    /done <event_id>
    /unsubscribe <config_group_identity>
    /listsubscriptions
"""


class TelegramInteractor():
    def __init__(self, token, connection):
        self.telegram_bot_instance = telebot.TeleBot(token)
        self.subscription_dao = SubscriptionDao(connection)
        self.event_dao = EventDao(connection)

    def notify(self, group_messages):
        subscriptions = self.subscription_dao.fetch_all()
        subscription_details = {}
        for s in subscriptions:
            subscription_details[s.config_group_identity] = [s.user_id] if s.config_group_identity not in subscription_details.keys(
            ) else subscription_details[s.config_group_identity] + [s.user_id]
        for group_identity, value in group_messages.items():
            user_ids = subscription_details[group_identity]
            event_ids = value[1]
            print(event_ids)
            reply_markup = ReplyKeyboardMarkup()
            for id in event_ids:
                reply_markup.add(f"/done {id}", row_width=3)
            for user_id in user_ids:
                self.telegram_bot_instance.send_message(
                    user_id, value[0], reply_markup=reply_markup)

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

        @self.telegram_bot_instance.message_handler(commands=['unsubscribe'])
        def unsubscribe(message):
            config_group_identity = " ".join(message.text.split()[1:])
            subscription = Subscription(
                message.from_user.id, message.from_user.username, config_group_identity)
            self.subscription_dao.unsubscribe(subscription)
            self.telegram_bot_instance.reply_to(
                message, f"Unsubscribed from '{config_group_identity}' group successfully!")

        @self.telegram_bot_instance.message_handler(commands=['listsubscriptions'])
        def list_subscriptions(message):
            subscriptions = self.subscription_dao.fetch_all()
            user_subscriptions = [
                s.config_group_identity for s in subscriptions if s.user_id == message.from_user.id]
            reply = "Your active subscription(s):\n" + \
                "\n".join(user_subscriptions)
            self.telegram_bot_instance.send_message(
                message.from_user.id, reply)

        @self.telegram_bot_instance.message_handler(commands=['done'])
        def done(message):
            event_id = " ".join(message.text.split()[1:])
            self.event_dao.mark_as_done(event_id)
            self.telegram_bot_instance.reply_to(
                message, f"Marked event number {event_id} as done!")

        @self.telegram_bot_instance.message_handler(func=lambda message: True)
        def default_message_reply(message):
            self.telegram_bot_instance.reply_to(
                message, "Invalid command\n" + help_str)

        self.telegram_bot_instance.polling()
