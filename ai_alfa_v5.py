import neat
import pygame as pg
from pygame.math import Vector2
from pygame.locals import *
import os
import sys
from math import sin, radians, degrees, copysign
from numpy import interp
from random import randint, uniform
import pickle
from ai_settings import *
from ai_car import Car
from ai_font import TextFont
import ai_visualize as vis


class Ai_Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Car training using NEAT Ai")
        width, height = WINDOW
        self.win_screen = pg.display.set_mode((width, height))
        self.generation = 0
        self.remain_cars = 0
        self.fitness_a = {}  # value of fitnes taken for tracking cars that are not moving
        self.FPS = 80
        # DEBUG:
        self.car_show = False
        self.input_show = False

    def checking_movment(self, cars, movement_treshold):
        for car in cars:
            if car.get_car_alive():
                if abs(car.distance - self.fitness_a[car.car_id]) <= movement_treshold \
                        and car.trafic_light_flag == False:
                    car.set_car_dead()
                    self.remain_cars -= 1
                elif car.distance <= self.fitness_a[car.car_id]:
                    car.set_car_dead()
                    self.remain_cars -= 1

        self.accumulate_fitness(cars)

    def accumulate_fitness(self, cars):  # accumulate fitness in dictionary d
        self.fitness_a = {}
        for i, car in enumerate(cars):
            if car.get_car_alive():
                # extract distance (fitness) and save with cars ID for later
                self.fitness_a[car.car_id] = car.distance

    def run(self, genomes, config):
        # cars must maintain a certain speed to stay alive, time_delsta over distance
        time_delay = 4000
        distance_threshold = 10
        no_move_rule = pg.USEREVENT + 1
        pg.time.set_timer(no_move_rule, time_delay)
        networks = []
        cars = []
        DONE = False
        # initialize genomes / generation population defined in config file
        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            networks.append(net)
            genome.fitness = 0
            # initialize cars and append them in list
            auto = Car(self.win_screen, genome_id, angle=CAR_START_ANGLE)
            cars.append(auto)
            # self.car_group.add(auto)

        self.accumulate_fitness(cars)

        clock = pg.time.Clock()

        self.screen_tx = TextFont(18)
        self.generation += 1
        while True:
            for index, car in enumerate(cars):
                out = networks[index].activate(car.get_data())
                # current controls
                car.auto_drive_test(out)
                # if self.input_show:
                #     if car.car_id == 20998:
                #         print(
                #             f'Car ID: {car.car_id} L: {out[0]}, R: {out[1]}')
                #     pass
                # if car.car_id == 46:
                # print(out)
                # car.auto_drive_test(out, 0)

            # draw screen
            self.win_screen.blit(MAP_VIEW, (0, 0))

            event_list = pg.event.get()
            for event in event_list:
                if event.type == pg.QUIT:
                    DONE = True
                    sys.exit(0)
                elif event.type == no_move_rule:
                    self.checking_movment(cars, distance_threshold)
                elif event.type == pg.KEYDOWN and event.key == pg.K_p:
                    if not self.car_show:
                        self.car_show = True
                    else:
                        self.car_show = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_i:
                    if not self.input_show:
                        self.input_show = True
                    else:
                        self.input_show = False

            self.remain_cars = 0
            for i, car in enumerate(cars):
                if car.get_car_alive():
                    self.remain_cars += 1
                    car.update(DT)
                    genomes[i][1].fitness = car.get_reward(car.vel.x, 0.6)
                    # drawing
                    if self.car_show:
                        car.draw()
                    if self.input_show:
                        print(
                            f'NN dir. input, Car ID: {car.car_id} {car.rays.nn_input[INPUT_NUM - 3]}')
                    # event checking
                    car.event_timer(event_list)

            if self.remain_cars == 0:
                print('NO ONE LEFT ALIVE!')
                break
            # SMALL INFORMATION BOX
            # TODO: change to something better
            self.screen_tx.draw_text_box(
                self.win_screen, (680, 680, 230, 75), (255, 255, 255), 60, 8)
            self.screen_tx.draw_text(
                self.win_screen, f'REMAINING CARS: {self.remain_cars}', (690, 720))

            pg.display.flip()
            clock.tick(self.FPS)


