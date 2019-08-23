import requests
import json
import os
from cogs.utils.logger import Logger
import hashlib

url_base = "https://pogoapi.net/api/v1/"
base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
hashes = "api_hashes.json"


def get_data(endpoint):
    return __get_or_read_cache(endpoint)


def test():
    __get_or_read_cache("raid_exclusive_pokemon.json")


def __get_or_read_cache(url_end):
    # print(url_end)

    # TODO only check cache every x amount of time or something
    hash_data = json.loads(__get_data_from_url(hashes))

    true_md5 = hash_data[url_end]['hash_md5']

    data = __get_data_from_url(url_end)
    json_data = json.loads(data)

    file_path = os.path.join(base_dir, "data", url_end)

    if os.path.exists(file_path):
        with open(file_path, 'rb', ) as f:
            old_data = f.read()

        test_md5 = hashlib.md5(old_data).hexdigest()
        # print(true_md5, test_md5)

        if test_md5 == true_md5:
            return json.loads(old_data.decode('utf-8'))
        else:
            new_data = __get_data_from_url(url_end)
            __file_write_bytes(file_path, new_data.encode('utf-8'))
            return json.loads(new_data)

    else:
        __file_write_bytes(file_path, data.encode('utf-8'))
        return json_data


def __file_read_bytes(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    return data


def __file_write_bytes(filepath, json_bytes):
    try:
        with open(filepath, "wb") as fw:
            fw.write(json_bytes)
            return
    except Exception as e:
        Logger.write(e)
        return


def __get_data_from_url(url_end):
    res = requests.get(url=(url_base+url_end))
    if res.status_code == requests.codes.ok:
        return res.text
    else:
        return None






