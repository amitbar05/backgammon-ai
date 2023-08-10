from __future__ import annotations
from enum import Enum

import tensorflow as tf


class PlayerColor(Enum):
    WHITE = -1
    BLACK = 1

    def __str__(self) -> str:
        return 'B' if self == PlayerColor.BLACK else 'W'

    def opposite(self) -> PlayerColor:
        return PlayerColor(-self.value)

    def win_factor(self) -> tf.float32:
        return 1.0 if self == PlayerColor.BLACK else -1.0
