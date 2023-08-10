
# AI Final Project: Backgammon

![826790654_A_dream_of_2_advanced_robots_play_chess_by_Thomas_Moran__octane_render](https://user-images.githubusercontent.com/13821119/187332206-1ff2af0f-6fc8-4fe3-8c46-6f15aeae5762.png)

## Usage
`python3 backgammon.py --display <display_type> --white <player> --black <player> --num_of_games <int>`
use `python3 backgammon.py --help` for documentation.

**Default Settings**: Human vs. Human, CLI Display.\
**Display types**: `cli` / `none` / `gui`
**Players**: `human` / `random-agent` / `expectimax-agent` / 

### Prerequisites
Run with python 3.7 (university computer version)

### Usage Example
first install the dependencies (we recommend using a virtual environment, but it's the user's consideration) using pip, or with the script `install.sh`.
Please run `export PYTHONPATH=$PYTHONPATH:$(pwd)` when in this directory for the import paths to work properly.

Example command to play vs. a human in the CLI:
`python3 backgammon.py --display cli --white human --black random-agent`
