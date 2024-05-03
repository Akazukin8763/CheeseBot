from dotenv import load_dotenv
import os

import aiohttp
import discord
from discord.ext import commands


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=os.environ['BOT_PREFIX'],
            intents=discord.Intents.all(),
            application_id=os.environ['CLIENT_ID']
        )

        self.initial_extensions = [
            'cogs.event',
            'cogs.commands.language.core',
            'cogs.commands.hololive.core',
            'cogs.commands.games.core'
        ]

    async def setup_hook(self):
        # self.session = aiohttp.ClientSession()

        # 將 Bot 的部件組裝起來
        for ext in self.initial_extensions:
            await self.load_extension(ext)
        await bot.tree.sync(guild=discord.Object(id=os.environ['SERVER_ID']))

    async def close(self):
        await super().close()
        # await self.session.close()

    # from discord import app_commands
    # @self.bot.tree.error
    # async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    #     await interaction.response.send_message(error)


if __name__ == "__main__":
    load_dotenv()

    bot = Bot()
    bot.run(os.environ['BOT_TOKEN'])

    # 有效解決使用 Cog 時造成指令執行複數次的效果，只需在 on_message 中刪除 await self.cogs.process_commands(message)
    # https://stackoverflow.com/questions/65673412/discord-bot-running-commands-twice-discord-py

    # Discord.py 2.0+ 開發者模式，目前尚未打包
    # https://www.youtube.com/watch?v=U0Us5NHG-nY
    # pip install -U git+https://github.com/Rapptz/discord.py

    # Emoji
    # 🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿
