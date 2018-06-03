from discord.ext import commands
from utils import perms
import os
import json

class Dev:
    def __init__(self, bot):
        self.bot = bot
        # cd = os.path.dirname(os.path.realpath())
        self.filepath = os.path.join("configs", "settings.json")

    @commands.command()
    @perms.is_dev()
    async def uptime(self):
        print("dang it")

    @commands.command(hidden=True)
    @perms.is_dev()
    async def cogs(self):
        ext_list = self.bot.extensions
        cog_list = []
        for cog in ext_list:
            cog_list.append(str(cog).replace("cogs.", ""))
        await self.bot.say("Currently Loaded Cogs: {}".format(", ".join(cog_list)))

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
            await self.bot.say("uh it errored or something")

def setup(bot):
    bot.add_cog(Dev(bot))






