import random
import time
from collections import defaultdict
from copy import copy
from typing import List, Union

from src.game.core.dice import Dice
from src.game.core.human_player import HumanPlayer
from src.game.core.move import Move
from src.game.core.player import Player
from src.game.core.game_state import GameState
from src.game.core.colors import PlayerColor


class BackgammonCLI:
    def __init__(self, white_player: Player, black_player: Player, silent_mode: bool) -> None:
        self.__players = {
            PlayerColor.WHITE: white_player,
            PlayerColor.BLACK: black_player
        }
        self.__total_wins = defaultdict(lambda: 0)
        self.__total_score = defaultdict(lambda: 0)
        self.__game_state: Union[GameState, None] = None
        self.__display = NoDisplay() if silent_mode else CliDisplay(
            white_player.nickname(),
            black_player.nickname(),
        )
        self.__turn_handler = self._choose_handle_turn_strategy(white_player, black_player)

    def run(self, num_of_games: int = 1) -> None:
        for _ in range(num_of_games):
            start_time = time.time()
            self._pre_game()
            self._game_loop()
            self._post_game()
            print(f"Game took {time.time() - start_time} seconds")
        self._display_summary(num_of_games, self.__total_wins, self.__total_score)

    def _pre_game(self):
        self.__display.say_hello()
        starting_player = random.choice([PlayerColor.WHITE, PlayerColor.BLACK])
        self.__game_state = GameState(starting_player)
        self.__display.show_state(self.__game_state)

    def _game_loop(self):
        while not self.__game_state.is_game_ended():
            self._play_turn()

    def _post_game(self):
        winner = self.__game_state.get_winner()
        score = abs(self.__game_state.get_winner_score())
        self.__display.show_winner(winner)
        self.__total_wins[winner] += 1
        self.__total_score[winner] += score
        self.__starting_player_color = winner

    def _play_turn(self) -> None:
        self.__game_state.dice.roll()
        self.__display.show_turn(self.__game_state.turn_color)
        self.__display.show_dice(self.__game_state.dice)
        self.__turn_handler()

    def _make_single_moves(self):
        if not self.__game_state.possible_moves:
            self.__display.notify_no_possible_moves(self.__game_state.turn_color)
        while self.__game_state.possible_moves and not self.__game_state.dice.is_depleted():
            move = self.__players[self.__game_state.turn_color].choose_move(self.__game_state, self.__game_state.possible_moves)
            self.__display.show_chosen_move(move)
            self.__game_state.apply_move(move)
            self.__display.show_state(self.__game_state)
            if self.__game_state.possible_moves and not self.__game_state.dice.is_depleted():
                self.__display.show_turn(self.__game_state.turn_color)
                self.__display.show_remaining_moves(self.__game_state.dice)
        self.__game_state.switch_turns()

    def _make_complete_play(self):
        if self.__game_state.possible_moves:
            new_state = self._get_play()
            self.__game_state.apply_play(new_state)
            self.__display.show_state(self.__game_state)
        else:
            self.__display.notify_no_possible_moves(self.__game_state.turn_color)
            self.__game_state.switch_turns()

    def _get_play(self) -> GameState:
        current_player = self.__players[self.__game_state.turn_color]
        return current_player.choose_play(copy(self.__game_state), set(self.__game_state.reachable_states))

    def _choose_handle_turn_strategy(self, white: Player, black: Player):
        is_there_human_player = type(white) == HumanPlayer or type(black) == HumanPlayer
        return self._make_single_moves if is_there_human_player else self._make_complete_play

    @staticmethod
    def _display_summary(num_of_games: int, wins: dict, score: dict) -> None:
        print(f"Total games: {num_of_games}\n"
              f"White wins: {wins[PlayerColor.WHITE]}, score: {score[PlayerColor.WHITE]}\n"
              f"Black wins: {wins[PlayerColor.BLACK]}, score: {score[PlayerColor.BLACK]}")

    def get_reward(self):
        return self.__game_state.get_winner_score()


class CliDisplay:
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
    def show_turn(player_color: PlayerColor) -> None:
        print(f"Turn: {player_color.name}")

    @staticmethod
    def show_dice(dice: Dice) -> None:
        print(f"Dice: {dice.value}")

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
            CliDisplay.show_chosen_move(move)

    @staticmethod
    def show_chosen_move(move: Move) -> None:
        print(f"Chosen move: {move}")


class NoDisplay:
    def say_hello(self) -> None:
        return

    @staticmethod
    def show_state(state: GameState) -> None:
        return

    @staticmethod
    def show_turn(player_color: PlayerColor) -> None:
        return

    @staticmethod
    def show_dice(dice: Dice) -> None:
        return

    @staticmethod
    def show_remaining_moves(dice: Dice) -> None:
        return

    @staticmethod
    def show_winner(player: PlayerColor) -> None:
        return

    @staticmethod
    def notify_impossible_move(move: Move) -> None:
        return

    @staticmethod
    def show_chosen_move(move: Move) -> None:
        return

    @staticmethod
    def show_chosen_moves(moves: List[Move]) -> None:
        return

    @staticmethod
    def notify_no_possible_moves(color: PlayerColor) -> None:
        return
