'''
Unit
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Holds information for units on the game map
'''

import random
import pygame
from Item import Weapon, WeaponTraits

# Found with some googling. Adjusted so it would copy the surface instead of adjusting the image directly
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

class Unit():
    def __init__(self, name, unitClass, x, y):
        self.tokenScaled = False
        self.name = name
        self.unitClass = unitClass
        self.x = x
        self.y = y
        
        self.originalX = -1
        self.originalY = -1
        
        self.weapon = -1
        
        self.moving = False
        self.attacking = False
        self.moved = False
        self.acted = False
        self.dead = False
        
        # A* calculation
        self.move_map = []
        
        self.unresolved_attack = []
        self.unresolved_move = []
        self.next_square = []
        
        self.attack_set = []
        self.attack_animating = False
        self.attack_animating_val = 1
        self.attacking_anim = [0,0]
        self.anim_target = []
        
        self.undealt_damage = 0
        self.damage_take_delay = 0
        
        self.exp = 0
        self.level = 1
        self.mov = 3
        self.stats = {
                "HP"     : 5,
                "str"    : 0,
                "mag"    : 0,
                "skl"    : 0,
                "spd"    : 0,
                "lck"    : 0,
                "defe"   : 0,
                "res"    : 0,
            }
        self.currentHP = self.stats["HP"]
    
    def attack_animation_adjust(self, x_goal, y_goal, speed=8):
        if self.anim_target[0] > self.x:
            self.attacking_anim[0] += self.attack_animating_val*round(x_goal/speed)
        elif self.anim_target[0] < self.x:
            self.attacking_anim[0] -= self.attack_animating_val*round(x_goal/speed)
            
        if self.anim_target[1] > self.y:
            self.attacking_anim[1] += self.attack_animating_val*round(y_goal/speed)
        elif self.anim_target[1] < self.y:
            self.attacking_anim[1] -= self.attack_animating_val*round(y_goal/speed)
            
        if self.attack_animating_val == 1 and (abs(self.attacking_anim[0]) >= x_goal or abs(self.attacking_anim[1]) >= y_goal):
            self.attack_animating_val = -1
            return True, True
        elif self.attack_animating_val == -1 and (self.attacking_anim[0] < 0 or self.attacking_anim[1] < 0):
            self.attacking_anim = [0,0]
            self.attack_animating_val = 1
            self.attack_animating = False
            return False, False
        return True, False
        
    def attack(self, damage, defense):
        dam = damage - defense
        if dam < 0:
            dam = 0
        return dam
    
    def move(self, newX, newY):
        self.x = newX
        self.y = newY
        
    def resolve_move(self):
        if not self.next_square == []:
            self.x = self.next_square[0]
            self.y = self.next_square[1]
            self.__next_move()
        elif self.unresolved_move.__len__() > 0:
            self.next_square = list(self.unresolved_move[0])
        
    
    def __next_move(self):
        self.next_square = []
        if self.unresolved_move.__len__() > 1:
            self.next_square = list(self.unresolved_move[0])
            self.unresolved_move.remove(self.unresolved_move[0])
        else:
            self.unresolved_move = []
            self.moving = False
            self.moved = True
        
    def equip_weapon(self, weapon):
        self.weapon = weapon
        
    def can_move(self, newX, newY):
        if self.move_map[newX][newY] != -1 and self.move_map[newX][newY] < self.mov:
            return True
        else:
            return False
        
    def can_move_move(self, newX, newY):
        if self.move_map[newX][newY] != -1 and self.move_map[newX][newY] < self.mov*2:
            return True
        else:
            return False
        
    def can_attack(self, newX, newY):
        if self.x == newX and self.y == newY:
            return False
        elif self.move_map[newX][newY] != -1 and self.move_map[newX][newY] < self.mov+self.weapon.range:
            return True
        else:
            return False
            
    def can_attack_stationary(self, newX, newY):
        if self.x == newX and self.y == newY:
            return False
        elif self.move_map[newX][newY] != -1 and self.move_map[newX][newY] <= self.weapon.range:
            return True
        else:
            return False
    
    def take_damage(self, damage):
        if damage > 0 or damage == -1:
            #self.currentHP -= damage
            self.undealt_damage = damage
    
    def damage_tick(self):
        if self.undealt_damage > 0:
            self.currentHP -= 1
            self.undealt_damage -= 1
        if self.currentHP <= 0:
            self.dead = True
            self.currentHP = 0
        #print("status {}: hp {}".format(self.name,self.currentHP))
    
    def add_exp(self, enemyLevel, kill=0):
        if enemyLevel == 0:
            exp = 1      
        elif kill == 1:
            exp = 70 * (enemyLevel/self.level)
        else:
            exp = 25 * (enemyLevel/self.level)
                  
        if(exp > 100):
            exp = 100
        
        self.exp += round(exp)
        #print(self.exp)
    
