"""
objects.py

Contains all of the various simulation objects.

Michael Davies and David Shorten
CSC3003S Capstone Project

All graphics used in this program are open content and 
were provided for by REFMAP(http://www.tekepon.net/fsm)
"""

from images import *
from agent import *
import random

class Object(object):
    """ Abstract base class for simulation objects.

    In addition to overriding show, kill and update, all Objects
    must have the following attributes:
    x, y - current simulation co-ordinates of the object
    world - reference to the containing World"""

    def __init__(self):
        raise NotImplementedError("Override in your subclass")

    def kill(self):
        """ Called when the object is destroyed. """
        pass

    def update(self):
        """ Called once every simulation step, to update the
        object's simulation model. """
        pass

    def render(self, screen):
        """ Called once every simulation step, to draw the
        object to the screen. """
        pass

    def distance_sq(self, other):
        """ Find the square of the distance between this Object and
        another Object. """

        # Since the world wraps around, it's not just a straight Euclidean
        # distance. We find the shorter x distance (either going across the
        # world in the normal way, or wrapping around the left/right edge).
        # Then we do the same for the y, then use these in the Euclidean
        # distance formula.
        dx = min(abs(self.x - other.x), self.config.world_width - abs(self.x - other.x))
        dy = min(abs(self.y - other.y), self.config.world_height - abs(self.y - other.y))

        return dx**2 + dy**2

    def get_type(self):
        """ Return a string defining the type of the object (e.g. "Critter"
        or "Food"). This should be the name of the class, but doesn't have to
        be. (Workaround for a Python bug in isinstance when multiple modules
        are used.)"""
        raise NotImplementedError("Override in your subclass")

class Food(Object):
    """ A food item (i.e. "goat"). """
    
    def __init__(self, config, world, object_ID, x, y, contained_energy):
        """ Create a food item at the given position containing
        the given amount of energy. (object_ID is not used)"""
        self.config = config
        self.world = world
        self.object_ID = object_ID
        self.x = x
        self.y = y
        self.energy = contained_energy
        self.food_image = get_food_image()

    def render(self, screen):
        screen.blit(self.food_image, (self.x - self.config.food_horizontal_offset,
                                      self.y - self.config.food_vertical_offset))

    def get_type(self):
        return "Food"


