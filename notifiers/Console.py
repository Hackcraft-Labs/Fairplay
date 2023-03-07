import json

from notifiers import Notifier


class Console(Notifier):
    def __init__(self):
        super().__init__()

    def execute(self, text):
        try:
            print("[+] {}\n".format(text))
        except:
            print("[!] Could not notify over {name}! Please check for sanity.".format(
                name=self.NAME))
