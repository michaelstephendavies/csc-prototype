from __future__ import division

import pygame
from pygame.locals import *

#imports from our own files
from main import *


text_font = None
def get_text_font():
    global text_font
    if text_font == None:
        text_font = pygame.font.Font(None, 16)
    return text_font

class Graph(object):
    def __init__(self, x, y, width, height, title,
                 bg_color=Color(255, 255, 255), out_file=None):
        self.rect = Rect(x, y, width, height)
        self.title_image = get_text_font().render(title, True, Color(0, 0, 0), bg_color)
        self.bg_color = bg_color
        
        if out_file != None:
            self.out = open(out_file, "w")
        else:
            self.out = None

    def finish(self):
        self.out.close()
    
    def render(self, screen):
        screen.fill(self.bg_color, self.rect)
        self.render_foreground(screen)
        screen.blit(self.title_image, self.rect)

    def render_foreground(self, screen):
        raise NotImplementedError("Override in your subclass")


class LineGraph(Graph):
    def __init__(self, x, y, width, height, title, high, bg_color=Color(255, 255, 255), out_file=None):
        Graph.__init__(self, x, y, width, height, title, bg_color, out_file)
        self.high = high

        self.last_data_point_scaled = self.rect.height
        self.graph_surface = pygame.Surface((width, height))
        self.graph_surface.fill(bg_color)

    def add_data_point(self, new_point):
        new_data_point_scaled = int((1 - new_point/self.high) * self.rect.height)

        self.graph_surface.scroll(dx=-1)
        pygame.draw.line(self.graph_surface, self.bg_color,
                         (self.rect.width-1, 0),
                         (self.rect.width-1, self.rect.height))
        pygame.draw.line(self.graph_surface, (0, 0, 0),
                         (self.rect.width-1, self.last_data_point_scaled),
                         (self.rect.width-1, new_data_point_scaled))

        self.last_data_point_scaled = new_data_point_scaled
    
    def render_foreground(self, screen):
        screen.blit(self.graph_surface, self.rect)
