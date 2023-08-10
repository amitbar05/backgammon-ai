from collections import defaultdict
from typing import Dict, List, Tuple
from src.game.core.colors import PlayerColor
from src.game.core.game_state import GameState


class HeuristicEvaluator:
    def __init__(self):
        self.white_blots_quadrant: dict = defaultdict(int)
        self.black_blots_quadrant: dict = defaultdict(int)
        # small house 2 checkers
        self.white_small_houses_quadrant: dict = defaultdict(int)
        self.black_small_houses_quadrant: dict = defaultdict(int)
        # medium house 3 checkers
        self.white_medium_houses_quadrant: dict = defaultdict(int)
        self.black_medium_houses_quadrant: dict = defaultdict(int)
        # big house >3 checkers
        self.white_big_houses_quadrant: dict = defaultdict(int)
        self.black_big_houses_quadrant: dict = defaultdict(int)

        self.quadrant_ranges = {1: (0, 6), 2: (6, 12), 3: (12, 18), 4: (18, 24)}

    # TODO maybe add penalty in case of no possible moves for current player.
    def evaluate(self,
                 game_state: GameState,
                 small_house_factors=[0.5, 0.6, 0.75, 0.9],
                 medium_houses_factors=[0.6, 0.7, 0.8, 1],
                 big_houses_factors=[0.3, 0.4, 0.5, 0.8],
                 blots_factor=[0.2524, 0.6, 0.8, 2],
                 bar_factor=3.5,
                 bear_off_factor=3,  # keep this factor low to prefer better moves and postpone bearing off.
                 color_turn_factor=1,
                 monotonicity_factor=0.03,
                 blocks_factor=2
                 ) -> int:
        player_color = game_state.turn_color
        # factors
        black_small_house_factors = small_house_factors
        white_small_houses_factors = list(reversed(black_small_house_factors))
        black_medium_houses_factors = medium_houses_factors
        white_medium_houses_factors = list(reversed(black_medium_houses_factors))
        black_big_houses_factors = big_houses_factors
        white_big_houses_factors = list(reversed(black_big_houses_factors))
        black_blots_factor = blots_factor
        white_blots_factor = list(reversed(black_blots_factor))

        for quadrant_number in range(1, 5):
            # fill all quadrants
            self._fill_board_quadrant(game_state, quadrant_number)

        # create sums of all white houses multiplied by a descending factor
        white_small_houses_sum = HeuristicEvaluator._houses_sum(self.white_small_houses_quadrant, white_small_houses_factors)
        white_medium_houses_sum = HeuristicEvaluator._houses_sum(self.white_medium_houses_quadrant, white_medium_houses_factors)
        white_big_houses_sum = HeuristicEvaluator._houses_sum(self.white_big_houses_quadrant, white_big_houses_factors)
        white_blots_penalty = HeuristicEvaluator._blots_penalty(self.white_blots_quadrant, white_blots_factor)

        # create sums of all black houses multiplied by a ascending factor
        black_small_houses_sum = HeuristicEvaluator._houses_sum(self.black_small_houses_quadrant, black_small_house_factors)
        black_medium_houses_sum = HeuristicEvaluator._houses_sum(self.black_medium_houses_quadrant, black_medium_houses_factors)
        black_big_houses_sum = HeuristicEvaluator._houses_sum(self.black_big_houses_quadrant, black_big_houses_factors)
        black_blots_penalty = HeuristicEvaluator._blots_penalty(self.black_blots_quadrant, black_blots_factor)

        # save bar and bear off values
        white_bar = game_state.board.bar.count(PlayerColor.WHITE)
        white_bear_off = game_state.board.point(0).count
        black_bar = game_state.board.bar.count(PlayerColor.BLACK)
        black_bear_off = game_state.board.point(25).count

        # calculate bar and bear off weighted values
        white_bar_penalty = -(bar_factor * white_bar)
        white_bear_off_sum = bear_off_factor * white_bear_off
        black_bar_penalty = -(bar_factor * black_bar)
        black_bear_off_sum = bear_off_factor * black_bear_off

        # calculate turn bonus
        white_bonus, black_bonus = self._turn_bonus(player_color, color_turn_factor)

        # calc mono and blocks bonuses
        white_monotonicity_bonus, black_monotonicity_bonus, white_blocks_bonus, black_blocks_bonus = HeuristicEvaluator._monotonicity_and_blocks(game_state)
        white_monotonicity_sum = monotonicity_factor * white_monotonicity_bonus
        black_monotonicity_sum = monotonicity_factor * black_monotonicity_bonus
        white_blocks_sum = blocks_factor * white_blocks_bonus
        black_blocks_sum = blocks_factor * black_blocks_bonus

        # calc white final score
        white_houses_sum = white_big_houses_sum + white_medium_houses_sum + white_small_houses_sum
        white_final_score = white_houses_sum + white_blots_penalty + white_bar_penalty + white_bear_off_sum + white_bonus + white_monotonicity_sum + white_blocks_sum

        # calc black score
        black_houses_sum = black_big_houses_sum + black_medium_houses_sum + black_small_houses_sum
        black_final_score = black_houses_sum + black_blots_penalty + black_bar_penalty + black_bear_off_sum + black_bonus + black_monotonicity_sum + black_blocks_sum

        # calc final score
        sum_score = PlayerColor.WHITE.win_factor() * white_final_score + PlayerColor.BLACK.win_factor() * black_final_score
        return sum_score

    def _fill_board_quadrant(self, game_state: GameState, quadrant_number: int):
        start, end = self.quadrant_ranges[quadrant_number]
        quadrant = game_state.board.points[start+1:end+1]
        for point in quadrant:
            if point.player_color == PlayerColor.WHITE:
                if point.count == 1:
                    self.white_blots_quadrant[quadrant_number] += 1
                elif point.count == 2:
                    self.white_small_houses_quadrant[quadrant_number] += 1
                elif point.count == 3:
                    self.white_medium_houses_quadrant[quadrant_number] += 1
                elif point.count > 3:
                    self.white_big_houses_quadrant[quadrant_number] += 1
            else:
                # black
                if point.count == 1:
                    self.black_blots_quadrant[quadrant_number] += 1
                elif point.count == 2:
                    self.black_small_houses_quadrant[quadrant_number] += 1
                elif point.count == 3:
                    self.black_medium_houses_quadrant[quadrant_number] += 1
                elif point.count > 3:
                    self.black_big_houses_quadrant[quadrant_number] += 1

    @staticmethod
    def _monotonicity_and_blocks(game_state) -> Tuple[int, int, int, int]:
        white_monotonicity_bonus = 0
        black_monotonicity_bonus = 0

        white_blocks_bonus = 0
        black_blocks_bonus = 0
        white_streak = 0
        black_streak = 0

        for i, point in enumerate(game_state.board.points[1:25]):
            index = i + 1
            if point.player_color == PlayerColor.WHITE:
                white_monotonicity_bonus += (25-index) * point.count
                if point.count > 2:
                    white_streak += 1
                    if white_streak >= 4:
                        white_blocks_bonus += 1
                else:
                    white_streak = 0
            else:
                black_monotonicity_bonus += index * point.count
                if point.count > 2:
                    black_streak += 1
                    if black_streak >= 4:
                        black_blocks_bonus += 1
        return white_monotonicity_bonus, black_monotonicity_bonus, white_blocks_bonus, black_blocks_bonus

    @staticmethod
    def _houses_sum(houses_quadrant: Dict, factors: List[int]):
        return sum(factors[i] * houses_quadrant[i + 1] for i in range(4))

    @staticmethod
    def _blots_penalty(blots_quadrant: Dict, factors: List[int]):
        return -sum(factors[i] * blots_quadrant[i + 1] for i in range(4))

    @staticmethod
    def _turn_bonus(color_turn, color_turn_factor):
        if color_turn == PlayerColor.WHITE:
            white_bonus = color_turn_factor
            black_bonus = 0
        else:
            white_bonus = 0
            black_bonus = color_turn_factor
        return white_bonus, black_bonus