class MagicUnit(Unit):
    def __init__(self, name, x, y, personalGrowths, personalStats, icon, portrait):
        super().__init__(name, "Mage", x, y)
        self.weapon = WeaponTraits.build_weapon("Fire Book")
        self.token = pygame.image.load(icon)
        self.gray_token = grayscale_image(self.token)
        self.icon = pygame.image.load(portrait)
        self.exp = 0
        self.level = 1
        self.mov = 3
        self.stats = {
                "HP"     : 15 + personalStats[0],
                "str"    : 0  + personalStats[1],
                "mag"    : 3 + personalStats[2],
                "skl"    : 1 + personalStats[3],
                "spd"    : 3 + personalStats[4],
                "lck"    : 6 + personalStats[5],
                "def"    : 0 + personalStats[6],
                "res"    : 3 + personalStats[7],
            }
        self.currentHP = self.stats["HP"]
        self.__set_growths(personalGrowths)
        self.__set_maximum_stats(personalGrowths)
    
    def __set_maximum_stats(self, personalGrowths):
        self.max_stats = {
                "HP"     : min(120,55   + int(55*(personalGrowths[0]/100))),
                "str"    : min(99,50   + int(50*(personalGrowths[1]/150))),
                "mag"    : min(99,70   + int(70*(personalGrowths[2]/150))),
                "skl"    : min(99,60   + int(60*(personalGrowths[3]/150))),
                "spd"    : min(99,60   + int(60*(personalGrowths[4]/150))),
                "lck"    : min(99,80   + int(80*(personalGrowths[5]/150))),
                "def"    : min(99,60   + int(60*(personalGrowths[6]/150))),
                "res"    : min(99,70   + int(70*(personalGrowths[7]/150)))
            }
            
    def __set_growths(self,personalGrowths):
        self.growths = {
                "HP"     : 45 + personalGrowths[0],
                "str"    : 20 + personalGrowths[1],
                "mag"    : 50 + personalGrowths[2],
                "skl"    : 30 + personalGrowths[3],
                "spd"    : 45 + personalGrowths[4],
                "lck"    : 40 + personalGrowths[5],
                "def"    : 20 + personalGrowths[6],
                "res"    : 50 + personalGrowths[7]
            }
    
    def __level_up(self):
        self.level += 1
        self.exp -= 100
        
        str = ""
        for stat in self.stats:
            rand = random.randrange(0,100) + 1
            if rand < self.growths[stat]:
                self.stats[stat] += 1
                str += '{} went up 1!\n'.format(stat.upper())
                if rand < self.growths[stat]-100:
                    self.stats[stat] += 1
                    str += '{} went up 1!\n'.format(stat.upper())
        print(str)
    
    def add_exp(self, enemyLevel, kill):
        super().add_exp(enemyLevel, kill)
        if self.exp >= 100:
            self.__level_up()
            
    def attack(self, target, crit=0):
        damage = self.stats["mag"] + self.weapon.damage
        defense = target.stats["res"]
        rand = random.randrange(0,100) + 1
        if rand < crit:
            damage *= 2
        return Unit.attack(self, damage, defense)
    
    def equip_weapon(self, weapon):
        # Can use basic small weapons, or magic weapons
        if weapon.type == 'Book' or weapon.type == 'Wand' or weapon.type == 'Staff' or weapon.type == "Dagger" or weapon.type == "Shortsword":
            Unit.equip_weapon(self, weapon)

