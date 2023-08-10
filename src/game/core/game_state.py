from __future__ import annotations
from copy import copy, deepcopy
from typing import Union, List

from src.game.core.board import Board
from src.game.core.dice import Dice
from src.game.core.move import Move
from src.game.core.colors import PlayerColor


class GameState:
    """
    A GameState describes the current state of the game.
    """

    def __init__(self, starting_player: PlayerColor,
                 initial_layout: Union[dict[int, int], dict[str, tuple[int, int]]] = None) -> None:
        if initial_layout is None:
            self.__board: Board = Board()
        else:
            self.__board: Board = Board(initial_layout)
        self.__dice: Dice = Dice()
        self.__turn_color: PlayerColor = starting_player
        self.__possible_moves: Union[None, set[Move]] = None  # lazy evaluation
        self.__reachable_states: Union[None, set[GameState]] = None  # lazy evaluation

    def __copy__(self) -> GameState:
        copy_state = GameState(self.turn_color)
        copy_state.__dice = copy(self.dice)
        copy_state.__board = copy(self.board)
        copy_state.__possible_moves = copy(self.__possible_moves)
        return copy_state

    def __eq__(self, other: GameState) -> bool:
        # deleted dice check
        # and removing turn_color check
        return self.turn_color == other.turn_color and self.board == other.board
        return self.board == other.board

    def __hash__(self):
        return hash(id(self))

    @property
    def board(self) -> Board:
        return self.__board

    @property
    def dice(self) -> Dice:
        return self.__dice

    @dice.setter
    def dice(self, dice: Dice) -> None:
        self.__dice = dice

    @property
    def turn_color(self) -> PlayerColor:
        return self.__turn_color

    @property
    def possible_moves(self) -> set[Move]:
        if self.__possible_moves is None:
            self.__possible_moves = self._calculate_possible_moves()
        return self.__possible_moves

    @property
    def reachable_states(self) -> set[GameState]:
        if self.__reachable_states is None:
            self.__reachable_states = set(self.get_possible_plays().keys())
        return self.__reachable_states

    def is_game_ended(self) -> bool:
        return self.board.did_white_bear_off() or self.board.did_black_bear_off()

    def apply_move(self, move: Move) -> None:
        assert move in self.possible_moves, "A player must choose from the given possible moves (reference equality)"
        self.board.apply_move(move)
        self.dice.use_move(move.distance)
        self.__possible_moves = None

    def apply_play(self, new_state: GameState) -> None:
        assert new_state in self.reachable_states, "A player must choose from the given reachable states (reference equality)"
        self.__board = new_state.board
        self.__dice = new_state.dice
        self.__turn_color = new_state.__turn_color
        self.__reachable_states = None
        self.__possible_moves = None

    def get_winner(self) -> PlayerColor:
        assert self.is_game_ended()
        return PlayerColor.WHITE if self.board.did_white_bear_off() else PlayerColor.BLACK

    def get_winner_score(self) -> int:
        winner = self.get_winner()
        score = 2 if self.board.count_active_checkers(winner.opposite()) == 15 else 1
        return winner.win_factor() * score

    def switch_turns(self) -> None:
        self.__turn_color = self.turn_color.opposite()
        self.__possible_moves = None
        self.__reachable_states = None

    def find_move(self, src: int, dst: int) -> Union[Move, None]:
        for move in self.possible_moves:
            if move.src == src and move.dest == dst:
                return move

    def _calculate_possible_moves(self) -> set[Move]:
        bar, color = self.board.bar, self.turn_color
        if bar.contains(color):
            return self._get_possible_debar_points()
        else:
            advances = set()
            for distance in set(self.dice.remaining_steps):
                advances.update(self._get_possible_advances(distance))
            return advances

    def _get_possible_debar_points(self) -> set[Move]:
        debars = set()
        for i in set(self.dice.remaining_steps):
            landing_point_idx = Board.debar_landing_point(self.turn_color, i)
            landing_point = self.board.point(landing_point_idx)
            if self.turn_color.opposite() != landing_point.player_color or landing_point.count < 2:
                debars.add(Move(self.turn_color, Move.BAR_INDEX, landing_point_idx, i))
        return debars

    def _get_possible_advances(self, distance: int) -> set[Move]:
        def can_place() -> bool:
            point = self.board.point(dest_index)
            if 1 <= dest_index <= 24:
                return point.player_color != color.opposite() or point.count < 2
            elif dest_index == self.board.goal_point_idx(color) and self.board.can_bear_off(color):
                actual_distance = abs(dest_index - src_index)
                return distance == actual_distance or \
                       (distance > actual_distance and self.board.get_furthest_point_idx(color) == src_index)
            else:
                return False

        color = self.turn_color
        points_indices = self.board.points_locations[color]
        advances = set()

        for src_index in points_indices:
            dest_index = Board.walk_landing_point(color, src_index, distance)
            if can_place():
                advances.add(Move(color, src_index, dest_index, distance))

        return advances

    def get_possible_plays(self) -> dict[GameState, List[Move]]:
        def _generate_states(curr_state: GameState, applied_moves: List[Move]):
            no_more_moves = curr_state.dice.is_depleted() or not curr_state.possible_moves or curr_state.is_game_ended()
            if no_more_moves:
                # TODO: Make sure we don't add duplicate states!
                possible_plays[curr_state] = applied_moves
                curr_state.switch_turns()
            else:
                for move in curr_state.possible_moves:
                    new_state, new_moves = deepcopy(curr_state), deepcopy(applied_moves)
                    next_move = new_state.find_move(move.src, move.dest)
                    new_state.apply_move(next_move)
                    new_moves.append(next_move)
                    _generate_states(new_state, new_moves)

        possible_plays = dict()
        _generate_states(self, [])
        return possible_plays or {deepcopy(self)}
