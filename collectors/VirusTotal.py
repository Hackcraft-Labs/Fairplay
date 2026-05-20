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
            except (vt.APIError):
                pass

if __name__ == "__main__":
    from ioc import load_iocs
    from config import get_config
    
    get_config() 
    
    from notifiers import Console
    Console.Console.CATEGORY = "notifiers"
    Console.Console.NAME = "Console"
    Console.Console()

    VirusTotal.CATEGORY = "collectors"
    VirusTotal.NAME = "VirusTotal"
    collector = VirusTotal()

    for ioc in load_iocs():
        collector.execute(ioc)