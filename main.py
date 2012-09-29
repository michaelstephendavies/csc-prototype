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
from graphs import *

class Config:

    # Map from setting name to a string parsing function
    setting_dict = {
        "random_seed": str,
        
        # Critter settings
        "initial_energy": float,
        "critter_energy_decay_rate": float,
        "reproduction_cost": float,
        "critter_view_distance": float,
        "critter_max_move_speed": float,
        "maturity_age": int,
        "reproduction_radius": float,
        
        # Food settings
        "food_spawn_period": int,
        "food_energy": int,
        "collision_radius": float,

        # Agent settings
        "agent_trait_variance": float,
        "reproduction_energy_threshold": float,
        "reproduction_energy_threshold_min": float,
        "reproduction_energy_threshold_max": float,
        "reproduction_period": float,
        "reproduction_period_min": float,
        "reproduction_period_max": float,
        "mean_turn_interval": float,
        "mean_turn_interval_min": float,
        "mean_turn_interval_max": float,
        "agent_move_speed": float,
        "agent_move_speed_min": float,
        "agent_move_speed_max": float,

        # Graphical settings
        "framerate": int,
        "tile_size": int,
        "animation_frame_interval": int,
        "critter_vertical_center": int,
        "critter_horizontal_center": int,
        "food_horizontal_offset" : int,
        "food_vertical_offset" : int, 
        "tree_horizontal_offset" : int,
        "tree_vertical_offset" : int,
        "palm_vertical_offset" : int,
        "ageing_interval" : int,
        "heart_time" : int,
        "heart_offset" : int,
        "skeleton_vertical_offset" : int,
        "skeleton_horizontal_offset" : int,
        "skeleton_time" : int,
        "small_object_offset" : int
    }
        
    tiles_dict = {
                  "daisies" : "d",
                  "hill" :  "h",
                  "long_grass" : "l",
                  "pit" : "p",
                  "sand" : "s",
                  "dirt" : "i",
                  }   
   
    def __init__(self, conf_filename, spec_filename):
        self.settings = {}
        errors = []
        
        with open(conf_filename) as conf_file:
            for line in conf_file.readlines():
                line = line.strip()
                if (not line.startswith("#")) and line != "":
                    (key, value) = line.split("=")
                    key = key.strip()
                    value = value.strip()
                    try:
                        parse_function = Config.setting_dict[key]
                        try:
                            self.settings[key] = parse_function(value)
                        except:
                            # parse_function threw an exception
                            errors.append("Invalid value for '{0}': {1}".format(key, value))
                            
                    except KeyError:
                        errors.append("Unknown config setting: {0}".format(key))

        for setting in Config.setting_dict.iterkeys():
            if setting not in self.settings:
                errors.append("Missing config setting: {0}".format(setting))

        if errors != []:
            raise ConfigParseException("\n".join(errors))
                
        self.critter_view_distance_sq = self.settings["critter_view_distance"]**2
        self.collision_radius_sq = self.settings["collision_radius"]**2
        self.reproduction_radius_sq = self.settings["reproduction_radius"]**2
        
        # the bit to do the world spec
        spec_file = open(spec_filename)
        first_line = spec_file.readline()
        (rows, cols) = first_line.split()
        self.rows = int(rows)
        self.cols = int(cols)
        # making something to hold info on
        self.scenery = []                
        # making a matrix of g's
        self.tile_spec = [["g" for a in xrange(int(cols))] for b in xrange(int(rows))]
        # adding in the other tiles
        for line in spec_file:
            (type, colon, x, y) = line.split()
            if type in self.tiles_dict:
                letter = self.tiles_dict[type]
                self.tile_spec[int(x)][int(y)] = letter   
            else:
                self.scenery.append([type, int(x), int(y)])

        self.world_width = self.cols * self.settings["tile_size"]
        self.world_height = self.rows * self.settings["tile_size"]          

    def __getitem__(self, name):
        # Operator overload for "config[name]"
        return getattr(self, name)
    
    def __getattr__(self, name):
        # Called when an attribute of a Config object is found, but Python
        # can't find it normally. Instead we return the correct config value.
        return self.settings[name]
    
class ConfigParseException(Exception):
    pass


