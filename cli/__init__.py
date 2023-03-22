from event import Events, broadcast_event, subscribe_to_event
from ioc import load_iocs, add_ioc

import os
import sys
import signal

BANNER = \
    """
███████╗ █████╗ ██╗██████╗ ██████╗ ██╗      █████╗ ██╗   ██╗
██╔════╝██╔══██╗██║██╔══██╗██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝
█████╗  ███████║██║██████╔╝██████╔╝██║     ███████║ ╚████╔╝
██╔══╝  ██╔══██║██║██╔══██╗██╔═══╝ ██║     ██╔══██║  ╚██╔╝
██║     ██║  ██║██║██║  ██║██║     ███████╗██║  ██║   ██║  (1.2)

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
    file_hash = input("[?] File Hash: ").strip()
    add_ioc(name, file_hash)
    load_iocs()
    print("[+} Added IOC!")


def cmd_iocs():
    load_iocs()
    print("[+] Reloaded IOCs from disk...")


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
    "reload": {
        "help": "Reloads everything from disk.",
        "handler": cmd_reload
    }
}

subscribe_to_event(Events.INITIALIZE, initialize)
