import numpy as np

from src.game.core.colors import PlayerColor
from src.game.core.game_state import GameState


class GameUtils:
    @staticmethod
    def extract_features(state: GameState, turn_color: PlayerColor = None) -> np.array:
        """ Return a representing vector of GameState"""
        vec = np.zeros(198)
        for point in state.board.points[1:25]:
            point_index = point.index - 1
            if point.count > 0:
                vec[(0 if point.player_color == PlayerColor.WHITE else 98) + point_index * 4] = 1
            else:
                continue
            if point.count > 1:
                vec[(1 if point.player_color == PlayerColor.WHITE else 99) + point_index * 4] = 1
            else:
                continue
            if point.count > 2:
                vec[(2 if point.player_color == PlayerColor.WHITE else 100) + point_index * 4] = 1
            else:
                continue
            if point.count > 3:
                value = (point.count - 3) / 2.0
                vec[(3 if point.player_color == PlayerColor.WHITE else 101) + point_index * 4] = value

        vec[96] = state.board.bar.count(PlayerColor.WHITE) / 2.0
        vec[97] = state.board.point(0).count / 15.0

        vec[194] = state.board.bar.count(PlayerColor.BLACK) / 2.0
        vec[195] = state.board.point(25).count / 15.0

        current_color = turn_color or state.turn_color
        if current_color == PlayerColor.WHITE:
            vec[196] = 1
        else:
            vec[197] = 1
        return vec
