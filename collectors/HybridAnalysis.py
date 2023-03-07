import re
from collectors import Collector

import requests


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

            detections = result.json()

            if not detections:
                return

            for detection in detections:
                if "vx_family" in detection:
                    if detection["vx_family"]:
                        self.extra(detection["vx_family"])
                        break

            self.report(ioc)
        except:
            pass
