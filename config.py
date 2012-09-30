"""
config.py

Parses and stores configuration settings and the world specification.

Michael Davies and David Shorten
CSC3003S Capstone Project

All graphics used in this program are open content and 
were provided for by REFMAP(http://www.tekepon.net/fsm)
"""

import os
from os import path

class Config:
    """ Parses and stores settings from the configuration file
    and world specification file.

    After instantiating, settings can be accessed with either the
    usual attribute access syntax ("config.setting") or, if the attribute name
    is not known at programming time, with the dictionary lookup syntax
    ("config['setting']").

    In addition to the settings defined in setting_dict,
    there are some "virtual settings":
        critter_view_distance_sq, collision_radius_sq, reproduction_radius_sq, scenery_avoidance_radius_sq
            The square of critter_view_distance, collision_radius, etc... respectively

        world_width, world_height
            Size of the world in pixels. """
    
    # Map from setting name to a string parsing function
    # To add a new config setting, just add an entry to this dictionary.
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
        "starting_males" : int,
        "starting_females" : int, 
        
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
        "critter_avoidance_radius" : int,
        "scenery_avoidance_radius" : int,
        "avoidance_time" : float,

        # Graph settings
        "enable_graphs": int,
        "graph_width": int,
        "population_graph": int,
        "population_graph_high": int,
        "population_graph_scale_division": int,
        "population_graph_update_period": int,
        "population_graph_export_path": str,
        "food_graph": int,
        "food_graph_high": int,
        "food_graph_scale_division": int,
        "food_graph_update_period": int,
        "food_graph_export_path": str,
        "agent_move_speed_graph": int,
        "agent_move_speed_graph_high": float,
        "agent_move_speed_graph_scale_division": float,
        "agent_move_speed_graph_update_period": int,
        "agent_move_speed_graph_export_path": str,
        
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
        """ Create a new Config option, given the name of the config file
        and world spec file (excluding "setups/"). Throws ConfigParseException
        if the config file is invalid. """
        self.settings = {}
        errors = []

        # Read config file
        conf_string = "setups/" + conf_filename
        conf_path = path.relpath(conf_string)
        with open(conf_path) as conf_file:
            for line in conf_file.readlines():
                line = line.strip()
                if (not line.startswith("#")) and line != "":
                    (key, value) = line.split("=")
                    key = key.strip()
                    value = value.strip()
                    try:
                        # Look up the parsing function from setting_dict and use
                        # it to parse the value; also, check that it's valid setting
                        parse_function = Config.setting_dict[key]
                        try:
                            self.settings[key] = parse_function(value)
                        except:
                            # Parse_function threw an exception
                            errors.append("Invalid value for '{0}': {1}".format(key, value))
                            
                    except KeyError:
                        errors.append("Unknown config setting: {0}".format(key))

        # Check that all settings are present
        for setting in Config.setting_dict.iterkeys():
            if setting not in self.settings:
                errors.append("Missing config setting: {0}".format(setting))

        if errors != []:
            raise ConfigParseException("\n".join(errors))

        # Precompute some squares of distances
        self.critter_view_distance_sq = self.settings["critter_view_distance"]**2
        self.collision_radius_sq = self.settings["collision_radius"]**2
        self.reproduction_radius_sq = self.settings["reproduction_radius"]**2
        self.scenery_avoidance_radius_sq = self.settings["scenery_avoidance_radius"]**2
        
        # Read the world specification file
        spec_string = "setups/" + spec_filename
        spec_path = path.relpath(spec_string)
        spec_file = open(spec_path)
        first_line = spec_file.readline()
        (rows, cols) = first_line.split()
        self.rows = int(rows)
        self.cols = int(cols)
        
        # making something to hold info on
        self.scenery = []                
        # making a matrix of g's
        self.tile_spec = [["g" for a in xrange(self.rows)] for b in xrange(int(self.cols))]
        # adding in the other tiles
        for line in spec_file:
            (type, colon, x, y) = line.split()
            if type in self.tiles_dict:
                letter = self.tiles_dict[type]
                self.tile_spec[int(x)][int(y)] = letter
            else:
                self.scenery.append([type, int(x), int(y)])

        spec_file.close()

        # world dimensions in pixels
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
