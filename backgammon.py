from __future__ import annotations

from src.agents.closer_agent import CloserAgent
from src.agents.eater_agent import HitterAgent
from src.agents.expectimax_agent import ExpectimaxAgent
from src.agents.heuristics.heuristic import HeuristicEvaluator
from src.agents.td_agent import TDAgent
from src.game.backgammon_cli import BackgammonCLI
from src.game.core.colors import PlayerColor
from src.game.core.human_player import HumanPlayer
from src.agents.random_agent import RandomAgent
from src.game.core.player import Player
import argparse
from argparse import ArgumentParser
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # disable pygame welcome message in console
from src.game.backgammon_gui import BackgammonGUI


displays = ['gui', 'cli', 'none']
players = ['human', 'random-agent', 'expectimax-agent', 'learning-agent', 'hitter-agent', 'closer-agent']


def create_player(player_type: str, color: PlayerColor) -> Player:
    if player_type == 'human':
        return HumanPlayer()
    elif player_type == 'random-agent':
        return RandomAgent(color)
    elif player_type == 'hitter-agent':
        return HitterAgent(color)
    elif player_type == 'closer-agent':
        return CloserAgent(color)
    elif player_type == 'expectimax-agent':
        return ExpectimaxAgent(color,
                               heuristic_function=HeuristicEvaluator(color).evaluate,
                               max_depth=1,
                               dice_sample_size=10,
                               )
    elif player_type == 'learning-agent':
        return TDAgent(color)
    else:
        raise Exception(f"Invalid player type {player_type}, see usage.")


def parse_args() -> argparse.Namespace:
    parser = ArgumentParser()
    parser.add_argument('--display', help='The display type to use.', choices=displays, default=displays[1], type=str)
    parser.add_argument('--white', help='The white player.', choices=players, default=players[0], type=str)
    parser.add_argument('--black', help='The black player.', choices=players, default=players[1], type=str)
    parser.add_argument('--num_of_games', help='The number of games to run.', default=1, type=int)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    white_player = create_player(args.white, PlayerColor.WHITE)
    black_player = create_player(args.black, PlayerColor.BLACK)

    if args.display == 'gui':
        assert args.num_of_games == 1, "The GUI runs a single game only."
        assert args.black != "human", "Black cannot be a human player in GUI mode"
        game = BackgammonGUI(white_player, black_player)
        game.run()

    else:  # cli
        silent_mode = args.display == 'none'
        game = BackgammonCLI(white_player, black_player, silent_mode)
        game.run(args.num_of_games)
