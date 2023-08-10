from src.game.core.colors import PlayerColor

# ------ Time ------
AGENT_MOVE_DELAY_IN_SECS = 0.5
WHITE_NO_POSSIBLE_MOVE_IN_SECS = 0.5

# ------ Images ------
BOARD_IMG_PATH = 'src/game/graphics/images/board.png'
ROLL_IMG_PATH = 'src/game/graphics/images/roll_button.png'
CUBES_IMG_PATH = [f'src/game/graphics/images/die{i}.png' for i in range(1, 7)]
CHECKER_IMG_PATH = {
    PlayerColor.WHITE: 'src/game/graphics/images/checker-white.png',
    PlayerColor.BLACK: 'src/game/graphics/images/checker-black.png'
}
HIGHLIGHTED_CHECKER_IMG_PATH = {
    PlayerColor.WHITE: 'src/game/graphics/images/checker-white-highlight.png',
    PlayerColor.BLACK: 'src/game/graphics/images/checker-black.png'
}

# ------ Screen size ------
SCREEN_WIDTH, SCREEN_HEIGHT = 869, 597

# ------ Screen elements positions ------
# Dice
DICE_HEIGHT_POS = 265
DICE_WIDTH_POS = {
    PlayerColor.WHITE: 547,
    PlayerColor.BLACK: 180,
}
# Bar
BAR_WIDTH_POS = 413
BAR_HEIGHT_POS = {
    PlayerColor.WHITE: 300,
    PlayerColor.BLACK: 260
}
# Points
HIGH_POINT_HEIGHT_POS = 15
LOW_POINT_HEIGHT_POS = 544
POINT_13_WIDTH_POS = 83
POINT_19_WIDTH_POS = 453
POINT_25_WIDTH_POS = 15
POINT_12_WIDTH_POS = 83
POINT_6_WIDTH_POS = 453
POINT_0_WIDTH_POS = 810
# Elements position for collisions
POINT_13_LEFT_TOP = (77, HIGH_POINT_HEIGHT_POS)
POINT_19_LEFT_TOP = (446, HIGH_POINT_HEIGHT_POS)
POINT_12_LEFT_TOP = (77, 321)
POINT_6_LEFT_TOP = (447, 321)
POINT_0_LEFT_TOP = (811, 321)
BAR_LEFT_TOP = (410, 301)

# ------ Checker's stack offsets ------
STACK_HEIGHT_LARGE_OFFSET = 40
STACK_HEIGHT_MEDIUM_OFFSET = 25
STACK_HEIGHT_SMALL_OFFSET = 15

# ------ Point size ------
POINT_WIDTH = 58
POINT_HEIGHT = 260

# ------ Misc ------
CHECKER_WIDTH_POS_OFFSET = 58
