'''
Item
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Has various functions used in multiple places
'''
from Unit import UnitGenerator
from Item import WeaponTraits

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    h = textobj.get_height()
    textrect = textobj.get_rect()
    textrect.center = (x,y+h)
    surface.blit(textobj, textrect)
    
def draw_la_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    #w = textobj.get_width()/2
    h = textobj.get_height()/1.25
    textrect = textobj.get_rect()
    textrect.topleft = (x+10, y+h)
    surface.blit(textobj, textrect)
    
def draw_ra_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    w = textobj.get_width()
    # Adjustment took testing
    h = textobj.get_height()/1.25
    textrect = textobj.get_rect()
    textrect.topleft = (x-w-10, y+h)
    surface.blit(textobj, textrect)
    
def draw_la_stat(text, font, color, surface, x, y):
    if(text.__len__() < 5):
        text = '  ' + text
    textobj = font.render(text, 1, color)
    #w = textobj.get_width()/2
    h = textobj.get_height()/1.25
    textrect = textobj.get_rect()
    textrect.topleft = (x+10, y+h)
    surface.blit(textobj, textrect)
    
def save_file(units,file="auto"):
    output = ""
    for unit in units:
        output += "{} {} {} {} ".format(unit.name.replace("The ",""),unit.weapon.name.replace(" ","_"),unit.level,unit.exp) 
        for stat in unit.stats:
            output += '{} '.format(unit.stats[stat])
        output += '\n'
        
    with open('../saves/' + file + '.txt', 'w') as f:
        f.write(output)

def load_file(file="auto"):
    units = []
    with open('../saves/' + file + '.txt') as f:
        lines = f.readlines()
    for line in lines:
        newLine = line.strip().split(' ')
        unit = UnitGenerator.create_unit('The ' + newLine[0], newLine[0],'../assets/characters/' + newLine[0].lower() +'Token.png', '../assets/characters/' + newLine[0].lower() + '.png')
        weapon = WeaponTraits.build_weapon(newLine[1].replace("_"," "))
        unit.weapon = weapon
        unit.level = int(newLine[2])
        unit.exp = int(newLine[3])
        i = 4
        for stat in unit.stats:
            unit.stats[stat] = int(newLine[i])
            i+=1
        units.append(unit)
    return units
    