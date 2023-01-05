
import pygame as pg
import os

WINDOW = (1720, 1040)
DEFAULT_SPEED = 1
RAY_LENGTH = 230
RAY_JUMP_LENGTH = 25
DRAW_RAYS = True
KEEP_DIRECTION = True
CAR_START_POS = (1370.0, 280.0)
CAR_START_ANGLE = 180
# CAR_START_POS = (1095.0, 110.0)
INPUT_NUM = 24
AI_TRAIN_SESSION = True
AI_DISPLAY_RAYS = True
# map colors - ROAD, GRASS, DISTANCE LINE

# COLOR1 = (255, 255, 255, 255)   # ROAD
# COLOR2 = (100, 116, 55, 255)    # GRASS
# COLOR3 = (226, 40, 29, 255)     # DISTANCE LINE
COLOR4 = (255, 204, 0)          # RAYS COLOR
COLOR5 = (102, 204, 255)        # DIRECTION RAY COLOR

COLOR1 = (255, 255, 255, 255)   # ROAD
COLOR2 = (0, 0, 0, 255)         # GRASS
COLOR3 = (0, 255, 255, 255)     # DISTANCE LINE

# road_map_sense_test_drive.png

C_DIR = os.path.dirname(os.path.abspath(__file__))

# MAP_BORDER = pg.image.load(os.path.join(
#     C_DIR, "ai_images", "road_map_sense_test_drive.png"))

MAP_BORDER = pg.image.load(os.path.join(
    C_DIR, "ai_images", "set_road_train6.png"))
# MAP_BORDER_SEMAFOR = pg.image.load(os.path.join(
#     C_DIR, "ai_images", "set_road_train6.png"))

# MAP_BORDER = pg.image.load(os.path.join(
#     C_DIR, "ai_images", "road_map_sense_TEST.png"))
# MAP_BORDER_SEMAFOR = pg.image.load(os.path.join(
#     C_DIR, "ai_images", "road_map_sense_TEST.png"))

MAP_VIEW = pg.image.load(os.path.join(
    C_DIR, "ai_images", "set_road_train6_view.png"))
CAR_SPRITE = pg.image.load(os.path.join(
    C_DIR, "ai_images", "small_ai_car.png"))

DT = 0.016  # fixed DT during training is a better option due to possible skipping of frames
