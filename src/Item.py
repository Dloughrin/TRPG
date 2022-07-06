'''
Item
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Holds information for items to be used in game
        Mainly used for weapons
'''
import random

class Item():
    def __init__(self, name):
        self.name = name
        
class Weapon(Item):
    def __init__(self, name, damage, weight, hit, crit, w_type, range=1):
        super().__init__(name)
        self.damage = int(damage)
        self.hit = int(hit)
        self.crit = int(crit)
        self.wt = int(weight)
        self.range = int(range)
        self.__type = w_type
    
    def get_type(self):
        return self.__type
    
    def __str__(self):
        return "{}: range {} wt {} mt {} hit {} crit {}".format(self.name, self.range, self.wt, self.damage, self.hit, self.crit)
    
    
class WeaponTraits():
    types = [
             "Book", "Wand", "Staff", # Magic types
             "Lance", "Greatsword", "Greataxe", # Heavy weapons
             "Sword", "Spear", "Axe", # Standard weapons
             "Dagger", "Shortsword", "Hatchet" # Light weapons
             ]
    
    metal = [
             "Iron", "Steel", "Mithril",
             "Adamantite", "Platinum"
            ]
    element = [
             "Fire", "Arcfire", "Firestorm" # High wt, high damage
             "Lightning", "Bolt", "Overload" # High wt, medium damage, crit
             "Wind", "Arcwind", "Tornado"   # Medium wt, medium damage, high hit
             "Light", "Sunlight", "Starlight" # High wt, low damage, crit/hit
             "Shade", "Darkness", "Void" # High wt, high damage, low hit, hit crit
             "Chill", "Frost", "Freeze" # Low wt, medium damage
            ]
    
    weaponMod = [
                 "Thin", "Heavy", "Cursed",
                 "Brutal", "Deadly"
                ]
    spellMod =  [
                 "Focused", "Sniping", "Powerful",
                 "Occult", "Quickcast"
                ]
    
    
    @staticmethod
    def find_mod(category, mod="none"):
        damage = 0
        hit = 0
        crit = 0
        wt = 0
        wrange = 0
        if category == 1: # magic
            if mod == "none":
                rand = int(random.randrange(0,WeaponTraits.spellMod.__len__()))
                mod = WeaponTraits.spellMod[rand]
            if mod == "Focused":
                damage = 0
                hit = 15
                crit = 5
                wt = 3
                wrange = 2
            elif mod == "Sniping":
                damage = 1
                hit = -5
                crit = 0
                wt = 3
                wrange = 3
            elif mod == "Powerful":
                damage = 4
                hit = -5
                crit = 0
                wt = 1
                wrange = 1
            elif mod == "Occult":
                damage = 0
                hit = 0
                crit = 10
                wt = 2
                wrange = 2
            elif mod == "Quickcast":
                damage = -2
                hit = 0
                crit = 0
                wt = -4
                wrange = 2
        else:   # weapon
            if mod == "none":
                rand = int(random.randrange(0,WeaponTraits.weaponMod.__len__()))
                mod = WeaponTraits.weaponMod[rand]
            if mod == "Thin":
                damage = -2
                hit = 0
                crit = 0
                wt = -4
                wrange = 1
            elif mod == "Heavy":
                damage = 3
                hit = 0
                crit = 0
                wt = 6
                wrange = 1
            elif mod == "Cursed":
                damage = 6
                hit = -20
                crit = 10
                wt = -2
                wrange = 1
            elif mod == "Brutal":
                damage = 4
                hit = -10
                crit = 10
                wt = 8
                wrange = 1
            elif mod == "Deadly":
                damage = -2
                hit = 0
                crit = 20
                wt = 6
                wrange = 1
        
        return [damage,hit,crit,wt,wrange]
    
    @staticmethod
    def find_tier(category, tier):
        damage = 0
        hit = 0
        crit = 0
        wt = 0
        if category == 1:
            if tier == "Fire":
                damage = 3
                hit = 40
                crit = 0
                wt = 0
            elif tier == "Lightning":
                damage = 2
                hit = 45
                crit = 5
                wt = 2
            elif tier == "Wind":
                damage = 2
                hit = 50
                crit = 0
                wt = 1
            elif tier == "Light":
                damage = 1
                hit = 50
                crit = 10
                wt = 3
            elif tier == "Shade":
                damage = 5
                hit = 30
                crit = 0
                wt = 4
            elif tier == "Chill":
                damage = 4
                hit = 30
                crit = 5
                wt = 4
            elif tier == "Arcfire":
                damage = 6
                hit = 30
                crit = 0
                wt = 5
            elif tier == "Bolt":
                damage = 4
                hit = 40
                crit = 8
                wt = 6
            elif tier == "Arcwind":
                damage = 6
                hit = 40
                crit = 3
                wt = 6
            elif tier == "Sunlight":
                damage = 2
                hit = 35
                crit = 20
                wt = 8
            elif tier == "Darkness":
                damage = 9
                hit = 20
                crit = 5
                wt = 10
            elif tier == "Frost":
                damage = 7
                hit = 25
                crit = 10
                wt = 10
            elif tier == "Firestorm":
                damage = 9
                hit = 25
                crit = 0
                wt = 7
            elif tier == "Overload":
                damage = 10
                hit = 35
                crit = 15
                wt = 13
            elif tier == "Tornado":
                damage = 9
                hit = 30
                crit = 8
                wt = 9
            elif tier == "Starlight":
                damage = 5
                hit = 20
                crit = 30
                wt = 12
            elif tier == "Void":
                damage = 14
                hit = 20
                crit = 8
                wt = 14
            elif tier == "Freeze":
                damage = 12
                hit = 25
                crit = 15
                wt = 15
        else:
            if tier == "Iron":
                damage = 1
                hit = 10
                crit = 0
                wt = 2
            if tier == "Steel":
                damage = 4
                hit = -5
                crit = 0
                wt = 7
            if tier == "Mithril":
                damage = 8
                hit = -10
                crit = 15
                wt = 6
            if tier == "Adamantite":
                damage = 12
                hit = -15
                crit = 0
                wt = 12
            if tier == "Platinum":
                damage = 9
                hit = 0
                crit = 5
                wt = 5
        return [damage,hit,crit,wt]
    
    @staticmethod
    def find_weapon(name):
        damage = 0
        hit = 0
        crit = 0
        wt = 0
        wrange = 0
        if name == "Book":
            damage = 2
            hit = 50
            crit = 0
            wt = 4
            wrange = 2
        elif name == "Wand":
            damage = 1
            hit = 45
            crit = 10
            wt = 2
            wrange = 1
        elif name == "Staff":
            damage = 3
            hit = 40
            crit = 0
            wt = 6
            wrange = 2
        elif name == "Lance":
            damage = 6
            hit = 70
            crit = 0
            wt = 6
            wrange = 1
        elif name == "Spear":
            damage = 4
            hit = 75
            crit = 0
            wt = 4
            wrange = 1
        elif name == "Greataxe":
            damage = 9
            hit = 60
            crit = 0
            wt = 8
            wrange = 1
        elif name == "Axe":
            damage = 7
            hit = 65
            crit = 0
            wt = 6
            wrange = 1
        elif name == "Hatchet":
            damage = 5
            hit = 55
            crit = 0
            wt = 7
            wrange = 2
        elif name == "Greatsword":
            damage = 6
            hit = 75
            crit = 0
            wt = 5
            wrange = 1
        elif name == "Sword":
            damage = 4
            hit = 80
            crit = 0
            wt = 3
            wrange = 1
        elif name == "Shortsword":
            damage = 3
            hit = 85
            crit = 5
            wt = 2
            wrange = 1
        elif name == "Dagger":
            damage = 2
            hit = 70
            crit = 5
            wt = 2
            wrange = 2
            
        return [damage,hit,crit,wt,wrange]
    
    @staticmethod
    def build_weapon(name="none"):
        words = name.split(' ')
        wtype = ""
        
        category = 0
        rand1 = int(random.randrange(0,WeaponTraits.types.__len__()))
        
        for twtype in WeaponTraits.types:
            for word in words:
                if word == twtype:
                    wtype = twtype
                    break
                
        if wtype == "Book" or wtype == "Wand" or wtype == "Staff":
            category = 1
            if name == "none":
                rand2 = int(random.randrange(0,WeaponTraits.element.__len__()))
                name = "{} {}".format(WeaponTraits.types[rand1],WeaponTraits.element[rand2])
                words = name.split(' ')
        elif name == "none":
            rand2 = int(random.randrange(0,WeaponTraits.metal.__len__()))
            name = "{} {}".format(WeaponTraits.types[rand1],WeaponTraits.metal[rand2])
            words = name.split(' ')
        
        weapon = False
        if words.__len__() == 3:
            mtemp = WeaponTraits.find_mod(category,words[0])
            ttemp = WeaponTraits.find_tier(category,words[1])
            wtemp = WeaponTraits.find_weapon(wtype)
            wrange = wtemp[4]
            if mtemp[4] > wtemp[4]:
                wrange += 1
            weapon = Weapon(name, mtemp[0]+ttemp[0]+wtemp[0],  mtemp[3]+ttemp[3]+wtemp[3], mtemp[1]+ttemp[1]+wtemp[1], mtemp[2]+ttemp[2]+wtemp[2], wtype, wrange)
        elif words.__len__() == 2:
            ttemp = WeaponTraits.find_tier(category,words[1])
            wtemp = WeaponTraits.find_weapon(wtype)
            weapon = Weapon(name, ttemp[0]+wtemp[0],  ttemp[3]+wtemp[3], ttemp[1]+wtemp[1], ttemp[2]+wtemp[2], wtype, wtemp[4])
        else:
            wtemp = WeaponTraits.find_weapon(wtype)
            weapon = Weapon(name, wtemp[0],  wtemp[3], wtemp[1], wtemp[2], type, wtemp[4])
        
        return weapon
            