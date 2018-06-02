from discord.ext import commands
import json
import discord
from discord.utils import get
import perms


class General:
    def __init__(self, bot):
        self.bot = bot

    # TODO add edit react command

    """
    @commands.command()
    async def test_online(self):
        s = self.bot.get_server("442608736864043008")
        c = s.get_channel("449352501393621012")
        r = s.roles

        def get_member_from_id(id):
            return s.get_member(id)

        skiz = get_member_from_id("438678163229507584")
        extr = get_member_from_id("92562410493202432")

        print(skiz, extr)
        print(skiz.status, extr.status)
    """

    @commands.group(pass_context=True)
    async def react(self, ctx):
        """Use =help react to see subcommands"""
        if ctx.invoked_subcommand is None:
            await self.bot.say("Use '=help react' to see subcommands")

    @react.command(pass_context=True, aliases=["rs"])
    @perms.is_server_owner_or_dev()
    async def add(self, ctx):
        """For adding custom reacts for people (MOD ONLY)"""
        # http://discordpy.readthedocs.io/en/latest/api.html#discord.Client.wait_for_reaction

        e_emoji = None
        e_user = None
        e_word = None

        mentioned = None
        t_res = None

        if len(ctx.message.mentions) > 0:
            mentioned = ctx.message.mentions[0]
        else:
            await self.bot.say("Please @ mention the user you would like to add a react for")
            t_res = await self.bot.wait_for_message(author=ctx.message.author,
                                                    channel=ctx.message.channel,
                                                    timeout=60)
        if mentioned is None:
            if t_res is not None:

                if len(t_res.mentions) > 0:
                    mentioned = t_res.mentions[0]
                else:
                    await self.bot.say("No @mention in that message...")
                    return

        if mentioned is not None:
            if mentioned.bot is True:
                await self.bot.say("This command can not be used on bots.")
                return
            else:
                e_user = "{0.name}#{0.discriminator}".format(mentioned)

        else:
            await self.bot.say("No @ mention. Where did you go?")
            return

        r_msg = await self.bot.say("Wait one moment")

        s = self.bot.get_server("450955854871658496")
        for emoji in s.emojis:
            try:
                await self.bot.add_reaction(r_msg, emoji)
            except Exception as e:
                await self.bot.say("Please don't add other reactions >:(")
                return

        await self.bot.edit_message(r_msg, "Please select one of these emoji's")

        def check(reaction, user):
            e = reaction.emoji
            if e in s.emojis:
                return True
            else:
                return False

        res = await self.bot.wait_for_reaction(message=r_msg,
                                               timeout=60,
                                               check=check,
                                               user=ctx.message.author)

        if res is not None:
            e_emoji = res.reaction.emoji.name
            # await self.bot.say("{0.user} reacted with {0.reaction.emoji}".format(res))

        else:
            await self.bot.say("You didn't pick an emoji. Are you still there?")
            return

        await self.bot.say("Lastly, please type the word you would like to trigger this react.\n"
                           "If you enter more than one word, only the first will be used as the trigger.")

        w_msg = await self.bot.wait_for_message(author=ctx.message.author,
                                                channel=ctx.message.channel,
                                                timeout=60)

        if w_msg is not None:
            e_word = str(w_msg.content).split(" ")[0]
            # await self.bot.say("{} {} {}".format(e_emoji, e_user, e_word))
        else:
            await self.bot.say("No reply... so close yet so far.")

        worked = add_to_file(e_user, e_word.lower(), e_emoji)
        if worked is True:
            await self.bot.say("Added!")
            return
        else:
            await self.bot.say("An error occurred when writing to the file!")
            return

    @react.command(pass_context=True)
    @perms.is_server_owner_or_dev()
    async def remove(self, ctx):
        """For removing a custom react from a user (MOD ONLY)"""
        e_user = None
        e_word = None

        if len(ctx.message.mentions) > 0:
            # print("mentions m8")
            mentioned = ctx.message.mentions[0]
            if mentioned.bot is False:
                e_user = "{0.name}#{0.discriminator}".format(mentioned)
            else:
                await self.bot.say("This command can not be used on bots.")
                return
            # print(e_user)
        else:
            # No react given so ask for one instead
            await self.bot.say("Please mention the user you would like to remove a react from")
            m_res = await self.bot.wait_for_message(author=ctx.message.author,
                                                    channel=ctx.message.channel,
                                                    timeout=60)
            if m_res is not None:
                if len(m_res.mentions) > 0:
                    mentioned = m_res.mentions[0]
                    if mentioned.bot is False:
                        e_user = "{0.name}#{0.discriminator}".format(mentioned)
                    else:
                        await self.bot.say("This command can not be used on bots.")
                        return
                else:
                    await self.bot.say("No @mention in that message...")
                    return

            else:
                await self.bot.say("No reply")
                return

        if e_user is None:
            # just to make sure
            await self.bot.say("Error occured. e_user is not set")
            return

        data = read_in_file()

        result = discord.Embed(title="{}'s Reacts".format(e_user),

                               colour=discord.Colour.red())

        word_list = []

        if e_user in data:
            for i in range(len(data[e_user])):
                word_list.append(data[e_user][i]['word'])

                emoji = get(self.bot.get_all_emojis(), name=data[e_user][i]['emoji'])
                result.add_field(name="{}".format(data[e_user][i]['word']),
                                 value="{}".format(emoji))  # .format(data[user][i]['emoji']))

        if len(word_list) == 0:
            await self.bot.say("User '{}' has no react word triggers to remove.".format(e_user))
            return

        await self.bot.say(embed=result)
        await self.bot.say("Reply with the word you would like to remove. (See list above)")

        w_res = await self.bot.wait_for_message(author=ctx.message.author,
                                                channel=ctx.message.channel,
                                                timeout=60)

        # print(word_list)

        if w_res is not None:
            if str(w_res.content).lower() in word_list:
                e_word = str(w_res.content).lower()
            else:
                await self.bot.say("That react isn't in the list...")
                return
        else:
            await self.bot.say("No Reply... :(")
            return

        # print(e_user, ": ", e_word)

        data = read_in_file()

        if e_user in data:
            for i in range(len(data[e_user])):
                # print(data[e_user][i]['word'])
                if e_word in data[e_user][i]['word']:
                    del data[e_user][i]
                    with open("configs/custom_reacts.json", "w") as f:
                        json.dump(data, f, indent=4)

                        await self.bot.say("Word removed!")
                        return

    @react.command()
    @perms.is_server_owner_or_dev()
    async def list(self):
        """List the available reaction options"""
        r_msg = await self.bot.say("Reaction Options: ")
        s = self.bot.get_server("450955854871658496")
        for emoji in s.emojis:
            try:
                await self.bot.add_reaction(r_msg, emoji)
            except Exception as e:
                await self.bot.say("Please don't add other reactions >:(")
                return

    @react.command()
    @perms.is_server_owner_or_dev()
    async def view(self, user: str):
        """View all of a user's reacts (MOD ONLY)"""

        # print(user)
        user = await General.process_user(self, user)
        # print(user)

        data = read_in_file()

        result = discord.Embed(title="{}'s Reacts".format(user),

                               colour=discord.Colour.red())

        if user in data:
            for i in range(len(data[user])):
                emoji = get(self.bot.get_all_emojis(), name=data[user][i]['emoji'])
                result.add_field(name="{}".format(data[user][i]['word']),
                                 value="{}".format(emoji))  # .format(data[user][i]['emoji']))

        await self.bot.say(embed=result)

    @commands.command()
    @perms.is_dev()
    async def avatar(self, image: str):
        """Change the bot's avatar (DEV ONLY)"""
        try:
            with open(image, "rb") as avatar:
                f = avatar.read()
                image_bytes = bytearray(f)
                await self.bot.edit_profile(avatar=image_bytes)
        except Exception as e:
            await self.bot.say("uh it errored or something")

    @commands.command()
    async def github(self):
        """Provide link to the bot's source code"""
        await self.bot.say("https://github.com/ExtraRandom/StellarBot")

    async def process_user(self, user):
        s = self.bot.get_server("442608736864043008")
        if user.startswith("<@!"):
            user = str(s.get_member(str(user).replace("<@!", "").replace(">", "")))
            return user
        elif user.startswith("<@"):
            user = str(s.get_member(str(user).replace("<@!", "").replace(">", "")))
            return user
        else:
            return user


def add_to_file(user, word, emoji):
    data = read_in_file()

    if user in data:
        for i in range(len(data[user])):
            if word in data[user][i]['word']:
                return False
            else:  # word not in data for user
                data[user].append(
                    {
                        "word": "{}".format(word.lower()),
                        "emoji": "{}".format(emoji)
                    })
                break
    else:
        data[user] = \
            {
            "word": "{}".format(word.lower()), "emoji": "{}".format(emoji)
            }

    if write_file(data) == True:
        return True
    else:
        return False


def read_in_file():
    try:
        with open("configs/custom_reacts.json", "r") as f:
            data = json.loads(f.read())
        return data
    except Exception as e:
        print(type(e).__name__)
        return False


def write_file(data):
    try:
        with open("configs/custom_reacts.json", "w") as f:
            json.dump(data, f, indent=4)
            return True
    except Exception as e:
        print(type(e).__name__)
        return False


def setup(bot):
    bot.add_cog(General(bot))




