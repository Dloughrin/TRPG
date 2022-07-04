'''
Main
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Open GUI and start game
'''
import pygame
pygame.init()
from pygame.locals import *
from Game import Game
from Options import Options

TILE_HEIGHT = 32
TILE_WIDTH = 32

font = pygame.font.SysFont(None, 30)
mainFont = pygame.font.SysFont(None, 80, italic=True)
mainClock = pygame.time.Clock()

button_color = (205, 0, 0)
highlighted_button_color = (255, 125, 125)
menu_color = (175, 0, 0)

def start_loop():
    game.reset_game()
    game.game_loop()
    
def change_map():
    if game.maps.getMapName() == "Map 1":
        game.setMap("Map 2")
    else:
        game.setMap("Map 1")
        
    
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 3, color)
    w = textobj.get_width()/2
    h = textobj.get_height()/2
    textrect = textobj.get_rect()
    textrect.topleft = (x-w, y+h)
    surface.blit(textobj, textrect)
     
def main_menu(screen):
    click = False
    running = True
    w, h = pygame.display.get_surface().get_size()
    selected = 1
    options = 3
    while running:
        image = pygame.image.load('../assets/Map 2.png')
        screen.fill((255,255,255))
        image = pygame.transform.smoothscale(image, (w,h))
        screen.blit(image, (0,0))
 
        #mx, my = pygame.mouse.get_pos()
        buttonStart = h/4
        buttonOffset = 60
        buttonSize = 400
        
        
        sidebar = pygame.Surface((buttonSize + 100, h))
        sidebar.set_alpha(150)
        sidebar.fill((0, 0, 0))
        screen.blit(sidebar,(w-10-buttonSize, 0))    
        
        #menuBar = pygame.Rect(w-buttonSize, 20, buttonSize, 75)
        #pygame.draw.rect(screen, menu_color, menuBar)
        draw_text('Main Menu', mainFont, (255, 255, 255), screen, w-buttonSize/2, 20)   
        
        # x, y, width, height
        button_1 = pygame.Rect(w-buttonSize, buttonStart, buttonSize, 50)
        button_2 = pygame.Rect(w-buttonSize, buttonStart+buttonOffset, buttonSize, 50)
        button_3 = pygame.Rect(w-buttonSize, buttonStart+buttonOffset*2, buttonSize, 50)
        
        # if button_1.collidepoint((mx, my)):
        if selected == 1:
            pygame.draw.rect(screen, highlighted_button_color, button_1)
            if click:
                start_loop()
        else:
            pygame.draw.rect(screen, button_color, button_1)
            
        # if button_2.collidepoint((mx, my)):
        if selected == 2:
            pygame.draw.rect(screen, highlighted_button_color, button_2)
            if click:
                change_map()
        else:
            pygame.draw.rect(screen, button_color, button_2)
            
        if selected == 3:
            pygame.draw.rect(screen, highlighted_button_color, button_3)
            if click:
                running = False
        else:
            pygame.draw.rect(screen, button_color, button_3)

        draw_text('Start Game', font, (255, 255, 255), screen, w-buttonSize/2, buttonStart)
        draw_text('Change Map', font, (255, 255, 255), screen, w-buttonSize/2, buttonStart+buttonOffset)
        draw_text('Quit Game', font, (255, 255, 255), screen, w-buttonSize/2, buttonStart+buttonOffset*2)
 
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == Options.ACTION:
                    click = True
                if event.key == Options.UP:
                    selected -= 1
                    if selected < 1:
                        selected = 1
                if event.key == Options.DOWN:
                    selected += 1
                    if selected > options:
                        selected = options
            #if event.type == MOUSEBUTTONDOWN:
                #if event.button == 1:
                    #click = True
 
        pygame.display.flip()
        mainClock.tick(60)
        

if __name__ == "__main__":
    game = Game(TILE_WIDTH, TILE_HEIGHT)
    surface = game.window
    main_menu(surface)
    
    '''main_menu = pygame_menu.Menu('Main Menu', 600, 400,theme=pygame_menu.themes.THEME_BLUE)
    about_menu = pygame_menu.Menu('About Menu', 300, 300)
    main_menu.add.button('Start Game', start_loop)
    main_menu.add.button(about_menu.get_title(), about_menu)
    main_menu.mainloop(surface)'''