class ScoutUnit(Unit):
    def __init__(self, name, x, y, personalGrowths, personalStats, icon, portrait):
        super().__init__(name, "Scout", x, y)
        self.token = pygame.image.load(icon)
        self.icon = pygame.image.load(portrait)
        self.gray_token = grayscale_image(self.token)
        self.weapon = WeaponTraits.build_weapon("Iron Shortsword")
        self.exp = 0
        self.level = 1
        self.mov = 4
        self.stats = {
                "HP"     : 14 + personalStats[0],
                "str"    : 2  + personalStats[1],
                "mag"    : 0 + personalStats[2],
                "skl"    : 2 + personalStats[3],
                "spd"    : 3 + personalStats[4],
                "lck"    : 7 + personalStats[5],
                "def"    : 1 + personalStats[6],
                "res"    : 2 + personalStats[7],
            }
        self.currentHP = self.stats["HP"]
        self.__set_growths(personalGrowths)
        self.__set_maximum_stats(personalGrowths)
    
    def __set_maximum_stats(self, personalGrowths):
        self.max_stats = {
                "HP"     : min(120,60   + int(60*(personalGrowths[0]/100))),
                "str"    : min(99,60   + int(60*(personalGrowths[1]/150))),
                "mag"    : min(99,50   + int(50*(personalGrowths[2]/150))),
                "skl"    : min(99,70   + int(70*(personalGrowths[3]/150))),
                "spd"    : min(99,70   + int(70*(personalGrowths[4]/150))),
                "lck"    : min(99,80   + int(80*(personalGrowths[5]/150))),
                "def"    : min(99,55   + int(70*(personalGrowths[6]/150))),
                "res"    : min(99,60   + int(70*(personalGrowths[7]/150)))
            }
        
    def __set_growths(self,personalGrowths):
        self.growths = {
                "HP"     : 50 + personalGrowths[0],
                "str"    : 35 + personalGrowths[1],
                "mag"    : 20 + personalGrowths[2],
                "skl"    : 50 + personalGrowths[3],
                "spd"    : 55 + personalGrowths[4],
                "lck"    : 50 + personalGrowths[5],
                "def"    : 20 + personalGrowths[6],
                "res"    : 20 + personalGrowths[7]
            }
    
    def __level_up(self):
        self.level += 1
        self.exp -= 100
        
        str = ""
        for stat in self.stats:
            rand = random.randrange(0,100) + 1
            if rand < self.growths[stat]:
                self.stats[stat] += 1
                str += '{} went up 1!\n'.format(stat.upper())
                if rand < self.growths[stat]-99:
                    self.stats[stat] += 1
                    str += '{} went up 1!\n'.format(stat.upper())
        print(str)
    
    def add_exp(self, enemyLevel, kill):
        super().add_exp(enemyLevel, kill)
        if self.exp >= 100:
            self.__level_up()
            
    def attack(self, target, crit=0):
        damage = self.stats["str"] + self.weapon.damage
        defense = target.stats["def"]
        rand = random.randrange(0,100) + 1
        if rand < crit:
            damage *= 2
        return Unit.attack(self, damage, defense)
    
    def equip_weapon(self, weapon):
        # Can't hold a lance properly, and no magic weapons
        if not weapon.type == 'Book' and not weapon.type == 'Wand' and not weapon.type == 'Staff' and not "Lance":
            Unit.equip_weapon(self, weapon)
            
