'''
CombatManager
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Manages turns, holds list of enemies and allies in a battle, 
        and resolves attacks
'''
import random


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
        self.count_acted()
        
    def count_acted(self):
        self.actions_available = 0
        self.moves_available = 0
        
        for char in self.characters:
            if not char.acted:
                self.actions_available += 1
            if not char.moved:
                self.moves_available += 1
                
    def next_turn(self):
        if(self.__turn == CombatManager.ENEMY_TURN):
            for char in self.characters:
                char.moved = False
                char.acted = False
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
    
    def ai(self, locations, terrain, npc):
        action = []
        npc.originalX = npc.x
        npc.originalY = npc.y
        inrange = 0
        inrangeCoords = []
        closestDist = -1
        closestCoord = []
        x = 0
        for xline in locations:
            y = 0
            for coord in xline:
                if coord == 'c':
                    if npc.can_attack(x,y):
                        inrange += 1
                        inrangeCoords.append([x,y])
                    if closestDist == -1 or closestDist > (abs(x-npc.x)+abs(y-npc.y)):
                        closestDist = (abs(x-npc.x)+abs(y-npc.y))
                        closestCoord = [x,y]
                y += 1
            x += 1
        
        if inrange == 0:  
            if closestCoord.__len__() == 0:
                return [CombatManager.WAIT]
            x = 0
            lowestMove = -1
            lowestCoord = []
            for xline in locations:
                y = 0
                for coord in xline:
                    if npc.can_move_move(x,y) and not coord == 'c' and not coord == 'e' and not terrain.tiles[x][y].block == 1:
                        if lowestMove == -1 or lowestMove > (abs(x-closestCoord[0])+abs(y-closestCoord[1])):
                            lowestMove = (abs(x-npc.x)+abs(y-npc.y))
                            lowestCoord = [x,y]
                    y += 1
                x += 1
            locations[lowestCoord[0]][lowestCoord[1]] = 'e'
            locations[npc.originalX][npc.originalY] = 'n'
            action = [CombatManager.MOVE_MOVE, lowestCoord]
        else:
            chosenCoord = inrangeCoords[0]
            targetI = -1
            damage = -100
            for coord in inrangeCoords:
                z = 0
                for target in self.characters:
                    damageOK = (damage == -1 or damage < (npc.attack(target) - target.attack(npc)))
                    if target.x == coord[0] and target.y == coord[1] and damageOK:
                        damage = npc.attack(target) - target.attack(npc)
                        chosenCoord = coord
                        targetI = z
                    z += 1
            
            if not npc.can_attack_stationary(chosenCoord[0],chosenCoord[1]):
                x = 0
                lowestMove = -1
                lowestCoord = []
                for xline in locations:
                    y = 0
                    for coord in xline:
                        if npc.can_move(x,y) and not coord == 'c' and not coord == 'e' and not terrain.tiles[x][y].block == 1:
                            if lowestMove == -1 or lowestMove > (abs(x-chosenCoord[0])+abs(y-chosenCoord[1])):
                                lowestMove = (abs(x-npc.x)+abs(y-npc.y))
                                lowestCoord = [x,y]
                        y += 1
                    x += 1
                locations[lowestCoord[0]][lowestCoord[1]] = 'e'
                locations[npc.originalX][npc.originalY] = 'n'
                action = [CombatManager.ACTION_MOVE, lowestCoord, targetI]
            else:
                action = [CombatManager.ACTION, closestCoord, targetI]
        return action
                    
            # Are there targets within movement range? Count them. Figure out which is the closest
            # If none are within range, move towards the closest enemy twice
            # If there's one in range, move to it then attack. If there's multiple, find which one takes the most damage while minimizing my damage taken
            # Append info to actions: Where to move and if attacking, and who
                
    
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
                    defender.take_damage(aset[1][0])
                    naset.append(aset[1][0])
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
        for i in range(0, hits):
            if attacker.can_attack_stationary(target.x, target.y):
                crit = CombatManager.calc_crit(target,attacker)
                damage = attacker.attack(target, crit)
                damages.append(damage)
            else:
                return [0,[-2]]
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
    