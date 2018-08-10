from cogs.utils import IO
import requests
import json


def remove_prefix_in_message(bot, message, command_name):
    """Removes prefix and the command from the message string"""
    cmd = command_name
    prefixes = bot.command_prefix(bot, message)
    result = ""
    for prefix in prefixes:
        if prefix in message.content:
            replace_str = "{}{} ".format(prefix, cmd)
            result = str(message.content).strip().replace(replace_str, "")
            if result == "{}{}".format(prefix, cmd):
                return None

    return result


def remove_prefix_no_command(bot, message):
    """Similar to remove_prefix_in_message but doesn't remove the command from the message string"""
    prefixes = bot.command_prefix(bot, message)
    result = ""
    for prefix in prefixes:
        if prefix in message.content:
            replace_str = "{}".format(prefix)
            result = str(message.content).strip().replace(replace_str, "")

    return result


def convert_USD_to_GBP(amount):
    """For converting USD into EUR and then into GBP (due to limitation's of the API)
    Used for the chrono command, shouldn't be used anywhere else"""
    def get_page_data(page):
        """Get the Raw Data (whether that be html or json) of the URL given"""
        response = requests.request("GET", page)
        if response.status_code == requests.codes.ok:
            return response.text
        else:
            return "Error"

    s_data = IO.read_settings_as_json()
    if s_data is not None:
        api_key = s_data["keys"]["fixer-io-key"]
    else:
        return -1

    if api_key is None:
        return -2

    url = "http://data.fixer.io/api/latest?access_key={}&format=1&symbols=GBP,USD".format(api_key)

    j_data = get_page_data(url)
    if j_data == "Error":
        return -3

    data = json.loads(j_data)

    EUR_GBP = float(data["rates"]["GBP"])
    EUR_USD = float(data["rates"]["USD"])

    amount_to_EUR = amount / EUR_USD
    amount_to_GBP = amount_to_EUR * EUR_GBP

    return round(amount_to_GBP, 2)







