import numpy as np

from src.game.core.colors import PlayerColor


class ReplayBuffer:
    """
    Replay buffer to store experience tuples.
    """
    def __init__(self, buffer_size=200):
        self.buffer = []
        self.turn_buffer = []
        self.buffer_size = buffer_size
        self.count = 0

    def add(self, experience: np.ndarray, turn: PlayerColor) -> None:
        """
        Add experience to the buffer.
        """
        if self.count < self.buffer_size:
            #experience = vec, turn
            self.buffer.append(experience)
            self.turn_buffer.append(turn)
            self.count += 1
        else:
            self.buffer.pop(0)
            self.turn_buffer.pop(0)
            self.buffer.append(experience)
            self.turn_buffer.append(turn)

    def reset(self):
        self.buffer = []
        self.turn_buffer = []
        self.count = 0

    def get_turns_factors(self, winner: PlayerColor) -> np.ndarray:
        """
        Return a list of factors for the turns in the buffer.
        """
        turn_factors = np.ones(self.count)
        for index, turn in enumerate(self.turn_buffer):
            if turn != winner:
                turn_factors[index] = 0.5
        return turn_factors

    def __len__(self):
        """
        Return the current size of internal memory.
        """
        return self.count

    def __iter__(self):
        return iter(self.buffer)
