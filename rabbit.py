from __future__ import division

#from visual import *
import os, sys
import pygame
from pygame.locals import *
from math import *
import random
random.seed()

INITIAL_ENERGY = 100
REPRODUCTION_ENERGY_THRESHOLD = 130
REPRODUCTION_COST = 30
CRITTER_ENERGY_DECAY_RATE = 0.2
FOOD_SPAWN_PERIOD = 50
FOOD_ENERGY = 50
FLOOR_COLOUR = (0.2, 1, 0.2)
FOOD_COLOUR = (0, 0.5, 0)
CRITTER_COLOUR = (1, 0, 0)
CRITTER_VIEW_DISTANCE = 100
CRITTER_VIEW_DISTANCE_SQ = CRITTER_VIEW_DISTANCE**2
CRITTER_MAX_MOVE_SPEED = 0.5
REPRODUCTION_PERIOD = 120
COLLISION_RADIUS = 50
COLLISION_RADIUS_SQ = COLLISION_RADIUS**2
FRAMERATE = 50
ANIMATION_MOVE_INTERVAL = 8
MEAN_TURN_INTERVAL = 10
CRITTER_VERTICAL_CENTER = 48
CRITTER_HORIZONTAL_CENTER = 16

class World(object):
    def __init__(self, width, height, screen):
        
        # A note on co-ordinate systems.
        # The simulation model has two co-ordinate axes, whereas
        # VPython has three co-ordinate axes.
        
        # We map a simulation point (x, y) to the VPython point (x, z, y)
        # where z is some arbitrary level above the "floor" of the world which
        # depends on the specific kind of object.
        
        # The simulation model has a toroidal topology (x and y co-ordinates
        # "wrap around"); we keep all x values in [0, width) and y values in
        # [0, height).
        self.width = width
        self.height = height
        self.objects = []
        self.screen = screen
        boy_south1 = pygame.image.load('boy_south_walk1.png').convert()
        boy_south2 = pygame.image.load('boy_south_walk2.png').convert()
        boy_north1 = pygame.image.load('boy_north_walk1.png').convert()
        boy_north2 = pygame.image.load('boy_north_walk2.png').convert()
        boy_east1 = pygame.image.load('boy_east_walk1.png').convert()
        boy_east2 = pygame.image.load('boy_east_walk2.png').convert()
        boy_west1 = pygame.image.load('boy_west_walk1.png').convert()
        boy_west2 = pygame.image.load('boy_west_walk2.png').convert()
        for i in xrange(10):
            self.objects.append(Critter(self, len(self.objects),
                random.random()*(width-2)+1, random.random()*(height-2)+1, (3*pi)/2, 
                            screen, 0, CRITTER_HORIZONTAL_CENTER, CRITTER_VERTICAL_CENTER,
                            boy_south1, boy_south2, boy_north1, boy_north2, 
                            boy_east1, boy_east2, boy_west1, boy_west2))
        #for i in xrange(5):
        #    self.objects.append(Critter(self, len(self.objects),
        #        random.random()*(width-2)+1, random.random()*(height-2), random.random()*2*pi))
            
        for i in xrange(10):
            self.objects.append(Food(self, len(self.objects), random.random()*(width-2)+1,
                random.random()*(height-2)+1, FOOD_ENERGY, 8, 8, self.screen))

    def delete(self, obj):
        obj.kill()        
        self.objects.remove(obj)

    def add(self, new_obj):
        new_obj.show()
        self.objects.append(new_obj)
    
    def run(self):
        # Create the floor
        #box(pos = (self.width/2, 0, self.height/2), length = self.width, height = 0.5,
        #    width = self.height, color = FLOOR_COLOUR)
        
        # Reposition the camera so it is looking at the center of the world
        #scene.center = (self.width/2, 0, self.height/2)
        
        for obj in self.objects:
            obj.show()

        counter = 0
        
        
        background = pygame.image.load('tile_grass.png').convert()
        
        
        while True:
            clock = pygame.time.Clock()
            clock.tick(FRAMERATE)
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
            for i in range(10):
                for j in range(10):
                    self.screen.blit(background, (i*64, j*64))
            # Iterate over a copy of the object list since modifying a list
            # while iterating over it is problematic
            for obj in self.objects:
                obj.update()
            if counter % FOOD_SPAWN_PERIOD == 0:
                self.add(Food(self, 0, random.random()*(self.width-2)+1,
                              random.random()*(self.height-2)+1, FOOD_ENERGY, 8, 8, self.screen))
            pygame.display.flip()
            
                
            counter += 1
            
            #rate(SIMULATION_RATE)      

