'''
Item
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Holds information for items to be used in game
        Mainly used for weapons
'''

class Item():
    def __init__(self, name):
        self.name = name
        
class Weapon(Item):
    def __init__(self, name, damage, weight, hit, crit, w_type):
        super().__init__(name)
        self.damage = damage
        self.hit = hit
        self.crit = crit
        self.wt = weight
        self.__type = w_type
    
    def get_type(self):
        return self.__type