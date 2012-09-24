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

INITIAL_ENERGY = 100
REPRODUCTION_ENERGY_THRESHOLD = 130
REPRODUCTION_COST = 30
CRITTER_ENERGY_DECAY_RATE = 0.2
FOOD_SPAWN_PERIOD = 50
FOOD_ENERGY = 50
CRITTER_VIEW_DISTANCE = 100
CRITTER_VIEW_DISTANCE_SQ = CRITTER_VIEW_DISTANCE**2
CRITTER_MAX_MOVE_SPEED = 0.5
REPRODUCTION_PERIOD = 120
COLLISION_RADIUS = 10
COLLISION_RADIUS_SQ = COLLISION_RADIUS**2
MEAN_TURN_INTERVAL = 10

WORLD_WIDTH = 640
WORLD_HEIGHT = 640
TILE_SIZE = 64

FRAMERATE = 50
ANIMATION_FRAME_INTERVAL = 8
CRITTER_VERTICAL_CENTER = 48
CRITTER_HORIZONTAL_CENTER = 16
FOOD_CENTER = 8



class World(object):
    def __init__(self, screen):
        
        # The simulation model has a toroidal topology (x and y co-ordinates
        # "wrap around"); we keep all x values in [0, width) and y values in
        # [0, height).
        
        # (0, 0) in the simulation model maps to the top-left corner,
        # positive y is down. Directions are given with positive being clockwise.
        self.screen = screen
        
        self.objects = []           
        for i in xrange(10):
            self.objects.append(Critter(self, len(self.objects),
                random.random()*WORLD_WIDTH, random.random()*WORLD_HEIGHT, 0, 
                            0, get_images())) # TODO: random counter_offset
            
        for i in xrange(10):
            self.objects.append(Food(self, len(self.objects), random.random()*WORLD_WIDTH,
                random.random()*WORLD_HEIGHT, FOOD_ENERGY))
    
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
            clock.tick(FRAMERATE)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                
            for x in xrange(0, WORLD_WIDTH, TILE_SIZE):
                for y in xrange(0, WORLD_HEIGHT, TILE_SIZE):
                    self.screen.blit(background, (x, y))
                    
            # Iterate over a copy of the object list since modifying a list
            # while iterating over it is verboten
            for obj in self.objects:
                obj.update()
            
            if counter % FOOD_SPAWN_PERIOD == 0:
                self.add(Food(self, 0, random.random()*WORLD_WIDTH,
                              random.random()*WORLD_HEIGHT, FOOD_ENERGY))

            for obj in self.objects:
                obj.render(self.screen)
                
            pygame.display.flip()
                
            counter += 1    

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
    World(screen).run()
