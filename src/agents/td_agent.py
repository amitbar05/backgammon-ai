from typing import Set

from src.agents.agent import Agent
from src.agents.expectimax_agent import ExpectimaxAgent
from src.game.core.colors import PlayerColor

from src.game.core.game_state import GameState
from src.game.core.move import Move
from src.agents.learning.medium_network import q_network


class TDAgent(Agent):
    def __init__(self, color: PlayerColor):
        # super().__init__(color, q_network.get_score, max_depth)
        super().__init__(color)

    def choose_play(self, game_state: GameState, reachable_states: Set[GameState]) -> GameState:
        if self.color == PlayerColor.BLACK:
            return max(reachable_states, key=lambda state: self.evaluation_function(state))
        else:
            return min(reachable_states, key=lambda state: self.evaluation_function(state))

    def evaluation_function(self, state: GameState):
        return q_network.get_score(state)

    def nickname(self) -> str:
        return "TempDiffAgent"
