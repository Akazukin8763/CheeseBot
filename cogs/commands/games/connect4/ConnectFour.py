from io import BytesIO
from enum import Enum
import random

import cv2
import numpy as np
from PIL import Image

import discord

from ..Utils import Game, add_title
from exceptions import GameActivateError, GameJoinError, OutOfSlotError


class GameStatus(Enum):
    STAGING = 1
    PLAYING = 2
    FINISHED = 3

    def __str__(self):
        return self.name


class GameColor(Enum):
    NONE = 0
    RED = 1
    YELLOW = 2

    def __str__(self):
        return self.name


class GameChunkInfo:

    def __init__(self, x: int, y: int, color: GameColor):
        self._x = x
        self._y = y
        self._color = color

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def color(self):
        return self._color


class PlayerInfo:

    def __init__(self, player: discord.Member, order: int):
        self._player = player
        self._order = order

    @property
    def player(self):
        return self._player

    @property
    def display_name(self):
        return self._player.display_name

    @property
    def mention(self):
        return self._player.mention

    @property
    def color(self):
        return GameColor(self._order + 1)

    def __str__(self):
        return f"Player: {self._player}, Color: {self.color}"


class ConnectFour(Game):

    def __init__(self):
        super().__init__()

        self._COLOR_BACKGROUND = [78, 123, 215]
        self._COLOR_WHITE = [255, 255, 255]
        self._COLOR_RED = [255, 68, 44]
        self._COLOR_YELLOW = [254, 221, 32]
        self._COLOR_RED_ENHANCE = [71, 8, 0]
        self._COLOR_YELLOW_ENHANCE = [71, 60, 0]

        self._chunk = None
        self._chunk_red = None
        self._chunk_yellow = None
        self._chunk_red_enhance = None
        self._chunk_yellow_enhance = None

        self._status = GameStatus.STAGING

        self._showcase = None
        self._showcase_idx = None

        self._remain_slot = [0, 1, 2, 3, 4, 5, 6]
        self._record_step = [GameChunkInfo(-1, -1, GameColor.NONE)]
        self._board = [[GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                        GameColor.NONE],
                       [GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                        GameColor.NONE],
                       [GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                        GameColor.NONE],
                       [GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                        GameColor.NONE],
                       [GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                        GameColor.NONE],
                       [GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                        GameColor.NONE]]

        self._players = []  # PlayerInfo
        self._maxPlayers = 2

    @property
    def players(self):
        return self._players

    @property
    def maxPlayers(self):
        return self._maxPlayers

    @property
    def remainSlot(self):
        return self._remain_slot

    @property
    def status(self):
        return self._status

    def isFull(self):
        return len(self.players) == self._maxPlayers

    def isFinished(self):
        return self._status == GameStatus.FINISHED

    """
    參數初始化
    """
    def _init_chunk(self):
        chunk = np.zeros((100, 100, 3), dtype=np.uint8)
        chunk[:, :, :] = np.array(self._COLOR_BACKGROUND)

        self._chunk = cv2.circle(chunk.copy(), (50, 50), 40, self._COLOR_WHITE, -1)
        self._chunk_red = cv2.circle(chunk.copy(), (50, 50), 40, self._COLOR_RED, -1)
        self._chunk_yellow = cv2.circle(chunk.copy(), (50, 50), 40, self._COLOR_YELLOW, -1)

        self._chunk_red_enhance = cv2.circle(self._chunk_red.copy(), (50, 50), 40, self._COLOR_RED_ENHANCE, 3)
        self._chunk_yellow_enhance = cv2.circle(self._chunk_yellow.copy(), (50, 50), 40, self._COLOR_YELLOW_ENHANCE, 3)

    def _init_showcase(self):
        self._showcase = np.zeros((600, 700, 3), dtype=np.uint8)
        self._fill_showcase(self._showcase, copy=False)

    def _init_showcase_idx(self):
        self._showcase_idx = np.zeros((100, 700, 3), dtype=np.uint8)

        chunk = np.zeros((100, 100, 3), dtype=np.uint8)
        chunk[:, :, :] = np.array(self._COLOR_BACKGROUND)

        for w in range(0, 700, 100):
            self._showcase_idx[:, w:w + 100, :] = add_title(chunk.copy(), f"{w // 100 + 1}")

    """
    遊戲刷新、判定函式
    """
    def _fill_showcase(self, showcase, board=None, copy=False):
        if copy:
            showcase = showcase.copy()
        if board is None:
            board = [[GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                      GameColor.NONE],
                     [GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                      GameColor.NONE],
                     [GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                      GameColor.NONE],
                     [GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                      GameColor.NONE],
                     [GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                      GameColor.NONE],
                     [GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                      GameColor.NONE]]

        for h in range(6):
            for w in range(7):
                if board[h][w] == GameColor.RED:
                    showcase[h * 100:h * 100 + 100, w * 100:w * 100 + 100, :] = self._chunk_red
                elif board[h][w] == GameColor.YELLOW:
                    showcase[h * 100:h * 100 + 100, w * 100:w * 100 + 100, :] = self._chunk_yellow
                else:
                    showcase[h * 100:h * 100 + 100, w * 100:w * 100 + 100, :] = self._chunk

        return showcase

    def _refresh_showcase(self, showcase, old: GameChunkInfo, new: GameChunkInfo, copy=False):
        if copy:
            showcase = showcase.copy()

        if not (old.x == -1 and old.y == -1):
            showcase[old.x * 100:old.x * 100 + 100, old.y * 100:old.y * 100 + 100, :] = \
                self._chunk_red if old.color == GameColor.RED else \
                    self._chunk_yellow if old.color == GameColor.YELLOW else self._chunk

        if not (new.x == -1 and new.y == -1):
            showcase[new.x * 100:new.x * 100 + 100, new.y * 100:new.y * 100 + 100, :] = \
                self._chunk_red_enhance if new.color == GameColor.RED else \
                    self._chunk_yellow_enhance if new.color == GameColor.YELLOW else self._chunk

            self._board[new.x][new.y] = new.color

        return showcase

    def _check_line(self):
        h, w, color = self._record_step[-1].x, self._record_step[-1].y, self._record_step[-1].color

        # Top to Bottom
        connect = 0
        for i in range(0, 6):
            if self._board[i][w] == color or i == h:
                connect += 1
                if connect >= 4:
                    return True
            else:
                connect = 0

        # Left to Right
        connect = 0
        for i in range(0, 7):
            if self._board[h][i] == color or i == w:
                connect += 1
                if connect >= 4:
                    return True
            else:
                connect = 0

        # TopLeft to BottomRight
        connect = 0
        for i, j in zip(range(h - 3, h + 4), range(w - 3, w + 4)):
            if 0 <= i <= 5 and 0 <= j <= 6:
                if self._board[i][j] == color or i == h and j == w:
                    connect += 1
                    if connect >= 4:
                        return True
                else:
                    connect = 0

        # TopRight to BottomLeft
        connect = 0
        for i, j in zip(range(h - 3, h + 4), range(w - 3, w + 4)[::-1]):
            if 0 <= i <= 5 and 0 <= j <= 6:
                if self._board[i][j] == color or i == h and j == w:
                    connect += 1
                    if connect >= 4:
                        return True
                else:
                    connect = 0

        # 尚未連線成功
        return False

    """
    遊戲顯示畫面、資訊
    """
    def get_thumbnail(self):
        thumbnail = np.zeros((600, 700, 3), dtype=np.uint8)
        board = [[GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                  GameColor.NONE],
                 [GameColor.RED, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE, GameColor.NONE,
                  GameColor.NONE],
                 [GameColor.YELLOW, GameColor.NONE, GameColor.RED, GameColor.NONE, GameColor.RED, GameColor.NONE,
                  GameColor.RED],
                 [GameColor.YELLOW, GameColor.YELLOW, GameColor.RED, GameColor.YELLOW, GameColor.RED, GameColor.YELLOW,
                  GameColor.YELLOW],
                 [GameColor.YELLOW, GameColor.RED, GameColor.RED, GameColor.RED, GameColor.YELLOW, GameColor.YELLOW,
                  GameColor.YELLOW],
                 [GameColor.RED, GameColor.RED, GameColor.RED, GameColor.YELLOW, GameColor.YELLOW, GameColor.YELLOW,
                  GameColor.RED]]

        return self._fill_showcase(thumbnail, board)

    def get_showcase(self, filename: str):
        showcase = None

        # 準備階段，顯示預設遊戲圖片
        if self._status == GameStatus.STAGING:
            showcase = self.get_thumbnail()
            showcase = add_title(showcase, "Connect Four")
        # 遊戲中，顯示目前遊玩狀態
        elif self._status == GameStatus.PLAYING:
            if len(self._record_step) == 1:
                self._refresh_showcase(self._showcase, GameChunkInfo(-1, -1, GameColor.NONE), self._record_step[-1])
            else:
                self._refresh_showcase(self._showcase, self._record_step[-2], self._record_step[-1])

            showcase = np.concatenate((self._showcase, self._showcase_idx), axis=0)
        # 遊戲結束
        elif self._status == GameStatus.FINISHED:
            self._refresh_showcase(self._showcase, self._record_step[-2], self._record_step[-1])
            showcase = self._showcase

        with BytesIO() as image:
            Image.fromarray(showcase).save(image, 'PNG')
            image.seek(0)

            return discord.File(fp=image, filename=filename)

    def get_order(self):
        return self._players[0], self._players[1]

    def get_winner(self):
        if self._status == GameStatus.FINISHED:
            if len(self._remain_slot) == 0:
                winners = [self._players[0], self._players[1]]
            else:
                winners = [self._players[0]]

            return winners
        else:
            return None

    def make_record(self, filename: str):
        showcase = np.zeros((600, 700, 3), dtype=np.uint8)
        self._fill_showcase(showcase)

        # 儲存歷史步驟
        frames = []
        for i in range(1, len(self._record_step)):
            self._refresh_showcase(showcase, self._record_step[i-1], self._record_step[i])
            frame = Image.fromarray(showcase)

            image_binary = BytesIO()
            frame.save(image_binary, 'GIF')
            frame = Image.open(image_binary)
            frames.append(frame)

        # 將每一步轉換成 GIF
        animated_gif = BytesIO()
        frames[0].save(animated_gif,
                       format='GIF',
                       save_all=True,
                       append_images=frames[1:],  # Pillow >= 3.4.0
                       duration=500,
                       loop=0)
        animated_gif.seek(0)

        return discord.File(fp=animated_gif, filename=filename)

    """
    遊戲操作
    """
    def create(self):
        self._init_chunk()
        self._init_showcase()
        self._init_showcase_idx()

        self._setup = True

    def join(self, player: discord.Member):
        if not self._setup:
            raise GameActivateError(message="Game is uncreated, please execute create() first.")

        if self.isFull():
            raise GameJoinError(message="This game is full.")
        else:
            for info in self._players:
                if player == info.player:
                    raise GameJoinError(message="You are already in this game.")

            self._players.append(PlayerInfo(player, len(self._players)))

    def start(self):
        if not self._setup:
            raise GameActivateError(message="Game is uncreated, please execute create() first.")
        if not self.isFull():
            raise GameActivateError(message="Players is less than 2.")

        self._status = GameStatus.PLAYING

        # 隨機一位玩家為初始玩家
        random.shuffle(self._players)

    def choose(self, slot: int):
        if not self._setup:
            raise GameActivateError(message="Game is uncreated, please execute create() first.")
        if not self._status == GameStatus.PLAYING:
            raise GameActivateError(message="Game isn't started, please execute start() first.")

        for h in range(6)[::-1]:
            if self._board[h][slot] == GameColor.NONE:
                self._record_step.append(GameChunkInfo(h, slot, self._players[0].color))

                # 移除已經滿的格位
                if h == 0:
                    self._remain_slot.remove(slot)
                break
            # 從 UI 上操作並不會進入下方條件式，除非手動打指令
            elif h == 0:
                raise OutOfSlotError(message="Out of slot.")

        if self._check_line() or len(self._remain_slot) == 0:
            self._status = GameStatus.FINISHED
        else:
            # 交換順序
            self._players[0], self._players[1] = self._players[1], self._players[0]
