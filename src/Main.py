'''
Main
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Open GUI and start game
'''
import pygame
pygame.init()
from Menus import main_menu, game 

if __name__ == "__main__":
    surface = game.window
    main_menu(surface)