from discord.ext import commands
from GameStoresAPI.steam import Steam
from GameStoresAPI.itad_rw import Itad
from GameStoresAPI.playstation import Playstation
from GameStoresAPI.origin import Origin
from cogs.utils import IO
from cogs.utils.logger import Logger
from mcstatus import MinecraftServer
from re import sub
import discord
import traceback


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fetching = "Retrieving data... please wait!"

    @commands.command(name="steam")
    async def steam_search(self, ctx, *, search_term: str):
        """Search for games on Steam"""
        msg = await ctx.send(self.fetching)

        results = Steam.search_by_name(Steam.format_search(search_term))
        if results == "Error":
            await msg.edit("An error occured whilst getting results. Try again later")
            return

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
        """Search ITAD.com for games"""
        msg = await ctx.send(self.fetching)

        term = search_term.lower()
        term = sub(r'[^\w]', ' ', term)
        term = term.strip().replace("   ", " ").replace("  ", " ")

        if len(term) == 0:
            await msg.edit(content="{} cannot be used as a search term.".format(search_term))
            return

        s_data = IO.read_settings_as_json()
        if s_data['keys']['itad-api-key'] is None:
            await msg.edit("ITAD API Key hasn't been set. Go to the settings file to set it now!")
            return
        else:
            api_key = s_data['keys']['itad-api-key']

        data = Itad.find_games(api_key, term)  # print(data)

        embed = discord.Embed(title="'{}' on IsThereAnyDeal.com".format(term),
                              colour=discord.Colour.red())
        embed.set_footer(text="Make sure to check the website for where the key will redeem.")
        count = 0
        for game in data:
            count += 1
            if count == 6:
                break

            price_raw = data[game]['price']
            if price_raw == 0:
                price_formatted = "Free"
            else:
                price_formatted = "£{}".format(round(price_raw, 2))  # print(price_formatted)

                if "." in price_formatted:
                    if len(price_formatted.split(".")[1]) == 1:
                        price_formatted = "{}0".format(price_formatted)

            embed.add_field(name=game,
                            value="Price: {}\n"
                                  "Store: {}\n"
                                  "  URL: {}"
                                  "".format(price_formatted, data[game]['store'], data[game]['url']))
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
        """Search for games on Origin"""
        msg = await ctx.send(self.fetching)
        try:
            data = Origin.search_by_name(search_term)
        except Exception as e:
            Logger.write(traceback.format_exception(type(e), e, e.__traceback__))
            await msg.edit(content="Failed to fetch data from Origin. Check log for more details.")
            return

        url_base = "https://www.origin.com/gbr/en-us/store"

        if data['success'] is False:
            await msg.edit(content="Failed to fetch data from Origin\n"
                                   "Reason: {}".format(data['reason']))
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
                                "URL: {}{}"
                                "".format(item['desc'], item['price'], item['currency'],
                                          item['type'], url_base, item['url_end']))

                count += 1
                if count == limit:
                    break
        else:
            await msg.edit(content="No Results for Origin Search '{}'".format(search_term))
            return

        await msg.edit(embed=embed)

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


