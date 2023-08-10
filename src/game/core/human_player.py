from copy import deepcopy
from typing import Set
from src.game.core.game_state import GameState
from src.game.core.move import Move
from src.game.core.player import Player


class HumanPlayer(Player):
    def choose_move(self, game_state: GameState, possible_moves: Set[Move]) -> Move:
        while True:
            src, dst = HumanPlayer._get_input()
            move = game_state.find_move(src, dst)
            if move is not None:
                return move
            else:
                print("Illegal move! try again.")

    def choose_play(self, game_state: GameState, reachable_states: Set[GameState]) -> GameState:
        raise NotImplemented("Human can only do single moves")

    def nickname(self) -> str:
        return "Human"

    @staticmethod
    def _get_input():
        src = input("Choose source move location (-1 is bar): ")
        while not src.strip("-").isnumeric():
            src = input("Bad input. Please insert an integer (-1 is bar): ")
        dst = input("Choose destination move location: ")
        while not dst.strip("-").isnumeric():
            dst = input("Bad input. Please insert an integer: ")
        return int(src), int(dst)