class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Human driving / Car training using NEAT Ai")
        width, height = WINDOW
        self.win_screen = pg.display.set_mode((width, height))
        screen_width, screen_height = pg.display.get_surface().get_size()
        self.map_image = MAP_VIEW
        self.clock = pg.time.Clock()
        self.FPS = 120
        Game.exit = False
        self.screen_tx = TextFont(18)

    def run(self):

        car = Car(self.win_screen, 101, angle=CAR_START_ANGLE)
        while not self.exit:
            # self.screen.fill((0, 0, 0))
            self.win_screen.blit(MAP_BORDER, (0, 0))
            # dt = self.clock.get_time() / 1000
            # NOTE: Fixed value DT during AI training due to possible
            # preformance problems and frame skipping
            DT = 0.016
            # Event queue
            event_list = pg.event.get()
            for event in event_list:
                event_holder = event
                # pressed = pg.key.get_pressed()
                pressed = pg.key.get_pressed()
                if event.type == pg.QUIT:
                    self.exit = True
                elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    # self.exit = True
                    event_holder = event
                    car.reset()
                    car.distance = 0
            # print(
            #     f'NN: {car.rays.nn_input[INPUT_NUM - 4]}, {car.rays.nn_input[INPUT_NUM - 3]}')
            # NOTE: this input turnd off in new waz to move
            # car.auto_drive(pressed, ai=False)
            car.auto_drive_test(pressed, ai=False)
            # logic
            car.update(DT)
            # drawing
            car.draw()
            # checking events like trafic light
            # car.event_timer_second(event_list)
            car.event_timer(event_list)
            revard = car.get_reward(car.vel.x, 0.6)
            self.screen_tx.draw_text_box(
                self.win_screen, (850, 680, 300, 75), (255, 255, 255), 60, 8)
            self.screen_tx.draw_text(
                self.win_screen, f'DISTANCE: {round(revard, 1)}', (880, 695))
            self.screen_tx.draw_text(
                self.win_screen, f'SPEED: {round(car.vel.x, 1)}', (880, 720))
            # DEBUG: display input data
            # print(self.car.rays.nn_input)
            pg.display.flip()
            self.clock.tick(self.FPS)
        pg.quit()


# if __name__ == '__main__':
#     game = Game()
#     game.run()


if __name__ == "__main__":
    # Set configuration file
    # config_path = "./config-feedforward.txt"
    config_path = os.path.join(C_DIR, 'config-feedforward')
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation, config_path)

    # Core evolution algorithm class
    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-1594')
    # p = neat.Population(config)

    # Add reporter for fancy statistical result
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(15))

    # Run NEAT
    train_ob = Ai_Game()
    # p.run(net_run, 1000)
    winner = p.run(train_ob.run, 1700)

    with open('winner-feedforward', 'wb') as f:
        pickle.dump(winner, f)

    print(winner)
    vis.plot_stats(stats, ylog=True, view=False,
                   filename="feedforward-fitness.svg")
    vis.plot_species(
        stats, view=False, filename="feedforward-speciation.svg")

    node_names = {}
    for i in range(5, -1, -1):
        print(i)
        node_names[i] = f'out{i}'

    for i in range(-1, -48, -1):
        node_names[i] = f'in{abs(i)}'

    vis.draw_net(config, winner, view=False, node_names=node_names)

    vis.draw_net(config, winner, view=False,
                 filename="winner-feedforward.gv")
    # vis.draw_net(config, winner, view=False, node_names=node_names,
    #              filename="winner-feedforward-enabled-pruned.gv", prune_unused=True)
