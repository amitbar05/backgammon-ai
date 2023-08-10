
from abc import ABC, abstractmethod
from typing import Set

import numpy as np

from src.agents.learning.policy import Policy, CollectPolicy
from src.game.core.colors import PlayerColor
from src.game.core.game_state import GameState
from src.game.core.move import Move
from src.game.core.player import Player


class Agent(Player, ABC):
    def __init__(self, color: PlayerColor):
        self.current_play: list[Move] = []
        self.color = color

    def choose_move(self, game_state: GameState, possible_moves: Set[Move]) -> Move:
        if not self.current_play:
            possible_plays = game_state.get_possible_plays()
            successor_state = self.choose_play(game_state, set(possible_plays.keys()))
            self.current_play = list(reversed(possible_plays[successor_state]))
        move = self.current_play.pop()
        return game_state.find_move(move.src, move.dest)

    def choose_play(self, game_state: GameState, reachable_states: Set[GameState]) -> GameState:
        return max(reachable_states, key=lambda state: self.evaluation_function(state))

    @abstractmethod
    def evaluation_function(self, state: GameState):
        pass

    def get_policy(self, agent_nickname) -> Policy:
        return Policy(self.choose_play, agent_nickname)

    def get_collect_policy(self, agent_nickname, replay_buffer) -> CollectPolicy:
        return CollectPolicy(self.choose_play, agent_nickname, replay_buffer)
