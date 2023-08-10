import random

from src.agents.agent import Agent
from src.game.core.colors import PlayerColor
from src.game.core.game_state import GameState


class RandomAgent(Agent):
    def __init__(self, color: PlayerColor):
        super().__init__(color)

    def evaluation_function(self, state: GameState):
        return random.uniform(0, 1)

    def nickname(self) -> str:
        return "RandomAgent"
