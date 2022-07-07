'''
Item
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Loads various menu types
'''
import pygame
from pygame.locals import *
from Util import *
from multiprocessing import sys
from Game import Game
from Options import Options
#from Unit import UnitGenerator

TILE_HEIGHT = 32
TILE_WIDTH = 32

font = pygame.font.Font(pygame.font.match_font('calibri',bold=True), 22)
mainFont = pygame.font.Font(pygame.font.match_font('calibri',bold=True,italic=True), 60)
mainClock = pygame.time.Clock()
clockSpeed = 30


button_color = (195, 0, 0)
menu_color = (175, 0, 0)
game = Game()


def start_loop():
    try:
        game.reset_game()
    except Exception as e:
        print("Something went wrong in game reset:",e)
    #try:
    game.game_loop()
    #except Exception as e:
    #    print("Something went wrong in game loop:",e)
    
def change_map():
    if game.maps.getMapName() == "Map 1":
        game.setMap("Map 2")
    else:
        game.setMap("Map 1")        
    
def get_keys(selected, options, mainmenu=True):
    click = False
    running = True
    for event in pygame.event.get():
        if event.type == QUIT:
            if not mainmenu:
                pygame.quit()
                sys.exit(0)
            else:
                running = False
        if event.type == KEYDOWN:
            if event.key == Options.BACK and not mainmenu:
                running = False
            if event.key == Options.ACTION:
                click = True
            if event.key == Options.LEFT:
                if not mainmenu:
                    selected -= 1
                    if selected < 1:
                        selected = 1
            if event.key == Options.RIGHT:
                if not mainmenu:
                    selected += 1
                    if selected > options:
                        selected = options
            if event.key == Options.UP:
                if mainmenu:
                    selected -= 1
                    if selected < 1:
                        selected = 1
                else:
                    selected -= 2
                    if selected < 1:
                        selected = 1
            if event.key == Options.DOWN:
                if mainmenu:
                    selected += 1
                    if selected > options:
                        selected = options
                else:
                    selected += 2
                    if selected > options:
                        selected = options
    return [click, running, selected]

def save_menu(screen):
    count = 3    
    saving =  True
    load = False
    click = False
    selected = 1
    options = 2 + count
    
    text = ""
    
    alphad = 90
    flip = -1
    while saving:
        w, h = pygame.display.get_surface().get_size()
        if load:
            screen.fill((40, 130, 70))
        else:
            screen.fill((40, 70, 130))
        
        alphad += 2*flip
        if alphad < 50:
            flip = 1
        elif alphad > 120:
            flip = -1
        
        barSize = h/20
        
        titlebar = pygame.Surface((w, barSize))
        titlebar.fill((0, 0, 0))
        screen.blit(titlebar,(0, 0))   
        if load:
            draw_la_text('Select File to Load', font, (255, 255, 255), screen, 0, 0)   
        else: 
            draw_la_text('Select File to Save', font, (255, 255, 255), screen, 0, 0)   
        draw_ra_text(text, font, (255, 255, 255), screen, w, 0) 
        
        buttonbar = pygame.Surface((w, barSize))
        buttonbar.fill((0, 0, 0))
        screen.blit(buttonbar,(0, h-barSize))  
        
        back_button = pygame.Rect(barSize/6, h-11*barSize/12, barSize*3, barSize-barSize/6)
        load_button = pygame.Rect(w-barSize*3-barSize/6, h-11*barSize/12, barSize*3, barSize-barSize/6)
        pygame.draw.rect(screen, (140,70,70), back_button)
        pygame.draw.rect(screen, (70,140,70), load_button)
        draw_text('Back', font, (0, 0, 0), screen, barSize*1.5+barSize/6, h-11*barSize/12)  
        if not load:
            draw_text("Switch to load", font, (0, 0, 0), screen, w+barSize*1.5-barSize*3-barSize/6, h-11*barSize/12)  
        else:
            draw_text("Switch to save", font, (0, 0, 0), screen, w+barSize*1.5-barSize*3-barSize/6, h-11*barSize/12)  
            
        draw_text('Note: Game auto saves into a separate slot after every battle', font, (150, 200, 150), screen, w/2, h-11*barSize/12) 
        
        hs = round(h - barSize*2)
        hs = hs - hs/2
        displayh = hs / (count/2)
        displayw = w / 1.5
        
        borderWidth = 2
        i = 0
        while i < count:
            x = w/6
            y = displayh*i + barSize
            
            background = pygame.Surface((displayw-borderWidth*2, displayh-borderWidth*2))
            background.set_alpha(180)
            if load:
                background.fill((120, 220, 170))
            else:
                background.fill((120, 170, 220))
            screen.blit(background,(x+borderWidth, y+borderWidth)) 
            draw_text('Slot {}'.format(i+1), mainFont, (0, 0, 0), screen, x+borderWidth+displayw/2, y+displayh/3)  
            i += 1
            #lines = 3
            #displayOffset = displayh/lines
            
        # Check for key presses
        sselected = selected
        click, saving, selected = get_keys(selected, options, mainmenu=False)
        if abs(selected - sselected) > 1:
            if selected > sselected:
                selected -= 1
            else:
                selected += 1
        
        if selected < options-1:
            selectedHighlight = pygame.Surface((displayw-borderWidth*2, displayh-borderWidth*2))
            selectedHighlight.set_alpha(alphad)
            selectedHighlight.fill((200, 200, 200))
            x = w/6
            y = displayh*(selected-1) + barSize
            screen.blit(selectedHighlight,(x+borderWidth, y+borderWidth)) 
            if click:
                if not load:
                    save_file(game.units,'save{}'.format(selected))
                    text = "Saved in slot {}".format(selected)
                else:
                    game.units = load_file('save{}'.format(selected))
                    text = "Loaded data from slot {}".format(selected)
        else:
            selectedHighlight = pygame.Surface((barSize*3, barSize-barSize/6))
            selectedHighlight.set_alpha(alphad)
            selectedHighlight.fill((200, 200, 200))
            if selected == options-1:
                screen.blit(selectedHighlight,(barSize/6, h-11*barSize/12)) 
            elif selected == options:
                screen.blit(selectedHighlight,(w-barSize*3-barSize/6, h-11*barSize/12)) 
                
            if click and selected == options-1:
                saving = False
            elif click and selected == options:
                load = not load
        
        pygame.display.flip()
        mainClock.tick(clockSpeed)
        
