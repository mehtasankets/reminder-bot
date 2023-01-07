from telebot import apihelper
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from reminder.model.event import Event
from reminder.dao.event_dao import EventDao
from reminder.dao.config_dao import ConfigDao
from reminder.model.subscription import Subscription
from reminder.dao.subscription_dao import SubscriptionDao
import reminder.util.event_util as EventUtil
import traceback
import telebot
import logging
from datetime import datetime

help_str = """
Supported commands:
    /help
    /subscribe <config_group_identity>
    /done <event_id>
    /unsubscribe <config_group_identity>
    /listsubscriptions
"""

log = logging.getLogger(__name__)


class TelegramInteractor():
    def __init__(self, token, connection):
        apihelper.SESSION_TIME_TO_LIVE = 300
        self.telegram_bot_instance = telebot.TeleBot(token)
        self.subscription_dao = SubscriptionDao(connection)
        self.event_dao = EventDao(connection)
        self.config_dao = ConfigDao(connection)

    def refresh_list(self, config_group_identity):
        current_time = datetime.now()
        log.debug(f"Refresh time= {current_time}, {config_group_identity}")
        events = self.event_dao.fetch_all_active()
        configs_list = self.config_dao.fetch_all()
        configs = {x.id: x for x in configs_list}
        events_to_be_notified = []
        for event in events:
            config = configs[event.config_id]
            if event.remaining_repetition_count < config.repetition_count and event.config_group_identity == config_group_identity:
                events_to_be_notified.append(event)
        if len(events_to_be_notified) > 0:
            log.debug(f"Events to report= {events_to_be_notified}")
            group_messages = EventUtil.generate_telegram_notifications(
                events_to_be_notified)
            log.debug(f"group_messages= {group_messages}")
            self.notify(group_messages)
        else:
            subscriptions = self.subscription_dao.fetch_all()
            for s in subscriptions:
                if s.config_group_identity == config_group_identity:
                    self.telegram_bot_instance.send_message(
                        s.user_id, 'No more reminders for now! :)', reply_markup=ReplyKeyboardRemove())

    def notify(self, group_messages):
        subscriptions = self.subscription_dao.fetch_all()
        subscription_details = {}
        for s in subscriptions:
            subscription_details[s.config_group_identity] = [s.user_id] if s.config_group_identity not in subscription_details.keys(
            ) else subscription_details[s.config_group_identity] + [s.user_id]
        for group_identity, value in group_messages.items():
            user_ids = subscription_details[group_identity]
            event_ids = value[1]
            log.info(event_ids)
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
            log.info(f"Received '{message.text}' as done command")
            event_id = " ".join(message.text.split()[1:])
            log.info(f"{event_id} was extracted as event_id")
            
            if not event_id:
                return
            self.event_dao.mark_as_done(event_id)
            event = self.event_dao.fetch(event_id)
            subscriptions = self.subscription_dao.fetch_all()
            user_ids = []
            for s in subscriptions:
                if (s.config_group_identity == event.config_group_identity):
                    user_ids.append(s.user_id)
            for user_id in user_ids:
                self.telegram_bot_instance.send_message(
                    user_id, f"{message.from_user.first_name} marked event {event_id} as done!")
            self.refresh_list(event.config_group_identity)

        @self.telegram_bot_instance.message_handler(commands=['refresh'])
        def refresh(message):
            config_group_identity = " ".join(message.text.split()[1:])
            self.refresh_list(config_group_identity)

        @self.telegram_bot_instance.message_handler(func=lambda message: True)
        def default_message_reply(message):
            self.telegram_bot_instance.reply_to(
                message, "Invalid command\n" + help_str)

        try:
            self.telegram_bot_instance.infinity_polling()
        except Exception as e:
            log.error(traceback.format_exc())
