import os
import datetime

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands


from language import set_lang, get_lang


class Language(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="language", description="Switch bot language")
    @app_commands.describe(language="Language")
    @app_commands.choices(language=[
        Choice(name="Chinese", value="zh-tw"),
        Choice(name="English", value="en-us"),
    ])
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    async def _language(self, interation: discord.Interaction, language: str):
        set_lang(language)
        msg = get_lang("cmd", "lang")
        await interation.response.send_message(msg["SWITCH_LANG"] % language)

    @_language.error
    async def _language_error(self, interaction : discord.Interaction, error: app_commands.AppCommandError):
        msg = get_lang("cmd", "lang")
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(msg["ERROR_PERMISSION"], ephemeral=True)
        elif isinstance(error, app_commands.CommandOnCooldown):
            remain = str(datetime.timedelta(seconds=int(error.retry_after)))
            await interaction.response.send_message(msg["ERROR_COOLDOWN"] % remain, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Language(bot), guild=discord.Object(id=os.environ['SERVER_ID']))
