# Fairplay 

```
███████╗ █████╗ ██╗██████╗ ██████╗ ██╗      █████╗ ██╗   ██╗
██╔════╝██╔══██╗██║██╔══██╗██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝
█████╗  ███████║██║██████╔╝██████╔╝██║     ███████║ ╚████╔╝ 
██╔══╝  ██╔══██║██║██╔══██╗██╔═══╝ ██║     ██╔══██║  ╚██╔╝  
██║     ██║  ██║██║██║  ██║██║     ███████╗██║  ██║   ██║  (2.0)

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
- Terminal Console (stdout) 

### Setup

Install the requirements (probably in a virtual environment) using Python 3.10 as usual with:

`python -m pip install -r requirements.txt`

#### Frontend (Angular)

From `frontend/`:

- `npm install`
- `ng serve`

The UI will be available at `http://localhost:4200`.

#### Backend (FastAPI)

From the repo root:

- `uvicorn api.app:app --reload --host 127.0.0.1 --port 8000`

The backend listens on `http://127.0.0.1:8000`.

#### `useMockData`

In `frontend/src/environments/environment.ts`, `useMockData` controls whether the frontend uses mock/example data instead of calling the real backend.

- Default is `false` (use the real API via `/api`)
- Set it to `true` if you want to see example/mock data in the UI

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

Finally, detections are now stored in a local SQLite database file named `fairplay.db` in the project root so that detections are not repeated every time, but rather only when a new source is found that detects them.

On first run with this version, if a legacy `detections/detections.json` file exists and the SQLite database is empty, its contents will be automatically migrated into `fairplay.db`. After migration, the JSON file is no longer used.

If you want to reset the detection state and start from scratch, you can:

- **Web UI:** In the dashboard sidebar, use **Reset DB** and confirm. This clears all rows in the SQLite tables (`detections`, `detection_sources`, `iocs`) via the API (see below). **There is no authentication on this endpoint yet**—only use it in trusted environments or behind your own controls.
- **CLI / manual:** Stop Fairplay and delete `fairplay.db`, or clear those tables with any SQLite client.

### Web dashboard and HTTP API

The repository includes an **Angular** frontend under `frontend/` and a **FastAPI** app under `api/`. The UI talks to the API over `/api` in dev (see `frontend/proxy.conf.json`), which strips the prefix and forwards to the backend (e.g. `uvicorn` on port `8000`).

**API routes (high level):**

| Prefix | Purpose |
| ------ | ------- |
| `/detections` | List, create, update, soft-delete, restore detections |
| `/iocs` | List, create, update, delete IOCs (JSON files under `ioc/` plus DB mirror) |
| `/ops/reset-db` | `POST` — clears all rows in the SQLite tables (same effect as wiping stored detections/IOC mirror data in the DB) |

### CLI: IOCs and detections

The interactive CLI (`cli`) supports more than IOC reloads. Detection-related commands (all backed by the same SQLite persistence as the collectors):

| Command | Description |
| ------- | ----------- |
| `detections` | List current detections (name, hash, sources). |
| `detections_add` | Add a manual detection (name, hash, optional collector). |
| `detections_remove` | Soft-delete by hash (or permanent delete if you answer the prompt accordingly). |
| `detections_restore` | Restore a soft-deleted detection. |
| `detections_remove_source` | Remove one collector source from a detection. |
| `detections_show` | Show one detection including per-source extra info. |
| `detections_export` | Export detections to JSON (optional include soft-deleted). |
| `detections_import` | Import detections from JSON. |

Use `help` in the CLI for the full command list.

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

A more detailed analysis of Fairplay and its features can be found [on our blog](https://www.hackcraft.gr/2026/05/fairplay-evolves-introducing-the-web-dashboard-and-api/). Our initial article introducing Fairplay can be found [here](https://www.hackcraft.gr/2023/05/introducing-fairplay/).

### Contributors
| Contributor        | Module                                                                      |
| ------------------ | --------------------------------------------------------------------------- |
| Nick Aliferopoulos | Core, VirusTotal/HybridAnalysis Collectors, Microsoft Teams/Slack Notifiers |
| Despoina Choctoula | Google Search Collector                                                     |
| Dimitris Lazarakis | MalwareBazaar Collector                                                     |
| Nomiki Parginou    | MetaDefender Collector, IOC Generation Utility                              |
| Alexandros Vavakos | Pushover Notifier                                                           |
| Nikos Vourdas      | Mattermost, Discord Notifiers                                                |
| Aldo Mihasi        | Database, Frontend, API                                                       |

### Community

Join the Hackcraft community discord server [here](https://discord.gg/KZZfsnQsja). On the server you can receive support and discuss issues related to Fairplay.