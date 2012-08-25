
from __future__ import division

from visual import *
import random
random.seed()

INITIAL_ENERGY = 100
REPRODUCTION_ENERGY_THRESHOLD = 130
REPRODUCTION_COST = 30
CRITTER_ENERGY_DECAY_RATE = 0.2
FOOD_SPAWN_PERIOD = 40
FOOD_ENERGY = 50
FLOOR_COLOUR = (0.2, 1, 0.2)
FOOD_COLOUR = (0, 0.5, 0)
CRITTER_COLOUR = (1, 0, 0)
CRITTER_VIEW_DISTANCE = 5
CRITTER_VIEW_DISTANCE_SQ = CRITTER_VIEW_DISTANCE**2
CRITTER_MAX_MOVE_SPEED = 0.05
REPRODUCTION_PERIOD = 120
COLLISION_RADIUS = 0.1
COLLISION_RADIUS_SQ = COLLISION_RADIUS**2
SIMULATION_RATE = 60

class World(object):
    def __init__(self, width, height):
        
        # A note on co-ordinate systems.
        # The simulation model has two co-ordinate axes, whereas
        # VPython has three co-ordinate axes.
        # We map a simulation point (x, y) to the VPython point (x, z, y)
        # where z is some arbitrary level above the "floor" of the world which
        # depends on the specific kind of object.
        self.width = width
        self.height = height
        self.objects = []
        for i in xrange(5):
            self.objects.append(Critter(self, len(self.objects),
                random.random()*(width-2)+1, random.random()*(height-2), random.random()*2*pi))
            
        for i in xrange(10):
            self.objects.append(Food(len(self.objects), random.random()*(width-2)+1,
                random.random()*(height-2)+1, FOOD_ENERGY))

    def delete(self, obj):
        obj.kill()
        self.objects.remove(obj)

    def add(self, new_obj):
        new_obj.show()
        self.objects.append(new_obj)
    
    def run(self):
        # Create the floor
        box(pos = (self.width/2, 0, self.height/2), length = self.width, height = 0.5,
            width = self.height, color = FLOOR_COLOUR)
        
        # Reposition the camera so it is looking at the center of the world
        scene.center = (self.width/2, 0, self.height/2)
        
        for obj in self.objects:
            obj.show()

        counter = 0
        while True:
            # Iterate over a copy of the object list since modifying a list
            # while iterating over it is problematic
            for obj in self.objects[:]:
                obj.update()

            if counter % FOOD_SPAWN_PERIOD == 0:
                self.add(Food(0, random.random()*(self.width-2)+1,
                              random.random()*(self.height-2)+1, FOOD_ENERGY))
                
            counter += 1
            
            rate(SIMULATION_RATE)      

class Object(object):
    """ Abstract base class for simulation objects.
    
    In addition to overriding show, kill and update, all Objects
    must have the following attributes:
    object_ID - unique identifier for the object
    x, y - current simulation co-ordinates of the object """
    
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
        return (self.x - other.x)**2 + (self.y - other.y)**2  


class Food(Object):
    def __init__(self, object_ID, x, y, contained_energy):
        self.object_ID = object_ID
        self.x = x
        self.y = y
        self.energy = contained_energy

    def show(self):
        self.representation = sphere(pos = (self.x, 0.75, self.y),
                                     radius = 0.5, color = FOOD_COLOUR)

    def kill(self):
        self.representation.visible = False
    
    def update(self):
        pass


class Critter(Object):
        def __init__(self, world, object_ID, x, y, direction):
            self.world = world
            self.object_ID = object_ID
            self.x = x
            self.y = y
            self.direction = direction
            self.energy = INITIAL_ENERGY
            self.agent = Agent()

        def show(self):
            self.representation = cone(pos = (self.x, 0.75, self.y),
                axis = (1, 0, 0), radius = 0.5, color = CRITTER_COLOUR)

        def kill(self):
            self.representation.visible = False
        
        def update(self):
            # Find all objects close enough to be visible to the agent
            visible_objects = [obj for obj in self.world.objects \
                if obj != self \
                and self.distance_sq(obj) < CRITTER_VIEW_DISTANCE_SQ]

            # Ask the agent what to do
            (turn_angle, move_distance, reproduce) = \
                self.agent.compute_next_action(self, visible_objects)

            # Move
            if move_distance > CRITTER_MAX_MOVE_SPEED: move_distance = CRITTER_MAX_MOVE_SPEED
            self.direction += turn_angle
            self.direction %= 2*pi
            self.x += cos(self.direction) * move_distance
            self.y += sin(self.direction) * move_distance
            
            self.representation.axis = rotate((1, 0, 0), self.direction, (0, -1, 0))
            self.representation.pos = (self.x, 0.75, self.y)

            # Reproduce
            if reproduce:
                child = Critter(self.world, 0, self.x, self.y,
                                (self.direction + pi)%(2*pi)) # FIXME: object_ID
                self.world.add(child)
                self.energy -= REPRODUCTION_COST
            
            # Collide with edges of world
            if self.x > self.world.width: self.x = self.world.width
            elif self.x < 0: self.x = 0
            if self.y > self.world.height: self.y = self.world.height
            elif self.y < 0: self.y = 0

            # Eat food
            for obj in self.world.objects:
                if isinstance(obj, Food):
                    if self.distance_sq(obj) < COLLISION_RADIUS_SQ:
                        self.world.delete(obj)
                        self.energy += obj.energy

            # Energy decay + death
            self.energy -= CRITTER_ENERGY_DECAY_RATE
            if self.energy <= 0:
                self.world.delete(self)
            

class Agent(object):
    def __init__(self):
        self.clock = 0

    def compute_next_action(self, critter, visible_objects):
        """ Returns a tuple (turn_angle, move_distance, reproduce)
        where reproduce is a boolean, which tells the given critter
        what to do. """

        self.clock += 1
        
        visible_food = [obj for obj in visible_objects if isinstance(obj, Food)]
        if visible_food != []:
            closest_food = min(visible_food, key = critter.distance_sq)
            angle = atan2(closest_food.y - critter.y, closest_food.x - critter.x)
            return (angle - critter.direction, CRITTER_MAX_MOVE_SPEED, False)
        else:
            reproduce = False
            if critter.energy > REPRODUCTION_ENERGY_THRESHOLD:
                if self.clock > REPRODUCTION_PERIOD:
                    reproduce = True
                    self.clock = 0
            return (random.random()*0.4 - 0.2, CRITTER_MAX_MOVE_SPEED, reproduce)
            

if __name__ == "__main__":     
    World(30, 30).run()
