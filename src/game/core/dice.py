from __future__ import annotations

import itertools
from typing import List
from copy import copy

import numpy


class Dice:
    TOTAL_COMBINATIONS = 36

    def __init__(self, value: List[int, int] = None) -> None:
        self.__value: List[int, int] = value or []
        self.__remaining_steps: list = []
        self.__rng = numpy.random.default_rng()

    def __copy__(self):
        copy_dice = Dice()
        copy_dice.__value = self.__value.copy()
        copy_dice.__remaining_steps = self.remaining_steps.copy()
        return copy_dice

    def __str__(self) -> str:
        return f"Dice: {self.value}"

    @property
    def value(self) -> list[int]:
        return self.__value

    @property
    def remaining_steps(self) -> list[int]:
        return self.__remaining_steps

    def roll(self, outcome: List[int] = None) -> None:
        result = outcome or self.__rng.integers(1, 7, size=2).tolist()
        self.__value = copy(result)
        self.__remaining_steps = [result[0]] * 4 if result[0] == result[1] else result

    def use_move(self, steps: int) -> None:
        self.__remaining_steps.remove(steps)

    def is_depleted(self) -> bool:
        return len(self.__remaining_steps) == 0

    @staticmethod
    def get_all_combinations() -> List[List[int]]:
        return [list(combination) for combination in itertools.product(range(1, 7), range(1, 7))]

    @staticmethod
    def get_possible_rolls_excluding_doubles() -> List[List[int]]:
        return [list(combination) for combination in itertools.combinations(range(1, 7), 2)]

    @staticmethod
    def get_possible_doubles() -> List[List[int]]:
        return [[i, i] for i in range(1, 7)]
