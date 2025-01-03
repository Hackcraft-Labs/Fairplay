import requests

from notifiers import Notifier

def send_message_to_mattermost(webhook_url, message, username="Webhook Bot"):
    payload = {
        "text": message,
        "username": username
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, json=payload, headers=headers)
    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed to send message: {response.text}")

class Mattermost(Notifier):
    def __init__(self):
        self.verify("webhook")
        super().__init__()

    def execute(self, text):
        try:
            webhook_url = self.get_key("webhook")
            message = str(text)
            send_message_to_mattermost(webhook_url, message)
        except Exception as exc:
            print(f"[{self.NAME}] {exc}\n")
