import json
import time
import logging

from event import Events, subscribe_to_event, broadcast_event

DETECTIONS_FILE = "detections/detections.json"

detections = []


def load_detections():
    global detections
    print("[*] Loading detections...\n")

    # Load all detections
    try:
        with open(DETECTIONS_FILE, "r") as detections_file:
            detections = json.loads(detections_file.read())

            logging.info("Loaded detections from '{file}'.".format(file=DETECTIONS_FILE))

    except:
        print("[!] Could not open file {name}!".format(name=DETECTIONS_FILE))

    return detections


def save_detections():
    print("[*] Saving detections...")
    # Save all detections
    try:
        with open('detections/detections.json', "w") as detections_file:
            detections_file.write(json.dumps(detections))

            logging.info("Saved detections to '{file}'".format(file=DETECTIONS_FILE))
    except:
        print("[!] Could not save detections!")


def is_known_hash(file_hash):
    for detection in detections:
        if detection['file_hash'] == file_hash:
            return True

    return False


def is_known_pair(file_hash, collector_name):
    for detection in detections:
        if detection['file_hash'] == file_hash:
            for source in detection['sources']:
                if source == collector_name:
                    return True

    return False


def register_detection(name, file_hash, collector_name, extra_info_table):
    # Return if this detection is known by this collector
    if is_known_pair(file_hash, collector_name):
        return

    # Check if this detection is known by any collector
    if is_known_hash(file_hash):
        # If yes, just add the source and extra info
        for detection in detections:
            if detection['file_hash'] == file_hash:
                detection['sources'].append(collector_name)
                detection['extra_info'][collector_name] = extra_info_table

                extra_info_text = ""

                if extra_info_table:
                    extra_info_text = "Extra Info:\n\t"
                    extra_info_text += '\n\t'.join(extra_info_table)

                text = "Detected {name} ({hash}) which was previously known, on new source {collector}. {extra}".format(
                    name=name, hash=file_hash, collector=collector_name, extra=extra_info_text)

                broadcast_event(Events.NOTIFY, text)
    else:
        # Else, create a new detection
        initial_detection_time = {
            "unix": str(int(time.time())),
            "text": time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        }

        extra_info = {}
        extra_info[collector_name] = extra_info_table

        detection = {"name": name, "file_hash": file_hash, "sources": [
            collector_name], "initial_detection_time": initial_detection_time, "extra_info": extra_info}

        detections.append(detection)

        extra_info_text = ""

        if extra_info_table:
            extra_info_text = "Extra Info:\n\t"
            extra_info_text += '\n\t'.join(extra_info_table)

        text = "Detected {name} ({hash}) on {collector}. {extra}".format(
            name=name, hash=file_hash, collector=collector_name, extra=extra_info_text)
        broadcast_event(Events.NOTIFY, text)


subscribe_to_event(Events.INITIALIZE, load_detections)
subscribe_to_event(Events.TERMINATE, save_detections)
