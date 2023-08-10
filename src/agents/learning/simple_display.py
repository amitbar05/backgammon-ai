from typing import List

from src.game.core.bar import Bar
from src.game.core.colors import PlayerColor
from src.game.core.dice import Dice
from src.game.core.game_state import GameState
from src.game.core.move import Move


class SimpleDisplay:
    def __init__(self, white_nickname: str, black_nickname: str) -> None:
        self.white_nickname = white_nickname
        self.black_nickname = black_nickname

    def say_hello(self) -> None:
        print("========================================================")
        print(f"Backgammon CLI    "
              f"White: {self.white_nickname}   "
              f"Black: {self.black_nickname}")

    @staticmethod
    def show_state(state: GameState) -> None:
        print(state.board, end="\n\n")

    @staticmethod
    def show_turn(player: PlayerColor, play_number: int) -> None:
        print(f"\n{'-' * 5} Turn: {player.name}, (Play {play_number}) {'-' * 5}")
        # print(f"{player.name}'s turn ({play_number})")
        # print(f"Turn: {player.name}")

    @staticmethod
    def show_dice(dice: Dice) -> None:
        print(dice)

    @staticmethod
    def show_remaining_moves(dice: Dice) -> None:
        print(f"Moves left: {dice.remaining_steps}")

    @staticmethod
    def show_winner(player: PlayerColor) -> None:
        print(f"{player.name} has won!")

    @staticmethod
    def notify_impossible_move(move: Move) -> None:
        print(f"Impossible move: {move} ! try again")

    @staticmethod
    def notify_no_possible_moves(color: PlayerColor) -> None:
        print("\n***No moves possible for ", color)
        print("*** switch to ", color.opposite(), "\n")

    @staticmethod
    def show_chosen_moves(moves: List[Move]) -> None:
        for move in moves:
            SimpleDisplay.show_chosen_move(move)

    @staticmethod
    def show_chosen_move(move: Move) -> None:
        print(f"Chosen move: {move}")