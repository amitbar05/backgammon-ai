from __future__ import annotations
from typing import Union

from src.game.core.colors import PlayerColor


class Point:
    def __init__(self, index) -> None:
        self.__count: int = 0
        self.__index: int = index
        self.__player_color: Union[PlayerColor, None] = None

    def __hash__(self):
        return hash((self.index, self.count, self.player_color))

    def __str__(self) -> str:
        if self.count == 0:
            return " .  "
        return f" {self.count}{self.player_color} "

    @property
    def index(self) -> int:
        return self.__index

    @property
    def count(self) -> int:
        return self.__count

    @property
    def player_color(self) -> Union[PlayerColor, None]:
        return self.__player_color

    def add_checker(self, color: PlayerColor, amount: int = 1):
        assert not self.player_color == color.opposite(), \
            "Point already has a checker from the opposite side. You should remove the opponent's checkers first."
        self.__count += amount
        self.__player_color = color

    def remove_checker(self, color: PlayerColor):
        assert self.player_color == color, "This point belongs to the opposite player"
        assert abs(self.__count) != 0, "You tried to remove more checkers than what exists"
        self.__count -= 1
        if self.count == 0:
            self.__player_color = None

    def __eq__(self, other: Point) -> bool:
        return self.index == other.index and \
               self.count == other.count and\
               self.player_color == other.player_color
