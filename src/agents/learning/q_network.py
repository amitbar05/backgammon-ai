import numpy as np
import tensorflow as tf
from tensorflow import keras

from src.game.core.colors import PlayerColor
from src.game.core.game_state import GameState
from src.game.core.utils import GameUtils

# for numerical stability (is 1e-6, for safery 1e-5)
FLOAT32_DELTA = 1e-5


class QNetwork(tf.keras.Model):

    def __init__(self, n_inputs, hidden_layers_size, n_output):
        """
        n_inputs - the size of the input vector
        hidden_layers_size - the size of the hidden layers
        n_output - the size of the output vector
        base_rate - initial base used for calculating the decay factor of the gradient
        base_rate - decay rate used for calculating the decay factor of the gradient

        for example if the parameters are 100, [16, 32], 4 the NN will contain:
        input_layer - 100 units
        layer1 - 16 units
        layer2 - 32 units
        output - 4 units
        """
        super().__init__()
        input_layer = keras.layers.InputLayer(input_shape=n_inputs)
        dense_layers = [self.create_hidden_layer(units) for units in hidden_layers_size]
        output_layer = keras.layers.Dense(n_output, )
        network_layers = [input_layer] + dense_layers + [output_layer]
        self.model = keras.Sequential(network_layers)

        self.model.compile(
            optimizer=tf.keras.optimizers.SGD(learning_rate=0.0001),
            loss=keras.losses.MSE)


    @staticmethod
    def create_hidden_layer(num_neurons):
        return keras.layers.Dense(num_neurons, activation="relu")

    @staticmethod
    def decayed_array_alternative(base_rate=0.4, decay_rate=0.94, decay_steps=64) -> tf.float32:
        """

        :param base_rate:
        :param decay_rate:
        :param decay_steps: the number of decayed contansts needed
        :return: a list with [decay_steps] numbers such that they are elements in the reverse geometric series

        for example:
        would return [b*q^(n-1), ..., b*q^2, b*q, b]
        when n is the decay steps, and q is the decay rate, and b is the base rate
        """
        decay_factors = [base_rate * decay_rate ** (decay_steps - i) for i in range(1, decay_steps + 1)]
        numeric_stable_factors = [f if f > FLOAT32_DELTA else FLOAT32_DELTA for f in decay_factors]
        return tf.constant(numeric_stable_factors, dtype=tf.float32)

    @staticmethod
    def get_decayed_array(n_moves, turn_factors):
        part_1 = np.geomspace(start=FLOAT32_DELTA, stop=0.17, num=n_moves - 3)
        part_2 = np.geomspace(start=0.2, stop=0.5, num=3)
        decay_factor = np.append(part_1, part_2)
        return decay_factor * turn_factors

    def train(self, replay_buffer, result, winner: PlayerColor) -> None:
        """
        :param replay_buffer: a list that contains the moves made during the game (states after each move)
        :param result: the game result represented the same format as the prediction
        :param winner: color of the winner of the game
        :return:
        """
        n_moves = len(replay_buffer)
        print(f"n_moves: {n_moves}")
        turn_factors = replay_buffer.get_turns_factors(winner)
        decay_factors = QNetwork.get_decayed_array(n_moves, turn_factors)
        trainable_variables = self.model.trainable_variables
        # create a list with all game gradients
        for step_count, state_features in enumerate(replay_buffer):
            with tf.GradientTape() as tape:
                prediction = self.model(state_features)
                loss = self.model.compiled_loss(result, prediction)  # MSE
            gradient = tape.gradient(loss, trainable_variables)

            decayed_gradient = [g * decay_factors[step_count] for g in gradient]
            self.model.optimizer.apply_gradients(zip(decayed_gradient, trainable_variables))

    def train_on_specific_state(self, state_features, result):
        with tf.GradientTape() as tape:
            prediction = self.model(state_features)
            loss = self.model.compiled_loss(result, prediction)  # MSE
        trainable_variables = self.model.trainable_variables
        gradient = tape.gradient(loss, trainable_variables)
        self.model.optimizer.apply_gradients(zip(gradient, trainable_variables))

    def get_score(self, game_state: GameState) -> int:
        # here we need the board representation as described by Gerald Tesauro (198 vec)
        input_vec = GameUtils.extract_features(game_state)
        sample = np.reshape(input_vec, (1, -1))
        return self.model(sample)
