import os
import json
from cogs.utils.logger import Logger

# Logger IO is handled in logger.py

settings_fail_read = "Failed to read settings"
settings_fail_write = "Failed to write settings"

react_fail_read = "Failed to read custom reacts file"
react_fail_write = "Failed to write custom reacts file"

c_dir = os.path.dirname(os.path.realpath(__file__))
cwd = os.path.dirname(os.path.dirname(c_dir))

settings_file_path = os.path.join(cwd, "configs", "settings.json")
reacts_file_path = os.path.join(cwd, "configs", "custom_reacts.json")


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




