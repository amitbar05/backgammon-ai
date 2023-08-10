import sys
import time
import random
from copy import copy
from typing import Dict, List, Union, Tuple

import pygame
from pygame.sprite import Sprite
from pygame.surface import Surface
from pygame.time import Clock

from src.game.core.human_player import HumanPlayer
from src.game.core.move import Move
from src.game.graphics.graphic_config import *
from src.game.core.colors import PlayerColor
from src.game.core.game_state import GameState
from src.game.core.player import Player


class BackgammonGUI:
    def __init__(self, white: Player, black: Player):
        pygame.init()
        pygame.display.set_caption("Backgammon")
        starting_player = random.choice([PlayerColor.WHITE, PlayerColor.BLACK])
        self.game_state = GameState(starting_player)
        self.screen: Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock: Clock = pygame.time.Clock()
        self.board_sprite = BoardSprite(self.screen, self.game_state)
        self.dice_sprite = DiceSprite(self.screen, self.game_state)
        self.white, self.black = white, black

    def run(self) -> None:
        self.game_state.dice.roll()
        self._game_loop()
        print(f"Winner: {self.white.nickname() if self.game_state.get_winner() == PlayerColor.WHITE else self.black.nickname()}")
        pygame.quit()

    def _game_loop(self):
        source_point: Union[int, None] = None  # The point from which the user wants to move a checker
        dice_rolls_count: int = 0  # Used for dice rolling animation
        dice_rolling_process: bool = True

        while not self.game_state.is_game_ended():
            event = pygame.event.poll()

            # When the user wants to quit
            if event.type == pygame.QUIT:
                sys.exit()

            # During dice rolling animation
            if dice_rolling_process:
                self.game_state.dice.roll()
                dice_rolls_count += 1
                if dice_rolls_count == 30:
                    dice_rolling_process = False
                    dice_rolls_count = 0

            # When it's the opponent's turn
            elif self.game_state.turn_color == PlayerColor.BLACK:
                if not self.game_state.dice.is_depleted() and self.game_state.possible_moves:
                    time.sleep(AGENT_MOVE_DELAY_IN_SECS)
                    move = self.black.choose_move(copy(self.game_state), self.game_state.possible_moves)
                    self.game_state.apply_move(move)
                else:
                    self.game_state.switch_turns()
                    dice_rolling_process = True

            # When the user has no more moves to do, switch turns
            elif self.game_state.dice.is_depleted() or not self.game_state.possible_moves:
                time.sleep(WHITE_NO_POSSIBLE_MOVE_IN_SECS)
                self.game_state.switch_turns()
                dice_rolling_process = True

            elif type(self.white) != HumanPlayer:
                if not self.game_state.dice.is_depleted() and self.game_state.possible_moves:
                    time.sleep(AGENT_MOVE_DELAY_IN_SECS)
                    move = self.white.choose_move(copy(self.game_state), self.game_state.possible_moves)
                    self.game_state.apply_move(move)
                else:
                    self.game_state.switch_turns()
                    dice_rolling_process = True

            # When the user selects a checker to move -> store the source point
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = event.dict["pos"]
                source_point = self.board_sprite.get_selected_source_point(click_pos)
                self.board_sprite.source_point_idx = source_point

            # When the user drags the selected checker -> update the checker's position
            elif source_point and event.type == pygame.MOUSEMOTION:
                click_pos = event.dict["pos"]
                self.board_sprite.pressed_checker_pos = click_pos

            # When the user lands the selected checker on a target point -> apply the user's move using source,
            elif source_point and event.type == pygame.MOUSEBUTTONUP:
                click_pos = event.dict["pos"]
                target_point = self.board_sprite.get_selected_target_point(click_pos)
                move = None if target_point is None else self._get_user_move_from_possible_moves(source_point, target_point)
                if move:
                    self.game_state.apply_move(move)
                self.board_sprite.reset_checker_selection()
                source_point = None

            self.clock.tick(60)
            self._draw_sprites()
            pygame.display.update()

    def _get_user_move_from_possible_moves(self, source, target) -> Union[Move, None]:
        for move in self.game_state.possible_moves:
            if move.src == source and move.dest == target:
                return move

    def _draw_sprites(self):
        self.board_sprite.draw()
        self.dice_sprite.draw()


