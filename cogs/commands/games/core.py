import os

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands


class Games(commands.GroupCog, name="games"):

    # 將 Numpy 陣列直接轉乘 discord.File()，這方法真他媽神
    # https://stackoverflow.com/questions/59868527/how-can-i-upload-a-pil-image-object-to-a-discord-chat-without-saving-the-image
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.game = None
        self.playing = False

    @app_commands.command(name="create", description="Create a game")
    @app_commands.describe(game="Game")
    @app_commands.choices(game=[
        Choice(name="Connect Four", value="Connect Four"),
    ])
    async def _create(self, interaction: discord.Interaction, game: str):
        await interaction.response.defer()

        if game == "Connect Four":
            from .connect4.interact import GameEmbed

            self.game = GameEmbed(interaction.user)

            embed, file, view = self.game.create()
            self.game.ctx = await interaction.followup.send(embed=embed, file=file, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Games(bot), guild=discord.Object(id=os.environ['SERVER_ID']))
