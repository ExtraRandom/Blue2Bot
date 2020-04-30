from discord.ext import commands
from datetime import datetime
import json
import os
import discord


class AnimalCrossing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wip_warning = "Work-in-Progress! Some details might be incorrect or missing!"
        self.folder = os.path.join(self.bot.base_directory, "cogs", "data", "animal_crossing")

    @commands.command()
    async def villager(self, ctx, search_name: str):
        """Get details on a specific AC:NH villager

        Search name can be a partial or full name. For example 'Sha' and 'Shari' will both return details about Shari.
        If multiple villagers names start with the search name given, only the first result will be shown."""
        filepath = os.path.join(self.folder, "villagers.json")
        with open(filepath, "r") as f:
            r_data = f.read()
            data = json.loads(r_data)

        match = None
        match_count = 0

        for npc in data:
            name = npc['name']
            if str(name).lower().startswith(search_name.lower()):
                match = npc
                match_count += 1

        if match is not None:
            name = match['name']
            personality = match['personality']
            catchphrase = match['catchPhrase']
            birthday = match['birthday']
            species = match['species']
            image = match['imageLink']

            embed = discord.Embed(title="{}".format(name))
            embed.set_thumbnail(url=image)
            embed.add_field(name="Personality", value=personality, inline=True)
            embed.add_field(name="Species", value=species, inline=True)
            embed.add_field(name="Birthday", value=birthday, inline=True)
            embed.add_field(name="Catchphrase", value=catchphrase, inline=True)

            if match_count >= 3:
                embed.set_footer(text="Wrong Villager? Search again with more letters or a full name.")

            await ctx.send(embed=embed)
            return

        await ctx.send(embed=discord.Embed(title="No Villager called '{}' found".format(search_name)))

    @commands.command()
    async def fish(self, ctx):
        """List currently spawning Fish"""
        data = self.search_critters("fish")
        if type(data) is list:
            for item in data:
                item.set_footer(text=self.wip_warning)
                await ctx.send(embed=item)
        else:
            data.set_footer(text=self.wip_warning)
            await ctx.send(embed=data)

    @commands.command()
    async def bugs(self, ctx):
        """List currently spawning Bugs"""
        data = self.search_critters("bugs")
        if type(data) is list:
            for item in data:
                item.set_footer(text=self.wip_warning)
                await ctx.send(embed=item)
        else:
            data.set_footer(text=self.wip_warning)
            await ctx.send(embed=data)

    # https://github.com/sungyeonu/animal-crossing-scraper/blob/master/scrapy.py

    def search_critters(self, search_type="fish"):
        if search_type == "fish":
            filepath = os.path.join(self.folder, "fish.json")
        elif search_type == "bugs":
            filepath = os.path.join(self.folder, "bugs.json")
        else:
            return discord.Embed(title="{} is not a valid critters search type".format(search_type))

        with open(filepath, "r") as f:
            r_data = f.read()
            data = json.loads(r_data)

        now_date = datetime.now()
        now_month = now_date.strftime("%b").lower()
        now_hour = int(now_date.strftime("%H"))
        field_count = 0
        embed_list = []

        # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        # print(now_hour)          # print(now_month)

        # TODO fix as it cuts off some fish as the field limit is 25 

        msg = discord.Embed(title="Currently Spawning {}".format(search_type.capitalize()))

        for item in data:
            if field_count >= 21:
                field_count = 0
                embed_list.append(msg)
                msg = discord.Embed(title="Currently Spawning {}".format(search_type.capitalize()))

            if item[now_month] is True:
                name = item['name']  # print(name)
                where = item['location']
                add = False
                when = None

                time = item['time']
                if time == "All day":
                    start, end = 0, 24
                else:
                    start, end = self.time_sort(time)  # print(start, end)

                if start == 0 and end == 24:
                    add = True
                    when = "All Day"

                elif end < start:
                    if now_hour >= start or now_hour < end:
                        add = True
                        when = time  # print("yes", item['name'], start, end)
                else:  # start > end
                    if start <= now_hour < end:
                        add = True
                        when = time  # print("yes", item['name'], start, end)

                if add is True:
                    field_count += 1  # print(name, "added")
                    msg.add_field(name="{}".format(name), value="Where: {}\n"
                                                                "When: {}"
                                                                "".format(where, when))
        if len(embed_list) is 0:
            return msg
        else:
            embed_list.append(msg)
            return embed_list

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


