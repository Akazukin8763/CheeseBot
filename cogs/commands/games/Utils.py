import abc

import cv2
import numpy as np

import discord


def add_title(img: np.ndarray, title: str, font=cv2.FONT_HERSHEY_SIMPLEX, fontScale=2, thickness=2):
    textsize = cv2.getTextSize(title, font, fontScale, thickness)[0]

    offsetX = (img.shape[1] - textsize[0]) // 2
    offsetY = (img.shape[0] + textsize[1]) // 2

    return cv2.putText(img, title, (offsetX, offsetY), font, fontScale, (0, 0, 0), thickness, cv2.LINE_AA)


class Game(metaclass=abc.ABCMeta):

    def __init__(self):
        self._setup = False

    @property
    def players(self):
        return NotImplemented

    @property
    def maxPlayers(self):
        return NotImplemented

    @abc.abstractmethod
    def get_showcase(self, filename: str):
        return NotImplemented

    @abc.abstractmethod
    def create(self):
        return NotImplemented

    @abc.abstractmethod
    def join(self, user: discord.Member):
        return NotImplemented

    @abc.abstractmethod
    def start(self):
        return NotImplemented

    @abc.abstractmethod
    def choose(self, move: int):
        return NotImplemented
