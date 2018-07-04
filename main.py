import discord
from discord.ext import commands  # from discord.utils import get
from datetime import datetime
import os
from cogs.utils import IO, simplify
from cogs.utils.logger import Logger


def get_prefix(d_bot, message):
    prefixes = ["?", "="]

    if message.channel.is_private:
        return '?'
    else:
        return commands.when_mentioned_or(*prefixes)(d_bot, message)


class BlueBot(commands.Bot):
    def __init__(self):
        self.base_directory = os.path.dirname(os.path.realpath(__file__))

        super().__init__(command_prefix=get_prefix,
                         description="Bot Developed by @Extra_Random#2564\n"
                                     "Source code: https://github.com/ExtraRandom/Blue2Bot\n"
                                     "Report an Issue: https://github.com/ExtraRandom/Blue2Bot/issues/new",
                         pm_help=False)

    async def on_ready(self):
        login_time = datetime.now()
        data = IO.read_settings_as_json()

        if data is None:
            raise Exception(IO.settings_fail_read)

        data['info']['last-login-time'] = str(login_time)

        if IO.write_settings(data) is False:
            print(IO.settings_fail_write)

        login_msg = "Bot Logged In at {}".format(login_time)
        Logger.log_write("----------------------------------------------------------\n"
                         "{}\n"
                         "".format(login_msg))
        print(login_msg)

        game = discord.Game(name="@Blue2#2113 help")
        await self.change_presence(game=game)

    async def on_message(self, message):
        bot_msg = message.author.bot
        if bot_msg is True:
            return

        if message.content == "are you sure about that":
            await self.send_file(message.channel, 'pictures/memes/aysat.gif')

        await self.process_commands(message)

    async def on_command_error(self, error, ctx):
        channel = ctx.message.channel

        if isinstance(error, commands.MissingRequiredArgument):
            # c_obj = bot.get_command(cmd)
            # print(c_obj.help)
            await self.bot.send_message(channel, "Missing Argument")
        elif isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CheckFailure):
            await self.bot.send_message(channel, "You do not have permission to use that command!")

        else:
            cmd = simplify.remove_prefix_no_command(self, ctx.message)
            cog = self.get_command(cmd).cog_name

            err_msg = "----------------------------------------------------------\n" \
                      "An Error Occurred at {}\n" \
                      "Command: {}\n" \
                      "    Cog: {}\n" \
                      "  Error: {}\n" \
                      "   Args: {}\n" \
                      "----------------------------------------------------------" \
                      "".format(Logger.time_now(), cmd, cog, error.original, error.args)
            Logger.log_write(err_msg)
            await self.send_message(channel, "**Command Errored:**\n "
                                             "{}".format(error))

    @staticmethod
    def get_cogs_in_folder():
        c_dir = os.path.dirname(os.path.realpath(__file__))
        c_list = []
        for file in os.listdir(os.path.join(c_dir, "cogs")):
            if file.endswith(".py"):
                c_list.append(file.replace(".py", ""))
        return c_list

    @staticmethod
    def get_cogs_in_settings():
        c_list = []
        data = IO.read_settings_as_json()
        if data is None:
            return None
        for cog in data['cogs']:
            c_list.append(cog)
        return c_list

    def run(self):
        # if __name__ == '__main__':
        first_time = False
        s_data = {}
        should_write_after_finish = False

        """First time run check"""
        if os.path.isfile(IO.settings_file_path) is False:
            print("First Time Run - Creating Settings JSON")
            first_time = True
            s_data['keys'] = {}
            s_data['keys']['token'] = None
            s_data['keys']['itad-api-key'] = None
            s_data['cogs'] = {}
            s_data['info'] = {}
            s_data['info']['last-login-time'] = None
            s_data['info']['chrono-last-check'] = None
            s_data['info']['chrono-true-last-check'] = None
        else:
            s_data = IO.read_settings_as_json()
            if s_data is None:
                raise Exception(IO.settings_fail_read)

        """Load cogs"""
        folder_cogs = self.get_cogs_in_folder()
        for folder_cog in folder_cogs:
            cog_path = "cogs.{}".format(folder_cog)
            if first_time is True:
                s_data['cogs'][folder_cog] = True
                should_load = True
            else:
                try:
                    should_load = s_data['cogs'][folder_cog]
                except KeyError:
                    print("New Cog '{}'".format(folder_cog))
                    s_data['cogs'][folder_cog] = True
                    should_load = True
                    should_write_after_finish = True

                if should_load is True:
                    try:
                        self.load_extension(cog_path)
                    except Exception as exc:
                        print("Failed to load cog '{}', Reason: {}".format(folder_cog, type(exc).__name__))
                        Logger.write(exc)
                        s_data['cogs'][folder_cog] = False

        """Get token"""
        if first_time is True:
            if IO.write_settings(s_data) is False:
                raise Exception(IO.settings_fail_write)
            token = None
        else:
            token = s_data['keys']['token']

        """Clean up removed cogs from settings"""
        r_cogs = self.get_cogs_in_folder()
        f_cogs = self.get_cogs_in_settings()
        for f_cog in f_cogs:
            if f_cog not in r_cogs:
                print("Cog {} no longer exists, removing settings entry".format(f_cog))
                del s_data['cogs'][f_cog]
                should_write_after_finish = True

        """Write settings to file"""
        if should_write_after_finish is True:
            if IO.write_settings(s_data) is False:
                raise Exception(IO.settings_fail_write)

        if token:
            super().run(token)
            # self.bot.run(token)
        else:
            print("Token is not set! Go to {} and change the token parameter!".format(IO.settings_file_path))


if __name__ == '__main__':
    the_bot = BlueBot()
    the_bot.run()
