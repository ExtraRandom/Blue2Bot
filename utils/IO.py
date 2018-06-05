import os
import json
from utils.logger import Logger

# TODO handle all file IO here

# Most methods are using this except for react commands in general
# Logger IO is handled in logger.py

generic_fail_read = "Failed to read settings"
generic_fail_write = "Failed to write settings"

settings_file_path = os.path.join("configs", "settings.json")
reacts_file_path = os.path.join("configs", "custom_reacts.json")


def read_settings_as_json():
    """Read the settings.json file and then return as python object
    Returns none if failed"""
    try:
        with open(settings_file_path, "r") as f:
            r_data = f.read()
            data = json.loads(r_data)
            return data

    except Exception as e:
        Logger.write(e)
        return None


def write_settings(data):
    """Write data to the settings file.
    Returns true if successful, False if not"""
    try:
        with open(settings_file_path, "w") as f:
            json.dump(data, f, indent=4)
            return True

    except Exception as e:
        Logger.write(e)
        return False


def read_custom_reacts_as_json():
    """Read in custom_reacts.json file and return as python object
    Returns none if failed to read"""

    try:
        with open(reacts_file_path, "r") as f:
            r_data = f.read()
            data = json.loads(r_data)
            return data

    except Exception as e:
        Logger.write(e)
        return None


def write_custom_reacts(data):
    """Write data to the custom react file.
    Returns true if successful, False if not"""
    try:
        with open(reacts_file_path, "w") as f:
            json.dump(data, f, indent=4)
            return True

    except Exception as e:
        Logger.write(e)
        return False




