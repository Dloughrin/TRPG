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
from aStar import astar_map
import random
import math

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
        self.clockSpeed = 60
        pygame.display.set_caption("Tile Trial")
        self.units = []
        self.load_units()
        self.reset_game()
    
    def setMap(self, mapName):
        self.maps.setMap(mapName)
        self.dimensions = self.maps.getMapDimensions()
        
    def load_units(self):
        for charName in UnitGenerator.unit_classes:  
            tchar = UnitGenerator.create_unit('The ' + charName, charName, '../assets/characters/' + charName.lower() +'Token.png', '../assets/characters/' + charName.lower() + '.png')
            self.units.append(tchar)
            
    def new_game(self):
        nunits = []
        for charName in UnitGenerator.unit_classes:  
            tchar = UnitGenerator.create_unit('The ' + charName, charName, '../assets/characters/' + charName.lower() +'Token.png', '../assets/characters/' + charName.lower() + '.png') 
            nunits.append(tchar)
        self.units = nunits
        self.reset_game()
    
    def load_team(self):
        charNames = []
        with open('../assets/characters/selected.txt') as f:
            lines = f.readlines()
            for line in lines:
                newLine = line.strip()
                charNames.append(newLine)
                
        chars = []
        for name in charNames:
            for char in self.units:
                if 'The ' + name == char.name:
                    if not char.tokenScaled and char.token.get_width() < UnitGenerator.tokenSize/2 and char.token.get_width() == char.token.get_height():
                        #aw = char.token.get_width()/self.ADJUSTED_TILE_WIDTH
                        #ah = char.token.get_height()/self.ADJUSTED_TILE_HEIGHT
                        char.tokenScaled = True
                        char.token = pygame.transform.scale(char.token, (self.ADJUSTED_TILE_WIDTH,self.ADJUSTED_TILE_HEIGHT))
                        char.gray_token = pygame.transform.scale(char.gray_token, (self.ADJUSTED_TILE_WIDTH,self.ADJUSTED_TILE_HEIGHT))
                    elif not char.tokenScaled and char.token.get_width() == char.token.get_height():
                        aw = (min(85,char.token.get_width())/UnitGenerator.tokenSize)*self.ADJUSTED_TILE_WIDTH
                        ah = (min(85,char.token.get_height())/UnitGenerator.tokenSize)*self.ADJUSTED_TILE_HEIGHT
                        char.tokenScaled = True
                        char.token = pygame.transform.scale(char.token, (aw,ah))
                        char.gray_token = pygame.transform.scale(char.gray_token, (aw,ah))
                    elif not char.tokenScaled:
                        aw = (char.token.get_width()/UnitGenerator.tokenSize)*self.ADJUSTED_TILE_WIDTH
                        ah = (char.token.get_height()/UnitGenerator.tokenSize)*self.ADJUSTED_TILE_HEIGHT
                        char.tokenScaled = True
                        char.token = pygame.transform.scale(char.token, (aw,ah))
                        char.gray_token = pygame.transform.scale(char.gray_token, (aw,ah))
                    chars.append(char)
        return chars
        
    
    def load_enemies(self, count):
        self.combat_manager.enemies = []
        enemy_types = ["Bandit", "Cultist", "Paladin"]
        primary = int(random.randrange(0, 3))
        
        tchar = UnitGenerator.create_unit('The ' + enemy_types[primary], enemy_types[primary], '../assets/enemies/' + enemy_types[primary].lower() +'Token.png', '../assets/enemies/' + enemy_types[primary].lower() + '.png')  
        if tchar.token.get_width() == tchar.token.get_height():
            aw = (min(85,tchar.token.get_width())/UnitGenerator.tokenSize)*self.ADJUSTED_TILE_WIDTH
            ah = (min(85,tchar.token.get_height())/UnitGenerator.tokenSize)*self.ADJUSTED_TILE_HEIGHT
        else:
            aw = (tchar.token.get_width()/UnitGenerator.tokenSize)*self.ADJUSTED_TILE_WIDTH
            ah = (tchar.token.get_height()/UnitGenerator.tokenSize)*self.ADJUSTED_TILE_HEIGHT
        tchar.token = pygame.transform.scale(tchar.token, (aw,ah))
        tchar.gray_token = pygame.transform.scale(tchar.gray_token, (aw,ah))
        self.combat_manager.enemies.append(tchar)
        
        for x in range(1,count):
            etype = int(random.randrange(0, 3))
            if not etype == primary:
                etype = int(random.randrange(0, 3))
                
            tchar = UnitGenerator.create_unit('The ' + enemy_types[etype], enemy_types[etype], '../assets/enemies/' + enemy_types[etype].lower() +'Token.png', '../assets/enemies/' + enemy_types[etype].lower() + '.png')  
            #tchar.token = pygame.transform.scale(tchar.token, (self.ADJUSTED_TILE_WIDTH,self.ADJUSTED_TILE_HEIGHT))
            if tchar.token.get_width() == tchar.token.get_height():
                aw = (min(85,tchar.token.get_width())/UnitGenerator.tokenSize)*self.ADJUSTED_TILE_WIDTH
                ah = (min(85,tchar.token.get_height())/UnitGenerator.tokenSize)*self.ADJUSTED_TILE_HEIGHT
            else:
                aw = (tchar.token.get_width()/UnitGenerator.tokenSize)*self.ADJUSTED_TILE_WIDTH
                ah = (tchar.token.get_height()/UnitGenerator.tokenSize)*self.ADJUSTED_TILE_HEIGHT
            tchar.token = pygame.transform.scale(tchar.token, (aw,ah))
            tchar.gray_token = pygame.transform.scale(tchar.gray_token, (aw,ah))
            self.combat_manager.enemies.append(tchar)
    
    def reset_game(self):
        for unit in self.units:
            unit.currentHP = unit.stats["HP"]
            unit.dead = False
            unit.acted = False
            unit.moved = False
            unit.attacking = False
            unit.moving = False
            unit.unresolved_attack = []
            unit.unresolved_move = []
            unit.next_square = []
        characters = self.load_team()
        self.character = characters[0]
        self.combat_manager = CombatManager(characters)
        self.combat_manager.enemies = []
        self.spriteMap = []
        self.myTiles = []
    
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
                if t[-1] == 'C' and i < self.combat_manager.characters.__len__():
                    spriteLine.append('c')
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
        cenemyI = 0
        
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
        showAttacks = False
        menuSelected = 1
        options = 1
        self.combat_manager.update_cost_map(self.myTiles.tiles, self.spriteMap)
        
        animating = False
        damaging = False
        waiting = 0
        
        attacker = -1
        defender = -1
        while self.running:
            clicked = False
            # Process the next enemy's turn. Double check there's not an issue after
            if self.combat_manager.current_turn() == CombatManager.ENEMY_TURN and not cenemyI < self.combat_manager.enemies.__len__():
                cenemyI = 0
                self.combat_manager.next_turn(self.myTiles.tiles, self.spriteMap)
                self.cursor.x = self.character.x * self.ADJUSTED_TILE_WIDTH
                self.cursor.y = self.character.y * self.ADJUSTED_TILE_HEIGHT
            currentEnemy = self.combat_manager.enemies[cenemyI]
            while currentEnemy.dead:
                cenemyI+=1
                if self.combat_manager.current_turn() == CombatManager.ENEMY_TURN and not cenemyI < self.combat_manager.enemies.__len__():
                    cenemyI = 0
                    self.combat_manager.next_turn(self.myTiles.tiles, self.spriteMap)
                    self.cursor.x = self.character.x * self.ADJUSTED_TILE_WIDTH
                    self.cursor.y = self.character.y * self.ADJUSTED_TILE_HEIGHT
                if cenemyI < self.combat_manager.enemies.__len__():
                    currentEnemy = self.combat_manager.enemies[cenemyI]
                else:
                    break
            
            if waiting > 0:
                waiting -= self.clockSpeed/10
                if waiting <= 0:
                    animating = False
                    waiting = 0
            
            # tick damage
            if damaging:
                if defender.undealt_damage > 0 or attacker.undealt_damage > 0:
                    pass
                else:
                    damaging = False
                    
                if not defender == -1 and defender.undealt_damage > 0:
                    if defender.damage_take_delay <= 0:
                        defender.damage_take_delay = self.clockSpeed
                        defender.damage_tick()
                        if defender.undealt_damage == 0:
                            if len(defender.attack_set) > 0:
                                dam = defender.attack_set[0]
                                attacker.take_damage(dam)
                                defender.attack_set.remove(dam)
                                damaging = False
                        if defender.dead:
                            damaging = False
                            waiting = True
                            attacker.undealt_damage = 0
                            defender.undealt_damage = 0
                            if defender in self.combat_manager.enemies:
                                self.spriteMap[defender.x][defender.y] = 'n'
                                attacker.add_exp(defender.level,1)
                                self.combat_manager.enemies.remove(defender)
                                if self.combat_manager.enemies.__len__() <= 0:
                                    # You win
                                    self.running = False
                            elif defender in self.combat_manager.characters:
                                self.spriteMap[defender.x][defender.y] = 'n'
                                self.combat_manager.characters.remove(defender)
                                if self.character == defender and self.combat_manager.characters.__len__() > 0:
                                    self.character = self.combat_manager.characters[0]
                                elif self.character == defender:
                                    # Game over
                                    self.running = False
                        elif defender.undealt_damage <= 0 and defender in self.combat_manager.enemies:
                            attacker.add_exp(defender.level,0)
                    else:
                        defender.damage_take_delay -= self.clockSpeed/4
                elif not defender == -1 and (defender.undealt_damage == -1 or defender.undealt_damage == -2):
                    if len(defender.attack_set) > 0:
                        dam = defender.attack_set[0]
                        attacker.take_damage(dam)
                        defender.attack_set.remove(dam)
                        damaging = False
                elif not attacker == -1 and attacker.undealt_damage > 0:
                    if attacker.damage_take_delay <= 0:
                        attacker.damage_take_delay = self.clockSpeed
                        attacker.damage_tick()
                        if attacker.undealt_damage == 0:
                            if len(attacker.attack_set) > 0:
                                dam = attacker.attack_set[0]
                                defender.take_damage(dam)
                                attacker.attack_set.remove(dam)
                                damaging = False
                        if attacker.dead:
                            damaging = False
                            waiting = True
                            attacker.undealt_damage = 0
                            defender.undealt_damage = 0
                            if attacker in self.combat_manager.characters:
                                self.spriteMap[attacker.x][attacker.y] = 'n'
                                self.combat_manager.characters.remove(attacker)
                                if self.character == attacker and self.combat_manager.characters.__len__() > 0:
                                    self.character = self.combat_manager.characters[0]
                                elif self.character == attacker:
                                    # Game over
                                    self.running = False
                            elif attacker in self.combat_manager.enemies:
                                self.spriteMap[attacker.x][attacker.y] = 'n'
                                defender.add_exp(attacker.level,1)
                                self.combat_manager.enemies.remove(attacker)
                                if self.combat_manager.enemies.__len__() <= 0:
                                    # You win
                                    self.running = False
                        elif attacker.undealt_damage <= 0 and attacker in self.combat_manager.enemies:
                            defender.add_exp(defender.level,0)
                    else:
                        attacker.damage_take_delay -= self.clockSpeed/4
                elif not defender == -1 and (defender.undealt_damage == -1 or defender.undealt_damage == -2):
                    if len(attacker.attack_set) > 0:
                        dam = attacker.attack_set[0]
                        defender.take_damage(dam)
                        attacker.attack_set.remove(dam)
                        damaging = False
                                
            # Redraw map
            self.window.fill((255, 255, 255))
            self.draw_map(currentTiles, self.myTiles)
            
            cx = int(self.cursor.x/self.ADJUSTED_TILE_WIDTH)
            cy = int(self.cursor.y/self.ADJUSTED_TILE_HEIGHT)
            if self.spriteMap[cx][cy] == 'c' and not self.character.moving and not self.character.attacking:
                for char in self.combat_manager.characters:
                    if char.x == cx and char.y == cy:
                        self.character = char
                        if char.acted and char.moved:
                            menuSelected = 1
                        break
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
                
                if self.combat_manager.current_turn() == CombatManager.PLAYER_TURN and not animating:
                    if event.type == KEYDOWN:
                        #if event.key == K_ESCAPE:
                            #self.running = False
                        if event.key == Options.DANGER:
                            showAttacks = not showAttacks
                        if event.key == Options.ACTION:
                            if self.character.moving == True:
                                self.spriteMap[self.character.originalX][self.character.originalY] = 'n'
                                self.spriteMap[self.character.x][self.character.y] = 'c'
                                self.combat_manager.update_cost_map(self.myTiles.tiles, self.spriteMap)
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
                                index = 0
                                for target in self.combat_manager.enemies:
                                    if target.x == cx and target.y == cy and not target.name == self.character.name:
                                        attacker = self.character
                                        defender = target
                                        aset, dset = CombatManager.fight(attacker,defender) 
                                        if len(aset) > 0:
                                            dam = aset[0]
                                            defender.take_damage(dam)
                                            aset.remove(dam)
                                            attacker.attack_set = aset
                                            defender.attack_set = dset
                                            animating = True
                                            menuSelected = 1
                                            attacker.anim_target = [target.x,target.y]
                                            attacker.attack_animating = True
                                        attacker.attacking = False
                                        attacker.acted = True
                                        attacker.moved = True
                                        attacker.originalX = -1
                                        attacker.originalY = -1
                                        break
                                    index += 1
                            elif menu == False:
                                menu = True
                            else:
                                clicked = True
                        if event.key == Options.BACK:
                            if self.character.moving == True:
                                self.spriteMap[self.character.x][self.character.y] = 'n'
                                self.character.move(self.character.originalX,self.character.originalY)
                                self.spriteMap[self.character.x][self.character.y] = 'c'
                                self.character.move_map = astar_map(self.combat_manager.map, (self.character.x,self.character.y), self.character.mov*2, allied = True, allow_diagonal_movement = False)
                                self.character.originalX = -1
                                self.character.originalY = -1
                                self.character.moving = False
                                self.cursor.x = self.character.x * self.ADJUSTED_TILE_WIDTH
                                self.cursor.y = self.character.y * self.ADJUSTED_TILE_HEIGHT
                                menu = True
                                menuSelected = 1
                            elif self.character.attacking == True:
                                if not self.character.originalX == -1:
                                    self.spriteMap[self.character.x][self.character.y] = 'n'#here
                                    self.character.move(self.character.originalX,self.character.originalY)
                                    self.spriteMap[self.character.x][self.character.y] = 'c'
                                    self.character.move_map = astar_map(self.combat_manager.map, (self.character.x,self.character.y), self.character.mov*2, allied = True, allow_diagonal_movement = False)
                                    self.character.originalX = -1
                                    self.character.originalY = -1
                                    self.character.moved = False
                                self.cursor.x = self.character.x * self.ADJUSTED_TILE_WIDTH
                                self.cursor.y = self.character.y * self.ADJUSTED_TILE_HEIGHT
                                menu = True
                                self.character.attacking = False
                                menuSelected = 1
                            elif menu == True:
                                menu = False
                                menuSelected = 1
                                if not self.character.originalX == -1:
                                    self.spriteMap[self.character.x][self.character.y] = 'n'
                                    self.character.move(self.character.originalX,self.character.originalY)
                                    self.spriteMap[self.character.x][self.character.y] = 'c'
                                    self.character.move_map = astar_map(self.combat_manager.map, (self.character.x,self.character.y), self.character.mov*2, allied = True, allow_diagonal_movement = False)
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
                                
            # Enemy turn processing
            if self.combat_manager.current_turn() == CombatManager.ENEMY_TURN and not animating:
                # If the enemy has been given move orders and is processing them, move to the next square
                if not currentEnemy.moved and currentEnemy.moving:
                    if currentEnemy.unresolved_move.__len__() == 1 and (self.spriteMap[currentEnemy.next_square[0]][currentEnemy.next_square[1]] == 'c' or self.spriteMap[currentEnemy.next_square[0]][currentEnemy.next_square[1]] == 'e'):
                        currentEnemy.unresolved_move = []
                        currentEnemy.next_square = []
                        currentEnemy.moved = True
                        currentEnemy.moving = False
                    else:
                        self.spriteMap[currentEnemy.x][currentEnemy.y] = 'n'
                        currentEnemy.resolve_move()
                        self.spriteMap[currentEnemy.x][currentEnemy.y] = 'e'
                        self.cursor.x = currentEnemy.x * self.ADJUSTED_TILE_WIDTH
                        self.cursor.y = currentEnemy.y * self.ADJUSTED_TILE_HEIGHT
                elif not currentEnemy.acted and currentEnemy.attacking:
                    # If the enemy has been given attack orders, do it after having finished any movement
                    ti = 0
                    for t in self.combat_manager.characters:
                        if t.name == currentEnemy.unresolved_attack:
                            break
                        ti+=1
                    target = -1
                    if ti < self.combat_manager.characters.__len__():
                        target = self.combat_manager.characters[ti]
                        currentEnemy.move_map = astar_map(self.combat_manager.map, (currentEnemy.x,currentEnemy.y), currentEnemy.mov*2, allied = True, allow_diagonal_movement = False)
                        if currentEnemy.can_attack(target.x,target.y):
                            #CombatManager.fight(currentEnemy,target) 
                            attacker = currentEnemy
                            defender = target
                            aset, dset = CombatManager.fight(attacker,defender) 
                            if len(aset) > 0:
                                dam = aset[0]
                                if not dam == -2:
                                    defender.take_damage(dam)
                                    aset.remove(dam)
                                    attacker.attack_set = aset
                                    defender.attack_set = dset
                                    attacker.anim_target = [target.x,target.y]
                                    attacker.attack_animating = True
                                    animating = True
                    currentEnemy.attacking = True
                    currentEnemy.acted = True
                    currentEnemy.moved = True
                    '''if target in self.combat_manager.characters:
                        if target.dead:
                            self.spriteMap[target.x][target.y] = 'n'
                            self.combat_manager.characters.remove(target)
                            if self.combat_manager.characters.__len__() > 0:
                                self.character = self.combat_manager.characters[0]
                            else:
                                # Game over
                                self.running = False
                        elif currentEnemy.dead:
                            self.spriteMap[currentEnemy.x][currentEnemy.y] = 'n'
                            self.combat_manager.enemies.remove(currentEnemy)
                            # Defeated the attacking enemy, 100% exp
                            target.add_exp(target.level,1)
                            if self.combat_manager.enemies.__len__() <= 0:
                                # You win
                                self.running = False
                        elif not target.can_attack_stationary(currentEnemy.x,currentEnemy.y):
                            # Survived an attack, but enemy survived too. Reduced exp
                            target.add_exp(target.level,0)
                        else:
                            # Survied an attack, but couldn't attack back. Heavily reduced exp
                            target.add_exp(0,0)'''
                elif currentEnemy.moved or currentEnemy.acted:
                    # If the unit has already attacked or moved, move to the next enemy in the list
                    currentEnemy.moved = True
                    currentEnemy.acted = True
                    cenemyI+=1
                else:
                    self.combat_manager.update_cost_map(self.myTiles.tiles, self.spriteMap)
                    # If the unit has no orders and hasn't moved yet, generate the orders through the AI function
                    # Set [ type of action , location for movement , target for attack ]
                    set = self.combat_manager.ai(self.spriteMap,self.myTiles, currentEnemy)
                    #print(set[0])
                    # NPC decides to move twice
                    if set[0] == CombatManager.MOVE_MOVE:
                        currentEnemy.moving = True
                        currentEnemy.unresolved_move = set[1]
                        self.spriteMap[currentEnemy.x][currentEnemy.y] = 'n'
                        currentEnemy.resolve_move()
                        self.spriteMap[currentEnemy.x][currentEnemy.y] = 'e'
                    # NPC decides to attack
                    elif set[0] == CombatManager.ACTION_MOVE:
                        currentEnemy.unresolved_attack = set[2]
                        print(set[2])
                        currentEnemy.attacking = True
                        # NPC also decides to move
                        currentEnemy.moving = True
                        currentEnemy.unresolved_move = set[1]
                        self.spriteMap[currentEnemy.x][currentEnemy.y] = 'n'
                        currentEnemy.resolve_move()
                        self.spriteMap[currentEnemy.x][currentEnemy.y] = 'e'
                    elif set[0] == CombatManager.ACTION:
                        print(set[1])
                        currentEnemy.unresolved_attack = set[1]
                        currentEnemy.attacking = True
                    else:
                        currentEnemy.acted = True
                        currentEnemy.moved = True
                
                
            # Display all characters
            anyAction = False
            for char in self.combat_manager.characters:
                if char.attack_animating and not damaging:
                    animating, damaging = char.attack_animation_adjust(round(self.ADJUSTED_TILE_WIDTH/2),round(self.ADJUSTED_TILE_HEIGHT/2))
                    if damaging == False and animating == False and (attacker.undealt_damage > 0 or defender.undealt_damage > 0):
                        if defender.undealt_damage > 0:
                            attacker.anim_target = [defender.x,defender.y]
                            attacker.attack_animating = True
                            animating = True
                        elif attacker.undealt_damage > 0:
                            defender.anim_target = [attacker.x,attacker.y]
                            defender.attack_animating = True
                            animating = True
                    if animating == False:
                        animating = True
                        waiting = self.clockSpeed*5
                charX = char.x*self.ADJUSTED_TILE_WIDTH-(char.token.get_width()-self.ADJUSTED_TILE_WIDTH) + char.attacking_anim[0]
                charY = char.y*self.ADJUSTED_TILE_HEIGHT-(char.token.get_height()-self.ADJUSTED_TILE_HEIGHT) + char.attacking_anim[1]
                if not char.acted or not char.moved:
                    anyAction = True
                if char.moved and char.acted and not char.dead:
                    self.window.blit(char.gray_token,(charX, charY)) 
                elif not char.dead:
                    self.window.blit(char.token,(charX, charY))  
                    
            for char in self.combat_manager.enemies:
                if char.attack_animating and not damaging:
                    animating, damaging = char.attack_animation_adjust(round(self.ADJUSTED_TILE_WIDTH/2),round(self.ADJUSTED_TILE_HEIGHT/2))
                    if animating == False and (attacker.undealt_damage > 0 or defender.undealt_damage > 0):
                        if attacker.undealt_damage > 0:
                            attacker.anim_target = [defender.x,defender.y]
                            attacker.attack_animating = True
                            animating = True
                        elif defender.undealt_damage > 0:
                            defender.anim_target = [attacker.x,attacker.y]
                            defender.attack_animating = True
                            animating = True
                    if animating == False:
                        animating = True
                        waiting = self.clockSpeed*5
                charX = char.x*self.ADJUSTED_TILE_WIDTH-(char.token.get_width()-self.ADJUSTED_TILE_WIDTH) + char.attacking_anim[0]
                charY = char.y*self.ADJUSTED_TILE_HEIGHT-(char.token.get_height()-self.ADJUSTED_TILE_HEIGHT) + char.attacking_anim[1]
                if char.moved and char.acted and not char.dead:
                    self.window.blit(char.gray_token,(charX, charY)) 
                elif not char.dead:
                    self.window.blit(char.token,(charX, charY))  
            
            # Draw oversized parts of tokens over again so they always appear over other tokens
            for char in self.combat_manager.characters:
                if char.token.get_height() <= self.ADJUSTED_TILE_WIDTH and char.token.get_width() <= self.ADJUSTED_TILE_WIDTH:
                    continue
                charX = char.x*self.ADJUSTED_TILE_WIDTH-(char.token.get_width()-self.ADJUSTED_TILE_WIDTH) + char.attacking_anim[0]
                charY = char.y*self.ADJUSTED_TILE_HEIGHT-(char.token.get_height()-self.ADJUSTED_TILE_HEIGHT) + char.attacking_anim[1]
                if char.moved and char.acted and not char.dead:
                    ttoken = char.gray_token.copy()
                    # Create subsurface for normal area of the tile, then make it transparent
                    subsurface = ttoken.subsurface(((char.token.get_width()-self.ADJUSTED_TILE_WIDTH)/2, char.token.get_height()-self.ADJUSTED_TILE_HEIGHT, self.ADJUSTED_TILE_WIDTH, self.ADJUSTED_TILE_HEIGHT))
                    subsurface.fill((0,0,0,0))
                    self.window.blit(ttoken,(charX, charY)) 
                elif not char.dead:
                    ttoken = char.token.copy()
                    # Create subsurface for normal area of the tile, then make it transparent
                    subsurface = ttoken.subsurface(((char.token.get_width()-self.ADJUSTED_TILE_WIDTH)/2, char.token.get_height()-self.ADJUSTED_TILE_HEIGHT, self.ADJUSTED_TILE_WIDTH, self.ADJUSTED_TILE_HEIGHT))
                    subsurface.fill((0,0,0,0))
                    self.window.blit(ttoken,(charX, charY))  
                    
            for char in self.combat_manager.enemies:
                if char.token.get_height() <= self.ADJUSTED_TILE_WIDTH and char.token.get_width() <= self.ADJUSTED_TILE_WIDTH:
                    continue
                charX = char.x*self.ADJUSTED_TILE_WIDTH-(char.token.get_width()-self.ADJUSTED_TILE_WIDTH) + char.attacking_anim[0]
                charY = char.y*self.ADJUSTED_TILE_HEIGHT-(char.token.get_height()-self.ADJUSTED_TILE_HEIGHT) + char.attacking_anim[1]
                if char.moved and char.acted and not char.dead:
                    ttoken = char.gray_token.copy()
                    # Create subsurface for normal area of the tile, then make it transparent
                    subsurface = ttoken.subsurface(((char.token.get_width()-self.ADJUSTED_TILE_WIDTH)/2, char.token.get_height()-self.ADJUSTED_TILE_HEIGHT, self.ADJUSTED_TILE_WIDTH, self.ADJUSTED_TILE_HEIGHT))
                    subsurface.fill((0,0,0,0))
                    self.window.blit(ttoken,(charX, charY)) 
                elif not char.dead:
                    ttoken = char.token.copy()
                    # Create subsurface for normal area of the tile, then make it transparent
                    subsurface = ttoken.subsurface(((char.token.get_width()-self.ADJUSTED_TILE_WIDTH)/2, char.token.get_height()-self.ADJUSTED_TILE_HEIGHT, self.ADJUSTED_TILE_WIDTH, self.ADJUSTED_TILE_HEIGHT))
                    subsurface.fill((0,0,0,0))
                    self.window.blit(ttoken,(charX, charY))  
                
            if not anyAction:
                self.combat_manager.next_turn(self.myTiles.tiles, self.spriteMap)
                
            # Draw menu if action button is clicked. pass in object clicked on to figure out which options show up
            if not self.combat_manager.current_turn() == CombatManager.PLAYER_TURN or animating:
                flip = self.reticle_idle(flip)
            elif self.character.attacking == True:
                flip = self.attacking_cursor(flip)
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
                        if self.character.can_move(x, y) and self.combat_manager.map[x][y] != 4:
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
                    
            if showAttacks:
                sidebar = pygame.Surface((self.ADJUSTED_TILE_WIDTH, self.ADJUSTED_TILE_HEIGHT))
                sidebar.set_alpha(100)
                x = 0
                for xline in self.myTiles.tiles:
                    y = 0
                    for yline in xline:
                        for npc in self.combat_manager.enemies:
                            npc.originalX = npc.x
                            npc.originalY = npc.y
                            if npc.can_attack(x,y):
                                sidebar.fill((220,20,20))
                                self.window.blit(sidebar,(x*self.ADJUSTED_TILE_WIDTH, y*self.ADJUSTED_TILE_HEIGHT))
                                npc.originalX = -1
                                npc.originalY = -1
                                break
                            npc.originalX = -1
                            npc.originalY = -1
                        y += 1
                    x += 1
                
            
            if (self.spriteMap[cx][cy] == 'c' or self.spriteMap[cx][cy] == 'e') and not self.character.moving or animating:
                if not self.character.attacking and not animating:
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
                else:
                    if self.spriteMap[cx][cy] == 'e' or animating:
                        for char in self.combat_manager.enemies:
                            if char.x == cx and char.y == cy and not char.dead:
                                #self.draw_stats(char,1) 
                                self.draw_battle_preview(char)
                                # Draw preview
                                break
            
            # Update display
            pygame.display.flip()
            clock.tick(self.clockSpeed)
    
    def draw_battle_preview(self, target):
        w, h = pygame.display.get_surface().get_size()
        border_length = 2
        sidebar_options = 4
        # Name, damage per hit x hit count, hit rate, crit rate
        
        border_color = (0, 0, 0)
        attacker_color = (67, 160, 76)
        defender_color = (190, 77, 86)
        
        cell_w = h/6
        cell_h = h/12
        
        hpbar_y = h-cell_h
        sidebar_y = h-(sidebar_options+1)*cell_h
        
        if self.character.y*self.ADJUSTED_TILE_WIDTH >= h/2:
            hpbar_y = 0
            sidebar_y = h/12
        
        # Place background for the borders first    
        attacking_hpbar = pygame.Surface((w/2,h/12))
        attacking_hpbar.fill(border_color)
        attacking_hpbar.set_alpha(200)
        self.window.blit(attacking_hpbar,(0, hpbar_y)) 
        
        defending_hpbar = pygame.Surface((w/2,h/12))
        defending_hpbar.fill(border_color)
        defending_hpbar.set_alpha(200)
        self.window.blit(defending_hpbar,(w/2, hpbar_y)) 
        
        attacking_sidebar = pygame.Surface((w/6,sidebar_options*h/12))
        attacking_sidebar.fill(border_color)
        attacking_sidebar.set_alpha(200)
        self.window.blit(attacking_sidebar,(0, sidebar_y)) 
        
        defending_sidebar = pygame.Surface((w/6,sidebar_options*h/12))
        defending_sidebar.fill(border_color)
        defending_sidebar.set_alpha(200)
        self.window.blit(defending_sidebar,(w-w/6, sidebar_y)) 
        
        attacking_hp_textbox = pygame.Surface((cell_w-border_length*2,cell_h-border_length*2))
        attacking_hp_textbox.fill(attacker_color)
        attacking_hp_textbox.set_alpha(200)
        self.window.blit(attacking_hp_textbox,(border_length, hpbar_y+border_length)) 
        
        defending_hp_textbox = pygame.Surface((cell_w-border_length*2,cell_h-border_length*2))
        defending_hp_textbox.fill(defender_color)
        defending_hp_textbox.set_alpha(200)
        self.window.blit(defending_hp_textbox,(w-cell_w+border_length, hpbar_y+border_length)) 
        
        attacking_hp_backbox = pygame.Surface((w/2-cell_w-border_length*2,cell_h-border_length*2))
        attacking_hp_backbox.fill(attacker_color)
        attacking_hp_backbox.set_alpha(150)
        self.window.blit(attacking_hp_backbox,(cell_w+border_length, hpbar_y+border_length)) 
        
        defending_hp_backbox = pygame.Surface((w/2-cell_w-border_length*2,cell_h-border_length*2))
        defending_hp_backbox.fill(defender_color)
        defending_hp_backbox.set_alpha(150)
        self.window.blit(defending_hp_backbox,(w/2+border_length, hpbar_y+border_length)) 
        
        hp_blit_w = math.floor((w/2-cell_w)/60)-border_length
        hp_blit_h = (cell_h/2)-border_length
        
        hp_blit = pygame.Surface((hp_blit_w,hp_blit_h))
        hp_blit.fill((220,220,180))
        hp_blit.set_alpha(220)
        
        hp_dead_blit = pygame.Surface((hp_blit_w,hp_blit_h))
        hp_dead_blit.fill((130,130,130))
        hp_dead_blit.set_alpha(220)
        
        for i in range(1,self.character.stats["HP"]):
            if i <= 60:
                if i <= self.character.currentHP:
                    self.window.blit(hp_blit,(cell_w+i*(hp_blit_w+border_length),hpbar_y+border_length))
                else:
                    self.window.blit(hp_dead_blit,(cell_w+i*(hp_blit_w+border_length),hpbar_y+border_length))
            else:
                if i <= self.character.currentHP or True:
                    self.window.blit(hp_blit,(cell_w+(i-60)*(hp_blit_w+border_length),hpbar_y+border_length+hp_blit_h+border_length))
                else:
                    self.window.blit(hp_dead_blit,(cell_w+(i-60)*(hp_blit_w+border_length),hpbar_y+border_length+hp_blit_h+border_length))
                    
        for i in range(1,target.stats["HP"]):
            if i <= 60:
                if i <= target.currentHP:
                    self.window.blit(hp_blit,(w-cell_w-border_length-i*(hp_blit_w+border_length),hpbar_y+border_length))
                else:
                    self.window.blit(hp_dead_blit,(w-cell_w-border_length-i*(hp_blit_w+border_length),hpbar_y+border_length))
            else:
                if i <= target.currentHP or True:
                    self.window.blit(hp_blit,(w-cell_w-border_length-(i-60)*(hp_blit_w+border_length),hpbar_y+border_length+hp_blit_h+border_length))
                else:
                    self.window.blit(hp_dead_blit,(w-cell_w-border_length-(i-60)*(hp_blit_w+border_length),hpbar_y+border_length+hp_blit_h+border_length))
                
        # Attacker boxes
        attacking_name_textbox = pygame.Surface((cell_w-border_length*2,cell_h-border_length*2))
        attacking_name_textbox.fill((220,235,220))
        attacking_name_textbox.set_alpha(200)
        self.window.blit(attacking_name_textbox,(border_length, sidebar_y+border_length)) 
        
        attacking_dam_textbox = pygame.Surface((cell_w-border_length*2,cell_h-border_length*2))
        attacking_dam_textbox.fill(attacker_color)
        attacking_dam_textbox.set_alpha(200)
        self.window.blit(attacking_dam_textbox,(border_length, sidebar_y+border_length+cell_h)) 
        
        attacking_hitr_textbox = pygame.Surface((cell_w-border_length*2,cell_h-border_length*2))
        attacking_hitr_textbox.fill(attacker_color)
        attacking_hitr_textbox.set_alpha(200)
        self.window.blit(attacking_hitr_textbox,(border_length, sidebar_y+border_length+cell_h*2)) 
        
        attacking_critr_textbox = pygame.Surface((cell_w-border_length*2,cell_h-border_length*2))
        attacking_critr_textbox.fill(attacker_color)
        attacking_critr_textbox.set_alpha(200)
        self.window.blit(attacking_critr_textbox,(border_length, sidebar_y+border_length+cell_h*3)) 
        
        # Defender boxes
        defending_name_textbox = pygame.Surface((cell_w-border_length*2,cell_h-border_length*2))
        defending_name_textbox.fill((235,220,220))
        defending_name_textbox.set_alpha(200)
        self.window.blit(defending_name_textbox,(w-cell_w+border_length, sidebar_y+border_length)) 
        
        defending_dam_textbox = pygame.Surface((cell_w-border_length*2,cell_h-border_length*2))
        defending_dam_textbox.fill(defender_color)
        defending_dam_textbox.set_alpha(200)
        self.window.blit(defending_dam_textbox,(w-cell_w+border_length, sidebar_y+border_length+cell_h)) 
        
        defending_hitr_textbox = pygame.Surface((cell_w-border_length*2,cell_h-border_length*2))
        defending_hitr_textbox.fill(defender_color)
        defending_hitr_textbox.set_alpha(200)
        self.window.blit(defending_hitr_textbox,(w-cell_w+border_length, sidebar_y+border_length+cell_h*2)) 
        
        defending_critr_textbox = pygame.Surface((cell_w-border_length*2,cell_h-border_length*2))
        defending_critr_textbox.fill(defender_color)
        defending_critr_textbox.set_alpha(200)
        self.window.blit(defending_critr_textbox,(w-cell_w+border_length, sidebar_y+border_length+cell_h*3)) 
        
        
        font = pygame.font.Font(pygame.font.match_font('calibri',bold=True), 25)
        adam, ahits, acrit, ahit = CombatManager.calc_preview(target, self.character)
        ddam, dhits, dcrit, dhit = CombatManager.calc_preview(self.character, target)
        
        self.draw_text("HP {}/{}".format(self.character.currentHP,self.character.stats["HP"]), font, (0, 0, 0), cell_w/2, hpbar_y+border_length+cell_h/2)
        self.draw_text("{}".format(self.character.name), font, (0, 0, 0), cell_w/2, sidebar_y+border_length+cell_h/2)
        if not ahits == "-" and ahits > 1:
            self.draw_text("MT {}x{}".format(adam, ahits), font, (0, 0, 0), cell_w/2, sidebar_y+border_length+cell_h/2+cell_h)
        else:
            self.draw_text("MT {}".format(adam), font, (0, 0, 0), cell_w/2, sidebar_y+border_length+cell_h/2+cell_h)
        self.draw_text("Hit {}%".format(ahit), font, (0, 0, 0), cell_w/2, sidebar_y+border_length+cell_h/2+cell_h*2)
        self.draw_text("Crit {}%".format(acrit), font, (0, 0, 0), cell_w/2, sidebar_y+border_length+cell_h/2+cell_h*3)
        
        
        self.draw_text("HP {}/{}".format(target.currentHP,target.stats["HP"]), font, (0, 0, 0), w-cell_w+cell_w/2, hpbar_y+border_length+cell_h/2)
        self.draw_text("{}".format(target.name), font, (0, 0, 0), w-cell_w+cell_w/2, sidebar_y+border_length+cell_h/2)
        if not dhits == "-" and dhits > 1:
            self.draw_text("MT {}x{}".format(ddam, dhits), font, (0, 0, 0), w-cell_w+cell_w/2, sidebar_y+border_length+cell_h/2+cell_h)
        else:
            self.draw_text("MT {}".format(ddam), font, (0, 0, 0), w-cell_w+cell_w/2, sidebar_y+border_length+cell_h/2+cell_h)
        self.draw_text("Hit {}%".format(dhit), font, (0, 0, 0), w-cell_w+cell_w/2, sidebar_y+border_length+cell_h/2+cell_h*2)
        self.draw_text("Crit {}%".format(dcrit), font, (0, 0, 0), w-cell_w+cell_w/2, sidebar_y+border_length+cell_h/2+cell_h*3)
        
            
    def draw_stats(self, character, enemy=0):
        optionsW = 4
        optionsH = 4
        # Same thickness as the menu for each line. 4 lines
        height = (self.ADJUSTED_TILE_HEIGHT * 2/3) * optionsH
        # Same width as the menu for each option. maximum 4 options per line
        width = self.ADJUSTED_TILE_WIDTH * 2 * optionsW
        borderSize = 3
        
        #Background for image
        background = pygame.Surface((height, height))
        background.set_alpha(180)
        
        statMenu = pygame.Surface((width, height))
        statMenu.set_alpha(180)
        if enemy == 0:
            statMenu.fill((67, 160, 76))
            background.fill((140,180,140))
        else:
            statMenu.fill((190, 77, 86))
            background.fill((180, 140, 140))
        
        border = pygame.Surface((width+borderSize*2+height, height+borderSize*2))
        border.set_alpha(180)
        border.fill((0, 0, 0))
        
        # Set up the image and border
        #wborder = pygame.Surface((height+borderSize*2, height+borderSize*2))
        #wborder.set_alpha(90)
        #wborder.fill((0, 0, 0))
        
        image = character.icon.copy()
        image = pygame.transform.scale(image, (height,height))
        
        # Place the menu on the screen
        imageX = 0
        x = imageX + height + borderSize
        y = self.dimensions[1]*self.ADJUSTED_TILE_WIDTH - height
        borderX = imageX + borderSize
        if self.cursor.x < self.dimensions[0]*self.ADJUSTED_TILE_WIDTH / 2:
            x = self.dimensions[0]*self.ADJUSTED_TILE_WIDTH - width
            imageX = x - height - borderSize
            borderX = imageX
        if self.cursor.y > self.dimensions[1]*self.ADJUSTED_TILE_HEIGHT / 2:
            y = 0
        
        # Place the menu and its border
        self.window.blit(border,(borderX-borderSize, y-borderSize)) 
        self.window.blit(statMenu,(x, y)) 
        
        # Place the character image and its border
        #self.window.blit(wborder,(imageX-borderSize, y-borderSize)) 
        self.window.blit(background,(imageX, y)) 
        self.window.blit(image,(imageX, y)) 
        
        '''
        Name, type, level
        current hp / max hp
        str skl res lck
        mag spd def mov
        '''
        statXOffset = width/optionsW
        statYOffset = height/optionsH
        font = pygame.font.Font(pygame.font.match_font('calibri',bold=True), 25)
        
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
        
      
    # Left aligned text 
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
        font = pygame.font.Font(pygame.font.match_font('calibri',bold=True), 25)
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
        if y + self.ADJUSTED_TILE_HEIGHT + menuH >= h:
            y = self.cursor.y - menuH + self.ADJUSTED_TILE_HEIGHT/2
        if x - self.ADJUSTED_TILE_WIDTH < 0:
            x = self.cursor.x + self.ADJUSTED_TILE_WIDTH
            
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
        if option == 'Wait':
            self.character.moved = True
            self.character.acted = True
            self.character.originalY = -1
            self.character.originalX = -1
            menu = False
        if option == 'End Turn':
            self.combat_manager.next_turn(self.myTiles.tiles, self.spriteMap)
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
            if not self.character.acted or not self.character.moved:
                options.append('Wait')
            options.append('Unit Status')
        elif clickedObject == 'e':
            options.append('Unit Status')
        else:
            options.append('End Turn')
            options.append('Main Menu')
            
        options.append('Options')
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
            self.cursor.a -= 15*(15/self.clockSpeed)
        else:
            self.cursor.a += 15*(15/self.clockSpeed)
            
        if(self.cursor.a <= 50):
            self.cursor.a = 50
            flip = 1
        elif(self.cursor.a >= 255):
            self.cursor.a = 255
            flip = 0
        
        self.cursor.set_alpha()
        return flip
    
    def attacking_cursor(self, flip):
        moveDelay = 15/self.clockSpeed
        keys = pygame.key.get_pressed()
        w, h = pygame.display.get_surface().get_size()
        x1 = 0
        y1 = 0
        
        adjustX = int(self.cursor.x/self.ADJUSTED_TILE_WIDTH)
        adjustY = int(self.cursor.y/self.ADJUSTED_TILE_HEIGHT)
        if(self.cursor.move_delay <= 0 and any((keys[Options.LEFT], keys[Options.RIGHT], keys[Options.UP], keys[Options.DOWN]))):
            if keys[Options.LEFT] and (self.cursor.x-self.ADJUSTED_TILE_WIDTH) >= 0:
                if self.character.can_attack_stationary(adjustX-1,adjustY):
                    x1 -= 1
                elif adjustY == self.character.y and adjustX-1 == self.character.x and self.character.can_attack_stationary(adjustX-2,adjustY):
                    x1 -= 2
                elif not adjustX == self.character.x-2 and self.character.can_attack_stationary(self.character.x-1,self.character.y):
                    self.cursor.y = self.character.y*self.ADJUSTED_TILE_HEIGHT
                    self.cursor.x = self.character.x*self.ADJUSTED_TILE_WIDTH
                    x1 -= 1
                    if not adjustY == self.character.y+1 and not adjustY == self.character.y-1:
                        if self.character.can_attack_stationary(self.character.x-1,self.character.y+1) and adjustY > self.character.y:
                            y1 += 1
                        elif self.character.can_attack_stationary(self.character.x-1,self.character.y-1) and adjustY < self.character.y:
                            y1 -= 1
                self.cursor.move_delay = moveDelay
            elif keys[Options.RIGHT] and (self.cursor.x+self.ADJUSTED_TILE_WIDTH) < w:
                if self.character.can_attack_stationary(adjustX+1,adjustY):
                    x1 += 1
                elif adjustY == self.character.y and adjustX+1 == self.character.x and self.character.can_attack_stationary(adjustX+2,adjustY):
                    x1 += 2
                elif not adjustX == self.character.x+2 and self.character.can_attack_stationary(self.character.x+1,self.character.y):
                    self.cursor.y = self.character.y*self.ADJUSTED_TILE_HEIGHT
                    self.cursor.x = self.character.x*self.ADJUSTED_TILE_WIDTH
                    x1 += 1
                    if not adjustY == self.character.y+1 and not adjustY == self.character.y-1:
                        if self.character.can_attack_stationary(self.character.x+1,self.character.y+1) and adjustY > self.character.y:
                            y1 += 1
                        elif self.character.can_attack_stationary(self.character.x+1,self.character.y-1) and adjustY < self.character.y:
                            y1 -= 1
                self.cursor.move_delay = moveDelay
            elif keys[Options.UP] and (self.cursor.y-self.ADJUSTED_TILE_HEIGHT) >= 0:
                if self.character.can_attack_stationary(adjustX,adjustY-1):
                    y1 -= 1
                elif adjustY-1 == self.character.y and adjustX == self.character.x and self.character.can_attack_stationary(adjustX,adjustY-2):
                    y1 -= 2
                elif not adjustY == self.character.y-2 and self.character.can_attack_stationary(self.character.x,self.character.y-1):
                    self.cursor.y = self.character.y*self.ADJUSTED_TILE_HEIGHT
                    self.cursor.x = self.character.x*self.ADJUSTED_TILE_WIDTH
                    y1 -= 1
                    if not adjustX == self.character.x+1 and not adjustX == self.character.x-1:
                        if self.character.can_attack_stationary(self.character.x+1,self.character.y-1) and adjustX > self.character.x:
                            x1 += 1
                        elif self.character.can_attack_stationary(self.character.x-1,self.character.y-1) and adjustX < self.character.x:
                            x1 -= 1
                self.cursor.move_delay = moveDelay
            elif keys[Options.DOWN] and (self.cursor.y+self.ADJUSTED_TILE_HEIGHT) < h:
                if self.character.can_attack_stationary(adjustX,adjustY+1):
                    y1 += 1
                elif adjustY+1 == self.character.y and adjustX == self.character.x and self.character.can_attack_stationary(adjustX,adjustY+2):
                    y1 += 2
                elif not adjustY == self.character.y+2 and self.character.can_attack_stationary(self.character.x,self.character.y+1):
                    self.cursor.y = self.character.y*self.ADJUSTED_TILE_HEIGHT
                    self.cursor.x = self.character.x*self.ADJUSTED_TILE_WIDTH
                    y1 += 1
                    if not adjustX == self.character.x+1 and not adjustX == self.character.x-1:
                        if self.character.can_attack_stationary(self.character.x+1,self.character.y+1) and adjustX > self.character.x:
                            x1 += 1
                        elif self.character.can_attack_stationary(self.character.x-1,self.character.y+1) and adjustX < self.character.x:
                            x1 -= 1
                self.cursor.move_delay = moveDelay
        else:
            self.cursor.move_delay -= moveDelay/3*(15/self.clockSpeed)
            
        self.cursor.y += y1*self.ADJUSTED_TILE_HEIGHT
        self.cursor.x += x1*self.ADJUSTED_TILE_WIDTH
        return self.reticle_idle(flip)
    
    def cursor_movement(self, flip, currentEnemyI, currentCharI):
        moveDelay = 15/self.clockSpeed
        keys = pygame.key.get_pressed()
        w, h = pygame.display.get_surface().get_size()
        x1 = 0
        y1 = 0
        
        # While a key is being pressed, the delay between moving the cursor reduces. It's reset when no keys are being pressed
        if not any((keys[Options.LEFT], keys[Options.RIGHT], keys[Options.UP], keys[Options.DOWN], keys[Options.REWIND], keys[Options.NEXT])):
            self.cursor.move_delay_reduce = 0
        elif self.character.moving:
            self.cursor.move_delay_reduce = moveDelay/2
            
            
            
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
                self.cursor.move_delay = moveDelay - self.cursor.move_delay_reduce
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
                self.cursor.move_delay = moveDelay - self.cursor.move_delay_reduce
            elif keys[Options.LEFT] and (self.cursor.x-self.ADJUSTED_TILE_WIDTH) >= 0:
                x1 -= 1
                if self.character.moving:
                    if self.character.can_move(adjustX-1, adjustY):
                        # Check if the tile is a blocked tile, and allow the cursor to move there if it's an enemy and the character can move there
                        if self.myTiles.tiles[int(adjustX-1)][int(adjustY)].block == 1:
                            if not self.spriteMap[adjustX-1][adjustY] == 'e' and self.character.can_move(adjustX-1,adjustY):
                                x1 += 1
                        # Check if character can move to where the cursor is, and check that that place is neither a character or an enemy
                        elif self.character.can_move(adjustX-1, adjustY) and not self.spriteMap[adjustX-1][adjustY] == 'c' and not self.spriteMap[adjustX-1][adjustY] == 'e':
                            self.character.move(int(adjustX-1),int(adjustY))
                        elif not self.spriteMap[adjustX-1][adjustY] == 'c' and not self.spriteMap[adjustX-1][adjustY] == 'e':
                            x1 += 1
                    # If the character can't move there, prevent the cursor from moving
                    else:
                        x1 += 1    
                self.cursor.move_delay = moveDelay - self.cursor.move_delay_reduce
            elif keys[Options.RIGHT] and (self.cursor.x+self.ADJUSTED_TILE_WIDTH) < w:
                x1 += 1
                if self.character.moving:
                    if self.character.can_move(adjustX+1, adjustY):
                        if self.myTiles.tiles[int(adjustX+1)][int(adjustY)].block == 1:
                            if not self.spriteMap[adjustX+1][adjustY] == 'e' and self.character.can_move(adjustX+1,adjustY):
                                x1 -= 1
                        elif self.character.can_move(adjustX+1, adjustY) and not self.spriteMap[adjustX+1][adjustY] == 'c' and not self.spriteMap[adjustX+1][adjustY] == 'e':
                            self.character.move(int(adjustX+1),int(adjustY))
                        elif not self.spriteMap[adjustX+1][adjustY] == 'c' and not self.spriteMap[adjustX+1][adjustY] == 'e':
                            x1 -= 1
                    else:
                        x1 -= 1
                self.cursor.move_delay = moveDelay - self.cursor.move_delay_reduce
            elif keys[Options.UP] and (self.cursor.y-self.ADJUSTED_TILE_HEIGHT) >= 0:
                y1 -= 1
                if self.character.moving:
                    if self.character.can_move(adjustX, adjustY-1):
                        if self.myTiles.tiles[int(adjustX)][int(adjustY-1)].block == 1:
                            if not self.spriteMap[adjustX][adjustY-1] == 'e' and self.character.can_move(adjustX,adjustY-1):
                                y1 += 1
                        elif self.character.can_move(adjustX, adjustY-1) and not self.spriteMap[adjustX][adjustY-1] == 'c' and not self.spriteMap[adjustX][adjustY-1] == 'e':
                            self.character.move(int(adjustX),int(adjustY-1))
                        elif not self.spriteMap[adjustX][adjustY-1] == 'c' and not self.spriteMap[adjustX][adjustY-1] == 'e':
                            y1 += 1
                    else:
                        y1 += 1
                self.cursor.move_delay = moveDelay - self.cursor.move_delay_reduce
            elif keys[Options.DOWN] and (self.cursor.y+self.ADJUSTED_TILE_HEIGHT) < h:
                y1 += 1
                if self.character.moving:
                    if self.character.can_move(adjustX, adjustY+1):
                        if self.myTiles.tiles[int(adjustX)][int(adjustY+1)].block == 1:
                            if not self.spriteMap[adjustX][adjustY+1] == 'e' and self.character.can_move(adjustX,adjustY+1):
                                y1 -= 1
                        elif self.character.can_move(adjustX, adjustY+1) and not self.spriteMap[adjustX][adjustY+1] == 'c' and not self.spriteMap[adjustX][adjustY+1] == 'e':
                            self.character.move(int(adjustX),int(adjustY+1))
                        elif not self.spriteMap[adjustX][adjustY+1] == 'c' and not self.spriteMap[adjustX][adjustY+1] == 'e':
                            y1 -= 1
                    else:
                        y1 -= 1
                self.cursor.move_delay = moveDelay - self.cursor.move_delay_reduce
                
            if any(keys):
                self.cursor.move_delay_reduce += moveDelay/6
            if self.cursor.move_delay_reduce > moveDelay-moveDelay/8:
                self.cursor.move_delay_reduce = moveDelay-moveDelay/8
        else:
            self.cursor.move_delay -= moveDelay/3*(15/self.clockSpeed)
            
        self.cursor.y += y1*self.ADJUSTED_TILE_HEIGHT
        self.cursor.x += x1*self.ADJUSTED_TILE_WIDTH
        
        # After moving, change alpha of cursor
        return [self.reticle_idle(flip), currentEnemyI, currentCharI]
            