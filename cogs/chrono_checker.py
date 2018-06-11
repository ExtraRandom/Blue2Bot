import asyncio
import json
import requests
import discord
from datetime import datetime
from cogs.utils import IO
from cogs.utils.logger import Logger


class Main:
    def __init__(self, bot):
        self.bot = bot
        self.bg_task = self.bot.loop.create_task(self.chorno_gg())
        data = IO.read_settings_as_json()
        if data is not None:
            lds = data['info']['chrono-last-check']
            if lds is None:
                self.last_date_sent = datetime(2000, 1, 1)
            else:
                self.last_date_sent = datetime.strptime(lds, "%Y-%m-%d %H:%M:%S")
        else:
            self.last_date_sent = datetime(2000, 1, 1)

    async def chorno_gg(self):
        def get_id_from_channel_name(bot, c_name):
            chans = []
            servers = bot.servers
            for server in servers:
                channels = server.channels
                for channel in channels:
                    if channel.name == c_name:
                        chans.append(channel)
            return chans

        await asyncio.sleep(5)

        store_link = "https://www.chrono.gg/"
        channel_ids = get_id_from_channel_name(self.bot, "deals")

        while True:
            today = datetime.utcnow()

            if today.hour >= 16 and today.minute >= 20:
                if self.last_date_sent != datetime(today.year, today.month, today.day, 10, 00, 00, 00):
                    name, discount, sale_price, normal_price, image, start_date, end_date, \
                        steam_link = await fetch_chrono_data()

                    if name != "Error":
                        self.last_date_sent = datetime(today.year, today.month, today.day, 10, 00, 00, 00)
                        data = IO.read_settings_as_json()
                        if data is not None:
                            data['info']['chrono-last-check'] = str(self.last_date_sent)
                            if IO.write_settings(data) is False:
                                Logger.write(IO.settings_fail_write)
                        else:
                            Logger.write(IO.settings_fail_read)

                        end_time = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%fZ")

                        embed = discord.Embed(title="Chrono.gg Deal",
                                              colour=discord.Colour.dark_green(),
                                              description="Deal Ends at {} UTC".format(end_time))

                        embed.set_thumbnail(url=image)
                        embed.add_field(name="Game: {}".format(name),
                                        value="Sale Price: ${} ~~${}~~\n"
                                              "Discount: {}"
                                              "".format(sale_price, normal_price, discount))
                        embed.add_field(name="Links",
                                        value="{}\n"
                                              "{}".format(store_link, steam_link))

                        for c_id in channel_ids:
                            await self.bot.send_message(c_id, embed=embed)

                        else:
                            pass
                else:
                    pass
            else:
                pass

            await asyncio.sleep(5 * 60)


async def fetch_chrono_data():
    url = "https://api.chrono.gg/sale"
    resp = requests.get(url)
    if resp.status_code == requests.codes.ok:
        data = json.loads(resp.text)
        return data["name"], data["discount"], data["sale_price"], data["normal_price"],\
            data["og_image"], data["start_date"], data["end_date"], data["steam_url"]
    else:
        return "Error", "2", "3", "4", "5", "6", "7", "8"


def setup(bot):
    bot.add_cog(Main(bot))