'''
Item
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Has various functions used in multiple places
'''

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