class Object(object):
    """ Abstract base class for simulation objects.
    
    In addition to overriding show, kill and update, all Objects
    must have the following attributes:
    object_ID - unique identifier for the object
    x, y - current simulation co-ordinates of the object
    world - reference to the containing World"""
    
    def __init__(self):
        raise NotImplementedError("Override in your subclass")
    
    def show(self):
        """ Called when the object first becomes visible. """
        raise NotImplementedError("Override in your subclass")
    
    def kill(self):
        """ Called when the object is destroyed. """
        raise NotImplementedError("Override in your subclass")
    
    def update(self):
        """ Called once every simulation step. """
        raise NotImplementedError("Override in your subclass")
    
    def distance_sq(self, other):
        """ Find the square of the distance between this Object and
        another Object. """

        # Since the world wraps around, it's not just a straight Euclidean
        # distance. We find the shorter x distance (either going across the
        # world in the normal way, or wrapping around the left/right edge).
        # Then we do the same for the y, then use these in the Euclidean
        # distance formula.
        dx = min(abs(self.calc_x - other.calc_x), self.world.width - abs(self.calc_x - other.calc_x))
        dy = min(abs(self.calc_y - other.calc_y), self.world.height - abs(self.calc_y - other.calc_y))
        
        return dx**2 + dy**2  


class Food(Object):
    def __init__(self, world, object_ID, x, y, contained_energy, horizontal_offset
                 , vertical_offset, screen):
        self.world = world
        self.object_ID = object_ID
        self.x = x
        self.y = y
        self.energy = contained_energy
        self.horizontal_offset = horizontal_offset
        self.vertical_offset = vertical_offset
        self.screen = screen
        self.food_image = pygame.image.load('small_food_bush.png').convert_alpha()
        self.calc_x = self.x + self.horizontal_offset
        self.calc_y = self.y + self.vertical_offset
        
    def show(self):
        screen.blit(self.food_image, (self.x, self.y))
        #self.representation = sphere(pos = (self.x, 0.75, self.y),
                 #                    radius = 0.5, color = FOOD_COLOUR)

    def kill(self):
        pass
        #self.representation.visible = False
    
    def update(self):
        self.screen.blit(self.food_image, (self.x, self.y))


class Critter(Object):
        def __init__(self, world, object_ID, x, y, direction, 
                     screen, counter_offset, horizontal_offset,
                     vertical_offset, 
                     img_south1, img_south2, 
                     img_north1, img_north2, 
                     img_east1, img_east2,
                     img_west1, img_west2):
            self.world = world
            self.object_ID = object_ID
            self.x = x
            self.y = y
            self.direction = direction
            self.energy = INITIAL_ENERGY
            self.iteration_counter = counter_offset
            self.horizontal_offset = horizontal_offset
            self.vertical_offset = vertical_offset
            self.agent = Agent()
            self.img_south1 = img_south1
            self.img_south2 = img_south2
            self.img_north1 = img_north1
            self.img_north2 = img_north2
            self.img_east1 = img_east1
            self.img_east2 = img_east2
            self.img_west1 = img_west1
            self.img_west2 = img_west2
            # counter to know when to change the animation
            # given offset so that critters do not move in 
            # unison. 
            self.calc_x = self.x + self.horizontal_offset
            self.calc_y = self.y + self.vertical_offset
            

        def show(self):
            pass
            #self.representation = cone(pos = (self.x, 0.75, self.y),
             #   axis = (1, 0, 0), radius = 0.5, color = CRITTER_COLOUR)

        def kill(self):
            pass
            #self.representation.visible = False
        
        def update(self):
            # Find all objects close enough to be visible to the agent;
            # tag each along with its delta-x and delta-y values relative
            # to this object
            self.calc_x = self.x + self.horizontal_offset
            self.calc_y = self.y + self.vertical_offset
            visible_objects = []
            for obj in self.world.objects:
                if obj != self:
                    # There's two different ways to get from self.x to obj.x:
                    # directly, or around the left/right edge. We calculate
                    # both of these and get two possible "delta x" values
                    # Example: width=100, self.x=40, obj.x=80. Then
                    # dxDirect = +40 (40 units from left to right)
                    # and dxAround = -60 (60 units from right to left)
                    dxDirect = obj.calc_x - self.calc_x
                    if obj.calc_x >= self.calc_x:
                        dxAround = dxDirect - self.world.width
                    else:
                        dxAround = dxDirect + self.world.width

                    # Take the shorter one, i.e. the one with smaller
                    # absolute value
                    dx = min((dxDirect, dxAround), key = abs)

                    # And the same with the y values
                    dyDirect = obj.calc_y - self.calc_y
                    if obj.calc_y >= self.calc_y:
                        dyAround = dyDirect - self.world.height
                    else:
                        dyAround = dyDirect + self.world.height
                        
                    dy = min((dyDirect, dyAround), key = abs)

                    if dx**2 + dy**2 < CRITTER_VIEW_DISTANCE_SQ:
                        visible_objects.append((obj, dx, dy))

            # Ask the agent what to do
            (turn_angle, move_distance, reproduce) = \
                self.agent.compute_next_action(self, visible_objects)

            # Move
            if move_distance > CRITTER_MAX_MOVE_SPEED: move_distance = CRITTER_MAX_MOVE_SPEED
            self.direction += turn_angle
            self.direction %= 2*pi
            self.x += cos(self.direction) * move_distance
            # minus sign because (0, 0) is top left
            self.y += -sin(self.direction) * move_distance

            # Wrap around
            while self.x < 0: self.x += self.world.width
            while self.x >= self.world.width: self.x -= self.world.width
            while self.y < 0: self.y += self.world.height
            while self.y >= self.world.height: self.y -= self.world.height

            # Update representation
            #self.representation.axis = rotate((1, 0, 0), self.direction, (0, -1, 0))
            #self.representation.pos = (self.x, 0.75, self.y)
            self.direction %= 2*pi

            #north direction
            if self.direction > (5*pi)/4 and self.direction <= (7*pi)/4 :
                if round((self.iteration_counter/ANIMATION_MOVE_INTERVAL))%2 ==  0:
                   screen.blit(self.img_south1, (self.x, self.y))
                else:
                    screen.blit(self.img_south2, (self.x, self.y))
            elif self.direction > pi/4 and self.direction <= (3*pi)/4 :
                if round((self.iteration_counter/ANIMATION_MOVE_INTERVAL))%2 ==  0:
                    screen.blit(self.img_north1, (self.x, self.y))
                else:
                    screen.blit(self.img_north2, (self.x, self.y))
            elif self.direction > (3*pi)/4 and self.direction <= (5*pi)/4 :
                if round((self.iteration_counter/ANIMATION_MOVE_INTERVAL))%2 ==  0:
                    screen.blit(self.img_west1, (self.x, self.y))
                else:
                    screen.blit(self.img_west2, (self.x, self.y))
            elif self.direction > (7*pi)/4 or self.direction <= pi/4 :
                if round((self.iteration_counter/ANIMATION_MOVE_INTERVAL))%2 ==  0:
                    screen.blit(self.img_east1, (self.x, self.y))
                else:
                    screen.blit(self.img_east2, (self.x, self.y))
                

            # Reproduce
            if reproduce:
                boy_south1 = pygame.image.load('boy_south_walk1.png').convert()
                boy_south2 = pygame.image.load('boy_south_walk2.png').convert()
                boy_north1 = pygame.image.load('boy_north_walk1.png').convert()
                boy_north2 = pygame.image.load('boy_north_walk2.png').convert()
                boy_east1 = pygame.image.load('boy_east_walk1.png').convert()
                boy_east2 = pygame.image.load('boy_east_walk2.png').convert()
                boy_west1 = pygame.image.load('boy_west_walk1.png').convert()
                boy_west2 = pygame.image.load('boy_west_walk2.png').convert()
                child = Critter(self.world, 0,
                                self.x, self.y, 
                             self.direction + pi, screen, 0, CRITTER_HORIZONTAL_CENTER, CRITTER_VERTICAL_CENTER,
                            boy_south1, boy_south2, boy_north1, boy_north2, 
                            boy_east1, boy_east2, boy_west1, boy_west2)
                self.world.add(child)
                self.energy -= REPRODUCTION_COST

            # Eat food
            for obj in self.world.objects:
                if isinstance(obj, Food):
                    if self.distance_sq(obj) < COLLISION_RADIUS_SQ:
                        self.world.delete(obj)
                        self.energy += obj.energy

            #Energy decay + death
            self.energy -= CRITTER_ENERGY_DECAY_RATE
            if self.energy <= 0:
                self.world.delete(self)
                
            # update the counter
            self.iteration_counter += 1
            

