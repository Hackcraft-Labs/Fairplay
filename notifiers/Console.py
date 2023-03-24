import json

from notifiers import Notifier


class Console(Notifier):
    def __init__(self):
        super().__init__()

    def execute(self, text):
        try:
            print("[+] {}\n".format(text))
        except Exception as exc:
            print(f"[{self.NAME}] {exc}\n")
