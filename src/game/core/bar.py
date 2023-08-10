from __future__ import annotations
from collections import defaultdict
from copy import deepcopy

from src.game.core.colors import PlayerColor


class Bar:
    def __init__(self, number_of_checkers: tuple[int, int] = None) -> None:
        self.__counter: dict[PlayerColor, int] = defaultdict(lambda: 0)
        if number_of_checkers is not None:
            self.__counter[PlayerColor.BLACK] += number_of_checkers[0]
            self.__counter[PlayerColor.WHITE] += number_of_checkers[1]

    def __eq__(self, other: Bar) -> bool:
        return self.__counter == other.__counter

    def __copy__(self) -> Bar:
        copy_bar = Bar()
        copy_bar.__counter = deepcopy(self.__counter)
        return copy_bar

    def __str__(self) -> str:
        if self.contains(PlayerColor.BLACK):
            return f"Bar: {self.count(PlayerColor.BLACK)}B"
        if self.contains(PlayerColor.WHITE):
            return f"Bar: {self.count(PlayerColor.WHITE)}W"
        return ""

    def __bool__(self) -> bool:
        return bool(self.__counter.get(PlayerColor.BLACK)) or bool(self.__counter.get(PlayerColor.WHITE))

    def contains(self, color: PlayerColor) -> bool:
        return bool(self.__counter.get(color))

    def count(self, color: PlayerColor) -> int:
        return self.__counter.get(color) or 0

    def add_checker(self, color: PlayerColor):
        self.__counter[color] += 1

    def remove_checker(self, color: PlayerColor):
        self.__counter[color] -= 1
