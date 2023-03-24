import re

import requests

from collectors import Collector


class HybridAnalysis(Collector):
    def __init__(self):
        super().__init__()
        self.verify("api_base")

    def execute(self, ioc):
        try:
            headers = {
                "api-key": self.get_key("api_key"),
                "User-Agent": "Falcon Sandbox"
            }

            data = {
                "hash": ioc['file_hash']
            }

            # Search for hash
            result = requests.post(self.get_key("api_base").format(
                endpoint="/search/hash"), headers=headers, data=data)
            
            if result.status_code != 200:
                print(f"[HybridAnalysis] {result.json()['message']}\n")
                return

            detections = result.json()

            if not detections:
                return

            for detection in detections:
                if "vx_family" in detection:
                    if detection["vx_family"]:
                        self.extra(detection["vx_family"])
                        break

            self.report(ioc)
        except Exception as exc:
            print(f"[{self.NAME}] {exc}\n")
