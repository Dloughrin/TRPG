'''
Main
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Maintain and set keybind options
'''

import pygame

class Options:
    KEYBOARD_UP = pygame.K_UP
    KEYBOARD_DOWN = pygame.K_DOWN
    KEYBOARD_LEFT = pygame.K_LEFT
    KEYBOARD_RIGHT = pygame.K_RIGHT
    KEYBOARD_ACTION = pygame.K_z
    KEYBOARD_BACK = pygame.K_x
    KEYBOARD_NEXT = pygame.K_v
    KEYBOARD_REWIND = pygame.K_c
    
    ALT_KEYBOARD_UP = pygame.K_w
    ALT_KEYBOARD_DOWN = pygame.K_s
    ALT_KEYBOARD_LEFT = pygame.K_a
    ALT_KEYBOARD_RIGHT = pygame.K_d
    
    
    UP = KEYBOARD_UP
    DOWN = KEYBOARD_DOWN
    LEFT = KEYBOARD_LEFT
    RIGHT = KEYBOARD_RIGHT
    ACTION = KEYBOARD_ACTION
    BACK = KEYBOARD_BACK
    
    #Cycling characters
    NEXT = KEYBOARD_NEXT
    REWIND = KEYBOARD_REWIND