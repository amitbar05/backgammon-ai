from abc import ABC, abstractmethod
from typing import Set
from src.game.core.game_state import GameState
from src.game.core.move import Move


class Player(ABC):
    @abstractmethod
    def choose_move(self, game_state: GameState, possible_moves: Set[Move]) -> Move:
        """ This method must return a move from the possible_moves set"""
        pass

    @abstractmethod
    def choose_play(self, game_state: GameState, reachable_states: Set[GameState]) -> GameState:
        """ This method must return a state from the reachable states"""
        pass

    @abstractmethod
    def nickname(self) -> str:
        pass