def char_select_menu(screen):
    maxChar = 6
    count = UnitGenerator.unit_classes.__len__()
    chosenChars = []
    
    with open('../assets/characters/selected.txt') as f:
        lines = f.readlines()
    for line in lines:
        chosenChars.append(line.strip())
    print(chosenChars)
    
    selecting =  True
    click = False
    selected = 1
    options = 2 + count
    
    alphad = 90
    flip = -1
    while selecting:
        w, h = pygame.display.get_surface().get_size()
        screen.fill((255,255,255))
        
        alphad += 2*flip
        if alphad < 50:
            flip = 1
        elif alphad > 120:
            flip = -1
        
        barSize = h/20
        
        titlebar = pygame.Surface((w, barSize))
        titlebar.fill((0, 0, 0))
        screen.blit(titlebar,(0, 0))    
        draw_la_text('Select {} More Characters'.format(maxChar-chosenChars.__len__()), font, (255, 255, 255), screen, 0, 0)   
        draw_ra_text('{} are curently selected out of {}'.format(chosenChars.__len__(),maxChar), font, (255, 255, 255), screen, w, 0) 
        
        buttonbar = pygame.Surface((w, barSize))
        buttonbar.fill((0, 0, 0))
        screen.blit(buttonbar,(0, h-barSize))  
        
        #back_button = pygame.Rect(w-buttonSize, buttonStart, barSize*3, barSize-barSize/6)
        back_button = pygame.Rect(barSize/6, h-11*barSize/12, barSize*3, barSize-barSize/6)
        accept_button = pygame.Rect(w-barSize*3-barSize/6, h-11*barSize/12, barSize*3, barSize-barSize/6)
        pygame.draw.rect(screen, (70,140,70), accept_button)
        pygame.draw.rect(screen, (140,70,70), back_button)
        draw_text('Back'.format(maxChar-chosenChars.__len__()), font, (0, 0, 0), screen, barSize*1.5+barSize/6, h-11*barSize/12)  
        draw_text('Accept'.format(maxChar-chosenChars.__len__()), font, (0, 0, 0), screen, w+barSize*1.5-barSize*3-barSize/6, h-11*barSize/12)  
        
        hs = round(h - barSize*2)
        displayh = hs / (count/2)
        displayw = w / 2
        
        borderWidth = 2
        i = 0
        align = 0
        current = 0
        for unit in UnitGenerator.unit_classes:
            imageFile = '../assets/characters/' + unit.lower() +'.png'
            image = pygame.image.load(imageFile)
            image = pygame.transform.scale(image, (displayh-borderWidth*2,displayh-borderWidth*2))
            imageborder = pygame.Surface((displayh-borderWidth*2, displayh-borderWidth*2))
            imageborder.set_alpha(150)
            x = displayw*align
            y = displayh*i + barSize
            
            if click and selected-1 == current:
                if unit in chosenChars:
                    chosenChars.remove(unit)
                elif chosenChars.__len__() < maxChar:
                    chosenChars.append(unit)
            
            background = pygame.Surface((displayw-borderWidth*2, displayh-borderWidth*2))
            background.set_alpha(180)
            if unit in chosenChars:
                imageborder.fill((77, 150, 86))
                background.fill((67, 140, 76))
            else:
                imageborder.fill((180, 87, 96))
                background.fill((170, 77, 86))
            
            screen.blit(background,(x+borderWidth, y+borderWidth)) 
            screen.blit(imageborder,(x+borderWidth, y+borderWidth)) 
            screen.blit(image,(x+borderWidth, y+borderWidth)) 
            lines = 8
            displayOffset = displayh/lines
            cinfo = next(x for x in game.units if x.name == 'The ' + unit)
            draw_la_text('{}'.format(cinfo.name), font, (0, 0, 0), screen, x+2*borderWidth+image.get_width(), y+borderWidth)  
            draw_ra_text('{} EXP'.format(cinfo.exp), font, (0, 0, 0), screen, x+displayw-borderWidth, y+borderWidth)  
            
            
            draw_la_text('Lv. {} {}'.format(cinfo.level, cinfo.unitClass, cinfo.exp), font, (0, 0, 0), screen, x+2*borderWidth+image.get_width(), y+borderWidth+displayOffset)  
            draw_ra_text('{}/{} HP'.format(cinfo.stats["HP"], cinfo.max_stats["HP"]), font, (0, 0, 0), screen, x+displayw-borderWidth, y+borderWidth+displayOffset) 
            
            ra_adjust = 2*borderWidth+image.get_width()+(2*borderWidth+image.get_width())/1.5-10
            
            draw_la_text('STR', font, (0, 0, 0), screen, x+2*borderWidth+image.get_width(), y+borderWidth+displayOffset*2)
            draw_la_stat('{}/{}'.format(cinfo.stats["str"], cinfo.max_stats["str"]), font, (0, 0, 0), screen, x+2*borderWidth+image.get_width()+50, y+borderWidth+displayOffset*2)
            draw_la_text('MAG', font, (0, 0, 0), screen, x+ra_adjust, y+borderWidth+displayOffset*2)
            draw_la_stat('{}/{}'.format(cinfo.stats["mag"], cinfo.max_stats["mag"]), font, (0, 0, 0), screen, x+ra_adjust+60, y+borderWidth+displayOffset*2)
              
            draw_la_text('SKL', font, (0, 0, 0), screen, x+2*borderWidth+image.get_width(), y+borderWidth+displayOffset*3)
            draw_la_stat('{}/{}'.format(cinfo.stats["skl"], cinfo.max_stats["skl"]), font, (0, 0, 0), screen, x+2*borderWidth+image.get_width()+50, y+borderWidth+displayOffset*3)
            draw_la_text('SPD', font, (0, 0, 0), screen, x+ra_adjust, y+borderWidth+displayOffset*3)
            draw_la_stat('{}/{}'.format(cinfo.stats["spd"], cinfo.max_stats["spd"]), font, (0, 0, 0), screen, x+ra_adjust+60, y+borderWidth+displayOffset*3)
              
            draw_la_text('DEF', font, (0, 0, 0), screen, x+2*borderWidth+image.get_width(), y+borderWidth+displayOffset*4) 
            draw_la_stat('{}/{}'.format(cinfo.stats["def"], cinfo.max_stats["def"]), font, (0, 0, 0), screen, x+2*borderWidth+image.get_width()+50, y+borderWidth+displayOffset*4) 
            draw_la_text('RES', font, (0, 0, 0), screen, x+ra_adjust, y+borderWidth+displayOffset*4) 
            draw_la_stat('{}/{}'.format(cinfo.stats["res"], cinfo.max_stats["res"]), font, (0, 0, 0), screen, x+ra_adjust+60, y+borderWidth+displayOffset*4) 
             
            draw_la_text('LCK', font, (0, 0, 0), screen, x+2*borderWidth+image.get_width(), y+borderWidth+displayOffset*5)  
            draw_la_stat('{}/{}'.format(cinfo.stats["lck"], cinfo.max_stats["lck"]), font, (0, 0, 0), screen, x+2*borderWidth+image.get_width()+50, y+borderWidth+displayOffset*5)  
            draw_la_text('MOV', font, (0, 0, 0), screen, x+ra_adjust, y+borderWidth+displayOffset*5)    
            draw_la_text('{}'.format(cinfo.mov), font, (0, 0, 0), screen, x+ra_adjust+60, y+borderWidth+displayOffset*5)  
            draw_la_text('{}'.format(cinfo.weapon.name), font, (0, 0, 0), screen, x+2*borderWidth+image.get_width(), y+borderWidth+displayOffset*6)  
            
            if align == 1:
                align = 0
                i += 1
            else:
                align = 1
            current += 1
        
        # Check for keys
        click, selecting, selected = get_keys(selected, options, mainmenu=False)
        
        if selected-1 < count:
            selectedHighlight = pygame.Surface((displayw-borderWidth*2, displayh-borderWidth*2))
            selectedHighlight.set_alpha(alphad)
            selectedHighlight.fill((200, 200, 200))
            tselect = selected - 1
            if tselect % 2 == 0:
                align = 0
            else:
                align = 1
            i = int(tselect/2)
            x = displayw*align
            y = displayh*i + barSize
            screen.blit(selectedHighlight,(x+borderWidth, y+borderWidth)) 
        else:
            selectedHighlight = pygame.Surface((barSize*3, barSize-barSize/6))
            selectedHighlight.set_alpha(alphad)
            selectedHighlight.fill((200, 200, 200))
            if selected == options-1:
                screen.blit(selectedHighlight,(barSize/6, h-11*barSize/12)) 
            elif selected == options:
                screen.blit(selectedHighlight,(w-barSize*3-barSize/6, h-11*barSize/12)) 
                
            if click and selected == options-1:
                selecting = False
            elif click and selected == options and chosenChars.__len__() > 0:
                selecting = False
                str = ""
                for char in chosenChars:
                    str += char + '\n'
                with open('../assets/characters/selected.txt', 'w') as f:
                    f.write(str)
        
        pygame.display.flip()
        mainClock.tick(clockSpeed)
     
