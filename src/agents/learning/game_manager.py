from random import Random
from collections import defaultdict
from copy import copy
from typing import Union

import tensorflow as tf

from src.agents.learning.policy import Policy
from src.agents.learning.simple_display import SimpleDisplay
from src.game.core.colors import PlayerColor
from src.game.core.game_state import GameState
from src.game.core.move import Move


class GameManager:
    """
    A GameRunner runs the game.
    """

    def __init__(self, white_policy: Policy, black_policy: Policy, seed=None) -> None:
        """
        :param display:
        :param white_player:
        :param black_player:
        """
        self.__policies = {
            PlayerColor.WHITE: white_policy,
            PlayerColor.BLACK: black_policy
        }
        self.__display = SimpleDisplay(white_nickname=white_policy.agent_nickname, black_nickname=black_policy.agent_nickname)
        self.__game_state: Union[GameState, None] = None
        self.__total_wins = defaultdict(lambda: 0)
        self.__total_score = defaultdict(lambda: 0)
        self.__starting_player_color = None
        self.__rng = Random(seed)
        self.__plays_counter = 0
        self.__n_plays_list = []
        # debugging stats
        self._times_white_started = 0
        self._times_black_started = 0
        # debugging stats
        self.__eval_state = dict()

    def init_evaluation_state(self):
        # construct states for evaluation
        self.__eval_state["white_init"] = GameState(PlayerColor.WHITE)
        self.__eval_state["black_init"] = GameState(PlayerColor.BLACK)

        # little advantage to white, prediction should be [-1,0]
        board1 = {1: 1, 4: -3, 6: -3, 8: -2, 9: -2, 12: 2, 13: -1, 15: 3, 16: 1, 18: -2, 19: 3, 20: 1, 21: -2, 22: 2,
                  "bar": (2, 0)}
        self.__eval_state["eval_board1"] = GameState(PlayerColor.WHITE, board1)

        # little advantage to white, prediction should be [-1,0] closer to 0
        board2 = {1: 2, 4: -2, 5: -2, 6: -2, 8: -2, 11: -1, 12: 1, 13: -4, 17: 6, 16: 1, 19: 5, 24: -2, "bar": (1, 0)}
        self.__eval_state["eval_board2"] = GameState(PlayerColor.WHITE, board2)

        # little advantage to black, prediction should be [0,1]
        board3 = {1: -1, 4: -2, 5: -1, 6: -3, 8: -2, 9: 2, 10: -1, 12: -1, 13: -2, 17: 2, 18: 2, 19: 3, 20: 2, 21: 2,
                  22: 2, 24: -1, "bar": (0, 1)}
        self.__eval_state["eval_board3"] = GameState(PlayerColor.BLACK, board3)

        # black has an advantage, prediction should be 1.
        board4 = {4: -2, 5: -1, 6: -3, 8: -3, 9: 2, 12: -1, 13: -3, 14: 2, 16: 3, 17: 3, 19: 5, 22: -1, 24: -1}
        self.__eval_state["eval_board4"] = GameState(PlayerColor.BLACK, board4)

        # should be huge advantage to white, so prediction should be close to -2
        board5 = {1: -2, 2: -2, 3: -2, 4: -2, 5: -2, 6: -2, 8: -1, 12: 1, 13: -2, 15: 1, 17: 2, 19: 3, 20: 3, 21: 1,
                  22: 2, "bar": (2, 0)}
        self.__eval_state["eval_board5"] = GameState(PlayerColor.WHITE, board5)

    def get_eval_state_and_display(self, eval_code: str) -> GameState:
        state = self.__eval_state[eval_code]
        print("Turn color:", state.turn_color)
        print(state.board)
        return state

    def get_eval_state(self, eval_code: str) -> GameState:
        return self.__eval_state[eval_code]

    def run(self, num_of_games: int) -> None:
        for _ in range(num_of_games):
            self.play_episode()
        # self._display_summary(num_of_games, self.__total_wins, self.__total_score)
        # debug
        print(f"White started {self._times_white_started} times")
        print(f"Black started {self._times_black_started} times")
        print("Number of plays:", self.__n_plays_list)

    def play_episode(self) -> int:
        self._pre_game()
        self._game_loop()
        self._post_game()
        self.__n_plays_list.append(self.__plays_counter)
        n_of_plays = self.__plays_counter
        self.__plays_counter = 0
        return n_of_plays

    def _pre_game(self):
        self.__starting_player_color = self._choose_starting_player()
        # debug
        if self.__starting_player_color == PlayerColor.WHITE:
            self._times_white_started += 1
        else:
            self._times_black_started += 1
        # end debug
        self.__game_state = GameState(self.__starting_player_color)

    def _game_loop(self):
        while not self.__game_state.is_game_ended():
            # self.__display.show_state(self.__game_state)
            self._play_turn()
            self.__plays_counter += 1
            # self.__game_state.switch_turns()
            # should print "switched turns" using display

    def _post_game(self):
        winner = self.__game_state.get_winner()
        score = abs(self.__game_state.get_winner_score())
        # self.__display.show_winner(winner)
        self.__total_wins[winner] += 1
        self.__total_score[winner] += score
        # self.__starting_player_color = winner

    def _play_turn(self) -> None:
        self.__game_state.dice.roll()
        # self.__display.show_turn(self.__game_state.turn_color, self.__plays_counter)
        # self.__display.show_dice(self.__game_state.dice)
        if self.__game_state.possible_moves:
            # self.__display.show_remaining_moves(self.__game_state.dice)  # maybe delete this
            # get the moves from the policy
            new_state = self._get_new_state()
            self.__game_state.apply_play(new_state)
            # update the display
            # self.display_chosen_moves(moves)
            # self.__display.show_state(self.__game_state)
        else:
            # self.__display.notify_no_possible_moves(self.__game_state.turn_color)
            self.__game_state.switch_turns()

    # def display_chosen_moves(self, moves: list[Move]):
    #     for move in moves:
    #         self.__display.show_chosen_move(move)

    def _get_new_state(self) -> GameState:
        copy_state = copy(self.__game_state)
        new_state = self.__policies[self.__game_state.turn_color].choose_play(copy_state,
                                                                              set(self.__game_state.reachable_states))
        return new_state

    def _choose_starting_player(self) -> PlayerColor:
        random_player = self.__rng.choice([PlayerColor.WHITE, PlayerColor.BLACK])
        return PlayerColor(random_player)

    @staticmethod
    def _display_summary(num_of_games: int, wins: dict, score: dict) -> None:
        print(f"Total games: {num_of_games}\n"
              f"White wins: {wins[PlayerColor.WHITE]}, score: {score[PlayerColor.WHITE]}\n"
              f"Black wins: {wins[PlayerColor.BLACK]}, score: {score[PlayerColor.BLACK]}")

    def get_reward(self):
        winner = self.__game_state.get_winner()
        reward = tf.constant(self.__game_state.get_winner_score(), dtype=tf.float32)
        return winner, reward
