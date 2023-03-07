import logging

from enum import Enum


class Events(Enum):
    INITIALIZE = "INITIALIZE"
    TERMINATE = "TERMINATE"
    COLLECT = "COLLECT"
    NOTIFY = "NOTIFY"


event_handlers = {}


def subscribe_to_event(event, handler):
    if not event in event_handlers:
        event_handlers[event] = []

    event_handlers[event].append(handler)


def broadcast_event(event, *args):
    output_list = []

    if not event in event_handlers:
        event_handlers[event] = []

    for handler in event_handlers[event]:
        output = handler(*args)

        if (output):
            output_list.append(output)

    return output_list