class Critter(Object):
    """ A critter. This should not be confused with Agent;
    A critter is the "physical body" of the critter, which contains
    an Agent, which is the critter's "brain" which tells it how to act.

    Publically accessible attributes (read-only):
    agent - the critter's agent"""
    
    def __init__(self, config, world, object_ID, x, y, direction,
                 counter_offset, age, images, gender, parent1=None, parent2=None):
        """ Create a new Critter.
        object_ID - not used
        x, y, direction - initial position and direction of the critter
        counter_offset - allows you to start the critter's walking animation
                         in a different position, preventing the initial critters
                         from "marching in unison"
        age - age of the critter in seconds; for newborn critters this is 0, but
              not for the initial critters
        images - A 3-dimension image array of the format returned by images.get_male_images
                 or images.get_female_images
        gender - "m" or "f"
        parent1, parent2 - The agents of the critters parents, or None if this is one
                           of the initial critters. """
        
        self.config = config
        self.world = world
        self.object_ID = object_ID
        self.x = x
        self.y = y
        self.direction = direction
        self.energy = self.config.initial_energy
        self.agent = Agent(self.config, parent1, parent2)
        self.images = images
        self.heart_image = get_heart()
        self.iteration_counter = counter_offset # counter used for animations and aging
        self.age = age
        self.heart_countdown = 0
        self.gender = gender

    def update(self):
        # Find all objects close enough to be visible to the agent;
        # tag each along with its delta-x and delta-y values relative
        # to this object.
        visible_objects = []
        for obj in self.world.objects:
            if obj != self:
                # There's two different ways to get from self.x to obj.x:
                # directly, or around the left/right edge. We calculate
                # both of these and get two possible "delta x" values
                # Example: width=100, self.x=40, obj.x=80. Then
                # dxDirect = +40 (40 units from left to right)
                # and dxAround = -60 (60 units from right to left)
                dxDirect = obj.x - self.x
                if obj.x >= self.x:
                    dxAround = dxDirect - self.config.world_width
                else:
                    dxAround = dxDirect + self.config.world_width

                # Take the shorter one, i.e. the one with smaller
                # absolute value
                dx = min((dxDirect, dxAround), key = abs)
                
                # And the same with the y values
                dyDirect = obj.y - self.y
                if obj.y >= self.y:
                    dyAround = dyDirect - self.config.world_height
                else:
                    dyAround = dyDirect + self.config.world_height

                dy = min((dyDirect, dyAround), key = abs)

                if dx**2 + dy**2 < self.config.critter_view_distance_sq:
                    visible_objects.append((obj, dx, dy))

        # Give the list of visible objects to the agent, and ask it what to do
        (turn_angle, move_distance, reproduce) = \
            self.agent.compute_next_action(self, visible_objects)

        # Move according to the agent's instructions
        if move_distance > self.config.critter_max_move_speed:
            move_distance = self.config.critter_max_move_speed
        self.direction += turn_angle
        self.direction %= 2*pi
        self.x += cos(self.direction) * move_distance
        self.y += sin(self.direction) * move_distance

        # Normalise our coordinates in the range [0, width)x[0, height)
        # and our direction in [0, 2pi)
        while self.x < 0: self.x += self.config.world_width
        while self.x >= self.config.world_width: self.x -= self.config.world_width
        while self.y < 0: self.y += self.config.world_height
        while self.y >= self.config.world_height: self.y -= self.config.world_height

        self.direction %= 2*pi

        # Reproduce if the agent told us to, and the provided reproduction target
        # is suitable
        if reproduce and reproduce.get_type() == "Critter" \
                     and self.is_mature() and reproduce.is_mature() \
                     and self.gender != reproduce.gender \
                     and self.distance_sq(reproduce) < self.config.reproduction_radius_sq:

            # Add the heart above our own head and the target's head
            self.heart_countdown = self.config.heart_time
            reproduce.heart_countdown = self.config.heart_time

            # Create a child; flip a coin to decide on the child's gender
            if random.randint(0, 1) == 1:
                child = Critter(self.config, self.world, 0,
                                self.x, self.y,
                                self.direction + pi, 0, 0,
                                get_male_images(), "m",
                                self.agent, reproduce.agent)
            else:
                child = Critter(self.config, self.world, 0,
                                self.x, self.y,
                                self.direction + pi, 0, 0,
                                get_female_images(), "f",
                                self.agent, reproduce.agent)

            self.world.add_here(child)

            # Note that only this critter loses energy, and not the target
            # This is intentional, as it prevents critters from taking away
            # other critters' energy against their will.
            self.energy -= self.config.reproduction_cost

        # Eat food if we are on top of it. This is automatic and does not need
        # to be initiated by the agent.
        for obj in self.world.objects:
            if isinstance(obj, Food):
                if self.distance_sq(obj) < self.config.collision_radius_sq:
                    self.world.delete(obj)
                    self.energy += obj.energy

        # Energy decay + death
        self.energy -= self.config.critter_energy_decay_rate
        if self.energy <= 0:
            self.world.add_skeleton(Skeleton(self.config, self.world,
                                                 0, self.x, self.y, 
                                   get_skeleton(), 
                                   self.config.skeleton_horizontal_offset, 
                                   self.config.skeleton_vertical_offset))
            self.world.delete(self)

        # update the counter
        self.iteration_counter += 1
        # update these once per second
        if self.iteration_counter % self.config.framerate == 0:
            self.heart_countdown -= 1
            self.age += 1

    def render(self, screen):
        # Determine which sprite to use according to our age, the direction we're facing,
        # and our current position along the animation
        age_images = self.images[int(min(floor(self.age/self.config.ageing_interval), 3))]
        direction_quadrant = int(((self.direction + pi/4)%(2*pi))/(pi/2))
        animation_frame = int(self.iteration_counter/self.config.animation_frame_interval) \
                              % len(age_images[direction_quadrant])

        # Offset the sprite such that the sprite's feet (instead of the top-left corner)
        # are on top of our current coordinates
        screen.blit(age_images[direction_quadrant][animation_frame],
                    (self.x - self.config.critter_horizontal_center,
                     self.y - self.config.critter_vertical_center))

        # Draw the heart if necessary
        if self.heart_countdown > 0:
            screen.blit(self.heart_image,
                    (self.x - self.config.critter_horizontal_center + self.config.heart_offset - 2,
                     self.y - self.config.critter_vertical_center - self.config.heart_offset - 7))

    def is_mature(self):
        """ Determines whether the critter is old enough to reproduce. """
        return self.age >= self.config.maturity_age

    def get_type(self):
        return "Critter"

class Scenery(Object):
    """ A scenery object (like a tree or bush), not including tiles.
    Critters move around these. """
    
    def __init__(self, config, world, object_ID, x, y, image,
                    horizontal_offset, vertical_offset):
        """ Create a scenery object.
        object_ID - not used
        horizontal_offset, vertical_offset
            - offset applied to the image so that a reasonable point on the image
              (such as the trunk of a tree) lines up with (x,y), and not
              the top-left corner. """
        
        self.config = config
        self.world = world
        self.object_ID = object_ID
        self.x = x
        self.y = y
        self.image = image
        self.horizontal_offset = horizontal_offset
        self.vertical_offset = vertical_offset

    def render(self, screen):
        screen.blit(self.image, (self.x - self.horizontal_offset,
                                 self.y - self.vertical_offset))

    def get_type(self):
        return "Scenery"
    
class Skeleton(Object):
    """ A skeleton of a dead critter. Has no effect on the simulation. """
    
    def __init__(self, config, world, object_ID, x, y, image,
                    horizontal_offset, vertical_offset):
        self.config = config
        self.world = world
        self.object_ID = object_ID
        self.x = x
        self.y = y
        self.image = image
        self.horizontal_offset = horizontal_offset
        self.vertical_offset = vertical_offset
        self.countdown = self.config.skeleton_time*self.config.framerate

    def render(self, screen):
        screen.blit(self.image, (self.x - self.horizontal_offset,
                                 self.y - self.vertical_offset))

    def update(self):
        self.countdown -= 1
        if self.countdown <= 0:
            self.world.delete_skeleton(self)

    def get_type(self):
        return "Scenery"


