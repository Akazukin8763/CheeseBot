import os

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from .SelectionView import SelectGeneration

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


class Hololive(commands.GroupCog, name="hololive"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="info", description="Hololive talents information")
    async def _info(self, interaction: discord.Interaction):
        embed = discord.Embed(description="Select the talent which you want to know.", color=0x46c4f2)
        embed.set_author(name="Talents Info.", url="https://hololive.hololivepro.com/talents",
                         icon_url="https://yt3.ggpht.com/ytc/AKedOLShj3wK6CEmow693uwoMqS7yj09e3AvtdrIRsXHQw=s176-c-k-c0x00ffffff-no-rj")

        await interaction.response.send_message(embed=embed, view=SelectGeneration(), ephemeral=True)

    @app_commands.command(name="schedule", description="Hololive talents today schedule")
    @app_commands.describe(status="Streaming status")
    @app_commands.choices(status=[
        Choice(name="past", value="past"),
        Choice(name="now", value="now"),
        Choice(name="upcoming", value="upcoming")
    ])
    async def _schedule(self, interation: discord.Interaction, status: str):
        # 在這邊戳 Hololive API，並整理成 HTML 格式，但我們只需要 json 即可
        # https://hololive.hololivepro.com/schedule
        # https://hololive.hololivepro.com/wp-content/themes/hololive/json/list.js?pro_a
        # /7 是只有 Hololive，不填寫則包含 Holostar
        official_url = f"https://schedule.hololive.tv/api/list/7"

        response = requests.get(official_url)
        soup = BeautifulSoup(response.text, "html.parser")

        data = json.loads(soup.text)

        yesterday = data["dateGroupList"][0]
        today = data["dateGroupList"][1]
        tomorrow = data["dateGroupList"][2]

        past = []
        now = []
        upcoming = []
        streams = {"past": past, "now": now, "upcoming": upcoming}

        current_time = datetime.now()

        for stream in today["videoList"]:
            if stream["isLive"]:
                now.append(stream)
            else:
                if datetime.strptime(stream["datetime"], "%Y/%m/%d %H:%M:%S") < current_time:
                    past.append(stream)
                else:
                    upcoming.append(stream)

        embeds = []
        for stream in streams[status]:
            embed = discord.Embed(color=int(os.environ["BOT_COLOR"], 0))
            embed.set_author(name=stream["title"], url=stream["url"], icon_url=stream["talent"]["iconImageUrl"])
            embed.set_thumbnail(url=stream["talent"]["iconImageUrl"])
            embed.set_image(url=stream["thumbnail"])
            embed.set_footer(text=stream["name"])
            embed.timestamp = datetime.strptime(stream["datetime"], "%Y/%m/%d %H:%M:%S")

            embeds.append(embed)

        if len(embeds) == 0:
            await interation.response.send_message("No one streaming yet.", ephemeral=True)
        else:
            await interation.response.send_message(embeds=embeds, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Hololive(bot), guild=discord.Object(id=os.environ['SERVER_ID']))
