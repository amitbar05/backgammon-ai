import sys

from src.game.core.board import Board
from src.game.core.colors import PlayerColor


class HeuristicEvaluator:
    """
    Terminology:
    * Blot - A single checker sitting alone on a point where it is vulnerable to being hit.
    * Hit - To move to a point occupied by an opposing blot and put the blot on the bar.
    * Block - A point occupied by two or more checkers of the same color.
    * Blockade - A series of blocks arranged to prevent escape of the opponent's runners.
    * Prime - Several consecutive blocks
    * Anchor - A block in the opponent's home board.
    """

    def __init__(self, color: PlayerColor):
        self.color = color
        self.opponent = color.opposite()
        self.quadrants = None

    def evaluate(self, board: Board) -> float:
        self._fill_quadrants(board)

        return sum(feature * weight for feature, weight in [
            (self._vulnerability_score(board), 0.4),
            (self._hitting_score(board), 0.4),
            (self._blocking_score(board), 0.4),
            (self._running_score(board), 0.2),
            (self._bear_in_score(board), 0.2),
            (self._bear_off_score(board), 0.2),
            (self._terminal_state_score(board), 1),
        ])

    def _vulnerability_score(self, board: Board) -> float:
        """ Minimize the amount of blots, based on quadrants."""
        score = sum([self._count_blots(self.quadrants[i]) * (4-i) for i in range(0, 4)])
        return 1 - self._normalize(score, 0, 15)

    def _terminal_state_score(self, board: Board) -> float:
        """ Evaluates a terminal state """
        if board.goal_point(self.color).count == 15:
            return float('inf')
        elif board.goal_point(self.opponent).count == 15:
            return float('-inf')
        else:
            return 0

    def _running_score(self, board: Board) -> float:
        """ Evaluates a terminal state """
        if board.points_locations[self.color]:
            furthest_idx = board.get_furthest_point_idx(self.color)
            score = furthest_idx if self.color == PlayerColor.WHITE else 25 - furthest_idx
            return 1 - self._normalize(score, 0, 24)
        else:
            return 1

    def _hitting_score(self, board: Board) -> float:
        """ Maximize the amount of the eaten opponent's checkers """
        score = board.bar.count(self.opponent)
        return self._normalize(score, 0, 15)

    def _blocking_score(self, board: Board) -> float:
        """ Maximize the amount of blocks, based on quadrants (consider anchors). """
        score = sum([self._count_blocks(self.quadrants[i]) * (4-i) for i in range(0, 4)])  # TODO: consider anchors
        return self._normalize(score, 0, 27)

    def _bear_in_score(self, board: Board):
        """ Maximize the amount of checkers inside home board"""
        score = sum([1 for point in self.quadrants[0] + [board.goal_point(self.color)] if point.player_color == self.color])
        return self._normalize(score, 0, 15)

    def _bear_off_score(self, board: Board):
        """ Maximize the amount of checkers inside home board"""
        score = board.goal_point(self.color).count
        return self._normalize(score, 0, 15)

    def _fill_quadrants(self, board: Board):
        self.quadrants = [
            board.points[1:6+1],
            board.points[7:12+1],
            board.points[13:18+1],
            board.points[19:24+1],
        ]
        if self.color == PlayerColor.BLACK:
            self.quadrants.reverse()

    def _count_blocks(self, points):
        return sum([1 for point in points if point.player_color == self.color and point.count > 1])

    def _count_blots(self, points):
        return sum([1 for point in points if point.player_color == self.color and point.count == 1])

    @staticmethod
    def _normalize(x: float, x_min: float, x_max: float) -> float:
        """
        Normalization is a scaling technique in which values are shifted and rescaled so that they end up ranging between 0 and 1.
        It is also known as Min-Max scaling.
        :param x: the actual feature value.
        :param x_max: the maximum possible value of the feature.
        :param x_min: the minimum possible value of the feature.
        :return: A number between 0 and 1.
        """
        return (x - x_min) / (x_max - x_min)

