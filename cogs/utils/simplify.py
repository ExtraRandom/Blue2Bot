
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
