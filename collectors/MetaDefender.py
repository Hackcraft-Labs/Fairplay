import requests
from collectors import Collector


class MetaDefender(Collector):
	def __init__(self):
		super().__init__()


	def execute(self, ioc):
		try:
			headers = {
				"apikey": self.get_key("api_key"),
			}

			response = requests.request("GET", self.get_key("api_base").format(ioc=ioc['file_hash']), headers=headers)
			
			detection = response.json()

			if not detection or response.status_code == 404:
				return
			else:
				threat = 0
				suspicious = 0
				undetected = 0
				date = 0

			if "error" in detection:
				if "messages" in detection["error"]:
					for msg in detection["error"]["messages"]:
						if "not found" in msg:
							return

			threat = 0
			suspicious = 0
			undetected = 0
			date = 0

			if "malware_family" in detection:
				if detection["malware_family"]:
					self.extra(detection["malware_family"])
			if "file_info" in detection:
					if detection["file_info"]:
						if "upload_timestamp" in detection["file_info"]:
							if detection["file_info"]["upload_timestamp"]:
								date = detection["file_info"]["upload_timestamp"]
								self.extra(detection["file_info"]["upload_timestamp"])
							else:
								date = "unknown date"
			if "scan_results" in detection:
				if "scan_details" in detection["scan_results"]:
					if detection["scan_results"]["scan_details"]:
						for engine in detection["scan_results"]["scan_details"]:
							if "scan_result_i" in detection["scan_results"]["scan_details"][engine]:
								if detection["scan_results"]["scan_details"][engine]["scan_result_i"] == 0:
									undetected+=1
								if detection["scan_results"]["scan_details"][engine]["scan_result_i"] == 1:
									threat+=1
								if detection["scan_results"]["scan_details"][engine]["scan_result_i"] == 2:
									suspicious+=1

			self.report(ioc)

			# print("Malware {name} with hash {hash} was uploaded on MetaDefender on {date}!".format(name=ioc['name'], hash=ioc['file_hash'], date=date))
			if threat > 0:
				threat_str = "Marked as \"Theat Detected\" on {n} engines".format(n=threat)
				self.extra(threat_str)
			if suspicious > 0:
				suspicious_str = "Marked as \"Suspicious\" on {n} engines".format(n=suspicious)
				self.extra(suspicious_str)
			if undetected > 0:
				undetected_str = "Marked as \"No Threat Detected\" on {n} engines".format(n=undetected)
				self.extra(undetected_str)
		except Exception as exc:
			print(f"[MetaDefender] {exc}\n")
