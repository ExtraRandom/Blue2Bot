from discord.ext import commands
from cogs.utils import perms, IO
from cogs.utils.logger import Logger
import os


class Owner:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @perms.is_dev()
    async def shutdown(self, ctx):
        """Shutdown the bot"""
        print("Shutting Down")
        await ctx.send("Shutting down...")
        await self.bot.logout()

    # TODO update to work with 3.7

    """
    @commands.command(hidden=True)
    @perms.is_dev()
    async def avatar(self, ctx, image: str):
        ""Change the bot's avatar""
        try:
            with open(os.path.join(self.bot.base_directory, image), "rb") as avatar:
                f = avatar.read()
                image_bytes = bytearray(f)
                await self.bot.edit(avatar=image_bytes)
        except Exception as e:
            Logger.write(e)
            await ctx.send("Failed to change avatar")
    """

    @commands.command()
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


def setup(bot):
    bot.add_cog(Owner(bot))
