import os
import json

CONFIG_FILE = 'config/config.json'

config = None


def load_config():
    global config

    try:
        with open(CONFIG_FILE, "r") as settings_file:
            try:
                config = json.loads(settings_file.read())
            except:
                print("[!] Could not parse configuration file '{file}'!".format(
                    file=CONFIG_FILE))
    except:
        print("[!] Could not open file '{file}'!".format(file=CONFIG_FILE))

    return config


def get_config_key(key, module):
    if not config:
        load_config()

    return config[module.CATEGORY][module.NAME][key]


def verify_config_key(key, module):
    if not config:
        load_config()

    if not module.CATEGORY in config:
        print(
            "[!] Category '{name}' is missing its configuration block entirely!".format(name=module.CATEGORY))
        os._exit(1)

    if not module.NAME in config[module.CATEGORY]:
        print(
            "[!] Module '{name}' is missing its configuration block entirely!".format(name=module.NAME))
        os._exit(1)

    if not key in config[module.CATEGORY][module.NAME]:
        print("[!] Module '{name}' is missing key '{key}' in its configuration!".format(
            name=module.NAME, key=key))
        os._exit(1)


def get_config():
    if not config:
        load_config()

    return config
