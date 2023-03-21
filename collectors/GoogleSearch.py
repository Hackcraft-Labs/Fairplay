from collectors import Collector
from googleapiclient.discovery import build
import json

class GoogleSearch(Collector):

    def __init__(self):
        super().__init__()
        self.verify("engine_id")

    def execute(self, ioc):
        try:
            keywords = ["malware", "APT", "malicious", "virus"]

            api_key = self.get_key("api_key")
            ioc_hash = ioc['file_hash']
            cse_id = self.get_key("engine_id")

            service = build("customsearch", "v1", developerKey=api_key)
            res = service.cse().list(q=ioc_hash, cx=cse_id, num=10).execute()
            try:
                results = res['items']
            except:
                results = []
                return

            counter = 0
            for result in results:
                result_json = json.dumps(result)
                reference = json.loads(result_json)
                for i in keywords:
                    if i in json.dumps(result):
                        counter+=1
                        self.extra("Reference to malware or APT found. Result title: " + reference['htmlTitle'] + ". More info: "+ reference['link'])
            if counter > 0:
                self.report(ioc, reference)
        except Exception as e:
            print(e)

