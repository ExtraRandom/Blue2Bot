import discord
from discord.ext import commands
from discord.utils import get
from datetime import datetime
import os
from cogs.utils import perms, IO, simplify
from cogs.utils.logger import Logger


def get_prefix(d_bot, message):
    prefixes = ["?", "="]

    if message.channel.is_private:
        return '?'
    else:
        return commands.when_mentioned_or(*prefixes)(d_bot, message)


bot = commands.Bot(command_prefix=get_prefix,
                   description="Bot Developed by @Extra_Random#2564\n"
                               "Source code: https://github.com/ExtraRandom/Blue2Bot\n"
                               "Report an Issue: https://github.com/ExtraRandom/Blue2Bot/issues/new",
                   pm_help=False)


@bot.event
async def on_ready():
    login_time = datetime.now()
    data = IO.read_settings_as_json()

    if data is None:
        raise Exception(IO.settings_fail_read)

    data['info']['last-login-time'] = str(login_time)

    if IO.write_settings(data) is False:
        print(IO.settings_fail_write)

    login_msg = "Bot Logged In at {}".format(login_time)
    Logger.log_write("----------------------------------------------------------\n"
                     "{}\n"
                     "".format(login_msg))
    print(login_msg)

    game = discord.Game(name="@Blue2#2113 help")
    await bot.change_presence(game=game)


@bot.event
async def on_message(message):
    bot_msg = message.author.bot
    if bot_msg is True:
        return

    if message.content == "are you sure about that":
        await bot.send_message(message.channel,
                               "https://media1.tenor.com/images/43fa142652563cb2035049e95ae639b6/"
                               "tenor.gif?itemid=10002272")

    await bot.process_commands(message)


@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel

    if isinstance(error, commands.MissingRequiredArgument):
        # c_obj = bot.get_command(cmd)
        # print(c_obj.help)
        await bot.send_message(channel, "Missing Argument")
    elif isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.CheckFailure):
        await bot.send_message(channel, "You do not have permission to use that command!")

    else:
        cmd = simplify.remove_prefix_no_command(bot, ctx.message)
        cog = bot.get_command(cmd).cog_name

        err_msg = "----------------------------------------------------------\n" \
                  "An Error Occurred at {}\n" \
                  "Command: {}\n" \
                  "    Cog: {}\n" \
                  "  Error: {}\n" \
                  "   Args: {}\n" \
                  "----------------------------------------------------------" \
                  "".format(Logger.time_now(), cmd, cog, error.original, error.args)
        Logger.log_write(err_msg)
        await bot.send_message(channel, "**Command Errored:**\n "
                                        "{}".format(error))


@bot.command(hidden=True)
@perms.is_dev()
async def load(*, cog: str):
    """Load a cog"""
    cog_list = []
    c_dir = os.path.dirname(os.path.realpath(__file__))
    for c_file in os.listdir(os.path.join(c_dir, "cogs")):
        if c_file.endswith(".py"):
            cog_list.append("cogs.{}".format(c_file.replace(".py", "")))

    l_cog_name = "cogs.{}".format(cog)  # print(cog, cog_name, cog_list)

    if l_cog_name in cog_list:
        try:
            bot.load_extension(l_cog_name)
            await bot.say("Successfully loaded cog '{}'.".format(cog))
        except Exception as e:
            await bot.say("Failed to load cog '{}'. Reason: {}".format(cog, type(e).__name__))
            return
    else:
        await bot.say("No cog called '{}'.".format(cog))
        return

    data = IO.read_settings_as_json()
    if data is None:
        await bot.say(IO.settings_fail_read)
        return

    data['cogs'][cog] = True

    if IO.write_settings(data) is False:
        await bot.say(IO.settings_fail_write)
        return


@bot.command(hidden=True)
@perms.is_dev()
async def unload(*, cog: str):
    """Unload a cog"""
    ext_list = bot.extensions
    cog_list = []
    for cogs in ext_list:
        cog_list.append(cogs)

    l_cog_name = "cogs.{}".format(cog)  # print(cog, cog_name, cog_list)

    if l_cog_name in cog_list:
        try:
            bot.unload_extension(l_cog_name)
            await bot.say("Successfully unloaded cog '{}'.".format(cog))
        except Exception as e:
            await bot.say("Failed to unload cog '{}'. Reason: {}".format(cog, type(e).__name__))
            return
    else:
        await bot.say("No (loaded) cog called '{}'.".format(cog))
        return

    data = IO.read_settings_as_json()
    if data is None:
        await bot.say(IO.settings_fail_read)
        return
    data['cogs'][cog] = False
    if IO.write_settings(data) is False:
        await bot.say(IO.settings_fail_write)
        return


@bot.command(hidden=True)
@perms.is_dev()
async def shutdown():
    """Should be pretty obvious what this does"""
    await bot.say("Shutting down...")
    await bot.logout()


def get_cogs_in_folder():
    c_dir = os.path.dirname(os.path.realpath(__file__))
    c_list = []
    for file in os.listdir(os.path.join(c_dir, "cogs")):
        if file.endswith(".py"):
            c_list.append(file.replace(".py", ""))
    return c_list


def get_cogs_in_settings():
    c_list = []
    data = IO.read_settings_as_json()
    if data is None:
        return None
    for cog in data['cogs']:
        c_list.append(cog)
    return c_list


if __name__ == '__main__':
    first_time = False
    s_data = {}
    should_write_after_finish = False

    """First time run check"""
    if os.path.isfile(IO.settings_file_path) is False:
        print("First Time Run - Creating Settings JSON")
        first_time = True
        s_data['keys'] = {}
        s_data['keys']['token'] = None
        s_data['keys']['itad-api-key'] = None
        s_data['cogs'] = {}
        s_data['info'] = {}
        s_data['info']['last-login-time'] = None
        s_data['info']['chrono-last-check'] = None
        s_data['info']['chrono-true-last-check'] = None
    else:
        s_data = IO.read_settings_as_json()
        if s_data is None:
            raise Exception(IO.settings_fail_read)

    """Load cogs"""
    folder_cogs = get_cogs_in_folder()
    for folder_cog in folder_cogs:
        cog_path = "cogs.{}".format(folder_cog)
        if first_time is True:
            s_data['cogs'][folder_cog] = True
            should_load = True
        else:
            try:
                should_load = s_data['cogs'][folder_cog]
            except KeyError:
                print("New Cog '{}'".format(folder_cog))
                s_data['cogs'][folder_cog] = True
                should_load = True
                should_write_after_finish = True

            if should_load is True:
                try:
                    bot.load_extension(cog_path)
                except Exception as exc:
                    print("Failed to load cog '{}', Reason: {}".format(folder_cog, type(exc).__name__))
                    Logger.write(exc)

    """Get token"""
    if first_time is True:
        if IO.write_settings(s_data) is False:
            raise Exception(IO.settings_fail_write)
        token = None
    else:
        token = s_data['keys']['token']

    """Clean up removed cogs from settings"""
    r_cogs = get_cogs_in_folder()
    f_cogs = get_cogs_in_settings()
    for f_cog in f_cogs:
        if f_cog not in r_cogs:
            print("Cog {} no longer exists, removing settings entry".format(f_cog))
            del s_data['cogs'][f_cog]
            should_write_after_finish = True

    """Write settings to file"""
    if should_write_after_finish is True:
        if IO.write_settings(s_data) is False:
            raise Exception(IO.settings_fail_write)

    if token:
        bot.run(token)
    else:
        print("Token is not set! Go to {} and change the token parameter!".format(IO.settings_file_path))


