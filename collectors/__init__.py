from module import Module
from event import Events, subscribe_to_event
from detections import register_detection


class Collector(Module):
    def __init__(self):
        super().__init__()
        self.verify("lookup_url")
        self.verify("api_key")
        self.extra_info = []
        subscribe_to_event(Events.COLLECT, self.execute)

    def extra(self, text):
        self.extra_info.append(text)

    def report(self, ioc, reference_list = []):
        if reference_list:
            self.extra(ioc["file_hash"])

            register_detection(ioc["name"], ioc["file_hash"],
                           self.NAME, self.extra_info)

            self.extra_info = []
            return

        self.extra(self.get_key(
            "lookup_url").format(ioc=ioc["file_hash"]))

        register_detection(ioc["name"], ioc["file_hash"],
            self.NAME, self.extra_info)

        self.extra_info = []
