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

            # Query parameters for GET
            params = {
                "hash": ioc['file_hash']
            }

            # Perform a GET request
            result = requests.get(
                self.get_key("api_base").format(endpoint="/search/hash"),
                headers=headers,
                params=params
            )

            if result.status_code != 200:
                if "hash not found" in result.text:
                    return

            if result.status_code != 200:
                print("[HybridAnalysis] {}".format(result.text))
                return

            detections = result.json()

            for detection in detections:
                if "vx_family" in detection and detection["vx_family"]:
                    self.extra(detection["vx_family"])
                    break

            self.report(ioc)
        except Exception as e:
            # Consider logging the exception for debugging
            print(f"[HybridAnalysis] Error: {e}")

if __name__ == "__main__":
    from ioc import load_iocs
    from config import get_config
    
    get_config() 
    
    from notifiers import Console
    Console.Console.CATEGORY = "notifiers"
    Console.Console.NAME = "Console"
    Console.Console()

    HybridAnalysis.CATEGORY = "collectors"
    HybridAnalysis.NAME = "HybridAnalysis"
    collector = HybridAnalysis()

    for ioc in load_iocs():
        collector.execute(ioc)