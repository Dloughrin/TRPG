'''
Unit
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Holds information for units on the game map
'''
import random
import pygame
from Item import Weapon

class Unit():
    def __init__(self, name, unitClass, x, y):
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
        
        self.exp = 0
        self.level = 1
        self.mov = 3
        self.range = 2
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
        
    def attack(self, damage, defense):
        dam = damage - defense
        if dam < 0:
            dam = 0
        return dam
    
    def move(self, newX, newY):
        self.x = newX
        self.y = newY
        
    def equip_weapon(self, weapon):
        self.weapon = weapon
        
    def can_move(self, newX, newY):
        dx = abs(self.originalX - newX)
        dy = abs(self.originalY - newY)
        if dx+dy > self.mov:
            return False
        else:
            return True
        
    def can_move_move(self, newX, newY):
        dx = abs(self.originalX - newX)
        dy = abs(self.originalY - newY)
        if dx+dy > self.mov+self.mov:
            return False
        else:
            return True
        
    def can_attack(self, newX, newY):
        dx = abs(self.originalX - newX)
        dy = abs(self.originalY - newY)
        if (dx+dy) > (self.mov+self.range):
            return False
        else:
            return True
            
    def can_attack_stationary(self, newX, newY):
        dx = abs(self.x - newX)
        dy = abs(self.y - newY)
        if dx+dy > self.range:
            return False
        else:
            return True
    
    def take_damage(self, damage):
        if damage > 0:
            self.currentHP -= damage
        if self.currentHP <= 0:
            self.dead = True
            self.currentHP = 0
    
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
        print(self.exp)
    
