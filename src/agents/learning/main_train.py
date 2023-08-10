from src.agents.learning.medium_network import q_network
from src.game.core.colors import PlayerColor
from trainer import Trainer
from src.agents.td_agent import TDAgent

N_EPISODES = 501

if __name__ == '__main__':
    # create the temporal difference agents
    black_agent = TDAgent(PlayerColor.BLACK)
    white_agent = TDAgent(PlayerColor.WHITE)

    driver = Trainer(q_network, black_agent, white_agent)
    driver.run(N_EPISODES)
