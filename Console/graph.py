#!/usr/bin/python

import time
import threading
import pygame
from py2d.Math import *

SCREEN_WIDTH = 450
SCREEN_HEIGHT = 200
BACKGROUND_COLOR = 0xa00033
TEXT_BACKGROUND = (16, 16, 16)
TEXT_COLOR = (255,255,255)

class Graph(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running=True
        
        pygame.display.init()
        pygame.font.init()
        
        self.offset = pygame.display.get_surface().get_size()[1]
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + self.offset))
        
        self.scale = [5*4,  8*4]    # 16x2 zeichen, 4 als skalierung, aus Virtual LCD
        self.font = pygame.font.SysFont("monospace", self.scale[1])
        
        self.show_help = False
        self.help_msg = "Dies ist der GRAPH der Temperatur\nZeitraum: 1:30h\nAuflösung: 600 Werte/h"
        
        self.data = ['0'] * 900# 600 messungen pro std, 1.5h verlauf
        
    def run(self):
        last_time = pygame.time.get_ticks()
        while self.running:
            time_now = pygame.time.get_ticks()
            time_elapsed = time_now - last_time
            last_time = time_now
            
            self.update(time_elapsed)
            self.render()
            
            pygame.display.update()
            time.sleep(0.5)
            
    def update(self, time_elapsed):
        for event in pygame.event.get():
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                if event.key == pygame.K_F1 and event.type == pygame.KEYDOWN:
                    self.show_help = not self.show_help

            elif event.type == pygame.QUIT:
                self.running = False


    def render(self):
        if self.show_help:
            #self.screen.fill(TEXT_BACKGROUND)
            pygame.draw.rect(self.screen, TEXT_BACKGROUND, (0,self.offset,SCREEN_WIDTH,SCREEN_HEIGHT))
            
            for l, line in enumerate([s.replace("\t","") for s in self.help_msg.split("\n")]):
                surf = self.font.render(line, True, TEXT_COLOR, TEXT_BACKGROUND)
                self.screen.blit(surf, (10, self.offset + 15 * l + 10) )

        else:
            #self.screen.fill(BACKGROUND_COLOR)
            pygame.draw.rect(self.screen, BACKGROUND_COLOR, (0,self.offset,SCREEN_WIDTH,SCREEN_HEIGHT))

            
            #lineThickness = 2
            #pygame.draw.lines(screen, color, False, points, lineThickness)
            
            pygame.display.update()
            
    def addDataPoint(timeInSec, Temp):
        timeToLast = timeInSec - self.data[-1].x 
        if timeToLast < 5 or timeToLast > 7:
            print("DataPoint not added To Graph. needs to be in interval of 5 to 7 sec to last point")
        else:
            self.data = self.data[1:].append(Vector(timeInSec, Temp))
            