class InfantryUnit(Unit):
    def __init__(self, name, x, y, personalGrowths, personalStats, icon, portrait):
        super().__init__(name, "Infantry", x, y)
        self.token = pygame.image.load(icon)
        self.icon = pygame.image.load(portrait)
        self.gray_token = grayscale_image(self.token)
        self.weapon = WeaponTraits.build_weapon("Iron Sword")
        self.exp = 0
        self.level = 1
        self.mov = 3
        self.stats = {
                "HP"     : 17 + personalStats[0],
                "str"    : 3  + personalStats[1],
                "mag"    : 0 + personalStats[2],
                "skl"    : 1 + personalStats[3],
                "spd"    : 1 + personalStats[4],
                "lck"    : 5 + personalStats[5],
                "def"    : 2 + personalStats[6],
                "res"    : 2 + personalStats[7],
            }
        self.currentHP = self.stats["HP"]
        self.__set_growths(personalGrowths)
        self.__set_maximum_stats(personalGrowths)
    
    def __set_maximum_stats(self, personalGrowths):
        self.max_stats = {
                "HP"     : min(120,60   + int(60*(personalGrowths[0]/100))),
                "str"    : min(99,65   + int(60*(personalGrowths[1]/150))),
                "mag"    : min(99,50   + int(50*(personalGrowths[2]/150))),
                "skl"    : min(99,65   + int(70*(personalGrowths[3]/150))),
                "spd"    : min(99,70   + int(70*(personalGrowths[4]/150))),
                "lck"    : min(99,80   + int(80*(personalGrowths[5]/150))),
                "def"    : min(99,65   + int(70*(personalGrowths[6]/150))),
                "res"    : min(99,60   + int(70*(personalGrowths[7]/150)))
            }
        
    def __set_growths(self,personalGrowths):
        self.growths = {
                "HP"     : 60 + personalGrowths[0],
                "str"    : 40 + personalGrowths[1],
                "mag"    : 15 + personalGrowths[2],
                "skl"    : 45 + personalGrowths[3],
                "spd"    : 40 + personalGrowths[4],
                "lck"    : 30 + personalGrowths[5],
                "def"    : 40 + personalGrowths[6],
                "res"    : 30 + personalGrowths[7]
            }
    
    def __level_up(self):
        self.level += 1
        self.exp -= 100
        
        str = ""
        for stat in self.stats:
            rand = random.randrange(0,100) + 1
            if rand < self.growths[stat]:
                self.stats[stat] += 1
                str += '{} went up 1!\n'.format(stat.upper())
                if rand < self.growths[stat]-99:
                    self.stats[stat] += 1
                    str += '{} went up 1!\n'.format(stat.upper())
        print(str)
    
    def add_exp(self, enemyLevel, kill):
        super().add_exp(enemyLevel, kill)
        if self.exp >= 100:
            self.__level_up()
            
    def attack(self, target, crit=0):
        damage = self.stats["str"] + self.weapon.damage
        defense = target.stats["def"]
        rand = random.randrange(0,100) + 1
        if rand < crit:
            damage *= 2
        return Unit.attack(self, damage, defense)
    
    def equip_weapon(self, weapon):
        # Can't hold a lance properly, and no magic weapons
        if not weapon.type == 'Book' and not weapon.type == 'Wand' and not weapon.type == 'Staff' and not "Lance":
            Unit.equip_weapon(self, weapon)

