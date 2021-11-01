# Reminder bot

A bot to remind me of various things

## MVP

1. Allow user to create recurring reminders:
    * Daily at 10:00 PM: Check if doors are locked
    * Weekly on Sunday: Order grocery
    * Monthly on 1st: Pay rent
1. Generate items from recurrences
1. Push items to users

## Future

1. Allow creation of 1 time events
1. Allow muting and un-muting of specific / all events

## Cloud run

```
(One time) git clone https://github.com/mehtasankets/reminder-bot.git
cd reminder-bot
git pull
(One time) cp prod-env.list-tmpl prod-env.list
(One time) Edit prod-env.list to populate environment variables
Run db query versions if any
docker-compose down
./run.sh
```

## Local run

```
.\env\Scripts\activate
(one time) py -m pip install -r requirements.txt
.\local-env.ps1
py .\reminder_bot_driver.py
```