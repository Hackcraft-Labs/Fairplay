from event import Events, broadcast_event, subscribe_to_event
from ioc import load_iocs, add_ioc
from detections import (
    add_detection_manual,
    remove_detection,
    restore_detection,
    list_detections,
    remove_detection_source,
    get_detection,
    export_detections_to_file,
    import_detections_from_file,
)

import os
import sys
import signal

BANNER = \
    """
███████╗ █████╗ ██╗██████╗ ██████╗ ██╗      █████╗ ██╗   ██╗
██╔════╝██╔══██╗██║██╔══██╗██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝
█████╗  ███████║██║██████╔╝██████╔╝██║     ███████║ ╚████╔╝ 
██╔══╝  ██╔══██║██║██╔══██╗██╔═══╝ ██║     ██╔══██║  ╚██╔╝  
██║     ██║  ██║██║██║  ██║██║     ███████╗██║  ██║   ██║  (2.0)

"If you know, we know."

Press Ctrl-C for console.

"""

original_sigint = None


def prompt():
    sys.stdout.write('\r')
    sys.stdout.flush()

    print("")

    return input("[?] ").strip()


def cmd_exit():
    broadcast_event(Events.TERMINATE)
    print("[+] Exiting...")
    os._exit(0)


def cmd_help():
    for command in commands:
        print("{command}\t\t-\t{help}".format(command=command,
              help=commands[command]["help"]))


def cmd_add():
    name = input("[?] Name: ").strip()
    if name == "":
        print("[!] Name is required.")
        return
    file_hash = input("[?] File Hash: ").strip()
    if file_hash == "":
        print("[!] File hash is required.")
        return
    if add_ioc(name, file_hash):
        load_iocs()
        print("[+] Added IOC!")
    else:
        print("[!] Failed to add IOC. Check logs for details.")


def cmd_iocs():
    load_iocs()
    print("[+] Reloaded IOCs from disk...")


def cmd_detections_list():
    detections = list_detections()
    if not detections:
        print("[*] No detections found.")
        return

    print("[+] Detections:")
    for det in detections:
        sources = ", ".join(det.get("sources", [])) or "<none>"
        print(
            " - {name} ({hash}) from [{sources}]".format(
                name=det.get("name"),
                hash=det.get("file_hash"),
                sources=sources,
            )
        )


def cmd_detections_add():
    name = input("[?] Detection name: ").strip()
    file_hash = input("[?] File hash: ").strip()
    collector = input("[?] Collector name (default: manual): ").strip() or "manual"

    add_detection_manual(name, file_hash, collector_name=collector)
    print("[+] Added detection.")


def cmd_detections_remove():
    file_hash = input("[?] File hash to remove: ").strip()
    confirm = input("[?] Soft delete detection for {h}? [y/N]: ".format(h=file_hash)).strip().lower()
    if confirm == "N":
        remove_detection(file_hash, soft=False)
        print("[+] Detection removed permanently.")
        return

    remove_detection(file_hash, soft=True)
    print("[+] Detection soft-deleted (will be re-added if seen again).")


def cmd_detections_restore():
    file_hash = input("[?] File hash to restore: ").strip()
    restore_detection(file_hash)
    print("[+] Detection restored (if it existed).")


def cmd_detections_remove_source():
    file_hash = input("[?] File hash: ").strip()
    collector = input("[?] Collector name to remove: ").strip()

    remove_detection_source(file_hash, collector)
    print("[+] Removed collector source (if it existed).")


def cmd_detections_show():
    file_hash = input("[?] File hash to show: ").strip()
    det = get_detection(file_hash, include_deleted=True)
    if not det:
        print("[*] No detection found for that hash.")
        return

    print("Name: {name}".format(name=det.get("name")))
    print("Hash: {hash}".format(hash=det.get("file_hash")))
    print("Deleted: {deleted}".format(deleted=det.get("deleted", False)))
    print("Sources:")
    for src in det.get("sources", []):
        print("  - {src}".format(src=src))
        extras = det.get("extra_info", {}).get(src, [])
        for line in extras:
            print("      {line}".format(line=line))


def cmd_detections_export():
    default_path = "detections-export.json"
    path = input(
        "[?] Output JSON path (default: {p}): ".format(p=default_path)
    ).strip() or default_path

    include_deleted = (
        input("[?] Include soft-deleted detections? [y/N]: ").strip().lower() == "y"
    )

    export_detections_to_file(path, include_deleted=include_deleted)
    print("[+] Exported detections to {p}".format(p=path))


def cmd_detections_import():
    path = input("[?] Input JSON path to import from: ").strip()
    if not path:
        print("[!] No path provided.")
        return

    if not os.path.exists(path):
        print("[!] File does not exist: {p}".format(p=path))
        return

    import_detections_from_file(path)
    print("[+] Imported detections from {p}".format(p=path))


def cmd_reload():
    broadcast_event(Events.INITIALIZE)
    print("[+] Reloaded from disk...")


def initialize():
    global original_sigint

    # Save the original signal handler
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, handler)

    print(BANNER)


def handler(sig, frame):
    # Pass it to the original handler
    signal.signal(signal.SIGINT, original_sigint)

    while True:
        command = prompt()

        try:
            if command == "resume":
                break

            commands[command]["handler"]()

        except SystemExit:
            break

        except KeyboardInterrupt:
            signal.signal(signal.SIGINT, handler)

        except:
            print("[!] Unknown command! Type 'help' for help.")

        signal.signal(signal.SIGINT, handler)


commands = {
    "exit": {
        "help": "Quits the program.",
        "handler": cmd_exit
    },
    "help": {
        "help": "Displays this help dialog.",
        "handler": cmd_help
    },
    "add": {
        "help": "Adds a new IOC.",
        "handler": cmd_add
    },
    "iocs": {
        "help": "Reloads all IOCs from disk.",
        "handler": cmd_iocs
    },
    "detections": {
        "help": "Lists current detections.",
        "handler": cmd_detections_list
    },
    "detections_add": {
        "help": "Adds a manual detection.",
        "handler": cmd_detections_add
    },
    "detections_remove": {
        "help": "Soft-deletes a detection by hash.",
        "handler": cmd_detections_remove
    },
    "detections_restore": {
        "help": "Restores a previously soft-deleted detection.",
        "handler": cmd_detections_restore
    },
    "detections_remove_source": {
        "help": "Removes a collector source from a detection.",
        "handler": cmd_detections_remove_source
    },
    "detections_show": {
        "help": "Shows details for a specific detection.",
        "handler": cmd_detections_show
    },
    "detections_export": {
        "help": "Exports detections to a JSON file.",
        "handler": cmd_detections_export
    },
    "detections_import": {
        "help": "Imports detections from a JSON file.",
        "handler": cmd_detections_import
    },
    "reload": {
        "help": "Reloads everything from disk.",
        "handler": cmd_reload
    }
}

subscribe_to_event(Events.INITIALIZE, initialize)
