import discord
from discord.ext import commands
import time


class Calculation:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["temp"])
    async def temperature(self, degrees: float):
        """Convert between Celsius and Fahrenheit"""
        to_fahrenheit = (degrees * 1.8) + 32
        to_celsius = (degrees - 32) / 1.8

        await self.bot.say("{0}°C Celsius to Fahrenheit: {1:.2f}°F\n"
                           "{0}°F Fahrenheit to Celsius: {2:.2f}°C"
                           "".format(degrees, to_fahrenheit, to_celsius))

    @commands.command()
    async def dltime(self, size_in_gigabytes: float):
        """See how long it'll take to download a given file size (in GB's)

        500 MegaBytes (MB) = 0.5 GigaBytes (GB)
        """
        speeds = {'1MB/s': 8, '2MB/s': 16, '3MB/s': 24, '4MB/s': 32}
        order = ['1MB/s', '2MB/s', '3MB/s', '4MB/s']

        embed = discord.Embed(title="Download Times for {} GigaBytes (GB)".format(size_in_gigabytes),
                              colour=discord.Colour.dark_green(),
                              description="Actual times taken will vary. Speeds are in MegaBytes per second")
        for i in order:
            if i in speeds:
                value = (((1048576 * size_in_gigabytes) * 1024) * 8) / (speeds[i] * 1000000)
                if 3599 < value < 7199:
                    fmt_value = time.strftime('%H hour, %M minutes', time.gmtime(value))
                elif 7199 < value < 86399:
                    fmt_value = time.strftime('%H hours, %M minutes', time.gmtime(value))
                elif 86399 < value:
                    fmt_value = time.strftime('{} Day(s), %H hours, %M minutes'.format(secs_to_days(value)),
                                              time.gmtime(value))
                    embed.set_footer(text="What on earth are you downloading?")
                else:
                    fmt_value = time.strftime('%M minutes', time.gmtime(value))

                embed.add_field(name="{}".format(i),
                                value="{}".format(fmt_value))

        await self.bot.say(embed=embed)


def secs_to_days(seconds):
    return str(seconds / 86400).split(".")[0]


def setup(bot):
    bot.add_cog(Calculation(bot))


