from discord.ext import commands
import discord
from cogs.utils import perms, IO
from datetime import datetime, timedelta
import os


class Dev:
    def __init__(self, bot):
        self.bot = bot

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
        """Link to the bot's source code"""
        await self.bot.say("https://github.com/ExtraRandom/Blue2Bot")

    @commands.command(aliases=["version", "update"])
    async def changelog(self):
        """See what was changed in the last few updates"""
        if not os.path.isdir(os.path.join(self.bot.base_directory, ".git")):
            await self.bot.say("Bot wasn't installed with Git")
            return

        result = os.popen('cd {} &&'
                          'git show -s -n 3 HEAD --format="%cr|%s|%H"'.format(self.bot.base_directory)).read()

        cl = discord.Embed(title="Bot Changelog")

        lines = result.split("\n")

        for line in lines:
            if line is not "":
                time_ago, changed, c_hash = str(line).split("|")
                cl.add_field(name="Changes commited {}".format(time_ago),
                             value="{}\n".format(changed.replace(" [", "\n[")))

        await self.bot.say(embed=cl)

    @commands.command(hidden=True)
    @perms.is_dev()
    async def chrono(self):
        """Check when chrono check last occurred"""
        data = IO.read_settings_as_json()
        if data is None:
            await self.bot.say(IO.settings_fail_read)
            return

        lc = data['info']['chrono-true-last-check']
        await self.bot.say("Last Check: {}".format(lc))

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

    # @commands.command()
    # async def err(self):
    #    print(10 / 0)
    #    open(self.bot.base_directory)


def setup(bot):
    bot.add_cog(Dev(bot))






