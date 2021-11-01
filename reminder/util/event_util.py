def generate_telegram_notifications(events):
    group_messages = {}
    for event in events:
        message = f"{event.id}. {event.todo} @ {event.next_trigger_time} ({event.remaining_repetition_count - 1})\n"
        group_messages[event.config_group_identity] = group_messages.get(
            event.config_group_identity, ["", []])
        group_messages[event.config_group_identity][0] += message
        group_messages[event.config_group_identity][1].append(
            f"{event.id}")
    return group_messages
