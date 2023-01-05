
import pygame as pg
from pygame.math import Vector2
from pygame.locals import *
import time
import os
import sys
from numpy import interp
from math import sin, radians, degrees, copysign
from ai_settings import *
from ai_particle import Particle


class Car():
    def __init__(self, win_screen, car_id, pos=(750.0, 960.0), angle=0.0, ai_train=True):
        super().__init__()
        # self.map = MAP_BORDER_SEMAFOR
        self.win_screen = win_screen
        self.car_id = car_id
        self.image = CAR_SPRITE.convert_alpha()
        self.rect = self.image.get_rect()
        self.position = Vector2(CAR_START_POS)
        self.vel = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = 1.0
        self.max_acc = 10.0
        self.max_steering = 90
        self.max_vel = 7
        self.brake_decel = 7
        self.free_decel = 2
        self.acc = 0.0
        self.steering = 0.0
        self.ppu = 26
        # NEAT AI data
        self.car_alive = True
        self.distance = 0.0
        self.progress_fovard = 0
        # rays section
        self.rays = Particle(self.win_screen, self.rect.center, (0, 210))
        # trafic light section
        self.trafic_event = 0
        self.trafic_enable_event = 0
        self.tl_completed = False
        self.trafic_light_flag = False
        self.trafic_time_bonus = 0
        # trein
        self.ai_train = ai_train
        self.d_action = [0, 0]
        self.turn_state = {'right': False, 'left': False, 'foward': False}
        self.visited_state = {'orange': False,
                              'magenta': False, 'green': False, 'yellow': False, 'fallow': False}
        self.p_number = 0
        self.direction_input = [0, 0]

    def reset(self):
        self.position = Vector2(CAR_START_POS)
        self.vel = pg.Vector2(0, 0)
        self.acc = 0.0
        self.angle = CAR_START_ANGLE

    def auto_drive_test(self, out, ai=True):
        if not ai:
            d_list = [out[pg.K_d], out[pg.K_a],
                      out[pg.K_w], out[pg.K_SPACE]]
            d_action = [1 if i else 0 for i in d_list]
            # print(d_list)
        else:
            d_action = out
        # control reset button, maybe needed
        # if d_action[4] > 0:
        #     d_action = [-1, -1, -1, -1, -1]

        if d_action[3] > 0:
            if abs(self.vel.x) > DT * self.brake_decel:
                self.acc = - \
                    copysign(self.brake_decel, self.vel.x)
            else:
                self.acc = -self.vel.x / DT

        elif d_action[2] > 0:
            if self.vel.x < 0:
                self.acc = self.brake_decel
            else:
                self.acc += 2 * DT
        else:
            if abs(self.vel.x) > DT * self.free_decel:
                self.acc = - \
                    copysign(self.free_decel, self.vel.x)
            # TODO: delete this part after adding second speed
            else:
                if DT != 0:
                    # pass
                    self.acc = -self.vel.x / DT
        self.acc = max(-self.max_acc,
                       min(self.acc, self.max_acc))

        # steering
        if d_action[1] > 0:
            if self.steering < 0:
                self.steering = 0
            self.steering += 60 * DT
        elif d_action[0] > 0:
            if self.steering > 0:
                self.steering = 0
            self.steering -= 60 * DT
        else:
            self.steering = 0
        self.steering = max(-self.max_steering,
                            min(self.steering, self.max_steering))

        # steering PROPORTIONAL
        def steer_interp(x):
            if x > 100:
                return 45
            else:
                return interp(x, [0.2, 100], [30, self.max_steering])

        # if d_action[0] >= 0.2:
        #     self.steering -= steer_interp(d_action[0]) * DT
        # elif d_action[1] >= 0.2:
        #     self.steering += steer_interp(d_action[1]) * DT
        # else:
        #     self.steering = 0
        # self.steering = max(-self.max_steering,
        #                     min(self.steering, self.max_steering))

    def auto_drive(self, out, ai=True):
        if not ai:
            d_list = [out[pg.K_d], out[pg.K_a],
                      out[pg.K_w], out[pg.K_SPACE]]
            d_action = [1 if i else 0 for i in d_list]
            # print(d_list)
        else:
            d_action = out
        # control reset button, maybe needed
        # if d_action[4] > 0:
        #     d_action = [-1, -1, -1, -1, -1]

        if d_action[3] > 0:
            if abs(self.vel.x) > DT * self.brake_decel:
                self.acc = - \
                    copysign(self.brake_decel, self.vel.x)
            else:
                self.acc = -self.vel.x / DT

        elif d_action[2] > 0:
            if self.vel.x < 0:
                self.acc = self.brake_decel
            else:
                self.acc += 2 * DT
        else:
            if abs(self.vel.x) > DT * self.free_decel:
                self.acc = - \
                    copysign(self.free_decel, self.vel.x)
            # TODO: delete this part after adding second speed
            else:
                if DT != 0:
                    # pass
                    self.acc = -self.vel.x / DT
        self.acc = max(-self.max_acc,
                       min(self.acc, self.max_acc))
        # steering
        if d_action[0] > 0:
            self.steering -= 45 * DT
        elif d_action[1] > 0:
            self.steering += 45 * DT
        else:
            self.steering = 0
        self.steering = max(-self.max_steering,
                            min(self.steering, self.max_steering))

    def update(self, dt):
        self.vel += (self.acc * dt * DEFAULT_SPEED, 0)
        self.vel.x = max(-self.max_vel,
                         min(self.vel.x, self.max_vel))
        # DEBUG:
        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            # turning_radius = -2
            angular_vel = self.vel.x / turning_radius
        else:
            angular_vel = 0

        self.position += self.vel.rotate(-self.angle) * dt * self.ppu
        self.angle += degrees(angular_vel) * dt
        self.rotated = pg.transform.rotate(self.image, self.angle)
        self.rect = self.rotated.get_rect()

        self.rays.update_pos(self.position, self.angle)
        # distance from car center, map, rays spred angles, angle between rays, color
        self.rays.send_rays(15, MAP_BORDER, (0, 189), 9, COLOR3)
        # self.rays.send_rays(13, MAP_BORDER, (0, 60), 15, COLOR3)
        # self.rays.send_rays(13, MAP_BORDER, (55, 130), 5, COLOR3)
        # self.rays.send_rays(13, MAP_BORDER, (135, 195), 15, COLOR3)

        self.rays.nn_input.append(self.direction_input[0])
        # input 0 to be trafic_light input
        self.rays.nn_input.append(0)
        self.rays.nn_input.append(0)
        # colision check and update car_alive status
        self.colision_check(self.position, self.angle, MAP_BORDER)

    def draw(self):
        if AI_TRAIN_SESSION:
            self.win_screen.blit(
                self.rotated, self.position - self.rect.center)

    def colision_check(self, pos, angle, map):
        hypo_len = 27  # The length of the hypotenuse to the corners of the car
        points = []  # saved corners (x, y)
        # order of corners: left_top, right_top, left_bottom, right_bottom
        for v in range(4):
            v = pg.Vector2(0, 0)
            points.append(v)
        # finad position of all car corners
        # left top 160
        points[0].from_polar((hypo_len, 360 - (angle + 200)))
        points[0] = pos - points[0]
        # right_top 200
        points[1].from_polar((hypo_len, 360 - (angle + 160)))
        points[1] = pos - points[1]
        # left_bottom 20
        points[2].from_polar((hypo_len, 360 - (angle + 340)))
        points[2] = pos - points[2]
        # left_bottom 340
        points[3].from_polar((hypo_len, 360 - (angle + 20)))
        points[3] = pos - points[3]

        # c_size = 2
        # pg.draw.circle(self.win_screen, (255, 0, 128),
        #                points[0], 7, width=c_size)
        # pg.draw.circle(self.win_screen, (255, 0, 128),
        #                points[1], 7, width=c_size)
        # pg.draw.circle(self.win_screen, (255, 0, 128),
        #                points[2], 7, width=c_size)
        # pg.draw.circle(self.win_screen, (255, 0, 128),
        #                points[3], 7, width=c_size)

        colided_points = [0, 0, 0, 0]  # colision results
        trafic_light_points = [0, 0, 0, 0]
        # print(f'LEN: {len(self.rays.nn_input)}')
        color = {
            # normal road color
            'white': (255, 255, 255),
            # road border
            'aqua': (0, 255, 255),
            # trafic light
            'red': (255, 0, 0),
            # end of tracif light
            'blue': (0, 0, 255),
            # ff00ff magenta - right turn
            'magenta': (255, 0, 255),
            # 00ff00 green - left turn
            'green': (0, 255, 0),
            # ffff00 yellow - no turn
            'yellow': (255, 255, 0),
            # ff6600 orange - triger color
            'orange': (255, 102, 0),
            # ff6600 fallow - triger color
            'fallow': (204, 153, 102)

        }
        self.rays.nn_input[INPUT_NUM - 1] = 0

        def left():
            self.rays.nn_input[INPUT_NUM - 3] = -500
            self.direction_input[0] = -500
            # self.rays.nn_input[INPUT_NUM - 3] = 150
            # self.direction_input[1] = 150
            self.turn_state['left'] = True
            self.turn_state['right'] = False

            # DEBUG:
            # print(f'LEFT - TURN STATE:')
            # print(self.turn_state)

        def right():
            self.rays.nn_input[INPUT_NUM - 3] = 500
            self.direction_input[0] = 500
            # self.rays.nn_input[INPUT_NUM - 3] = 0
            # self.direction_input[1] = 0
            self.turn_state['right'] = True
            self.turn_state['left'] = False
            # DEBUG:
            # print(f'RIGHT - TURN STATE:')
            # print(self.turn_state)

        def foward():
            self.rays.nn_input[INPUT_NUM - 3] = 0
            self.direction_input[0] = 0
            # self.rays.nn_input[INPUT_NUM - 3] = 0
            # self.direction_input[1] = 0
            self.turn_state['foward'] = True
            self.turn_state['right'] = False
            # DEBUG:
            # print(f'FOWARD - TURN STATE:')
            # print(self.turn_state)

            # DEBUG:
        def debug():
            print(f'Test pass through orange')
            print(f'FOWARD - TURN STATE:')
            print(self.turn_state)

        pass_number = {
            0: left,
            1: right,
            2: foward,
            3: debug,
            4: debug,
            5: debug,
            6: debug
        }
        # last NN input is semafor input if road below car is red
        for i, v in enumerate(points):
            road_color = map.get_at((int(v.x), int(v.y)))
            if road_color != color['white']:
                if road_color == color['aqua']:
                    colided_points[i] = 1
                elif road_color == (0, 0, 0):
                    colided_points[i] = 1
                elif road_color == color['red']:
                    trafic_light_points[i] = 1
                elif road_color == color['blue'] and not self.tl_completed:
                    colided_points[i] = 1

                # determining the direction of movement training based on the number of crossing the orange strip
                elif road_color == color['orange']:
                    if not self.visited_state['orange']:
                        self.visited_state['orange'] = True
                        pass_number[self.p_number]()
                        # DEBUG:
                        # print(f'VIS STATE: {self.visited_state}')
                        # print(f'P_number: {self.p_number}')

                elif road_color == color['magenta']:
                    if not self.turn_state['left']:
                        # DEBUG:
                        # print(f'COLISION WITH magenta')
                        colided_points[i] = 1

                    else:
                        if not self.visited_state['magenta']:
                            self.visited_state['magenta'] = True
                            self.visited_state['orange'] = False
                            self.p_number += 1
                            # DEBUG:
                            # print(f'VIS STATE: {self.visited_state}')

                elif road_color == color['fallow']:
                    if self.turn_state['right'] or self.turn_state['foward']:
                        # print(f'passing fallow')
                        pass
                    else:
                        colided_points[i] = 1
                        # print(f'hiting fallow')
                        pass

                elif road_color == color['green']:
                    if not self.turn_state['right']:
                        # DEBUG:
                        # print(f'COLISION WITH green')
                        colided_points[i] = 1
                    else:
                        if not self.visited_state['green']:
                            self.visited_state['green'] = True
                            self.visited_state['orange'] = False
                            self.p_number += 1
                            # DEBUG:
                            # print(f'VIS STATE: {self.visited_state}')

                elif road_color == color['yellow']:
                    if not self.turn_state['foward']:
                        # DEBUG:
                        # print(f'COLISION WITH yellow')
                        colided_points[i] = 1
                    else:
                        if not self.visited_state['yellow']:
                            self.visited_state['yellow'] = True
                            self.visited_state['orange'] = False
                            self.p_number += 1
                            # DEBUG:
                            # print(f'VIS STATE: {self.visited_state}')
                else:
                    pass  # for now

        if any(colided_points):
            self.car_alive = False
            self.vel = pg.Vector2(0, 0)
            self.acc = 0.0
        elif self.ai_train and all(trafic_light_points):
            if not self.tl_completed:
                # signal to car over last two NN input
                self.rays.nn_input[INPUT_NUM - 1] = 150
                self.rays.nn_input[INPUT_NUM - 2] = 150
                if not self.trafic_light_flag:
                    self.set_trafic_light_timer(3000)
        else:
            self.rays.nn_input[INPUT_NUM - 1] = 0
            self.rays.nn_input[INPUT_NUM - 2] = 0

    def set_car_dead(self):
        self.car_alive = False

    def get_car_alive(self):
        return self.car_alive

    # list of inputs in nural network
    def get_data(self):
        return self.rays.nn_input

    def get_reward(self, vel_x, max_reward):
        # Speed is rewarded, interpolate and proportionally reward a small amount.
        # Using the right side of the road is also rewarded in small amount

        # numpy interp function, faster then my fun
        def revard_rs(distance):
            return interp(distance, [-12, -3], [0, 0.2])

        def revard_n(x, max_vel, max_reward):
            return interp(x, [0, max_vel], [0, max_reward])

        def revard_h(x, max_vel, max_reward):
            # from 0 to max velocity map to 0 to max_revard
            return (float(x - 0) / float(max_vel)) * max_reward

        # primitive way to add/update distance car traveled
        if vel_x > 0:
            self.distance += (
                vel_x * (1 + round(revard_n(vel_x, self.max_vel, max_reward), 2))) / 12
         # primitive way to add/update distance car traveled
        # if vel_x > 0:
        #     self.distance += (
        #         vel_x * (1 + round(revard_n(vel_x, self.max_vel, max_reward), 2)
        #                  + round(revard_rs(self.rays.nn_input[INPUT_NUM - 3]), 2))) / 12
        # not used at moment, going backward is disabled
        elif vel_x < 0:
            self.distance += (
                vel_x * ((1 + round(revard_n(vel_x, self.max_vel, max_reward), 2)) * 1.7)) / 12
        # trafic stop revard bonus
        if self.trafic_light_flag and self.car_alive:
            time_addition = round(
                (time.time() - self.trafic_time_bonus) * 0.8, 2)
            self.distance += time_addition
        return self.distance

    def set_trafic_light_timer(self, delayMiliSeconds):
        self.trafic_light_flag = True
        self.trafic_time_bonus = time.time()
        # debug print(f'Trafic Light Flag SET: {self.car_id}')
        self.trafic_event = pg.USEREVENT + self.car_id
        pg.time.set_timer(self.trafic_event, delayMiliSeconds)

    def event_timer(self, event_list):
        # check for trafic light time and turn off timer
        if self.trafic_event in [e.type for e in event_list]:
            self.tl_completed = True
            pg.time.set_timer(self.trafic_event, 0)
            self.trafic_light_flag = False
            # self.trafic_time_bonus = 0
            # print(f'Trafic Light Flag REMOVED: {self.car_id}')
            # lower trafic_light_completed after 3 seconds so the car is ready
            # for new traffic light training
            # self.set_timer_trafic_enable()

    # def set_timer_trafic_enable(self):
    #     self.trafic_enable_event = pg.USEREVENT + (self.car_id + 1000)
    #     pg.time.set_timer(self.trafic_enable_event, 6000)

    # def event_timer_second(self, event_list):
    #     if self.trafic_enable_event in [e.type for e in event_list]:
    #         self.tl_completed = False
    #         pg.time.set_timer(self.trafic_enable_event, 0)


# Not used for now
class CarTrain:
    def __init__(self):
        pass

    def trafic_lights(self):
        pass
