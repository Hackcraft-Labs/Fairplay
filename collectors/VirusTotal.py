import vt

from collectors import Collector


class VirusTotal(Collector):
    def __init__(self):
        super().__init__()

    def execute(self, ioc):
        with vt.Client(self.get_key("api_key")) as client:
            try:
                identified = client.get_object(
                    '/files/{hash}'.format(hash=ioc["file_hash"]))

                self.extra("Flagged malicious on {n} engines".format(
                    n=identified.last_analysis_stats["malicious"]))
                self.extra("Flagged harmless on {n} engines".format(
                    n=identified.last_analysis_stats["harmless"]))
                self.extra("Unscanned on {n} engines".format(
                    n=identified.last_analysis_stats["undetected"]))

                self.report(ioc)
            except vt.error.APIError as e:
                if e.code != "NotFoundError":
                    print(f"[{self.NAME}] {e.message}\n")
