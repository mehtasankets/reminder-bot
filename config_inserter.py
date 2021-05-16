from reminder.model.config import Config
from reminder.model.frequency import Frequency
from reminder.dao.config_dao import ConfigDao
import sqlite3
import os


def main():

    db_file_path = os.path.abspath('./etc/reminders.db')
    connection = sqlite3.connect(db_file_path, check_same_thread=False)
    config_dao = ConfigDao(connection)

    freq = Frequency("*/5 * * * *", None, None)
    config = Config(None, "SanketPersonal", f"Check mobile", freq, 3, 1)
    config_dao.insert(config)
    configs = config_dao.fetch_all()
    print(configs)


if __name__ == "__main__":
    main()
