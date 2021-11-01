import sqlite3
import threading
from reminder.service.telegram_interaction import TelegramInteractor
from reminder.service.event_creator import EventCreator
from reminder.service.event_notifier import EventNotifier
import logging
import os


def main():
    setup_logger()
    log = logging.getLogger(__name__)
    log.info("Welcome to Reminder Bot!")

    db_file_path = os.path.abspath(os.environ.get(
        'REMINDER_BOT_DB_PATH', 'reminders.db'))
    connection = sqlite3.connect(db_file_path, check_same_thread=False)
    token = os.environ['TELEGRAM_BOT_TOKEN']
    telegram_interactor = TelegramInteractor(token, connection)

    t1 = threading.Thread(name='TelegramInteractor',
                          target=telegram_interactor.interact, daemon=True)
    t2 = threading.Thread(name='EventCreator', target=EventCreator(
        connection).create, daemon=True)
    t3 = threading.Thread(name='EventNotifier', target=EventNotifier(
        telegram_interactor, connection).notify, daemon=True)
    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()


def setup_logger():
    logFormatter = logging.Formatter(
        "%(asctime)s [%(threadName)-13.13s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    fileHandler = logging.FileHandler("reminder_bot.log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)


if __name__ == "__main__":
    main()