class MagicUnit(Unit):
    def __init__(self, name, x, y, personalGrowths, personalStats, icon, portrait):
        super().__init__(name, "Mage", x, y)
        self.weapon = Weapon('Fire', 5, 4, 100, 5, 'Book')
        self.token = pygame.image.load(icon)
        self.icon = pygame.image.load(portrait)
        self.exp = 0
        self.level = 1
        self.mov = 3
        self.range = 2
        self.stats = {
                "HP"     : 6 + personalStats[0],
                "str"    : 0  + personalStats[1],
                "mag"    : 3 + personalStats[2],
                "skl"    : 1 + personalStats[3],
                "spd"    : 2 + personalStats[4],
                "lck"    : 2 + personalStats[5],
                "def"    : 0 + personalStats[6],
                "res"    : 3 + personalStats[7],
            }
        self.currentHP = self.stats["HP"]
        self.__set_growths(personalGrowths)
        self.__set_maximum_stats(personalGrowths)
    
    def __set_maximum_stats(self, personalGrowths):
        self.max_stats = {
                "HP"     : 55   + int(55*(personalGrowths[0]/100)),
                "str"    : 50   + int(50*(personalGrowths[1]/150)),
                "mag"    : 70   + int(70*(personalGrowths[2]/150)),
                "skl"    : 60   + int(60*(personalGrowths[3]/150)),
                "spd"    : 60   + int(60*(personalGrowths[4]/150)),
                "lck"    : 80   + int(80*(personalGrowths[5]/150)),
                "def"    : 60   + int(60*(personalGrowths[6]/150)),
                "res"    : 70   + int(70*(personalGrowths[7]/150))
            }
            
    def __set_growths(self,personalGrowths):
        self.growths = {
                "HP"     : 35 + personalGrowths[0],
                "str"    : 25 + personalGrowths[1],
                "mag"    : 55 + personalGrowths[2],
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
        if weapon.type == 'Book' or weapon.type == 'Wand' or weapon.type == 'Staff':
            Unit.equip_weapon(self, weapon)

class InfantryUnit(Unit):
    def __init__(self, name, x, y, personalGrowths, personalStats, icon, portrait):
        super().__init__(name, "Infantry", x, y)
        self.token = pygame.image.load(icon)
        self.icon = pygame.image.load(portrait)
        self.weapon = Weapon('Light Sword', 4, 3, 90, 10, 'Sword')
        self.exp = 0
        self.level = 1
        self.mov = 3
        self.range = 1
        self.stats = {
                "HP"     : 7 + personalStats[0],
                "str"    : 2  + personalStats[1],
                "mag"    : 0 + personalStats[2],
                "skl"    : 1 + personalStats[3],
                "spd"    : 2 + personalStats[4],
                "lck"    : 2 + personalStats[5],
                "def"    : 2 + personalStats[6],
                "res"    : 1 + personalStats[7],
            }
        self.currentHP = self.stats["HP"]
        self.__set_growths(personalGrowths)
        self.__set_maximum_stats(personalGrowths)
    
    def __set_maximum_stats(self, personalGrowths):
        self.max_stats = {
                "HP"     : 60   + int(60*(personalGrowths[0]/100)),
                "str"    : 60   + int(60*(personalGrowths[1]/150)),
                "mag"    : 50   + int(50*(personalGrowths[2]/150)),
                "skl"    : 70   + int(70*(personalGrowths[3]/150)),
                "spd"    : 70   + int(70*(personalGrowths[4]/150)),
                "lck"    : 80   + int(80*(personalGrowths[5]/150)),
                "def"    : 55   + int(70*(personalGrowths[6]/150)),
                "res"    : 60   + int(70*(personalGrowths[7]/150))
            }
        
    def __set_growths(self,personalGrowths):
        self.growths = {
                "HP"     : 45 + personalGrowths[0],
                "str"    : 35 + personalGrowths[1],
                "mag"    : 20 + personalGrowths[2],
                "skl"    : 40 + personalGrowths[3],
                "spd"    : 55 + personalGrowths[4],
                "lck"    : 45 + personalGrowths[5],
                "def"    : 30 + personalGrowths[6],
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
        if not weapon.type == 'Book' and not weapon.type == 'Wand' and not weapon.type == 'Staff':
            Unit.equip_weapon(self, weapon)

class MountedUnit(Unit):
    def __init__(self, name, x, y, personalGrowths, personalStats, icon, portrait):
        super().__init__(name, "Mounted", x, y)
        self.token = pygame.image.load(icon)
        self.icon = pygame.image.load(portrait)
        self.weapon = Weapon('Iron Lance', 7, 8, 80, 0, 'Spear')
        self.exp = 0
        self.level = 1
        self.mov = 6
        self.range = 1
        self.stats = {
                "HP"     : 8 + personalStats[0],
                "str"    : 2 + personalStats[1],
                "mag"    : 0 + personalStats[2],
                "skl"    : 3 + personalStats[3],
                "spd"    : 2 + personalStats[4],
                "lck"    : 0 + personalStats[5],
                "def"    : 2 + personalStats[6],
                "res"    : 0 + personalStats[7],
            }
        self.currentHP = self.stats["HP"]
        self.__set_growths(personalGrowths)
        self.__set_maximum_stats(personalGrowths)
    
    def __set_maximum_stats(self, personalGrowths):
        self.max_stats = {
                "HP"     : 70   + int(70*(personalGrowths[0]/100)),
                "str"    : 60   + int(60*(personalGrowths[1]/150)),
                "mag"    : 40   + int(40*(personalGrowths[2]/150)),
                "skl"    : 60   + int(60*(personalGrowths[3]/150)),
                "spd"    : 55   + int(55*(personalGrowths[4]/150)),
                "lck"    : 80   + int(80*(personalGrowths[5]/150)),
                "def"    : 70   + int(70*(personalGrowths[6]/150)),
                "res"    : 70   + int(70*(personalGrowths[7]/150))
            }
        
    def __set_growths(self,personalGrowths):
        self.growths = {
                "HP"     : 55 + personalGrowths[0],
                "str"    : 60 + personalGrowths[1],
                "mag"    : 15 + personalGrowths[2],
                "skl"    : 45 + personalGrowths[3],
                "spd"    : 20 + personalGrowths[4],
                "lck"    : 20 + personalGrowths[5],
                "def"    : 50 + personalGrowths[6],
                "res"    : 35 + personalGrowths[7]
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
        if not weapon.type == 'Book' and not weapon.type == 'Wand' and not weapon.type == 'Staff':
            Unit.equip_weapon(self, weapon)
        

class UnitGenerator:
    unit_classes = ["duelist", "rogue", "sage",
                    "mage", "general", "knight"]
    
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
            personalStats.extend((1,1,0,3,2,1,1,1)) 
            return InfantryUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'rogue':
            personalGrowths.extend((0,15,10,25,60,40,0,0)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((0,0,0,2,3,4,1,2))
            rogue = InfantryUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
            rogue.mov = 4
            return rogue
        elif unitClass.lower() == 'sage':
            personalGrowths.extend((30,10,35,10,20,25,10,10)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((2,0,3,0,1,2,2,2)) 
            return MagicUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'mage':
            personalGrowths.extend((10,0,55,30,10,20,5,20)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((1,0,4,1,2,2,0,2)) 
            return MagicUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'general':
            personalGrowths.extend((50,30,0,10,5,5,30,20)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((4,2,0,1,0,0,3,2)) 
            return MountedUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'knight':
            personalGrowths.extend((35,30,0,25,15,5,20,20)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((3,2,0,2,1,1,1,2)) 
            return MountedUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'bandit':
            personalGrowths.extend((35,45,0,10,10,0,25,25))
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((3,4,0,0,0,0,2,3)) 
            return InfantryUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'cultist':
            personalGrowths.extend((30,0,65,0,10,0,25,20)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((3,0,4,0,1,0,2,2)) 
            return MagicUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        elif unitClass.lower() == 'paladin':
            personalGrowths.extend((40,20,0,20,0,0,35,35)) 
            if boss == 1:
                for x in personalGrowths:
                    x += 10
            personalStats.extend((4,2,0,1,0,0,2,3)) 
            return MountedUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
        else:
            personalGrowths.extend((20,20,20,10,20,40,10,10)) 
            personalStats.extend((0,2,2,1,1,4,1,1)) 
            return InfantryUnit(name, 0, 0, personalGrowths, personalStats, icon, portrait)
            
        