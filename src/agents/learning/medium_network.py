# model parameters
from src.agents.learning.q_network import QNetwork

N_INPUTS = 198  # the size of the input vector (using Gerald Tesauro specification)
N_HIDDEN_LAYERS_SUB = 10
N_NEURONS_HIGH = 64
N_NEURONS_LOW = 32

# create the model
# [64] * 10 + [32] * 10
HIDDEN_LAYERS_SHAPE = [N_NEURONS_HIGH] * N_HIDDEN_LAYERS_SUB + [N_NEURONS_LOW] * N_HIDDEN_LAYERS_SUB
q_network = QNetwork(N_INPUTS, HIDDEN_LAYERS_SHAPE, 1)
