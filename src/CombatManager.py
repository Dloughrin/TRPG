'''
CombatManager
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Manages turns, holds list of enemies and allies in a battle, 
        and resolves attacks
'''
import random
#import Utility
from InterpretMap import *
from aStar import astar_map,astar
from PyQt5.Qt5.qml.Qt.labs import location

class CombatManager():
    ALLY_TURN   = '2' # Maybe
    PLAYER_TURN = '1'
    ENEMY_TURN  = '0'
    
    ACTION_MOVE = '0'
    MOVE_MOVE   = '1'
    ACTION      = '2'
    WAIT        = '3'
    
    def __init__(self, allies, enemies=[]):
        self.characters = allies
        self.enemies = enemies
        
        self.__turn = CombatManager.PLAYER_TURN
        self.__turn_count = 0
        self.map = []
        self.count_acted()
        
    def count_acted(self):
        self.actions_available = 0
        self.moves_available = 0
        
        for char in self.characters:
            if not char.acted:
                self.actions_available += 1
            if not char.moved:
                self.moves_available += 1
    
    # For A*
    def update_cost_map(self,terrain,sprites):
        print("updating")
        tmap = []
        x = 0
        for row in terrain:
            y = 0
            rrow = []
            for pos in row:
                val = 1
                if pos.block == 1:
                    val = -1
                elif pos.slow == 1:
                    val = 2
                if sprites[x][y] == 'c':
                    val = 3
                elif sprites[x][y] == 'e':
                    val = 4
                rrow.append(val)
                y+=1
            x+=1
            tmap.append(rrow)
        self.map = tmap
        
        for char in self.characters:
            char.move_map = astar_map(self.map, (char.x,char.y), char.mov*2, allied = True, allow_diagonal_movement = False)
        for char in self.enemies:
            char.move_map = astar_map(self.map, (char.x,char.y), char.mov*2, allied = False, allow_diagonal_movement = False)
                
    def next_turn(self,terrain,sprites):
        self.update_cost_map(terrain,sprites)
        for char in self.enemies:
            char.moved = False
            char.acted = False
            char.attacking = False
            char.moving = False
            char.unresolved_attack = []
            char.unresolved_move = []
            char.next_square = []
        for char in self.characters:
            char.moved = False
            char.acted = False
            char.attacking = False
            char.moving = False
            char.unresolved_attack = []
            char.unresolved_move = []
            char.next_square = []
        
        if(self.__turn == CombatManager.ENEMY_TURN):
            self.__turn = CombatManager.PLAYER_TURN
        elif(self.__turn == CombatManager.PLAYER_TURN):
            self.__turn = CombatManager.ENEMY_TURN
        self.__turn_count += 1
        
    def current_turn_count(self):
        return self.__turn_count
    
    def current_turn(self):
        return self.__turn
    
    def place_enemy(self, placed):
        i = 0
        for x in self.enemies:
            if i == 0:
                i += 1
            elif (i-1) == placed:
                return i
            else:
                i += 1
    
    '''
    Looks to see if units are in range for movement or attack, then 
    decides which until to run at and attack based on how much damage
    they can each do to each other in one attack
    '''
    def ai(self, locations, terrain, npc):
        in_range_units= []
        x = 0
        for line in locations:
            y = 0
            #print(locations[x],npc.move_map[x])
            for coord in line:
                if coord == 'c' and npc.can_move_move(x,y):
                    print(coord)
                    for unit in self.characters:
                        if unit.x == x and unit.y == y:
                            npca = npc.attack(unit)
                            unita = npc.attack(npc)
                            damageVal = npca - unita
                            record = {"x":x, "y":y,"name":unit.name, "prio":damageVal}
                            in_range_units.append(record)
                y+=1
            x+=1
            
        
        print(in_range_units.__len__())
        if in_range_units.__len__() > 0:
            in_range_units = sorted(in_range_units,key=lambda x: x["prio"], reverse=True)
            rangeI = 0
            path = -1
            while path == -1 and rangeI < in_range_units.__len__():
                if npc.can_attack_stationary(in_range_units[rangeI]["x"],in_range_units[rangeI]["y"]):
                    print("attacking")
                    return [CombatManager.ACTION,in_range_units[rangeI]["name"]]
                elif npc.can_attack(in_range_units[rangeI]["x"],in_range_units[rangeI]["y"]):
                    print("move attacking")
                    path = astar(self.map, (npc.x,npc.y), (in_range_units[rangeI]["x"],in_range_units[rangeI]["y"]), allied=False, allow_diagonal_movement = False)
                    path = CombatManager.find_point(locations, path)
                    if path == -1:
                        pass
                    else:
                        return [CombatManager.ACTION_MOVE, path, in_range_units[rangeI]["name"]]
                elif npc.can_move_move(in_range_units[rangeI]["x"],in_range_units[rangeI]["y"]):
                    print("moving")
                    path = astar(self.map, (npc.x,npc.y), (in_range_units[rangeI]["x"],in_range_units[rangeI]["y"]), allied=False, allow_diagonal_movement = False) 
                    path = CombatManager.find_point(locations, path)
                    if path == -1:
                        pass
                    else:
                        return [CombatManager.MOVE_MOVE, path]
                rangeI += 1
                
            if path == -1:
                return [CombatManager.WAIT]
        
        return [CombatManager.WAIT]
    
           
    @staticmethod
    def find_point(locations,path):
        if path.__len__() <= 1:
            return -1
        elif locations[path[-2][0]][path[-2][1]] == 'c' or locations[path[-2][0]][path[-2][1]] == 'e':
            return CombatManager.find_point(locations,path[:-1])
        else:
            return path
    
    @staticmethod
    def fight(attacker, defender):
        aset = CombatManager.attack_unit(defender, attacker)
        dset = CombatManager.attack_unit(attacker, defender)
        naset = []
        ndset = []
        
        if CombatManager.calc_hit(defender, attacker):
            defender.take_damage(aset[1][0])
            naset.append(aset[1][0])
        else:
            naset.append(-1)
            
        if not defender.dead:
            if CombatManager.calc_hit(attacker,defender):
                attacker.take_damage(dset[1][0])
                ndset.append(dset[1][0])
            else:
                ndset.append(-1)
        
        i = 1
        while i < aset[0] or i < dset[0]:
            if defender.dead or attacker.dead:
                break
            elif aset[0] > dset[0]:
                if CombatManager.calc_hit(defender, attacker):
                    defender.take_damage(aset[1][i])
                    naset.append(aset[1][i])
                else:
                    naset.append(-1)
            else:
                if CombatManager.calc_hit(attacker,defender):
                    attacker.take_damage(dset[1][i])
                    ndset.append(dset[1][i])
                else:
                    ndset.append(-1)
            i += 1
        
        return [naset,ndset]
                
    
    @staticmethod
    def attack_unit(target, attacker):
        hits = CombatManager.calc_speed(target, attacker)
        damages = []
        attacker.currentX = attacker.x
        attacker.currentY = attacker.y
        for i in range(0, hits):
            if attacker.can_attack_stationary(target.x, target.y):
                crit = CombatManager.calc_crit(target,attacker)
                damage = attacker.attack(target, crit)
                damages.append(damage)
            else:
                return [0,[-2]]
        attacker.currentX = -1
        attacker.currentY = -1
        return [hits,damages]
    
    @staticmethod
    def calc_speed(target, attacker):
        spd = attacker.stats["spd"] - max(0,attacker.weapon.wt-attacker.stats["str"])
        dc = target.stats["spd"] - max(0,target.weapon.wt-target.stats["str"])
        if spd >= (dc*2) and spd >= (dc+10):
            return 3
        elif spd >= (dc+5):
            return 2
        else:
            return 1
    
    @staticmethod
    def calc_crit(target, attacker):
        crit = attacker.stats["skl"] / 2 + attacker.stats["lck"] / 5 + max(0,attacker.weapon.crit)
        cevade = target.stats["lck"]
        return max(0,(crit - cevade))
    
    @staticmethod
    def calc_hit(target, attacker):
        hit = attacker.weapon.hit + attacker.stats["skl"] * 2 + attacker.stats["lck"] / 2 
        dodge = target.stats["spd"] / 10 + target.stats["lck"] - max(0,target.weapon.wt-target.stats["str"])
        rand = random.randrange(0,100) + 1
        if rand < round(max(0,hit-dodge)):
            print("{} hit".format(attacker.name))
            return True    
        else:
            print("{} miss".format(attacker.name))
            return False
    