import re
import requests

from notifiers import Notifier


class Pushover(Notifier):
    def __init__(self):
        self.verify("api_base")
        self.verify("api_key")
        self.verify("user_keys")
        super().__init__()

    def execute(self, text):
        try:
            message = text.split(" Extra Info:")[0]
            extra = re.findall("http[s]?://[^\s]+", text)[0]
            signature = re.findall(" \(.*\)", message)[0]
            message = message.replace("Detected ", f"[{self.get_key('project')}] A wild '") \
                             .replace(signature, "' appeared") \
                             .replace(" which was previously known,", "") \
                             .replace(" new source", "") + "\n" + extra

            for user_key in self.get_key("user_keys"):
                pushover_data = {'token': self.get_key("api_key"), 'user': user_key, 'message': message}
                requests.post(self.get_key("api_base"), data=pushover_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        except Exception as exc:
            print(f"[{self.Name}] {exc}\n")
