from discord.ext import commands
import discord
from cogs.utils import perms, IO
from datetime import datetime, timedelta
import os


class Dev:
    def __init__(self, bot):
        self.bot = bot
        self.c_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    @commands.command(hidden=True)
    @perms.is_dev()
    async def cogs(self):
        ext_list = self.bot.extensions
        loaded = []
        unloaded = []
        for cog in ext_list:
            loaded.append(str(cog).replace("cogs.", ""))

        for cog_f in os.listdir(os.path.join(self.c_dir, "cogs")):
            if cog_f.endswith(".py"):
                if cog_f.replace(".py", "") not in loaded:
                    unloaded.append(cog_f.replace(".py", ""))

        await self.bot.say("```diff\n"
                           "+ Loaded Cogs:\n{}\n\n"
                           "- Unloaded Cogs:\n{}"
                           "```"
                           "".format(", ".join(sorted(loaded)),
                                     ", ".join(sorted(unloaded))))

    @commands.command(hidden=True)
    @perms.is_dev()
    async def avatar(self, image: str):
        """Change the bot's avatar (DEV ONLY)"""
        try:
            with open(os.path.join(self.c_dir, image), "rb") as avatar:
                f = avatar.read()
                image_bytes = bytearray(f)
                await self.bot.edit_profile(avatar=image_bytes)
        except Exception as e:
            await self.bot.say("Failed to change avatar")

    @commands.command()
    async def uptime(self):
        """Shows the bots current uptime"""
        try:
            data = IO.read_settings_as_json()
            if data is None:
                await self.bot.say(IO.settings_fail_read)
                return

            login_time = datetime.strptime(data['info']['last-login-time'], "%Y-%m-%d %H:%M:%S.%f")
            now = datetime.now()

            td = timedelta.total_seconds(now - login_time)
            td = int(td)

            m, s = divmod(td, 60)
            h, m = divmod(m, 60)
            uptime = "%d:%02d:%02d" % (h, m, s)

            await self.bot.say("Bot Uptime: {}".format(uptime))

        except Exception as e:
            await self.bot.say("Error getting bot uptime. Reason: {}".format(type(e).__name__))

    @commands.command()
    async def github(self):
        """Provide link to the bot's source code"""
        await self.bot.say("https://github.com/ExtraRandom/StellarBot")

    @commands.command(aliases=["version", "update"])
    async def changelog(self):
        """See what was changed in the last update"""
        if not os.path.isdir(os.path.join(self.c_dir, ".git")):
            await self.bot.say("Bot wasn't installed with Git")
            return

        result = os.popen('cd {} &&'
                          'git show -s -n 1 HEAD --format="%cr|%s|%H"'.format(self.c_dir)).read()

        time_ago, changed, commit = result.split("|")

        cl = discord.Embed(title="Bot Changelog",
                           description="Last Updated: {}".format(time_ago))

        cl.add_field(name="Changes: ",
                     value="{}".format(changed.replace(" [", "\n[")))

        await self.bot.say(embed=cl)

    @commands.command()
    @perms.is_dev()
    async def chrono(self):
        data = IO.read_settings_as_json()
        if data is None:
            await self.bot.say(IO.settings_fail_read)
            return

        lc = data['info']['chrono-true-last-check']
        await self.bot.say("Last Check: {}".format(lc))

    @commands.command(hidden=True)
    @perms.is_server_owner()
    async def welcoming(self):
        """See whether the bot is currently welcoming newcomers"""
        data = IO.read_settings_as_json()
        if data is None:
            await self.bot.say(IO.settings_fail_read)
            return

        current = bool(data['handle-newcomers'])
        if current is True:
            await self.bot.say("Bot is currently handling newcomers even if mods are online.")
            return
        else:
            await self.bot.say("Bot isn't handling newcomers whilst mods are online, "
                               "will still handle newcomers if all mods go offline")
            return

    @commands.command(hidden=True, pass_context=True)
    @perms.is_dev()
    async def test(self, ctx):
        command = "itad"
        c_obj = self.bot.get_command(command)

        print(dir(c_obj))
        print(c_obj.brief)
        print("h", c_obj.help)
        print("d", c_obj.description)
        print("c", c_obj.commands)
        print("cd", c_obj.command)


def setup(bot):
    bot.add_cog(Dev(bot))