def main_menu(screen):
    clockSpeed = game.clockSpeed
    game.units = load_file()
    click = False
    running = True
    w, h = pygame.display.get_surface().get_size()
    selected = 1
    options = 6
    
    pulse = 25
    switch = 1
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
        button_4 = pygame.Rect(w-buttonSize, buttonStart+buttonOffset*3, buttonSize, 50)
        button_5 = pygame.Rect(w-buttonSize, buttonStart+buttonOffset*4, buttonSize, 50)
        button_6 = pygame.Rect(w-buttonSize, buttonStart+buttonOffset*5, buttonSize, 50)
        
        pulse += 1*switch
        if pulse > 60:
            pulse = 60
            switch = -1
        elif pulse < 30:
            pulse = 30
            switch = 1
        
        if selected == 1:
            pygame.draw.rect(screen, (195+pulse,0+round(pulse*2.5),0+round(pulse*2.5)), button_1)
            if click:
                start_loop()
                save_file(game.units)
        else:
            pygame.draw.rect(screen, button_color, button_1)
            
        if selected == 2:
            pygame.draw.rect(screen, (195+pulse,0+round(pulse*2.5),0+round(pulse*2.5)), button_2)
            if click:
                try:
                    char_select_menu(screen)
                except Exception as e:
                    print("Something went wrong in character select:",e)
        else:
            pygame.draw.rect(screen, button_color, button_2)
            
        if selected == 3:
            pygame.draw.rect(screen, (195+pulse,0+round(pulse*2.5),0+round(pulse*2.5)), button_3)
            if click:
                try:
                    save_menu(screen)
                except Exception as e:
                    print("Something went wrong in save menu:",e)
        else:
            pygame.draw.rect(screen, button_color, button_3)
            
        if selected == 4:
            pygame.draw.rect(screen, (195+pulse,0+round(pulse*2.5),0+round(pulse*2.5)), button_4)
            if click:
                try:
                    change_map()
                except Exception as e:
                    print("Something went wrong when changing maps:",e)
        else:
            pygame.draw.rect(screen, button_color, button_4)

        if selected == 5:
            pygame.draw.rect(screen, (195+pulse,0+round(pulse*2.5),0+round(pulse*2.5)), button_5)
            if click:
                running = False #TODO: OPTIONS
        else:
            pygame.draw.rect(screen, button_color, button_5)
            
        if selected == 6:
            pygame.draw.rect(screen, (195+pulse,0+round(pulse*2.5),0+round(pulse*2.5)), button_6)
            if click:
                running = False
        else:
            pygame.draw.rect(screen, button_color, button_6)
            
        draw_text('Start Game', font, (255, 255, 255), screen, w-buttonSize/2, buttonStart)
        draw_text('Set Characters', font, (255, 255, 255), screen, w-buttonSize/2, buttonStart+buttonOffset)
        draw_text('Save/Load', font, (255, 255, 255), screen, w-buttonSize/2, buttonStart+buttonOffset*2)
        draw_text('Change Map', font, (255, 255, 255), screen, w-buttonSize/2, buttonStart+buttonOffset*3)
        draw_text('Options', font, (255, 255, 255), screen, w-buttonSize/2, buttonStart+buttonOffset*4)
        draw_text('Quit Game', font, (255, 255, 255), screen, w-buttonSize/2, buttonStart+buttonOffset*5)
 
        # Check for keys
        click, running, selected = get_keys(selected, options)
 
        pygame.display.flip()
        mainClock.tick(clockSpeed)
        