import discord
from discord.ext import commands
from GameStoresAPI.steam import Steam
from GameStoresAPI.itad import Itad
from GameStoresAPI.playstation import Playstation
from cogs.utils import IO, simplify, fortnite_api as fn_api
from cogs.utils.logger import Logger
from datetime import datetime, timedelta


class Games:
    def __init__(self, bot):
        self.bot = bot
        self.fetching = "Retrieving data... please wait!"

    @commands.command(name="steam")
    async def steam_search(self, *, search_term: str):
        """Search for games on steam"""
        msg = await self.bot.say(self.fetching)

        results = Steam.search_by_name(Steam.format_search(search_term))
        if results == "Error":
            await self.bot.edit_message(msg, "An error occured whilst getting results. Try again later")

        len_res = len(results)

        embed = discord.Embed(title="'{}' on Steam".format(search_term),
                              colour=discord.Colour.blue())

        if results[0]['results'] is False:
            embed.add_field(name="Search",
                            value="No games found using term '{}'".format(search_term))
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

            if results[i]['discount'] != "None":
                price = "{}\nCurrent Discount: {}".format(price, results[i]['discount'])

            embed.add_field(name="{}".format(results[i]['title']),
                            value="Release: {}\n"
                                  "Price: {}\n"
                                  "URL: {}"
                                  "".format(results[i]['release_date'], price, steam_link))

        await self.bot.edit_message(msg, embed=embed)

    @commands.command()
    async def itad(self, *, search_term: str):
        """Search for games on ITAD.com using Steam App ID's"""
        msg = await self.bot.say(self.fetching)

        results = Steam.search_by_name(Steam.format_search(search_term))
        len_res = len(results)

        embed = discord.Embed(title="'{}' on IsThereAnyDeal.com".format(search_term),
                              colour=discord.Colour.red())

        if results[0]['results'] is False:
            embed.add_field(name="Search",
                            value="No games found using term '{}'".format(search_term))
            await self.bot.edit_message(msg, embed=embed)
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
            await self.bot.say(IO.settings_fail_read)
            return

        if s_data['keys']['itad-api-key'] is None:
            await self.bot.say("ITAD API Key hasn't been set. Go to the settings file to set it now!")
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

        await self.bot.edit_message(msg, embed=embed)

    @commands.command()
    async def ps4(self, *, search_term: str):
        """Search for PS4 games on the UK Playstation Store"""
        msg = await self.bot.say(self.fetching)

        try:
            await self.bot.edit_message(msg, embed=playstation_search("PS4", search_term))

        except Exception as e:
            Logger.write(e)
            await self.bot.edit_message(msg, "PS4 Game Search Failed")

    @commands.command()
    async def ps3(self, *, search_term: str):
        """Search for PS3 games on the UK Playstation Store"""
        msg = await self.bot.say(self.fetching)

        try:
            await self.bot.edit_message(msg, embed=playstation_search("PS3", search_term))

        except Exception as e:
            Logger.write(e)
            await self.bot.edit_message(msg, "PS3 Game Search Failed")

    @commands.command(aliases=["76", "fallout", "f76", "fo76"])
    async def fallout76(self):
        """Fallout 76 Countdown"""
        rd = datetime(year=2018, month=11, day=14, hour=0, minute=0, second=0, microsecond=0)
        now = datetime.now()
        td = timedelta.total_seconds(rd - now)

        m, s = divmod(td, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        cd_str = ("%d:%02d:%02d:%02d" % (d, h, m, s))
        day, hour, minute, second = cd_str.split(":")

        if int(day) <= -1:
            await self.bot.say("Fallout 76 is out now!")
            return
        elif int(day) == 0:
            if int(hour) >= 1:
                await self.bot.say("It's so close! Fallout 76 releases in {} hours, {} minutes and {} seconds"
                                   "".format(hour, minute, second))
                return
            else:  # hour is 0
                if int(minute) >= 1:
                    await self.bot.say("Only {} minutes and {} seconds until Fallout 76 is released!"
                                       "".format(minute, second))
                    return
                else:
                    await self.bot.say("Wew lad, only {} seconds until Fallout 76 is upon us."
                                       "".format(second))
                    return
        else:
            await self.bot.say("Fallout 76 is {} days, {} hours, {} minutes and {} seconds away from release."
                               "".format(day, hour, minute, second))
            return

    @commands.group(pass_context=True, aliases=["fn"])
    async def fortnite(self, ctx):
        """Use '?help fortnite' to see subcommands"""
        if ctx.invoked_subcommand is None:
            await self.bot.say("Use '?help fortnite' to see subcommands")

    @fortnite.command(aliases=["c", "challenge", "chal"])
    async def challenges(self):
        """Get this weeks battle pass challenges"""
        data, cached = fn_api.get_challenges()

        if data is None:
            await self.bot.say("Couldn't reach Fortnite API")
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

        await self.bot.say(embed=embed)

    @fortnite.command(aliases=["s", "shop", "i", "items", "item"])
    async def store(self):

        data = fn_api.get_store()

        if data is None:
            await self.bot.say("Couldn't reach Fortnite API")
            return

        date = data[0]["date"]

        emb = discord.Embed(title="Fortnite Store - {}".format(date),
                            colour=discord.Colour.dark_blue())
        # emb.set_footer(text="Version of this command with Images coming soon")

        for item in data[0]["items"]:
            name = item['name']
            cost = item['cost']
            img = item['item']['images']['background']
            item_type = str(item['item']['type']).capitalize()
            rarity = str(item['item']['rarity']).capitalize()

            emb.add_field(name="{}".format(name),
                          value="Cost: {}\n"
                                "Type: {}\n"
                                "Rarity: {}\n"
                                "".format(cost, item_type, rarity))

        await self.bot.say(embed=emb)


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


