from discord.ext import commands
from cogs.utils.logger import Logger
import discord
import time


class Calculation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["temp"])
    async def temperature(self, ctx, degrees: float):
        """Convert between Celsius and Fahrenheit
        Input degrees should be a number."""
        to_fahrenheit = (degrees * 1.8) + 32
        to_celsius = (degrees - 32) / 1.8

        await ctx.send("{0}°C Celsius to Fahrenheit: {1:.2f}°F\n"
                       "{0}°F Fahrenheit to Celsius: {2:.2f}°C"
                       "".format(degrees, to_fahrenheit, to_celsius))

    @commands.command()
    async def dltime(self, ctx, size_in_gigabytes: float, download_speed_megabytes_per_second: float = 0):
        """Calculate time to download given file size (in GB's)

        Argument size_in_gigabytes should be the download size in gigabytes.
        For reference, 500 MegaBytes is 0.5 Gigabytes.

        OPTIONAL Argument download_speed_megabytes_per_second should be the speed in MegaBytes per second.
        If you only have access to your speed in MegaBits per second, take the speed and divide it by 8 to get MegaBytes per second.
        """
        if size_in_gigabytes >= 1000000:
            await ctx.send("{} GigaBytes?! You'll be dead before that finishes downloading!".format(size_in_gigabytes))
            return

        if download_speed_megabytes_per_second == 0:
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
                                  description="Actual times taken may vary. Speeds are in MegaBytes per second")
            for i in order:
                if i in speeds:
                    value = (((1048576 * size_in_gigabytes) * 1024) * 8) / (speeds[i] * 1000000)

                    try:
                        if 60 > value:
                            fmt_value = "{} Seconds".format(round(value))
                        elif 3599 < value < 7199:
                            fmt_value = time.strftime('%H hour, %M minutes', time.gmtime(value))
                        elif 7199 < value < 86399:
                            fmt_value = time.strftime('%H hours, %M minutes', time.gmtime(value))
                        elif 86399 < value:
                            fmt_value = time.strftime('{} Day(s), %H hours, %M minutes'.format(secs_to_days(value)),
                                                      time.gmtime(value))
                            if embed.footer is discord.Embed.Empty:
                                embed.set_footer(text="Now that's a lot of data")
                        elif value >= 31536000:
                            fmt_value = time.strftime('{} Year(s), {} Day(s), %H hours, %M minutes'.format(
                                secs_to_years(value), secs_to_days(value)), time.gmtime(value))
                            embed.set_footer(text="Yeah it's gonna take a while")
                        else:
                            fmt_value = time.strftime('%M minutes', time.gmtime(value))

                        embed.add_field(name="{}".format(i),
                                        value="{}".format(fmt_value))

                    except Exception as e:
                        Logger.write(e)
                        await ctx.send("An error occurred whilst calculating.")
                        return

            await ctx.send(embed=embed)

        else:
            speed = download_speed_megabytes_per_second * 8
            value = (((1048576 * size_in_gigabytes) * 1024) * 8) / (speed * 1000000)

            if 60 > value:
                fmt_value = "{} Seconds".format(round(value))
            elif 3599 < value < 7199:
                fmt_value = time.strftime('%H hour, %M minutes', time.gmtime(value))
            elif 7199 < value < 86399:
                fmt_value = time.strftime('%H hours, %M minutes', time.gmtime(value))
            elif 86399 < value:
                fmt_value = time.strftime('{} Day(s), %H hours, %M minutes'.format(secs_to_days(value)),
                                          time.gmtime(value))
            elif value >= 31536000:
                fmt_value = time.strftime('{} Year(s), {} Day(s), %H hours, %M minutes'.format(
                    secs_to_years(value), secs_to_days(value)), time.gmtime(value))
            else:
                fmt_value = time.strftime('%M minutes', time.gmtime(value))

            embed = discord.Embed(title="Download Time for {} GigaBytes (GB)".format(size_in_gigabytes),
                                  colour=discord.Colour.dark_green(),
                                  description="Actual times taken may vary. Speed is MegaBytes per second")

            embed.add_field(name="{} MB/s".format(download_speed_megabytes_per_second),
                            value="{}".format(fmt_value))

            await ctx.send(embed=embed)


def secs_to_days(seconds):
    return round(seconds / 86400)


def secs_to_years(seconds):
    return round(seconds / 31536000)


def setup(bot):
    bot.add_cog(Calculation(bot))


