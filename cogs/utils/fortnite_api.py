import requests
import json
import os
from cogs.utils import IO
from cogs.utils.logger import Logger
import time


url_base = "https://fortnite-public-api.theapinetwork.com/prod09/"
base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

challenges_json = os.path.join(base_dir, "data", "fortnite_challenges.json")
store_json = os.path.join(base_dir, "data", "fortnite_store.json")


def get_challenges():
    url_end = "challenges/get"
    filepath = challenges_json
    payload = {
        "season": "current",
        "language": "en"
    }

    return __get_or_read_cache(url_end, filepath, payload)


def get_store():
    url_end = "store/get"
    filepath = store_json
    payload = {
        "language": "en"
    }

    return __get_or_read_cache(url_end, filepath, payload)


def __get_or_read_cache(url_end, filepath, payload):
    if os.path.isfile(filepath):
        c_data = __file_read(filepath)
        if "cached_time" in c_data:
            time_then = c_data["cached_time"]
            time_now = time.time()

            if (time_now - time_then) >= 60 * 60 * 2:
                r_data = __get_data_from_url(url_end, payload)
                j_data = json.loads(r_data)
                j_data["cached_time"] = time.time()
                __file_write(filepath, j_data)
                return j_data, False
            else:
                return c_data, True
        else:
            r_data = __get_data_from_url(url_end, payload)
            j_data = json.loads(r_data)
            j_data["cached_time"] = time.time()
            __file_write(filepath, j_data)
            return j_data, False

    else:  # file doesnt exist
        r_data = __get_data_from_url(url_end, payload)
        j_data = json.loads(r_data)
        j_data["cached_time"] = time.time()
        __file_write(filepath, j_data)
        return j_data, False


def __file_read(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


def __file_write(filepath, json_obj):
    try:
        with open(filepath, "w") as fw:
            json.dump(json_obj, fw, indent=4)
            return
    except Exception as e:
        Logger.write(e)
        return


def __get_data_from_url(url_end, payload):
    res = requests.post(url=(url_base+url_end),
                        data=payload,
                        headers={"Authorization": __read_api_key_from_file()})
    print(res.status_code)
    if res.status_code == requests.codes.ok:
        return res.text
    else:
        return None


def __read_api_key_from_file():
    s_data = IO.read_settings_as_json()
    if s_data is None:
        return ""
    else:
        return s_data["keys"]["ftn-api-key"]





