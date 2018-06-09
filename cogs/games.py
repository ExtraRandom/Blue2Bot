import discord
from discord.ext import commands
from GameStoresAPI.Steam.steam import Steam
from GameStoresAPI.ITAD.itad import Itad
from cogs.utils import IO


class Games:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="steam", pass_context=True)
    async def steam_search(self, ctx):
        """Search for games on steam"""
        msg = await self.bot.say("Retrieving data... please wait!")
        replace_str = "{}steam ".format(self.bot.command_prefix)
        term = str(ctx.message.content).strip().replace(replace_str, "")

        if term == "{}steam".format(self.bot.command_prefix):
            await self.bot.say("Please provide a search term for the Steam Command")
            return

        results = Steam.search_by_name(Steam.format_search(term))
        len_res = len(results)

        embed = discord.Embed(title="'{}' on Steam".format(term),
                              colour=discord.Colour.blue())

        if results[0]['results'] is False:
            embed.add_field(name="Search",
                            value="No games found using term '{}'".format(term))
            await self.bot.edit_message(msg, embed=embed)
            return

        g_counter = 0

        for i in range(1, len_res):
            g_counter += 1
            if g_counter >= 5:
                break
            price = results[i]['price']
            steam_url = results[i]['store_url']
            steam_url_split = str(steam_url).split("/")
            steam_link = steam_url_split[0] + "//" + steam_url_split[1] + "/" + steam_url_split[2] \
                        + "/" + steam_url_split[3] + "/" + steam_url_split[4]

            # app_id = steam_url_split[3] + "/" + steam_url_split[4]

            if results[i]['discount'] != "None":
                price = "{}\nCurrent Discount: {}".format(price, results[i]['discount'])

            embed.add_field(name="{}".format(results[i]['title']),
                            value="Release: {}\n"
                                  "Price: {}\n"
                                  "URL: {}"
                                  "".format(results[i]['release_date'], price, steam_link))

        await self.bot.edit_message(msg, embed=embed)

    @commands.command(pass_context=True)
    async def itad(self, ctx):
        """Search for games on ITAD.com using Steam App ID's"""
        replace_str = "{}itad ".format(self.bot.command_prefix)
        term = str(ctx.message.content).strip().replace(replace_str, "")

        msg = await self.bot.say("Retrieving data... please wait!")

        if term == "{}itad".format(self.bot.command_prefix):
            await self.bot.edit_message(msg, "Please provide a search term for the Steam Command")
            return

        results = Steam.search_by_name(Steam.format_search(term))
        len_res = len(results)

        embed = discord.Embed(title="'{}' on IsThereAnyDeal.com".format(term),
                              colour=discord.Colour.red())

        if results[0]['results'] is False:
            embed.add_field(name="Search",
                            value="No games found using term '{}'".format(term))
            await self.bot.edit_message(msg, embed=embed)
            return

        g_counter = 0
        app_id_list = []
        for i in range(1, len_res):
            g_counter += 1
            if g_counter >= 5:
                break
            steam_url = results[i]['store_url']
            steam_url_split = steam_url.split("/")
            app_id = steam_url_split[3] + "/" + steam_url_split[4]
            app_id_list.append(app_id)

        s_data = IO.read_settings_as_json()
        if s_data is None:
            await self.bot.say(IO.settings_fail_read)
            return

        if s_data['keys']['itad-api-key'] is None:
            await self.bot.say("ITAD API Key hasn't been set. Go to the settings file to set it now!")
            return
        else:
            api_key = s_data['keys']['itad-api-key']

        plains = Itad.get_multiple_plains_from_steam_appids(api_key, app_id_list)

        p_counter = 1
        for plain in plains:
            title = results[p_counter]['title']
            p_counter += 1
            price, shop, url = Itad.get_best_price(api_key, plain)
            embed.add_field(name="{}".format(title),
                            value="Price: £{}\n"
                                  "Shop: {}\n"
                                  "URL: {}"
                                  "".format(price, url, shop))

        await self.bot.edit_message(msg, embed=embed)


def setup(bot):
    bot.add_cog(Games(bot))





