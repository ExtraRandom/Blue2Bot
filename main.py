import discord
from discord.ext import commands
from discord.utils import get
from datetime import datetime
import asyncio
import os
from cogs.utils import perms, IO
from cogs.utils.logger import Logger

bot = commands.Bot(command_prefix='=',
                   description="Stellar Bot\n"
                               "Developed by @Extra_Random#2564\n"
                               "Source code: https://github.com/ExtraRandom/StellarBot\n"
                               "Report an Issue: "
                               "https://github.com/ExtraRandom/StellarBot/issues/new"
                   , pm_help=False)


@bot.event
async def on_ready():
    login_time = datetime.now()
    data = IO.read_settings_as_json()

    if data is None:
        raise Exception(IO.settings_fail_read)

    data['last-login-time'] = str(login_time)

    if IO.write_settings(data) is False:
        print(IO.settings_fail_write)

    Logger.write_and_print("Bot Logged In at {}".format(login_time))
    # Logger.check_for_folder()
    # print(Logger.get_filename())


@bot.event
async def on_message(message):
    bot_msg = message.author.bot
    if bot_msg is True:
        return

    if not message.channel.is_private:
        await custom_reaction(message)

    if message.content == "are you sure about that":
        await bot.send_message(message.channel,
                               "https://media1.tenor.com/images/43fa142652563cb2035049e95ae639b6/"
                               "tenor.gif?itemid=10002272")

    # await custom_processing.process_custom(message)

    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    # print(member.name)

    s = bot.get_server("442608736864043008")
    c = s.get_channel("449352501393621012")
    r = s.roles

    def get_member_from_id(id):
        return s.get_member(id)

    def get_role_from_id(id):
        for role in r:
            if role.id == id:
                return role

    m_role = get_role_from_id("448402174985240576")
    o_role = get_role_from_id("449194917411946496")

    skiz = get_member_from_id("438678163229507584")
    extr = get_member_from_id("92562410493202432")

    data = IO.read_settings_as_json()
    if data is None:
        await bot.send_message(c, "Warning: Failed to read settings to check whether to handle welcoming newcomers.\n"
                                  "Will not handle until this issue is fixed.")
        return

    if data['handle-newcomers'] is False:
        # If False then bot will only handle newcomers when Mod's are offline
        if skiz.status == discord.Status.offline and extr.status == discord.Status.offline:
            # await bot.send_message(c, "No mod's are online.")
            pass
        else:
            # print("Mod's online")
            return
    else:
        # If true then bot will handle newcomers no matter what
        pass

    await bot.send_message(c, "Hello there {}. Please take a moment to read the rules!".format(member.mention))

    await asyncio.sleep(10)

    r_msg = await bot.send_message(c, "Once you have read the rules, react with the tick if you agree or "
                                      "the cross if you do not agree. Thanks!")

    await bot.add_reaction(r_msg, get(bot.get_all_emojis(), name="SBE_yes"))
    await bot.add_reaction(r_msg, get(bot.get_all_emojis(), name="SBE_no"))

    def check(reaction, user):

        e_list = ["SBE_yes", "SBE_no"]
        e = reaction.emoji

        if e.name in e_list:
            return True
        else:
            return False

    r_res = await bot.wait_for_reaction(message=r_msg,
                                        timeout=180,
                                        user=member,
                                        check=check)

    if r_res is not None:
        # await bot.send_message(c, "reaction was {0.reaction.emoji.name}".format(r_res))
        if r_res.reaction.emoji.name == "SBE_yes":
            # user accepts
            await bot.send_message(c, "Thanks for accepting! Setting up your roles now!")
            await bot.add_roles(member, m_role)
            await bot.remove_roles(member, o_role)
            return
        else:
            # user doesn't accept
            await bot.send_message(c, "Ok then... Byeeeee")
            await bot.kick(member)
            return
    else:
        # user didn't reply within 3 minutes
        await bot.send(c, "3 Minutes with no reply... Bye then")
        await bot.kick(member)
        return


@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel

    # r_cmd = ctx.message.content
    # cmd = r_cmd.split(" ")[0].replace(bot.command_prefix, "")
    # print(cmd)

    if isinstance(error, commands.MissingRequiredArgument):
        # c_obj = bot.get_command(cmd)
        # print(c_obj.help)

        await bot.send_message(channel, "Missing Argument")
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.CheckFailure):
        await bot.send_message(channel, "You do not have permission to use that command!")

    else:
        await bot.send_message(channel, "**Command Errored:**\n "
                                        "{}".format(error))


@bot.command(hidden=True)
@perms.is_dev()
async def load(*, cog: str):
    """Load a cog"""
    cog_list = []
    for c_file in os.listdir("cogs"):
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
@perms.is_server_owners()
async def bot_welcome():
    """Toggle bot dealing with new people (MODS ONLY)
    Toggles whether bot handles newcomers when mods are online
    Bot will still handle newcomers when no mods are online despite whether this is set or not"""

    data = IO.read_settings_as_json()
    if data is None:
        await bot.say(IO.settings_fail_read)
        return

    current = bool(data['handle-newcomers'])

    new = not current
    data['handle-newcomers'] = new

    if IO.write_settings(data) is False:
        await bot.say(IO.settings_fail_write)
        return

    if current is True:
        await bot.say("Turning off bot welcome handling, will still handle newcomers if no mods are online")
    else:
        await bot.say("Turning on bot welcome handling")


async def custom_reaction(message):
    msg = str(message.content).lower()
    user = "{}#{}".format(message.author.name, message.author.discriminator)

    data = IO.read_custom_reacts_as_json()
    if data is None:
        Logger.write_and_print(IO.react_fail_read)
        return False

    try:
        test = data[user]
    except KeyError as ex:
        return False

    try:
        for i in range(len(data[user])):
            try:
                word = data[user][i]['word']
            except KeyError:
                print("Key Error")
                return False

            if word in msg:
                emoji = get(bot.get_all_emojis(), name=data[user][i]['emoji'])
                if emoji is None:
                    await bot.send_message(message.channel, "Emoji '{}' doesn't exist!".format(data[user][i]['emoji']))
                    return

                if msg.startswith(word.lower()):
                    pass
                elif " {} ".format(word.lower()) in msg:
                    pass
                elif "{} ".format(word.lower()) in msg:
                    pass
                elif " {}".format(word.lower()) in msg:
                    pass
                else:
                    return
                await react(message, emoji)

    except Exception as e:
        Logger.write(e)


async def react(msg, emoji):
    try:
        await bot.add_reaction(msg, emoji)
    except Exception as ex:
        Logger.write(ex)
        return


def get_cogs_in_folder():
    c_list = []
    for file in os.listdir("cogs"):
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
        s_data['token'] = None
        s_data['handle-newcomers'] = False
        s_data['cogs'] = {}
        s_data['last-login-time'] = None
    else:
        s_data = IO.read_settings_as_json()
        if s_data is None:
            raise Exception(IO.settings_fail_read)

    """Update JSON with new settings if it doesn't have them to prevent potential issues"""
    try:
        test_newcomers = s_data['handle-newcomers']
    except KeyError:
        s_data['handle-newcomers'] = False

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
                print("New Cog {}".format(folder_cog))
                s_data['cogs'][folder_cog] = True
                should_load = True

            if should_load is True:
                try:
                    bot.load_extension(cog_path)
                except Exception as exc:
                    print("Failed to load cog '{}', Reason: {}".format(folder_cog, type(exc).__name__))

    """Get token"""
    if first_time is True:
        if IO.write_settings(s_data) is False:
            raise Exception(IO.settings_fail_write)
        token = None
    else:
        token = s_data['token']

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


