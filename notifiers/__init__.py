from event import Events, subscribe_to_event
from module import Module


class Notifier(Module):
    def __init__(self):
        super().__init__()

        subscribe_to_event(Events.NOTIFY, self.execute)
