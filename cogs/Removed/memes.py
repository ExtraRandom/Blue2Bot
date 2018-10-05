from discord.ext import commands
# from cogs.utils import perms
import os
from PIL import Image, ImageDraw, ImageFont
# import requests
# from io import BytesIO
from cogs.utils.logger import Logger
from cogs.utils import simplify


class Memes:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="salesman", pass_context=True)
    async def this_bad_boy(self, ctx):
        """*slaps roof of meme generator*
        very likely to break horribly"""

        message = simplify.remove_prefix_in_message(self.bot, ctx.message, "salesman")
        if message is None:
            self.bot.say("You forgot the text you doof...")
            return

        # url = "https://upload.wikimedia.org/wikipedia/en/thumb/9/9b/Command_%26_Conquer_Red_Alert_3_Game_Cover.jpg" \
        #      "/220px-Command_%26_Conquer_Red_Alert_3_Game_Cover.jpg"

        # res = requests.get(url)
        # img = Image.open(BytesIO(res.content))

        in_file = os.path.join(self.bot.base_directory, "pictures", "memes", "thisbadboy.png")
        out_file = os.path.join(self.bot.base_directory, "pictures", "memes", "temp", "sale.png")
        font_path = os.path.join(self.bot.base_directory, "pictures", "fonts")
        font_file = os.path.join(font_path, "Calibri.ttf")

        img = Image.open(in_file).convert('RGBA')

        # w, h = img.size
        # img.crop((100, 100, w - 100, h - 100))

        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_file, 30)
        # draw.text((5, 5), "this is some cheeky test text", font=font, fill=(0, 0, 0, 0))

        # message = text_to_write
        # "*slaps roof of car* now this bad boy is fucking worthless and you should not buy it"
        msg_length = font.getsize(message)
        # print(msg_length)

        msg_w = msg_length[0]
        msg_h = msg_length[1]

        line_count = 1
        lines = []

        # if need to move down move down by 30 pixels

        limit_w = 640

        if msg_w >= limit_w:
            # Message needs to be broken into lines
            words = message.split(" ")
            count = 0
            line = ""
            for word in words:
                # print("count", count, "word", word, "line", line)
                word_length = font.getsize((word + " "))[0]
                # print("after count is going to be", (count + word_length + 1))

                if count + word_length < limit_w:
                    count += word_length + 1
                    line += word + " "
                else:
                    lines.append(line)
                    count = word_length
                    line = word + " "
                    line_count += 1

            lines.append(line)
        else:
            lines.append(message)

        # for l in lines:
        #    print("line sizes", font.getsize(l)[0])
        # print(lines)
        # print(msg_w, msg_h)

        draw_h = 5

        for line in lines:
            draw.text((5, draw_h), line, font=font, fill=(0, 0, 0, 0))
            draw_h += 30

        out = img

        try:
            out.save(out_file)
        except Exception as e:
            Logger.write(e)

        await self.bot.send_file(ctx.message.channel, out_file)


def setup(bot):
    bot.add_cog(Memes(bot))
