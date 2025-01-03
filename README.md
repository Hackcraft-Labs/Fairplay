# Fairplay 

```
███████╗ █████╗ ██╗██████╗ ██████╗ ██╗      █████╗ ██╗   ██╗
██╔════╝██╔══██╗██║██╔══██╗██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝
█████╗  ███████║██║██████╔╝██████╔╝██║     ███████║ ╚████╔╝ 
██╔══╝  ██╔══██║██║██╔══██╗██╔═══╝ ██║     ██╔══██║  ╚██╔╝  
██║     ██║  ██║██║██║  ██║██║     ███████╗██║  ██║   ██║  (1.2)

"If you know, we know."
```

During Red Team operations, one of the most important things is protecting the malware, the crown jewels, the heart pumping blood throughout the whole operation. As soon as our payload is delivered to the targets, an analyst on the Blue Team or perhaps even the target themselves will upload a copy to an online database/sandbox for further analysis. Luckily, these online sources can also be accessed by us, and queried frequently to identify when any of our samples are detected. Fairplay is a framework for performing such tasks, which allows you to define your own IOCs which are searched against multiple sources (you can also define your own sources) and be notified on different channels (you can also define more of these). This is what we consider fair play :^).

### Intel Sources

The following list of intel sources have collectors implemented for them in Fairplay:

- VirusTotal
- HybridAnalysis
- Google
- MetaDefender
- MalwareBazaar

### Notifiers

The following list of channels have notifiers implemente for them in Fairplay:
- Microsoft Teams
- Slack
- Pushover
- Terminal Console (stdout)
- Mattermost

### Setup

Install the requirements in a virtual environment:

```
python -m pip install pipenv
python -m pipenv install
```

Run the tool within the virtual environment:

```
pipenv shell
python main.py
```

### Monitoring IOCs

Define your IOCs in JSON files in the `ioc` directory, named `ANYTHING.json`. The content of the file should be a JSON object with the key `file_hash` containing the hash (any variant supported by the sources will do) of the payload to be monitored, its `name` and `poll_time` which specifies the interval between polling, in minutes. Take a look at the other examples provided to see the structure. Other keys can also be included freely and will be ignored. An example IOC file looks like this:

```json
{
    "name": "EICAR",
    "poll_time": 60,
    "file_hash": "3395856ce81f2b7382dee72602f798b642f14140"
}
```

API keys will need to be provided for each collector. You can do that in `config/config.json`. Multiple other keys can be configured there as well and required keys that are missing will be automatically detected.

Finally, detections are stored in `detections/detections.json` so that detections are not repeated every time, but rather only when a new source is found that detects them. You can freely delete this file to reset the state and start from scratch.

### Adding new collectors

In order to add a new source, add a new .py file named after your source, such as `collectors\MyCollector.py` which contains a subclass of `Collector` named `MyCollector`. Remember to override the `execute(ioc)` method in order to perform the collection. You can add extra info collected by calling `extra(text)`. Also, usually during your constructor, you can call `verify(key)` to ensure that a specific configuration key is present, and prompt the user to create it if it isn't. After checking, you can get its value using `get_key(key)`. Finally, pass your results to `report(ioc)`. You can refer to already implemented collectors for example usage of the API, but a minimal example is provided below:

```python
# Contents of 'collectors/MyCollector.py'

from collectors import Collector

class MyCollector(Collector):
    def __init__(self):
        super().__init__()
        self.verify("api_key")

    def execute(self, ioc):
        response = imaginary_method_to_check_ioc(ioc, self.get_key("api_key"))
        self.extra("Here is some extra info {info}".format(info=response.info))
        self.report(ioc)
```

Certain configuration keys are considered mandatory for every collector and are automatically verified in the `Collector` class. These are the following:

| Key        | Usage                                                               |
| ---------- | ------------------------------------------------------------------- |
| api_key    | API key for service                                                 |
| lookup_url | URL to the detection, which is automatically returned as extra info |

### Adding new notifiers

In order to add a new notifier, add a new .py file named after your notifier, such as `notifiers\MyNotifier.py` which contains a subclass of `Notifier` named `MyNotifier`. Remember to override the `execute(text)` method in order to perform the notification. Just like before, during your constructor, you can call `verify(key)` to ensure that a specific configuration key is present, and prompt the user to create it if it isn't. After checking, you can get its value using `get_key(key)`. You can refer to already implemented collectors for example usage of the API, but a minimal example is provided below:

```python
# Contents of 'notifiers/MyNotifier.py'

from notifiers import Notifier

class MyCollector(Notifier):
    def __init__(self):
        super().__init__()
        self.verify("webhook")

    def execute(self, text):
        imaginary_method_to_notify(ioc, self.get_key("webhook"))
```

Currently no configuration keys are considered mandatory and are automatically veryfied in the `Notifier` class. 

The following key is verified on notifiers that POST to a webhook:

| Key     | Usage                                                   |
| ------- | ------------------------------------------------------- |
| webhook | URL to the channel which will be used for notifications |

### Detailed Analysis

A more detailed analysis of Fairplay and its features can be found [on our blog](https://www.hackcraft.gr/2023/05/introducing-fairplay/).

### Contributors
| Contributor        | Module                                                                      |
| ------------------ | --------------------------------------------------------------------------- |
| Nick Aliferopoulos | Core, VirusTotal/HybridAnalysis Collectors, Microsoft Teams/Slack Notifiers |
| Despoina Choctoula | Google Search Collector                                                     |
| Dimitris Lazarakis | MalwareBazaar Collector                                                     |
| Nomiki Parginou    | MetaDefender Collector, IOC Generation Utility                              |
| Alexandros Vavakos | Pushover Notifier                                                           |

### Community

Join the Hackcraft community discord server [here](https://discord.gg/KZZfsnQsja). On the server you can receive support and discuss issues related to Fairplay.
