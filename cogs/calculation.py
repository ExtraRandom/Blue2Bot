import discord
from discord.ext import commands
import time
from cogs.utils.logger import Logger


class Calculation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["temp"])
    async def temperature(self, ctx, degrees: float):
        """Convert between Celsius and Fahrenheit
        Input degrees should be a number."""
        chan = ctx.message.channel
        to_fahrenheit = (degrees * 1.8) + 32
        to_celsius = (degrees - 32) / 1.8

        await chan.send("{0}°C Celsius to Fahrenheit: {1:.2f}°F\n"
                           "{0}°F Fahrenheit to Celsius: {2:.2f}°C"
                           "".format(degrees, to_fahrenheit, to_celsius))

    @commands.command()
    async def dltime(self, ctx, size_in_gigabytes: float):
        """Calculate time to download given file size (in GB's)
        Input size_in_gigabytes should be a number.
        500 MegaBytes (MB) = 0.5 GigaBytes (GB)
        """

        chan = ctx.message.channel

        if size_in_gigabytes >= 1000000:
            await chan.send("{} GigaBytes?! You'll be dead before that finishes downloading!".format(size_in_gigabytes))
            return

        speeds = {'3MB/s (24Mb/s)': 24,
                  '4MB/s (32Mb/s)': 32,
                  '5MB/s (40Mb/s)': 40,
                  '25MB/s (200Mb/s)': 200,
                  '37.5MB/s (300Mb/s)': 300,
                  '50MB/s (400Mb/s)': 400}

        order = ['3MB/s (24Mb/s)',
                 '4MB/s (32Mb/s)',
                 '5MB/s (40Mb/s)',
                 '25MB/s (200Mb/s)',
                 '37.5MB/s (300Mb/s)',
                 '50MB/s (400Mb/s)']

        embed = discord.Embed(title="Download Times for {} GigaBytes (GB)".format(size_in_gigabytes),
                              colour=discord.Colour.dark_green(),
                              description="Actual times taken will vary. Speeds are in MegaBytes per second")
        for i in order:
            if i in speeds:
                value = (((1048576 * size_in_gigabytes) * 1024) * 8) / (speeds[i] * 1000000)

                try:

                    if 3599 < value < 7199:
                        fmt_value = time.strftime('%H hour, %M minutes', time.gmtime(value))
                    elif 7199 < value < 86399:
                        fmt_value = time.strftime('%H hours, %M minutes', time.gmtime(value))
                    elif value >= 31536000:
                        fmt_value = time.strftime('{} Year(s), {} Day(s), %H hours, %M minutes'.format(
                            secs_to_years(value), secs_to_days(value)), time.gmtime(value))
                        embed.set_footer(text="Yeah it's gonna take a while")
                    elif 86399 < value:
                        fmt_value = time.strftime('{} Day(s), %H hours, %M minutes'.format(secs_to_days(value)),
                                                  time.gmtime(value))
                        if embed.footer is discord.Embed.Empty:
                            embed.set_footer(text="Now that's a lotta data")
                    elif 60 > value:
                        fmt_value = "{} Seconds".format(round(value))
                    else:
                        fmt_value = time.strftime('%M minutes', time.gmtime(value))

                    embed.add_field(name="{}".format(i),
                                    value="{}".format(fmt_value))

                except Exception as e:
                    Logger.write(e)
                    await chan.send("An error occurred whilst calculating.")
                    return

        await chan.send(embed=embed)


def secs_to_days(seconds):
    return round(seconds / 86400)


def secs_to_years(seconds):
    return round(seconds / 31536000)


def setup(bot):
    bot.add_cog(Calculation(bot))


