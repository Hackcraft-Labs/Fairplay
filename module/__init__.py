from config import verify_config_key, get_config_key, get_config
from event import Events, subscribe_to_event

import traceback
import importlib
import logging
import os

modules = {}


def nop(*args):
    pass


class Module():
    def __init__(self):
        self.verify("enabled")
        if not self.get_key("enabled"):
            self.execute = nop

    def verify(self, key):
        verify_config_key(key, self)

    def get_key(self, key):
        return get_config_key(key, self)


def load_module(category, name):
    module_name = "{category}.{name}".format(category=category, name=name)
    try:
        module = importlib.import_module(module_name)
        logging.info("Imported module '{module_name}'.".format(module_name=module_name))
    except Exception as e:
        print("[!] Could not import module {module_name}!".format(
            module_name=module_name))
        traceback.print_exception(e)
        os._exit(1)

    if not name in dir(module):
        print("[!] Could not import module {module_name} because it does not contain a class named '{class_name}'!".format(
            module_name=module_name, class_name=name))
        os._exit(1)

    attribute = getattr(module, name)

    attribute.NAME = name
    attribute.CATEGORY = category

    return attribute()


def load_modules():
    global modules
    config = get_config()

    for category in config:
        modules[category] = []

        for module in config[category]:
            loaded_module = load_module(category, module)
            modules[category].append(loaded_module)

    logging.info("Loaded all modules.")

    return modules


subscribe_to_event(Events.INITIALIZE, load_modules)
