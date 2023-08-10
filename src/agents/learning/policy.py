from typing import Callable, Set

import numpy as np

from src.agents.learning.replay_buffer import ReplayBuffer
from src.game.core.game_state import GameState
from src.game.core.utils import GameUtils


class Policy:
    def __init__(self, choose_action: Callable, agent_nickname: str) -> None:
        self.choose_action = choose_action
        self.agent_nickname = agent_nickname

    def choose_play(self, game_state: GameState, reachable_states: Set[GameState]) -> GameState:
        return self.choose_action(game_state, reachable_states)

    def agent_nickname(self):
        return self.agent_nickname


class CollectPolicy(Policy):
    def __init__(self, choose_action: Callable, agent_nickname: str, replay_buffer: ReplayBuffer):
        super().__init__(choose_action, agent_nickname)
        self.replay_buffer = replay_buffer

    def choose_play(self, game_state: GameState, reachable_states: Set[GameState]) -> GameState:
        new_state = super().choose_play(game_state, reachable_states)
        input_vec = GameUtils.extract_features(new_state)
        input_tensor = np.reshape(input_vec, (1, -1))
        self.replay_buffer.add(input_tensor, new_state.turn_color)
        return new_state
