import os

import discord
from discord.ext import commands


class Event(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as <{self.bot.user}>")
        print(f"Server ID is <{self.bot.guilds[0].id}>")

        # online（上線）、offline（下線）、idle（閒置）、dnd（請勿打擾）、invisible（隱身）
        _status = discord.Status.dnd

        # playing（遊玩中）、streaming（直撥中）、listening（聆聽中）、watching（觀看中）、custom（自定義）
        _activity = discord.Activity(type=discord.ActivityType.watching, name="莎曉")

        await self.bot.change_presence(status=_status, activity=_activity)

    # @commands.Cog.listener()
    # async def on_message(self, msg):
    #     # 排除自己的訊息，避免陷入無限循環
    #     if msg.author == self.bot.user:
    #         return
    #
    #     # if message.content.startswith('$thumb'):
    #     #     channel = message.channel
    #     #     await channel.send('Send me that 👍 reaction, mate')
    #     #
    #     #     def check(reaction, user):
    #     #         return user == message.author and str(reaction.emoji) == '👍'
    #     #
    #     #     try:
    #     #         reaction, user = await self.wait_for('reaction_add', timeout=60.0, check=check)
    #     #     except asyncio.TimeoutError:
    #     #         await channel.send('👎')
    #     #     else:
    #     #         await channel.send('👍')
    #
    #     await msg.channel.send(f"{msg.author} - {msg.content}")

    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     if hasattr(ctx.command, "on_error"):
    #         ctx.send(f"{ctx.command} 發生錯誤並已觸發自身的 Error Handler")
    #         return
    #
    #     await ctx.send(error)


async def setup(bot: commands.Bot):
    await bot.add_cog(Event(bot), guild=discord.Object(id=os.environ['SERVER_ID']))
