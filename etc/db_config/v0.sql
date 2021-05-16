DROP TABLE IF EXISTS subscription;
DROP TABLE IF EXISTS config;
DROP TABLE IF EXISTS event;

CREATE TABLE IF NOT EXISTS subscription(
    user_id INT,
    username TEXT,
    config_group_identity TEXT
);

CREATE TABLE IF NOT EXISTS config(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_group_identity TEXT,
    todo TEXT,
    frequency TEXT,
    repetition_count INT,
    snooze_for_minutes INT
);

CREATE TABLE IF NOT EXISTS event(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_id INTEGER,
    config_group_identity TEXT,
    todo TEXT,
    next_trigger_time TEXT,
    remaining_repetition_count INT,
    snooze_for_minutes INT
);