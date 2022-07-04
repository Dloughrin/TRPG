'''
Main
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Open GUI and start game
'''
import pygame
from pygame.locals import *
from multiprocessing import sys
from GameMap import GameMap
from InterpretMap import TileMap
from Options import Options
from Unit import UnitGenerator
from CombatManager import CombatManager
import random

class Cursor:
    def __init__(self, image, cursorx=0, cursory=0):
        self.icon = pygame.image.load(image)
        self.x = cursorx
        self.y = cursory
        self.a = 100
        self.move_delay = 0;
        self.move_delay_reduce = 0
        
    def set_alpha(self):
        self.icon.set_alpha(self.a)
        

class Game:
    def __init__(self, TILE_WIDTH=32, TILE_HEIGHT=32):
        self.maps = GameMap()
        self.TILE_WIDTH = TILE_WIDTH
        self.TILE_HEIGHT = TILE_HEIGHT
        self.ADJUSTED_TILE_WIDTH = TILE_WIDTH + 16
        self.ADJUSTED_TILE_HEIGHT = TILE_HEIGHT + 16
        
        self.running = False
        pygame.display.set_caption("Tile Trial")
        self.reset_game()
    
    def setMap(self, mapName):
        self.maps.setMap(mapName)
        self.dimensions = self.maps.getMapDimensions()
        
    def load_units(self):
        charNames = []
        with open('../assets/characters/selected.txt') as f:
            lines = f.readlines()
            for line in lines:
                newLine = line.strip()
                charNames.append(newLine)
        
        chars = []
        for charName in charNames:  
            tchar = UnitGenerator.create_unit('The ' + charName, charName, '../assets/characters/' + charName.lower() +'Token.png', '../assets/characters/' + charName.lower() + '.png')     
            # tchar = MagicUnit("The " + charName, charName, 0, 0, [20,20,20,20,20,20,20,20], [4,0,0,0,0,0,0,0], '../assets/characters/' + charName +'Token.png', '../assets/characters/' + charName + '.png')
            tchar.token = pygame.transform.scale(tchar.token, (self.ADJUSTED_TILE_WIDTH,self.ADJUSTED_TILE_HEIGHT))
            #print(tchar.name)
            #print(tchar.stats)
            #print(tchar.max_stats)
            #print(tchar.growths)
            chars.append(tchar)
        return chars
    
    def load_enemies(self, count):
        self.combat_manager.enemies = []
        enemy_types = ["Bandit", "Cultist", "Paladin"]
        primary = int(random.randrange(0, 3))
        
        tchar = UnitGenerator.create_unit('The ' + enemy_types[primary], enemy_types[primary], '../assets/enemies/' + enemy_types[primary].lower() +'Token.png', '../assets/enemies/' + enemy_types[primary].lower() + '.png')  
        tchar.token = pygame.transform.scale(tchar.token, (self.ADJUSTED_TILE_WIDTH,self.ADJUSTED_TILE_HEIGHT))
        self.combat_manager.enemies.append(tchar)
        
        for x in range(1,count):
            etype = int(random.randrange(0, 3))
            if not etype == primary:
                etype = int(random.randrange(0, 3))
                
            tchar = UnitGenerator.create_unit('The ' + enemy_types[etype], enemy_types[etype], '../assets/enemies/' + enemy_types[etype].lower() +'Token.png', '../assets/enemies/' + enemy_types[etype].lower() + '.png')  
            tchar.token = pygame.transform.scale(tchar.token, (self.ADJUSTED_TILE_WIDTH,self.ADJUSTED_TILE_HEIGHT))
            self.combat_manager.enemies.append(tchar)
    
    def reset_game(self):
        characters = self.load_units()
        self.character = characters[0]
        self.combat_manager = CombatManager(characters)
    
        self.dimensions = self.maps.getMapDimensions()
        self.window = pygame.display.set_mode((self.dimensions[0]*self.ADJUSTED_TILE_WIDTH, self.dimensions[1]*self.ADJUSTED_TILE_HEIGHT))
        self.cursor = Cursor('../assets/reticle.png', self.dimensions[0]*self.ADJUSTED_TILE_WIDTH/2, self.dimensions[1]*self.ADJUSTED_TILE_HEIGHT/2)
        self.cursor.icon = pygame.transform.scale(self.cursor.icon, (self.ADJUSTED_TILE_WIDTH,self.ADJUSTED_TILE_HEIGHT))
        
    
    def game_loop(self):
        clock = pygame.time.Clock()
        currentMap = self.maps.getCurrentMap()
        currentTiles = self.maps.currentTileSet
        self.myTiles = TileMap(currentMap[1])
        
        # For keeping track of characters
        self.spriteMap = []
        x = 0
        i = 0
        enemyCount = 0
        
        for tile in currentMap[1]:
            spriteLine = []
            y = 0
            for t in tile:
                # If the last character of the string is C, it indicates a character spawn spot. if E, it's an enemy spawn spot
                if t[-1] == 'C':
                    spriteLine.append('c')
                    if i < self.combat_manager.characters.__len__():
                        self.combat_manager.characters[i].move(x,y);
                        i += 1
                elif t[-1] == 'E':
                    spriteLine.append('e')
                    enemyCount += 1
                elif t[-1] == 'B':
                    spriteLine.append('e')
                    enemyCount += 1
                else:
                    spriteLine.append('n')
                y += 1
            x += 1
            self.spriteMap.append(spriteLine)
            
            
        self.load_enemies(enemyCount) 
        
        ei = 0
        x = 0
        for tile in currentMap[1]:
            spriteLine = []
            y = 0
            for t in tile:
                if t[-1] == 'E' and ei < self.combat_manager.enemies.__len__():
                    z = self.combat_manager.place_enemy(ei)
                    self.combat_manager.enemies[z].move(x,y);
                    ei += 1
                elif t[-1] == 'B':
                    self.combat_manager.enemies[0].move(x,y);
                y += 1
            x += 1
              
        
        self.cursor.x = self.character.x * self.ADJUSTED_TILE_WIDTH
        self.cursor.y = self.character.y * self.ADJUSTED_TILE_HEIGHT
        
        flip = 0
        currentCharI = 0
        currentEnemyI = 0
        
        self.running = True
        menu = False
        menuSelected = 1
        options = 1
        while self.running:
            clicked = False
            # Redraw map
            self.window.fill((255, 255, 255))
            self.draw_map(currentTiles, self.myTiles)
            
            cx = int(self.cursor.x/self.ADJUSTED_TILE_WIDTH)
            cy = int(self.cursor.y/self.ADJUSTED_TILE_HEIGHT)
            if self.spriteMap[cx][cy] == 'c' and not self.character.moving and not self.character.attacking:
                for char in self.combat_manager.characters:
                    if char.x == cx and char.y == cy:
                        self.character = char
                        break
                
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
                if self.combat_manager.current_turn() == CombatManager.PLAYER_TURN:
                    if event.type == KEYDOWN:
                        #if event.key == K_ESCAPE:
                            #self.running = False
                        if event.key == Options.ACTION:
                            if self.character.moving == True:
                                self.spriteMap[self.character.originalX][self.character.originalY] = 'n'
                                self.spriteMap[self.character.x][self.character.y] = 'c'
                                self.character.moving = False
                                self.character.moved = True
                                if self.character.acted:
                                    self.character.originalX = -1
                                    self.character.originalY = -1
                                self.cursor.x = self.character.x * self.ADJUSTED_TILE_WIDTH
                                self.cursor.y = self.character.y * self.ADJUSTED_TILE_HEIGHT
                                menuSelected = 1
                                if not self.character.acted or not self.character.moved:
                                    menu = True
                            elif self.character.attacking == True:
                                for target in self.combat_manager.enemies:
                                    if target.x == cx and target.y == cy and not target.name == self.character.name:
                                        CombatManager.fight(self.character,target) 
                                        menuSelected = 1
                                        self.character.attacking = False
                                        self.character.acted = True
                                        self.character.moved = True
                                        self.character.originalX = -1
                                        self.character.originalY = -1
                                        # Display exp results and small animation for attacking
                                        if target.dead:
                                            self.character.add_exp(target.level,1)
                                            self.combat_manager.enemies.remove(target)
                                            self.spriteMap[cx][cy] = 'n'
                                            if self.combat_manager.enemies.__len__() <= 0:
                                                # You win
                                                self.running = False
                                        else:
                                            self.character.add_exp(target.level,0)
                                        if self.character.dead:
                                            self.spriteMap[self.character.x][self.character.y] = 'n'
                                            self.combat_manager.characters.remove(self.character)
                                            if self.combat_manager.characters.__len__() > 0:
                                                self.character = self.combat_manager.characters[0]
                                            else:
                                                # Game over
                                                self.running = False
                                        break
                            elif menu == False:
                                menu = True
                            else:
                                clicked = True
                        if event.key == Options.BACK:
                            if self.character.moving == True:
                                self.character.move(self.character.originalX,self.character.originalY)
                                self.spriteMap[self.character.x][self.character.y] = 'c'
                                self.character.originalX = -1
                                self.character.originalY = -1
                                self.character.moving = False
                                self.cursor.x = self.character.x * self.ADJUSTED_TILE_WIDTH
                                self.cursor.y = self.character.y * self.ADJUSTED_TILE_HEIGHT
                                menu = True
                                menuSelected = 1
                            elif self.character.attacking == True:
                                if not self.character.originalX == -1:
                                    self.spriteMap[self.character.x][self.character.y] = 'n'
                                    self.character.move(self.character.originalX,self.character.originalY)
                                    self.spriteMap[self.character.x][self.character.y] = 'c'
                                    self.character.originalX = -1
                                    self.character.originalY = -1
                                    self.character.moved = False
                                    self.cursor.x = self.character.x * self.ADJUSTED_TILE_WIDTH
                                    self.cursor.y = self.character.y * self.ADJUSTED_TILE_HEIGHT
                                menu = True
                                self.character.attacking = False
                                menuSelected = 1
                            elif menu == True and not self.character.moved and not self.character.acted:
                                menu = False
                                menuSelected = 1
                            elif menu == True:
                                menu = False
                                menuSelected = 1
                                if not self.character.originalX == -1:
                                    self.spriteMap[self.character.x][self.character.y] = 'n'
                                    self.character.move(self.character.originalX,self.character.originalY)
                                    self.spriteMap[self.character.x][self.character.y] = 'c'
                                    self.character.originalX = -1
                                    self.character.originalY = -1
                                    self.character.moved = False
                                    self.cursor.x = self.character.x * self.ADJUSTED_TILE_WIDTH
                                    self.cursor.y = self.character.y * self.ADJUSTED_TILE_HEIGHT
                                
                        if event.key == Options.UP and menu == True:
                            menuSelected -= 1
                            if menuSelected < 1:
                                menuSelected = 1
                        if event.key == Options.DOWN and menu == True:
                            menuSelected += 1
                            if menuSelected > options:
                                menuSelected = options
                                
            cx = int(self.cursor.x/self.ADJUSTED_TILE_WIDTH)
            cy = int(self.cursor.y/self.ADJUSTED_TILE_HEIGHT)
                                
            if self.combat_manager.current_turn() == CombatManager.ENEMY_TURN:
                for char in self.combat_manager.enemies:
                    # Set [ type of action , location for movement , target for attack ]
                    set = self.combat_manager.ai(self.spriteMap,self.myTiles, char)
                    # NPC decides to move twice
                    if set[0] == CombatManager.MOVE_MOVE:
                        char.move(set[1][0],set[1][1])
                    # NPC decides to attack
                    elif set[0] == CombatManager.ACTION_MOVE or set[0] == CombatManager.ACTION:
                        target = self.combat_manager.characters[set[2]]
                        # NPC also decides to move
                        if set[0] == CombatManager.ACTION_MOVE:
                            char.move(set[1][0],set[1][1])
                        CombatManager.fight(char,target) 
                        if target.dead:
                            self.spriteMap[target.x][target.y] = 'n'
                            self.combat_manager.characters.remove(target)
                            if self.combat_manager.characters.__len__() > 0:
                                self.character = self.combat_manager.characters[0]
                            else:
                                # Game over
                                self.running = False
                        elif char.dead:
                            self.spriteMap[char.x][char.y] = 'n'
                            self.combat_manager.enemies.remove(char)
                            # Defeated the attacking enemy, 100% exp
                            target.add_exp(target.level,1)
                            if self.combat_manager.enemies.__len__() <= 0:
                                # You win
                                self.running = False
                        elif not target.can_attack_stationary(char.x,char.y):
                            # Survived an attack, but enemy survived too. Reduced exp
                            target.add_exp(target.level,0)
                        else:
                            # Survied an attack, but couldn't attack back. Heavily reduced exp
                            target.add_exp(0,0)
                            
                        
                self.combat_manager.next_turn()
                
                
            # Display all characters
            for char in self.combat_manager.characters:
                if char.moved and char.acted and not char.dead:
                    self.window.blit(Game.grayscale_image(char.token),(char.x*self.ADJUSTED_TILE_WIDTH, char.y*self.ADJUSTED_TILE_HEIGHT)) 
                elif not char.dead:
                    self.window.blit(char.token,(char.x*self.ADJUSTED_TILE_WIDTH, char.y*self.ADJUSTED_TILE_HEIGHT))  
                    
            for char in self.combat_manager.enemies:
                if char.moved and char.acted and not char.dead:
                    self.window.blit(Game.grayscale_image(char.token),(char.x*self.ADJUSTED_TILE_WIDTH, char.y*self.ADJUSTED_TILE_HEIGHT)) 
                elif not char.dead:
                    self.window.blit(char.token,(char.x*self.ADJUSTED_TILE_WIDTH, char.y*self.ADJUSTED_TILE_HEIGHT))   
                
            # Draw menu if action button is clicked. pass in object clicked on to figure out which options show up
            if not self.combat_manager.current_turn() == CombatManager.PLAYER_TURN:
                flip = self.reticle_idle(flip)
            elif menu == False:
                flip, currentEnemyI, currentCharI = self.cursor_movement(flip,currentEnemyI, currentCharI)
            else:
                flip = self.reticle_idle(flip)
                options, menu = self.draw_menu(menuSelected, self.spriteMap[int(self.cursor.x/self.ADJUSTED_TILE_WIDTH)][int(self.cursor.y/self.ADJUSTED_TILE_HEIGHT)], clicked)
            
            
            # Draw cursor on top
            self.window.blit(self.cursor.icon,(self.cursor.x, self.cursor.y))
            
            if self.character.moving:
                sidebar = pygame.Surface((self.ADJUSTED_TILE_WIDTH, self.ADJUSTED_TILE_HEIGHT))
                sidebar.set_alpha(100)
                x = 0
                for xline in self.myTiles.tiles:
                    y = 0
                    for yline in xline:
                        if self.character.can_move(x, y) and yline.block == 0:
                            sidebar.fill((33,237,217))
                            self.window.blit(sidebar,(x*self.ADJUSTED_TILE_WIDTH, y*self.ADJUSTED_TILE_HEIGHT))
                        elif self.character.can_attack(x, y):
                            sidebar.fill((220,20,20))
                            self.window.blit(sidebar,(x*self.ADJUSTED_TILE_WIDTH, y*self.ADJUSTED_TILE_HEIGHT))
                        y += 1
                    x += 1
                #self.window.blit(sidebar,(w-10-buttonSize, 0))  
            if self.character.attacking:
                sidebar = pygame.Surface((self.ADJUSTED_TILE_WIDTH, self.ADJUSTED_TILE_HEIGHT))
                sidebar.set_alpha(100)
                x = 0
                for xline in self.myTiles.tiles:
                    y = 0
                    for yline in xline:
                        if self.character.can_attack_stationary(x, y):
                            sidebar.fill((220,20,20))
                            self.window.blit(sidebar,(x*self.ADJUSTED_TILE_WIDTH, y*self.ADJUSTED_TILE_HEIGHT))
                        y += 1
                    x += 1
                
            
            if (self.spriteMap[cx][cy] == 'c' or self.spriteMap[cx][cy] == 'e') and not self.character.moving:
                if self.spriteMap[cx][cy] == 'c':
                    for char in self.combat_manager.characters:
                        if char.x == cx and char.y == cy and not char.dead:
                            self.draw_stats(char) 
                            break
                elif self.spriteMap[cx][cy] == 'e':
                    for char in self.combat_manager.enemies:
                        if char.x == cx and char.y == cy and not char.dead:
                            self.draw_stats(char,1) 
                            break
            
            # Update display
            pygame.display.flip()
            clock.tick(15)
    
    # Found with some googling. Adjusted so it would copy the surface instead of adjusting the image directly
    @staticmethod  
    def grayscale_image(surface):
        width, height = surface.get_size()
        nsurface = surface.copy()
        for x in range(width):
            for y in range(height):
                red, green, blue, alpha = nsurface.get_at((x, y))
                L = 0.3 * red + 0.59 * green + 0.11 * blue
                gs_color = (L, L, L, alpha)
                nsurface.set_at((x, y), gs_color)
        return nsurface
            
    def draw_stats(self, character, enemy=0):
        optionsW = 4
        optionsH = 4
        # Same thickness as the menu for each line. 4 lines
        height = (self.ADJUSTED_TILE_HEIGHT * 2/3) * optionsH
        # Same width as the menu for each option. maximum 4 options per line
        width = self.ADJUSTED_TILE_WIDTH * 2 * optionsW
        borderSize = 3
        
        statMenu = pygame.Surface((width, height))
        statMenu.set_alpha(180)
        if enemy == 0:
            statMenu.fill((67, 140, 76))
        else:
            statMenu.fill((170, 77, 86))
        
        border = pygame.Surface((width+borderSize*2, height+borderSize*2))
        border.set_alpha(180)
        border.fill((0, 0, 0))
        
        # Place the menu on the screen
        x = 0
        y = self.dimensions[1]*self.ADJUSTED_TILE_WIDTH - height
        if self.cursor.x < self.dimensions[0]*self.ADJUSTED_TILE_WIDTH / 2:
            x = self.dimensions[0]*self.ADJUSTED_TILE_WIDTH - width
        if self.cursor.y > self.dimensions[1]*self.ADJUSTED_TILE_HEIGHT / 2:
            y = 0
        
        # Place the menu and its border
        self.window.blit(border,(x-borderSize, y-borderSize)) 
        self.window.blit(statMenu,(x, y)) 
        
        '''
        Name, type, level
        current hp / max hp
        str skl res lck
        mag spd def mov
        '''
        statXOffset = width/optionsW
        statYOffset = height/optionsH
        font = pygame.font.SysFont(None, 30)
        
        # Line 1
        l1offset = width/2
        self.draw_la_text(character.name, font, (0, 0, 0), x+5, y+((height/optionsH)/2))
        self.draw_la_text("Lv. {} {}".format(character.level, character.unitClass), font, (0, 0, 0), x+l1offset, y+((height/optionsH)/2))
        
        # Line 2
        self.draw_la_text("{}/{} HP".format(character.currentHP,character.stats["HP"]), font, (0, 0, 0), x+5, y+statYOffset+((height/optionsH)/2))
        self.draw_la_text("{} EXP".format(character.exp), font, (0, 0, 0), x+l1offset, y+statYOffset+((height/optionsH)/2))
        
        # Line 3
        self.draw_la_text("{} STR".format(character.stats["str"]), font, (0, 0, 0), x+5, y+statYOffset*2+((height/optionsH)/2))
        self.draw_la_text("{} SKL".format(character.stats["skl"]), font, (0, 0, 0), x+5+statXOffset, y+statYOffset*2+((height/optionsH)/2))
        self.draw_la_text("{} RES".format(character.stats["res"]), font, (0, 0, 0), x+5+statXOffset*2, y+statYOffset*2+((height/optionsH)/2))
        self.draw_la_text("{} LCK".format(character.stats["lck"]), font, (0, 0, 0), x+5+statXOffset*3, y+statYOffset*2+((height/optionsH)/2))
        
        # Line 4
        self.draw_la_text("{} MAG".format(character.stats["mag"]), font, (0, 0, 0), x+5, y+statYOffset*3+((height/optionsH)/2))
        self.draw_la_text("{} SPD".format(character.stats["spd"]), font, (0, 0, 0), x+5+statXOffset, y+statYOffset*3+((height/optionsH)/2))
        self.draw_la_text("{} DEF".format(character.stats["def"]), font, (0, 0, 0), x+5+statXOffset*2, y+statYOffset*3+((height/optionsH)/2))
        self.draw_la_text("{} MOV".format(character.mov), font, (0, 0, 0), x+5+statXOffset*3, y+statYOffset*3+((height/optionsH)/2))
        
       
    def draw_la_text(self, text, font, color, x, y):
        textobj = font.render(text, 2, color)
        textrect = textobj.get_rect()
        #w = textobj.get_width()/2
        h = textobj.get_height()/2
        textrect.topleft = (x, y-h)
        self.window.blit(textobj, textrect) 
    
    def draw_text(self, text, font, color, x, y):
        textobj = font.render(text, 2, color)
        textrect = textobj.get_rect()
        w = textobj.get_width()/2
        h = textobj.get_height()/2
        textrect.topleft = (x-w, y-h)
        self.window.blit(textobj, textrect)
    
    def draw_menu(self, selected, objectClicked, clicked):
        menu = True
        font = pygame.font.SysFont(None, 30)
        # Generate list of options depending on what's on the square clicked
        options = self.__create_options(objectClicked)
        menuW = self.ADJUSTED_TILE_WIDTH * 2.7
        menuH = (self.ADJUSTED_TILE_HEIGHT * 2/3) * options.__len__()
        borderSize = 2
        actionMenu = pygame.Surface((menuW, menuH))
        actionMenu.set_alpha(180)
        actionMenu.fill((67, 140, 76))
        
        border = pygame.Surface((menuW+borderSize*2, menuH+borderSize*2))
        border.set_alpha(180)
        border.fill((0, 0, 0))
        
        # Place the menu on the screen
        w, h = pygame.display.get_surface().get_size()
        w += 1 # annoying warning gone
        x = self.cursor.x - menuW
        y = self.cursor.y + self.ADJUSTED_TILE_HEIGHT/2
        if x - self.ADJUSTED_TILE_WIDTH < 0:
            x = self.cursor.x + self.ADJUSTED_TILE_WIDTH
        if y + self.ADJUSTED_TILE_HEIGHT + menuH >= h:
            y = self.cursor.y - menuH + self.ADJUSTED_TILE_HEIGHT/2
            
        # Place the menu and its border
        self.window.blit(border,(x-borderSize, y-borderSize)) 
        self.window.blit(actionMenu,(x, y)) 
        
        # Place the buttons on the menu
        i = 1
        # How far to space the buttons from each other
        buttonOffset = menuH/options.__len__()
        for option in options:
            button = pygame.Surface((menuW, buttonOffset))
            button.fill((117, 190, 126))
            if(selected == i):
                button.set_alpha(180)
                if clicked:
                    menu = self.__do_option(option)
            else:
                button.set_alpha(0)
            self.window.blit(button,(x, y+buttonOffset*(i-1))) 
            self.draw_text(option, font, (0, 0, 0), x+menuW/2, y+buttonOffset*(i-1)+((menuH/options.__len__())/2))
            i += 1
            
        #pygame.draw.rect(self.window, (255,255,255), button_1)
        # Return length so that the main loop knows when to prevent increasing or decreasing the selection
        # Some menu actions will close the menu, so update it as appropriate 
        return [options.__len__(), menu]
    
    def __do_option(self, option):
        menu = True
        if option == 'Main Menu':
            self.running = False
        if option == 'Attack':
            menu = False
            self.character.attacking = True
        if option == 'Move':
            menu = False
            self.character.moving = True
            self.character.originalY = self.character.y
            self.character.originalX = self.character.x
            self.spriteMap[self.character.originalX][self.character.originalY] = 'n'
        if option == 'Move Action':
            menu = False
            self.character.moved = False
            self.character.acted = True
            self.character.moving = True
            self.character.originalY = self.character.y
            self.character.originalX = self.character.x
            self.spriteMap[self.character.originalX][self.character.originalY] = 'n'
        if option == 'End Turn':
            self.combat_manager.next_turn()
            menu = False
        if option == 'Cancel':
            menu = False
            
        return menu
    
    def __create_options(self, clickedObject):
        options = []
        if clickedObject == 'c':
            if not self.character.acted:
                options.append('Attack')
            if not self.character.moved:
                options.append('Move')
            elif not self.character.acted:
                options.append('Move Action')
            options.append('Unit Status')
        elif clickedObject == 'e':
            options.append('Unit Status')
        
        options.append('End Turn')
        options.append('Options')
        options.append('Main Menu')
        options.append('Cancel')
        return options
    
    def draw_map(self, currentTiles, myTiles):
        x = 0
        #FLIPPED ON DIAGONAL FOR MAPS
        while x < self.dimensions[1]:
            y = 0
            #tileLine = []
            while y < self.dimensions[0]:
                i = currentTiles.findKey(myTiles.tiles[x][y].getImage())
                tile = currentTiles.tiles[i]
                tile = pygame.transform.scale(tile, (self.ADJUSTED_TILE_WIDTH,self.ADJUSTED_TILE_HEIGHT))
                self.window.blit(tile,(x*self.ADJUSTED_TILE_WIDTH, y*self.ADJUSTED_TILE_HEIGHT))
                y += 1
                #tileLine.append(currentTiles.tileKeys[i])
            x += 1
    
    def reticle_idle(self, flip):
        if(flip == 0): 
            self.cursor.a -= 15
        else:
            self.cursor.a += 15
            
        if(self.cursor.a <= 50):
            self.cursor.a = 50
            flip = 1
        elif(self.cursor.a >= 255):
            self.cursor.a = 255
            flip = 0
        
        self.cursor.set_alpha()
        return flip
    
    def cursor_movement(self, flip, currentEnemyI, currentCharI):
            keys = pygame.key.get_pressed()
            w, h = pygame.display.get_surface().get_size()
            x1 = 0
            y1 = 0
            
            # While a key is being pressed, the delay between moving the cursor reduces. It's reset when no keys are being pressed
            if not any((keys[Options.LEFT], keys[Options.RIGHT], keys[Options.UP], keys[Options.DOWN], keys[Options.REWIND], keys[Options.NEXT])) or self.character.moving:
                self.cursor.move_delay_reduce = 0
                
                
            adjustX = int(self.cursor.x/self.ADJUSTED_TILE_WIDTH)
            adjustY = int(self.cursor.y/self.ADJUSTED_TILE_HEIGHT)
            if(self.cursor.move_delay <= 0 and any((keys[Options.LEFT], keys[Options.RIGHT], keys[Options.UP], keys[Options.DOWN], keys[Options.REWIND], keys[Options.NEXT]))):
                if keys[Options.NEXT]:
                    if self.spriteMap[int(self.cursor.x/self.ADJUSTED_TILE_WIDTH)][int(self.cursor.y/self.ADJUSTED_TILE_HEIGHT)] == 'e':
                        self.cursor.x = self.combat_manager.enemies[currentEnemyI].x * self.ADJUSTED_TILE_WIDTH
                        self.cursor.y = self.combat_manager.enemies[currentEnemyI].y * self.ADJUSTED_TILE_HEIGHT
                        currentEnemyI += 1
                        if currentEnemyI > self.combat_manager.enemies.__len__()-1:
                            currentEnemyI = 0
                    else:
                        self.cursor.x = self.combat_manager.characters[currentCharI].x * self.ADJUSTED_TILE_WIDTH
                        self.cursor.y = self.combat_manager.characters[currentCharI].y * self.ADJUSTED_TILE_HEIGHT
                        currentCharI += 1
                        if currentCharI > self.combat_manager.characters.__len__()-1:
                            currentCharI = 0
                    self.cursor.move_delay = 60 - self.cursor.move_delay_reduce
                elif keys[Options.REWIND]:
                    if self.spriteMap[int(self.cursor.x/self.ADJUSTED_TILE_WIDTH)][int(self.cursor.y/self.ADJUSTED_TILE_HEIGHT)] == 'e':
                        self.cursor.x = self.combat_manager.enemies[currentEnemyI].x * self.ADJUSTED_TILE_WIDTH
                        self.cursor.y = self.combat_manager.enemies[currentEnemyI].y * self.ADJUSTED_TILE_HEIGHT
                        currentEnemyI -= 1
                        if currentEnemyI < 0:
                            currentEnemyI = self.combat_manager.enemies.__len__() - 1
                    else:
                        self.cursor.x = self.combat_manager.characters[currentCharI].x * self.ADJUSTED_TILE_WIDTH
                        self.cursor.y = self.combat_manager.characters[currentCharI].y * self.ADJUSTED_TILE_HEIGHT
                        currentCharI -= 1
                        if currentCharI < 0:
                            currentCharI = self.combat_manager.characters.__len__() - 1
                    self.cursor.move_delay = 60 - self.cursor.move_delay_reduce
                elif keys[Options.LEFT] and (self.cursor.x-self.ADJUSTED_TILE_WIDTH) >= 0:
                    x1 -= 1
                    if self.character.moving:
                        if self.character.can_move(self.character.x-1, self.character.y):
                            if self.myTiles.tiles[int(adjustX-1)][int(adjustY)].block == 1:
                                if not self.spriteMap[adjustX-1][adjustY] == 'e':
                                    x1 += 1
                            elif self.character.can_move(adjustX-1, adjustY) and not self.spriteMap[adjustX-1][adjustY] == 'c':
                                self.character.move(int(adjustX-1),int(adjustY))
                        else:
                            x1 += 1    
                    self.cursor.move_delay = 60 - self.cursor.move_delay_reduce
                elif keys[Options.RIGHT] and (self.cursor.x+self.ADJUSTED_TILE_WIDTH) < w:
                    x1 += 1
                    if self.character.moving:
                        if self.character.can_move(self.character.x+1, self.character.y):
                            if self.myTiles.tiles[int(adjustX+1)][int(adjustY)].block == 1:
                                if not self.spriteMap[adjustX+1][adjustY] == 'e':
                                    x1 -= 1
                            elif self.character.can_move(adjustX+1, adjustY) and not self.spriteMap[adjustX+1][adjustY] == 'c':
                                self.character.move(int(adjustX+1),int(adjustY))
                        else:
                            x1 -= 1
                    self.cursor.move_delay = 60 - self.cursor.move_delay_reduce
                elif keys[Options.UP] and (self.cursor.y-self.ADJUSTED_TILE_HEIGHT) >= 0:
                    y1 -= 1
                    if self.character.moving:
                        if self.character.can_move(self.character.x, self.character.y-1):
                            if self.myTiles.tiles[int(adjustX)][int(adjustY-1)].block == 1:
                                if not self.spriteMap[adjustX][adjustY-1] == 'e':
                                    y1 += 1
                            elif self.character.can_move(adjustX, adjustY-1) and not self.spriteMap[adjustX][adjustY-1] == 'c':
                                self.character.move(int(adjustX),int(adjustY-1))
                        else:
                            y1 += 1
                    self.cursor.move_delay = 60 - self.cursor.move_delay_reduce
                elif keys[Options.DOWN] and (self.cursor.y+self.ADJUSTED_TILE_HEIGHT) < h:
                    y1 += 1
                    if self.character.moving:
                        if self.character.can_move(self.character.x, self.character.y+1):
                            if self.myTiles.tiles[int(adjustX)][int(adjustY+1)].block == 1:
                                if not self.spriteMap[adjustX][adjustY+1] == 'e':
                                    y1 -= 1
                            elif self.character.can_move(adjustX, adjustY+1) and not self.spriteMap[adjustX][adjustY+1] == 'c':
                                self.character.move(int(adjustX),int(adjustY+1))
                        else:
                            y1 -= 1
                    self.cursor.move_delay = 60 - self.cursor.move_delay_reduce
                    
                if any(keys):
                    self.cursor.move_delay_reduce += 15
                if self.cursor.move_delay_reduce > 60:
                    self.cursor.move_delay_reduce = 60
            else:
                self.cursor.move_delay -= 20
                
            self.cursor.y += y1*self.ADJUSTED_TILE_HEIGHT
            self.cursor.x += x1*self.ADJUSTED_TILE_WIDTH
            
            # After moving, change alpha of cursor
            return [self.reticle_idle(flip), currentEnemyI, currentCharI]
            