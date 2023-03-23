import pymsteams

from notifiers import Notifier


class Teams(Notifier):
    def __init__(self):
        self.verify("webhook")
        super().__init__()

    def execute(self, text):
        try:
            myTeamsMessage = pymsteams.connectorcard(
                self.get_key("webhook"))
            myTeamsMessage.text(str(text))
            myTeamsMessage.send()
        except:
            print(f"[{self.Name}] {exc}\n")