class Agent(object):
    def __init__(self):
        self.clock = 0

    def compute_next_action(self, critter, visible_objects):
        """ Given the current state of the critter and a list of visible
        objects, returns the next set of actions for this agent's critter.

        critter is just the Critter instance
        visible_objects is a list of triples (obj, dx, dy) where:
        * obj is an Object instance
        * dx is the "delta-x" of the object relative to the critter
        * dy is the "delta-y" of the object relative to the critter
        Note that dx and dy have already taken into account the fact
        that the world wraps around.
        
        Returns a tuple (turn_angle, move_distance, reproduce)
        where reproduce is a boolean, which tells the given critter
        what to do. """

        self.clock += 1
        
        visible_food_positions = [(dx, dy) for (obj, dx, dy) in visible_objects
                                  if isinstance(obj, Food)]
        
        if visible_food_positions != []:
            (closest_food_dx, closest_food_dy) = min(visible_food_positions,
                                                     key = lambda (dx, dy): dx**2 + dy**2)
            
            angle = atan2(-closest_food_dy, closest_food_dx)
            return (angle - critter.direction, CRITTER_MAX_MOVE_SPEED, False)
        else:
            reproduce = False
            if critter.energy > REPRODUCTION_ENERGY_THRESHOLD:
                if self.clock > REPRODUCTION_PERIOD:
                    reproduce = True
                    self.clock = 0
            turn_angle = 0
            if random.randint(0, FRAMERATE*MEAN_TURN_INTERVAL) == 5:
                turn_angle = (random.randint(0, 4)*pi)/2
            return (turn_angle, CRITTER_MAX_MOVE_SPEED, reproduce)
            

if __name__ == "__main__": 
    pygame.init()    
    
    screen = pygame.display.set_mode((640, 640))   
    World(640, 640, screen).run()
