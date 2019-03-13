import discord
from discord.ext import commands
from GameStoresAPI.steam import Steam
from GameStoresAPI.itad import Itad
from GameStoresAPI.playstation import Playstation
from GameStoresAPI.origin import Origin
from cogs.utils import IO, fortnite_api as fn_api
from cogs.utils.logger import Logger
from PIL import Image
import requests
from io import BytesIO
import os
from mcstatus import MinecraftServer
from re import sub
import traceback


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
        """Search for games on ITAD.com (Steam Games Only)"""
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
                if cb_price == 0:
                    cb_price = "Free or Unavailable"
                else:
                    cb_price = "£{}".format(cb_price)
                cb_url = current_best[c_plain]["url"]
                cb_store = current_best[c_plain]["store"]

                try:
                    hb_price = historical_best[c_plain]["price"]
                    hb_date = historical_best[c_plain]["date"]
                    hb_store = historical_best[c_plain]["store"]
                    embed.add_field(name="{}".format(title),
                                    value="**Current Best Price**\n"
                                          "Price: {}\n"
                                          "Shop: {}\n"
                                          "URL: {}\n"
                                          "**Historical Best Price**\n"
                                          "Price: £{}\n"
                                          "Shop: {}\n"
                                          "When: {}"
                                          "".format(cb_price, cb_store, cb_url, hb_price, hb_store, hb_date))

                except KeyError:
                    embed.add_field(name="{}".format(title),
                                    value="**Current Best Price**\n"
                                          "Price: {}\n"
                                          "Shop: {}\n"
                                          "URL: {}\n"
                                          "".format(cb_price, cb_store, cb_url))

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

    @commands.command(name="origin")
    async def origin_search(self, ctx, *, search_term: str):
        msg = await ctx.send(self.fetching)
        try:
            data = Origin.search_by_name(search_term)
        except Exception as e:
            Logger.write(traceback.format_exception(type(e), e, e.__traceback__))
            await msg.edit(content="Failed to fetch data from Origin. Check log for more details.")
            return

        url_base = "https://www.origin.com/gbr/en-us/store"

        if data['success'] == False:
            await msg.edit(content="Failed to fetch data from Origin")
            return

        count = 0
        limit = 5

        embed = discord.Embed(title="Origin Search Results for '{}'".format(search_term),
                              colour=discord.Colour.orange())

        if len(data['results']) > 0:
            for item in data['results']:
                embed.add_field(name=item['name'],
                                value="Description: {}\n"
                                      "Price: {} {}\n"
                                      "Type: {}\n"
                                      "".format(item['desc'], item['price'], item['currency'],
                                                item['type']))  # , url_base, item['url_end'])) # "URL: {}{}"
                """

                embed.add_field(name=item['name'],
                                value="Description: {}\n"
                                "Price: {} {}\n"
                                "Type: {}\n"
                                "URL: {}{}"
                                "".format(item['desc'], item['price'], item['currency'],
                                          item['type'], url_base, item['url_end']))
                """

                count += 1
                if count == limit:
                    break
                # print("item name ", item['name'], item['type'], item['price'])
        else:
            await msg.edit(content="No Results for Origin Search '{}'".format(search_term))
            return

        await msg.edit(embed=embed)

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
        if left_over >= 1:
            rows = full_rows + 1
        else:
            rows = full_rows

        calc_h = base_h * rows
        calc_w = base_w * 5

        STORE_IMAGE = Image.new("RGBA", (calc_w, calc_h), (255, 0, 0, 0))

        vbucks_folder = os.path.join(self.bot.base_directory, 'cogs', 'data', 'images', 'fortnite')

        for item in data[0]['items']:
            img_url = item['item']['images']['background']
            cost = item['cost']

            res = requests.get(img_url)
            ITEM_IMAGE = Image.open(BytesIO(res.content)).convert("RGBA")

            cost_img_loc = os.path.join(vbucks_folder, "{}vbucks.png".format(cost))

            if os.path.exists(cost_img_loc):
                COST_IMAGE = Image.open(cost_img_loc)
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

    @fortnite.command(aliases=["u", "upc", "leaked", "l"])
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
        if left_over >= 1:
            rows = full_rows + 1
        else:
            rows = full_rows

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

    @commands.command(name="mc")
    async def minecraft_ip(self, ctx, ip: str):
        """Get Status of Minecraft Servers"""
        # From https://github.com/ExtraRandom/Red-DiscordBot/blob/develop/cogs/games.py
        try:
            server = MinecraftServer.lookup(ip)
            status = server.status()
            data = status.raw  # print(data)
            ver = data['version']['name']
            s_desc = "N/A"
            try:
                s_desc = data['description']['text']
            except TypeError:
                s_desc = data['description']

            desc_filter = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "k", "l",
                           "m", "n", "o", "r"]

            for item in desc_filter:
                s_desc = str(s_desc).replace("§{}".format(item), "")

            s_desc = sub(' +', ' ', s_desc)  # not sure if this is actually needed

            player_count = int(data['players']['online'])
            player_limit = int(data['players']['max'])

            if player_count > 1000:
                try_players = False
            else:
                try_players = True

            players = ""

            if try_players:
                try:
                    for player in data['players']['sample']:
                        players += "{}, ".format(player['name'])
                    players = players[:-2]  # Remove final comma and the space after it
                except Exception:
                    players = "None"
            else:
                players = "N/A"

            embed = discord.Embed(title="Status of {}".format(ip),
                                  colour=discord.Colour.green())

            embed.add_field(name="Info", value="Version Info: {}\n\n"
                                               "Player Count/Limit: **{}**/**{}**\n"
                                               "Player Sample: {}\n\n"
                                               "Description: {}".format(ver, player_count, player_limit, players,
                                                                        s_desc))

            await ctx.send(embed=embed)

        except ValueError as e:
            await ctx.send("Error Occured - Check IP is correct - Value Error")
            # log.warn(e)

        except ConnectionRefusedError as e:
            await ctx.send("Error Occured - Target Refused Connection")
            # log.warn(e)

        except Exception as e:
            await ctx.send("Error Occured - Server didn't respond")
            # log.warn(e)


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

    count = 0
    limit = 5
    for game in search_data:
        count += 1
        if count == limit:
            break
        results.add_field(name="{}\n".format(game['title']),
                          value="Price: {}\n"
                                "Link: {}\n"
                                "".format(game['price'], (url_base + game['id'])))

    return results


def setup(bot):
    bot.add_cog(Games(bot))


