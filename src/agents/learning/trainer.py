import time

import numpy as np
import os

from src.agents.agent import Agent
from src.agents.learning.game_manager import GameManager
from src.agents.learning.replay_buffer import ReplayBuffer
from src.game.backgammon_cli import NoDisplay, CliDisplay
from src.game.core.utils import GameUtils
import tensorflow as tf

WEIGHTS_CHECKPOINT_FILE = 'src/agents/learning/checkpoints/weights_v2'


class Trainer:
    def __init__(self, model, black_agent: Agent, white_agent: Agent):

        self.model = model
        # Restore the weights
        if os.path.exists(WEIGHTS_CHECKPOINT_FILE + ".index"):
            self.model.load_weights(WEIGHTS_CHECKPOINT_FILE)
            print("Weights restored")
        else:
            print("No weights found, starting from scratch")
            print(os.getcwd())
            # print(os.listdir(path='./checkpoints'))

        # Create the game manager
        self.replay_buffer = ReplayBuffer()
        white_nickname = white_agent.nickname()
        black_nickname = black_agent.nickname()
        self.black_policy = black_agent.get_collect_policy(black_nickname, self.replay_buffer)
        self.white_policy = white_agent.get_collect_policy(white_nickname, self.replay_buffer)
        self.display = NoDisplay()
        self.cli_display = CliDisplay(white_nickname, black_nickname)
        self.env = GameManager(self.white_policy, self.black_policy)
        self.env.init_evaluation_state()

    def print_initial_state_scores(self, print_state=False):
        """Print the score of the starting board"""
        if print_state:
            white_init_state = self.env.get_eval_state_and_display("white_init")
        else:
            white_init_state = self.env.get_eval_state("white_init")
        print(f"White score on initial board:{self.model.get_score(white_init_state)}\n")
        if print_state:
            black_init_state = self.env.get_eval_state_and_display("black_init")
        else:
            black_init_state = self.env.get_eval_state("black_init")
        print(f"Black score on initial board:{self.model.get_score(black_init_state)}\n")

    def eval_chosen_states(self, print_state=False):
        if print_state:
            state1 = self.env.get_eval_state_and_display("eval_board1")
        else:
            state1 = self.env.get_eval_state("eval_board1")
        print("Little advantage to white, prediction should be [-1,0]")
        print(f"prediction is: {self.model.get_score(state1)}\n")

        # little advantage to white, prediction should be [-1,0] closer to 0
        if print_state:
            state2 = self.env.get_eval_state_and_display("eval_board2")
        else:
            state2 = self.env.get_eval_state("eval_board2")
        print("Little advantage to white, prediction should be [-1,0] closer to 0")
        print(f"prediction is: {self.model.get_score(state2)}\n")

        # little advantage to black, prediction should be [0,1]
        if print_state:
            state3 = self.env.get_eval_state_and_display("eval_board3")
        else:
            state3 = self.env.get_eval_state("eval_board3")
        print("Little advantage to black, prediction should be [0,1]")
        print(f"prediction is: {self.model.get_score(state3)}\n")

        # black has an advantage, prediction should be 1.
        if print_state:
            state4 = self.env.get_eval_state_and_display("eval_board4")
        else:
            state4 = self.env.get_eval_state("eval_board4")
        print("Black has an advantage, prediction should be 1.")
        print(f"prediction is: {self.model.get_score(state4)}\n")

        # should be huge advantage to white, so prediction should be close to -2
        if print_state:
            state5 = self.env.get_eval_state_and_display("eval_board5")
        else:
            state5 = self.env.get_eval_state("eval_board5")
        print("Should be huge advantage to white, so prediction should be close to -2")
        print(f"prediction is: {self.model.get_score(state5)}\n")

    def evaluate_model(self, print_state=False):
        """Evaluate the model on specific cases"""
        print("------------------------------------------Evaluating current model:-------------------------------------------")
        self.print_initial_state_scores(print_state)
        self.eval_chosen_states(print_state)
        print("------------------------------------------End eval:-------------------------------------------")

    def collect_experience(self):
        """Play an entire game and return reward"""
        n_of_plays = self.env.play_episode()
        print(f"it took {n_of_plays} plays ")
        return self.env.get_reward()

    def train_on_initial(self):
        # train on initial state to normalize and smooth the function approximation
        white_init_vec = GameUtils.extract_features(self.env.get_eval_state("white_init"))
        white_init_vec = np.reshape(white_init_vec, (1, -1))
        black_init_vec = GameUtils.extract_features(self.env.get_eval_state("black_init"))
        black_init_vec = np.reshape(black_init_vec, (1, -1))
        white_result = tf.constant(-0.01, dtype=tf.float32, shape=(1, 1), name="white_reward")
        black_result = tf.constant(0.01, dtype=tf.float32, shape=(1, 1), name="black_reward")
        self.model.train_on_specific_state(white_init_vec, white_result)
        self.model.train_on_specific_state(black_init_vec, black_result)

    def train_an_episode(self, episode):
        start_time = time.time()
        # play game and fill replay buffer
        winner, reward = self.collect_experience()
        print("Finished the episode, with the reward", reward)
        tensor_reward = tf.constant(float(reward), dtype=tf.float32, shape=(1, 1), name="reward")
        play_time = time.time() - start_time
        print(f"Finished playing episode {episode}, it took {play_time / 60} minutes")
        # train the model
        self.model.train(self.replay_buffer, tensor_reward, winner)  # train model on replay buffer
        # Save the weights
        self.model.save_weights(WEIGHTS_CHECKPOINT_FILE)
        # reset game and replay buffer
        self.reset()

    def run(self, n_episodes: int):
        """Run the training process"""
        for episode in range(n_episodes):
            if episode % 5 == 0:
                # evaluate model
                self.evaluate_model()
                # to normalize and smooth the function approximation
                # self.train_on_initial()
            print("\nstarting episode", episode)
            self.train_an_episode(episode)
            


    def reset(self):
        self.replay_buffer.reset()  # reset replay buffer for both agents
