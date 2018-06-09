from discord.ext import commands
import discord
from cogs.utils import perms, IO
from datetime import datetime, timedelta
import os


class Dev:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @perms.is_dev()
    async def cogs(self):
        c_dir = os.path.dirname(os.path.realpath(__file__))
        ext_list = self.bot.extensions
        loaded = []
        unloaded = []
        for cog in ext_list:
            loaded.append(str(cog).replace("cogs.", ""))

        for cog_f in os.listdir(c_dir):
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
            with open(image, "rb") as avatar:
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
        if not os.path.isdir(".git"):
            await self.bot.say("Bot wasn't installed with Git")
            return

        result = os.popen('git show -s -n 1 HEAD --format="%cr|%s|%H"').read()

        time_ago, changed, commit = result.split("|")

        cl = discord.Embed(title="Bot Changelog",
                           description="Last Updated: {}".format(time_ago))

        cl.add_field(name="Changes: ",
                     value="{}".format(changed.replace(" [", "\n[")))

        await self.bot.say(embed=cl)

    @commands.command(hidden=True)
    @perms.is_server_owners()
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
        command = "react"
        c_obj = self.bot.get_command(command)

        print(dir(c_obj))
        print(c_obj.brief)
        print("h", c_obj.help)
        print("d", c_obj.description)
        print("c", c_obj.commands)
        print("cd", c_obj.command)

    @commands.command(hidden=True)
    @perms.is_dev()
    async def err(self):
        print(10/0)


def setup(bot):
    bot.add_cog(Dev(bot))






