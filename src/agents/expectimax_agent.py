import random
from copy import deepcopy
from typing import Set, Callable

from src.agents.agent import Agent
from src.game.core.board import Board
from src.game.core.colors import PlayerColor
from src.game.core.dice import Dice
from src.game.core.game_state import GameState


class ExpectimaxAgent(Agent):
    def __init__(self, color: PlayerColor,
                 heuristic_function: Callable[[Board], float],
                 max_depth=1,
                 dice_sample_size=36
                 ):
        super().__init__(color)
        self.max_depth = max_depth
        self.dice_sample_size = dice_sample_size
        self.heuristic_function = heuristic_function

    def choose_play(self, game_state: GameState, reachable_states: Set[GameState]) -> GameState:
        return max((state for state in reachable_states), key=lambda state: self._expectimax_value(state, self.color, depth=1))

    def _expectimax_value(self, state: GameState, player: PlayerColor, depth) -> float:
        expected_value = 0
        for dice, factor in [(Dice.get_possible_rolls_excluding_doubles(), 2), (Dice.get_possible_doubles(), 1)]:
            new_state = deepcopy(state)
            new_state.dice = Dice(dice)
            value = self._max_value(new_state, depth) if state.turn_color == player else self._min_value(new_state, depth)
            expected_value += factor * float(value)/Dice.TOTAL_COMBINATIONS
        return expected_value

    def _min_value(self, state: GameState, current_depth) -> float:
        if current_depth == self.max_depth or state.is_game_ended():
            return self.evaluation_function(state)
        else:
            return min((self._expectimax_value(state, self.color, current_depth + 1) for state in state.reachable_states))

    def _max_value(self, state: GameState, current_depth) -> float:
        if current_depth == self.max_depth or state.is_game_ended():
            return self.evaluation_function(state)
        else:
            return max((self._expectimax_value(state, self.color, current_depth + 1) for state in state.reachable_states))

    def evaluation_function(self, state: GameState) -> float:
        return self.heuristic_function(state.board)

    def nickname(self) -> str:
        return "ExpectimaxAgent"
