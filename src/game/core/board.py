from __future__ import annotations

from copy import deepcopy
from typing import List, Union

from sortedcontainers import SortedList

from src.game.core.bar import Bar
from src.game.core.colors import PlayerColor
from src.game.core.move import Move
from src.game.core.point import Point


class Board:
    def __init__(self, initial_layout: Union[dict[int, int], dict[str, tuple[int, int]]] = None) -> None:
        if initial_layout is None: initial_layout = Board._initial_layout()
        if "bar" in initial_layout:
            self.__bar: Bar = Bar(initial_layout["bar"])
            initial_layout.pop("bar", None)
        else:
            self.__bar: Bar = Bar()
        self.__points: List[Point] = self._init_points(initial_layout)
        self.__points_locations: dict[PlayerColor, SortedList] = {
            PlayerColor.WHITE: self._init_white_points_locations(),
            PlayerColor.BLACK: self.__init_black_points_locations()
        }

    def __eq__(self, other: Board):
        return self.__points == other.__points and self.bar == other.bar

    def __copy__(self) -> Board:
        copy_board = Board()
        copy_board.__bar = deepcopy(self.__bar)
        copy_board.__points = deepcopy(self.__points)
        copy_board.__points_locations = deepcopy(self.__points_locations)
        return copy_board

    def __hash__(self):
        print("Test")
        return hash(tuple(self.__points))

    def __str__(self) -> str:
        string = ''
        string += "========================================================\n"
        string += "| 13  14  15  16  17  18 | 19  20  21  22  23  24 | 25 |\n"
        string += "--------------------------------------------------------\n"
        line = "|"
        for i in range(13, 18 + 1):
            line = line + str(self.point(i))
        line = line + "|"
        for i in range(19, 24 + 1):
            line = line + str(self.point(i))
        line = line + "|"
        line = line + str(self.point(25))
        string += line + "\n"
        for _ in range(3):
            string += "|                        |                        |\n"
        line = "|"
        for i in reversed(range(7, 12+1)):
            line = line + str(self.point(i))
        line = line + "|"
        for i in reversed(range(1, 6+1)):
            line = line + str(self.point(i))
        line = line + "|"
        line = line + str(self.point(0))
        string += line + "\n"
        string += "--------------------------------------------------------\n"
        string += "| 12  11  10  9   8   7  |  6  5   4   3   2   1  | 0  |\n"
        if self.bar:
            string += str(self.bar) + "\n"
        string += "========================================================"
        return string

    @property
    def points(self) -> List[Point]:
        return self.__points

    @property
    def bar(self) -> Bar:
        return self.__bar

    @property
    def points_locations(self) -> dict[PlayerColor, SortedList]:
        return self.__points_locations

    def point(self, index) -> Point:
        return self.__points[index]

    def apply_move(self, move: Move) -> None:
        if move.src == Move.BAR_INDEX:
            self.bar.remove_checker(move.player_color)
        else:
            self._remove_checker_from_point(move)
        self._handle_possible_eat(move)
        self._add_checker_to_point(move)

    def did_white_bear_off(self) -> bool:
        return self.point(0).count == 15

    def did_black_bear_off(self) -> bool:
        return self.point(25).count == 15

    def count_active_checkers(self, color: PlayerColor) -> int:
        return sum(self.point(i).count for i in range(1, 25) if self.point(i).player_color == color)

    def can_bear_off(self, color: PlayerColor) -> bool:
        if color == PlayerColor.WHITE:
            return max(self.__points_locations[PlayerColor.WHITE]) <= 6 and not self.bar.contains(color)
        else:
            return min(self.__points_locations[PlayerColor.BLACK]) >= 19 and not self.bar.contains(color)

    def get_furthest_point_idx(self, color):
        return max(self.__points_locations[PlayerColor.WHITE]) if color == PlayerColor.WHITE else\
            min(self.__points_locations[PlayerColor.BLACK])

    def goal_point(self, color: PlayerColor) -> Point:
        return self.point(self.goal_point_idx(color))

    def _remove_checker_from_point(self, move: Move) -> None:
        index = move.src
        self.point(index).remove_checker(move.player_color)
        if self.point(index).count == 0:
            self.__points_locations[move.player_color].remove(index)

    def _add_checker_to_point(self, move: Move) -> None:
        index = move.dest
        self.point(index).add_checker(move.player_color)
        if self.point(index).count == 1 and index != self.goal_point_idx(move.player_color):
            self.points_locations[move.player_color].add(index)

    def _handle_possible_eat(self, move: Move) -> None:
        opponent = move.player_color.opposite()
        if self.point(move.dest).player_color == opponent:
            self.point(move.dest).remove_checker(opponent)
            self.points_locations[opponent].remove(move.dest)
            self.bar.add_checker(opponent)

    @staticmethod
    def movement_direction(color: PlayerColor) -> int:
        return 1 if color == PlayerColor.BLACK else -1

    @staticmethod
    def debar_landing_point(color: PlayerColor, die: int) -> int:
        return die if color == PlayerColor.BLACK else 25 - die

    @staticmethod
    def walk_landing_point(color: PlayerColor, start_index: int, distance: int) -> int:
        dest = start_index + (distance * Board.movement_direction(color))
        return dest if 0 <= dest <= 25 else Board.goal_point_idx(color)

    @staticmethod
    def goal_point_idx(color: PlayerColor) -> int:
        return 0 if color == PlayerColor.WHITE else 25

    @staticmethod
    def _init_points(initial_layout: dict[int, int]) -> List[Point]:
        points = [Point(i) for i in range(0, 26)]
        for index, count in initial_layout.items():
            color = PlayerColor.WHITE if count < 0 else PlayerColor.BLACK
            points[index].add_checker(color, abs(count))
        return points

    @staticmethod
    def _init_white_points_locations() -> SortedList:
        white_pts = SortedList()
        for i, count in Board._initial_layout().items():
            if count < 0:
                white_pts.add(i)
        return white_pts

    @staticmethod
    def __init_black_points_locations() -> SortedList:
        black_pts = SortedList()
        for i, count in Board._initial_layout().items():
            if count > 0:
                black_pts.add(i)
        return black_pts

    @staticmethod
    def _initial_layout() -> dict[int, int]:
        """
        Keys: points indices
        Values: negative represents white checkers, positive represents black.
        """
        return {
            6: -5,
            8: -3,
            13: -5,
            24: -2,
            19: 5,
            17: 3,
            12: 5,
            1: 2
        }
