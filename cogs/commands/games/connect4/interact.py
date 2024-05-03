from datetime import datetime

import discord

from language import lang
from exceptions import GameJoinError, OutOfSlotError
from . import ConnectFour


class GameEmbed:

    def __init__(self, creator: discord.Member, timeout: int = 180):
        self.game = ConnectFour()

        self.ctx = None
        self.creator = creator
        self.time_out = timeout

        # 現有互動式視窗
        self._view = None

        self.game.create()

    @lang("cmd", "game", "connect4")
    def create(self, lang_pack=None):
        # 遊戲圖片
        file = self.game.get_showcase("image.png")

        # 遊戲狀態敘述嵌入
        embed = discord.Embed(title=lang_pack['NAME'], color=0xfadf1c)
        embed.add_field(name=lang_pack['WAIT'], value="...", inline=True)
        embed.add_field(name=lang_pack['STATUS'], value=lang_pack['STATUS_WAIT'] % self.game.maxPlayers, inline=True)
        embed.set_image(url="attachment://image.png")

        # 遊戲互動視窗
        self._set_join_view(timeout=self.time_out)

        return embed, file, self._view

    @lang("cmd", "game", "connect4")
    async def _countdown(self, lang_pack=None):
        # 使用表情符號進行遊戲開始倒數
        # 🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿
        reactions = ['🇬', '🇦', '🇲', '🇪', '🟦', '🇮', '🇳', '➡️']
        countdown = ['5️⃣', '4️⃣', '3️⃣', '2️⃣', '1️⃣', '0️⃣']

        for reaction in reactions:
            await self.ctx.add_reaction(reaction)
        for number in countdown:
            await self.ctx.add_reaction(number)
            await self.ctx.remove_reaction(number, self.ctx.author)
        await self.ctx.clear_reactions()

        # 倒數結束，準備開始遊戲
        embed, file, view = self.start()
        await self.ctx.edit(embed=embed, attachments=[file], view=view)

    @lang("cmd", "game", "connect4")
    def start(self, lang_pack=None):
        self.game.start()

        # 玩家資訊
        current, next = self.game.get_order()

        # 遊戲圖片
        file = self.game.get_showcase("image.png")

        # 遊戲狀態敘述嵌入
        embed = discord.Embed(title=lang_pack['NAME'], color=0xfadf1c)
        embed.add_field(name=lang_pack['CURRENT'] % current.color, value=current.mention, inline=True)
        embed.add_field(name=lang_pack['NEXT'] % next.color, value=next.mention, inline=True)
        embed.set_image(url="attachment://image.png")

        # 遊戲互動視窗
        self._set_play_view(timeout=self.time_out)

        return embed, file, self._view

    @lang("cmd", "game", "connect4")
    def _set_join_view(self, timeout=180, lang_pack=None):
        # 避免已經觸發一般事件，依舊跑入超時事件
        if self._view is not None:
            self._view.stop()

        self._view = discord.ui.View(timeout=timeout)
        self._view.on_timeout = self._callback_on_timeout

        _join = discord.ui.Button(label=lang_pack['JOIN'], style=discord.ButtonStyle.primary, emoji="🚸")
        _join.callback = self._callback_join

        _abort = discord.ui.Button(label=lang_pack['ABORT'], style=discord.ButtonStyle.danger, emoji="❌")
        _abort.callback = self._callback_abort

        self._view.add_item(_join)
        self._view.add_item(_abort)

    @lang("cmd", "game", "connect4")
    def _set_play_view(self, timeout=180, lang_pack=None):
        # 避免已經觸發一般事件，依舊跑入超時事件
        if self._view is not None:
            self._view.stop()

        self._view = discord.ui.View(timeout=timeout)
        self._view.on_timeout = self._callback_on_timeout

        for i in self.game.remainSlot:
            _slot = discord.ui.Button(label=f"{i + 1}", style=discord.ButtonStyle.primary)
            _slot.callback = self._callback_choose(i)

            self._view.add_item(_slot)

    @lang("cmd", "game", "connect4")
    def _clear_view(self, lang_pack=None):
        # 避免已經觸發一般事件，依舊跑入超時事件
        if self._view is not None:
            self._view.stop()
        self._view = None

    @lang("cmd", "game", "connect4")
    async def _callback_on_timeout(self, lang_pack=None):
        embed = discord.Embed(title=lang_pack['NAME'], color=0xfadf1c)
        embed.add_field(name=lang_pack['TIMEOUT'],
                        value=datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

        self._clear_view()
        await self.ctx.edit(embed=embed, attachments=[], view=self._view)

    @lang("cmd", "game", "connect4")
    async def _callback_join(self, interaction: discord.Interaction, lang_pack=None):
        # 避免出現交互失敗
        await interaction.response.defer()

        try:
            self.game.join(interaction.user)
        except GameJoinError as err:
            await interaction.followup.send(lang_pack['ERROR_JOIN'], ephemeral=True)
            return

        players = ", ".join([player.mention for player in self.game.players])

        file = self.game.get_showcase("image.png")

        embed = discord.Embed(title=lang_pack['NAME'], color=0xfadf1c)
        embed.set_image(url="attachment://image.png")

        if not self.game.isFull():
            # 遊戲人數尚未滿，等待玩家中
            embed.add_field(name=lang_pack['WAIT'], value=players, inline=True)
            embed.add_field(name=lang_pack['STATUS'],
                            value=lang_pack['STATUS_WAIT'] % (self.game.maxPlayers - len(self.game.players)),
                            inline=True)

            self._set_join_view(timeout=self.time_out)

            await self.ctx.edit(embed=embed, attachments=[file], view=self._view)
        else:
            # 遊戲準備開始，清空互動 UI
            embed.add_field(name=lang_pack['PLAYERS'], value=players, inline=True)
            embed.add_field(name=lang_pack['STATUS'], value=lang_pack['STATUS_PREPARE'], inline=True)

            self._clear_view()
            await self.ctx.edit(embed=embed, attachments=[file], view=self._view)
            await self._countdown()

    @lang("cmd", "game", "connect4")
    async def _callback_abort(self, interaction: discord.Interaction, lang_pack=None):
        # 避免出現交互失敗
        await interaction.response.defer()

        if interaction.user == self.creator:
            embed = discord.Embed(title=lang_pack['NAME'], color=0xfadf1c)
            embed.add_field(name=lang_pack['ABORT_SUCCESS'],
                            value=datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

            self._clear_view()
            await self.ctx.edit(embed=embed, attachments=[], view=self._view)
        else:
            await interaction.followup.send(lang_pack['ERROR_ABORT'], ephemeral=True)

    @lang("cmd", "game", "connect4")
    def _callback_choose(self, slot: int, lang_pack=None):
        async def _callback_template(interaction: discord.Interaction):
            # 避免交互失敗
            await interaction.response.defer()

            # 可操縱玩家
            target = self.game.get_order()[0].player
            if interaction.user == target:
                try:
                    self.game.choose(slot)
                except OutOfSlotError as err:
                    await interaction.followup.send(lang_pack['ERROR_OUTOFSLOT'], ephemeral=True)

                if not self.game.isFinished():
                    # 玩家資訊
                    current, next = self.game.get_order()

                    # 棋盤戰況
                    file = self.game.get_showcase("image.png")

                    embed = discord.Embed(title=lang_pack['NAME'], color=0xfadf1c)
                    embed.add_field(name=lang_pack['CURRENT'] % current.color, value=current.mention, inline=True)
                    embed.add_field(name=lang_pack['NEXT'] % next.color, value=next.mention, inline=True)
                    embed.set_image(url="attachment://image.png")

                    self._set_play_view(timeout=self.time_out)

                    await self.ctx.edit(embed=embed, attachments=[file], view=self._view)
                else:
                    # 玩家資訊
                    winners = self.game.get_winner()

                    # 棋盤紀錄
                    file = self.game.make_record("image.gif")

                    embed = discord.Embed(title=lang_pack['NAME'], color=0xfadf1c)
                    embed.set_image(url="attachment://image.gif")

                    if len(winners) == 1:
                        embed.add_field(name=lang_pack['WINNER'] % winners[0].color,
                                        value=winners[0].mention, inline=True)
                        content = lang_pack['WINNER_MENTION'] % winners[0].mention
                    else:
                        # 1, 0 相反是因為最後一部並沒有交換順序，反過來輸出會是由起始玩家先輸出
                        embed.add_field(name=lang_pack['DRAW'] % (winners[1].color, winners[0].color),
                                        value=winners[1].mention + ', ' + winners[0].mention, inline=True)
                        content = lang_pack['DRAW_MENTION'] % (winners[1].mention, winners[0].mention)

                    self._clear_view()
                    await self.ctx.edit(content=content,
                                        embed=embed, attachments=[file], view=self._view)
            else:
                await interaction.followup.send(lang_pack['ERROR_OPERATE'] % target.mention, ephemeral=True)
        return _callback_template
