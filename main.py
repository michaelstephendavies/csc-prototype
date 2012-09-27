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

    # Map from setting name to a string parsing function
    setting_dict = {
        "initial_energy": float,
        "reproduction_energy_threshold": float,
        "reproduction_cost": float,
        "critter_energy_decay_rate": float,
        "food_spawn_period": int,
        "food_energy": int,
        "critter_view_distance": float,
        "critter_max_move_speed": float,
        "reproduction_period": float,
        "collision_radius": float,
        "reproduction_radius": float,
        "mean_turn_interval": float,
        "world_width": int,
        "world_height": int,
        "tile_size": int,
        "framerate": int,
        "animation_frame_interval": int,
        "critter_vertical_center": int,
        "critter_horizontal_center": int,
        "food_center": int,
        "tree_horizontal_offset" : int,
        "tree_vertical_offset" : int,
        "palm_vertical_offset" : int
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
                      
        self.reproduction_radius_sq = self.settings["reproduction_radius"]**2

    def __getitem__(self, name):
        # Operator overload for "config[name]"
        return self.settings[name]
    
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
        
        while True:
            clock = pygame.time.Clock()
            clock.tick(self.config.framerate)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    return            
            
            tiles = {    
            "g" : get_tile_grass(),
            "d" : get_tile_daisies(),
            "h" : get_tile_hill(),
            "l" : get_tile_long_grass(),
            "p" : get_tile_pit(),
            "s" : get_tile_sand(),
            "i" : get_tile_dirt()
            }
            
            
            for x in xrange(self.config.rows):
                for y in xrange(self.config.cols):
                       self.screen.blit(tiles[self.config.tile_spec[x][y]], 
                                        (x*self.config.tile_size, y*self.config.tile_size)) 
                    
                    
                    
                    
            # Iterate over a copy of the object list since modifying a list
            # while iterating over it is verboten
            for obj in self.objects[:]:
                obj.update()
            
            if counter % self.config.food_spawn_period == 0:
                self.add(Food(config, self, 0, random.random()*self.config.world_width,
                              random.random()*self.config.world_height, self.config.food_energy))
                
            self.objects.sort(key = lambda obj: obj.y)

            for obj in self.objects:
                obj.render(self.screen)
                
            pygame.display.flip()
                
            counter += 1    

if __name__ == '__main__':
    try:
        config = Config(sys.argv[1], sys.argv[2])
    except ConfigParseException as ex:
        print ex
        sys.exit(1)
        
    pygame.init()
    screen = pygame.display.set_mode((config.world_width, config.world_height))
    World(screen, config).run()
