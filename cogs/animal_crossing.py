from discord.ext import commands
from datetime import datetime
import json
import os
import discord


class AnimalCrossing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wip_warning = "Work-in-Progress! Some details might be incorrect or missing!"

    @commands.command()
    async def fish(self, ctx):
        data = self.search_critters("fish")
        data.set_footer(text=self.wip_warning)
        await ctx.send(embed=data)

    @commands.command()
    async def bugs(self, ctx):
        data = self.search_critters("bugs")
        data.set_footer(text=self.wip_warning)
        await ctx.send(embed=data)

    # https://github.com/sungyeonu/animal-crossing-scraper/blob/master/scrapy.py

    def search_critters(self, search_type="fish"):
        if search_type == "fish":
            filepath = os.path.join(self.bot.base_directory, "cogs", "data", "animal_crossing", "fish.json")
        elif search_type == "bugs":
            filepath = os.path.join(self.bot.base_directory, "cogs", "data", "animal_crossing", "bugs.json")
        else:
            return "err"

        # print(filepath)

        with open(filepath, "r") as f:
            r_data = f.read()
            data = json.loads(r_data)

        now_date = datetime.now()
        now_month = now_date.strftime("%b").lower()
        now_hour = int(now_date.strftime("%H"))

        # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        # print(now_hour)
        # print(now_month)

        msg = discord.Embed(title="Currently Spawning {}".format(search_type.capitalize()))

        for item in data:
            if item[now_month] is True:
                name = item['name']
                where = item['location']
                add = False
                when = None

                time = item['time']
                if time == "All day":
                    start, end = 0, 24
                else:
                    start, end = self.time_sort(time)

                if start == 0 and end == 24:
                    add = True
                    when = "All Day"

                elif end < start:
                    if now_hour >= start or now_hour < end:
                        add = True
                        when = time
                        # print("yes", item['name'], start, end)
                else:  # start > end
                    if start <= now_hour < end:
                        add = True
                        when = time
                        # print("yes", item['name'], start, end)

                if add is True:
                    msg.add_field(name="{}".format(name), value="Where: {}\n"
                                                                "When: {}"
                                                                "".format(where, when))
        return msg

    @staticmethod
    def time_sort(time_string):
        t = str(time_string).split(" - ")
        results = []
        for time in t:
            t_split = time.split(" ")
            hour = t_split[0]
            if t_split[1] == "PM":
                hour = int(hour) + 12
            results.append(hour)
        return int(results[0]), int(results[1])




def setup(bot):
    bot.add_cog(AnimalCrossing(bot))


