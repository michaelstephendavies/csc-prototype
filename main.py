from __future__ import division

import os, sys
import pygame
from pygame.locals import *
from math import *
import random
random.seed()

#imports from our own files
from images import *
from objects import *

class Config:
    def __init__(self, filename):
        conf_file = open(filename)
        lines = conf_file.readlines()
        self.initial_energy = float(lines[0].split()[2])
        self.reproduction_energy_threshold = float(lines[1].split()[2])
        self.reproduction_cost = float(lines[2].split()[2])
        self.critter_energy_decay_rate = float(lines[3].split()[2])
        self.food_spawn_period = float(lines[4].split()[2])
        self.food_energy = float(lines[5].split()[2])
        self.critter_view_distance = float(lines[6].split()[2])
        self.critter_view_distance_sq = self.critter_view_distance**2
        self.critter_max_move_speed = float(lines[7].split()[2])
        self.reproduction_period = float(lines[8].split()[2])
        self.collision_radius = float(lines[9].split()[2])
        self.collision_radius_sq = self.collision_radius**2
        self.mean_turn_interval = float(lines[10].split()[2])
        self.world_width = int(lines[11].split()[2])
        self.world_height = int(lines[12].split()[2])
        self.tile_size = int(lines[13].split()[2])
        self.framerate = int(lines[14].split()[2])
        self.animation_frame_interval = int(lines[15].split()[2])
        self.critter_vertical_center = int(lines[16].split()[2])
        self.critter_horizontal_center = int(lines[17].split()[2])
        self.food_center = int(lines[18].split()[2])
    
    

class World(object):
    def __init__(self, screen, config):
        
        # The simulation model has a toroidal topology (x and y co-ordinates
        # "wrap around"); we keep all x values in [0, width) and y values in
        # [0, height).
        
        # (0, 0) in the simulation model maps to the top-left corner,
        # positive y is down. Directions are given with positive being clockwise.
        self.screen = screen
        self.config = config
        
        self.objects = []           
        for i in xrange(10):
            self.objects.append(Critter(config, self, len(self.objects),
                random.random()*self.config.world_width, random.random()
                    *self.config.world_height, 0, 
                            0, get_man_images())) # TODO: random counter_offset
            
        for i in xrange(10):
            self.objects.append(Food(config, self, len(self.objects), random.random()*self.config.world_width,
                random.random()*self.config.world_height, self.config.food_energy))
    
    def delete(self, obj):
        obj.kill()        
        self.objects.remove(obj)

    def add(self, new_obj):
        self.objects.append(new_obj)
    
    def run(self):
        counter = 0
        
        background = get_background_image()
        
        while True:
            clock = pygame.time.Clock()
            clock.tick(self.config.framerate)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                
            for x in xrange(0, self.config.world_width, self.config.tile_size):
                for y in xrange(0, self.config.world_height, self.config.tile_size):
                    self.screen.blit(background, (x, y))
                    
            # Iterate over a copy of the object list since modifying a list
            # while iterating over it is verboten
            for obj in self.objects:
                obj.update()
            
            if counter % self.config.food_spawn_period == 0:
                self.add(Food(config, self, 0, random.random()*self.config.world_width,
                              random.random()*self.config.world_height, self.config.food_energy))

            for obj in self.objects:
                obj.render(self.screen)
                
            pygame.display.flip()
                
            counter += 1    

if __name__ == '__main__':
    config = Config(sys.argv[1])
    pygame.init()
    screen = pygame.display.set_mode((config.world_width, config.world_height))
    World(screen, config).run()
