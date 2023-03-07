from event import Events, subscribe_to_event, broadcast_event

import os
import json
import logging
import schedule

iocs = []


def add_ioc(name, file_hash):
    try:
        with open("ioc/{name}.json".format(name=name), "w") as ioc:
            ioc.write(json.dumps({"file_hash": file_hash}))
            load_iocs()
        return True
    except:
        return False


def print_iocs(iocs):
    if len(iocs) > 0:
        print("[+] Loaded IOCs:")

        for ioc in iocs:
            print("\t - {name}".format(name=ioc["name"]))

        print("")


def load_iocs():
    global iocs

    iocs = []

    # Load all IOCs
    try:
        files = os.listdir("ioc")
    except:
        print("[!] Could not list IOC directory!")

    for file in files:
        if file.endswith(".json"):
            try:
                with open(os.path.join("ioc/", file)) as ioc:
                    logging.info("Loaded IOC from {file}.".format(file=file))
                    iocs.append(json.loads(ioc.read()))
            except Exception as e:
                print("[!] Could not load {ioc}".format(
                    ioc=file
                ))
                print(e)
                continue

    print_iocs(iocs)

    return iocs


def schedule_iocs():
    for ioc in iocs:
        schedule.every(ioc["poll_time"]).minutes.do(broadcast_event, Events.COLLECT, ioc)

    # Also hunt them manually once when initializing.
    hunt_iocs()

def hunt_iocs():
    for ioc in iocs:
        broadcast_event(Events.COLLECT, ioc)


subscribe_to_event(Events.INITIALIZE, load_iocs)
