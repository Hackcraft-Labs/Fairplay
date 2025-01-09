import json

import requests

from notifiers import Notifier


class Slack(Notifier):
    def __init__(self):
        self.verify("webhook")
        super().__init__()

    def execute(self, text):
        try:
            slack_data = {'text': str(text)}
            requests.post(self.get_key("webhook"), data=json.dumps(slack_data),
                          headers={'Content-Type': 'application/json'})
        except Exception as exc:
            print(f"[{self.NAME}] {exc}\n")