class MountedUnit(Unit):
    def __init__(self, name, x, y, personalGrowths, personalStats, icon, portrait):
        super().__init__(name, "Cavalry", x, y)
        self.token = pygame.image.load(icon)
        self.icon = pygame.image.load(portrait)
        self.gray_token = grayscale_image(self.token)
        self.weapon = WeaponTraits.build_weapon("Iron Lance")
        self.exp = 0
        self.level = 1
        self.mov = 6
        self.stats = {
                "HP"     : 17 + personalStats[0],
                "str"    : 2 + personalStats[1],
                "mag"    : 0 + personalStats[2],
                "skl"    : 3 + personalStats[3],
                "spd"    : 2 + personalStats[4],
                "lck"    : 5 + personalStats[5],
                "def"    : 2 + personalStats[6],
                "res"    : 0 + personalStats[7],
            }
        self.currentHP = self.stats["HP"]
        self.__set_growths(personalGrowths)
        self.__set_maximum_stats(personalGrowths)
    
    def __set_maximum_stats(self, personalGrowths):
        self.max_stats = {
                "HP"     : min(120,70   + int(70*(personalGrowths[0]/100))),
                "str"    : min(99,60   + int(60*(personalGrowths[1]/150))),
                "mag"    : min(99,40   + int(40*(personalGrowths[2]/150))),
                "skl"    : min(99,60   + int(60*(personalGrowths[3]/150))),
                "spd"    : min(99,55   + int(55*(personalGrowths[4]/150))),
                "lck"    : min(99,80   + int(80*(personalGrowths[5]/150))),
                "def"    : min(99,70   + int(70*(personalGrowths[6]/150))),
                "res"    : min(99,70   + int(70*(personalGrowths[7]/150)))
            }
        
    def __set_growths(self,personalGrowths):
        self.growths = {
                "HP"     : 65 + personalGrowths[0],
                "str"    : 60 + personalGrowths[1],
                "mag"    : 15 + personalGrowths[2],
                "skl"    : 40 + personalGrowths[3],
                "spd"    : 20 + personalGrowths[4],
                "lck"    : 20 + personalGrowths[5],
                "def"    : 50 + personalGrowths[6],
                "res"    : 30 + personalGrowths[7]
            }
    
    def __level_up(self):
        self.level += 1
        self.exp -= 100
        
        str = ""
        for stat in self.stats:
            rand = random.randrange(0,100) + 1
            if rand < self.growths[stat]:
                self.stats[stat] += 1
                str += '{} went up 1!\n'.format(stat.upper())
                if rand < self.growths[stat]-100:
                    self.stats[stat] += 1
                    str += '{} went up 1!\n'.format(stat.upper())
        print(str)
    
    def add_exp(self, enemyLevel, kill):
        super().add_exp(enemyLevel, kill)
        if self.exp >= 100:
            self.__level_up()
            
    def attack(self, target, crit=0):
        damage = self.stats["str"] + self.weapon.damage
        defense = target.stats["def"]
        rand = random.randrange(0,100) + 1
        if rand < crit:
            damage *= 2
        return Unit.attack(self, damage, defense)
    
    def equip_weapon(self, weapon):
        # No light weapons, no magic weapons
        if not weapon.type == 'Book' and not weapon.type == 'Wand' and not weapon.type == 'Staff' and not "Dagger" and not "Shortsword" and not "Hatchet":
            Unit.equip_weapon(self, weapon)
        

class UnitGenerator:
    unit_classes = ["Duelist", "Soldier", "Rogue", "Assassin",
                    "Sage", "Mage", "General", "Knight"]
    tokenSize = 70
    
    @staticmethod
    def create_unit(name, unitClass, icon, portrait, boss=0):
        # HP, str, mag, skl, spd, lck, def, res
        personalGrowths = []
        personalStats = []
        if unitClass.lower() == 'duelist':
            personalGrowths.extend((15,35,0,45,30,15,5,5))
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((4,1,0,3,2,1,1,1)) 
            return InfantryUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'soldier':
            personalGrowths.extend((30,25,0,5,30,0,40,20)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((3,2,0,0,1,0,3,3))
            rogue = InfantryUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
            return rogue
        elif unitClass.lower() == 'rogue':
            personalGrowths.extend((0,10,10,25,60,45,0,0)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((3,1,0,2,3,3,1,2))
            rogue = ScoutUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
            return rogue
        elif unitClass.lower() == 'assassin':
            personalGrowths.extend((15,35,0,20,30,50,0,0)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((6,3,0,1,0,5,0,0))
            assassin = ScoutUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
            return assassin
        elif unitClass.lower() == 'sage':
            personalGrowths.extend((30,10,35,10,20,25,10,10)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((5,0,3,0,1,2,2,2)) 
            return MagicUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'mage':
            personalGrowths.extend((10,0,55,30,10,20,5,20)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((4,0,4,1,2,2,0,2)) 
            return MagicUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'general':
            personalGrowths.extend((50,30,0,10,5,5,30,20)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((7,2,0,1,0,0,3,2)) 
            return MountedUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'knight':
            personalGrowths.extend((35,30,0,25,15,5,20,20)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((6,2,0,2,1,1,1,2)) 
            return MountedUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'bandit':
            personalGrowths.extend((35,45,0,10,10,0,25,25))
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((6,4,0,0,0,0,2,3)) 
            return InfantryUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'cultist':
            personalGrowths.extend((30,0,65,0,10,0,25,20)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((6,0,4,0,1,0,2,2)) 
            return MagicUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'paladin':
            personalGrowths.extend((40,20,0,20,0,0,35,35)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((7,2,0,1,0,0,2,3)) 
            return MountedUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        else:
            personalGrowths.extend((20,20,20,10,20,40,10,10)) 
            personalStats.extend((3,2,2,1,1,4,1,1)) 
            return InfantryUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
            
        