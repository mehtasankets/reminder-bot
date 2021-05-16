# Reminder bot

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

## Design

### subscription

* username
* config_group_identity

### config

* config_group_identity
* id
* todo
* frequency
  * cron
  * start_time
  * end_time
* repetition_count

### event

* id
* config_id
* todo
* event_time
* remaining_repetition_count
