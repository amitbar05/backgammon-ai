from __future__ import annotations
from typing import Union

from src.game.core.colors import PlayerColor


class Move:
    BAR_INDEX = -1

    def __init__(self, player: PlayerColor, source: int, dest: int, distance: int = None) -> None:
        if source != Move.BAR_INDEX:
            assert 1 <= source <= 24, f"Input source was {source}"
        if player == PlayerColor.WHITE:
            assert 0 <= dest <= 24
        if player == PlayerColor.BLACK:
            assert 1 <= dest <= 25
        self.__src: int = source
        self.__dest: int = dest
        self.__player_color = player
        if distance:
            self.__distance: int = distance
        elif source == Move.BAR_INDEX:
            self.__distance: int = dest
        else:
            self.__distance: int = abs(source - dest)

    def __repr__(self):
        return f"{self.src} ---[{self.distance}]---> {self.dest}"

    @property
    def src(self) -> int:
        return self.__src

    @property
    def dest(self) -> int:
        return self.__dest

    @property
    def distance(self) -> int:
        return self.__distance

    @property
    def player_color(self) -> PlayerColor:
        return self.__player_color
