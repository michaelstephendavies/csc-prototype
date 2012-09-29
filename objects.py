from images import *
from agent import *
import random

class Object(object):
    """ Abstract base class for simulation objects.

    In addition to overriding show, kill and update, all Objects
    must have the following attributes:
    object_ID - unique identifier for the object
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
        raise NotImplementedError("Override in your subclass")

class Food(Object):
    def __init__(self, config, world, object_ID, x, y, contained_energy):
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
        def __init__(self, config, world, object_ID, x, y, direction,
                     counter_offset, age, images, gender, parent1=None, parent2=None):
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
            # counter to know when to change the animation
            # given offset so that critters do not move in
            # unison.
            self.iteration_counter = counter_offset
            self.age = age
            self.heart_countdown = 0
            self.gender = gender
            self.avoidance_countdown = 0

        def update(self):
            # Find all objects close enough to be visible to the agent;
            # tag each along with its delta-x and delta-y values relative
            # to this object
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

            # Ask the agent what to do
            (turn_angle, move_distance, reproduce) = \
                self.agent.compute_next_action(self, visible_objects)

            # Move
            if move_distance > self.config.critter_max_move_speed:
                move_distance = self.config.critter_max_move_speed
            self.direction += turn_angle
            self.direction %= 2*pi
            self.x += cos(self.direction) * move_distance
            self.y += sin(self.direction) * move_distance

            # Wrap around
            while self.x < 0: self.x += self.config.world_width
            while self.x >= self.config.world_width: self.x -= self.config.world_width
            while self.y < 0: self.y += self.config.world_height
            while self.y >= self.config.world_height: self.y -= self.config.world_height

            self.direction %= 2*pi

            # Reproduce
            if reproduce and self.is_mature() and reproduce.is_mature() and self.gender != reproduce.gender:
                self.heart_countdown = self.config.heart_time
                reproduce.heart_countdown = self.config.heart_time
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

                self.world.add(child)
                self.energy -= self.config.reproduction_cost

            # Eat food
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
            if self.iteration_counter % self.config.framerate == 0 :
                self.heart_countdown -= 1
                self.age += 1

        def render(self, screen):
            age_images = self.images[int(min(floor(self.age/self.config.ageing_interval), 3))]
            direction_quadrant = int(((self.direction + pi/4)%(2*pi))/(pi/2))
            animation_frame = int(self.iteration_counter/self.config.animation_frame_interval) \
                                  % len(age_images[direction_quadrant])

            screen.blit(age_images[direction_quadrant][animation_frame],
                        (self.x - self.config.critter_horizontal_center,
                         self.y - self.config.critter_vertical_center))

            if self.heart_countdown > 0:
                screen.blit(self.heart_image,
                        (self.x - self.config.critter_horizontal_center + self.config.heart_offset - 2,
                         self.y - self.config.critter_vertical_center
                         - self.config.heart_offset - 7))

        def is_mature(self):
            return self.age >= self.config.maturity_age

        def get_type(self):
            return "Critter"

class Scenery(Object):
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

    def render(self, screen):
        screen.blit(self.image, (self.x - self.horizontal_offset,
                                 self.y - self.vertical_offset))

    def get_type(self):
        return "Scenery"
    
class Skeleton(Object):
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
        self.countdown -= 1
        if self.countdown <= 0:
            self.world.delete_skeleton(self)

    def get_type(self):
        return "Scenery"


