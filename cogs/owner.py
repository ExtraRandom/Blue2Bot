import discord, os
from discord.ext import commands
from cogs.utils import perms, IO
from datetime import datetime, timedelta


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @perms.is_dev()
    async def shutdown(self, ctx):
        """Shutdown the bot"""
        print("Shutting Down")
        await ctx.send("Shutting down...")
        await self.bot.logout()

    @commands.command(hidden=True)
    @perms.is_dev()
    async def avatar(self, ctx, image: str):
        """Change the bot's avatar"""
        try:
            with open(os.path.join(self.bot.base_directory, image), "rb") as avatar:
                f = avatar.read()
                image_bytes = bytearray(f)
                await self.bot.user.edit(avatar=image_bytes)
        except Exception as e:
            await ctx.send("Failed to change avatar")
            print(e)

    @commands.command(hidden=True)
    @perms.is_dev()
    async def purge(self, ctx, number: int):
        """Purge given number of messages in the current channel"""
        m_list = []

        if number > 100:
            number = 100

        async for message in ctx.channel.history(limit=number+1):
            m_list.append(message)
        await ctx.channel.delete_messages(m_list)
        await ctx.send("Purged {} messages in {}".format(number, ctx.channel))

    @commands.command()
    async def uptime(self, ctx):
        """Shows the bots current uptime"""
        try:
            data = IO.read_settings_as_json()
            if data is None:
                await ctx.send(IO.settings_fail_read)
                return

            login_time = datetime.strptime(data['info']['last-login-time'], "%Y-%m-%d %H:%M:%S.%f")
            now = datetime.now()

            td = timedelta.total_seconds(now - login_time)
            td = int(td)

            m, s = divmod(td, 60)
            h, m = divmod(m, 60)
            uptime = "%d:%02d:%02d" % (h, m, s)

            await ctx.send("Bot Uptime: {}".format(uptime))

        except Exception as e:
            await ctx.send("Error getting bot uptime. Reason: {}".format(type(e).__name__))

    @commands.command(aliases=["version", "update", "cl"])
    async def changelog(self, ctx):
        """See what was changed in the last few updates"""
        if not os.path.isdir(os.path.join(self.bot.base_directory, ".git")):
            await ctx.send("Bot wasn't installed with Git")
            return

        result = os.popen('cd {} &&'
                          'git show -s -n 3 HEAD --format="%cr|%s|%H"'.format(self.bot.base_directory)).read()

        cl = discord.Embed(title="Bot Changelog")

        lines = result.split("\n")

        for line in lines:
            if line is not "":
                time_ago, changed, c_hash = str(line).split("|")
                cl.add_field(name="Changes committed {}".format(time_ago),
                             value="{}\n".format(changed.replace(" [", "\n[")))

        await ctx.send(embed=cl)


def setup(bot):
    bot.add_cog(Owner(bot))