class BoardSprite(Sprite):
    def __init__(self, surface: Surface, initial_state: GameState):
        super().__init__()
        self.surface: Surface = surface
        self.board_img = pygame.image.load(BOARD_IMG_PATH).convert()
        self.checkers_img = {
            PlayerColor.WHITE: pygame.image.load(CHECKER_IMG_PATH[PlayerColor.WHITE]),
            PlayerColor.BLACK: pygame.image.load(CHECKER_IMG_PATH[PlayerColor.BLACK])
        }
        self.highlight_checkers_img = {
            PlayerColor.WHITE: pygame.image.load(HIGHLIGHTED_CHECKER_IMG_PATH[PlayerColor.WHITE]),
            PlayerColor.BLACK: pygame.image.load(HIGHLIGHTED_CHECKER_IMG_PATH[PlayerColor.BLACK])
        }
        self.points_positions = BoardSprite._calculate_points_positions()
        self.game_state: GameState = initial_state
        self.source_point_idx = None  # for movement animation
        self.pressed_checker_pos = None  # for movement animation

    def draw(self):
        self.surface.blit(self.board_img, (0, 0))
        self._draw_points()
        self._draw_bar()

    def get_selected_source_point(self, position) -> Union[None, int]:
        bar = self.game_state.board.bar
        if bar.contains(PlayerColor.WHITE):
            bar_rect = self.calculate_bar_rect()
            return Move.BAR_INDEX if bar_rect.collidepoint(position) else None
        else:
            source_point_rects = self._calculate_points_rects()
            for i in set(self.game_state.board.points_locations[PlayerColor.WHITE]) - {0, 25}:
                if source_point_rects[i].collidepoint(position) and\
                        i != self.game_state.board.goal_point_idx(PlayerColor.WHITE):
                    return i

    def get_selected_target_point(self, position) -> Union[None, int]:
        target_point_rects = self._calculate_points_rects()
        for i in range(0, 25):
            if target_point_rects[i].collidepoint(position):
                return i

    def reset_checker_selection(self):
        self.source_point_idx = None
        self.pressed_checker_pos = None

    def _draw_bar(self):
        bar = self.game_state.board.bar
        for color in [PlayerColor.WHITE, PlayerColor.BLACK]:
            if bar.contains(color):
                height_offset = 0
                amount = bar.count(color)
                offset = STACK_HEIGHT_MEDIUM_OFFSET if amount <= 6 else STACK_HEIGHT_SMALL_OFFSET
                direction = 1 if color == PlayerColor.WHITE else -1
                for i in range(0, amount-1):
                    self.surface.blit(self.checkers_img[color],
                                      (BAR_WIDTH_POS, BAR_HEIGHT_POS[color] + direction * height_offset))
                    height_offset += offset
                if self.source_point_idx == Move.BAR_INDEX:
                    self.surface.blit(self.highlight_checkers_img[color], self.pressed_checker_pos or (BAR_WIDTH_POS, BAR_HEIGHT_POS[color] + direction * height_offset))
                else:
                    self.surface.blit(self.checkers_img[color],
                                      (BAR_WIDTH_POS, BAR_HEIGHT_POS[color] + direction * height_offset))

    def _draw_points(self):
        for i in range(0, 26):
            point = self.game_state.board.point(i)
            if point.player_color is not None:
                self._draw_point(i, point.player_color, point.count)

    def _draw_point(self, index: int, color: PlayerColor, count: int):
        width, height = self.points_positions[index]
        height_offset = 0
        offset = self._calculate_height_offset(count, index)
        stack_direction = 1 if 13 <= index <= 25 else -1
        for i in range(0, count-1):
            self.surface.blit(self.checkers_img[color], (width, height + stack_direction * height_offset))
            height_offset += offset
        if self.source_point_idx == index:
            self.surface.blit(self.highlight_checkers_img[color], self.pressed_checker_pos or (width, height + stack_direction * height_offset))
        else:
            self.surface.blit(self.checkers_img[color], (width, height + stack_direction * height_offset))

    @staticmethod
    def _calculate_height_offset(count, index) -> int:
        if index != 0 and index != 25:
            offset = STACK_HEIGHT_SMALL_OFFSET if count >= 11 else \
                STACK_HEIGHT_MEDIUM_OFFSET if count >= 8 else STACK_HEIGHT_LARGE_OFFSET
        else:
            offset = STACK_HEIGHT_SMALL_OFFSET if count >= 6 else STACK_HEIGHT_LARGE_OFFSET
        return offset

    @staticmethod
    def _calculate_points_positions() -> List[Tuple[int, int]]:
        def helper(base_width_pos: int, height_pos, start, end, jump):
            width_offset = 0
            for i in range(start, end, jump):
                positions[i] = (base_width_pos + width_offset, height_pos)
                width_offset += CHECKER_WIDTH_POS_OFFSET

        positions = [(0, 0) for _ in range(0, 26)]

        helper(POINT_12_WIDTH_POS, LOW_POINT_HEIGHT_POS, 12, 6, -1)
        helper(POINT_6_WIDTH_POS, LOW_POINT_HEIGHT_POS, 6, 0, -1)
        helper(POINT_13_WIDTH_POS, HIGH_POINT_HEIGHT_POS, 13, 19, 1)
        helper(POINT_19_WIDTH_POS, HIGH_POINT_HEIGHT_POS, 19, 25, 1)

        positions[0] = (POINT_0_WIDTH_POS, LOW_POINT_HEIGHT_POS)
        positions[25] = (POINT_25_WIDTH_POS, HIGH_POINT_HEIGHT_POS)

        return positions

    @staticmethod
    def _calculate_points_rects() -> Dict[int, pygame.Rect]:
        def helper(left, top, start, end, jump=1):
            for i in range(start, end, jump):
                rects[i] = pygame.Rect(left, top, POINT_WIDTH, POINT_HEIGHT)
                left += POINT_WIDTH

        rects = dict()
        helper(*POINT_13_LEFT_TOP, 13, 19)
        helper(*POINT_19_LEFT_TOP, 19, 25)
        helper(*POINT_12_LEFT_TOP, 12, 6, -1)
        helper(*POINT_6_LEFT_TOP, 6, 0, -1)
        helper(*POINT_0_LEFT_TOP, 0, 1)
        return rects

    @staticmethod
    def calculate_bar_rect() -> pygame.Rect:
        return pygame.Rect(*BAR_LEFT_TOP, CHECKER_WIDTH_POS_OFFSET, 300)


class DiceSprite(Sprite):
    def __init__(self, surface: Surface, initial_state: GameState):
        super().__init__()
        self.surface = surface
        self.state = initial_state
        self.cubes_img = [pygame.image.load(CUBES_IMG_PATH[i]) for i in range(0, 6)]

    def draw(self):
        if self.state.dice.value:
            color = self.state.turn_color
            a, b = self.state.dice.value
            self.surface.blit(self.cubes_img[a-1], (DICE_WIDTH_POS[color], DICE_HEIGHT_POS))
            self.surface.blit(self.cubes_img[b-1], (DICE_WIDTH_POS[color] + 80, DICE_HEIGHT_POS))
