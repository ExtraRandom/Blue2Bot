import discord
from discord.ext import commands
from GameStoresAPI.steam import Steam
from GameStoresAPI.itad import Itad
from GameStoresAPI.playstation import Playstation
from cogs.utils import IO, simplify, fortnite_api as fn_api
from cogs.utils.logger import Logger
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import time


class Games:
    def __init__(self, bot):
        self.bot = bot
        self.fetching = "Retrieving data... please wait!"

    @commands.command(name="steam")
    async def steam_search(self, ctx, *, search_term: str):
        """Search for games on steam"""
        msg = await ctx.send(self.fetching)

        results = Steam.search_by_name(Steam.format_search(search_term))
        if results == "Error":
            await msg.edit("An error occured whilst getting results. Try again later")

        len_res = len(results)

        embed = discord.Embed(title="'{}' on Steam".format(search_term),
                              colour=discord.Colour.blue())

        if results[0]['results'] is False:
            embed.add_field(name="Search",
                            value="No games found using term '{}'".format(search_term))
            await msg.edit(embed=embed)
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

            if results[i]['discount'] != "None":
                price = "{}\nCurrent Discount: {}".format(price, results[i]['discount'])

            embed.add_field(name="{}".format(results[i]['title']),
                            value="Release: {}\n"
                                  "Price: {}\n"
                                  "URL: {}"
                                  "".format(results[i]['release_date'], price, steam_link))

        await msg.edit(embed=embed)

    @commands.command()
    async def itad(self, ctx, *, search_term: str):
        """Search for games on ITAD.com using Steam App ID's"""
        msg = await ctx.send(self.fetching)

        results = Steam.search_by_name(Steam.format_search(search_term))
        len_res = len(results)

        embed = discord.Embed(title="'{}' on IsThereAnyDeal.com".format(search_term),
                              colour=discord.Colour.red())

        if results[0]['results'] is False:
            embed.add_field(name="Search",
                            value="No games found using term '{}'".format(search_term))
            await msg.edit(embed=embed)
            return

        g_counter = 0
        app_id_list = []
        titles = []

        for i in range(1, len_res):
            g_counter += 1
            if g_counter >= 4:
                break
            steam_url = results[i]['store_url']
            steam_url_split = steam_url.split("/")
            app_id = steam_url_split[3] + "/" + steam_url_split[4]
            app_id_list.append(app_id)

            titles.append(results[i]["title"])

        s_data = IO.read_settings_as_json()
        if s_data is None:
            await msg.edit(IO.settings_fail_read)
            return

        if s_data['keys']['itad-api-key'] is None:
            await msg.edit("ITAD API Key hasn't been set. Go to the settings file to set it now!")
            return
        else:
            api_key = s_data['keys']['itad-api-key']

        plains = Itad.get_multiple_plains_from_steam_appids(api_key, app_id_list)

        titles_plains = []
        for k in range(len(titles)):
            titles_plains.append(
                {
                    "title": titles[k],
                    "plain": plains[k]
                }
            )

        current_best = Itad.get_multiple_current_best_price(api_key, plains)
        historical_best = Itad.get_multiple_historical_best_price(api_key, plains)

        for game in titles_plains:

            c_plain = game["plain"]
            title = game["title"]

            try:
                cb_price = current_best[c_plain]["price"]
                cb_url = current_best[c_plain]["url"]
                cb_store = current_best[c_plain]["store"]

                hb_price = historical_best[c_plain]["price"]
                hb_date = historical_best[c_plain]["date"]
                hb_store = historical_best[c_plain]["store"]

                embed.add_field(name="{}".format(title),
                                value="**Current Best Price**\n"
                                      "Price: £{}\n"
                                      "Shop: {}\n"
                                      "URL: {}\n"
                                      "**Historical Best Price**\n"
                                      "Price: £{}\n"
                                      "Shop: {}\n"
                                      "When: {}"
                                      "".format(cb_price, cb_store, cb_url, hb_price, hb_store, hb_date))

            except Exception as e:
                Logger.write(e)

        await msg.edit(embed=embed)

    @commands.command()
    async def ps4(self, ctx, *, search_term: str):
        """Search for PS4 games on the UK Playstation Store"""
        msg = await ctx.send(self.fetching)

        try:
            await msg.edit(embed=playstation_search("PS4", search_term))

        except Exception as e:
            Logger.write(e)
            await msg.edit("PS4 Game Search Failed")

    @commands.command()
    async def ps3(self, ctx, *, search_term: str):
        """Search for PS3 games on the UK Playstation Store"""
        msg = await ctx.send(self.fetching)

        try:
            await msg.edit(embed=playstation_search("PS3", search_term))

        except Exception as e:
            Logger.write(e)
            await msg.edit("PS3 Game Search Failed")

    @commands.group(aliases=["fn"])
    async def fortnite(self, ctx):
        """Use '?help fortnite' to see subcommands"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use '?help fortnite' to see subcommands")

    @fortnite.command(aliases=["c", "challenge", "chal"])
    async def challenges(self, ctx):
        """Get this weeks battle pass challenges"""
        data, cached = fn_api.get_challenges()

        if data is None:
            await ctx.send("Couldn't reach Fortnite API")
            return

        current_week = data["currentweek"]
        season = data["season"]
        star_img = data["star"]
        cw = "week{}".format(current_week)
        raw_challenges = data["challenges"][cw]

        embed = discord.Embed(title="Fortnite Challenges",
                              description="Season {}, Week {}".format(season, current_week),
                              colour=discord.Colour.blue())
        embed.set_thumbnail(url=star_img)
        if cached is True:
            embed.set_footer(text="This is cached data")

        for challenge in raw_challenges:
            desc = challenge["challenge"]
            todo = challenge["total"]
            reward = challenge["stars"]
            difficulty = challenge["difficulty"]

            if difficulty == "hard":
                f_desc = "{} (Hard)".format(desc)
            else:
                f_desc = desc

            embed.add_field(name="{}".format(f_desc),
                            value="Required Amount: {}\n"
                                  "Reward: {} stars"
                                  "".format(todo, reward))

        await ctx.send(embed=embed)

    @fortnite.command(aliases=["s", "shop", "i", "items", "item"])
    async def store(self, ctx):
        """Get the current item shop"""

        data = fn_api.get_store()

        if data is None:
            await ctx.send("Couldn't reach Fortnite API")

        fetch_msg = await ctx.send("Fetching Fortnite Store Data from API")

        num_of_items = len(data[0]['items'])

        base_w = 512
        base_h = 512

        current_w = 0
        current_h = 0

        full_rows, left_over = divmod(num_of_items, 5)
        rows = full_rows + 1

        calc_h = base_h * rows
        calc_w = base_w * 5

        STORE_IMAGE = Image.new("RGBA", (calc_w, calc_h), (255, 0, 0, 0))

        vbucks_folder = os.path.join(self.bot.base_directory, 'cogs', 'data', 'images', 'fortnite')

        for item in data[0]['items']:
            img_url = item['item']['images']['background']
            cost = item['cost']

            res = requests.get(img_url)
            ITEM_IMAGE = Image.open(BytesIO(res.content)).convert("RGBA")

            if int(cost) == 2000:
                COST_IMAGE = Image.open(os.path.join(vbucks_folder, "2000vbucks.png"))
            elif int(cost) == 1500:
                COST_IMAGE = Image.open(os.path.join(vbucks_folder, "1500vbucks.png"))
            elif int(cost) == 1200:
                COST_IMAGE = Image.open(os.path.join(vbucks_folder, "1200vbucks.png"))
            elif int(cost) == 800:
                COST_IMAGE = Image.open(os.path.join(vbucks_folder, "800vbucks.png"))
            elif int(cost) == 500:
                COST_IMAGE = Image.open(os.path.join(vbucks_folder, "500vbucks.png"))
            elif int(cost) == 200:
                COST_IMAGE = Image.open(os.path.join(vbucks_folder, "200vbucks.png"))
            else:
                COST_IMAGE = Image.open(os.path.join(vbucks_folder, "unknownvbucks.png"))

            ITEM_IMAGE.paste(COST_IMAGE, COST_IMAGE)
            STORE_IMAGE.paste(ITEM_IMAGE, (current_w, current_h), ITEM_IMAGE)

            current_w = current_w + 512
            if current_w >= calc_w:
                current_w = 0
                current_h = current_h + 512

        final_img = os.path.join(vbucks_folder, "STORE.png")
        STORE_IMAGE.save(final_img)
        img_file = discord.File(final_img)

        await ctx.send(file=img_file)
        await fetch_msg.delete()

    @fortnite.command()
    async def upcoming(self, ctx):
        """Get known upcoming items"""
        data = fn_api.get_upcoming()

        if data is None:
            await ctx.send("Couldn't reach Fortnite API")

        fetch_msg = await ctx.send("Fetching Fortnite Upcoming Items Data from API")

        num_of_items = len(data[0]['items'])

        base_w = 512
        base_h = 512

        current_w = 0
        current_h = 0

        full_rows, left_over = divmod(num_of_items, 5)
        rows = full_rows + 1

        calc_h = base_h * rows
        calc_w = base_w * 5

        UPCOMING_IMAGE = Image.new("RGBA", (calc_w, calc_h), (255, 0, 0, 0))
        final_img_folder = os.path.join(self.bot.base_directory, 'cogs', 'data', 'images', 'fortnite')

        for item in data[0]['items']:
            img_url = item['item']['images']['information']

            res = requests.get(img_url)
            ITEM_IMAGE = Image.open(BytesIO(res.content)).convert("RGBA")

            UPCOMING_IMAGE.paste(ITEM_IMAGE, (current_w, current_h), ITEM_IMAGE)

            current_w = current_w + 512
            if current_w >= calc_w:
                current_w = 0
                current_h = current_h + 512

        final_img = os.path.join(final_img_folder, "UPCOMING.png")
        UPCOMING_IMAGE.save(final_img)
        img_file = discord.File(final_img)

        await ctx.send(file=img_file)
        await fetch_msg.delete()


def playstation_search(platform, term):
    if platform == "PS4":
        s_url = Playstation.format_url(["games", "bundles"], ["ps4"], term)
    elif platform == "PS3":
        s_url = Playstation.format_url(["games", "bundles"], ["ps3"], term)
    else:
        Logger.write("Invalid platform '{}' given to playstation_search function in games.py".format(platform))
        return discord.Embed(title="Error whilst fetching results, Admin please check bot logs",
                             colour=discord.Colour.red())

    url_base = "https://store.playstation.com"

    search_data = Playstation.get_data(s_url)
    if search_data == "Empty":
        return discord.Embed(title="Search found no results",
                             colour=discord.Colour.red(),
                             description="Try checking your spellings and try again.")
    elif search_data == "Error":
        return discord.Embed(title="Error occurred whilst fetching results",
                             colour=discord.Colour.red(),
                             description="Try again later.")

    results = discord.Embed(title="{} PSN Search for '{}'".format(platform, term),
                            colour=discord.Colour.dark_blue(),
                            description="Search results from Playstation Store UK")

    for game in search_data:
        results.add_field(name="{}\n".format(game['title']),
                          value="Price: {}\n"
                                "Link: {}\n"
                                "".format(game['price'], (url_base + game['id'])))

    return results


def setup(bot):
    bot.add_cog(Games(bot))


