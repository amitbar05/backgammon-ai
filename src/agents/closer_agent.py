from src.agents.agent import Agent
from src.game.core.colors import PlayerColor
from src.game.core.game_state import GameState


class CloserAgent(Agent):
    def __init__(self, color: PlayerColor):
        super().__init__(color)

    def evaluation_function(self, state: GameState):
        return sum(1 for point in state.board.points if point.count > 1 and point.player_color == self.color)

    def nickname(self) -> str:
        return "CloserAgent"
