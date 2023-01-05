import pygame as pg
from ai_settings import *
from pygame.locals import *


class Particle:
    def __init__(self, win_screen, ray_angle, pos):
        self.car_angle = 0
        self.rays = []
        self.pos = pg.Vector2(pos)
        self.w, self.h = pg.display.get_surface().get_size()
        self.r_angle = ray_angle  # tuple
        self.nn_input = [0 for i in range(INPUT_NUM)]
        # self.nn_input = []
        self.rect_offset = []
        self.win_screen = win_screen
        self.rays_display = AI_DISPLAY_RAYS

    # TODO to delete
    def mouse_press(self, event):
        """For debugging purposes, a method that allows moving the window while
        the Particle object is connected to the mass position"""
        self.shortcuts = {
            (K_w): 'self.update_pos(pg.mouse.get_pos())',
            (K_SPACE): 'self.update_pos(pg.mouse.get_pos())                    '
        }
        if event:
            k = event.key
            if k in self.shortcuts:
                exec(self.shortcuts[k])

    def update_pos(self, pos, car_angle):
        # update position to mouse pos
        self.pos = pg.Vector2(pos)
        # connect the particle angle with the car angle
        self.car_angle = car_angle
        # reset input array (list of distances)
        # self.nn_input.clear()
        self.nn_input = []

    def send_rays(self, hypo_len, map, field_of_view, step, color):

        start_vec = pg.Vector2(0, 0)
        # start_vec.from_polar((hypo_len, 360 - (angle - self.car_angle)))
        start_vec.from_polar((hypo_len, 360 - (self.car_angle - 180)))
        start_vec = self.pos - start_vec
        ray_pos = start_vec

        for i in range(field_of_view[0], field_of_view[1], step):
            self.nn_input.append(self.calculate_ray(i, ray_pos, map, color))

    def calculate_ray(self, angle, pos, map, color):
        """The rays were calculated using a simple search at the start with
        jumps (pjump=40 pixels), and then a binary search at the end after
        reaching green sufrace. The search uses the pygame method map.get_at(x, y)
        which returns the color RGBA pixels value on the defined map."""
        # translate from pygame coordinate to local
        # because vector work is done on pygame origin (0, 0)
        def trans_vec(x): return pos - x

        # check pixel color on map in function, it is more redable
        def map_check(x): return map.get_at(
            (int(end_vec.x), int(end_vec.y))) == x
        def map_check_not_equal(x): return map.get_at(
            (int(end_vec.x), int(end_vec.y))) != x

        max_size = RAY_LENGTH
        pjump = RAY_JUMP_LENGTH
        ray_vec = pg.Vector2(0, 1).rotate(angle - self.car_angle)
        distance = 0
        done = False
        while not done:
            end_vec = trans_vec(ray_vec)
            if map_check(COLOR2) and distance == 0:
                done = True
                end_vec = trans_vec(ray_vec)
                # ad ray value to input list
                self.draw_line(pos, end_vec)
                return distance
            else:
                if (map_check_not_equal(COLOR2) and map_check_not_equal(COLOR3)) and distance < max_size:
                    # if map_check(COLOR1) and distance < max_size:
                    distance += pjump
                    ray_vec.scale_to_length(int(distance))
                elif map_check(COLOR2):

                    pjump = pjump / 2
                    distance -= pjump
                    ray_vec.scale_to_length(int(distance))
                    end_vec = trans_vec(ray_vec)
                    while True:
                        if map.get_at((int(end_vec.x), int(end_vec.y))) != color:
                            if map_check(COLOR2):
                                pjump = pjump / 2
                                if pjump < 1:
                                    done = True
                                    return 0
                                    break
                                distance -= pjump
                                ray_vec.scale_to_length(int(distance))
                                end_vec = trans_vec(ray_vec)
                            # elif map_check(COLOR1):
                            elif map_check_not_equal(COLOR2) and map_check_not_equal(COLOR3):
                                pjump = pjump / 2
                                distance += pjump
                                if pjump < 1:
                                    done = True
                                    return 0
                                    break
                                ray_vec.scale_to_length(int(distance))
                                end_vec = trans_vec(ray_vec)
                        else:
                            end_vec = trans_vec(ray_vec)
                            # ad ray value to input list
                            self.draw_line(pos, end_vec)
                            done = True
                            return distance
                            break
                else:
                    done = True
                    end_vec = trans_vec(ray_vec)
                    # ad ray value to input list
                    self.draw_line(pos, end_vec)
                    return distance

    def draw_line(self, start, coord, raycolor=(255, 204, 0)):
        if AI_TRAIN_SESSION and AI_DISPLAY_RAYS:
            pg.draw.line(self.win_screen, raycolor, start, coord, 1)
