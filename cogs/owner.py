from discord.ext import commands
from cogs.utils import perms, IO
import os


class Owner:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @perms.is_dev()
    async def load(self, *, cog: str):
        """Load a cog"""
        cog_list = []
        c_dir = os.path.dirname(os.path.realpath(__file__))
        for c_file in os.listdir(os.path.join(c_dir, "cogs")):
            if c_file.endswith(".py"):
                cog_list.append("cogs.{}".format(c_file.replace(".py", "")))

        l_cog_name = "cogs.{}".format(cog)  # print(cog, cog_name, cog_list)

        if l_cog_name in cog_list:
            try:
                self.bot.load_extension(l_cog_name)
                await self.bot.say("Successfully loaded cog '{}'.".format(cog))
            except Exception as e:
                await self.bot.say("Failed to load cog '{}'. Reason: {}".format(cog, type(e).__name__))
                return
        else:
            await self.bot.say("No cog called '{}'.".format(cog))
            return

        data = IO.read_settings_as_json()
        if data is None:
            await self.bot.say(IO.settings_fail_read)
            return

        data['cogs'][cog] = True

        if IO.write_settings(data) is False:
            await self.bot.say(IO.settings_fail_write)
            return

    @commands.command(hidden=True)
    @perms.is_dev()
    async def unload(self, *, cog: str):
        """Unload a cog"""
        ext_list = self.bot.extensions
        cog_list = []
        for cogs in ext_list:
            cog_list.append(cogs)

        l_cog_name = "cogs.{}".format(cog)  # print(cog, cog_name, cog_list)

        if l_cog_name in cog_list:
            try:
                self.bot.unload_extension(l_cog_name)
                await self.bot.say("Successfully unloaded cog '{}'.".format(cog))
            except Exception as e:
                await self.bot.say("Failed to unload cog '{}'. Reason: {}".format(cog, type(e).__name__))
                return
        else:
            await self.bot.say("No (loaded) cog called '{}'.".format(cog))
            return

        data = IO.read_settings_as_json()
        if data is None:
            await self.bot.say(IO.settings_fail_read)
            return
        data['cogs'][cog] = False
        if IO.write_settings(data) is False:
            await self.bot.say(IO.settings_fail_write)
            return

    @commands.command(hidden=True)
    @perms.is_dev()
    async def shutdown(self):
        """Should be pretty obvious what this does"""
        print("shutdown")
        await self.bot.say("Shutting down...")
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Owner(bot))
