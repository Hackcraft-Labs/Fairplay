import sys
import time
import signal
import logging
import schedule
import traceback

import module

from ioc import schedule_iocs
from event import Events, broadcast_event

import cli

if __name__ == "__main__":
    broadcast_event(Events.INITIALIZE)
    logging.info("Initialized Fairplay!")

    try:
        schedule_iocs()
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)

            except KeyboardInterrupt:
                signal.signal(signal.SIGINT, cli.handler)

    except SystemExit:
        broadcast_event(Events.TERMINATE)
        sys.exit(0)

    except:
        print("[!] Generic error! Please be kind enough to open an issue with the stack trace information below:")

        print("")
        traceback.print_exc()
        print("")

        print("[+] Exiting gracefully...")
        logging.info("Terminating Fairplay!")
        broadcast_event(Events.TERMINATE)
        sys.exit(1)
