import discord
from discord.ext import commands
from discord.utils import get
import json
from datetime import datetime
import asyncio
import random
import custom_processing
import os

bot = commands.Bot(command_prefix='=', description="Stellar Bot", pm_help=False)


@bot.event
async def on_ready():
    login_time = datetime.utcnow()
    print("Bot Logged In at {} UTC".format(login_time))


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

    # print(skiz, extr)

    if skiz.status == discord.Status.offline and extr.status == discord.Status.offline:
        # await bot.send_message(c, "No mod's are online.")
        pass
    else:
        # print("Mod's online")
        return

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

    if isinstance(error, commands.MissingRequiredArgument):
        await bot.send_message(channel, "Missing Argument")
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.CheckFailure):
        await bot.send_message(channel, "You do not have permission to use that command!")

    else:
        await bot.send_message(channel, "**Command Errored:**\n "
                                        "{}".format(error))


async def custom_reaction(message):
    msg = str(message.content).lower()

    with open("configs/custom_reacts.json", "r") as f:
        data = json.loads(f.read())
        user = str(message.author)
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
                    # when = str(data[user][i]['when'])

                    # print(message.content)

                    if msg.startswith(word.lower()):
                        pass  # print("starts with")
                    elif " {} ".format(word.lower()) in msg:
                        pass  # print("in there with spaces")
                    elif "{} ".format(word.lower()) in msg:
                        pass  # print("in there with space after")
                    elif " {}".format(word.lower()) in msg:
                        pass  # print("in there with space before")
                    else:
                        # print("probably an emoji")
                        return
                    await react(message, emoji)

        except Exception as e:
            pass


async def react(msg, emoji):
    try:
        await bot.add_reaction(msg, emoji)
    except Exception as e:
        print(e)
        return


if __name__ == '__main__':
    first_time = False
    data = {}
    cd = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(cd, "configs", "settings.json")  # "/configs/settings.json"
    # print(file)

    if os.path.isfile(filepath) is False:
        print("First Time running")
        # file doesn't exist
        first_time = True
        data['token'] = None
        data['cogs'] = {}
    else:
        with open(filepath, "r") as f:
            f_data = f.read()
            data = json.loads(f_data)

    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            cog_name = file.replace(".py", "")
            cog_path = "cogs.{}".format(cog_name)  # os.path.join("cogs/", cog_name)
            # print(cog_name, cog_path)

            if first_time is True:
                data['cogs'][cog_name] = True
                should_load = True
            else:
                should_load = data['cogs'][cog_name]
            if should_load is True:
                try:
                    bot.load_extension(cog_path)
                    print("Sucessfully loaded cog '{}'".format(cog_name))
                except Exception as e:
                    print("Failed to load cog '{}', Reason: {}".format(cog_name, type(e).__name__))

    if first_time is True:
        with open(filepath, "w") as f:
            print("dumping data")
            json.dump(data, f, indent=4)
        token = None
    else:
        token = data['token']

    if token:
        bot.run(token)
    else:
        print("Token is not set! Go to {} and change the token parameter!".format(filepath))