class World(object):
    def __init__(self, screen, config):
        
        # The simulation model has a toroidal topology (x and y co-ordinates
        # "wrap around"); we keep all x values in [0, width) and y values in
        # [0, height).
        
        # (0, 0) in the simulation model maps to the top-left corner,
        # positive y is down. Directions are given with positive being clockwise.
        self.screen = screen
        self.config = config
        self.skeletons = []
        self.objects = []
        
        # add scenery to objects
        for item in self.config.scenery:
            if item[0] == "palm":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_palm(), self.config.tree_horizontal_offset, 
                                    self.config.palm_vertical_offset))
            elif item[0] == "oak":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_oak(), self.config.tree_horizontal_offset, 
                                    self.config.tree_vertical_offset))
            elif item[0] == "dead_tree":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_dead_tree(), self.config.tree_horizontal_offset, 
                                    self.config.tree_vertical_offset))
            elif item[0] == "pine":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_pine(), self.config.tree_horizontal_offset, 
                                    self.config.tree_vertical_offset))
            elif item[0] == "fern":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_fern(), self.config.small_object_offset, 
                                    self.config.small_object_offset))
            elif item[0] == "rocks":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_rocks(), self.config.small_object_offset, 
                                    self.config.small_object_offset))
            elif item[0] == "stump":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_stump(), self.config.small_object_offset, 
                                    self.config.small_object_offset))
            elif item[0] == "yellow_flowers":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_yellow_flowers(), self.config.small_object_offset, 
                                    self.config.small_object_offset))
            elif item[0] == "pink_flowers":
                self.objects.append(Scenery(self.config, self, 0, item[1], item[2], 
                                    get_pink_flowers(), self.config.small_object_offset, 
                                    self.config.small_object_offset))
                   
        for i in xrange(5):
            self.objects.append(Critter(config, self, len(self.objects),
                random.random()*self.config.world_width, random.random()
                    *self.config.world_height, random.randint(0, 5), 
                            random.randint(0, 5), 2*self.config.ageing_interval, get_male_images(), "m")) # TODO: random counter_offset
        
        for i in xrange(5):
            self.objects.append(Critter(config, self, len(self.objects),
                random.random()*self.config.world_width, random.random()
                    *self.config.world_height, random.randint(0, 5), 
                            random.randint(0, 5), 2*self.config.ageing_interval, get_female_images(), "f"))
            
        for i in xrange(10):
            self.objects.append(Food(config, self, len(self.objects), random.random()*self.config.world_width,
                random.random()*self.config.world_height, self.config.food_energy))
    
    def delete(self, obj):
        obj.kill()        
        self.objects.remove(obj)

    def add(self, new_obj):
        self.objects.append(new_obj)
        
    def add_skeleton(self, new_skeleton):
        self.skeletons.append(new_skeleton)
        
    def delete_skeleton(self, skeleton):
        self.skeletons.remove(skeleton)
    
    def run(self):
        counter = 0
        
        tiles = {    
        "g" : get_tile_grass(),
        "d" : get_tile_daisies(),
        "h" : get_tile_hill(),
        "l" : get_tile_long_grass(),
        "p" : get_tile_pit(),
        "s" : get_tile_sand(),
        "i" : get_tile_dirt()
        }

        test_graph = LineGraph(5, 5, 200, 100, "Population vs Time", 50, Color(200, 200, 200), Color(50, 50, 100))
        
        # variables to help the eagle and dove only sometimes
        # fly accross 
        eagle_on = True
        eagle_x = 0
        eagle_y = 0.1*self.config.world_height # first y channel
        eagle_start = 0
        dove_on = True
        dove_x = 0.1*self.config.world_width # first x channel
        dove_y = 0
        dove_start = 0
        
        
        while True:
            clock = pygame.time.Clock()
            clock.tick(self.config.framerate)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    return            

            for y in xrange(self.config.rows):
                for x in xrange(self.config.cols):
                       self.screen.blit(tiles[self.config.tile_spec[y][x]], 
                                        (x*self.config.tile_size, y*self.config.tile_size)) 
        
            # Iterate over a copy of the object list since modifying a list
            # while iterating over it is verboten
            for obj in self.objects[:]:
                obj.update()
            
            if counter % self.config.food_spawn_period == 0:
                self.add(Food(config, self, 0, random.random()*self.config.world_width,
                              random.random()*self.config.world_height, self.config.food_energy))
                
            self.objects.sort(key = lambda obj: obj.y)
            
            for skeleton in self.skeletons:
                skeleton.render(self.screen)

            for obj in self.objects:
                obj.render(self.screen)
            
            # add in the eagle and dove
            frame_choice = int(floor((counter / self.config.framerate)*5) % 2)
            if(eagle_on):
                if eagle_x > self.config.world_width:
                    eagle_on = False   
                eagle_x = (counter - eagle_start)
                screen.blit(get_eagle()[frame_choice], (eagle_x, eagle_y))
            if (not eagle_on) and \
                random.randint(0, 2*self.config.framerate - 1) == \
                (counter % 2*self.config.framerate):
                eagle_on = True
                eagle_x = 0
                eagle_start = counter
                eagle_y = (random.randint(1, 9)/10)*self.config.world_height
            if(dove_on):
                if dove_y < 0:
                    dove_on = False   
                dove_y = (self.config.world_height - (counter - dove_start))
                screen.blit(get_dove()[frame_choice], (dove_x, dove_y))
            if (not dove_on) and \
                random.randint(0, 2*self.config.framerate - 1) == \
                (counter % 2*self.config.framerate):
                dove_on = True
                dove_y = 0
                dove_start = counter
                dove_x = (random.randint(1, 9)/10)*self.config.world_width

            test_graph.add_data_point(len([obj for obj in self.objects if obj.get_type() == "Critter"]))
            test_graph.render(self.screen)
            
            counter += 1    
            
            pygame.display.flip()

if __name__ == '__main__':
    try:
        config = Config(sys.argv[1], sys.argv[2])
    except ConfigParseException as ex:
        print ex
        sys.exit(1)

    if config.random_seed == "":
        random.seed() # using the OS-specific randomness source
    else:
        random.seed(hash(config.random_seed))
    
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((config.world_width, config.world_height))
    World(screen, config).run()
